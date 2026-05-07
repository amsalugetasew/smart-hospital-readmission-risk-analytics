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
            model_path = "models/random_forest_model.joblib"
            preprocessor_path = "models/preprocessor.joblib"
            feature_names_path = "models/feature_names.json"
            metrics_path = "models/metrics.json"
            
            # Check if files exist
            if not os.path.exists(model_path):
                print(f"Warning: Model file not found at {model_path}")
                return
                
            self.model = joblib.load(model_path)
            print(f"Model loaded: {type(self.model).__name__}")
            
            self.preprocessor = joblib.load(preprocessor_path)
            print("Preprocessor loaded successfully")
            
            with open(feature_names_path, "r") as f:
                self.feature_names = json.load(f)
            print(f"Feature names loaded: {len(self.feature_names)} features")
                
            with open(metrics_path, "r") as f:
                self.metrics = json.load(f)
            print(f"Metrics loaded: Accuracy = {self.metrics.get('accuracy', 0):.2%}")
                
            # Initialize TreeExplainer for SHAP if model is tree-based
            model_type = type(self.model).__name__
            if model_type in ['RandomForestClassifier', 'DecisionTreeClassifier', 'XGBClassifier']:
                print(f"Initializing SHAP TreeExplainer for {model_type}...")
                self.explainer = shap.TreeExplainer(self.model)
                print("SHAP explainer initialized successfully")
            else:
                print(f"SHAP TreeExplainer not available for {model_type}")
                self.explainer = None
                
        except Exception as e:
            print(f"Error loading models: {e}")
            import traceback
            traceback.print_exc()
            self.model = None
            self.preprocessor = None
            self.feature_names = None
            self.metrics = None
            self.explainer = None

    def predict(self, data: dict):
        """
        Make a prediction using the trained model.
        
        IMPORTANT: This method uses the EXACT same preprocessing pipeline
        that was used during model training. The preprocessor is loaded from
        'models/preprocessor.joblib' which contains:
        - SimpleImputer for handling missing values
        - StandardScaler/MinMaxScaler/RobustScaler for numerical features
        - OneHotEncoder for categorical features
        
        The preprocessing steps are applied in the same order and with the
        same parameters as during training, ensuring consistency.
        """
        try:
            # Validate that preprocessor is loaded
            if self.preprocessor is None:
                raise Exception("Preprocessor not loaded. Please train the model first.")
            
            # Create DataFrame from input data
            # This ensures the data structure matches what the preprocessor expects
            df = pd.DataFrame([data])
            
            print(f"Input data columns: {df.columns.tolist()}")
            print(f"Input data shape: {df.shape}")
            
            # Ensure correct data types to match training data
            # This is critical for the preprocessor to work correctly
            
            # Categorical columns - must be strings for OneHotEncoder
            categorical_cols = ['season', 'gender', 'region', 'primary_diagnosis',
                              'treatment_type', 'insurance_type', 'discharge_disposition']
            
            for col in categorical_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str)
            
            # Numerical columns - must be numeric for imputation and scaling
            numerical_cols = ['age', 'comorbidities_count', 'length_of_stay',
                            'medications_count', 'followup_visits_last_year',
                            'prev_readmissions', 'readmission_risk_score']
            
            for col in numerical_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Verify all required columns are present
            expected_cols = categorical_cols + numerical_cols
            missing_cols = [col for col in expected_cols if col not in df.columns]
            if missing_cols:
                raise Exception(f"Missing required columns: {missing_cols}")
            
            # Debug: Print data types
            print("DataFrame dtypes before preprocessing:")
            print(df.dtypes)
            
            # Apply the SAME preprocessing pipeline used during training
            # This includes:
            # 1. Imputation (filling missing values)
            # 2. Scaling (standardizing numerical features)
            # 3. One-hot encoding (converting categorical to numerical)
            print("Applying saved preprocessing pipeline...")
            X_processed = self.preprocessor.transform(df)
            print(f"Preprocessed shape: {X_processed.shape}")
            print(f"Expected features: {len(self.feature_names)}")
            
            # Validate preprocessed shape matches training
            if X_processed.shape[1] != len(self.feature_names):
                raise Exception(
                    f"Preprocessed feature count mismatch! "
                    f"Got {X_processed.shape[1]}, expected {len(self.feature_names)}"
                )
            
            # Make prediction using the trained model
            prob = self.model.predict_proba(X_processed)[0][1]
            prediction_label = self.model.predict(X_processed)[0]
            
            # Map prediction to readable format
            prediction = "Readmitted" if prediction_label == 1 else "Not Readmitted"
            
            print(f"Prediction: {prediction}, Probability: {prob:.2%}")
            
            # Risk Category
            if prob < 0.33:
                risk_category = "Low Risk"
            elif prob < 0.66:
                risk_category = "Medium Risk"
            else:
                risk_category = "High Risk"
                
            # SHAP Values or Coefficients
            feature_importance = {}
            
            try:
                if self.explainer:
                    # Get SHAP values
                    shap_values = self.explainer.shap_values(X_processed)
                    
                    # Handle different SHAP output formats
                    if isinstance(shap_values, list):
                        # Binary classification: [class_0_shap, class_1_shap]
                        shap_values = shap_values[1]
                        if len(shap_values.shape) > 1:
                            shap_values = shap_values[0]
                    elif isinstance(shap_values, np.ndarray):
                        if len(shap_values.shape) == 3:
                            # Shape: (n_samples, n_features, n_classes)
                            shap_values = shap_values[0, :, 1]
                        elif len(shap_values.shape) == 2:
                            # Shape: (n_samples, n_features)
                            shap_values = shap_values[0]
                        
                    # Combine feature names with shap values
                    for name, val in zip(self.feature_names, shap_values):
                        feature_importance[name] = float(val)
                        
                elif hasattr(self.model, 'coef_'):
                    # Fallback for Logistic Regression (Coefficient * Feature Value)
                    X_dense = X_processed.toarray() if hasattr(X_processed, 'toarray') else X_processed
                    coefs = self.model.coef_[0]
                    for i, name in enumerate(self.feature_names):
                        feature_importance[name] = float(coefs[i] * X_dense[0][i])
                        
                elif hasattr(self.model, 'feature_importances_'):
                    # Use model's built-in feature importances
                    for name, importance in zip(self.feature_names, self.model.feature_importances_):
                        feature_importance[name] = float(importance)
                        
            except Exception as shap_error:
                print(f"Warning: Could not compute feature importance: {shap_error}")
                # Provide default feature importance if SHAP fails
                feature_importance = {"Feature importance unavailable": 0.0}
                
            # Sort by absolute magnitude and get top 10
            if feature_importance:
                feature_importance = dict(sorted(feature_importance.items(), 
                                                key=lambda item: abs(item[1]), 
                                                reverse=True)[:10])

            return {
                "prediction": prediction,
                "probability": float(prob),
                "risk_category": risk_category,
                "feature_importance": feature_importance,
                "model_type": type(self.model).__name__ if self.model else "Unknown"
            }
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Prediction failed: {str(e)}")
        
predictor = HealthcarePredictor()
