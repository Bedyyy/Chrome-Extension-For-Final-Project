import pandas as pd

dataset1 = pd.read_csv('dataset/after_DU/dataset1.csv')
dataset2 = pd.read_csv('dataset/after_DU/dataset2.csv')
dataset3 = pd.read_csv('dataset/after_DU/dataset3.csv')
dataset4 = pd.read_csv('dataset/after_DU/dataset4.csv')
dataset5 = pd.read_csv('dataset/after_DU/dataset5.csv')

#############################################
#                                           #
#           AREA DATA REDUCTION             #
#                                           #
#############################################

# dataset1 = dataset1['Label'].value_counts()
# print("Distribusi Data Dataset 1 (Aalto University):")
# print(dataset1)
# dataset2 = dataset2['Label'].value_counts()
# print("\nDistribusi Data Dataset 2 (Kaggle):")
# print(dataset2)
# dataset3 = dataset3['URL'].count()
# print("\nJumlah Data URL Phishing Dataset 3 (OpenPhish):")
# print(dataset3)
# dataset4 = dataset4['URL'].count()
# print("\nJumlah Data URL Phishing Dataset 4 (PhishTank):")
# print(dataset4)
# dataset5 = dataset5['Label'].value_counts()
# print("\nDistribusi Data Dataset 5 (UCI MLR):")
# print(dataset5)

legitimate_dataset1 = dataset1[dataset1['Label'] == 0.0]
legitimate_dataset2 = dataset2[dataset2['Label'] == 'benign']
legitimate_dataset5 = dataset5[dataset5['Label'] == 0]

phishing_dataset1 = dataset1[dataset1['Label'] == 1.0]
phishing_dataset2 = dataset2[dataset2['Label'] == 'phishing']
phishing_dataset5 = dataset5[dataset5['Label'] == 1]

merged_legitimate = pd.concat([legitimate_dataset1, legitimate_dataset2, legitimate_dataset5], ignore_index=True)
merged_phishing = pd.concat([phishing_dataset1, phishing_dataset2, dataset3, dataset4, phishing_dataset5], ignore_index=True)

reduced_legitimate_dataset = merged_legitimate.sample(n=50, random_state=42,ignore_index=True)
reduced_phishing_dataset = merged_phishing.sample(n=50, random_state=42,ignore_index=True)

# reduced_legitimate_dataset.to_csv('dataset/reduced/reduced_legitimate_dataset.csv', index=False)
# reduced_phishing_dataset.to_csv('dataset/reduced/reduced_phishing_dataset.csv', index=False)

#############################################
#                                           #
#         AREA DATA TRANSFORMATION          #
#                                           #
#############################################

reduced_legitimate_dataset['Label'] = 0
reduced_phishing_dataset['Label'] = 1

# reduced_legitimate_dataset['Label'] = reduced_legitimate_dataset['Label'].astype(int)
# reduced_phishing_dataset['Label'] = reduced_phishing_dataset['Label'].astype(int)

#############################################
#                                           #
#          AREA DATA INTEGRATION            #
#                                           #
#############################################

final_dataset = pd.concat([reduced_legitimate_dataset, reduced_phishing_dataset], ignore_index=True)
final_dataset = final_dataset.sample(frac=1, random_state=42).reset_index(drop=True)
final_dataset.to_csv('dataset/final/final_dataset2.csv', index=False)

#############################################
#                                           #
#            AREA DATA CLEANING             #
#                                           #
#############################################

# final_dataset = pd.read_csv('dataset/final/final_features_dataset.csv')

# Remove duplicates
# final_dataset = final_dataset.drop_duplicates()

# # Check missing value
# missing_values = final_dataset.isnull().sum()
# print("Missing Values in Each Column:")
# print(missing_values)

# # Remove rows with missing values
# final_dataset = final_dataset.dropna()
# # Reset index after dropping rows
# final_dataset = final_dataset.reset_index(drop=True)

# Save the cleaned dataset
# final_dataset.to_csv('dataset/final/cleaned_final_dataset.csv', index=False)