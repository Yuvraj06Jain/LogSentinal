"""
GENERAL FORMAT OF LINUX ATH FILES:
<MONTH> <DATE> <TIMESTAMP> <SERVER MACHINE> <PROGRAM WHICH TRIGGERED THE PROCESS>[<PID>]: <MESSAGE>

Authentication FAILURE logs: (ONLY MESSAGE FIELD IS CHANGED)

Failed password for <SERVER SIDE USER> from <IP> port <CLIENT PORT> ssh2

Authentication SUCCESS logs: 

Accepted password for <SERVER SIDE USER> from <IP> port <CLIENT PORT> ssh2

"""

import re
import os
from collections import Counter, defaultdict, deque
from datetime import datetime, timedelta


#GLOBAL THRESHOLDS:
threshold = 6               # Threshold for the no. of failed logins in a min

#REGEX PATTERNS:
gen_pattern = r"""(?P<month>[^ ]*) (?P<date>[^ ]*) (?P<timestamp>[^ ]*) (?P<machine>[^ ]*) (?P<service>[^ \[]*)\[(?P<pid>[^ \]]*)\]: """
auth_msg_passwd = r"""(?P<status>Accepted|Failed) password for (?P<user>[^ ]*) from (?P<ip>[^ ]*) port (?P<port>[^ ]*) ssh2"""
auth_msg_key_success = r"""(?P<status>Accepted) publickey for (?P<user>[^ ]*) from (?P<ip>[^ ]*) port (?P<port>[^ ]*) ssh2"""
auth_msg_key_fail1 = r"""Connection closed by authenticating user (?P<user>[^ ]*) (?P<ip>[^ ]*) port (?P<port>[^ ]*) \[preauth\]"""
auth_msg_key_fail2 = r"""Received disconnect from (?P<ip>[^ ]*) port (?P<port>[^ ]*):11: Bye Bye \[preauth\]"""
possible_messages = [auth_msg_key_success, auth_msg_key_fail1, auth_msg_key_fail2, auth_msg_passwd]

#SUMMARY PATH:
summaryFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..","summary.txt")

class authParser():
    def __init__(self):
        self.fails_ip = defaultdict(int)
        
        self.sus_failed_logins_per_min = []
        self.failed_logins_dq = defaultdict(lambda: deque([]))

    def analyze(self, line):
        if line[0] == '#':
            return

        matches = [re.match(gen_pattern + msg, line) for msg in possible_messages]

        match = next((x for x in matches if isinstance(x, re.Match)), None)
        if not match:
            return

        grp = match.groupdict()

        grp.setdefault('status', 'Failed')
        grp.setdefault('user', 'unknown')


        self.login_analysis(grp)
        self.failed_logins_ip(grp)
    
    def login_analysis(self, grp):
        if grp['status'] == 'Failed':
            self.fails_ip[grp['ip']] += 1


    def failed_logins_ip(self, grp):

        if grp['status'] == 'Accepted':
            return
            
        self.failed_logins_dq[grp['ip']].append(grp['timestamp'])

        currentTimestamp = datetime.strptime(self.failed_logins_dq[grp['ip']][-1], "%H:%M:%S")

        while self.failed_logins_dq[grp['ip']] and currentTimestamp >= datetime.strptime(self.failed_logins_dq[grp['ip']][0], "%H:%M:%S") + timedelta(minutes=1):
            self.failed_logins_dq[grp['ip']].popleft()

        if len(self.failed_logins_dq[grp['ip']]) >= threshold:
            self.sus_failed_logins_per_min.append({ "IP" : grp['ip'], "From" : f"{self.failed_logins_dq[grp['ip']][0]}", "To" : self.failed_logins_dq[grp['ip']][-1], "No. of Failure attempts in a min" : len(self.failed_logins_dq[grp['ip']]) })
    
    def data_collection(self):
        data = {
                    'No. of Failed login attempts per IP' : self.fails_ip, 
                    f'Suspicious IPs based on failed login attempts greater than {threshold} per min' : self.sus_failed_logins_per_min
               }

        return data
    
    def data_clear(self):
        self.sus_failed_logins_per_min = []
        # self.fails_ip = defaultdict(int)
