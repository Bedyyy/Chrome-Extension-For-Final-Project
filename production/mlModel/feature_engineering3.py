import pandas as pd
import ipaddress
import re
import whois
import requests
from urllib.parse import urlparse
from datetime import datetime, timezone
import concurrent.futures
import time
import random
from tqdm import tqdm
import tldextract


def havingIP(url):
    try:
        ipaddress.ip_address(urlparse(url).netloc)
        return 1
    except:
        return 0

def haveAtSign(url):
    return 1 if "@" in url else 0

def getLength(url):
    return 1 if len(url) >= 54 else 0

def getDepth(url):
    path = urlparse(url).path
    return path.count('/')

def redirection(url):
    return 1 if url.rfind('//') > 7 else 0

def httpDomain(url):
    return 1 if 'http' in urlparse(url).netloc else 0

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
    
    if not isinstance(creation_date, datetime):
        return 1 

    if creation_date.tzinfo is None:
        creation_date = creation_date.replace(tzinfo=timezone.utc)
        
    age_in_days = (datetime.now(timezone.utc) - creation_date).days
    return 1 if age_in_days < 180 else 0

def domainEnd(domain_info):
    if not domain_info or not hasattr(domain_info, 'expiration_date'): return 1
    expiration_date = domain_info.expiration_date
    if expiration_date is None: return 1
    if isinstance(expiration_date, list): expiration_date = expiration_date[0]

    if not isinstance(expiration_date, datetime):
        return 1

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

def process_url(url):

    time.sleep(random.uniform(0.5, 1.5))
    
    domain_info = None
    response = None
    dns_record_valid = 0
    
    try:
        ext = tldextract.extract(url)
        if ext.top_domain_under_public_suffix:
            domain_info = whois.whois(ext.top_domain_under_public_suffix)
            if domain_info and domain_info.creation_date:
                dns_record_valid = 1
    except Exception as e:
        pass

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, timeout=7, headers=headers)
        response.raise_for_status()
    except Exception:
        pass

    dns_record = 1 if dns_record_valid == 0 else 0
    domain_age_feature = domainAge(domain_info) if dns_record_valid else 1
    domain_end_feature = domainEnd(domain_info) if dns_record_valid else 1
    
    iframe_feature = iframe(response)
    mouseover_feature = mouseOver(response)
    rightclick_feature = rightClick(response)
    forwarding_feature = forwarding(response)
    
    return [
        dns_record, domain_age_feature, domain_end_feature, 
        iframe_feature, mouseover_feature, rightclick_feature, forwarding_feature
    ]

if __name__ == '__main__':
    input_csv = 'final_dataset_10k_balanced.csv' 
    output_csv = 'final_featured_dataset_skripsi.csv'
    
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: File '{input_csv}' tidak ditemukan.")
        exit()

    if 'URL' not in df.columns:
        print("Error: CSV harus memiliki kolom bernama 'URL'.")
        exit()
        
    df.dropna(subset=['URL'], inplace=True)


    print("Memulai ekstraksi fitur...")
    
    print("Mengekstrak fitur cepat berbasis URL...")
    df['Have_IP'] = df['URL'].apply(havingIP)
    df['Have_At'] = df['URL'].apply(haveAtSign)
    df['URL_Length'] = df['URL'].apply(getLength)
    df['URL_Depth'] = df['URL'].apply(getDepth)
    df['Redirection'] = df['URL'].apply(redirection)
    df['https_Domain'] = df['URL'].apply(httpDomain)
    df['TinyURL'] = df['URL'].apply(tinyURL)
    df['Prefix/Suffix'] = df['URL'].apply(prefixSuffix)
    
    urls = df['URL'].tolist()
    
    MAX_WORKERS = 5
    
    print(f"\nMengekstrak fitur lambat berbasis jaringan menggunakan {MAX_WORKERS} workers...")
    print(f"Ini akan memakan waktu. Progress bar akan ditampilkan di bawah.")
    
    start_time = time.time()
    
    network_features_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(tqdm(executor.map(process_url, urls), total=len(urls)))
        network_features_list = results

    end_time = time.time()
    print(f"Ekstraksi fitur jaringan selesai dalam {end_time - start_time:.2f} detik.")

    print("Menggabungkan semua fitur dan menyimpan hasil...")
    
    slow_feature_names = [
        'DNS_Record', 'Domain_Age', 'Domain_End', 'iFrame', 
        'Mouse_Over','Right_Click', 'Web_Forwards'
    ]
    
    df_slow = pd.DataFrame(network_features_list, columns=slow_feature_names)
    
    final_df = pd.concat([df.reset_index(drop=True), df_slow], axis=1)

    final_feature_order = [
        'URL', 'Have_IP', 'Have_At', 'URL_Length', 'URL_Depth', 'Redirection', 'https_Domain', 'TinyURL', 
        'Prefix/Suffix', 'DNS_Record', 'Domain_Age', 'Domain_End', 'iFrame', 
        'Mouse_Over', 'Right_Click', 'Web_Forwards'
    ]
    if 'Label' in final_df.columns:
        final_feature_order.append('Label')
    
    final_df = final_df[final_feature_order]
    
    final_df.to_csv(output_csv, index=False)
    
    print(f"\nProses selesai! Dataset dengan fitur lengkap telah disimpan ke '{output_csv}'")
    print("\nContoh 5 baris pertama dari dataset yang dihasilkan:")
    print(final_df.head())