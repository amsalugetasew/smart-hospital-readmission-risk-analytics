"""
Comprehensive script to fix backend connection issues
"""

import requests
import subprocess
import time
import os
import sys

def check_port_usage():
    """Check what's using port 8000"""
    print("🔍 Checking port 8000 usage...")
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, shell=True)
        lines = result.stdout.split('\n')
        port_8000_lines = [line for line in lines if ':8000' in line]
        
        if port_8000_lines:
            print("📊 Port 8000 usage:")
            for line in port_8000_lines:
                print(f"   {line.strip()}")
        else:
            print("❌ Nothing is using port 8000")
        return len(port_8000_lines) > 0
    except Exception as e:
        print(f"❌ Error checking port usage: {e}")
        return False

def test_backend_urls():
    """Test different backend URLs"""
    urls = [
        "http://localhost:8000/health",
        "http://127.0.0.1:8000/health",
        "http://0.0.0.0:8000/health"
    ]
    
    print("\n🔍 Testing backend URLs...")
    working_urls = []
    
    for url in urls:
        try:
            print(f"Testing: {url}")
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"   ✅ SUCCESS: {response.json()}")
                working_urls.append(url)
            else:
                print(f"   ❌ FAILED: Status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"   ❌ CONNECTION ERROR")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    return working_urls

def check_backend_process():
    """Check if uvicorn process is running"""
    print("\n🔍 Checking for uvicorn processes...")
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True, shell=True)
        if 'python' in result.stdout.lower() or 'uvicorn' in result.stdout.lower():
            print("✅ Python processes found (backend might be running)")
        else:
            print("❌ No Python/uvicorn processes found")
    except Exception as e:
        print(f"❌ Error checking processes: {e}")

def suggest_fixes(working_urls, port_in_use):
    """Suggest fixes based on findings"""
    print("\n" + "=" * 60)
    print("💡 SUGGESTED FIXES")
    print("=" * 60)
    
    if not port_in_use:
        print("🚨 ISSUE: Nothing is running on port 8000")
        print("📋 SOLUTION:")
        print("   1. Start the backend server:")
        print("      uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
        print("   2. Wait for it to show 'Application startup complete'")
        print("   3. Then restart Streamlit")
        return
    
    if not working_urls:
        print("🚨 ISSUE: Backend is running but not accessible")
        print("📋 SOLUTIONS:")
        print("   1. Check if backend started successfully (no errors in terminal)")
        print("   2. Try restarting backend with --reload flag")
        print("   3. Check Windows Firewall settings")
        print("   4. Try running on different port:")
        print("      uvicorn backend.main:app --host 127.0.0.1 --port 8001")
        return
    
    if working_urls:
        print("✅ GOOD NEWS: Backend is accessible!")
        print(f"🔗 Working URLs: {working_urls}")
        
        if "http://localhost:8000/health" in working_urls:
            print("✅ Frontend should work with current settings")
        else:
            print("⚠️  Frontend might need URL update")
            print(f"   Update API_URL in frontend/app.py to: {working_urls[0].replace('/health', '')}")

def main():
    print("🔧 BACKEND CONNECTION DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('backend/main.py'):
        print("❌ Error: Run this from the project root directory")
        print("   Current directory:", os.getcwd())
        return
    
    # Run diagnostics
    port_in_use = check_port_usage()
    working_urls = test_backend_urls()
    check_backend_process()
    
    # Suggest fixes
    suggest_fixes(working_urls, port_in_use)
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. Follow the suggested fixes above")
    print("2. Run 'python quick_test.py' to verify")
    print("3. Restart Streamlit: 'streamlit run frontend/app.py'")
    print("=" * 60)

if __name__ == "__main__":
    main()