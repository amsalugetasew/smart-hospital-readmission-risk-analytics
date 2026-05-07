"""
Data upload and validation utilities for custom datasets
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Tuple, Optional, Dict, Any
import os

def validate_dataset_columns(df: pd.DataFrame) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validate that uploaded dataset has required columns and structure
    
    Returns:
        - is_valid: bool
        - message: str (error message or success message)
        - info: dict with validation details
    """
    
    # Required columns for the model
    required_columns = {
        'season', 'age', 'gender', 'region', 'primary_diagnosis',
        'comorbidities_count', 'length_of_stay', 'treatment_type',
        'medications_count', 'followup_visits_last_year', 'prev_readmissions',
        'insurance_type', 'discharge_disposition', 'readmission_risk_score'
    }
    
    # Optional columns (identifiers and target)
    optional_columns = {'patient_id', 'admission_date', 'label'}
    
    # Check if dataset has required columns
    df_columns = set(df.columns.str.lower())
    missing_required = required_columns - df_columns
    
    validation_info = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'required_columns_found': len(required_columns & df_columns),
        'required_columns_total': len(required_columns),
        'missing_columns': list(missing_required),
        'extra_columns': list(df_columns - required_columns - optional_columns),
        'has_target': 'label' in df_columns,
        'has_patient_id': 'patient_id' in df_columns
    }
    
    if missing_required:
        return False, f"Missing required columns: {', '.join(missing_required)}", validation_info
    
    # Check data types and ranges
    try:
        # Numerical columns validation
        numerical_cols = ['age', 'comorbidities_count', 'length_of_stay', 
                         'medications_count', 'followup_visits_last_year', 
                         'prev_readmissions', 'readmission_risk_score']
        
        for col in numerical_cols:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    return False, f"Column '{col}' must be numerical", validation_info
                
                # Specific range validations
                if col == 'age' and (df[col].min() < 0 or df[col].max() > 150):
                    return False, f"Age values should be between 0-150", validation_info
                
                if col == 'readmission_risk_score' and (df[col].min() < 0 or df[col].max() > 1):
                    return False, f"Readmission risk score should be between 0-1", validation_info
        
        # Categorical columns validation (more flexible)
        categorical_validations = {
            'gender': ['male', 'female', 'm', 'f', 'man', 'woman'],
            'season': ['spring', 'summer', 'fall', 'winter', 'autumn'],
            'region': ['north', 'south', 'east', 'west', 'central', 'northeast', 'northwest', 'southeast', 'southwest', 'midwest'],
            'treatment_type': ['medical', 'surgical', 'interventional', 'emergency', 'outpatient', 'inpatient'],
            'insurance_type': ['private', 'medicare', 'medicaid', 'self-pay', 'self pay', 'commercial', 'government', 'uninsured'],
            'discharge_disposition': ['home', 'home health', 'skilled nursing', 'rehab', 'other', 'snf', 'nursing home', 'hospice', 'deceased', 'transfer']
        }
        
        # Make validation more lenient - only warn about unusual values, don't fail
        validation_warnings = []
        for col, valid_values in categorical_validations.items():
            if col in df.columns:
                unique_values = df[col].str.lower().unique()
                invalid_values = [v for v in unique_values if v not in valid_values and pd.notna(v)]
                if invalid_values:
                    validation_warnings.append(f"Unusual values in '{col}': {invalid_values}")
        
        # Add warnings to validation info but don't fail validation
        validation_info['warnings'] = validation_warnings
        
        return True, "Dataset validation successful!", validation_info
        
    except Exception as e:
        return False, f"Validation error: {str(e)}", validation_info

def standardize_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize uploaded dataset to match expected format
    """
    df_clean = df.copy()
    
    # Standardize column names (lowercase)
    df_clean.columns = df_clean.columns.str.lower().str.strip()
    
    # Standardize categorical values (more comprehensive mappings)
    categorical_mappings = {
        'gender': {'m': 'Male', 'f': 'Female', 'male': 'Male', 'female': 'Female', 
                  'man': 'Male', 'woman': 'Female'},
        'season': {'spring': 'Spring', 'summer': 'Summer', 'fall': 'Fall', 
                  'winter': 'Winter', 'autumn': 'Fall'},
        'region': {'north': 'North', 'south': 'South', 'east': 'East', 'west': 'West',
                  'central': 'Central', 'northeast': 'Northeast', 'northwest': 'Northwest',
                  'southeast': 'Southeast', 'southwest': 'Southwest', 'midwest': 'Midwest'},
        'treatment_type': {'medical': 'Medical', 'surgical': 'Surgical', 
                          'interventional': 'Interventional', 'emergency': 'Emergency',
                          'outpatient': 'Outpatient', 'inpatient': 'Inpatient'},
        'insurance_type': {'private': 'Private', 'medicare': 'Medicare', 
                          'medicaid': 'Medicaid', 'self-pay': 'Self-Pay', 'self pay': 'Self-Pay',
                          'commercial': 'Private', 'government': 'Medicare', 'uninsured': 'Self-Pay'},
        'discharge_disposition': {'home': 'Home', 'home health': 'Home Health', 
                                'skilled nursing': 'Skilled Nursing', 'rehab': 'Rehab', 
                                'other': 'Other', 'snf': 'Skilled Nursing', 'nursing home': 'Skilled Nursing',
                                'hospice': 'Other', 'deceased': 'Other', 'transfer': 'Other'}
    }
    
    for col, mapping in categorical_mappings.items():
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].str.lower().map(mapping).fillna(df_clean[col])
    
    # Handle missing values
    numerical_cols = ['age', 'comorbidities_count', 'length_of_stay', 
                     'medications_count', 'followup_visits_last_year', 
                     'prev_readmissions', 'readmission_risk_score']
    
    for col in numerical_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            if col == 'readmission_risk_score':
                df_clean[col] = df_clean[col].fillna(0.5)  # Default medium risk
            else:
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
    
    return df_clean

def load_uploaded_file(uploaded_file) -> Optional[pd.DataFrame]:
    """
    Load uploaded CSV or Excel file
    """
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload CSV or Excel files.")
            return None
        
        return df
    
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def save_uploaded_dataset(df: pd.DataFrame, filename: str = "uploaded_dataset.csv") -> str:
    """
    Save uploaded dataset to data folder
    """
    try:
        filepath = os.path.join("data", filename)
        df.to_csv(filepath, index=False)
        return filepath
    except Exception as e:
        st.error(f"Error saving dataset: {str(e)}")
        return None

def get_dataset_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get summary statistics for the dataset
    """
    summary = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().sum(),
        'duplicate_rows': df.duplicated().sum(),
        'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
    }
    
    # Target distribution if available
    if 'label' in df.columns:
        summary['target_distribution'] = df['label'].value_counts().to_dict()
        summary['readmission_rate'] = df['label'].mean() if df['label'].dtype in ['int64', 'float64'] else None
    
    # Numerical columns summary
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    if len(numerical_cols) > 0:
        summary['numerical_columns'] = len(numerical_cols)
        summary['numerical_summary'] = df[numerical_cols].describe().to_dict()
    
    # Categorical columns summary
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        summary['categorical_columns'] = len(categorical_cols)
        summary['categorical_summary'] = {col: df[col].nunique() for col in categorical_cols}
    
    return summary