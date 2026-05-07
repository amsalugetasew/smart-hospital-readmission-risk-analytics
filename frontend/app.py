import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from streamlit_option_menu import option_menu
import os
import subprocess
import time
import socket

@st.cache_resource
def start_backend():
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0
            
    if not is_port_in_use(8000):
        print("Starting backend server...")
        subprocess.Popen(["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"])
        time.sleep(3)

start_backend()

# Configure page
st.set_page_config(
    page_title="Smart Hospital Readmission Risk Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-top: 4px solid #4CAF50;
    }
    .high-risk-metric {
        border-top: 4px solid #F44336 !important;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background-color: #008080 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 128, 128, 0.2) !important;
    }
    .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 128, 128, 0.3) !important;
        background-color: #006666 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #f1f1f1 !important;
    }
</style>
""", unsafe_allow_html=True)

# API URL
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def get_analytics():
    try:
        response = requests.get(f"{API_URL}/analytics")
        if response.status_code == 200:
            return response.json()
    except:
        return None
        
def get_prediction(data):
    try:
        response = requests.post(f"{API_URL}/predict", json=data, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error ({response.status_code}): {response.text}")
            return None
    except requests.exceptions.ConnectionError as e:
        st.error(f"❌ Cannot connect to backend API at {API_URL}. Please ensure the backend server is running.")
        st.info("💡 Try running: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. The model might be taking too long to respond.")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return None

# Sidebar navigation
with st.sidebar:
    st.markdown('<div style="text-align: left; margin-bottom: 0px;"><h2>🏥 Hospital Readmission</h2></div>', unsafe_allow_html=True)
    page = option_menu(
        menu_title=None,
        options=["Overview", "EDA", "Preprocessing", "Model Training", "Patient Risk Analysis", "Analytics Dashboard", "Model Performance"],
        icons=["house", "bar-chart", "gear", "cpu", "activity", "graph-up", "speedometer2"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#008080", "font-size": "18px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "5px 0",
                "color": "#1e293b",
                "--hover-color": "#ff00ff",
            },
            "nav-link-selected": {
                "background-color": "#008080",
                "color": "white",
            },
        }
    )

# Dataset path
DATASET_PATH = "data/hospital_readmission_dataset.csv"

if page == "Overview":
    st.title("Hospital Readmission Overview")
    
    analytics = get_analytics()
    if analytics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Patients", f"{analytics['total_patients']:,}")
        with col2:
            st.metric("Readmission Rate", f"{analytics['readmission_rate']:.1%}")
        with col3:
            st.metric("Avg Length of Stay", f"{analytics['average_length_of_stay']:.1f} days")
        with col4:
            st.markdown('<div class="stMetric high-risk-metric">', unsafe_allow_html=True)
            st.metric("High Risk Patients", f"{analytics['high_risk_percentage']:.1%}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.divider()
        
        # Load dataset for detailed overview
        try:
            df = pd.read_csv(DATASET_PATH)
            
            st.markdown("""
            ### Welcome to the Smart Hospital Readmission Risk Analytics Platform
            
            This AI-powered platform helps healthcare professionals:
            - 🎯 Predict patient readmission risks using machine learning
            - 🔍 Identify major risk factors using Explainable AI (SHAP)
            - 📊 Monitor hospital performance indicators
            - 💡 Make data-driven decisions to improve patient outcomes
            """)
            
            st.divider()
            
            # Dataset Overview Section
            st.subheader("📋 Dataset Overview")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Dataset Statistics:**")
                st.write(f"- Total Records: **{len(df):,}**")
                st.write(f"- Total Features: **17**")
                st.write(f"- Training Features: **14**")
                st.write(f"- Missing Values: **{df.isna().sum().sum()}**")
                
            with col2:
                st.markdown("**Target Distribution:**")
                readmitted_count = (df['label'] == 1).sum()
                not_readmitted_count = (df['label'] == 0).sum()
                st.write(f"- Readmitted: **{readmitted_count:,}** ({readmitted_count/len(df)*100:.1f}%)")
                st.write(f"- Not Readmitted: **{not_readmitted_count:,}** ({not_readmitted_count/len(df)*100:.1f}%)")
                st.write(f"- Class Imbalance: **{readmitted_count/not_readmitted_count:.2f}:1**")
                
            with col3:
                st.markdown("**Key Statistics:**")
                st.write(f"- Avg Age: **{df['age'].mean():.1f}** years")
                st.write(f"- Avg Comorbidities: **{df['comorbidities_count'].mean():.1f}**")
                st.write(f"- Avg Medications: **{df['medications_count'].mean():.1f}**")
                st.write(f"- Avg Risk Score: **{df['readmission_risk_score'].mean():.2f}**")
            
            st.divider()
            
            # Feature Categories
            st.subheader("🔢 Feature Categories")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Numerical Features (7):**")
                numerical_features = [
                    "age", "comorbidities_count", "length_of_stay",
                    "medications_count", "followup_visits_last_year",
                    "prev_readmissions", "readmission_risk_score"
                ]
                for feat in numerical_features:
                    st.write(f"- {feat}")
                    
            with col2:
                st.markdown("**Categorical Features (7):**")
                categorical_features = [
                    "season", "gender", "region", "primary_diagnosis",
                    "treatment_type", "insurance_type", "discharge_disposition"
                ]
                for feat in categorical_features:
                    unique_count = df[feat].nunique()
                    st.write(f"- {feat} ({unique_count} categories)")
            
            st.divider()
            
            # Quick Insights
            st.subheader("💡 Quick Insights")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Top 3 Diagnoses:**")
                top_diagnoses = df['primary_diagnosis'].value_counts().head(3)
                for diag, count in top_diagnoses.items():
                    st.write(f"- {diag}: {count} ({count/len(df)*100:.1f}%)")
                    
            with col2:
                st.markdown("**Regional Distribution:**")
                regions = df['region'].value_counts()
                for region, count in regions.items():
                    st.write(f"- {region}: {count} ({count/len(df)*100:.1f}%)")
                    
            with col3:
                st.markdown("**Treatment Types:**")
                treatments = df['treatment_type'].value_counts()
                for treatment, count in treatments.items():
                    st.write(f"- {treatment}: {count} ({count/len(df)*100:.1f}%)")
            
            st.divider()
            
            # Model Information
            st.subheader("🤖 Model Information")
            
            try:
                with open("models/metrics.json", "r") as f:
                    metrics = json.load(f)
                
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Accuracy", f"{metrics['accuracy']:.1%}")
                col2.metric("Precision", f"{metrics['precision']:.1%}")
                col3.metric("Recall", f"{metrics['recall']:.1%}")
                col4.metric("F1 Score", f"{metrics['f1_score']:.1%}")
                col5.metric("ROC AUC", f"{metrics['roc_auc']:.3f}")
                
                st.success("✅ Model is trained and ready for predictions!")
                
            except FileNotFoundError:
                st.warning("⚠️ Model not trained yet. Please go to 'Model Training' page to train the model.")
            
            st.divider()
            st.info("👈 Please navigate using the sidebar to explore different functionalities.")
            
        except Exception as e:
            st.error(f"Error loading dataset details: {e}")
            st.markdown("""
            ### Welcome to the Smart Hospital Readmission Risk Analytics Platform
            
            This AI-powered platform helps healthcare professionals predict patient readmission risks.
            
            Please navigate using the sidebar to explore different functionalities.
            """)
    else:
        st.error("Could not connect to the backend API. Please ensure it is running.")

elif page == "EDA":
    st.title("Exploratory Data Analysis (EDA)")
    st.markdown("Analyze the hospital readmission dataset interactively.")
    
    try:
        df = pd.read_csv(DATASET_PATH)
        
        # Drop patient_id for analysis
        if 'patient_id' in df.columns:
            df_analysis = df.drop(columns=['patient_id', 'admission_date'])
            st.info("ℹ️ patient_id and admission_date have been excluded from analysis.")
        else:
            df_analysis = df.copy()
        
        st.write("### Dataset Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Rows", df.shape[0])
        col2.metric("Total Features", df_analysis.shape[1])
        col3.metric("Missing Values", df_analysis.isna().sum().sum())
        col4.metric("Readmission Rate", f"{(df['label']==1).sum()/len(df)*100:.1f}%")
        
        st.dataframe(df.head(10), use_container_width=True)
        
        with st.expander("Data Quality Analysis"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("#### Missing Values per Column (%)")
                missing_pct = (df_analysis.isna().sum() / len(df_analysis)) * 100
                missing_df = pd.DataFrame({"Feature": missing_pct.index, "Missing (%)": missing_pct.values})
                missing_df = missing_df[missing_df["Missing (%)"] > 0].sort_values("Missing (%)", ascending=False)
                if len(missing_df) > 0:
                    st.dataframe(missing_df, use_container_width=True, hide_index=True)
                else:
                    st.success("No missing values found!")
                    
            with col2:
                st.write("#### Label Distribution")
                label_counts = df['label'].value_counts()
                fig = px.pie(values=label_counts.values, names=['Not Readmitted', 'Readmitted'],
                            color_discrete_sequence=['#00cc96', '#ef553b'])
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        st.write("### Interactive Graph Explorer")
        chart_type = st.selectbox("Select Chart Type", 
                                  ["Histogram", "Box Plot", "Scatter Plot", "Correlation Heatmap", "Bar Chart (Counts)"])
        
        num_cols = df_analysis.select_dtypes(include=['int64', 'float64']).columns.tolist()
        cat_cols = df_analysis.select_dtypes(include=['object']).columns.tolist()
        all_cols = df_analysis.columns.tolist()
        
        if chart_type == "Histogram":
            x_col = st.selectbox("Select X-axis Feature", all_cols, 
                                index=all_cols.index("age") if "age" in all_cols else 0)
            color_col = st.selectbox("Select Color Grouping", ["None"] + all_cols,
                                    index=all_cols.index("label")+1 if "label" in all_cols else 0)
            color_arg = None if color_col == "None" else color_col
            fig = px.histogram(df_analysis, x=x_col, color=color_arg, barmode="overlay")
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_type == "Bar Chart (Counts)":
            x_col = st.selectbox("Select Categorical Feature to Count", cat_cols)
            color_col = st.selectbox("Select Color Grouping", ["None"] + all_cols,
                                    index=all_cols.index("label")+1 if "label" in all_cols else 0)
            color_arg = None if color_col == "None" else color_col
            fig = px.histogram(df_analysis, x=x_col, color=color_arg, barmode="group", text_auto=True)
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_type == "Box Plot":
            y_col = st.selectbox("Select Y-axis (Numerical)", num_cols)
            x_col = st.selectbox("Select X-axis (Categorical)", ["None"] + cat_cols)
            x_arg = None if x_col == "None" else x_col
            fig = px.box(df_analysis, x=x_arg, y=y_col, color=x_arg)
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_type == "Scatter Plot":
            x_col = st.selectbox("Select X-axis (Numerical)", num_cols)
            y_col = st.selectbox("Select Y-axis (Numerical)", num_cols, 
                                index=1 if len(num_cols)>1 else 0)
            color_col = st.selectbox("Select Color Grouping", ["None"] + cat_cols)
            color_arg = None if color_col == "None" else color_col
            fig = px.scatter(df_analysis, x=x_col, y=y_col, color=color_arg)
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_type == "Correlation Heatmap":
            st.write("Showing Pearson correlation for numerical features:")
            corr = df_analysis[num_cols].corr()
            fig = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r')
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error loading dataset: {e}")

elif page == "Preprocessing":
    st.title("Interactive Data Preprocessing")
    st.markdown("Configure how to handle missing values, scale numerical features, and encode categorical variables.")
    
    try:
        df = pd.read_csv(DATASET_PATH)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            imputation_strategy = st.selectbox("Missing Value Handling (Numerical)", 
                                              ["mean", "median", "constant (zero)"])
        with col2:
            scaling_method = st.selectbox("Scaling Method", 
                                         ["StandardScaler", "MinMaxScaler", "RobustScaler"])
        with col3:
            encoding_method = st.selectbox("Categorical Encoding", ["OneHotEncoder"])
            
        if st.button("Apply & Confirm Preprocessing", type="primary", use_container_width=True):
            with st.spinner("Building pipeline and transforming data..."):
                from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, OneHotEncoder, LabelEncoder
                from sklearn.impute import SimpleImputer
                from sklearn.compose import ColumnTransformer
                from sklearn.pipeline import Pipeline
                
                # Drop patient_id and admission_date
                columns_to_drop = ['patient_id', 'admission_date']
                df_clean = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
                
                # Setup target
                X = df_clean.drop('label', axis=1)
                y = df_clean['label']
                
                numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
                categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
                
                # Numerical Pipeline
                imputer_strat = "constant" if "zero" in imputation_strategy else imputation_strategy
                fill_val = 0 if imputer_strat == "constant" else None
                
                if scaling_method == "StandardScaler":
                    scaler = StandardScaler()
                elif scaling_method == "MinMaxScaler":
                    scaler = MinMaxScaler()
                else:
                    scaler = RobustScaler()
                    
                numeric_transformer = Pipeline(steps=[
                    ('imputer', SimpleImputer(strategy=imputer_strat, fill_value=fill_val)),
                    ('scaler', scaler)
                ])
                
                # Categorical Pipeline
                categorical_transformer = Pipeline(steps=[
                    ('imputer', SimpleImputer(strategy='most_frequent')),
                    ('encoder', OneHotEncoder(handle_unknown='ignore'))
                ])
                
                preprocessor = ColumnTransformer(
                    transformers=[
                        ('num', numeric_transformer, numerical_cols),
                        ('cat', categorical_transformer, categorical_cols)
                    ])
                
                # Fit and transform
                X_processed = preprocessor.fit_transform(X)
                
                # Encode target (already 0/1, but for consistency)
                le = LabelEncoder()
                y_encoded = le.fit_transform(y)
                
                # Extract feature names
                cat_encoder = preprocessor.named_transformers_['cat'].named_steps['encoder']
                cat_feature_names = cat_encoder.get_feature_names_out(categorical_cols).tolist()
                feature_names = numerical_cols + cat_feature_names
                
                # Save to session state
                st.session_state['preprocessor'] = preprocessor
                st.session_state['label_encoder'] = le
                st.session_state['X_processed'] = X_processed
                st.session_state['y_encoded'] = y_encoded
                st.session_state['feature_names'] = feature_names
                st.session_state['preprocessing_complete'] = True
                
                st.success("Preprocessing completed and saved to session memory!")
                
                # Show summary
                st.write("### Preprocessed Dataset Summary")
                col1, col2, col3 = st.columns(3)
                col1.metric("Original Features", len(X.columns))
                col2.metric("Encoded Features", len(feature_names))
                col3.metric("Samples", X_processed.shape[0])
                
                st.write("**Feature Breakdown:**")
                st.write(f"- Numerical features: {len(numerical_cols)}")
                st.write(f"- Categorical features: {len(categorical_cols)}")
                st.write(f"- Total after encoding: {len(feature_names)}")
                
    except Exception as e:
        st.error(f"Error during preprocessing: {e}")
        import traceback
        st.code(traceback.format_exc())

# Continue in next part...

elif page == "Model Training":
    st.title("Automated Model Training")
    st.markdown("Train the model using your custom preprocessed dataset.")
    
    if not st.session_state.get('preprocessing_complete', False):
        st.warning("⚠️ Please complete and confirm the Preprocessing step first.")
    else:
        st.info("✅ Preprocessed dataset loaded from session memory.")
        
        X_processed = st.session_state['X_processed']
        feature_names = st.session_state['feature_names']
        
        st.write("### Data Overview")
        st.write(f"**Shape of Training Data:** {X_processed.shape[0]} rows, {X_processed.shape[1]} features")
        
        st.divider()
        st.write("### Model Configuration")
        
        test_size_pct = st.slider("Test Set Size (%)", min_value=10, max_value=50, value=20, step=5) / 100.0
        model_choice = st.selectbox("Select Machine Learning Algorithm", 
                                   ["Random Forest", "Logistic Regression", "Decision Tree", "XGBoost"])
        
        if model_choice == "Random Forest":
            col1, col2 = st.columns(2)
            with col1:
                n_estimators = st.slider("Number of Trees", 50, 300, 100, 50)
                min_samples_split = st.slider("Min Samples Split", 2, 20, 2)
            with col2:
                max_depth = st.slider("Maximum Depth", 3, 50, 15, 1)
                min_samples_leaf = st.slider("Min Samples Leaf", 1, 20, 2)
        elif model_choice == "XGBoost":
            col1, col2 = st.columns(2)
            with col1:
                n_estimators = st.slider("Number of Trees", 50, 300, 100, 50)
                learning_rate = st.select_slider("Learning Rate", options=[0.01, 0.05, 0.1, 0.2, 0.3], value=0.1)
            with col2:
                max_depth = st.slider("Maximum Depth", 3, 50, 10, 1)
        elif model_choice == "Decision Tree":
            col1, col2 = st.columns(2)
            with col1:
                max_depth = st.slider("Maximum Depth", 3, 50, 10, 1)
                criterion = st.selectbox("Criterion", ["gini", "entropy"])
            with col2:
                min_samples_split = st.slider("Min Samples Split", 2, 20, 2)
        elif model_choice == "Logistic Regression":
            col1, col2 = st.columns(2)
            with col1:
                C_val = st.select_slider("Inverse of Regularization Strength (C)", 
                                        options=[0.01, 0.1, 1.0, 10.0, 100.0], value=1.0)
            with col2:
                solver = st.selectbox("Solver", ["lbfgs", "liblinear", "saga"])
            
        if st.button("Train Model", type="primary", use_container_width=True):
            with st.spinner(f"Training {model_choice} model..."):
                try:
                    from sklearn.ensemble import RandomForestClassifier
                    from sklearn.linear_model import LogisticRegression
                    from sklearn.tree import DecisionTreeClassifier
                    from xgboost import XGBClassifier
                    from sklearn.model_selection import train_test_split
                    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
                    import joblib
                    
                    y_encoded = st.session_state['y_encoded']
                    preprocessor = st.session_state['preprocessor']
                    le = st.session_state['label_encoder']
                    
                    # Split data
                    X_train, X_test, y_train, y_test = train_test_split(
                        X_processed, y_encoded, test_size=test_size_pct, random_state=42, stratify=y_encoded
                    )
                    
                    # Train model
                    if model_choice == "Random Forest":
                        model = RandomForestClassifier(
                            n_estimators=n_estimators, max_depth=max_depth, 
                            min_samples_split=min_samples_split, min_samples_leaf=min_samples_leaf,
                            random_state=42, class_weight='balanced'
                        )
                    elif model_choice == "Logistic Regression":
                        model = LogisticRegression(C=C_val, solver=solver, random_state=42, max_iter=1000)
                    elif model_choice == "Decision Tree":
                        model = DecisionTreeClassifier(
                            max_depth=max_depth, criterion=criterion, 
                            min_samples_split=min_samples_split, random_state=42
                        )
                    elif model_choice == "XGBoost":
                        model = XGBClassifier(
                            n_estimators=n_estimators, max_depth=max_depth, 
                            learning_rate=learning_rate, random_state=42, 
                            use_label_encoder=False, eval_metric='logloss'
                        )
                        
                    model.fit(X_train, y_train)
                    
                    # Evaluate
                    y_pred = model.predict(X_test)
                    y_prob = model.predict_proba(X_test)[:, 1]
                    
                    metrics = {
                        "accuracy": accuracy_score(y_test, y_pred),
                        "precision": precision_score(y_test, y_pred),
                        "recall": recall_score(y_test, y_pred),
                        "f1_score": f1_score(y_test, y_pred),
                        "roc_auc": roc_auc_score(y_test, y_prob)
                    }
                    
                    # Save artifacts
                    joblib.dump(model, "models/random_forest_model.joblib")
                    joblib.dump(preprocessor, "models/preprocessor.joblib")
                    joblib.dump(le, "models/label_encoder.joblib")
                    with open("models/feature_names.json", "w") as f:
                        json.dump(feature_names, f)
                    with open("models/metrics.json", "w") as f:
                        json.dump(metrics, f)
                        
                    # Reload model in backend
                    try:
                        response = requests.post(f"{API_URL}/reload-model")
                        if response.status_code == 200:
                            st.success(f"{model_choice} trained successfully and backend API reloaded!")
                        else:
                            st.warning(f"{model_choice} trained successfully, but backend API failed to reload.")
                    except:
                        st.warning("Model trained, but could not connect to backend API to reload.")
                    
                    # Display metrics
                    st.write("### Model Evaluation Results")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("Accuracy", f"{metrics['accuracy']:.1%}")
                    col2.metric("Precision", f"{metrics['precision']:.1%}")
                    col3.metric("Recall", f"{metrics['recall']:.1%}")
                    col4.metric("F1 Score", f"{metrics['f1_score']:.1%}")
                    col5.metric("ROC AUC", f"{metrics['roc_auc']:.3f}")
                    
                except Exception as e:
                    st.error(f"Error during training: {e}")
                    import traceback
                    st.code(traceback.format_exc())

elif page == "Patient Risk Analysis":
    st.title("Patient Risk Prediction")
    st.markdown("Enter patient details to predict their risk of hospital readmission within 30 days.")
    
    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Demographics")
            age = st.number_input("Age", min_value=18, max_value=120, value=65)
            gender = st.selectbox("Gender", ["Male", "Female"])
            region = st.selectbox("Region", ["North", "South", "East", "West"])
            season = st.selectbox("Season", ["Spring", "Summer", "Fall", "Winter"])
            
        with col2:
            st.subheader("Clinical Information")
            primary_diagnosis = st.selectbox("Primary Diagnosis", 
                ["Diabetes", "Hypertension", "Heart Failure", "Stroke", "COPD", 
                 "Pneumonia", "Kidney Disease", "Cancer", "Other"])
            comorbidities_count = st.number_input("Number of Comorbidities", min_value=0, max_value=20, value=2)
            length_of_stay = st.number_input("Length of Stay (days)", min_value=1, max_value=90, value=5)
            readmission_risk_score = st.slider("Readmission Risk Score", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
            
        with col3:
            st.subheader("Treatment & Follow-up")
            treatment_type = st.selectbox("Treatment Type", ["Medical", "Surgical", "Interventional"])
            medications_count = st.number_input("Number of Medications", min_value=0, max_value=50, value=5)
            followup_visits_last_year = st.number_input("Follow-up Visits (Last Year)", min_value=0, max_value=50, value=3)
            prev_readmissions = st.number_input("Previous Readmissions", min_value=0, max_value=20, value=1)
            insurance_type = st.selectbox("Insurance Type", ["Private", "Medicare", "Medicaid", "Self-Pay"])
            discharge_disposition = st.selectbox("Discharge Disposition", 
                ["Home", "Home Health", "Skilled Nursing", "Rehab", "Other"])
            
        submit = st.form_submit_button("Predict Risk", use_container_width=True)
        
    if submit:
        data = {
            "season": season,
            "age": age,
            "gender": gender,
            "region": region,
            "primary_diagnosis": primary_diagnosis,
            "comorbidities_count": comorbidities_count,
            "length_of_stay": length_of_stay,
            "treatment_type": treatment_type,
            "medications_count": medications_count,
            "followup_visits_last_year": followup_visits_last_year,
            "prev_readmissions": prev_readmissions,
            "insurance_type": insurance_type,
            "discharge_disposition": discharge_disposition,
            "readmission_risk_score": readmission_risk_score
        }
        
        with st.spinner("Analyzing patient data..."):
            result = get_prediction(data)
            
        if result:
            st.divider()
            st.subheader("Prediction Results")
            st.info(f"Model Used: **{result.get('model_type', 'Unknown')}**")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                risk_cat = result["risk_category"]
                color = "green" if risk_cat == "Low Risk" else "orange" if risk_cat == "Medium Risk" else "red"
                
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; background-color: {color}; color: white; border-radius: 10px;">
                    <h2>{risk_cat}</h2>
                    <h1>{result['probability']:.1%}</h1>
                    <p>Probability of Readmission</p>
                    <p><strong>{result['prediction']}</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                st.markdown("#### Key Risk Factors (Explainable AI)")
                factors = result["feature_importance"]
                
                if factors and "Feature importance unavailable" not in factors:
                    df_factors = pd.DataFrame({
                        "Feature": list(factors.keys()),
                        "Impact": list(factors.values())
                    })
                    df_factors["Impact_Pct"] = df_factors["Impact"] * 100
                    df_factors["Color"] = df_factors["Impact"].apply(
                        lambda x: "Increases Risk" if x > 0 else "Decreases Risk"
                    )
                    
                    fig = px.bar(df_factors, x="Impact_Pct", y="Feature", color="Color",
                                color_discrete_map={"Increases Risk": "#ef553b", "Decreases Risk": "#00cc96"},
                                orientation='h', title="Top Contributing Factors",
                                text=df_factors["Impact_Pct"].apply(lambda x: f"{x:+.1f}%"))
                    fig.update_layout(yaxis={'categoryorder':'total ascending'}, 
                                    xaxis_title="Impact on Readmission Risk (%)")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Feature importance not available for this prediction.")

elif page == "Analytics Dashboard":
    st.title("Analytics Dashboard")
    
    try:
        df = pd.read_csv(DATASET_PATH)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Readmission by Primary Diagnosis")
            diag_rates = df.groupby('primary_diagnosis')['label'].mean().sort_values()
            fig = px.bar(x=diag_rates.values, y=diag_rates.index, orientation='h',
                        labels={'x': 'Readmission Rate', 'y': 'Diagnosis'},
                        color=diag_rates.values, color_continuous_scale='Reds')
            fig.update_layout(xaxis_tickformat='.0%', showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Age Distribution by Readmission")
            fig = px.histogram(df, x="age", color=df['label'].map({0: 'Not Readmitted', 1: 'Readmitted'}),
                             barmode="overlay", nbins=30, color_discrete_sequence=["#00cc96", "#ef553b"])
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("Impact of Previous Readmissions")
            prev_rates = df.groupby('prev_readmissions')['label'].mean().reset_index()
            fig = px.bar(prev_rates, x='prev_readmissions', y='label',
                        labels={'label': 'Readmission Rate'},
                        color='prev_readmissions', color_continuous_scale='Viridis')
            fig.update_layout(yaxis_tickformat='.0%')
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Length of Stay vs Readmission")
            fig = px.box(df, x=df['label'].map({0: 'Not Readmitted', 1: 'Readmitted'}), 
                        y="length_of_stay", color=df['label'].map({0: 'Not Readmitted', 1: 'Readmitted'}),
                        color_discrete_sequence=["#00cc96", "#ef553b"])
            st.plotly_chart(fig, use_container_width=True)
            
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Readmission by Region")
            region_rates = df.groupby('region')['label'].mean()
            fig = px.bar(x=region_rates.index, y=region_rates.values,
                        labels={'x': 'Region', 'y': 'Readmission Rate'},
                        color=region_rates.values, color_continuous_scale='Blues')
            fig.update_layout(yaxis_tickformat='.0%')
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("Readmission by Season")
            season_rates = df.groupby('season')['label'].mean()
            fig = px.bar(x=season_rates.index, y=season_rates.values,
                        labels={'x': 'Season', 'y': 'Readmission Rate'},
                        color=season_rates.values, color_continuous_scale='Greens')
            fig.update_layout(yaxis_tickformat='.0%')
            st.plotly_chart(fig, use_container_width=True)
            
        with col3:
            st.subheader("Readmission by Treatment Type")
            treatment_rates = df.groupby('treatment_type')['label'].mean()
            fig = px.bar(x=treatment_rates.index, y=treatment_rates.values,
                        labels={'x': 'Treatment Type', 'y': 'Readmission Rate'},
                        color=treatment_rates.values, color_continuous_scale='Oranges')
            fig.update_layout(yaxis_tickformat='.0%')
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error loading analytics data: {e}")

elif page == "Model Performance":
    st.title("Model Performance & Explainability")
    
    try:
        with open("models/metrics.json", "r") as f:
            metrics = json.load(f)
            
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Accuracy", f"{metrics['accuracy']:.1%}")
        col2.metric("Precision", f"{metrics['precision']:.1%}")
        col3.metric("Recall", f"{metrics['recall']:.1%}")
        col4.metric("F1 Score", f"{metrics['f1_score']:.1%}")
        col5.metric("ROC AUC", f"{metrics['roc_auc']:.3f}")
        
        st.divider()
        st.subheader("Global Feature Importance")
        st.markdown("The following chart shows the most important features learned by the model.")
        
        import joblib
        model = joblib.load("models/random_forest_model.joblib")
        with open("models/feature_names.json", "r") as f:
            feature_names = json.load(f)
            
        importances = model.feature_importances_
        indices = np.argsort(importances)[-15:]
        
        importance_pct = importances[indices] * 100
        text_labels = [f"{val:.1f}%" for val in importance_pct]
        
        fig = go.Figure(go.Bar(
            x=importance_pct,
            y=[feature_names[i] for i in indices],
            orientation='h',
            marker=dict(
                color=importance_pct,
                colorscale='Viridis',
                showscale=False
            ),
            text=text_labels,
            textposition='auto'
        ))
        fig.update_layout(
            title="Top 15 Most Important Features", 
            height=600,
            xaxis_title="Importance (%)",
            yaxis_title="Feature"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading model metrics: {e}")
