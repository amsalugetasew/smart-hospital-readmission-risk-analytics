#!/usr/bin/env python3
"""
Test script to verify model compatibility with different algorithms
"""

import sys
import os
import numpy as np

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_feature_importance_compatibility():
    """Test feature importance extraction for different model types"""
    print("🧪 Testing feature importance compatibility...")
    
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.tree import DecisionTreeClassifier
        import pandas as pd
        
        # Create dummy data
        np.random.seed(42)
        X = np.random.rand(100, 5)
        y = np.random.randint(0, 2, 100)
        feature_names = ['feature_1', 'feature_2', 'feature_3', 'feature_4', 'feature_5']
        
        models_to_test = [
            ('RandomForestClassifier', RandomForestClassifier(n_estimators=10, random_state=42)),
            ('LogisticRegression', LogisticRegression(random_state=42, max_iter=100)),
            ('DecisionTreeClassifier', DecisionTreeClassifier(random_state=42))
        ]
        
        for model_name, model in models_to_test:
            print(f"\n📊 Testing {model_name}...")
            
            # Train model
            model.fit(X, y)
            
            # Test feature importance extraction
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                importance_type = "Feature Importance"
                print(f"   ✅ Has feature_importances_: {importances[:3]}...")
            elif hasattr(model, 'coef_'):
                importances = np.abs(model.coef_[0])
                importance_type = "Coefficient Magnitude"
                print(f"   ✅ Has coef_: {importances[:3]}...")
            else:
                importances = np.ones(len(feature_names))
                importance_type = "Equal Weight (Fallback)"
                print(f"   ⚠️  Using fallback: {importances[:3]}...")
            
            # Test sorting and selection
            indices = np.argsort(importances)[-3:]  # Top 3
            top_features = [feature_names[i] for i in indices]
            top_importances = importances[indices]
            
            print(f"   📈 {importance_type}")
            print(f"   🏆 Top 3 features: {top_features}")
            print(f"   📊 Importances: {top_importances}")
        
        print("\n🎉 All model types handled successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_feature_importance_compatibility()
    if success:
        print("\n✅ Model compatibility test passed!")
        print("   The application should handle different algorithms correctly.")
    else:
        print("\n❌ Model compatibility test failed!")
    
    input("\nPress Enter to exit...")