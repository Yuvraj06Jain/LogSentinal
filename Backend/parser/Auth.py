"""
GENERAL FORMAT OF LINUX ATH FILES:
<MONTH> <DATE> <TIMESTAMP> <SERVER MACHINE> <PROGRAM WHICH TRIGGERED THE PROCESS>[<PID>]: <MESSAGE>

Authentication FAILURE logs: (ONLY MESSAGE FIELD IS CHANGED)

Failed password for <SERVER SIDE USER> from <IP> port <CLIENT PORT> ssh2

Authentication SUCCESS logs: 

Accepted password for <SERVER SIDE USER> from <IP> port <CLIENT PORT> ssh2

"""

import re
import json
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


class authParser():
    def __init__(self):
        self.mismatched_log = []
        self.shipped_lines = 0

        self.fails_ip = defaultdict(int)
        
        self.sus_failed_logins_per_min = []
        self.failed_logins_dq = defaultdict(lambda: deque([]))

        self.db_aggregate_data = []  # Storing {timestamp, ip, url, method, status code, bandwidth} for calculating the Fails_ip during historical data

    def analyze(self, line):
        if not line or line[0] == '#' or line == "\n":
            self.mismatched_log.append(line)
            return

        matches = [re.match(gen_pattern + msg, line) for msg in possible_messages]

        match = next((x for x in matches if isinstance(x, re.Match)), None)
        if not match:
            self.mismatched_log.append(line)
            return

        grp = match.groupdict()
        grp.setdefault('status', 'Failed')
        grp.setdefault('user', 'unknown')

        dt_ts = datetime.strptime(grp['month'] + ' ' + grp['date'] + ' ' + grp['timestamp'] , "%b %d %H:%M:%S")
        isoFormat = dt_ts.isoformat()


        self.login_analysis(grp)
        self.failed_logins_ip(grp,isoFormat, dt_ts)
        self.db_aggregate_data.append({"Type" : "Auth","dbTimestamp": isoFormat,"IP" : grp['ip'],"User" : grp['user'],"Port" : grp['port'] ,"Status" : grp['status']})


    
    def login_analysis(self, grp):
        if grp['status'] == 'Failed':
            self.fails_ip[grp['ip']] += 1



    def failed_logins_ip(self, grp, isoFormat, dt_ts):

        if grp['status'] == 'Accepted':
            return
            
        self.failed_logins_dq[grp['ip']].append(dt_ts)

        currentTimestamp = self.failed_logins_dq[grp['ip']][-1]

        while self.failed_logins_dq[grp['ip']] and currentTimestamp >= self.failed_logins_dq[grp['ip']][0] + timedelta(minutes=1):
            self.failed_logins_dq[grp['ip']].popleft()

        if len(self.failed_logins_dq[grp['ip']]) >= threshold:
            self.sus_failed_logins_per_min.append({"dbTimestamp": isoFormat,"IP" : grp['ip'], "from" : self.failed_logins_dq[grp['ip']][0].isoformat(), "to" : self.failed_logins_dq[grp['ip']][-1].isoformat(), "No. of Failure attempts in a min" : len(self.failed_logins_dq[grp['ip']]) })



    def data_collection(self):
        failed_ips_list = sorted([ {"IP" : ip, "Count" : count}
            for ip,count in self.fails_ip.items()], key=lambda x: x['Count'], reverse=True)

        data = {
                    f'Suspicious IPs based on failed login attempts > {threshold} per min' : self.sus_failed_logins_per_min,
                    'No. of Failed login attempts per IP' : failed_ips_list
               }
        
        # Non Aggregate data:
        non_aggregate_data = {
                                f'Suspicious IPs based on failed login attempts > {threshold} per min' : self.sus_failed_logins_per_min
                             }
        
        events = []
        for category, events_list in non_aggregate_data.items():
            for events_dict in events_list:
                events.append({"Timestamp" : events_dict['dbTimestamp'],
                               "category" : category,
                               "detail" : json.dumps(events_dict)
                               })
                
        # Aggregate data:
        requests = self.db_aggregate_data

        return data, events, requests


    def data_clear(self):
        self.sus_failed_logins_per_min = []
        
        self.mismatched_log = []
        self.db_aggregate_data = []
