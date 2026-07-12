import gzip
import shutil
import requests
import geoip2.database, geoip2.errors
import ipaddress
import os

# URL for the .mmdb file
url = "https://cdn.jsdelivr.net/npm/geolite2-country/GeoLite2-Country.mmdb.gz"

# Country DB folder:
dbCountry = "Geolite2-country.mmdb"

def download_unzip():
    try:
        # Download File :

        response = requests.get(url, timeout=5)
        response.raise_for_status()

        zip_file = "Geolite2-country.mmdb.gz"

        with open(zip_file, "wb") as f:
            f.write(response.content)

        # Unzip the folder:

        with gzip.open(zip_file, "rb") as f_in:
            with open(dbCountry + ".tmp", "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        os.replace(dbCountry + ".tmp", dbCountry)
        os.remove(zip_file)

        print("[LogSentinal] dbCountry download succssfull...\n")
    except Exception as e:
        print("[LogSentinal] Unexpected Network Error occured. Country lookup might not be available...\n")
    

def country_lookup(ip):
    
    try:
        ip_adr = ipaddress.ip_address(ip)
        
        if ip_adr.is_private or ip_adr.is_loopback or ip_adr.is_reserved or ip_adr.is_multicast or ip_adr.is_link_local:
            return "Non-Public IP"
        
        elif ip_adr.is_global:
            with geoip2.database.Reader(dbCountry) as reader:
                country = reader.country(ip_adr).country.name
        
        return country if country else "Unknown"
    except ValueError:
        return "-"
    except geoip2.errors.AddressNotFoundError:
        return "Address Not Found"
    

if __name__ == "__main__":
    download_unzip()
    country_lookup("103.21.244.10")