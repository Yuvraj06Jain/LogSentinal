"""
GENERAL FORMAT OF LINUX ATH FILES:
<MONTH> <DATE> <TIMESTAMP> <SERVER MACHINE> <PROGRAM WHICH TRIGGERED THE PROCESS>[<PID>]: <MESSAGE>

Authentication FAILURE logs: (ONLY MESSAGE FIELD IS CHANGED)

Failed password for <SERVER SIDE USER> from <IP> port <CLIENT PORT> ssh2

Authentication SUCCESS logs: 

Accepted password for <SERVER SIDE USER> from <IP> port <CLIENT PORT> ssh2

"""

import re
from collections import Counter, defaultdict, deque
from datetime import datetime, timedelta


#GLOBAL SETTINGS:
threshold = 6               # Threshold for the no. of failed logins in a min


def auth_parsing(path):
    authentication_logs = defaultdict(list)

    gen_pattern = r"""(?P<month>[^ ]*) (?P<date>[^ ]*) (?P<timestamp>[^ ]*) (?P<machine>[^ ]*) (?P<service>[^ \[]*)\[(?P<pid>[^ \]]*)\]: """
    
    auth_msg_passwd = r"""(?P<status>Accepted|Failed) password for (?P<user>[^ ]*) from (?P<ip>[^ ]*) port (?P<port>[^ ]*) ssh2"""
    
    auth_msg_key_success = r"""(?P<status>Accepted) publickey for (?P<user>[^ ]*) from (?P<ip>[^ ]*) port (?P<port>[^ ]*) ssh2"""
    auth_msg_key_fail1 = r"""Connection closed by authenticating user (?P<user>[^ ]*) (?P<ip>[^ ]*) port (?P<port>[^ ]*) \[preauth\]"""
    auth_msg_key_fail2 = r"""Received disconnect from (?P<ip>[^ ]*) port (?P<port>[^ ]*):11: Bye Bye \[preauth\]"""
    
    possible_messages = [auth_msg_key_success, auth_msg_key_fail1, auth_msg_key_fail2, auth_msg_passwd]

    with open(path) as f:
        for line in f:
            line = line.strip()
            
            if not line:
                continue

            matches = [re.match(gen_pattern + msg, line) for msg in possible_messages]

            match = next((x for x in matches if isinstance(x, re.Match)), None)
            if not match:
                continue

            grp = match.groupdict()
            
            grp.setdefault('status', 'Failed')
            grp.setdefault('user', 'unknown')
            
            authentication_logs[grp['ip']].append(grp)

    analysis(authentication_logs)

def analysis(authentication_logs:dict):
    
    login_analysis(authentication_logs)
    failed_logins_min(authentication_logs)

def login_analysis(authentication_logs: dict):
    fails_ip = defaultdict(int)

    for ip in authentication_logs.keys():
        fails = 0
        for grp in authentication_logs[ip]:
            if grp['status'] == 'Failed':
                fails+=1
        fails_ip[ip] = fails

    print("No. of Failed Login attempts by each ip:")
    for k,v in fails_ip.items():
        print(f"{k} : {v}")
    print()
                

def failed_logins_min(authentication_logs: dict):
    sus_ip = []

    for ip in authentication_logs.keys():
        dq = deque([])
        flag = False
        for grp in authentication_logs[ip]:
            
            if grp['status'] == 'Accepted':
                continue
                
            dq.append(grp['timestamp'])

            currentTimestamp = datetime.strptime(dq[-1], "%H:%M:%S")

            while dq and currentTimestamp >= datetime.strptime(dq[0], "%H:%M:%S") + timedelta(minutes=1):
                dq.popleft()

                if len(dq) < threshold:
                    flag = False

            if len(dq) >= 5 and not flag:
                sus_ip.append([grp['ip'], f"from = {dq[0]}", f"to = {dq[-1]}"])
                flag = True


    print(f"Suspicious IPs with Failed login attempts >= {5} per min")
    for x in sus_ip:
        print(x)