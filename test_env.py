#!/usr/bin/env python3
"""Test script to verify .env loading"""

import os
import sys

print("=" * 60)
print("Testing .env file loading")
print("=" * 60)

# Get project root
project_root = os.path.dirname(os.path.abspath(__file__))
print(f"\n1. Project root: {project_root}")

# Check if .env exists
env_path = os.path.join(project_root, '.env')
print(f"2. .env path: {env_path}")
print(f"3. .env exists: {os.path.exists(env_path)}")

# Try to load .env
try:
    from dotenv import load_dotenv
    print("4. python-dotenv is installed: Yes")
    
    # Load the .env file
    result = load_dotenv(dotenv_path=env_path, verbose=True, override=True)
    print(f"5. load_dotenv() result: {result}")
    
except ImportError:
    print("4. python-dotenv is installed: No")
    print("   Install it with: pip install python-dotenv")
    sys.exit(1)

# Check environment variables
print("\n" + "=" * 60)
print("Environment Variables")
print("=" * 60)

api_keys = {
    "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
    "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
    "HF_API_KEY": os.getenv("HF_API_KEY"),
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
}

for key, value in api_keys.items():
    if value:
        print(f"✅ {key}: {value[:20]}... (length: {len(value)})")
    else:
        print(f"❌ {key}: Not found")

# Test backend loading
print("\n" + "=" * 60)
print("Testing Backend Loading")
print("=" * 60)

try:
    # Add backend to path
    sys.path.insert(0, project_root)
    
    # Import backend modules
    from backend import llm_advisor
    
    print(f"✅ Backend module imported successfully")
    print(f"   Mode: {llm_advisor.llm_advisor.mode}")
    print(f"   Model available: {llm_advisor.llm_advisor.model_available}")
    print(f"   Model name: {llm_advisor.llm_advisor.llm_model_name}")
    
    # Try to load the model
    llm_advisor.llm_advisor.load_model()
    
    print(f"\n   After load_model():")
    print(f"   Mode: {llm_advisor.llm_advisor.mode}")
    print(f"   Model available: {llm_advisor.llm_advisor.model_available}")
    print(f"   Model name: {llm_advisor.llm_advisor.llm_model_name}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
