from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models import PatientData, PredictionResponse, AnalyticsResponse
from backend.predictor import predictor
import pandas as pd
import uvicorn
import os

app = FastAPI(title="Smart Hospital Readmission Risk Analytics API", version="1.0")

# Configure CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://*.streamlit.app",  # Streamlit Cloud
        "https://*.streamlitapp.com",  # Streamlit Cloud (old domain)
        "http://localhost:8501",  # Local development
        "http://127.0.0.1:8501",  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Root endpoint for health checks."""
    return {
        "message": "Smart Hospital Readmission Risk Analytics API",
        "status": "running",
        "version": "1.0"
    }

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
        # Check if model is loaded
        if predictor.model is None:
            raise HTTPException(
                status_code=503, 
                detail="Model not loaded. Please train a model first or ensure model files exist in the 'models' directory."
            )
        
        if predictor.preprocessor is None:
            raise HTTPException(
                status_code=503,
                detail="Preprocessor not loaded. Please train a model first."
            )
            
        data_dict = patient_data.model_dump()
        result = predictor.predict(data_dict)
        return result
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Prediction error: {error_details}")
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

@app.get("/analytics", response_model=AnalyticsResponse)
def get_analytics():
    """Get aggregated analytics from the hospital readmission dataset."""
    try:
        df = pd.read_csv("data/hospital_readmission_dataset.csv")
        total_patients = len(df)
        readmission_rate = (df["label"] == 1).sum() / total_patients
        avg_los = df["length_of_stay"].mean()
        
        # Calculate high risk percentage (readmission_risk_score > 0.7)
        high_risk_percentage = (df["readmission_risk_score"] > 0.7).sum() / total_patients
        
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
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
