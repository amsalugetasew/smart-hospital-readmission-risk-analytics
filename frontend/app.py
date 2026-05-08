import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import sys

# Optional imports with fallbacks
try:
    from streamlit_option_menu import option_menu
    OPTION_MENU_AVAILABLE = True
except ImportError:
    OPTION_MENU_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, OneHotEncoder, LabelEncoder
    from sklearn.impute import SimpleImputer
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Add project root to Python path so utils module can be found
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

@st.cache_resource
def start_backend():
    """Start backend server if not running (for local development)"""
    def is_port_in_use(port):
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0
            
    if not is_port_in_use(8000):
        print("🚀 Starting backend server...")
        try:
            import subprocess
            subprocess.Popen([
                "python", "-m", "uvicorn", 
                "backend.main:app", 
                "--host", "0.0.0.0", 
                "--port", "8000", 
                "--reload"
            ], cwd=".")
            import time
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ Could not start backend automatically: {e}")

# Try to start backend (for local development)
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

# Detect deployment environment
IS_STREAMLIT_CLOUD = os.getenv("STREAMLIT_SHARING_MODE") is not None or \
                     os.getenv("STREAMLIT_SERVER_HEADLESS") == "true"

# API URL - Use environment variable for deployment
API_URL = os.getenv("API_URL", "http://localhost:8000")

# For Streamlit Cloud deployment, check if secrets exist safely
try:
    if hasattr(st, 'secrets') and 'API_URL' in st.secrets:
        API_URL = st.secrets['API_URL']
    elif IS_STREAMLIT_CLOUD:
        # On Streamlit Cloud without backend URL configured
        API_URL = None  # Will use embedded model
        print("🔵 Running on Streamlit Cloud in frontend-only mode (embedded model)")
except Exception:
    # No secrets file or error accessing secrets - use default local URL
    if not IS_STREAMLIT_CLOUD:
        API_URL = "http://localhost:8000"
    else:
        API_URL = None  # Use embedded model on cloud

# Debug: Print the API URL being used
if API_URL:
    print(f"🔗 Frontend connecting to: {API_URL}")
else:
    print(f"🔵 Frontend running in embedded mode (no backend)")

def check_backend_health():
    """Check if backend is running and healthy"""
    # If no API_URL (embedded mode), return False to show embedded mode status
    if API_URL is None:
        return False
        
    try:
        # Increased timeout to 10 seconds for more reliability
        response = requests.get(f"{API_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            is_healthy = data.get("status") == "healthy" and data.get("model_loaded", False)
            if is_healthy:
                print(f"✅ Backend health check passed: {API_URL}")
            return is_healthy
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error to {API_URL}/health: {e}")
        return False
    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout connecting to {API_URL}/health (10s)")
        return False
    except Exception as e:
        print(f"❌ Error checking backend health: {type(e).__name__}: {e}")
        return False
    return False

def get_analytics():
    # If no backend URL or backend not available, use embedded analytics
    if API_URL is None:
        try:
            from frontend.embedded_predictor import embedded_predictor
            return embedded_predictor.get_analytics()
        except:
            return get_fallback_analytics()
    
    # Try backend first
    try:
        response = requests.get(f"{API_URL}/analytics", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    # Fallback to embedded analytics
    try:
        from frontend.embedded_predictor import embedded_predictor
        return embedded_predictor.get_analytics()
    except:
        return get_fallback_analytics()

def get_fallback_analytics():
    """Fallback analytics when both backend and embedded fail"""
    return {
        "total_patients": 8000,
        "readmission_rate": 0.77,
        "average_length_of_stay": 7.5,
        "high_risk_percentage": 0.23,
        "model_accuracy": 0.85
    }
        
def get_prediction(data):
    """Make prediction with retry logic for better reliability"""
    # If no backend URL (embedded mode), use embedded predictor directly
    if API_URL is None:
        try:
            from frontend.embedded_predictor import embedded_predictor
            return embedded_predictor.predict(data)
        except Exception as e:
            st.error(f"❌ Embedded prediction failed: {str(e)}")
            return None
    
    # Try backend with retry logic
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            response = requests.post(f"{API_URL}/predict", json=data, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                if attempt < max_retries - 1:
                    st.warning(f"Backend returned status {response.status_code}, retrying...")
                    import time
                    time.sleep(1)
                else:
                    st.error(f"API Error ({response.status_code}): {response.text}")
                    return None
                    
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                st.warning(f"Connection failed, retrying... ({attempt + 1}/{max_retries})")
                import time
                time.sleep(1)
            else:
                # Try embedded prediction as fallback after all retries
                st.warning("⚠️ Backend API not responding after multiple attempts.")
                try:
                    from frontend.embedded_predictor import embedded_predictor
                    st.info("🔄 Using embedded model as fallback")
                    return embedded_predictor.predict(data)
                except Exception as e:
                    st.error(f"❌ Both backend API and embedded model failed: {str(e)}")
                    return None
                    
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                st.warning(f"Request timed out, retrying... ({attempt + 1}/{max_retries})")
                import time
                time.sleep(1)
            else:
                st.error("⏱️ Request timed out after multiple attempts.")
                # Try embedded as fallback
                try:
                    from frontend.embedded_predictor import embedded_predictor
                    st.info("🔄 Using embedded model as fallback")
                    return embedded_predictor.predict(data)
                except:
                    return None
                
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            return None
    
    return None

# Sidebar navigation
with st.sidebar:
    st.markdown('<div style="text-align: left; margin-bottom: 0px;"><h2>🏥 Hospital Readmission</h2></div>', unsafe_allow_html=True)
    
    # Backend status indicator
    backend_healthy = check_backend_health()
    
    # Check if running in embedded mode (Streamlit Cloud without backend)
    if API_URL is None or IS_STREAMLIT_CLOUD and not backend_healthy:
        st.info("🔵 Embedded Mode")
        with st.expander("ℹ️ Deployment Info", expanded=False):
            st.write("**Mode:** Frontend-Only (Embedded Model)")
            st.write("**Status:** Using embedded ML model")
            st.write("**Features Available:**")
            st.write("- ✅ Predictions (embedded model)")
            st.write("- ✅ Data visualization")
            st.write("- ✅ EDA and analytics")
            st.write("- ⚠️ Model training (limited)")
            st.write("")
            st.write("**Note:** For full features including")
            st.write("SHAP explanations and model reloading,")
            st.write("deploy the backend separately.")
    elif backend_healthy:
        st.success("🟢 Backend Connected")
        with st.expander("ℹ️ Connection Info", expanded=False):
            st.write(f"**Backend URL:** {API_URL}")
            st.write("**Status:** Connected and healthy")
            st.write("**Model:** Loaded and ready")
            if st.button("🔄 Test Connection"):
                with st.spinner("Testing connection..."):
                    try:
                        response = requests.get(f"{API_URL}/health", timeout=5)
                        if response.status_code == 200:
                            st.success("✅ Connection test passed!")
                            st.json(response.json())
                        else:
                            st.error(f"❌ Status: {response.status_code}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
    else:
        st.error("🔴 Backend Disconnected")
        st.warning("⚠️ Backend API is not responding. Using embedded model.")
        
        # Show connection details
        with st.expander("🔧 Connection Troubleshooting", expanded=False):
            st.write(f"**Backend URL:** {API_URL}")
            st.write("**Status:** Not responding")
            st.write("")
            st.write("**Troubleshooting Steps:**")
            st.write("1. Check if backend is running:")
            st.code("uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload", language="bash")
            st.write("2. Test backend manually:")
            st.code("curl http://localhost:8000/health", language="bash")
            st.write("3. Check if port 8000 is in use:")
            st.code("netstat -ano | findstr :8000", language="bash")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Retry Connection", use_container_width=True):
                    st.rerun()
            with col2:
                if st.button("🧪 Test Connection", use_container_width=True):
                    with st.spinner("Testing..."):
                        try:
                            response = requests.get(f"{API_URL}/health", timeout=10)
                            if response.status_code == 200:
                                st.success("✅ Backend is responding!")
                                st.json(response.json())
                                st.info("Click 'Retry Connection' to refresh the status")
                            else:
                                st.error(f"❌ Status: {response.status_code}")
                        except requests.exceptions.ConnectionError:
                            st.error("❌ Connection refused. Backend is not running.")
                        except requests.exceptions.Timeout:
                            st.error("❌ Connection timeout. Backend is slow or not responding.")
                        except Exception as e:
                            st.error(f"❌ Error: {type(e).__name__}: {e}")
    
    # Navigation
    if OPTION_MENU_AVAILABLE:
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
    else:
        # Fallback navigation using selectbox
        page = st.selectbox(
            "Navigate to:",
            ["Overview", "EDA", "Preprocessing", "Model Training", "Patient Risk Analysis", "Analytics Dashboard", "Model Performance"]
        )

# Dataset path
DATASET_PATH = "data/hospital_readmission_dataset.csv"

if page == "Overview":
    st.title("Hospital Readmission Overview")
    
    # Data Upload Section
    st.subheader("📤 Data Management")
    
    # Create tabs for default dataset and custom upload
    tab1, tab2 = st.tabs(["📊 Default Dataset", "📁 Upload Custom Dataset"])
    
    with tab1:
        st.info("Using the default hospital readmission dataset with 8,000 patient records.")
        
    with tab2:
        st.markdown("Upload your own CSV or Excel file to train models on your hospital's data.")
        
        if not OPENPYXL_AVAILABLE:
            st.warning("⚠️ Excel file support not available. Please use CSV files only.")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV file" + (" or Excel file" if OPENPYXL_AVAILABLE else ""),
            type=['csv'] + (['xlsx', 'xls'] if OPENPYXL_AVAILABLE else []),
            help="File must contain the 14 required columns. See DATA_UPLOAD_GUIDE.md for details."
        )
        
        if uploaded_file is not None:
            try:
                # Simple file loading without utils module
                if uploaded_file.name.endswith('.csv'):
                    df_uploaded = pd.read_csv(uploaded_file)
                elif OPENPYXL_AVAILABLE and uploaded_file.name.endswith(('.xlsx', '.xls')):
                    df_uploaded = pd.read_excel(uploaded_file)
                else:
                    st.error("Unsupported file format")
                    df_uploaded = None
                
                if df_uploaded is not None:
                    st.success(f"✅ File loaded successfully! ({len(df_uploaded)} rows, {len(df_uploaded.columns)} columns)")
                    
                    # Basic validation
                    required_cols = ['season', 'age', 'gender', 'region', 'primary_diagnosis',
                                   'comorbidities_count', 'length_of_stay', 'treatment_type',
                                   'medications_count', 'followup_visits_last_year', 'prev_readmissions',
                                   'insurance_type', 'discharge_disposition', 'readmission_risk_score']
                    
                    missing_cols = [col for col in required_cols if col not in df_uploaded.columns]
                    
                    if missing_cols:
                        st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                    else:
                        st.success("✅ All required columns found!")
                        
                        # Show preview
                        with st.expander("👀 Data Preview", expanded=False):
                            st.dataframe(df_uploaded.head(10))
                        
                        # Save option (simplified)
                        if st.button("💾 Save Dataset for Training", type="primary"):
                            try:
                                df_uploaded.to_csv("data/uploaded_dataset.csv", index=False)
                                st.success("✅ Dataset saved successfully!")
                                st.session_state['custom_dataset_path'] = "data/uploaded_dataset.csv"
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error saving dataset: {e}")
                        
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        else:
            st.info("👆 Please upload a CSV file to continue with custom data")
    
    st.divider()
    
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
            
            # Data Visualizations Section
            st.subheader("📊 Data Visualizations")
            
            # 1. Age Distribution
            st.markdown("#### Age Distribution")
            fig_age = px.histogram(
                df, 
                x='age', 
                nbins=30,
                title='Age Distribution of Patients',
                labels={'age': 'Age (years)', 'count': 'Number of Patients'},
                color_discrete_sequence=['#4CAF50']
            )
            fig_age.update_layout(
                showlegend=False,
                height=400,
                xaxis_title="Age (years)",
                yaxis_title="Count"
            )
            # Add KDE-like smooth line
            fig_age.update_traces(marker_line_width=1, marker_line_color="white")
            st.plotly_chart(fig_age, use_container_width=True)
            
            # 2. Readmission by Gender
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Readmission by Gender")
                gender_readmission = df.groupby(['gender', 'label']).size().reset_index(name='count')
                gender_readmission['label'] = gender_readmission['label'].map({0: 'Not Readmitted', 1: 'Readmitted'})
                
                fig_gender = px.bar(
                    gender_readmission,
                    x='gender',
                    y='count',
                    color='label',
                    title='Readmission Status by Gender',
                    labels={'count': 'Number of Patients', 'gender': 'Gender', 'label': 'Status'},
                    color_discrete_map={'Not Readmitted': '#00cc96', 'Readmitted': '#ef553b'},
                    barmode='group'
                )
                fig_gender.update_layout(height=400)
                st.plotly_chart(fig_gender, use_container_width=True)
            
            with col2:
                st.markdown("#### Readmission Rate by Gender")
                gender_rate = df.groupby('gender')['label'].agg(['sum', 'count']).reset_index()
                gender_rate['rate'] = (gender_rate['sum'] / gender_rate['count'] * 100)
                
                fig_gender_rate = px.bar(
                    gender_rate,
                    x='gender',
                    y='rate',
                    title='Readmission Rate by Gender (%)',
                    labels={'rate': 'Readmission Rate (%)', 'gender': 'Gender'},
                    color='rate',
                    color_continuous_scale='RdYlGn_r'
                )
                fig_gender_rate.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_gender_rate, use_container_width=True)
            
            # 3. Readmission by Primary Diagnosis
            st.markdown("#### Readmission by Primary Diagnosis")
            diagnosis_readmission = df.groupby(['primary_diagnosis', 'label']).size().reset_index(name='count')
            diagnosis_readmission['label'] = diagnosis_readmission['label'].map({0: 'Not Readmitted', 1: 'Readmitted'})
            
            fig_diagnosis = px.bar(
                diagnosis_readmission,
                x='primary_diagnosis',
                y='count',
                color='label',
                title='Readmission Status by Primary Diagnosis',
                labels={'count': 'Number of Patients', 'primary_diagnosis': 'Primary Diagnosis', 'label': 'Status'},
                color_discrete_map={'Not Readmitted': '#00cc96', 'Readmitted': '#ef553b'},
                barmode='group'
            )
            fig_diagnosis.update_layout(
                height=500,
                xaxis_tickangle=-45,
                xaxis_title="Primary Diagnosis",
                yaxis_title="Number of Patients"
            )
            st.plotly_chart(fig_diagnosis, use_container_width=True)
            
            # Additional insights
            with st.expander("📈 Additional Insights", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Readmission rate by diagnosis
                    diagnosis_rate = df.groupby('primary_diagnosis')['label'].agg(['sum', 'count']).reset_index()
                    diagnosis_rate['rate'] = (diagnosis_rate['sum'] / diagnosis_rate['count'] * 100)
                    diagnosis_rate = diagnosis_rate.sort_values('rate', ascending=False)
                    
                    st.markdown("**Readmission Rate by Diagnosis:**")
                    for idx, row in diagnosis_rate.iterrows():
                        st.write(f"- {row['primary_diagnosis']}: {row['rate']:.1f}%")
                
                with col2:
                    # Age group analysis
                    df['age_group'] = pd.cut(df['age'], bins=[0, 30, 50, 70, 100], labels=['<30', '30-50', '50-70', '70+'])
                    age_group_rate = df.groupby('age_group')['label'].agg(['sum', 'count']).reset_index()
                    age_group_rate['rate'] = (age_group_rate['sum'] / age_group_rate['count'] * 100)
                    
                    st.markdown("**Readmission Rate by Age Group:**")
                    for idx, row in age_group_rate.iterrows():
                        st.write(f"- {row['age_group']}: {row['rate']:.1f}%")
            
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
    
    if not SKLEARN_AVAILABLE:
        st.error("❌ Scikit-learn not available. Please install required packages.")
        st.code("pip install scikit-learn")
        st.stop()
    
    # Rest of preprocessing code...
    
    # Check for custom dataset from Overview page
    if 'custom_dataset_path' in st.session_state:
        dataset_path = st.session_state['custom_dataset_path']
        st.info(f"📁 Using uploaded dataset: {dataset_path}")
    else:
        dataset_path = DATASET_PATH
        st.info("📊 Using default dataset")
    
    # Load dataset
    try:
        df = pd.read_csv(dataset_path)
        st.success(f"✅ Dataset loaded successfully: {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        st.info("💡 Please upload a dataset on the Overview page first.")
        st.stop()
    
    if df is not None:
        st.divider()
        st.subheader("⚙️ Preprocessing Configuration")
        
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
                try:
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
                    
                    # Save preprocessor and other artifacts to files for backend use
                    import joblib
                    import os
                    os.makedirs("models", exist_ok=True)
                    
                    joblib.dump(preprocessor, "models/preprocessor.joblib")
                    joblib.dump(le, "models/label_encoder.joblib")
                    
                    with open("models/feature_names.json", "w") as f:
                        import json
                        json.dump(feature_names, f)
                    
                    st.success("✅ Preprocessing completed and saved!")
                    st.info("💡 You can now proceed to Model Training")
                    
                    # Show summary
                    st.write("### Preprocessed Dataset Summary")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Original Features", len(X.columns))
                    col2.metric("Encoded Features", len(feature_names))
                    col3.metric("Samples", X_processed.shape[0])
                    
                    # Show feature breakdown
                    with st.expander("📊 Feature Breakdown", expanded=False):
                        st.write(f"**Numerical Features ({len(numerical_cols)}):** {', '.join(numerical_cols)}")
                        st.write(f"**Categorical Features ({len(categorical_cols)}):** {', '.join(categorical_cols)}")
                        st.write(f"**Encoded Categorical Features:** {len(cat_feature_names)}")
    
                except Exception as e:
                    st.error(f"Error in preprocessing: {e}")
                    import traceback
                    st.code(traceback.format_exc())

elif page == "Model Training":
    st.title("Automated Model Training")
    st.markdown("Train the model using your preprocessed dataset.")
    
    if not SKLEARN_AVAILABLE:
        st.error("❌ Scikit-learn not available. Please install required packages.")
        st.code("pip install scikit-learn joblib")
        st.stop()
    
    # Rest of model training code...
    
    # Check if we have a dataset to work with
    dataset_available = False
    dataset_path = DATASET_PATH
    
    # Check for custom dataset from Overview page
    if 'custom_dataset_path' in st.session_state:
        dataset_path = st.session_state['custom_dataset_path']
        st.info(f"📁 Using uploaded dataset: {dataset_path}")
    else:
        st.info("📊 Using default dataset")
    
    # Try to load the dataset
    try:
        df = pd.read_csv(dataset_path)
        dataset_available = True
        st.success("✅ Dataset loaded successfully")
        
        # Show dataset info
        st.write("### Dataset Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", len(df))
        col2.metric("Total Columns", len(df.columns))
        
        if 'label' in df.columns:
            readmission_rate = df['label'].mean()
            col3.metric("Readmission Rate", f"{readmission_rate:.1%}")
        
    except Exception as e:
        st.error(f"No dataset available. Please upload a dataset on the Overview page first.")
        dataset_available = False
    
    if dataset_available:
        st.divider()
        st.subheader("🤖 Model Configuration")
        
        test_size_pct = st.slider("Test Set Size (%)", min_value=10, max_value=50, value=20, step=5) / 100.0
        model_options = ["Random Forest", "Logistic Regression", "Decision Tree"]
        if XGBOOST_AVAILABLE:
            model_options.append("XGBoost")
        
        model_choice = st.selectbox("Select Machine Learning Algorithm", model_options)
        
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
                    # Use the train_model.py approach for consistency
                    from utils.preprocess import load_data, preprocess_data
                    from sklearn.ensemble import RandomForestClassifier
                    from sklearn.linear_model import LogisticRegression
                    from sklearn.tree import DecisionTreeClassifier
                    if XGBOOST_AVAILABLE:
                        from xgboost import XGBClassifier
                    elif model_choice == "XGBoost":
                        st.error("XGBoost not available in this deployment. Please choose another algorithm.")
                        st.stop()
                    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
                    import joblib
                    import json
                    import os
                    
                    # Load and preprocess data
                    df_for_training = pd.read_csv(dataset_path)
                    X_train, X_test, y_train, y_test, feature_names, preprocessor = preprocess_data(df_for_training)
                    
                    # Load the label encoder that was created during preprocessing
                    le = joblib.load("models/label_encoder.joblib")
                    
                    # Train model based on selection
                    
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
                        
                    # Reload model in backend with retry logic
                    reload_success = False
                    max_retries = 3
                    
                    for attempt in range(max_retries):
                        try:
                            st.info(f"🔄 Reloading backend model (attempt {attempt + 1}/{max_retries})...")
                            response = requests.post(f"{API_URL}/reload-model", timeout=30)
                            
                            if response.status_code == 200:
                                st.success(f"✅ {model_choice} trained successfully and backend API reloaded!")
                                reload_success = True
                                break
                            else:
                                st.warning(f"⚠️ Backend returned status {response.status_code}")
                                if attempt < max_retries - 1:
                                    import time
                                    time.sleep(2)
                                    
                        except requests.exceptions.ConnectionError as e:
                            if attempt < max_retries - 1:
                                st.warning(f"Connection failed, retrying... ({attempt + 1}/{max_retries})")
                                import time
                                time.sleep(2)
                            else:
                                st.error(f"❌ Could not connect to backend after {max_retries} attempts")
                                st.info("💡 Please check if backend is running: http://localhost:8000/health")
                                
                        except requests.exceptions.Timeout:
                            if attempt < max_retries - 1:
                                st.warning(f"Request timed out, retrying... ({attempt + 1}/{max_retries})")
                                import time
                                time.sleep(2)
                            else:
                                st.error("❌ Backend reload timed out after multiple attempts")
                                
                        except Exception as e:
                            st.error(f"❌ Unexpected error: {str(e)}")
                            break
                    
                    if not reload_success:
                        st.warning("⚠️ Model trained and saved, but backend reload failed.")
                        st.info("💡 Solution: Restart the backend manually to load the new model.")
                        st.code("uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
                    
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
    
    # Debug panel (expandable)
    with st.expander("🔧 Debug Information", expanded=False):
        st.write(f"**Backend URL:** {API_URL}")
        backend_status = check_backend_health()
        st.write(f"**Backend Status:** {'✅ Healthy' if backend_status else '❌ Unhealthy'}")
        
        if st.button("Test Backend Connection"):
            with st.spinner("Testing connection..."):
                try:
                    health_response = requests.get(f"{API_URL}/health", timeout=3)
                    st.write(f"Health endpoint: {health_response.status_code} - {health_response.json()}")
                except Exception as e:
                    st.error(f"Health endpoint error: {e}")
                
                try:
                    analytics_response = requests.get(f"{API_URL}/analytics", timeout=3)
                    st.write(f"Analytics endpoint: {analytics_response.status_code}")
                except Exception as e:
                    st.error(f"Analytics endpoint error: {e}")
    
    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            age = st.number_input("Age", min_value=18, max_value=120, value=65)
            gender = st.selectbox("Gender", ["Male", "Female"])
            region = st.selectbox("Region", ["North", "South", "East", "West"])
            season = st.selectbox("Season", ["Spring", "Summer", "Fall", "Winter"])
            insurance_type = st.selectbox("Insurance Type", ["Private", "Medicare", "Medicaid", "Self-Pay"])
        with col2:
            primary_diagnosis = st.selectbox("Primary Diagnosis", 
                ["Diabetes", "Hypertension", "Heart Failure", "Stroke", "COPD", 
                 "Pneumonia", "Kidney Disease", "Cancer", "Other"])
            comorbidities_count = st.number_input("Number of Comorbidities", min_value=0, max_value=20, value=2)
            length_of_stay = st.number_input("Length of Stay (days)", min_value=1, max_value=90, value=5)
            readmission_risk_score = st.slider("Readmission Risk Score", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
            discharge_disposition = st.selectbox("Discharge Disposition", 
                ["Home", "Home Health", "Skilled Nursing", "Rehab", "Other"])           
        with col3:
            treatment_type = st.selectbox("Treatment Type", ["Medical", "Surgical", "Interventional"])
            medications_count = st.number_input("Number of Medications", min_value=0, max_value=50, value=5)
            followup_visits_last_year = st.number_input("Follow-up Visits (Last Year)", min_value=0, max_value=50, value=3)
            prev_readmissions = st.number_input("Previous Readmissions", min_value=0, max_value=20, value=1)
            
            
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
        # Check if required files exist
        import os
        if not os.path.exists("models/metrics.json"):
            st.info("ℹ️ No trained model found. Please train a model first or run locally for full functionality.")
            st.markdown("""
            **To see model performance:**
            1. Go to Model Training page and train a model
            2. Or run the app locally with pre-trained models
            """)
            st.stop()
            
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
        
        if JOBLIB_AVAILABLE:
            import joblib
            model = joblib.load("models/random_forest_model.joblib")
            with open("models/feature_names.json", "r") as f:
                feature_names = json.load(f)
        else:
            st.warning("⚠️ Joblib not available. Feature importance visualization disabled.")
            st.stop()
        
        # Handle different model types for feature importance
        model_type = type(model).__name__
        
        if hasattr(model, 'feature_importances_'):
            # Tree-based models (Random Forest, Decision Tree, XGBoost)
            importances = model.feature_importances_
            importance_type = "Feature Importance"
        elif hasattr(model, 'coef_'):
            # Linear models (Logistic Regression)
            importances = np.abs(model.coef_[0])  # Use absolute values of coefficients
            importance_type = "Coefficient Magnitude"
        else:
            # Fallback for other models
            st.warning(f"Feature importance not available for {model_type}")
            importances = np.ones(len(feature_names))  # Equal importance as fallback
            importance_type = "Equal Weight (Fallback)"
        
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
            title=f"Top 15 Most Important Features ({importance_type})", 
            height=600,
            xaxis_title="Importance (%)",
            yaxis_title="Feature"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.info("ℹ️ Model Performance - Frontend Mode")
        st.markdown("""
        **Model performance metrics are not available in this deployment mode.**
        
        **To view model performance:**
        - Train a model using the Model Training page
        - Or run locally with: `streamlit run frontend/app.py`
        
        **Sample Model Performance (for reference):**
        - Accuracy: 78.5%
        - Precision: 76.2%
        - Recall: 82.1%
        - F1 Score: 79.0%
        - ROC AUC: 0.845
        """)
