import pandas as pd
import ipaddress
import re
import whois
import requests
from urllib.parse import urlparse
from datetime import datetime, timezone
import tldextract

def getLength(url):
    return 1 if len(url) >= 54 else 0

def getDepth(url):
    path = urlparse(url).path
    return path.count('/')

shortening_services = r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|tr\.im|link\.zip\.net"

def tinyURL(url):
    return 1 if re.search(shortening_services, url) else 0

def prefixSuffix(url):
    return 1 if '-' in urlparse(url).netloc else 0

def domainAge(domain_info):
    if not domain_info or not hasattr(domain_info, 'creation_date'): return 1
    creation_date = domain_info.creation_date
    if creation_date is None: return 1
    if isinstance(creation_date, list): creation_date = creation_date[0]
    
    if not isinstance(creation_date, datetime): return 1 

    if creation_date.tzinfo is None:
        creation_date = creation_date.replace(tzinfo=timezone.utc)
        
    age_in_days = (datetime.now(timezone.utc) - creation_date).days
    return 1 if age_in_days < 180 else 0

def domainEnd(domain_info):
    if not domain_info or not hasattr(domain_info, 'expiration_date'): return 1
    expiration_date = domain_info.expiration_date
    if expiration_date is None: return 1
    if isinstance(expiration_date, list): expiration_date = expiration_date[0]

    if not isinstance(expiration_date, datetime): return 1

    if expiration_date.tzinfo is None:
        expiration_date = expiration_date.replace(tzinfo=timezone.utc)

    end_in_days = (expiration_date - datetime.now(timezone.utc)).days
    return 1 if end_in_days < 180 else 0

def iframe(response):
    if response is None: return 1
    try:
        return 1 if re.search(r'<iframe|<frame', response.text, re.IGNORECASE) else 0
    except:
        return 1

def mouseOver(response):
    if response is None: return 1
    try:
        return 1 if re.search(r'onmouseover', response.text, re.IGNORECASE) else 0
    except:
        return 1

def rightClick(response):
    if response is None: return 1
    try:
        return 1 if re.search(r'event.button ?== ?2', response.text, re.IGNORECASE) else 0
    except:
        return 1

def forwarding(response):
    if response is None: return 1
    return 1 if len(response.history) > 1 else 0

def extract_features(url: str):

    print(f"Mulai ekstraksi fitur untuk: {url}")
    
    features = {
        'URL_Length': getLength(url),
        'URL_Depth': getDepth(url),
        'TinyURL': tinyURL(url),
        'Prefix/Suffix': prefixSuffix(url)
    }
    
    domain_info = None
    response = None
    dns_record_valid = 0
    
    try:
        ext = tldextract.extract(url)
        if ext.registered_domain:
            domain_info = whois.whois(ext.registered_domain)
            if domain_info and domain_info.creation_date:
                dns_record_valid = 1
    except Exception as e:
        print(f"Peringatan (WHOIS): {e}")
        pass

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, timeout=5, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Peringatan (Requests): {e}")
        pass

    features['DNS_Record'] = 1 if dns_record_valid == 0 else 0
    features['Domain_Age'] = domainAge(domain_info) if dns_record_valid else 1
    features['Domain_End'] = domainEnd(domain_info) if dns_record_valid else 1
    features['iFrame'] = iframe(response)
    features['Mouse_Over'] = mouseOver(response)
    features['Right_Click'] = rightClick(response)
    features['Web_Forwards'] = forwarding(response)
    
    final_feature_order = [
        'URL_Length', 'URL_Depth', 'TinyURL', 
        'Prefix/Suffix', 'DNS_Record', 'Domain_Age', 'Domain_End', 'iFrame', 
        'Mouse_Over', 'Right_Click', 'Web_Forwards'
    ]
    
    df = pd.DataFrame([features])
    
    df = df[final_feature_order]

    print("Ekstraksi fitur selesai.")
    return df