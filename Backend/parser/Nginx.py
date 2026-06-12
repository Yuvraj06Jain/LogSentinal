"""
Basic format of nginx log entries:
<IP address of the sender> <indent> <user name> <timestamp> <request=inside quotes> <status code> <bytes=response size> <referrer=where request came from inside quotes> <user-agent=client software in quotes> <rt>
"""

import re
import os
from collections import Counter, defaultdict, deque
from datetime import datetime, timedelta

#GLOBAL THRESHOLDS:
bandwidth_threshold = 10000  # Maximum Download size
upload_threshold = 5        # Threshold for the no. of uploads per min by an IP
download_threshold = 5      # Threshold for the no. of uploads per min by an IP
min_threshold = 5           # Threshold for the no. of requests per min by an IP
hour_threshold = 20         # Threshold for the no. of requests per hour by an IP
error_threshold = 6         # Threshold for the no. of 4xx errors per min by an IP
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

        self.sus_bandwidth = []

        self.sus_ips_download = []
        self.sus_ips_upload = []
        self.download_ips = defaultdict(lambda: deque([]))
        self.upload_ips = defaultdict(lambda: deque([]))

        self.error_dqs = defaultdict(lambda: deque([]))
        self.sus_ips_error_per_min = []

        self.urls = defaultdict(lambda: defaultdict(int))

        self.ip_total_req = defaultdict(int)
        self.ip_404_req = defaultdict(int)
        self.sus_ip_404 = []

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
        while self.min_dqs[grp['ip']] and current_min_timestamp >= datetime.strptime(self.min_dqs[grp['ip']][0], "%d/%b/%Y:%H:%M:%S") + timedelta(minutes=1):
            self.min_dqs[grp['ip']].popleft()


        if len(self.min_dqs[grp['ip']]) >= min_threshold:
            self.sus_ips_req_rate_min.append({"ip" : grp['ip'], "from" : f"{self.min_dqs[grp['ip']][0]}", "to" : f"{self.min_dqs[grp['ip']][-1]}"})

        # Hour Window 
        while self.hour_dqs[grp['ip']] and current_hour_timestamp >= datetime.strptime(self.hour_dqs[grp['ip']][0], "%d/%b/%Y:%H:%M:%S") + timedelta(hours=1):
            self.hour_dqs[grp['ip']].popleft()

        if len(self.hour_dqs[grp['ip']]) >= hour_threshold:
            self.sus_ips_req_rate_hour.append({"ip" : grp['ip'], "from" : f"{self.hour_dqs[grp['ip']][0]}", "to" : f"{self.hour_dqs[grp['ip']][-1]}"})


    
    def bandwidth_analysis(self, grp):
        ip = grp['ip']
        method = grp['method']

        if method in ['GET', 'HEAD']:

            self.download_ips[ip].append(grp['timestamp'])

            current_timestamp = datetime.strptime(self.download_ips[ip][-1], "%d/%b/%Y:%H:%M:%S")

            #Download Minute Window 
            while self.download_ips[ip] and current_timestamp >= datetime.strptime(self.download_ips[ip][0], "%d/%b/%Y:%H:%M:%S") + timedelta(minutes=1):
                self.download_ips[ip].popleft()

            if len(self.download_ips[ip]) >= download_threshold:
                self.sus_ips_download.append({"IP" : grp['ip'], "from" : f"{self.download_ips[ip][0]}", "to" : f"{self.download_ips[ip][-1]}", "No. of Downloads in a min" : f"{len(self.download_ips[ip])}"})

            if grp['bandwidth'] and int(grp['bandwidth']) >= bandwidth_threshold:
                self.sus_bandwidth.append({"IP" : ip , "Action Type" : "Download" , "Download Size" : grp['bandwidth']})

        
        elif method in ['POST', 'PUT', 'PATCH']:

            self.upload_ips[ip].append(grp['timestamp'])

            current_timestamp = datetime.strptime(self.upload_ips[ip][-1], "%d/%b/%Y:%H:%M:%S")

            #Upload Minute Window 
            while self.upload_ips[ip] and current_timestamp >= datetime.strptime(self.upload_ips[ip][0], "%d/%b/%Y:%H:%M:%S") + timedelta(minutes=1):
                self.upload_ips[ip].popleft()

            if len(self.upload_ips[ip]) >= upload_threshold:
                self.sus_ips_upload.append({"IP" : grp['ip'], "from" : f"{self.upload_ips[ip][0]}", "to" : f"{self.upload_ips[ip][-1]}", "No. of Downloads in a min" : f"{len(self.upload_ips[ip])}"})

            if grp['bandwidth'] and int(grp['bandwidth']) >= bandwidth_threshold:
                self.sus_bandwidth.append({"IP" : ip , "Action Type" : "Upload" , "Download Size" : grp['bandwidth']})


            
    def error_analysis(self, grp):

        if grp['status_code'] not in ['401','403', '404']:
            return

        self.error_dqs[grp['ip']].append(grp['timestamp'])

        current_timestamp = datetime.strptime(self.error_dqs[grp['ip']][-1], "%d/%b/%Y:%H:%M:%S")

        # Minute Window 
        while self.error_dqs[grp['ip']] and current_timestamp >= datetime.strptime(self.error_dqs[grp['ip']][0], "%d/%b/%Y:%H:%M:%S") + timedelta(minutes=1):
            self.error_dqs[grp['ip']].popleft()

        if len(self.error_dqs[grp['ip']]) >= min_threshold:
            self.sus_ips_error_per_min.append({"IP" : grp['ip'], "from" : f"{self.error_dqs[grp['ip']][0]}", "to" : f"{self.error_dqs[grp['ip']][-1]}"})
    


    def error_404_ratio(self, grp):
        self.ip_total_req[grp['ip']] += 1
        if grp['status_code'] == '404': self.ip_404_req[grp['ip']] += 1

        if self.ip_404_req[grp['ip']]/self.ip_total_req[grp['ip']] >= ratio:
            self.sus_ip_404.append({'IP' : grp['ip'], 'Total Req' : self.ip_total_req[grp['ip']], '404 Requests' : self.ip_404_req[grp['ip'], "Ratio" : self.ip_404_req[grp['ip']]/self.ip_total_req[grp['ip']]]})   
 


    def urls_counter(self, grp):
        self.urls[grp['url']][grp['method']] += 1


    def injection_check(self, grp):
        ip = grp['ip']
        url = grp['url']

        injection_pattern = r"(?P<url>[^ ]*) (?P<sus>.*)"
        match = re.match(injection_pattern, url)
        
        if not match:
            return

        if any(keyword in SQL_checks for keyword in match['sus'].upper().split()) or any(re.search(r"""(.+)=\1""", keyword, re.IGNORECASE) for keyword in match['sus'].split()):
            sus_msg = "ALERT : SQL Injection Possible"
            self.sus_ips_based_injection.append({"IP" : ip , "URL" : url})


    def rt_analysis(self, grp):
        if grp['status_code'] == '499':
            self.incomplete_responses.append({"IP" : grp['ip'],"Timestamp" : grp['timestamp'],"Status Code" : grp['status_code'],"Response Time" : grp['rt'] })
    
    def data_collection(self):
        data = {
                    f'Suspicious IPs with req rate greater than {min_threshold} per min' : self.sus_ips_req_rate_min,
                    f'Suspicious IPs with req rate greater than {hour_threshold} per hour' : self.sus_ips_req_rate_hour,
                    f'Suspicious IPs based on No. of downloads greater than {download_threshold} per min': self.sus_ips_download,
                    f'Suspicious IPs based on Np. of Uploads greater than {upload_threshold} per min' : self.sus_ips_upload,
                    f'Suspicious IPs based on No. of errors greater than {error_threshold} per min' : self.sus_ips_error_per_min,
                    f"Suspicious IPs with raio of 404 errors greater than {ratio}" : self.sus_ip_404,
                    f"Bandwidth Analysis" : self.sus_bandwidth,
                    'Most Accessed URLs' : self.urls, 
                    'injection' : self.sus_ips_based_injection, 
                    'Incomplete Responses' : self.incomplete_responses
               }

        return data
    
    def data_clear(self):
        self.sus_ips_based_injection = []
        self.sus_ips_download = []
        self.sus_ips_error_per_min = []
        self.sus_ips_req_rate_min = []
        self.sus_ips_req_rate_hour = []
        self.sus_ips_upload = []
        self.sus_bandwidth = []
        self.sus_ips_404 = []
        self.incomplete_responses = []
        
        # self.urls = defaultdict(lambda: defaultdict(int))
