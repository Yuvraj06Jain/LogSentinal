import requests
import ipaddress

# URL 
url = "https://raw.githubusercontent.com/sefinek/trusted-ips-whitelist/main/lists/all-safe-ips.txt"

class bot_check():
    def __init__(self):
        self.cache = set()

    def create_cache(self):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            cache = set(ip for ip in response.text.splitlines() if not ip.startswith("#"))

            self.cache = cache

            print("[LogSentinal] Bot IPs cache updated successfully\n")
        except:
            print("[LogSentinal] Unexpected Network Error occured. Bot IP might not be available...\n")

    def botIp_check(self, ip):
        if not self.cache:
            return "UNKNOWN [CACHE_NOT_BUILT]"

        try:
            if ipaddress.ip_address(ip):
                pass
        except:
            return "UNKNOWN [MALFORMED IP]"    
    
        if ip in self.cache:
            return "Bot"
        else:
            return "Public"
        
obj = bot_check()    