/*
Module: Log Analyzer & Security Monitoring Tool

Problem Statement:
System administrators often need to analyze huge log files to identify suspicious activities. 

Solution:
Develop a python program to analyze the log, find out key statistics and identify the security vulnerability points.
Results should be presented in a dashboard.

Features:
•	Parse Apache/Nginx/Linux Logs
•	Detect Failed Login Attempts
•	Identify suspicious Ips
•	Identify top 10 URL accessed 
•	Identify total number of times a URL is called/accessed
•	Generate Summary Report
•	Real-time log monitoring
•	Diff reports – compare Today’s log vs Yesterday’s log [ Basically History ]
•	Date/time filtering [Range Filtering]

Following core python concepts would be helpful:
•	Regex
•	File streaming
•	Pattern matching
•	CLI tools
Following libraries can be used:
•	re
•	collections
•	argparse
•	datetime


Summary Report:
    Logs of from date to to date
    List the suspicious IPs according to their suspiciousness
    list the URLs accoridng to the number of times they are accessed
    .
    .
    .

Grounds on which an IP has to be marked suspicious:
- High Request Rate
	Detection Criteria
		* 100 requests/minutes
		* 1000 requests/hour

- Excessive 4xx Errors
	Detection Criteria
		* 404 errors > 40%
		* 100 errors (404) / minute
- Large Response Transder
	Detection Criteria
		* High Bandwidth per IP
		* Thousands of Downloads

Checks implemented for Linux Auth Files"
* No of failed login attempt
* ⁠Number of logins per minute

Phases:
1.  Manually giving a folder and generating reports for all the log files.
2.  Transforming it into a real time log monitoring system...preferablly monitorig the log file every 5 mins
3.  Frontend.
*/