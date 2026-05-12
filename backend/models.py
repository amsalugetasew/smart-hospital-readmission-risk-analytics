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


# ── LLM Medical Advisor models ───────────────────────────────────────────────

class LLMAnalysisRequest(BaseModel):
    """Request body for POST /llm-advisor/analyze."""
    clinical_notes: str                          # required, non-empty
    patient_history_text: Optional[str] = None
    lab_results_text: Optional[str] = None


class LLMAnalysisResponse(BaseModel):
    """Structured response from the LLM Medical Advisor."""
    admit_decision: str                  # "Admit" | "Do Not Admit" | "Undetermined"
    admission_recommendation: str        # "Home Treatment" | "Outpatient Care" | "Inpatient Admission" | "Undetermined"
    recommended_tasks: List[str]
    # ── Clinical reasoning fields ──────────────────────────────────────────
    key_factors: List[str]               # clinical features that drove the decision
    risk_indicators: List[str]           # specific risk signals found (e.g. elevated troponin)
    clinical_rationale: str              # brief explanation of why this decision was made
    # ── Metadata ──────────────────────────────────────────────────────────
    inputs_used: List[str]               # e.g. ["clinical_notes", "patient_history"]
    truncation_occurred: bool
    raw_output: Optional[str] = None     # populated when parsing fails
    error: Optional[str] = None          # populated on inference error
