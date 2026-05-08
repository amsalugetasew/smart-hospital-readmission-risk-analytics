"""
Comprehensive backend connection test
"""
import requests
import json

API_URL = "http://localhost:8000"

print("="*60)
print("BACKEND CONNECTION DIAGNOSTIC")
print("="*60)

# Test 1: Health Check
print("\n[1/4] Testing /health endpoint...")
try:
    response = requests.get(f"{API_URL}/health", timeout=5)
    print(f"✅ Status Code: {response.status_code}")
    print(f"✅ Response: {response.json()}")
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection Error: {e}")
    print("   Backend is not running or not accessible")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test 2: Root Endpoint
print("\n[2/4] Testing / (root) endpoint...")
try:
    response = requests.get(f"{API_URL}/", timeout=5)
    print(f"✅ Status Code: {response.status_code}")
    print(f"✅ Response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Reload Model Endpoint
print("\n[3/4] Testing /reload-model endpoint...")
try:
    response = requests.post(f"{API_URL}/reload-model", timeout=10)
    print(f"✅ Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Response: {response.json()}")
    else:
        print(f"❌ Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Predict Endpoint
print("\n[4/4] Testing /predict endpoint...")
test_data = {
    "season": "winter",
    "age": 65,
    "gender": "Male",
    "region": "north",
    "primary_diagnosis": "Diabetes",
    "comorbidities_count": 2,
    "length_of_stay": 5,
    "treatment_type": "surgical",
    "medications_count": 3,
    "followup_visits_last_year": 2,
    "prev_readmissions": 1,
    "insurance_type": "private",
    "discharge_disposition": "home",
    "readmission_risk_score": 0.65
}

try:
    response = requests.post(f"{API_URL}/predict", json=test_data, timeout=10)
    print(f"✅ Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Prediction: {result['prediction']}")
        print(f"✅ Probability: {result['probability']:.2%}")
        print(f"✅ Risk Category: {result['risk_category']}")
    else:
        print(f"❌ Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)
