from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class PatientData(BaseModel):
    """Patient data model matching hospital_readmission_dataset.csv structure"""
    season: str
    age: int
    gender: str
    region: str
    primary_diagnosis: str
    comorbidities_count: int
    length_of_stay: int
    treatment_type: str
    medications_count: int
    followup_visits_last_year: int
    prev_readmissions: int
    insurance_type: str
    discharge_disposition: str
    readmission_risk_score: float

class PredictionResponse(BaseModel):
    prediction: str  # "Readmitted" or "Not Readmitted"
    probability: float
    risk_category: str
    feature_importance: Dict[str, float]
    model_type: Optional[str] = None

class AnalyticsResponse(BaseModel):
    total_patients: int
    readmission_rate: float
    average_length_of_stay: float
    high_risk_percentage: float
    model_accuracy: float
