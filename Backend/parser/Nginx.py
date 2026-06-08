"""
Basic format of nginx log entries:
<IP address of the sender> <indent> <user name> <timestamp> <request=inside quotes> <status code> <bytes=response size> <referrer=where request came from inside quotes> <user-agent=client software in quotes> <rt>
"""

import re
import os
from collections import Counter, defaultdict, deque
from datetime import datetime, timedelta

#GLOBAL THRESHOLDS:
bandwidth_threshold = 1000  # Maximum Download size
upload_threshold = 5        # Threshold for the no. of uploads per min by an IP
download_threshold = 5      # Threshold for the no. of uploads per min by an IP
min_threshold = 5           # Threshold for the no. of 4xx errors per min by an IP
hour_threshold = 20         # Threshold for the no. of 4xx errors per hour by an IP
ratio = 0.4                 # No. of 404 errors/ No. of successes by an IP

#REGEX PATTERN
pattern = r"""(?P<ip>[^ ]*) (?P<intend>[^ ]*) (?P<user_name>[^ ]*) \[(?P<timestamp>[^ ]*) (?:\+\d{4})\] \"(?P<method>[^ ]*) (?P<url>.*?) (?:HTTP/1.1)\" (?P<status_code>\d{3}) (?P<bandwidth>[^ ]*) \"(?P<referrer>.*)\" \"(?P<user_agent>.*)\" rt=(?P<rt>\d+\.\d+)"""

#SUMMARY PATH
summaryFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..","summary.txt")

#SQL CHECKS TO BE DONE FOR CHECKING INJECTION:
SQL_checks = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE', 'UNION', 'JOIN', 'WHERE', 'FROM', 'INTO', 'TABLE', 'AND', 'OR', '--', '#', ';']

class nginxParser():
    def __init__(self):
        self.mismatched_log = []

        self.sus_ips_req_rate_min = []
        self.sus_ips_req_rate_hour = []
        self.min_dqs = defaultdict(lambda: deque([]))
        self.hour_dqs = defaultdict(lambda: deque([]))

        self.sus_ips_download = []
        self.sus_ips_upload = []
        self.download_ips = defaultdict(lambda: deque([]))
        self.upload_ips = defaultdict(lambda: deque([]))

        self.error_dqs = defaultdict(lambda: deque([]))
        self.sus_ips_error_per_min = []

        self.urls = defaultdict(lambda: defaultdict(int))

        self.sus_ips_based_injection = []

        self.incomplete_responses = []

    def analyze(self,line):
        if line[0] == '#':
            return
        
        match = re.match(pattern, line)
        if not match:
            self.mismatched_log.append(line)
            return

        grp = match.groupdict()

        self.req_rate_analysis(grp)
        self.bandwidth_analysis(grp)
        self.error_analysis(grp)
        self.injection_check(grp)
        self.rt_analysis(grp)

        self.urls_counter(grp)

    def req_rate_analysis(self, grp):
        self.min_dqs[grp['ip']].append(grp['timestamp'])
        self.hour_dqs[grp['ip']].append(grp['timestamp'])

        current_min_timestamp = datetime.strptime(self.min_dqs[grp['ip']][-1], "%d/%b/%Y:%H:%M:%S")
        current_hour_timestamp = datetime.strptime(self.hour_dqs[grp['ip']][-1], "%d/%b/%Y:%H:%M:%S")

        # Minute Window 
        while current_min_timestamp >= datetime.strptime(self.min_dqs[grp['ip']][0], "%d/%b/%Y:%H:%M:%S") + timedelta(minutes=1):
            self.min_dqs[grp['ip']].popleft()


        if len(self.min_dqs[grp['ip']]) >= min_threshold:
            self.sus_ips_req_rate_min.append([grp['ip'], f"from = {self.min_dqs[grp['ip']][0]}", f"to = {self.min_dqs[grp['ip']][-1]}"])

        # Hour Window 
        while current_hour_timestamp >= datetime.strptime(self.hour_dqs[grp['ip']][0], "%d/%b/%Y:%H:%M:%S") + timedelta(hours=1):
            self.hour_dqs[grp['ip']].popleft()

        if len(self.hour_dqs[grp['ip']]) >= hour_threshold:
            self.sus_ips_req_rate_hour.append([grp['ip'], f"from = {self.hour_dqs[grp['ip']][0]}", f"to = {self.hour_dqs[grp['ip']][-1]}"])

        with open(summaryFile, "a") as summ:
            summ.write(f"IPs with no. of requests >= {min_threshold} per min\n")
            for x in self.sus_ips_req_rate_min:
                summ.write(f"{x}\n")

            summ.write("\n")

            summ.write(f"IPs with no. of requests >= {hour_threshold} per hour\n")
            for x in self.sus_ips_req_rate_hour:
                summ.write(f"x\n")
            
            summ.write("\n")
    
    def bandwidth_analysis(self, grp):
        ip = grp['ip']
        method = grp['method']

        if method in ['GET', 'HEAD']:

            self.download_ips[ip].append(grp['timestamp'])

            current_timestamp = datetime.strptime(self.download_ips[ip][-1], "%d/%b/%Y:%H:%M:%S")

            # Minute Window 
            while current_timestamp >= datetime.strptime(self.download_ips[ip][0], "%d/%b/%Y:%H:%M:%S") + timedelta(minutes=1):
                self.download_ips[ip].popleft()

            if len(self.download_ips[ip]) >= download_threshold:
                self.sus_ips_download.append([grp['ip'], f"from = {self.download_ips[0]}", f"to = {self.download_ips[-1]}", f"No. of Downloads in a min = {len(self.download_ips[ip])}"])
        
        elif method in ['POST', 'PUT', 'PATCH']:

            self.upload_ips[ip].append(grp['timestamp'])

            current_timestamp = datetime.strptime(self.upload_ips[ip][-1], "%d/%b/%Y:%H:%M:%S")

            # Minute Window 
            while current_timestamp >= datetime.strptime(self.upload_ips[ip][0], "%d/%b/%Y:%H:%M:%S") + timedelta(minutes=1):
                self.upload_ips[ip].popleft()

            if len(self.upload_ips[ip]) >= upload_threshold:
                self.sus_ips_upload.append([grp['ip'], f"from = {self.upload_ips[0]}", f"to = {self.upload_ips[-1]}", f"No. of Uploads in a min = {len(self.upload_ips[ip])}"])
        
        with open(summaryFile,"a") as summ:
            summ.write(f"Suspicious IPs based on their No. of Downloads in a min = {download_threshold}:\n")

            for x in self.sus_ips_download:
                summ.write(f"{x}\n")

            summ.write(f"\nSuspicious IPs based on their No. of Uploads in a min = {upload_threshold}:\n")

            for x in self.sus_ips_upload:
                summ.write(f"{x}\n")
            
            summ.write("\n")
            
    def error_analysis(self, grp):

        if grp['status_code'] not in ['401','403', '404']:
            return

        self.error_dqs[grp['ip']].append(grp['timestamp'])

        current_timestamp = datetime.strptime(self.error_dqs[grp['ip']][-1], "%d/%b/%Y:%H:%M:%S")

        # Minute Window 
        while current_timestamp >= datetime.strptime(self.error_dqs[grp['ip']][0], "%d/%b/%Y:%H:%M:%S") + timedelta(minutes=1):
            self.error_dqs[grp['ip']].popleft()

        if len(self.error_dqs[grp['ip']]) >= min_threshold:
            self.sus_ips_error_per_min.append([grp['ip'], f"from = {self.error_dqs[grp['ip']][0]}", f"to = {self.error_dqs[grp['ip']][-1]}"])

        with open(summaryFile, "a") as summ:
            summ.write(f"IPs with bad requests >= {min_threshold} per min\n")
            for x in self.sus_ips_error_per_min:
                summ.write(f"{x}\n")
            summ.write("\n") 
    
    def urls_counter(self, grp):
        self.urls[grp['url']][grp['method']] += 1

        with open(summaryFile, "a+") as summ:
            summ.write("URLs Counter\n")
            for url in self.urls.keys():
                summ.write(f"url = {url } | ")
                for k,v in self.urls[url].items():
                    summ.write(f"| {k} = {v} |")
                summ.write("\n")
            
            summ.write("\n")

    def injection_check(self, grp):
        ip = grp['ip']
        url = grp['url']

        injection_pattern = r"(?P<url>[^ ]*) (?P<sus>.*)"
        match = re.match(injection_pattern, url)
        
        if not match:
            return

        if any(keyword in SQL_checks for keyword in match['sus'].upper().split()) or any(re.search(r"""(.+)=\1""", keyword, re.IGNORECASE) for keyword in match['sus'].split()):
            sus_msg = "ALERT : SQL Injection Possible"
            self.sus_ips_based_injection.append([ip, url, sus_msg])

        with open(summaryFile, "a+") as summ:
            summ.write("IPs that might be trying SQL injection: \n")

            for x in self.sus_ips_based_injection:
                summ.write(f"{x[0]} : {x[1]} || {x[2]}\n")

            summ.write("\n")

    def rt_analysis(self, grp):
        if grp['status_code'] == '499':
            self.incomplete_responses.append([ grp['ip'], grp['timestamp'], grp['status_code'], grp['rt'] ])

        with open(summaryFile, "a") as summ:
            summ.write("Incomplete Responses: \n")
            for x in self.incomplete_responses:
                summ.write(f"{x}\n")
            summ.write("\n")
    