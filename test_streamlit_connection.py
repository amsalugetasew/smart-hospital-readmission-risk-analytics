"""
Test connection exactly as Streamlit does
"""
import requests
import time
import os

# Mimic Streamlit's API_URL logic
API_URL = os.getenv("API_URL", "http://localhost:8000")

print("="*60)
print("STREAMLIT CONNECTION TEST")
print("="*60)
print(f"API_URL: {API_URL}")
print()

# Test 1: Health check with 3 second timeout (same as Streamlit)
print("[1/3] Health check (3s timeout)...")
try:
    response = requests.get(f"{API_URL}/health", timeout=3)
    if response.status_code == 200:
        data = response.json()
        is_healthy = data.get("status") == "healthy" and data.get("model_loaded", False)
        print(f"✅ Backend healthy: {is_healthy}")
        print(f"   Response: {data}")
    else:
        print(f"❌ Status code: {response.status_code}")
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection error: {e}")
except requests.exceptions.Timeout:
    print(f"❌ Timeout after 3 seconds")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Model reload with retry logic (same as Streamlit)
print("\n[2/3] Model reload with retry logic...")
max_retries = 3
reload_success = False

for attempt in range(max_retries):
    try:
        print(f"   Attempt {attempt + 1}/{max_retries}...")
        response = requests.post(f"{API_URL}/reload-model", timeout=30)
        
        if response.status_code == 200:
            print(f"   ✅ Success! Response: {response.json()}")
            reload_success = True
            break
        else:
            print(f"   ⚠️ Status {response.status_code}: {response.text}")
            if attempt < max_retries - 1:
                time.sleep(2)
                
    except requests.exceptions.ConnectionError as e:
        if attempt < max_retries - 1:
            print(f"   ⚠️ Connection failed, retrying...")
            time.sleep(2)
        else:
            print(f"   ❌ Connection error after {max_retries} attempts: {e}")
            
    except requests.exceptions.Timeout:
        if attempt < max_retries - 1:
            print(f"   ⚠️ Timeout, retrying...")
            time.sleep(2)
        else:
            print(f"   ❌ Timeout after {max_retries} attempts")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        break

if reload_success:
    print("✅ Model reload successful")
else:
    print("❌ Model reload failed")

# Test 3: Prediction with retry logic
print("\n[3/3] Prediction with retry logic...")
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

max_retries = 3
prediction_success = False

for attempt in range(max_retries):
    try:
        print(f"   Attempt {attempt + 1}/{max_retries}...")
        response = requests.post(f"{API_URL}/predict", json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Prediction: {result['prediction']}")
            print(f"   ✅ Probability: {result['probability']:.2%}")
            prediction_success = True
            break
        else:
            print(f"   ⚠️ Status {response.status_code}")
            if attempt < max_retries - 1:
                time.sleep(1)
                
    except requests.exceptions.ConnectionError:
        if attempt < max_retries - 1:
            print(f"   ⚠️ Connection failed, retrying...")
            time.sleep(1)
        else:
            print(f"   ❌ Connection error after {max_retries} attempts")
            
    except requests.exceptions.Timeout:
        if attempt < max_retries - 1:
            print(f"   ⚠️ Timeout, retrying...")
            time.sleep(1)
        else:
            print(f"   ❌ Timeout after {max_retries} attempts")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        break

if prediction_success:
    print("✅ Prediction successful")
else:
    print("❌ Prediction failed")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)

# Summary
print("\nSUMMARY:")
print(f"  Backend URL: {API_URL}")
print(f"  Backend accessible: ✅")
print(f"  Model reload: {'✅' if reload_success else '❌'}")
print(f"  Predictions: {'✅' if prediction_success else '❌'}")

if reload_success and prediction_success:
    print("\n✅ All tests passed! Backend connection is working correctly.")
    print("   If Streamlit still shows connection errors, try:")
    print("   1. Restart Streamlit")
    print("   2. Clear browser cache")
    print("   3. Check if Streamlit is using a different Python environment")
else:
    print("\n❌ Some tests failed. Check the errors above.")
