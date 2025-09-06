import pandas as pd

dataset1 = pd.read_csv('dataset/raw/Aalto University Dataset.csv', encoding_errors='replace', on_bad_lines='skip', low_memory=False)
dataset2 = pd.read_csv('dataset/raw/Kaggle Dataset.csv')
dataset3 = pd.read_csv('dataset/raw/OpenPhish Dataset.csv')
dataset4 = pd.read_csv('dataset/raw/PhishTank Dataset.csv')
dataset5 = pd.read_csv('dataset/raw/UCI MLR Dataset.csv')

dataset5['label'] = dataset5['label'].replace({1 : 0, 0 : 1})

# Data Reduction

reduced_dataset1 = dataset1[['domain', 'label']].rename(columns={'domain': 'URL', 'label': 'Label'})
reduced_dataset2 = dataset2[dataset2['type'].isin(['phishing', 'benign'])][['url', 'type']].rename(columns={'url': 'URL', 'type': 'Label'})
reduced_dataset3 = dataset3[['url']].rename(columns={'url': 'URL'})
reduced_dataset3['Label'] = 1
reduced_dataset4 = dataset4[['url']].rename(columns={'url': 'URL'})
reduced_dataset4['Label'] = 1
reduced_dataset5 = dataset5[['URL', 'label']].rename(columns={'label': 'Label'})

legitimate_dataset1 = reduced_dataset1[reduced_dataset1['Label'] == 0.0]
legitimate_dataset2 = reduced_dataset2[reduced_dataset2['Label'] == 'benign']
legitimate_dataset5 = reduced_dataset5[reduced_dataset5['Label'] == 0]

phishing_dataset1 = reduced_dataset1[reduced_dataset1['Label'] == 1.0]
phishing_dataset2 = reduced_dataset2[reduced_dataset2['Label'] == 'phishing']
phishing_dataset5 = reduced_dataset5[reduced_dataset5['Label'] == 1]

merged_legitimate = pd.concat([legitimate_dataset1, legitimate_dataset2, legitimate_dataset5], ignore_index=True)
merged_phishing = pd.concat([phishing_dataset1, phishing_dataset2, reduced_dataset3, reduced_dataset4, phishing_dataset5], ignore_index=True)

reduced_legitimate_dataset = merged_legitimate.sample(n=10000, ignore_index=True)
reduced_phishing_dataset = merged_phishing.sample(n=10000, ignore_index=True)

reduced_legitimate_dataset.to_csv('dataset/reduced/reduced_legitimate_dataset.csv', index=False)
reduced_phishing_dataset.to_csv('dataset/reduced/reduced_phishing_dataset.csv', index=False)

# Data Transformation

reduced_legitimate_dataset = pd.read_csv('dataset/reduced/reduced_legitimate_dataset.csv')
reduced_phishing_dataset = pd.read_csv('dataset/reduced/reduced_phishing_dataset.csv')

reduced_legitimate_dataset['Label'] = 0
reduced_phishing_dataset['Label'] = 1

# Data Cleaning

print("--- Memulai Proses Data Cleaning ---")

# --- Membersihkan Legitimate Dataset ---
print("\n[INFO] Membersihkan Legitimate Dataset...")
print(f"Bentuk data awal: {reduced_legitimate_dataset.shape}")

# 2. Menangani Missing Values
missing_before = reduced_legitimate_dataset.isnull().sum().sum()
reduced_legitimate_dataset.dropna(inplace=True) # Menghapus baris yang mengandung nilai kosong
print(f"Menangani missing values: {missing_before - reduced_legitimate_dataset.isnull().sum().sum()} baris dihapus.")

# 3. Menangani Duplikat
duplicates_before = reduced_legitimate_dataset.duplicated(subset=['URL']).sum()
reduced_legitimate_dataset.drop_duplicates(subset=['URL'], inplace=True, ignore_index=True)
print(f"Menangani duplikat: {duplicates_before} duplikat URL dihapus.")
print(f"Bentuk data setelah dibersihkan: {reduced_legitimate_dataset.shape}")


# --- Membersihkan Phishing Dataset ---
print("\n[INFO] Membersihkan Phishing Dataset...")
print(f"Bentuk data awal: {reduced_phishing_dataset.shape}")

# 2. Menangani Missing Values
missing_before = reduced_phishing_dataset.isnull().sum().sum()
reduced_phishing_dataset.dropna(inplace=True)
print(f"Menangani missing values: {missing_before - reduced_phishing_dataset.isnull().sum().sum()} baris dihapus.")

# 3. Menangani Duplikat
duplicates_before = reduced_phishing_dataset.duplicated(subset=['URL']).sum()
reduced_phishing_dataset.drop_duplicates(subset=['URL'], inplace=True, ignore_index=True)
print(f"Menangani duplikat: {duplicates_before} duplikat URL dihapus.")
print(f"Bentuk data setelah dibersihkan: {reduced_phishing_dataset.shape}")


# Data Integration

# 4. Menggabungkan kedua dataset yang sudah bersih
final_dataset = pd.concat([reduced_legitimate_dataset, reduced_phishing_dataset], ignore_index=True)

# Mengacak dataset agar data terdistribusi dengan baik (penting untuk machine learning)
final_dataset = final_dataset.sample(frac=1).reset_index(drop=True)

print("\n--- Proses Selesai ---")
print(f"Bentuk dataset final gabungan: {final_dataset.shape}")
print("Pemeriksaan akhir pada dataset final:")
print(f"  - Missing values: {final_dataset.isnull().sum().sum()}")
print(f"  - Duplikat URL: {final_dataset.duplicated(subset=['URL']).sum()}")

duplicates_before = final_dataset.duplicated(subset=['URL']).sum()
final_dataset.drop_duplicates(subset=['URL'], inplace=True, ignore_index=True)
print(f"Menangani duplikat: {duplicates_before} duplikat URL dihapus.")
print(f"Bentuk data setelah dibersihkan: {final_dataset.shape}")

# Tampilkan 5 baris pertama dari dataset final
print("\nContoh dataset final yang sudah bersih dan digabung:")
print(final_dataset.head())

# Opsi: Simpan dataset final yang bersih ke file CSV baru
final_dataset.to_csv('dataset/cleaned/final_cleaned_dataset.csv', index=False)