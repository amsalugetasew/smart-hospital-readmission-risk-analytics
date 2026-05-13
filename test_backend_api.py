#!/usr/bin/env python3
"""Test script to verify the backend API is working correctly"""

import requests
import json
import sys

API_URL = "http://localhost:8000"

print("=" * 80)
print("TESTING BACKEND API")
print("=" * 80)

# Test 1: Root endpoint
print("\n[TEST 1] Testing root endpoint...")
try:
    response = requests.get(f"{API_URL}/", timeout=5)
    if response.status_code == 200:
        print("✅ Root endpoint working")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Root endpoint failed: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Cannot connect to backend: {e}")
    print("   Make sure the backend is running on port 8000")
    sys.exit(1)

# Test 2: LLM Advisor Status
print("\n[TEST 2] Testing LLM advisor status endpoint...")
try:
    response = requests.get(f"{API_URL}/llm-advisor/status", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print("✅ LLM advisor status endpoint working")
        print(f"   Mode: {data.get('mode')}")
        print(f"   Model Name: {data.get('model_name')}")
        print(f"   Available: {data.get('available')}")
        
        if data.get('mode') == 'none' or not data.get('available'):
            print("\n❌ LLM advisor is NOT configured!")
            print("   Expected: mode='groq', available=True")
            print("   This means the backend did not load the .env file correctly")
            sys.exit(1)
        else:
            print("\n✅ LLM advisor is properly configured!")
    else:
        print(f"❌ Status endpoint failed: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error checking status: {e}")
    sys.exit(1)

# Test 3: LLM Advisor Analyze (with sample data)
print("\n[TEST 3] Testing LLM advisor analyze endpoint...")
try:
    payload = {
        "clinical_notes": "Patient presents with chest pain and shortness of breath. BP 140/90, HR 95.",
        "patient_history_text": None,
        "lab_results_text": None
    }
    
    print("   Sending test analysis request...")
    response = requests.post(
        f"{API_URL}/llm-advisor/analyze",
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ LLM advisor analyze endpoint working!")
        print(f"   Admit Decision: {data.get('admit_decision')}")
        print(f"   Admission Level: {data.get('admission_recommendation')}")
        print(f"   Key Factors: {len(data.get('key_factors', []))} found")
        print(f"   Risk Indicators: {len(data.get('risk_indicators', []))} found")
        print(f"   Recommended Tasks: {len(data.get('recommended_tasks', []))} found")
    elif response.status_code == 503:
        print("❌ LLM advisor not configured (503 error)")
        print(f"   Response: {response.json()}")
        print("\n   This means the backend is running but the LLM is not loaded.")
        print("   Check the backend console output for error messages.")
        sys.exit(1)
    else:
        print(f"❌ Analyze endpoint failed: {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error testing analyze endpoint: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED - Backend is working correctly!")
print("=" * 80)
