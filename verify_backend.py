"""
Verify that the backend models.py has the correct PatientData structure
AND check if the running backend server is using the new or old code
"""

import sys
import importlib.util
import requests

print("=" * 60)
print("🔍 BACKEND VERIFICATION SCRIPT")
print("=" * 60)

# Step 1: Verify backend/models.py file content
print("\n[1/2] Verifying backend/models.py file content...")
try:
    spec = importlib.util.spec_from_file_location("models", "backend/models.py")
    models = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models)

    patient_data_fields = list(models.PatientData.__fields__.keys())
    
    expected = ['season', 'age', 'gender', 'region', 'primary_diagnosis', 
                'comorbidities_count', 'length_of_stay', 'treatment_type',
                'medications_count', 'followup_visits_last_year', 'prev_readmissions',
                'insurance_type', 'discharge_disposition', 'readmission_risk_score']
    
    if set(patient_data_fields) == set(expected):
        print("   ✅ backend/models.py has CORRECT structure (new dataset)")
        print(f"   Fields: {', '.join(patient_data_fields[:5])}... ({len(patient_data_fields)} total)")
    else:
        print("   ❌ backend/models.py has INCORRECT structure")
        missing = set(expected) - set(patient_data_fields)
        extra = set(patient_data_fields) - set(expected)
        if missing:
            print(f"   Missing: {missing}")
        if extra:
            print(f"   Extra: {extra}")
except Exception as e:
    print(f"   ❌ Error loading models.py: {e}")

# Step 2: Check if backend server is running and what it expects
print("\n[2/2] Checking if backend server is running...")
try:
    response = requests.get("http://localhost:8000/health", timeout=2)
    if response.status_code == 200:
        print("   ✅ Backend server is RUNNING at http://localhost:8000")
        
        # Try a test prediction to see what fields the server expects
        print("\n   Testing what fields the running server expects...")
        test_data = {
            "season": "Spring",
            "age": 65,
            "gender": "Male",
            "region": "North",
            "primary_diagnosis": "Diabetes",
            "comorbidities_count": 2,
            "length_of_stay": 5,
            "treatment_type": "Medical",
            "medications_count": 5,
            "followup_visits_last_year": 3,
            "prev_readmissions": 1,
            "insurance_type": "Private",
            "discharge_disposition": "Home",
            "readmission_risk_score": 0.5
        }
        
        try:
            pred_response = requests.post("http://localhost:8000/predict", json=test_data, timeout=5)
            if pred_response.status_code == 200:
                print("   ✅ Server accepts NEW dataset fields - EVERYTHING IS WORKING!")
                print("   🎉 You can now use the prediction feature in the frontend!")
            elif pred_response.status_code == 422:
                print("   ❌ Server expects OLD dataset fields - RESTART REQUIRED!")
                print("\n   The running server has old code in memory.")
                print("   You need to RESTART the backend server:")
                print("   1. Press Ctrl+C in the backend terminal")
                print("   2. Run: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
            else:
                print(f"   ⚠️  Unexpected response: {pred_response.status_code}")
                print(f"   {pred_response.text[:200]}")
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  Could not test prediction endpoint: {e}")
    else:
        print(f"   ⚠️  Backend returned status code: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ❌ Backend server is NOT RUNNING")
    print("\n   Start the backend server with:")
    print("   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
except requests.exceptions.Timeout:
    print("   ⚠️  Backend server timeout")
except Exception as e:
    print(f"   ⚠️  Error checking backend: {e}")

print("\n" + "=" * 60)
print("📋 SUMMARY")
print("=" * 60)
print("\nIf you see '❌ Server expects OLD dataset fields':")
print("→ The files are correct, but the server needs to be restarted")
print("→ See RESTART_INSTRUCTIONS.md for detailed steps")
print("\nIf you see '✅ Server accepts NEW dataset fields':")
print("→ Everything is working! You can use the prediction feature")
print("=" * 60)
