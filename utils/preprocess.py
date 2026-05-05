import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import os

def load_data(filepath="data/synthetic_hospital_data.csv"):
    return pd.read_csv(filepath)

def preprocess_data(df, target_col="Readmitted", save_pipeline=True, pipeline_path="models/preprocessor.joblib"):
    """
    Preprocess the hospital data for machine learning.
    """
    # Drop Patient_ID as it is not a predictive feature
    if "Patient_ID" in df.columns:
        df = df.drop(columns=["Patient_ID"])
        
    # Separate features and target
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Encode target variable
    le = LabelEncoder()
    y = le.fit_transform(y)
    
    # Identify numerical and categorical columns
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Create preprocessing pipelines for both numeric and categorical data
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
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    
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
    X_train, X_test, y_train, y_test, feature_names, _ = preprocess_data(df)
    print(f"X_train shape: {X_train.shape}")
    print(f"X_test shape: {X_test.shape}")
