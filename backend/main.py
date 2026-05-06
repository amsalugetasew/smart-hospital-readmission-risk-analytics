from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models import PatientData, PredictionResponse, AnalyticsResponse
from backend.predictor import predictor
import pandas as pd
import uvicorn

app = FastAPI(title="Smart Hospital Readmission Risk Analytics API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Check API and Model health."""
    if predictor.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model_loaded": True}

@app.post("/predict", response_model=PredictionResponse)
def predict_readmission(patient_data: PatientData):
    """Predict readmission risk for a single patient."""
    try:
        data_dict = patient_data.model_dump()
        result = predictor.predict(data_dict)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/analytics", response_model=AnalyticsResponse)
def get_analytics():
    """Get aggregated analytics from the synthetic dataset."""
    try:
        df = pd.read_csv("data/synthetic_hospital_data.csv")
        total_patients = len(df)
        readmission_rate = df["Readmitted"].value_counts(normalize=True).get("Yes", 0)
        avg_los = df["Length_of_Stay"].mean()
        
        # Calculate high risk percentage based on basic rules or model predictions if needed
        # We will use simple threshold for demo analytics
        # A more realistic approach would be running batch inference, but for analytics dashboard we can simulate it
        high_risk_percentage = len(df[(df["Age"] > 65) & (df["Previous_Admissions"] > 1)]) / total_patients
        
        return {
            "total_patients": total_patients,
            "readmission_rate": float(readmission_rate),
            "average_length_of_stay": float(avg_los),
            "high_risk_percentage": float(high_risk_percentage),
            "model_accuracy": predictor.metrics.get("accuracy", 0.0) if predictor.metrics else 0.0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reload-model")
def reload_model():
    """Reload the ML models from disk."""
    try:
        predictor.load_models()
        if predictor.model is None:
            raise HTTPException(status_code=500, detail="Failed to load models.")
        return {"status": "success", "message": "Models reloaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reloading models: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
