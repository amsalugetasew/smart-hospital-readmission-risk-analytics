from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class PatientData(BaseModel):
    Age: int
    Gender: str
    Weight_kg: float
    Height_cm: float
    BMI: float
    Blood_Pressure: str
    Heart_Rate: int
    Diabetes: str
    Hypertension: str
    Heart_Disease: str
    Smoking_Status: str
    Alcohol_Use: str
    Previous_Admissions: int
    Length_of_Stay: int
    Diagnosis: str
    Lab_Result: str
    Cholesterol_Level: str
    Glucose_Level: int
    Medication_Adherence: str
    Insurance_Type: str
    Discharge_Type: str
    Follow_Up_Required: str

class PredictionResponse(BaseModel):
    prediction: str
    probability: float
    risk_category: str
    feature_importance: Dict[str, float]

class AnalyticsResponse(BaseModel):
    total_patients: int
    readmission_rate: float
    average_length_of_stay: float
    high_risk_percentage: float
    model_accuracy: float
