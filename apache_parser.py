"""
Basic format of apache log entries:
<IP address of the sender> <indent> <user name> <timestamp> <request=inside quotes> <status code> <bytes=response size> <referrer=where request came from inside quotes> <user-agent=client software in quotes>
"""

import re
from collections import Counter, defaultdict, deque
from datetime import datetime, timedelta

#GLOBAL THRESHOLDS:
bandwidth_threshold = 1000  # No. of Downloads/Uploads a user can perform
min_threshold = 5         # Minimum No. of 4xx errors per min by an IP
hour_threshold = 20       # Minimum No. of 4xx errors per hour by an IP
ratio = 0.4                 # No. of 404 errors/ No. of successes by an IP

def apache_parsing(path):
    mismatched_log = []
    ip_details = defaultdict(list)

    pattern = r"""(?P<ip>[^ ]*) (?P<intend>[^ ]*) (?P<user_name>[^ ]*) \[(?P<timestamp>[^ ]*) (?:\+\d{4})\] \"(?P<method>[^ ]*) (?P<url>.*?) (?:HTTP/1.1)\" (?P<status_code>\d{3}) (?P<bandwidth>[^ ]*) \"(?P<referrer>.*)\" \"(?P<user_agent>.*)\""""

    with open(path) as f:
        for line in f:
            line = line.strip()

            if not line:
                continue
            elif line[0] == '#':
                continue
                
            match = re.match(pattern,line)
            if not match:
                mismatched_log.append(line)
                continue

            grp = match.groupdict()
            ip_details[grp['ip']].append(grp)
    
    analysis(ip_details)

def analysis(ip_details: dict):
    
    req_rate_analysis(ip_details)
    bandwidth_analysis(ip_details)
    error_analysis(ip_details)
    injection_check(ip_details)

    urls_list = []
    for ip in ip_details.keys():
        for v in ip_details[ip]:
            urls_list.append([v['timestamp'], v['method'], v['url']])
    
    urls_counter(urls_list)

    
def req_rate_analysis(ip_details: dict):
    sus_ips_min = []
    sus_ips_hour = []

    for ip in ip_details.keys():
        flag_min = False
        flag_hour = False
            
        dq_min = deque([])
        dq_hour = deque([])

        for grp in ip_details[ip]:
            dq_min.append(grp['timestamp'])
            dq_hour.append(grp['timestamp'])

            current_min_timestamp = datetime.strptime(dq_min[-1], "%d/%b/%Y:%H:%M:%S")
            current_hour_timestamp = datetime.strptime(dq_hour[-1], "%d/%b/%Y:%H:%M:%S")

            # Minute Window 
            while current_min_timestamp >= datetime.strptime(dq_min[0], "%d/%b/%Y:%H:%M:%S") + timedelta(minutes=1):
                dq_min.popleft()

                if len(dq_min) < min_threshold:
                    flag_min = False

            if len(dq_min) >= min_threshold and not flag_min:
                sus_ips_min.append([grp['ip'], f"from = {dq_min[0]}", f"to = {dq_min[-1]}"])
                flag_min = True

            # Hour Window 
            while current_hour_timestamp >= datetime.strptime(dq_hour[0], "%d/%b/%Y:%H:%M:%S") + timedelta(hours=1):
                dq_hour.popleft()

                if len(dq_hour) < hour_threshold:
                    flag_hour = False

            if len(dq_hour) >= hour_threshold and not flag_hour:
                sus_ips_hour.append([grp['ip'], f"from = {dq_min[0]}", f"to = {dq_min[-1]}"])
                flag_hour = True
            
                
    print(f"IPs with no. of requests >= {min_threshold} per min")
    for x in sus_ips_min:
        print(x)

    print()

    print(f"IPs with no. of requests >= {hour_threshold} per hour")
    for x in sus_ips_hour:
        print(x)
    
    print()


def bandwidth_analysis(ips:dict):
    sus_ips_bandwidth = []

    for ip in ips.keys():
        sorted_timestamp = sorted(ips[ip],key=lambda x: datetime.strptime(x['timestamp'], "%d/%b/%Y:%H:%M:%S"))
        sorted_bandwidth = sorted(sorted_timestamp, key = lambda x: int(x['bandwidth'] if x['bandwidth'].isdigit() else 0), reverse=True)
        
        download_ips = [[x['method'], x['bandwidth'], x['timestamp']] for x in sorted_bandwidth if x['method'] in ['GET', 'HEAD'] and x['status_code']!='499']
        upload_ips = [[x['method'], x['bandwidth'], x['timestamp']] for x in sorted_bandwidth if x['method'] in ['POST', 'PUT', 'PATCH'] and 
                                                                                                                                        x['status_code']!='499']
    
        if len(download_ips) >= bandwidth_threshold or len(upload_ips) >= bandwidth_threshold:
            sus_ips_bandwidth.append(ip)


def error_analysis(ip_details: dict):

    error_ips = defaultdict(list)

    for ip in ip_details.keys():
        for grp in ip_details[ip]:
            if grp['status_code'] in ['401','403','404']:
                error_ips[ip].append(grp)

    sus_ips = []
    
    for ip in error_ips.keys():
        dq_min = deque([])
        flag = False

        for grp in ip_details[ip]:
            dq_min.append(grp['timestamp'])

            current_timestamp = datetime.strptime(dq_min[-1], "%d/%b/%Y:%H:%M:%S")

            # Minute Window 
            while current_timestamp >= datetime.strptime(dq_min[0], "%d/%b/%Y:%H:%M:%S") + timedelta(minutes=1):
                dq_min.popleft()

                if len(dq_min) < min_threshold:
                    flag = False

            if len(dq_min) >= min_threshold and not flag:
                sus_ips.append([grp['ip'], f"from = {dq_min[0]}", f"to = {dq_min[-1]}"])
                flag = True

    print(f"IPs with bad requests >= {min_threshold} per min")
    for x in sus_ips:
        print(x)
    print()
    

def urls_counter(url_list:list):
    urls = defaultdict(lambda: defaultdict(int))

    for v in url_list:
        urls[v[2]][v[1]] += 1
    
    print("URLs Counter")
    for url in urls.keys():
        print(f"url = {url }", end="|")
        for k,v in urls[url].items():
            print(f"| {k} = {v} |",end="")
        print()
    
    print()


def injection_check(ip_details:dict):
    sus_ips = []
    SQL_checks = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE', 'UNION', 'JOIN', 'WHERE', 'FROM', 'INTO', 'TABLE', 'AND', 'OR', '--', '#', ';']

    for ip in ip_details.keys():
        for grp in ip_details[ip]:
            method = grp['method']
            url = grp['url']

            pattern = r"(?P<url>[^ ]*) (?P<sus>.*)"
            match = re.match(pattern, url)
            
            if not match:
                continue

            if any(keyword in SQL_checks for keyword in match['sus'].upper().split()) or any(re.search(r"""(.+)=\1""", keyword, re.IGNORECASE) for keyword in match['sus'].split()):
                sus_msg = "ALERT : SQL Injection Possible"
                sus_ips.append([ip, url, sus_msg])
    
    print("IPs that might be trying SQL injection: ")
    for x in sus_ips:
        print(f"{x[0]} : {x[1]} || {x[2]}")
    print()