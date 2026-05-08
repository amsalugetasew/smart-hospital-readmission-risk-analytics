#!/usr/bin/env python3
"""
Test script to verify the updated validation logic
"""

import sys
import os
import pandas as pd

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.data_upload import validate_dataset_columns, standardize_dataset

def test_validation():
    """Test the updated validation with various treatment types"""
    print("🧪 Testing updated validation logic...")
    
    # Create test data with various treatment types including 'conservative'
    test_data = {
        'season': ['Spring', 'Summer', 'Fall', 'Winter'],
        'age': [65, 45, 78, 52],
        'gender': ['Male', 'Female', 'Male', 'Female'],
        'region': ['North', 'South', 'Central', 'West'],
        'primary_diagnosis': ['Diabetes', 'Hypertension', 'Heart Disease', 'Pneumonia'],
        'comorbidities_count': [2, 1, 3, 1],
        'length_of_stay': [5, 3, 7, 4],
        'treatment_type': ['conservative', 'medical', 'surgical', 'palliative'],  # Including 'conservative'
        'medications_count': [5, 3, 8, 4],
        'followup_visits_last_year': [3, 2, 4, 1],
        'prev_readmissions': [1, 0, 2, 0],
        'insurance_type': ['Private', 'Medicare', 'Medicaid', 'Private'],
        'discharge_disposition': ['Home', 'Rehab', 'Home', 'Home Health'],
        'readmission_risk_score': [0.5, 0.3, 0.8, 0.4],
        'label': [1, 0, 1, 0]
    }
    
    df = pd.DataFrame(test_data)
    
    # Test validation
    is_valid, message, validation_info = validate_dataset_columns(df)
    
    print(f"✅ Validation result: {message}")
    print(f"📊 Valid: {is_valid}")
    
    if 'warnings' in validation_info:
        print(f"⚠️  Warnings: {validation_info['warnings']}")
    
    # Test standardization
    if is_valid:
        df_standardized = standardize_dataset(df)
        print(f"🔧 Standardized treatment types: {df_standardized['treatment_type'].unique()}")
    
    return is_valid

if __name__ == "__main__":
    success = test_validation()
    if success:
        print("\n🎉 Validation test passed! 'Conservative' and other treatment types are now accepted.")
    else:
        print("\n❌ Validation test failed!")
    
    input("\nPress Enter to exit...")