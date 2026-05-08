#!/usr/bin/env python3
"""
Test script to verify minimal deployment requirements
"""

def test_minimal_imports():
    """Test that all essential packages can be imported"""
    print("🧪 Testing minimal deployment requirements...")
    
    essential_packages = [
        ('streamlit', 'st'),
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('plotly.express', 'px'),
        ('plotly.graph_objects', 'go'),
        ('requests', 'requests'),
        ('streamlit_option_menu', 'option_menu'),
        ('joblib', 'joblib'),
        ('openpyxl', 'openpyxl')
    ]
    
    optional_packages = [
        ('matplotlib.pyplot', 'plt'),
        ('seaborn', 'sns'),
        ('xgboost', 'xgb'),
        ('shap', 'shap')
    ]
    
    # Test essential packages
    failed_essential = []
    for package, alias in essential_packages:
        try:
            exec(f"import {package} as {alias}")
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_essential.append(package)
    
    # Test optional packages
    available_optional = []
    for package, alias in optional_packages:
        try:
            exec(f"import {package} as {alias}")
            print(f"✅ {package} (optional)")
            available_optional.append(package)
        except ImportError:
            print(f"⚠️  {package} (optional - not available)")
    
    print(f"\n📊 Results:")
    print(f"Essential packages: {len(essential_packages) - len(failed_essential)}/{len(essential_packages)} available")
    print(f"Optional packages: {len(available_optional)}/{len(optional_packages)} available")
    
    if failed_essential:
        print(f"\n❌ Missing essential packages: {failed_essential}")
        print("These must be installed for the app to work!")
        return False
    else:
        print(f"\n🎉 All essential packages available!")
        print(f"Optional features available: {available_optional}")
        return True

def test_streamlit_compatibility():
    """Test Streamlit-specific functionality"""
    print("\n🧪 Testing Streamlit compatibility...")
    
    try:
        import streamlit as st
        # Test basic Streamlit functions (won't actually run in this context)
        print("✅ Streamlit imported successfully")
        print(f"✅ Streamlit version: {st.__version__}")
        return True
    except Exception as e:
        print(f"❌ Streamlit compatibility issue: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 MINIMAL DEPLOYMENT TEST")
    print("=" * 60)
    
    imports_ok = test_minimal_imports()
    streamlit_ok = test_streamlit_compatibility()
    
    if imports_ok and streamlit_ok:
        print("\n🎉 DEPLOYMENT TEST PASSED!")
        print("The app should deploy successfully on Streamlit Cloud.")
    else:
        print("\n❌ DEPLOYMENT TEST FAILED!")
        print("Please install missing packages before deploying.")
    
    print("\n" + "=" * 60)
    input("Press Enter to exit...")