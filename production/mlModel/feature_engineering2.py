import pandas as pd
from urllib.parse import urlparse
import ipaddress
import re
from datetime import datetime, timezone
import requests
import whois
import concurrent.futures
import sys # Untuk mencetak error

# ==============================================================================
# PENTING: PASTIKAN INSTALASI LIBRARY WHOIS ANDA BENAR
# ==============================================================================
# Sering terjadi konflik. Jalankan perintah ini di terminal Anda untuk memastikan:
# pip uninstall whois
# pip install python-whois
# ==============================================================================


# Konstanta untuk keterbacaan
# Jika Anda masih melihat banyak error WHOIS, coba kurangi angka ini menjadi 20 atau 30.
MAX_WORKERS = 30 

# ==============================================================================
# 1. FUNGSI EKSTRAKSI FITUR (Dengan Logika yang Diperbaiki)
# ==============================================================================

# Fungsi 'cepat' tidak berubah, mereka sudah benar.
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
    s = urlparse(url).path.split('/')
    depth = 0
    for j in range(len(s)):
        if len(s[j]) != 0:
            depth += 1
    return depth

def redirection(url):
    pos = url.rfind('//')
    return 1 if pos > 7 else 0

def httpDomain(url):
    return 1 if urlparse(url).scheme == 'https' else 0

shortening_services = r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|" \
                      r"yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|" \
                      r"short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|" \
                      r"doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|db\.tt|" \
                      r"qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|is\.gd|" \
                      r"po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|" \
                      r"prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|" \
                      r"tr\.im|link\.zip\.net"

def tinyURL(url):
    return 1 if re.search(shortening_services, url) else 0

def prefixSuffix(url):
    return 1 if '-' in urlparse(url).netloc else 0

# --- Fungsi-fungsi ini bergantung pada hasil network call ---

def domainAge(domain_name):
    if not domain_name or not domain_name.creation_date: return 1
    creation_date = domain_name.creation_date
    
    if isinstance(creation_date, list): creation_date = creation_date[0]
    if not isinstance(creation_date, datetime): return 1
    
    # PERBAIKAN FINAL: Jika tanggal dari whois bersifat naive, jadikan aware (UTC)
    if creation_date.tzinfo is None:
        creation_date = creation_date.replace(tzinfo=timezone.utc)
    
    age_in_days = (datetime.now(timezone.utc) - creation_date).days
    return 1 if age_in_days < 180 else 0

def domainEnd(domain_name):
    if not domain_name or not domain_name.expiration_date: return 1
    expiration_date = domain_name.expiration_date
    
    if isinstance(expiration_date, list): expiration_date = expiration_date[0]
    if not isinstance(expiration_date, datetime): return 1
        
    # PERBAIKAN FINAL: Jika tanggal dari whois bersifat naive, jadikan aware (UTC)
    if expiration_date.tzinfo is None:
        expiration_date = expiration_date.replace(tzinfo=timezone.utc)
    
    end_in_days = (expiration_date - datetime.now(timezone.utc)).days
    return 1 if end_in_days < 180 else 0

def iframe(response):
    if not response: return 1 # Jika request gagal, anggap mencurigakan
    try:
        # LOGIKA DIPERBAIKI: 1 jika ditemukan (mencurigakan), 0 jika tidak.
        return 1 if re.findall(r"<iframe|<frameBorder>", response.text, re.IGNORECASE) else 0
    except:
        return 1

def mouseOver(response): 
    if not response: return 1
    try:
        # LOGIKA KONSISTEN: 1 jika ditemukan (mencurigakan), 0 jika tidak.
        return 1 if re.findall(r"onmouseover", response.text, re.IGNORECASE) else 0
    except:
        return 1

def rightClick(response):
    if not response: return 1 # Jika request gagal, anggap mencurigakan
    try:
        # LOGIKA DIPERBAIKI: 1 jika ditemukan (mencurigakan), 0 jika tidak.
        return 1 if re.findall(r"event.button ?== ?2", response.text, re.IGNORECASE) else 0
    except:
        return 1

def forwarding(response):
    if not response: return 1
    return 1 if len(response.history) > 2 else 0


# ==============================================================================
# 2. FUNGSI WORKER UNTUK OPERASI JARINGAN (DENGAN LOGGING ERROR)
# ==============================================================================

def process_url_network_features(url):
    dns = 0
    domain_name = None
    response = None
    
    # --- WHOIS Lookup ---
    try:
        domain_str = urlparse(url).netloc
        # Tambahan: beberapa domain mungkin memiliki 'www.' yang perlu dihilangkan untuk whois
        if domain_str.startswith('www.'):
            domain_str = domain_str[4:]
        domain_name = whois.whois(domain_str)
    except Exception as e:
        # PERBAIKAN: Tambahkan logging error untuk melihat MENGAPA gagal
        # Pesan error akan dicetak ke konsol, tidak menghentikan program
        print(f"Error WHOIS for {url[:50]}...: {e}", file=sys.stderr)
        dns = 1

    # --- Requests (HTTP GET) ---
    try:
        # PERBAIKAN: Timeout dinaikkan menjadi 7 detik
        response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        # PERBAIKAN: Tambahkan logging error untuk melihat MENGAPA gagal
        print(f"Error Request for {url[:50]}...: {e}", file=sys.stderr)
        response = None

    # Ekstraksi fitur sekarang menggunakan logika yang diperbaiki
    dns_record = dns
    # Logika di sini diubah sedikit agar lebih jelas
    domain_age = domainAge(domain_name) if dns == 0 else 1
    domain_end = domainEnd(domain_name) if dns == 0 else 1
    
    has_iframe = iframe(response)
    has_mouseover = mouseOver(response)
    has_rightclick = rightClick(response)
    has_forwarding = forwarding(response)
    
    return [dns_record, domain_age, domain_end, has_iframe, has_mouseover, has_rightclick, has_forwarding]


# ==============================================================================
# 3. PROSES UTAMA (Tidak ada perubahan signifikan)
# ==============================================================================
if __name__ == '__main__':
    print("Loading dataset...")
    try:
        # Menggunakan file yang Anda upload sebagai contoh
        dataset = pd.read_csv('dataset/cleaned/final_cleaned_dataset.csv')
    except FileNotFoundError:
        print("Error: 'final_cleaned_dataset.csv' not found. Please place the file in the same directory.")
        exit()

    urls = dataset['URL'].tolist()
    
    print("Extracting fast features (non-network)...")
    features_df = pd.DataFrame()
    fast_features = {
        'Have_IP': [havingIP(u) for u in urls],
        'Have_At': [haveAtSign(u) for u in urls],
        'URL_Length': [getLength(u) for u in urls],
        'URL_Depth': [getDepth(u) for u in urls],
        'Redirection': [redirection(u) for u in urls],
        'https_Domain': [httpDomain(u) for u in urls],
        'TinyURL': [tinyURL(u) for u in urls],
        'Prefix/Suffix': [prefixSuffix(u) for u in urls],
    }
    features_df = pd.DataFrame(fast_features)

    print(f"Extracting slow features (network-based) using up to {MAX_WORKERS} workers...")
    network_features_list = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(process_url_network_features, urls)
    
    network_features_list = list(results)
    print("\nNetwork feature extraction complete.") # Tambah newline agar log error tidak tercampur

    print("Combining features...")
    network_feature_names = ['DNS_Record', 'Domain_Age', 'Domain_End', 'iFrame', 'Mouse_Over', 'Right_Click', 'Web_Forwards']
    network_features_df = pd.DataFrame(network_features_list, columns=network_feature_names)

    final_df = pd.concat([features_df, network_features_df], axis=1)

    if 'Label' in dataset.columns:
        final_df['Label'] = dataset['Label']
        
    # Memasukkan kolom URL di awal untuk memudahkan pengecekan
    final_df.insert(0, 'URL', urls)

    output_path = 'final_features_dataset_corrected.csv'
    final_df.to_csv(output_path, index=False)
    
    print(f"\nProcessing complete! Corrected features saved to '{output_path}'.")
    print("Please check the console for any error messages that occurred during the process.")
    # Menampilkan beberapa hasil untuk verifikasi cepat
    print("\nSample of the generated data:")
    print(final_df[['URL', 'DNS_Record', 'Domain_Age', 'Right_Click', 'Label']].head())