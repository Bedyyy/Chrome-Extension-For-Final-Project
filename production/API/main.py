from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib

from feature_extractor import extract_features

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    model = joblib.load('phishing_detector_model.joblib')
    print("Model berhasil dimuat.")
except FileNotFoundError:
    print("Error: File model tidak ditemukan. Pastikan 'phishing_detector_model.joblib' ada di folder yang sama.")
    model = None

class URLPayload(BaseModel):
    url: str

@app.get("/")
async def root():
    return {"message": "Phishing detection API is running!"}

@app.post("/predict/")
async def predict_phishing(payload: URLPayload):
    if model is None:
        return {"error": "Model belum dimuat."}

    features_df = extract_features(payload.url)
    
    features_dict = features_df.iloc[0].to_dict()

    prediction_result = model.predict(features_df)
    
    label = "phishing" if prediction_result[0] == 1 else "safe"
    
    print(f"Hasil prediksi: {label}")
    
    return {
        "prediction": label, 
        "url": payload.url,
        "features": features_dict
    }
