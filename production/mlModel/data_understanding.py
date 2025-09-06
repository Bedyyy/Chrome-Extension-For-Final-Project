import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

dataset1 = pd.read_csv('dataset/raw/Aalto University Dataset.csv', encoding_errors='replace', on_bad_lines='skip', low_memory=False)
dataset2 = pd.read_csv('dataset/raw/Kaggle Dataset.csv')
dataset3 = pd.read_csv('dataset/raw/OpenPhish Dataset.csv')
dataset4 = pd.read_csv('dataset/raw/PhishTank Dataset.csv')
dataset5 = pd.read_csv('dataset/raw/UCI MLR Dataset.csv')

print(dataset1.shape)
print(dataset2.shape)
print(dataset3.shape)
print(dataset4.shape)
print(dataset5.shape)

#############################################
#                                           #
#      AREA ANALISIS DISTRIBUSI DATA        #
#                                           #
#############################################

def check_columns(dataset):
    print(dataset.columns)

for i, dataset in enumerate([dataset1, dataset2, dataset3, dataset4, dataset5], start=1):
    print(f"\n Kolom pada Dataset{i}:")
    check_columns(dataset)

label_col = 'label'
label_counts_dataset1 = dataset1[label_col].value_counts()
label_counts_dataset5 = dataset5[label_col].value_counts()
print("\nDistribusi Data Dataset 1:")
print(label_counts_dataset1)
print("\nDistribusi Data Dataset 5:")
print(label_counts_dataset5)

label_col = 'type'
label_counts_dataset2 = dataset2[label_col].value_counts()
print("\nDistribusi Data Dataset 2:")
print(label_counts_dataset2)

label_col = 'url'
label_counts_dataset3 = dataset3[label_col].count()
label_counts_dataset4 = dataset4[label_col].count()
print("\nDistribusi Data Dataset 3:")
print(label_counts_dataset3)
print("\nDistribusi Data Dataset 4:")
print(label_counts_dataset4)

def visualize_data_distribution(dataset, label_col, dataset_name):
    plt.figure(figsize=(6, 4))
    sns.countplot(x=label_col, hue=label_col, data=dataset, palette="Set2", legend=False)
    plt.title(f'Distribusi Label dalam {dataset_name}')
    plt.xlabel('Label')
    plt.ylabel('Jumlah Data')
    plt.tight_layout()
    plt.show()

visualize_data_distribution(dataset1, 'label', 'Dataset 1 (Aalto University)')
visualize_data_distribution(dataset5, 'label', 'Dataset 5 (UCI MLR)')
visualize_data_distribution(dataset2, 'type', 'Dataset 2 (Kaggle)')

plt.figure(figsize=(4, 4))
sns.barplot(x=['Dataset 3 (OpenPhish)'], y=[label_counts_dataset3])
plt.title('Jumlah Data URL Phishing - Dataset 3 (OpenPhish)')
plt.ylabel('Jumlah Data')
plt.xlabel('Dataset')
plt.tight_layout()
plt.show()

plt.figure(figsize=(4, 4))
sns.barplot(x=['Dataset 4 (PhishTank)'], y=[label_counts_dataset4])
plt.title('Jumlah Data URL Phishing - Dataset 4 (PhishTank)')
plt.ylabel('Jumlah Data')
plt.xlabel('Dataset')
plt.tight_layout()
plt.show()

#############################################
#                                           #
#         AREA PENYUSUNAN DATASET           #
#                                           #
#############################################

new_dataset1 = dataset1[['domain', 'label']].rename(columns={'domain': 'URL', 'label': 'Label'})
new_dataset2 = dataset2[dataset2['type'].isin(['phishing', 'benign'])][['url', 'type']].rename(columns={'url': 'URL', 'type': 'Label'})
new_dataset3 = dataset3[['url']].rename(columns={'url': 'URL'})
new_dataset3['Label'] = 1
new_dataset4 = dataset4[['url']].rename(columns={'url': 'URL'})
new_dataset4['Label'] = 1
new_dataset5 = dataset5[['URL', 'label']].rename(columns={'label': 'Label'})

new_dataset1.to_csv('dataset/after_DU/dataset1.csv', index=False)
new_dataset2.to_csv('dataset/after_DU/dataset2.csv', index=False)
new_dataset3.to_csv('dataset/after_DU/dataset3.csv', index=False)
new_dataset4.to_csv('dataset/after_DU/dataset4.csv', index=False)
new_dataset5.to_csv('dataset/after_DU/dataset5.csv', index=False)