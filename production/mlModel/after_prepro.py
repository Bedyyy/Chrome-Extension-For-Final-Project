import pandas as pd
import os

file_path = 'final_cleaned_dataset_skripsi.csv'

if not os.path.exists(file_path):
    print(f"[ERROR] File '{file_path}' tidak ditemukan. Preprocessing terlebih dahulu.")
else:
    final_dataset = pd.read_csv(file_path)
    print("Dataset awal berhasil dimuat.")
    print(f"Jumlah data awal: {len(final_dataset)}")
    print("Distribusi label awal:")
    print(final_dataset['Label'].value_counts())
    print("-" * 30)

    target_per_label = 5000
    current_counts = final_dataset['Label'].value_counts()
    
    current_legit_count = current_counts.get(0, 0)
    current_phishing_count = current_counts.get(1, 0)

    needed_legit = target_per_label - current_legit_count
    needed_phishing = target_per_label - current_phishing_count

    print(f"Target per label: {target_per_label}")
    print(f"Kekurangan data Legitimate (Label 0): {needed_legit}")
    print(f"Kekurangan data Phishing (Label 1): {needed_phishing}")
    print("-" * 30)

    if needed_legit > 0 or needed_phishing > 0:
        print("[INFO] Menyiapkan data sumber untuk penambahan...")
        
        dataset1 = pd.read_csv('dataset/raw/Aalto University Dataset.csv', encoding_errors='replace', on_bad_lines='skip', low_memory=False)
        dataset2 = pd.read_csv('dataset/raw/Kaggle Dataset.csv')
        dataset3 = pd.read_csv('dataset/raw/OpenPhish Dataset.csv')
        dataset4 = pd.read_csv('dataset/raw/PhishTank Dataset.csv')
        dataset5 = pd.read_csv('dataset/raw/UCI MLR Dataset.csv')
        dataset5['label'] = dataset5['label'].replace({1: 0, 0: 1})
        
        reduced_column_dataset1 = dataset1[['domain', 'label']]
        reduced_column_dataset2 = dataset2[dataset2['type'].isin(['phishing', 'benign'])][['url', 'type']]
        reduced_column_dataset4 = dataset4[['url']]
        reduced_column_dataset5 = dataset5[['URL', 'label']]
        
        legitimate_dataset1 = reduced_column_dataset1[reduced_column_dataset1['label'] == 0.0]
        legitimate_dataset2 = reduced_column_dataset2[reduced_column_dataset2['type'] == 'benign']
        legitimate_dataset5 = reduced_column_dataset5[reduced_column_dataset5['label'] == 0]
        phishing_dataset1 = reduced_column_dataset1[reduced_column_dataset1['label'] == 1.0]
        phishing_dataset2 = reduced_column_dataset2[reduced_column_dataset2['type'] == 'phishing']
        phishing_dataset5 = reduced_column_dataset5[reduced_column_dataset5['label'] == 1]
        
        legitimate_dataset1.rename(columns={'domain': 'URL', 'label': 'Label'}, inplace=True)
        legitimate_dataset2.rename(columns={'url': 'URL', 'type': 'Label'}, inplace=True)
        legitimate_dataset5.rename(columns={'label': 'Label'}, inplace=True)
        phishing_dataset1.rename(columns={'domain': 'URL', 'label': 'Label'}, inplace=True)
        phishing_dataset2.rename(columns={'url': 'URL', 'type': 'Label'}, inplace=True)
        dataset3 = dataset3.rename(columns={'url': 'URL'})
        reduced_column_dataset4.rename(columns={'url': 'URL'}, inplace=True)
        phishing_dataset5.rename(columns={'label': 'Label'}, inplace=True)
        legitimate_dataset1['Label'], legitimate_dataset2['Label'], legitimate_dataset5['Label'] = 0, 0, 0
        phishing_dataset1['Label'], phishing_dataset2['Label'], dataset3['Label'], reduced_column_dataset4['Label'], phishing_dataset5['Label'] = 1, 1, 1, 1, 1

        merged_legitimate = pd.concat([legitimate_dataset1, legitimate_dataset2, legitimate_dataset5], ignore_index=True)
        merged_phishing = pd.concat([phishing_dataset1, phishing_dataset2, dataset3, reduced_column_dataset4, phishing_dataset5], ignore_index=True)
        
        print("[SUCCESS] Data sumber berhasil disiapkan.")
        print("-" * 30)

        used_urls = set(final_dataset['URL'])

        available_legit = merged_legitimate[~merged_legitimate['URL'].isin(used_urls)].drop_duplicates(subset=['URL'])
        available_phishing = merged_phishing[~merged_phishing['URL'].isin(used_urls)].drop_duplicates(subset=['URL'])

        print(f"Jumlah data baru (non-duplikat) yang tersedia:")
        print(f"Legitimate: {len(available_legit)}")
        print(f"Phishing: {len(available_phishing)}")
        print("-" * 30)

        data_to_add = []
        if needed_legit > 0:
            if len(available_legit) >= needed_legit:
                new_legit_data = available_legit.sample(n=needed_legit, random_state=42)
                data_to_add.append(new_legit_data)
                print(f"[INFO] {needed_legit} data legitimate baru telah ditambahkan.")
            else:
                print(f"[WARNING] Sumber data legitimate tidak cukup. Hanya bisa menambahkan {len(available_legit)} data.")
                data_to_add.append(available_legit)

        if needed_phishing > 0:
            if len(available_phishing) >= needed_phishing:
                new_phishing_data = available_phishing.sample(n=needed_phishing, random_state=42)
                data_to_add.append(new_phishing_data)
                print(f"[INFO] {needed_phishing} data phishing baru telah ditambahkan.")
            else:
                print(f"[WARNING] Sumber data phishing tidak cukup. Hanya bisa menambahkan {len(available_phishing)} data.")
                data_to_add.append(available_phishing)
        
        if data_to_add:
            final_balanced_dataset = pd.concat([final_dataset] + data_to_add, ignore_index=True)
        else:
            final_balanced_dataset = final_dataset

        final_balanced_dataset = final_balanced_dataset.sample(frac=1, random_state=42).reset_index(drop=True)

        print("-" * 30)
        print("=== PROSES SELESAI ===")
        print("Total data setelah penambahan:", len(final_balanced_dataset))
        print("Distribusi label final:")
        print(final_balanced_dataset['Label'].value_counts())

        output_filename = 'final_dataset_10k_balanced.csv'
        final_balanced_dataset.to_csv(output_filename, index=False)
        print(f"\nDataset final yang seimbang telah disimpan ke '{output_filename}'")

    else:
        print("Dataset sudah seimbang, tidak ada data yang perlu ditambahkan.")