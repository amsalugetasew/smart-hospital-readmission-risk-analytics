from contextlib import asynccontextmanager
import os

print("=" * 80)
print("BACKEND STARTING - Loading environment variables...")
print("=" * 80)

# Load .env file before anything else so all env vars are available
try:
    from dotenv import load_dotenv
    import os
    # Load from project root (parent of backend directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(project_root, '.env')
    result = load_dotenv(dotenv_path=env_path, override=True)
    print(f"Loading .env from: {env_path}")
    print(f"load_dotenv() result: {result}")
    print(f"GROQ_API_KEY found: {'Yes' if os.getenv('GROQ_API_KEY') else 'No'}")
    if os.getenv('GROQ_API_KEY'):
        print(f"GROQ_API_KEY value: {os.getenv('GROQ_API_KEY')[:20]}...")
    print("=" * 80)
except ImportError:
    print("WARNING: python-dotenv not installed; relying on system env vars")
    print("=" * 80)
except Exception as e:
    print(f"ERROR loading .env: {e}")
    print("=" * 80)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models import PatientData, PredictionResponse, AnalyticsResponse
from backend.predictor import predictor
from backend.llm_advisor import router as llm_advisor_router, startup_load_model
import pandas as pd
import uvicorn
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load LLM model at startup (non-blocking for existing endpoints)
    await startup_load_model()
    yield


app = FastAPI(
    title="Smart Hospital Readmission Risk Analytics API",
    version="1.0",
    lifespan=lifespan,
)

# Register LLM advisor router
app.include_router(llm_advisor_router, prefix="/llm-advisor")

# Configure CORS for production and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",      # Local development
        "http://127.0.0.1:8501",      # Local development
    ],
    allow_origin_regex=r"https://.*\.streamlit\.app|https://.*\.streamlitapp\.com",  # Streamlit Cloud (both domains)
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
        # Check for uploaded dataset first, then fall back to default
        uploaded_path = "data/uploaded_dataset.csv"
        default_path = "data/hospital_readmission_dataset.csv"
        
        if os.path.exists(uploaded_path):
            df = pd.read_csv(uploaded_path)
        elif os.path.exists(default_path):
            df = pd.read_csv(default_path)
        else:
            raise HTTPException(status_code=404, detail="No dataset found")
        
        total_patients = len(df)
        readmission_rate = (df["label"] == 1).sum() / total_patients if "label" in df.columns else 0.0
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
