# LogSentinal
***Real Time Multiple Log Files Monitoring System***


---
## To run the System:

1. Make sure Python 3.12+ is installed.
2. Clone the Repositiry.
3. Open a new terminal and cd to the cloned folder.
4. Run the following commands in order:

    **Windows/MacOS:**
    ```
        python3 -m venv venv
        source venv/bin/activate
        python run.py
    ```

    **Linux:**
    ```
        python3 -m venv venv
        source venv/bin/activate
        sudo python3 run.py
        # Note that using sudo will give admistrator access to the script. This is necessary to get the live updates from the Auth Log files directly
    ```
        
5. This installs the required dependencies automatically, then prompts you for the log folder paths.
6. Make sure the path you enter does not have quotes.
7. Open the dashboard at the given port.

---
# About the App:

- The system detects and analyzes Apache Log Files, Nginx Log Files and Linux Auth logs.
- The application analyzes the files and gives the data about the following things:
  - Apache:
    1. Suspicious IPs with req rate > 100 per min
    2. Suspicious IPs with req rate > 1000 per min
    3. Suspicious IPs based on No. of Downloads > 1000 per min
    4. Suspicious IPs based on No. of Uploads > 1000 per min
    5. Suspicious IPs based on No. of errors > 100 per min
    6. SQL Injection Attempts
    7. Suspicious IPs based on No. of 404 errors > 40% if the total requests
    8. IPs sorted based on the bandwidth used.
  - Nginx:
    1. Suspicious IPs with req rate > 100 per min
    2. Suspicious IPs with req rate > 1000 per min
    3. Suspicious IPs based on No. of Downloads > 1000 per min
    4. Suspicious IPs based on No. of Uploads > 1000 per min
    5. Suspicious IPs based on No. of errors > 100 per min
    6. SQL Injection Attempts
    7. Suspicious IPs based on No. of 404 errors > 40% if the total requests
    8. IPs sorted based on the bandwidth used.
    9. Requests with incomplete Responses.
  - Auth:
    1. Suspicious IPs based on failed login attempts > 20 per min
    2. No. of Failed Login attempts by an IP.

    
- The Dashboard will be running on the user's local host.
- Real time monitoring starts for the latest files and the new files that might be created during the monitoring.
- If the folder has old files which have not been analyzed before then all they would be analyzed in the background during the monitoring.
- Analyzed data is stored in the database for 30 days and can be accessed via the Historical tab of the dashboard
- Every detected IP is enriched with country-level geolocation via a local MaxMind GeoLite2 database — no external API calls, no per-request latency.
- IPs are cross-checked against AbuseIPDB's blacklist, cached and refreshed on a background timer
- Known-good crawlers (Googlebot, Bingbot, etc.) are whitelisted against a maintained CIDR list, so they don't pollute your suspicious-IP results.
- The app runs as a persistent async daemon, not a one-shot script — file monitoring, geolocation refresh, and blacklist refresh all run as independent background tasks.
- Log rotation and compressed (.gz) log files are handled automatically; monitoring doesn't break or skip data when a log file rotates mid-session.
- Summary report can be generated for the analyzed data. All the reports are stored in the SummaryReport folder.
