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

# Dataset path management - Initialize before sidebar
DEFAULT_DATASET_PATH = "data/hospital_readmission_dataset.csv"
UPLOADED_DATASET_PATH = "data/uploaded_dataset.csv"

# Initialize session state for dataset path
if 'active_dataset_path' not in st.session_state:
    # Check if uploaded dataset exists
    if os.path.exists(UPLOADED_DATASET_PATH):
        st.session_state['active_dataset_path'] = UPLOADED_DATASET_PATH
        st.session_state['using_uploaded_data'] = True
    else:
        st.session_state['active_dataset_path'] = DEFAULT_DATASET_PATH
        st.session_state['using_uploaded_data'] = False

# Get current active dataset path
DATASET_PATH = st.session_state['active_dataset_path']

# Sidebar navigation
with st.sidebar:
    st.markdown('<div style="text-align: left; margin-bottom: 0px;"><h2>🏥 Hospital Readmission</h2></div>', unsafe_allow_html=True)
    
    # Dataset indicator
    st.markdown("---")
    if st.session_state.get('using_uploaded_data', False):
        st.info("📊 **Active Dataset:** Uploaded Data")
        if os.path.exists(DATASET_PATH):
            try:
                df_check = pd.read_csv(DATASET_PATH)
                st.caption(f"📁 {len(df_check):,} records")
            except:
                pass
    else:
        st.success("📊 **Active Dataset:** Default Data")
        if os.path.exists(DATASET_PATH):
            try:
                df_check = pd.read_csv(DATASET_PATH)
                st.caption(f"📁 {len(df_check):,} records")
            except:
                pass
    st.markdown("---")
    
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
            options=["Dataset Upload", "EDA", "Preprocessing", "Model Training", "Patient Risk Analysis", "Analytics Dashboard", "Model Performance"],
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
            ["Dataset Upload", "EDA", "Preprocessing", "Model Training", "Patient Risk Analysis", "Analytics Dashboard", "Model Performance"]
        )

if page == "Dataset Upload":
    st.title("Hospital Readmission Overview")
    
    # Data Upload Section
    st.subheader("📤 Data Management")
    
    # Show current dataset status
    if st.session_state.get('using_uploaded_data', False):
        st.info(f"🔵 **Currently using uploaded dataset**: `{os.path.basename(DATASET_PATH)}`")
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Switch to Default Dataset"):
                st.session_state['active_dataset_path'] = DEFAULT_DATASET_PATH
                st.session_state['using_uploaded_data'] = False
                st.success("✅ Switched to default dataset!")
                st.rerun()
    else:
        st.info(f"🟢 **Currently using default dataset**: `{os.path.basename(DATASET_PATH)}`")
    
    st.divider()
    
    # Create tabs for default dataset and custom upload
    tab1, tab2 = st.tabs(["📊 Default Dataset", "📁 Upload Custom Dataset"])
    
    with tab1:
        st.info("Using the default hospital readmission dataset with 8,000 patient records.")
        if os.path.exists(DEFAULT_DATASET_PATH):
            df_default = pd.read_csv(DEFAULT_DATASET_PATH)
            st.write(f"**Records:** {len(df_default):,}")
            st.write(f"**Features:** {len(df_default.columns)}")
            if not st.session_state.get('using_uploaded_data', False):
                st.success("✅ This dataset is currently active")
        
    with tab2:
        st.markdown("Upload your own CSV or Excel file to use across all pages (Overview, EDA, Preprocessing, Model Training, Analytics Dashboard).")
        
        if not OPENPYXL_AVAILABLE:
            st.warning("⚠️ Excel file support not available. Please use CSV files only.")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV file" + (" or Excel file" if OPENPYXL_AVAILABLE else ""),
            type=['csv'] + (['xlsx', 'xls'] if OPENPYXL_AVAILABLE else []),
            help="File must contain the 14 required columns for training. The 'label' column (0 or 1) is required for model training.",
            key="data_uploader"
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
                        st.info("💡 Required columns: " + ", ".join(required_cols))
                    else:
                        st.success("✅ All required columns found!")
                        
                        # Check for label column
                        if 'label' not in df_uploaded.columns:
                            st.warning("⚠️ 'label' column not found. This column is required for model training (0 = Not Readmitted, 1 = Readmitted).")
                        
                        # Show preview
                        with st.expander("👀 Data Preview", expanded=False):
                            st.dataframe(df_uploaded.head(10))
                        
                        # Show statistics
                        with st.expander("📊 Dataset Statistics", expanded=False):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Records", f"{len(df_uploaded):,}")
                            with col2:
                                st.metric("Total Features", len(df_uploaded.columns))
                            with col3:
                                st.metric("Missing Values", df_uploaded.isna().sum().sum())
                        
                        # Save and activate option
                        st.markdown("---")
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown("**💾 Save and activate this dataset for all pages:**")
                            st.caption("This will replace the current active dataset and apply to Overview, EDA, Preprocessing, Model Training, and Analytics Dashboard.")
                        with col2:
                            if st.button("💾 Save & Activate Dataset", type="primary", use_container_width=True):
                                try:
                                    # Save the uploaded dataset
                                    df_uploaded.to_csv(UPLOADED_DATASET_PATH, index=False)
                                    
                                    # Update session state to use uploaded dataset
                                    st.session_state['active_dataset_path'] = UPLOADED_DATASET_PATH
                                    st.session_state['using_uploaded_data'] = True
                                    
                                    st.success("✅ Dataset saved and activated successfully!")
                                    st.info("🔄 All pages will now use this dataset. Refreshing...")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error saving dataset: {e}")
                        
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        else:
            st.info("👆 Please upload a CSV or Excel file to continue with custom data")
    
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
            
            # Show which dataset is being used
            if st.session_state.get('using_uploaded_data', False):
                st.info(f"📊 **Displaying statistics for:** Uploaded Dataset ({len(df):,} records)")
            else:
                st.info(f"📊 **Displaying statistics for:** Default Dataset ({len(df):,} records)")
            
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
            st.subheader("📋 Dataset Upload")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Dataset Statistics:**")
                st.write(f"- Total Records: **{len(df):,}**")
                total_features = len(df.columns)
                st.write(f"- Total Features: **{total_features}**")
                # Count training features (exclude patient_id, admission_date, label)
                training_features = total_features - len([col for col in ['patient_id', 'admission_date', 'label'] if col in df.columns])
                st.write(f"- Training Features: **{training_features}**")
                st.write(f"- Missing Values: **{df.isna().sum().sum()}**")
                
            with col2:
                st.markdown("**Target Distribution:**")
                if 'label' in df.columns:
                    readmitted_count = (df['label'] == 1).sum()
                    not_readmitted_count = (df['label'] == 0).sum()
                    st.write(f"- Readmitted: **{readmitted_count:,}** ({readmitted_count/len(df)*100:.1f}%)")
                    st.write(f"- Not Readmitted: **{not_readmitted_count:,}** ({not_readmitted_count/len(df)*100:.1f}%)")
                    if not_readmitted_count > 0:
                        st.write(f"- Class Imbalance: **{readmitted_count/not_readmitted_count:.2f}:1**")
                else:
                    st.warning("⚠️ 'label' column not found in dataset")
                
            with col3:
                st.markdown("**Key Statistics:**")
                if 'age' in df.columns:
                    st.write(f"- Avg Age: **{df['age'].mean():.1f}** years")
                if 'comorbidities_count' in df.columns:
                    st.write(f"- Avg Comorbidities: **{df['comorbidities_count'].mean():.1f}**")
                if 'medications_count' in df.columns:
                    st.write(f"- Avg Medications: **{df['medications_count'].mean():.1f}**")
                if 'readmission_risk_score' in df.columns:
                    st.write(f"- Avg Risk Score: **{df['readmission_risk_score'].mean():.2f}**")
            
            st.divider()
            
            # Feature Categories
            st.subheader("🔢 Feature Categories")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Numerical Features:**")
                numerical_features = [
                    "age", "comorbidities_count", "length_of_stay",
                    "medications_count", "followup_visits_last_year",
                    "prev_readmissions", "readmission_risk_score"
                ]
                # Only show features that exist in the dataset
                existing_numerical = [feat for feat in numerical_features if feat in df.columns]
                for feat in existing_numerical:
                    st.write(f"- {feat}")
                st.caption(f"Total: {len(existing_numerical)} features")
                    
            with col2:
                st.markdown("**Categorical Features:**")
                categorical_features = [
                    "season", "gender", "region", "primary_diagnosis",
                    "treatment_type", "insurance_type", "discharge_disposition"
                ]
                # Only show features that exist in the dataset
                existing_categorical = [feat for feat in categorical_features if feat in df.columns]
                for feat in existing_categorical:
                    unique_count = df[feat].nunique()
                    st.write(f"- {feat} ({unique_count} categories)")
                st.caption(f"Total: {len(existing_categorical)} features")
            
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
            
            # Retrain Embedded Model Section (if using uploaded data)
            if st.session_state.get('using_uploaded_data', False) and 'label' in df.columns:
                st.subheader("🤖 Retrain Embedded Model")
                st.info("💡 You can retrain the embedded model to use your uploaded dataset for predictions.")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("""
                    **Why retrain?**
                    - Use your hospital's data for predictions
                    - Model learns patterns from your patient population
                    - Improves prediction accuracy for your specific context
                    """)
                
                with col2:
                    if st.button("🔄 Retrain Embedded Model", type="primary", use_container_width=True):
                        with st.spinner("Training model on your data..."):
                            try:
                                # Import training function
                                import sys
                                sys.path.insert(0, '.')
                                from train_model import train_and_evaluate_model
                                
                                # Train the model
                                train_and_evaluate_model()
                                
                                # Reload embedded predictor
                                from frontend.embedded_predictor import embedded_predictor
                                embedded_predictor.load_models()
                                
                                st.success("✅ Embedded model retrained successfully!")
                                st.info("🔄 The model will now use your uploaded data for predictions.")
                                
                            except Exception as e:
                                st.error(f"❌ Error retraining model: {str(e)}")
                                st.info("💡 Try using the Model Training page for more control.")
            
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
    st.title("🔮 Patient Risk Prediction")
    st.markdown("Predict hospital readmission risk for individual patients or batch processing")
    
    # Create tabs for single vs batch prediction
    tab1, tab2 = st.tabs(["📝 Single Patient Prediction", "📊 Batch Prediction (Upload File)"])
    
    # ==================== TAB 1: SINGLE PATIENT PREDICTION ====================
    with tab1:
        st.markdown("### Enter Patient Details")
        st.markdown("Fill in the form below to predict readmission risk for a single patient.")
        
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
                
                
            submit = st.form_submit_button("🔮 Predict Risk", use_container_width=True)
            
        if submit:
            data = {
                "season": season.lower(),
                "age": age,
                "gender": gender.lower(),
                "region": region.lower(),
                "primary_diagnosis": primary_diagnosis,
                "comorbidities_count": comorbidities_count,
                "length_of_stay": length_of_stay,
                "treatment_type": treatment_type.lower(),
                "medications_count": medications_count,
                "followup_visits_last_year": followup_visits_last_year,
                "prev_readmissions": prev_readmissions,
                "insurance_type": insurance_type.lower(),
                "discharge_disposition": discharge_disposition.lower(),
                "readmission_risk_score": readmission_risk_score
            }
            
            with st.spinner("Analyzing patient data..."):
                result = get_prediction(data)
                
            if result:
                st.divider()
                st.subheader("📊 Prediction Results")
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
    
    # ==================== TAB 2: BATCH PREDICTION ====================
    with tab2:
        st.markdown("### 📤 Upload Patient Data File")
        st.markdown("Upload a CSV or Excel file with multiple patient records for batch prediction.")
        
        # Show required columns
        with st.expander("📋 Required Columns", expanded=False):
            st.markdown("""
            Your file must contain these **14 columns** (case-insensitive):
            
            **Categorical Columns:**
            - `season` - winter, spring, summer, fall
            - `gender` - male, female
            - `region` - north, south, east, west
            - `primary_diagnosis` - Diabetes, Hypertension, Heart Failure, etc.
            - `treatment_type` - medical, surgical, interventional
            - `insurance_type` - private, medicare, medicaid, self-pay
            - `discharge_disposition` - home, home health, skilled nursing, rehab, other
            
            **Numerical Columns:**
            - `age` - Patient age (18-120)
            - `comorbidities_count` - Number of comorbidities (0-20)
            - `length_of_stay` - Hospital stay in days (1-90)
            - `medications_count` - Number of medications (0-50)
            - `followup_visits_last_year` - Follow-up visits (0-50)
            - `prev_readmissions` - Previous readmissions (0-20)
            - `readmission_risk_score` - Risk score (0.0-1.0)
            
            **Optional Column:**
            - `patient_id` - Patient identifier (will be included in results)
            """)
        
        # Download template
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("📥 Download Template", use_container_width=True):
                # Create template DataFrame
                template_data = {
                    'patient_id': ['P001', 'P002', 'P003'],
                    'season': ['winter', 'spring', 'summer'],
                    'age': [65, 72, 58],
                    'gender': ['male', 'female', 'male'],
                    'region': ['north', 'south', 'east'],
                    'primary_diagnosis': ['Diabetes', 'Hypertension', 'Heart Failure'],
                    'comorbidities_count': [2, 3, 1],
                    'length_of_stay': [5, 7, 3],
                    'treatment_type': ['medical', 'surgical', 'medical'],
                    'medications_count': [5, 8, 4],
                    'followup_visits_last_year': [3, 2, 4],
                    'prev_readmissions': [1, 0, 2],
                    'insurance_type': ['private', 'medicare', 'medicaid'],
                    'discharge_disposition': ['home', 'home health', 'home'],
                    'readmission_risk_score': [0.5, 0.6, 0.7]
                }
                template_df = pd.DataFrame(template_data)
                
                # Convert to CSV
                csv = template_df.to_csv(index=False)
                st.download_button(
                    label="💾 Download CSV Template",
                    data=csv,
                    file_name="batch_prediction_template.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col2:
            st.info("💡 Download the template to see the correct format, then fill it with your patient data.")
        
        st.divider()
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload a file with patient data for batch prediction"
        )
        
        if uploaded_file is not None:
            try:
                # Load file
                if uploaded_file.name.endswith('.csv'):
                    df_batch = pd.read_csv(uploaded_file)
                else:
                    if OPENPYXL_AVAILABLE:
                        df_batch = pd.read_excel(uploaded_file)
                    else:
                        st.error("❌ Excel support not available. Please use CSV files.")
                        st.stop()
                
                st.success(f"✅ File loaded: {len(df_batch)} patients")
                
                # Show preview
                with st.expander("👀 Data Preview", expanded=True):
                    st.dataframe(df_batch.head(10), use_container_width=True)
                
                # Validate columns
                required_cols = ['season', 'age', 'gender', 'region', 'primary_diagnosis',
                               'comorbidities_count', 'length_of_stay', 'treatment_type',
                               'medications_count', 'followup_visits_last_year', 'prev_readmissions',
                               'insurance_type', 'discharge_disposition', 'readmission_risk_score']
                
                # Case-insensitive column matching
                df_batch.columns = df_batch.columns.str.lower().str.strip()
                missing_cols = [col for col in required_cols if col not in df_batch.columns]
                
                if missing_cols:
                    st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                    st.stop()
                
                # Check if patient_id exists
                has_patient_id = 'patient_id' in df_batch.columns
                
                # Predict button
                if st.button("🔮 Predict for All Patients", type="primary", use_container_width=True):
                    with st.spinner(f"Processing {len(df_batch)} patients..."):
                        results = []
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, row in df_batch.iterrows():
                            status_text.text(f"Processing patient {idx + 1}/{len(df_batch)}...")
                            
                            # Prepare data
                            patient_data = {
                                'season': str(row['season']).lower(),
                                'age': int(row['age']),
                                'gender': str(row['gender']).lower(),
                                'region': str(row['region']).lower(),
                                'primary_diagnosis': str(row['primary_diagnosis']),
                                'comorbidities_count': int(row['comorbidities_count']),
                                'length_of_stay': int(row['length_of_stay']),
                                'treatment_type': str(row['treatment_type']).lower(),
                                'medications_count': int(row['medications_count']),
                                'followup_visits_last_year': int(row['followup_visits_last_year']),
                                'prev_readmissions': int(row['prev_readmissions']),
                                'insurance_type': str(row['insurance_type']).lower(),
                                'discharge_disposition': str(row['discharge_disposition']).lower(),
                                'readmission_risk_score': float(row['readmission_risk_score'])
                            }
                            
                            # Get prediction
                            result = get_prediction(patient_data)
                            
                            if result:
                                result_row = {
                                    'prediction': result['prediction'],
                                    'probability': result['probability'],
                                    'risk_category': result['risk_category']
                                }
                                
                                # Add patient_id if exists
                                if has_patient_id:
                                    result_row['patient_id'] = row['patient_id']
                                
                                # Add original data
                                for col in required_cols:
                                    result_row[col] = row[col]
                                
                                results.append(result_row)
                            else:
                                # Handle failed prediction
                                result_row = {
                                    'prediction': 'Error',
                                    'probability': 0.0,
                                    'risk_category': 'Error'
                                }
                                if has_patient_id:
                                    result_row['patient_id'] = row['patient_id']
                                for col in required_cols:
                                    result_row[col] = row[col]
                                results.append(result_row)
                            
                            # Update progress
                            progress_bar.progress((idx + 1) / len(df_batch))
                        
                        status_text.text("✅ Processing complete!")
                        progress_bar.empty()
                        
                        # Create results DataFrame
                        df_results = pd.DataFrame(results)
                        
                        # Reorder columns
                        if has_patient_id:
                            cols_order = ['patient_id', 'prediction', 'probability', 'risk_category'] + required_cols
                        else:
                            cols_order = ['prediction', 'probability', 'risk_category'] + required_cols
                        df_results = df_results[cols_order]
                        
                        st.divider()
                        st.subheader("📊 Batch Prediction Results")
                        
                        # Summary statistics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        total_patients = len(df_results)
                        readmitted_count = (df_results['prediction'] == 'Readmitted').sum()
                        high_risk_count = (df_results['risk_category'] == 'High Risk').sum()
                        avg_probability = df_results['probability'].mean()
                        
                        col1.metric("Total Patients", total_patients)
                        col2.metric("Predicted Readmissions", readmitted_count, 
                                   delta=f"{readmitted_count/total_patients:.1%}")
                        col3.metric("High Risk Patients", high_risk_count,
                                   delta=f"{high_risk_count/total_patients:.1%}")
                        col4.metric("Avg Probability", f"{avg_probability:.1%}")
                        
                        st.divider()
                        
                        # Show results table
                        st.markdown("### 📋 Detailed Results")
                        
                        # Add color coding
                        def highlight_risk(row):
                            if row['risk_category'] == 'High Risk':
                                return ['background-color: #ffcccc'] * len(row)
                            elif row['risk_category'] == 'Medium Risk':
                                return ['background-color: #fff4cc'] * len(row)
                            else:
                                return ['background-color: #ccffcc'] * len(row)
                        
                        st.dataframe(
                            df_results.style.apply(highlight_risk, axis=1),
                            use_container_width=True,
                            height=400
                        )
                        
                        st.divider()
                        
                        # Download options
                        st.markdown("### 💾 Download Results")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # CSV download
                            csv = df_results.to_csv(index=False)
                            st.download_button(
                                label="📥 Download as CSV",
                                data=csv,
                                file_name=f"batch_predictions_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        with col2:
                            # Excel download
                            if OPENPYXL_AVAILABLE:
                                from io import BytesIO
                                buffer = BytesIO()
                                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                                    df_results.to_excel(writer, index=False, sheet_name='Predictions')
                                buffer.seek(0)
                                
                                st.download_button(
                                    label="📥 Download as Excel",
                                    data=buffer,
                                    file_name=f"batch_predictions_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                            else:
                                st.info("Excel download not available. Use CSV instead.")
                        
                        # Visualization
                        st.divider()
                        st.markdown("### 📈 Results Visualization")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Pie chart: Risk categories
                            risk_counts = df_results['risk_category'].value_counts()
                            fig = px.pie(
                                values=risk_counts.values,
                                names=risk_counts.index,
                                title="Risk Category Distribution",
                                color=risk_counts.index,
                                color_discrete_map={
                                    'Low Risk': '#00A86B',
                                    'Medium Risk': '#FF6B35',
                                    'High Risk': '#DC143C'
                                }
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Histogram: Probability distribution
                            fig = px.histogram(
                                df_results,
                                x='probability',
                                nbins=20,
                                title="Readmission Probability Distribution",
                                labels={'probability': 'Probability', 'count': 'Number of Patients'},
                                color_discrete_sequence=['#0066CC']
                            )
                            fig.update_layout(xaxis_tickformat='.0%')
                            st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                import traceback
                with st.expander("🔍 Error Details"):
                    st.code(traceback.format_exc())

elif page == "Analytics Dashboard":
    st.title("🏥 Hospital Analytics Dashboard")
    st.markdown("Comprehensive analytics with hospital-themed visualizations")
    
    try:
        df = pd.read_csv(DATASET_PATH)
        
        # Hospital-themed color palette
        HOSPITAL_COLORS = {
            'primary': '#0066CC',      # Medical Blue
            'success': '#00A86B',      # Medical Green
            'warning': '#FF6B35',      # Medical Orange
            'danger': '#DC143C',       # Medical Red
            'info': '#20B2AA',         # Medical Teal
            'purple': '#9370DB',       # Medical Purple
            'navy': '#000080',         # Navy Blue
            'gradient_safe': ['#00A86B', '#90EE90', '#98FB98'],  # Green gradient (safe)
            'gradient_risk': ['#FFD700', '#FFA500', '#FF6347', '#DC143C'],  # Risk gradient
            'gradient_blue': ['#E3F2FD', '#90CAF9', '#42A5F5', '#1E88E5', '#1565C0'],  # Blue gradient
            'categorical': ['#0066CC', '#00A86B', '#FF6B35', '#9370DB', '#20B2AA', '#DC143C']
        }
        
        # Key Metrics Section
        st.markdown("### 📊 Key Performance Indicators")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_patients = len(df)
        readmitted = (df['label'] == 1).sum()
        readmission_rate = readmitted / total_patients
        avg_los = df['length_of_stay'].mean()
        high_risk = (df['readmission_risk_score'] > 0.7).sum()
        
        with col1:
            st.metric("Total Patients", f"{total_patients:,}", 
                     help="Total number of patients in the dataset")
        with col2:
            st.metric("Readmission Rate", f"{readmission_rate:.1%}", 
                     delta=f"{readmitted:,} patients",
                     delta_color="inverse",
                     help="Percentage of patients readmitted")
        with col3:
            st.metric("Avg Length of Stay", f"{avg_los:.1f} days",
                     help="Average hospital stay duration")
        with col4:
            st.metric("High Risk Patients", f"{high_risk:,}",
                     delta=f"{high_risk/total_patients:.1%}",
                     delta_color="inverse",
                     help="Patients with risk score > 0.7")
        with col5:
            avg_age = df['age'].mean()
            st.metric("Average Age", f"{avg_age:.0f} years",
                     help="Mean patient age")
        
        st.divider()
        
        # Row 1: Readmission Overview
        st.markdown("### 🎯 Readmission Overview")
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie Chart: Overall Readmission Distribution
            st.markdown("#### Overall Readmission Distribution")
            readmission_counts = df['label'].value_counts()
            fig = px.pie(
                values=readmission_counts.values,
                names=['Readmitted', 'Not Readmitted'],
                color_discrete_sequence=[HOSPITAL_COLORS['danger'], HOSPITAL_COLORS['success']],
                hole=0.4
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )
            fig.update_layout(
                showlegend=True,
                height=400,
                annotations=[dict(text=f'{total_patients:,}<br>Patients', x=0.5, y=0.5, font_size=16, showarrow=False)]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gauge Chart: Readmission Rate
            st.markdown("#### Readmission Rate Gauge")
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=readmission_rate * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Readmission Rate (%)", 'font': {'size': 20}},
                delta={'reference': 50, 'increasing': {'color': HOSPITAL_COLORS['danger']}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': HOSPITAL_COLORS['primary']},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 30], 'color': HOSPITAL_COLORS['success']},
                        {'range': [30, 60], 'color': HOSPITAL_COLORS['warning']},
                        {'range': [60, 100], 'color': HOSPITAL_COLORS['danger']}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 70
                    }
                }
            ))
            fig.update_layout(height=400, font={'size': 14})
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Row 2: Diagnosis and Treatment Analysis
        st.markdown("### 🏥 Clinical Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            # Horizontal Bar: Readmission by Diagnosis (sorted)
            st.markdown("#### Readmission Rate by Primary Diagnosis")
            diag_rates = df.groupby('primary_diagnosis')['label'].agg(['mean', 'count']).reset_index()
            diag_rates.columns = ['Diagnosis', 'Rate', 'Count']
            diag_rates = diag_rates.sort_values('Rate', ascending=True)
            
            fig = px.bar(
                diag_rates,
                x='Rate',
                y='Diagnosis',
                orientation='h',
                color='Rate',
                color_continuous_scale=HOSPITAL_COLORS['gradient_risk'],
                hover_data={'Count': True, 'Rate': ':.1%'},
                labels={'Rate': 'Readmission Rate', 'Diagnosis': 'Primary Diagnosis'}
            )
            fig.update_layout(
                xaxis_tickformat='.0%',
                showlegend=False,
                height=500,
                xaxis_title="Readmission Rate",
                yaxis_title="Primary Diagnosis"
            )
            fig.update_traces(
                hovertemplate='<b>%{y}</b><br>Rate: %{x:.1%}<br>Patients: %{customdata[0]}<extra></extra>'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Stacked Bar: Treatment Type Distribution
            st.markdown("#### Treatment Type Distribution by Outcome")
            treatment_data = df.groupby(['treatment_type', 'label']).size().reset_index(name='count')
            treatment_data['label'] = treatment_data['label'].map({0: 'Not Readmitted', 1: 'Readmitted'})
            
            fig = px.bar(
                treatment_data,
                x='treatment_type',
                y='count',
                color='label',
                barmode='stack',
                color_discrete_map={'Not Readmitted': HOSPITAL_COLORS['success'], 'Readmitted': HOSPITAL_COLORS['danger']},
                labels={'count': 'Number of Patients', 'treatment_type': 'Treatment Type', 'label': 'Outcome'},
                hover_data={'count': ':,'}
            )
            fig.update_layout(
                height=500,
                xaxis_title="Treatment Type",
                yaxis_title="Number of Patients",
                legend_title="Outcome",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Row 3: Age and Length of Stay Analysis
        st.markdown("### 📈 Patient Demographics & Stay Duration")
        col1, col2 = st.columns(2)
        
        with col1:
            # Area Chart: Age Distribution by Readmission
            st.markdown("#### Age Distribution by Readmission Status")
            age_bins = pd.cut(df['age'], bins=range(0, 101, 10))
            age_data = df.groupby([age_bins, 'label']).size().reset_index(name='count')
            age_data['age_group'] = age_data['age'].astype(str)
            age_data['label'] = age_data['label'].map({0: 'Not Readmitted', 1: 'Readmitted'})
            
            fig = px.area(
                age_data,
                x='age_group',
                y='count',
                color='label',
                color_discrete_map={'Not Readmitted': HOSPITAL_COLORS['success'], 'Readmitted': HOSPITAL_COLORS['danger']},
                labels={'count': 'Number of Patients', 'age_group': 'Age Group', 'label': 'Status'}
            )
            fig.update_layout(
                height=400,
                xaxis_title="Age Group",
                yaxis_title="Number of Patients",
                legend_title="Status",
                hovermode='x unified'
            )
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Violin Plot: Length of Stay Distribution
            st.markdown("#### Length of Stay Distribution by Outcome")
            df_plot = df.copy()
            df_plot['Outcome'] = df_plot['label'].map({0: 'Not Readmitted', 1: 'Readmitted'})
            
            fig = px.violin(
                df_plot,
                x='Outcome',
                y='length_of_stay',
                color='Outcome',
                box=True,
                points='outliers',
                color_discrete_map={'Not Readmitted': HOSPITAL_COLORS['success'], 'Readmitted': HOSPITAL_COLORS['danger']},
                labels={'length_of_stay': 'Length of Stay (days)', 'Outcome': 'Readmission Status'}
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                yaxis_title="Length of Stay (days)",
                xaxis_title="Readmission Status"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Row 4: Geographic and Seasonal Analysis
        st.markdown("### 🌍 Geographic & Seasonal Patterns")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Donut Chart: Regional Distribution
            st.markdown("#### Readmission by Region")
            region_data = df.groupby('region')['label'].agg(['sum', 'count']).reset_index()
            region_data['rate'] = region_data['sum'] / region_data['count']
            
            fig = px.pie(
                region_data,
                values='count',
                names='region',
                color='region',
                color_discrete_sequence=HOSPITAL_COLORS['categorical'],
                hole=0.5
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Patients: %{value}<br>Percentage: %{percent}<extra></extra>'
            )
            fig.update_layout(height=350, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show rates below
            st.markdown("**Readmission Rates:**")
            for _, row in region_data.iterrows():
                st.write(f"• {row['region'].title()}: {row['rate']:.1%}")
        
        with col2:
            # Bar Chart: Seasonal Patterns
            st.markdown("#### Seasonal Readmission Patterns")
            season_data = df.groupby('season')['label'].agg(['mean', 'count']).reset_index()
            season_data.columns = ['Season', 'Rate', 'Count']
            season_order = ['winter', 'spring', 'summer', 'fall']
            season_data['Season'] = pd.Categorical(season_data['Season'], categories=season_order, ordered=True)
            season_data = season_data.sort_values('Season')
            
            fig = px.bar(
                season_data,
                x='Season',
                y='Rate',
                color='Season',
                color_discrete_map={
                    'winter': '#4A90E2',  # Blue
                    'spring': '#7ED321',  # Green
                    'summer': '#F5A623',  # Orange
                    'fall': '#D0021B'     # Red
                },
                hover_data={'Count': True, 'Rate': ':.1%'},
                labels={'Rate': 'Readmission Rate', 'Season': 'Season'}
            )
            fig.update_layout(
                height=350,
                yaxis_tickformat='.0%',
                showlegend=False,
                yaxis_title="Readmission Rate",
                xaxis_title="Season"
            )
            fig.update_traces(
                hovertemplate='<b>%{x}</b><br>Rate: %{y:.1%}<br>Patients: %{customdata[0]}<extra></extra>'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Funnel Chart: Insurance Type
            st.markdown("#### Insurance Type Distribution")
            insurance_data = df.groupby('insurance_type')['label'].agg(['sum', 'count']).reset_index()
            insurance_data.columns = ['Insurance', 'Readmitted', 'Total']
            insurance_data = insurance_data.sort_values('Total', ascending=False)
            
            fig = go.Figure(go.Funnel(
                y=insurance_data['Insurance'],
                x=insurance_data['Total'],
                textposition="inside",
                textinfo="value+percent initial",
                marker={
                    "color": HOSPITAL_COLORS['gradient_blue'],
                    "line": {"width": 2, "color": "white"}
                },
                connector={"line": {"color": HOSPITAL_COLORS['primary'], "width": 2}}
            ))
            fig.update_layout(
                height=350,
                showlegend=False,
                yaxis_title="Insurance Type",
                xaxis_title="Number of Patients"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Row 5: Risk Factors Analysis
        st.markdown("### ⚠️ Risk Factors Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            # Scatter Plot: Comorbidities vs Medications
            st.markdown("#### Comorbidities vs Medications (Risk Analysis)")
            df_sample = df.sample(min(1000, len(df)))  # Sample for performance
            
            # Handle missing values in readmission_risk_score
            df_sample = df_sample.dropna(subset=['readmission_risk_score', 'comorbidities_count', 'medications_count'])
            
            if len(df_sample) > 0:
                df_sample['Outcome'] = df_sample['label'].map({0: 'Not Readmitted', 1: 'Readmitted'})
                
                # Ensure risk score is positive and scale it for better visualization
                df_sample['risk_size'] = df_sample['readmission_risk_score'] * 50 + 5  # Scale for visibility
                
                fig = px.scatter(
                    df_sample,
                    x='comorbidities_count',
                    y='medications_count',
                    color='Outcome',
                    size='risk_size',
                    color_discrete_map={'Not Readmitted': HOSPITAL_COLORS['success'], 'Readmitted': HOSPITAL_COLORS['danger']},
                    labels={
                        'comorbidities_count': 'Number of Comorbidities',
                        'medications_count': 'Number of Medications',
                        'readmission_risk_score': 'Risk Score'
                    },
                    hover_data=['age', 'length_of_stay', 'readmission_risk_score']
                )
                fig.update_layout(
                    height=450,
                    showlegend=True,
                    hovermode='closest'
                )
                fig.update_traces(
                    marker=dict(
                        line=dict(width=0.5, color='white'),
                        opacity=0.7
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Not enough valid data for scatter plot visualization.")
        
        with col2:
            # Heatmap: Correlation Matrix
            st.markdown("#### Risk Factor Correlation Heatmap")
            numeric_cols = ['age', 'comorbidities_count', 'length_of_stay', 
                          'medications_count', 'followup_visits_last_year', 
                          'prev_readmissions', 'readmission_risk_score', 'label']
            
            # Filter to only include columns that exist in the dataframe
            numeric_cols = [col for col in numeric_cols if col in df.columns]
            
            if len(numeric_cols) > 1:
                # Drop rows with NaN values for correlation calculation
                df_corr = df[numeric_cols].dropna()
                
                if len(df_corr) > 0:
                    corr_matrix = df_corr.corr()
                    
                    fig = px.imshow(
                        corr_matrix,
                        labels=dict(color="Correlation"),
                        x=corr_matrix.columns,
                        y=corr_matrix.columns,
                        color_continuous_scale='RdBu_r',
                        zmin=-1,
                        zmax=1,
                        aspect="auto"
                    )
                    fig.update_layout(
                        height=450,
                        xaxis_title="",
                        yaxis_title=""
                    )
                    fig.update_xaxes(tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ Not enough valid data for correlation heatmap.")
            else:
                st.warning("⚠️ Not enough numeric columns for correlation analysis.")
        
        st.divider()
        
        # Row 6: Previous Readmissions Impact
        st.markdown("### 🔄 Impact of Previous Readmissions")
        
        # Line Chart with Area: Previous Readmissions Trend
        prev_readm_data = df.groupby('prev_readmissions')['label'].agg(['mean', 'count']).reset_index()
        prev_readm_data.columns = ['Previous Readmissions', 'Rate', 'Count']
        
        fig = go.Figure()
        
        # Add area trace
        fig.add_trace(go.Scatter(
            x=prev_readm_data['Previous Readmissions'],
            y=prev_readm_data['Rate'],
            fill='tozeroy',
            name='Readmission Rate',
            line=dict(color=HOSPITAL_COLORS['danger'], width=3),
            fillcolor=f"rgba(220, 20, 60, 0.3)",
            hovertemplate='<b>Previous Readmissions: %{x}</b><br>Rate: %{y:.1%}<extra></extra>'
        ))
        
        # Add count as bar on secondary y-axis
        fig.add_trace(go.Bar(
            x=prev_readm_data['Previous Readmissions'],
            y=prev_readm_data['Count'],
            name='Patient Count',
            marker_color=HOSPITAL_COLORS['info'],
            opacity=0.6,
            yaxis='y2',
            hovertemplate='<b>Previous Readmissions: %{x}</b><br>Patients: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Readmission Rate vs Previous Readmissions",
            xaxis_title="Number of Previous Readmissions",
            yaxis_title="Readmission Rate",
            yaxis=dict(tickformat='.0%', side='left'),
            yaxis2=dict(title="Number of Patients", overlaying='y', side='right'),
            height=400,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary Statistics
        st.markdown("### 📋 Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("**Age Statistics**")
            st.write(f"• Min: {df['age'].min()} years")
            st.write(f"• Max: {df['age'].max()} years")
            st.write(f"• Median: {df['age'].median():.0f} years")
            st.write(f"• Std Dev: {df['age'].std():.1f}")
        
        with col2:
            st.markdown("**Length of Stay**")
            st.write(f"• Min: {df['length_of_stay'].min()} days")
            st.write(f"• Max: {df['length_of_stay'].max()} days")
            st.write(f"• Median: {df['length_of_stay'].median():.0f} days")
            st.write(f"• Std Dev: {df['length_of_stay'].std():.1f}")
        
        with col3:
            st.markdown("**Comorbidities**")
            st.write(f"• Min: {df['comorbidities_count'].min()}")
            st.write(f"• Max: {df['comorbidities_count'].max()}")
            st.write(f"• Median: {df['comorbidities_count'].median():.0f}")
            st.write(f"• Avg: {df['comorbidities_count'].mean():.1f}")
        
        with col4:
            st.markdown("**Medications**")
            st.write(f"• Min: {df['medications_count'].min()}")
            st.write(f"• Max: {df['medications_count'].max()}")
            st.write(f"• Median: {df['medications_count'].median():.0f}")
            st.write(f"• Avg: {df['medications_count'].mean():.1f}")
        
    except Exception as e:
        st.error(f"Error loading analytics data: {e}")
        import traceback
        st.code(traceback.format_exc())

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
