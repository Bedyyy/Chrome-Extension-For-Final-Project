import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix

print("Memuat dan mempersiapkan data...")
dataset = pd.read_csv("final_featured_dataset_skripsi.csv")
dataset = dataset.drop(columns=['URL', 'Have_IP', 'Have_At', 'Redirection', 'https_Domain'], axis=1).copy()
dataset.dropna(inplace=True)

X = dataset.drop(columns=['Label'])
y = dataset['Label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('selector', SelectKBest(score_func=f_classif)),
    ('classifier', DecisionTreeClassifier(random_state=42))
])

param_grid = {
    'selector__k': [5, 10, 15, 20, 25, 'all'],
    'classifier__criterion': ['gini', 'entropy'],
    'classifier__max_depth': [5, 10, 15, 20, 25, 30, 35, 40, None],
    'classifier__min_samples_split': [2, 3, 4, 5, 6, 7, 8, 9, 10],
    'classifier__min_samples_leaf': [1, 2, 3, 4],
    'classifier__class_weight': ['balanced']
}

print("Memulai Grid Search dengan Pipeline...")
grid_search = GridSearchCV(
    estimator=pipeline,
    param_grid=param_grid,
    cv=5,
    scoring='f1_weighted',
    n_jobs=-1,
    verbose=2
)

grid_search.fit(X_train, y_train)

print("\n==============================================")
print("Hyperparameter Terbaik Ditemukan untuk Seluruh Pipeline:")
print(grid_search.best_params_)
print("Skor F1 terbaik selama pencarian:", grid_search.best_score_)
print("==============================================")

print("\nMengevaluasi Pipeline terbaik pada set pengujian...")
best_pipeline = grid_search.best_estimator_
y_pred = best_pipeline.predict(X_test)

print("\nLaporan Klasifikasi:")
print(classification_report(y_test, y_pred))

print("Matriks Konfusi:")
print(confusion_matrix(y_test, y_pred))

print("\nMenyimpan model menjadi file...")

final_model = grid_search.best_estimator_

joblib.dump(final_model, 'phishing_detector_model.joblib')

print("Model disimpan sebagai 'phishing_detector_model.joblib'")