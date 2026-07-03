import requests
import ipaddress

# URL 
url = "https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/firehol_level1.netset"

class blackist_check():
    def __init__(self):
        self.cache = set()

    def create_cache(self):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            cache = set(ip for ip in response.text.splitlines() if not ip.startswith("#"))

            self.cache = cache

            print("[LogSentinal] Blacklisted IPs cache updated successfully\n")
        except:
            print("[LogSentinal] Unexpected Network Error occured. Info about Blacklisted IPs might not be available...\n")

    def blacklist_lookup(self, ip):
        if not self.cache:
            return -2           # CACHE NOT BUILT

        try:
            ip_adr = ipaddress.ip_address(ip)

            if ip_adr.is_private or ip_adr.is_reserved or ip_adr.is_loopback or ip_adr.is_multicast or ip_adr.is_link_local:
                return -1       # NON-PUBLIC IP
            
            elif ip_adr.is_global:
                if ip in self.cache:
                    return 1    # BLOCKED IP
                else:
                    return 0    # Not a blocked IP
        except:
            return -3           # Malformed IP
        
obj = blackist_check()    