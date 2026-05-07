import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report, confusion_matrix
import os
import json
from utils.preprocess import load_data, preprocess_data

def train_and_evaluate_model():
    print("=" * 60)
    print("TRAINING MODEL WITH HOSPITAL READMISSION DATASET")
    print("=" * 60)
    
    print("\n1. Loading data...")
    df = load_data()
    print(f"   Loaded {len(df)} rows, {df.shape[1]} columns")
    print(f"   Label distribution:")
    print(f"   - Readmitted (1): {(df['label']==1).sum()} ({(df['label']==1).sum()/len(df)*100:.1f}%)")
    print(f"   - Not Readmitted (0): {(df['label']==0).sum()} ({(df['label']==0).sum()/len(df)*100:.1f}%)")
    
    print("\n2. Preprocessing data...")
    X_train, X_test, y_train, y_test, feature_names, _ = preprocess_data(df)
    print(f"   Training set: {X_train.shape}")
    print(f"   Test set: {X_test.shape}")
    print(f"   Features after encoding: {len(feature_names)}")
    
    print("\n3. Training Random Forest model...")
    # Initialize Random Forest Classifier
    rf_model = RandomForestClassifier(
        n_estimators=100, 
        max_depth=15, 
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1
    )
    
    # Train the model
    rf_model.fit(X_train, y_train)
    print("   ✓ Model trained successfully")
    
    print("\n4. Evaluating model...")
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
    
    print(f"\n   Metrics:")
    print(f"   - Accuracy:  {metrics['accuracy']:.2%}")
    print(f"   - Precision: {metrics['precision']:.2%}")
    print(f"   - Recall:    {metrics['recall']:.2%}")
    print(f"   - F1 Score:  {metrics['f1_score']:.2%}")
    print(f"   - ROC AUC:   {metrics['roc_auc']:.3f}")
    
    print("\n   Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Not Readmitted', 'Readmitted']))
    
    print("\n5. Saving model and artifacts...")
    # Save the model
    model_path = "models/random_forest_model.joblib"
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(rf_model, model_path)
    print(f"   ✓ Model saved to {model_path}")
    
    # Save feature names for frontend/SHAP
    with open("models/feature_names.json", "w") as f:
        json.dump(feature_names, f)
    print(f"   ✓ Feature names saved ({len(feature_names)} features)")
        
    # Save metrics
    with open("models/metrics.json", "w") as f:
        json.dump(metrics, f)
    print(f"   ✓ Metrics saved")
    
    # Save feature importances
    feature_importance_dict = dict(zip(feature_names, rf_model.feature_importances_))
    sorted_features = sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True)
    
    print("\n6. Top 10 Most Important Features:")
    for i, (feature, importance) in enumerate(sorted_features[:10], 1):
        print(f"   {i}. {feature}: {importance:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ MODEL TRAINING COMPLETED SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    train_and_evaluate_model()
