import pandas as pd

# Load dataset
dataset1 = pd.read_csv('dataset/raw/Aalto University Dataset.csv', encoding_errors='replace', on_bad_lines='skip', low_memory=False)
dataset2 = pd.read_csv('dataset/raw/Kaggle Dataset.csv')
dataset3 = pd.read_csv('dataset/raw/OpenPhish Dataset.csv')
dataset4 = pd.read_csv('dataset/raw/PhishTank Dataset.csv')
dataset5 = pd.read_csv('dataset/raw/UCI MLR Dataset.csv')

# Perbaikan penafsiran label di dataset5
dataset5['label'] = dataset5['label'].replace({1: 0, 0: 1})

#######################
# AREA DATA REDUCTION #
#######################

# Reduksi kolom yang tidak diperlukan
reduced_column_dataset1 = dataset1.drop(columns=[col for col in dataset1.columns if col not in ['domain', 'label']])
reduced_column_dataset2 = dataset2[dataset2['type'].isin(['phishing', 'benign'])][['url', 'type']]
reduced_column_dataset4 = dataset4.drop(columns=[col for col in dataset4.columns if col != 'url'])
reduced_column_dataset5 = dataset5.drop(columns=[col for col in dataset5.columns if col not in ['URL', 'label']])

# Pemisahan data sesuai label
legitimate_dataset1 = reduced_column_dataset1[reduced_column_dataset1['label'] == 0.0]
legitimate_dataset2 = reduced_column_dataset2[reduced_column_dataset2['type'] == 'benign']
legitimate_dataset5 = reduced_column_dataset5[reduced_column_dataset5['label'] == 0]

phishing_dataset1 = reduced_column_dataset1[reduced_column_dataset1['label'] == 1.0]
phishing_dataset2 = reduced_column_dataset2[reduced_column_dataset2['type'] == 'phishing']
phishing_dataset5 = reduced_column_dataset5[reduced_column_dataset5['label'] == 1]

# Pengurangan jumlah data
reduced_value_legitimate_dataset1 = legitimate_dataset1.sample(n=2000, ignore_index=True, random_state=42)
reduced_value_legitimate_dataset2 = legitimate_dataset2.sample(n=2000, ignore_index=True, random_state=42)
reduced_value_legitimate_dataset5 = legitimate_dataset5.sample(n=2000, ignore_index=True, random_state=42)

reduced_value_phishing_dataset1 = phishing_dataset1.sample(n=1500, ignore_index=True, random_state=42)
reduced_value_phishing_dataset2 = phishing_dataset2.sample(n=1500, ignore_index=True, random_state=42)
reduced_value_phishing_dataset4 = reduced_column_dataset4.sample(n=1500, ignore_index=True, random_state=42)
reduced_value_phishing_dataset5 = phishing_dataset5.sample(n=1500, ignore_index=True, random_state=42)

############################
# AREA DATA TRANSFORMATION #
############################

# Penyesuaian nama kolom
reduced_value_legitimate_dataset1.rename(columns={'domain': 'URL', 'label': 'Label'}, inplace=True)
reduced_value_legitimate_dataset2.rename(columns={'url': 'URL', 'type': 'Label'}, inplace=True)
reduced_value_legitimate_dataset5.rename(columns={'label': 'Label'}, inplace=True)

reduced_value_phishing_dataset1.rename(columns={'domain': 'URL', 'label': 'Label'}, inplace=True)
reduced_value_phishing_dataset2.rename(columns={'url': 'URL', 'type': 'Label'}, inplace=True)
dataset3 = dataset3.rename(columns={'url': 'URL'})
reduced_value_phishing_dataset4.rename(columns={'url': 'URL'}, inplace=True)
reduced_value_phishing_dataset5.rename(columns={'label': 'Label'}, inplace=True)

# Label encoding
reduced_value_legitimate_dataset1['Label'] = 0
reduced_value_legitimate_dataset2['Label'] = 0
reduced_value_legitimate_dataset5['Label'] = 0

reduced_value_phishing_dataset1['Label'] = 1
reduced_value_phishing_dataset2['Label'] = 1
dataset3['Label'] = 1
reduced_value_phishing_dataset4['Label'] = 1
reduced_value_phishing_dataset5['Label'] = 1

#########################
# AREA DATA INTEGRATION #
#########################

# Penggabungan dataset legitimate
merged_legitimate = pd.concat(
    [reduced_value_legitimate_dataset1, reduced_value_legitimate_dataset2, reduced_value_legitimate_dataset5],
    ignore_index=True
)

# Penggabungan dataset phishing
merged_phishing = pd.concat(
    [reduced_value_phishing_dataset1, reduced_value_phishing_dataset2, dataset3, reduced_value_phishing_dataset4, reduced_value_phishing_dataset5],
    ignore_index=True
)

# Pengurangan jumlah data agar seimbang
balanced_legitimate = merged_legitimate.sample(n=5000, ignore_index=True, random_state=42)
balanced_phishing = merged_phishing.sample(n=5000, ignore_index=True, random_state=42)

# Penggabungan akhir
final_dataset = pd.concat([balanced_legitimate, balanced_phishing], ignore_index=True)

######################
# AREA DATA CLEANING #
######################

# Missing Values
check_missing = final_dataset.isnull().sum().sum()
if check_missing > 0:
    print(f"[INFO] Missing values: {check_missing}. Menghapus missing values.")
    final_dataset.dropna(inplace=True)

# Kesesuaian Tipe Data
check_type_data = final_dataset.info()

# Data Redundancy
check_duplicates = final_dataset.duplicated().sum()
if check_duplicates > 0:
    print(f"[INFO] Jumlah duplikat ditemukan: {check_duplicates}. Menghapus duplikat.")
    final_dataset.drop_duplicates(inplace=True)
    print("[INFO] Dataset : ", final_dataset.shape[0], " baris setelah menghapus duplikat.")

# # Acak dataset
final_dataset = final_dataset.sample(frac=1).reset_index(drop=True)
final_dataset.to_csv('final_cleaned_dataset_skripsi.csv', index=False)