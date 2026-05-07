"""
Test script to debug frontend-backend connection issues
"""

import requests
import json

# Test configuration
API_URL = "http://127.0.0.1:8000"

def test_backend_connection():
    print("=" * 60)
    print("🔍 TESTING BACKEND CONNECTION")
    print("=" * 60)
    
    print(f"\n📡 Testing connection to: {API_URL}")
    
    # Test 1: Health check
    print("\n[1/4] Testing health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check successful: {data}")
        else:
            print(f"   ❌ Health check failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Analytics endpoint
    print("\n[2/4] Testing analytics endpoint...")
    try:
        response = requests.get(f"{API_URL}/analytics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Analytics successful: {data}")
        else:
            print(f"   ❌ Analytics failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Analytics error: {e}")
    
    # Test 3: Reload model endpoint
    print("\n[3/4] Testing reload-model endpoint...")
    try:
        response = requests.post(f"{API_URL}/reload-model", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Reload model successful: {data}")
        else:
            print(f"   ❌ Reload model failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Reload model error: {e}")
    
    # Test 4: Prediction endpoint
    print("\n[4/4] Testing prediction endpoint...")
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
        response = requests.post(f"{API_URL}/predict", json=test_data, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Prediction successful!")
            print(f"   📊 Result: {data['prediction']} ({data['probability']:.1%} probability)")
            print(f"   🎯 Risk Category: {data['risk_category']}")
        else:
            print(f"   ❌ Prediction failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Prediction error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ CONNECTION TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_backend_connection()