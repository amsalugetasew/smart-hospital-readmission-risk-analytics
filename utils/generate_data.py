import pandas as pd
import numpy as np
import os

def generate_synthetic_data(num_samples=5000, output_path="data/synthetic_hospital_data.csv"):
    np.random.seed(42)
    
    # Basic Demographics
    patient_ids = [f"PID_{str(i).zfill(5)}" for i in range(1, num_samples + 1)]
    age = np.random.randint(18, 90, size=num_samples)
    gender = np.random.choice(['Male', 'Female'], size=num_samples)
    
    # Biometrics
    height_cm = np.random.normal(loc=170, scale=10, size=num_samples)
    weight_kg = np.random.normal(loc=75, scale=15, size=num_samples)
    bmi = weight_kg / ((height_cm / 100) ** 2)
    
    # Vitals
    sys_bp = np.random.normal(loc=120, scale=15, size=num_samples).astype(int)
    dia_bp = np.random.normal(loc=80, scale=10, size=num_samples).astype(int)
    blood_pressure = [f"{s}/{d}" for s, d in zip(sys_bp, dia_bp)]
    heart_rate = np.random.normal(loc=75, scale=12, size=num_samples).astype(int)
    
    # Medical History (Boolean/Categorical)
    diabetes = np.random.choice(['Yes', 'No'], size=num_samples, p=[0.15, 0.85])
    hypertension = np.where((sys_bp > 140) | (dia_bp > 90), 'Yes', np.random.choice(['Yes', 'No'], size=num_samples, p=[0.2, 0.8]))
    heart_disease = np.random.choice(['Yes', 'No'], size=num_samples, p=[0.1, 0.9])
    
    # Lifestyle
    smoking_status = np.random.choice(['Never', 'Former', 'Current'], size=num_samples, p=[0.6, 0.2, 0.2])
    alcohol_use = np.random.choice(['None', 'Occasional', 'Frequent'], size=num_samples, p=[0.4, 0.5, 0.1])
    
    # Hospitalization details
    previous_admissions = np.random.poisson(lam=0.5, size=num_samples)
    length_of_stay = np.random.poisson(lam=4, size=num_samples)
    length_of_stay = np.clip(length_of_stay, 1, 30)
    
    diagnoses = ['Pneumonia', 'Heart Failure', 'COPD', 'Diabetes Complication', 'Sepsis', 'Kidney Failure', 'Stroke', 'Other']
    diagnosis = np.random.choice(diagnoses, size=num_samples, p=[0.15, 0.15, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2])
    
    # Labs & Meds
    lab_results = np.random.choice(['Normal', 'Abnormal'], size=num_samples, p=[0.7, 0.3])
    cholesterol_level = np.random.choice(['Normal', 'Borderline', 'High'], size=num_samples, p=[0.5, 0.3, 0.2])
    glucose_level = np.random.normal(loc=100, scale=25, size=num_samples).astype(int)
    medication_adherence = np.random.choice(['High', 'Medium', 'Low'], size=num_samples, p=[0.5, 0.3, 0.2])
    
    # Admin details
    insurance_type = np.random.choice(['Private', 'Medicare', 'Medicaid', 'Uninsured'], size=num_samples)
    discharge_type = np.random.choice(['Home', 'Skilled Nursing', 'Rehabilitation', 'Against Medical Advice'], size=num_samples, p=[0.7, 0.15, 0.1, 0.05])
    follow_up_required = np.random.choice(['Yes', 'No'], size=num_samples, p=[0.8, 0.2])
    
    # Target Variable: Readmitted
    # We create some correlation with features
    risk_score = (
        (age > 65) * 1.5 + 
        (previous_admissions > 1) * 2.0 + 
        (diabetes == 'Yes') * 1.0 + 
        (hypertension == 'Yes') * 1.0 + 
        (heart_disease == 'Yes') * 1.5 + 
        (lab_results == 'Abnormal') * 1.2 + 
        (medication_adherence == 'Low') * 1.5 +
        (length_of_stay > 7) * 1.0 +
        (discharge_type != 'Home') * 1.0
    )
    
    # Convert score to probability
    prob_readmit = 1 / (1 + np.exp(-(risk_score - 4) * 0.5))
    readmitted = (np.random.rand(num_samples) < prob_readmit).astype(int)
    readmitted = np.where(readmitted == 1, 'Yes', 'No')
    
    # Create DataFrame
    df = pd.DataFrame({
        'Patient_ID': patient_ids,
        'Age': age,
        'Gender': gender,
        'Weight_kg': np.round(weight_kg, 1),
        'Height_cm': np.round(height_cm, 1),
        'BMI': np.round(bmi, 1),
        'Blood_Pressure': blood_pressure,
        'Heart_Rate': heart_rate,
        'Diabetes': diabetes,
        'Hypertension': hypertension,
        'Heart_Disease': heart_disease,
        'Smoking_Status': smoking_status,
        'Alcohol_Use': alcohol_use,
        'Previous_Admissions': previous_admissions,
        'Length_of_Stay': length_of_stay,
        'Diagnosis': diagnosis,
        'Lab_Result': lab_results,
        'Cholesterol_Level': cholesterol_level,
        'Glucose_Level': glucose_level,
        'Medication_Adherence': medication_adherence,
        'Insurance_Type': insurance_type,
        'Discharge_Type': discharge_type,
        'Follow_Up_Required': follow_up_required,
        'Readmitted': readmitted
    })
    
    # Introduce some missing values (for Phase 1 requirement)
    df.loc[np.random.choice(df.index, size=int(num_samples*0.05)), 'BMI'] = np.nan
    df.loc[np.random.choice(df.index, size=int(num_samples*0.02)), 'Cholesterol_Level'] = np.nan
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated {num_samples} records and saved to {output_path}")
    print(f"Readmission Rate: {df['Readmitted'].value_counts(normalize=True).get('Yes', 0):.2%}")
    return df

if __name__ == "__main__":
    generate_synthetic_data()
