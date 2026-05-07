import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import os

def load_data(filepath="data/hospital_readmission_dataset.csv"):
    """Load the hospital readmission dataset."""
    return pd.read_csv(filepath)

def preprocess_data(df, target_col="label", save_pipeline=True, pipeline_path="models/preprocessor.joblib"):
    """
    Preprocess the hospital readmission data for machine learning.
    
    Features in the dataset:
    - patient_id: Unique identifier (will be dropped)
    - admission_date: Date of admission (will be dropped)
    - season: Season of admission (categorical)
    - age: Patient age (numerical)
    - gender: Patient gender (categorical)
    - region: Geographic region (categorical)
    - primary_diagnosis: Primary diagnosis (categorical)
    - comorbidities_count: Number of comorbidities (numerical)
    - length_of_stay: Days in hospital (numerical)
    - treatment_type: Type of treatment (categorical)
    - medications_count: Number of medications (numerical)
    - followup_visits_last_year: Number of follow-up visits (numerical)
    - prev_readmissions: Previous readmissions count (numerical)
    - insurance_type: Type of insurance (categorical)
    - discharge_disposition: Discharge destination (categorical)
    - readmission_risk_score: Risk score (numerical)
    - label: Target variable (1=readmitted, 0=not readmitted)
    """
    
    # Drop patient_id and admission_date (not predictive features)
    columns_to_drop = ['patient_id']
    if 'admission_date' in df.columns:
        columns_to_drop.append('admission_date')
    
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
    
    # Separate features and target
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Target is already 0/1, but create label encoder for consistency
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Identify numerical and categorical columns
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()
    
    print(f"Numerical features ({len(numeric_features)}): {numeric_features}")
    print(f"Categorical features ({len(categorical_features)}): {categorical_features}")
    
    # Create preprocessing pipelines
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    # Combine preprocessing steps
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    # Stratified Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, stratify=y_encoded, random_state=42
    )
    
    # Fit and transform the training data
    X_train_preprocessed = preprocessor.fit_transform(X_train)
    
    # Transform testing data
    X_test_preprocessed = preprocessor.transform(X_test)
    
    # Get feature names after one-hot encoding
    cat_encoder = preprocessor.named_transformers_['cat'].named_steps['onehot']
    cat_features_encoded = cat_encoder.get_feature_names_out(categorical_features)
    feature_names = numeric_features + list(cat_features_encoded)
    
    if save_pipeline:
        os.makedirs(os.path.dirname(pipeline_path), exist_ok=True)
        joblib.dump(preprocessor, pipeline_path)
        joblib.dump(le, "models/label_encoder.joblib")
        print(f"Preprocessing pipeline saved to {pipeline_path}")
        
    return X_train_preprocessed, X_test_preprocessed, y_train, y_test, feature_names, preprocessor

if __name__ == "__main__":
    df = load_data()
    print(f"Dataset shape: {df.shape}")
    print(f"\nLabel distribution:")
    print(df['label'].value_counts())
    
    X_train, X_test, y_train, y_test, feature_names, _ = preprocess_data(df)
    print(f"\nX_train shape: {X_train.shape}")
    print(f"X_test shape: {X_test.shape}")
    print(f"Number of features after encoding: {len(feature_names)}")
