import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report, confusion_matrix
import os
import json
from utils.preprocess import load_data, preprocess_data

def train_and_evaluate_model():
    print("Loading data...")
    df = load_data()
    
    print("Preprocessing data...")
    X_train, X_test, y_train, y_test, feature_names, _ = preprocess_data(df)
    
    print("Training Random Forest model...")
    # Initialize Random Forest Classifier
    rf_model = RandomForestClassifier(
        n_estimators=100, 
        max_depth=10, 
        min_samples_split=5, 
        random_state=42,
        class_weight='balanced'
    )
    
    # Train the model
    rf_model.fit(X_train, y_train)
    
    print("Evaluating model...")
    y_pred = rf_model.predict(X_test)
    y_proba = rf_model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "f1_score": float(f1_score(y_test, y_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_proba))
    }
    
    print(f"Metrics: {metrics}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save the model
    model_path = "models/random_forest_model.joblib"
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(rf_model, model_path)
    print(f"Model saved to {model_path}")
    
    # Save feature names for frontend/SHAP
    with open("models/feature_names.json", "w") as f:
        json.dump(feature_names, f)
        
    # Save metrics
    with open("models/metrics.json", "w") as f:
        json.dump(metrics, f)

if __name__ == "__main__":
    train_and_evaluate_model()
