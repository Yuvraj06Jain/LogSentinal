"""
Basic format of apache log entries:
<IP address of the sender> <indent> <user name> <timestamp> <request=inside quotes> <status code> <bytes=response size> <referrer=where request came from inside quotes> <user-agent=client software in quotes>
"""

import re
import json
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


#SQL CHECKS TO BE DONE FOR CHECKING INJECTION:
SQL_checks = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE', 'UNION', 'JOIN', 'WHERE', 'FROM', 'INTO', 'TABLE', 'AND', 'OR', '--', '#', ';']

class nginxParser():
    def __init__(self):
        self.mismatched_log = []
        self.shipped_lines = 0

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
        self.sus_ips_404 = []

        self.sus_ips_based_injection = []

        self.incomplete_responses = []

        self.db_aggregate_data = []     # Storing {timestamp, ip, url, method, status code, bandwidth} for calculating the URLs Counter, Bandwidth Analysis and IP_404_ratio during historical data
        

    def analyze(self,line):
        if not line or line[0] == '#' or line == "\n":
            self.mismatched_log.append(line)
            return
        
        match = re.match(pattern, line)
        if not match:
            self.mismatched_log.append(line)
            return

        grp = match.groupdict()
        dt_ts = datetime.strptime(grp['timestamp'],"%d/%b/%Y:%H:%M:%S")
        isoFormat = dt_ts.isoformat()

        self.req_rate_analysis(grp,isoFormat,dt_ts)
        self.bandwidth_analysis(grp,isoFormat, dt_ts)
        self.error_analysis(grp,isoFormat, dt_ts)
        self.injection_check(grp,isoFormat)
        self.rt_analysis(grp, isoFormat)
        self.error_404_ratio(grp)
        
        self.urls_counter(grp)

        self.db_aggregate_data.append({"Type" : "Nginx", "dbTimestamp": isoFormat,"IP" : grp['ip'], "URL" : grp['url'], "Method" : grp['method'], "Status_code" : grp['status_code'], "Bandwidth" : grp['bandwidth']})


    def req_rate_analysis(self, grp, isoFormat, dt_ts):
        self.min_dqs[grp['ip']].append(dt_ts)
        self.hour_dqs[grp['ip']].append(dt_ts)

        current_min_timestamp = self.min_dqs[grp['ip']][-1]
        current_hour_timestamp = self.hour_dqs[grp['ip']][-1]

        # Minute Window 
        while self.min_dqs[grp['ip']] and current_min_timestamp >= self.min_dqs[grp['ip']][0] + timedelta(minutes=1):
            self.min_dqs[grp['ip']].popleft()


        if len(self.min_dqs[grp['ip']]) >= min_threshold:
            self.sus_ips_req_rate_min.append({"dbTimestamp": isoFormat,"ip" : grp['ip'], "from" : self.min_dqs[grp['ip']][0].isoformat(), "to" : self.min_dqs[grp['ip']][-1].isoformat(), "Req Rate" : len(self.min_dqs[grp['ip']])})

        # Hour Window 
        while self.hour_dqs[grp['ip']] and current_hour_timestamp >= self.hour_dqs[grp['ip']][0] + timedelta(hours=1):
            self.hour_dqs[grp['ip']].popleft()

        if len(self.hour_dqs[grp['ip']]) >= hour_threshold:
            self.sus_ips_req_rate_hour.append({"dbTimestamp": isoFormat,"ip" : grp['ip'], "from" : self.hour_dqs[grp['ip']][0].isoformat(), "to" : self.hour_dqs[grp['ip']][-1].isoformat(), "Req Rate" : len(self.hour_dqs[grp['ip']])})


    
    def bandwidth_analysis(self, grp, isoFormat, dt_ts):
        ip = grp['ip']
        method = grp['method']

        if method in ['GET', 'HEAD']:

            self.download_ips[ip].append(dt_ts)

            current_timestamp = self.download_ips[ip][-1]

            #Download Minute Window 
            while self.download_ips[ip] and current_timestamp >= self.download_ips[ip][0] + timedelta(minutes=1):
                self.download_ips[ip].popleft()

            if len(self.download_ips[ip]) >= download_threshold:
                self.sus_ips_download.append({"dbTimestamp": isoFormat,"IP" : grp['ip'], "from" : self.download_ips[ip][0].isoformat(), "to" : self.download_ips[ip][-1].isoformat(), "No. of Downloads in a min" : len(self.download_ips[ip])})
                

            if grp['bandwidth'] and grp['bandwidth'] != '-' and int(grp['bandwidth']) >= bandwidth_threshold:
                self.sus_bandwidth.append({"dbTimestamp": isoFormat,"IP" : ip , "Action Type" : "Download" , "Size" : grp['bandwidth']})
                

        
        elif method in ['POST', 'PUT', 'PATCH']:

            self.upload_ips[ip].append(dt_ts)

            current_timestamp = self.upload_ips[ip][-1]

            #Upload Minute Window 
            while self.upload_ips[ip] and current_timestamp >= self.upload_ips[ip][0] + timedelta(minutes=1):
                self.upload_ips[ip].popleft()

            if len(self.upload_ips[ip]) >= upload_threshold:
                self.sus_ips_upload.append({"dbTimestamp": isoFormat,"IP" : grp['ip'], "from" : self.upload_ips[ip][0].isoformat(), "to" : self.upload_ips[ip][-1].isoformat(), "No. of uploads in a min" : len(self.upload_ips[ip])})
                

            if grp['bandwidth'] and grp['bandwidth'] != '-' and int(grp['bandwidth']) >= bandwidth_threshold:
                self.sus_bandwidth.append({"dbTimestamp": isoFormat,"IP" : ip , "Action Type" : "Upload" , "Size" : grp['bandwidth']})
        

    def error_analysis(self, grp, isoFormat, dt_ts):

        if grp['status_code'] not in ['401','403', '404']:
            return

        self.error_dqs[grp['ip']].append(dt_ts)

        current_timestamp = self.error_dqs[grp['ip']][-1]

        # Minute Window 
        while self.error_dqs[grp['ip']] and current_timestamp >= self.error_dqs[grp['ip']][0] + timedelta(minutes=1):
            self.error_dqs[grp['ip']].popleft()

        if len(self.error_dqs[grp['ip']]) >= error_threshold:
            self.sus_ips_error_per_min.append({"dbTimestamp": isoFormat,"IP" : grp['ip'], "from" : self.error_dqs[grp['ip']][0].isoformat(), "to" : self.error_dqs[grp['ip']][-1].isoformat(),"No. of errors in a min" : len(self.error_dqs[grp['ip']])})



    def error_404_ratio(self, grp):
        self.ip_total_req[grp['ip']] += 1
        if grp['status_code'] == '404': self.ip_404_req[grp['ip']] += 1

    def urls_counter(self, grp):
        self.urls[grp['url']][grp['method']] += 1


    def injection_check(self, grp, isoFormat):
        ip = grp['ip']
        url = grp['url']

        injection_pattern = r"(?P<url>[^ ]*) (?P<sus>.*)"
        match = re.match(injection_pattern, url)
        
        if not match:
            return

        if any(check in keyword for check in SQL_checks for keyword in match['sus'].upper().split()) or any(re.search(r"""(.+)=\1""", keyword, re.IGNORECASE) for keyword in match['sus'].split()):
            self.sus_ips_based_injection.append({"dbTimestamp": isoFormat,"IP" : ip , "URL" : url})

    def rt_analysis(self, grp, isoFormat):
        if grp['status_code'] == '499':
            self.incomplete_responses.append({"dbTimestamp" : isoFormat , "IP" : grp['ip'],"Timestamp" : grp['timestamp'],"Status Code" : grp['status_code'],"Response Time" : grp['rt'] })

    def data_collection(self):
        urls_counter_list = sorted([ {"URLs" : url , "Method" : method , "No. of times accessed" : count}
            for url,counts in self.urls.items() for method,count in counts.items()
        ], key = lambda x: x['No. of times accessed'], reverse=True)

        for ip in self.ip_404_req.keys():
            errors = self.ip_404_req[ip]
            total = self.ip_total_req[ip]

            r = errors/total

            if r >= ratio:
                self.sus_ips_404.append({'IP' : ip, 'Total Reqs' : total, '404 Reqs' : errors, "Ratio" : r})


        data = {
                    f'Suspicious IPs with req rate > {min_threshold} per min' : self.sus_ips_req_rate_min, 
                    f'Suspicious IPs with req rate > {hour_threshold} per hour' : self.sus_ips_req_rate_hour, 
                    f'Suspicious IPs based on No. of downloads > {download_threshold} per min': self.sus_ips_download,
                    f'Suspicious IPs based on No. of uploads > {upload_threshold} per min' : self.sus_ips_upload,
                    f'Suspicious IPs based on No. of errors > {error_threshold} per min' : self.sus_ips_error_per_min,
                    'Injection Attempts' : self.sus_ips_based_injection,
                    "Incomplete Responses" : self.incomplete_responses,
                    f"Suspicious IPs with No. of 404 errors > {ratio * 100}%" : sorted(self.sus_ips_404, key = lambda x: (x['Ratio'], x['404 Reqs']) , reverse=True),
                    'URLs Accessed Counter' : urls_counter_list,
                    "Bandwidth Analysis" : sorted(self.sus_bandwidth,key=lambda x: int(x['Size']), reverse=True),
               }

        # Non Aggregate data:
        non_aggregate_data = {
                                f'Suspicious IPs with req rate > {min_threshold} per min' : self.sus_ips_req_rate_min, 
                                f'Suspicious IPs with req rate > {hour_threshold} per hour' : self.sus_ips_req_rate_hour, 
                                f'Suspicious IPs based on No. of downloads > {download_threshold} per min': self.sus_ips_download,
                                f'Suspicious IPs based on No. of uploads > {upload_threshold} per min' : self.sus_ips_upload,
                                f'Suspicious IPs based on No. of errors > {error_threshold} per min' : self.sus_ips_error_per_min,
                                'Injection Attempts' : self.sus_ips_based_injection,
                                "Incomplete Responses" : self.incomplete_responses
                             }

        events = []
        for category, events_list in non_aggregate_data.items():
            for events_dict in events_list:
                events.append({"Timestamp" : events_dict['dbTimestamp'],
                               "category" : category,
                               "detail" : json.dumps(events_dict)
                               })
                
        # Aggregate data
        requests = self.db_aggregate_data

        return data, events, requests
    
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

        self.db_aggregate_data = []
        self.mismatched_log = []