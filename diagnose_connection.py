#!/usr/bin/env python3
"""
Diagnostic tool to identify backend connection issues
"""

import requests
import time
import sys

API_URL = "http://localhost:8000"

def check_port_open():
    """Check if port 8000 is open"""
    print("🔍 Checking if port 8000 is open...")
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()
    
    if result == 0:
        print("✅ Port 8000 is open")
        return True
    else:
        print("❌ Port 8000 is closed")
        print("💡 Start backend: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
        return False

def check_health_endpoint():
    """Check health endpoint with detailed timing"""
    print("\n🔍 Testing /health endpoint...")
    try:
        start = time.time()
        response = requests.get(f"{API_URL}/health", timeout=5)
        elapsed = time.time() - start
        
        print(f"✅ Response time: {elapsed:.2f}s")
        print(f"✅ Status code: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - backend not running")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_reload_endpoint():
    """Check reload-model endpoint"""
    print("\n🔍 Testing /reload-model endpoint...")
    try:
        start = time.time()
        response = requests.post(f"{API_URL}/reload-model", timeout=30)
        elapsed = time.time() - start
        
        print(f"✅ Response time: {elapsed:.2f}s")
        print(f"✅ Status code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Response: {response.json()}")
            return True
        else:
            print(f"⚠️ Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>30s)")
        print("💡 Backend may be processing, try again")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_predict_endpoint():
    """Check prediction endpoint"""
    print("\n🔍 Testing /predict endpoint...")
    
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
        start = time.time()
        response = requests.post(f"{API_URL}/predict", json=sample_data, timeout=30)
        elapsed = time.time() - start
        
        print(f"✅ Response time: {elapsed:.2f}s")
        print(f"✅ Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prediction: {result.get('prediction')}")
            print(f"✅ Probability: {result.get('probability'):.2%}")
            return True
        else:
            print(f"⚠️ Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>30s)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 70)
    print("🔧 BACKEND CONNECTION DIAGNOSTIC TOOL")
    print("=" * 70)
    print(f"Target: {API_URL}")
    print()
    
    # Run diagnostics
    port_ok = check_port_open()
    
    if not port_ok:
        print("\n❌ DIAGNOSIS: Backend is not running")
        print("\n💡 SOLUTION:")
        print("   1. Open a terminal")
        print("   2. Navigate to project directory")
        print("   3. Run: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
        return
    
    health_ok = check_health_endpoint()
    reload_ok = check_reload_endpoint()
    predict_ok = check_predict_endpoint()
    
    print("\n" + "=" * 70)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 70)
    
    results = {
        "Port 8000 Open": port_ok,
        "Health Endpoint": health_ok,
        "Reload Endpoint": reload_ok,
        "Predict Endpoint": predict_ok
    }
    
    for check, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {check}")
    
    print()
    
    if all(results.values()):
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Backend is fully functional")
    else:
        print("⚠️ SOME CHECKS FAILED")
        print("\n💡 TROUBLESHOOTING:")
        
        if not health_ok:
            print("   - Backend may be starting up, wait a few seconds")
        if not reload_ok:
            print("   - Check if model files exist in models/ directory")
            print("   - Run: python train_model.py")
        if not predict_ok:
            print("   - Ensure model is trained and loaded")
            print("   - Check backend logs for errors")
        
        print("\n📝 BACKEND LOGS:")
        print("   Check the terminal where backend is running for error messages")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")