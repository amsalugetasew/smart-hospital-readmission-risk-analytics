#!/usr/bin/env python3
"""
Test script to verify all backend endpoints are working
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing /health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_reload_model():
    """Test model reload endpoint"""
    print("\n🔍 Testing /reload-model endpoint...")
    try:
        response = requests.post(f"{API_URL}/reload-model", timeout=30)
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_predict():
    """Test prediction endpoint"""
    print("\n🔍 Testing /predict endpoint...")
    
    # Sample patient data
    sample_data = {
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
        response = requests.post(f"{API_URL}/predict", json=sample_data, timeout=30)
        print(f"✅ Status: {response.status_code}")
        result = response.json()
        print(f"✅ Prediction: {result.get('prediction')}")
        print(f"✅ Probability: {result.get('probability')}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_analytics():
    """Test analytics endpoint"""
    print("\n🔍 Testing /analytics endpoint...")
    try:
        response = requests.get(f"{API_URL}/analytics", timeout=5)
        print(f"✅ Status: {response.status_code}")
        result = response.json()
        print(f"✅ Total Patients: {result.get('total_patients')}")
        print(f"✅ Readmission Rate: {result.get('readmission_rate')}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 BACKEND ENDPOINT TESTING")
    print("=" * 60)
    print(f"Backend URL: {API_URL}")
    
    results = {
        "Health Check": test_health(),
        "Model Reload": test_reload_model(),
        "Prediction": test_predict(),
        "Analytics": test_analytics()
    }
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All backend endpoints are working correctly!")
    else:
        print("\n⚠️ Some endpoints failed. Please check backend logs.")
        print("\n💡 Make sure backend is running:")
        print("   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")