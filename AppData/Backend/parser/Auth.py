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
import ipaddress

from mmdb_operations import country_lookup
from blacklist_check import obj as blck
from bot_check import obj as botchk

#GLOBAL THRESHOLDS:
threshold = 100               # Threshold for the no. of failed logins in a min

#REGEX PATTERNS:
gen_pattern = r"""(?P<month>[^ ]*) (?P<date>[^ ]*) (?P<timestamp>[^ ]*) (?P<machine>[^ ]*) (?P<service>[^ \[]*)\[(?P<pid>[^ \]]*)\]: """
auth_msg_passwd = r"""(?P<status>Accepted|Failed) password for (?P<user>[^ ]*) from (?P<ip>[^ ]*) port (?P<port>[^ ]*) ssh2"""
auth_msg_key_success = r"""(?P<status>Accepted) publickey for (?P<user>[^ ]*) from (?P<ip>[^ ]*) port (?P<port>[^ ]*) ssh2"""
auth_msg_key_fail1 = r"""Connection closed by authenticating user (?P<user>[^ ]*) (?P<ip>[^ ]*) port (?P<port>[^ ]*) \[preauth\]"""
auth_msg_key_fail2 = r"""Received disconnect from (?P<ip>[^ ]*) port (?P<port>[^ ]*):11: Bye Bye \[preauth\]"""
possible_messages = [auth_msg_key_success, auth_msg_key_fail1, auth_msg_key_fail2, auth_msg_passwd]

# Function to resolve the type of IP
def ip_type(ip):
    try:
        ip_adr = ipaddress.ip_address(ip)
        
        if ip_adr.is_private:
            return "Private"
        elif ip_adr.is_reserved:
            return "Reserved"
        elif ip_adr.is_loopback:
            return "Loopback"
        elif ip_adr.is_multicast:
            return "Multicast"
        elif ip_adr.is_link_local:
            return "Link Local"
        else:
            return botchk.botIp_check(ip)
    except:
        return "Malformed IP"


class authParser():
    def __init__(self):
        self.mismatched_log = []
        self.shipped_lines = 0

        self.fails_ip = defaultdict(int)
        
        self.sus_failed_logins_per_min = []
        self.failed_logins_dq = defaultdict(lambda: deque([]))

        self.blocked_ips = defaultdict(int)
        self.country_data = defaultdict(int)

        self.db_aggregate_data = []  # Storing {timestamp, ip, url, method, status code, bandwidth} for calculating the Fails_ip during historical data

    def analyze(self, line:str):
        if not line or line.startswith("#") or line == "\n":
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
        dt_ts = dt_ts.replace(year=datetime.now().year)    # Since we don't have the year in the log lines....

        isoFormat = dt_ts.isoformat()

        country = country_lookup(grp['ip'])
        self.country_data[country] += 1

        blocked = blck.blacklist_lookup(grp['ip'])
        if blocked==1:
            self.blocked_ips[grp['ip']] += 1

        self.db_aggregate_data.append({"dbTimestamp": isoFormat,"IP" : grp['ip'],"Type": ip_type(grp['ip']), "User" : grp['user'],"Port" : grp['port'] ,"Status_code" : grp['status'], "Country": country, "Blocked" : blocked})

        self.login_analysis(grp)
        self.failed_logins_ip(grp,isoFormat, dt_ts)

    
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
            self.sus_failed_logins_per_min.append({"dbTimestamp": isoFormat,"IP" : grp['ip'], "Type": ip_type(grp['ip']), "from" : self.failed_logins_dq[grp['ip']][0].isoformat(), "to" : self.failed_logins_dq[grp['ip']][-1].isoformat(), "No. of Failure attempts in a min" : len(self.failed_logins_dq[grp['ip']]) })


    def data_collection(self):
        failed_ips_list = sorted([ {"IP" : ip, "Count" : count}
            for ip,count in self.fails_ip.items()], key=lambda x: x['Count'], reverse=True)
        
        blocked_ips_counter = sorted([{"IP" : ip, "Counter" : count} for ip, count in self.blocked_ips.items()], key=lambda x: x['Counter'], reverse=True)

        country_counter = sorted([{"Country" : country, "Counter" : count} for country, count in self.country_data.items()], key=lambda x: x['Counter'], reverse=True)

        data = {
                    f'Suspicious IPs based on failed login attempts > {threshold} per min' : self.sus_failed_logins_per_min,
                    'No. of times a blocked IP is accessing the server' : blocked_ips_counter,
                    'No. of requests from different Countries' : country_counter,
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
