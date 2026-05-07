"""
Quick test to check if backend is accessible
Run this while your backend is running
"""

import requests
import sys

def test_backend():
    urls_to_test = [
        "http://localhost:8000/health",
        "http://127.0.0.1:8000/health", 
        "http://0.0.0.0:8000/health"
    ]
    
    print("🔍 Testing backend accessibility...")
    print("=" * 50)
    
    for url in urls_to_test:
        try:
            print(f"\nTesting: {url}")
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print(f"✅ SUCCESS: {response.json()}")
            else:
                print(f"❌ FAILED: Status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ CONNECTION ERROR: Cannot connect")
        except requests.exceptions.Timeout:
            print(f"❌ TIMEOUT: Request timed out")
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("💡 If all tests fail, the backend is not running or not accessible")
    print("💡 If some work, note which URL works and update the frontend")

if __name__ == "__main__":
    test_backend()