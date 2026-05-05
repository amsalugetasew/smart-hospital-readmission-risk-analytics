import joblib
import pandas as pd
import numpy as np
import shap
import json
import os

class HealthcarePredictor:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.feature_names = None
        self.metrics = None
        self.explainer = None
        self.load_models()

    def load_models(self):
        try:
            self.model = joblib.load("models/random_forest_model.joblib")
            self.preprocessor = joblib.load("models/preprocessor.joblib")
            
            with open("models/feature_names.json", "r") as f:
                self.feature_names = json.load(f)
                
            with open("models/metrics.json", "r") as f:
                self.metrics = json.load(f)
                
            # Initialize TreeExplainer for SHAP
            self.explainer = shap.TreeExplainer(self.model)
        except Exception as e:
            print(f"Error loading models: {e}")

    def predict(self, data: dict):
        df = pd.DataFrame([data])
        
        # Preprocess
        X_processed = self.preprocessor.transform(df)
        
        # Predict
        prob = self.model.predict_proba(X_processed)[0][1]
        prediction = "Yes" if prob > 0.5 else "No"
        
        # Risk Category
        if prob < 0.33:
            risk_category = "Low Risk"
        elif prob < 0.66:
            risk_category = "Medium Risk"
        else:
            risk_category = "High Risk"
            
        # SHAP Values
        shap_values = self.explainer.shap_values(X_processed)
        # SHAP for RandomForest might return a list [class_0_shap, class_1_shap]
        if isinstance(shap_values, list):
            shap_values = shap_values[1][0]
        else:
            # If shape is 3D (e.g. from new shap versions for classification)
            if len(shap_values.shape) == 3:
                shap_values = shap_values[0, :, 1]
            else:
                shap_values = shap_values[0]
                
        # Combine feature names with shap values
        feature_importance = {}
        for name, val in zip(self.feature_names, shap_values):
            feature_importance[name] = float(val)
            
        # Sort by absolute magnitude
        feature_importance = dict(sorted(feature_importance.items(), key=lambda item: abs(item[1]), reverse=True)[:10])

        return {
            "prediction": prediction,
            "probability": float(prob),
            "risk_category": risk_category,
            "feature_importance": feature_importance
        }
        
predictor = HealthcarePredictor()
