#!/usr/bin/env python3
"""
Quick test script to verify all imports work correctly
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing imports...")
    
    try:
        # Test utils imports
        from utils.preprocess import load_data, preprocess_data
        print("✅ utils.preprocess imported successfully")
        
        from utils.data_upload import load_uploaded_file, validate_dataset_columns
        print("✅ utils.data_upload imported successfully")
        
        # Test backend imports
        from backend.main import app
        print("✅ backend.main imported successfully")
        
        from backend.predictor import HealthcarePredictor
        print("✅ backend.predictor imported successfully")
        
        # Test key libraries
        import streamlit as st
        print("✅ streamlit imported successfully")
        
        import pandas as pd
        print("✅ pandas imported successfully")
        
        import sklearn
        print("✅ scikit-learn imported successfully")
        
        import xgboost
        print("✅ xgboost imported successfully")
        
        import fastapi
        print("✅ fastapi imported successfully")
        
        print("\n🎉 All imports successful! The application should run without import errors.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ Ready to run the application!")
        print("   Backend: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
        print("   Frontend: streamlit run frontend/app.py")
    else:
        print("\n❌ Please fix import errors before running the application.")
    
    input("\nPress Enter to exit..