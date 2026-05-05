import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from streamlit_option_menu import option_menu

# Configure page
st.set_page_config(
    page_title="Smart Hospital Readmission Risk Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium design
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
    /* Interactive Button Styling */
    .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background-color: #008080 !important; /* Solid Teal */
        background: none;
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
        background-color: #006666 !important; /* Darker Teal */
        color: white !important;
    }
    .stButton > button:active, div[data-testid="stFormSubmitButton"] > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 4px rgba(0, 128, 128, 0.2) !important;
    }
    
    /* Sidebar Background Color */
    [data-testid="stSidebar"] {
        background-color: #f1f1f1 !important; /* Web-recommended black */
    }
    [data-testid="stSidebar"] * {
        color: #000000 !important; /* White text for sidebar */
    }
    /* Sidebar text */
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    /* Navigation item */
    [data-testid="stSidebar"] .nav-link {
        border-radius: 10px;
        margin: 6px 8px;
        transition: all 0.25s ease;
        background-color: transparent;
    }

    /* Hover effect */
    [data-testid="stSidebar"] .nav-link:hover {
        background-color: #008080 !important;
        color: white !important;
        transform: translateX(3px);
    }

    /* Selected menu item */
    [data-testid="stSidebar"] .nav-link-selected {
        background: #008080 !important;
        color: white !important;
        font-weight: 600;
        box-shadow: 0 4px 10px rgba(20, 184, 166, 0.3);
    }

    /* Sidebar title */
    [data-testid="stSidebar"] h2 {
        color: #000000 !important;
        font-weight: 1000;
    }

    /* Sidebar icons */
    [data-testid="stSidebar"] .icon {
        color: #38bdf8 !important;
    }
    /* Selectbox Focus and Selection Styling */
    .stSelectbox div[data-baseweb="select"] > div:focus-within {
        border-color: #008080 !important;
        box-shadow: 0 0 0 1px #008080 !important;
    }
    /* Dropdown list items */
    li[aria-selected="true"] {
        background-color: #008080 !important;
        color: white !important;
    }
    li[role="option"]:hover {
        background-color: #008080 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# API URL
API_URL = "http://localhost:8000"

def get_analytics():
    try:
        response = requests.get(f"{API_URL}/analytics")
        if response.status_code == 200:
            return response.json()
    except:
        return None
        
def get_prediction(data):
    try:
        response = requests.post(f"{API_URL}/predict", json=data)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return None

# Sidebar navigation
with st.sidebar:
    st.markdown('<div style="text-align: left; margin-bottom: 0px;"><h2>🏥 Hospital Readmission</h2></div>', unsafe_allow_html=True)
    page = option_menu(
        menu_title=None,
        options=["Overview", "Patient Risk Analysis", "Analytics Dashboard", "Model Performance"],
        icons=["house", "activity", "graph-up", "speedometer2"],
        menu_icon="cast",
        default_index=0,
        styles={
        "container": {
            "padding": "0!important",
            "background-color": "transparent"
        },

        "icon": {
            "color": "#008080",
            "font-size": "18px"
        },

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
        st.markdown("""
        ### Welcome to the Smart Hospital Readmission Risk Analytics Platform
        
        This AI-powered platform helps healthcare professionals:
        - Predict patient readmission risks
        - Identify major risk factors using Explainable AI (SHAP)
        - Monitor hospital performance indicators
        - Make data-driven decisions to improve patient outcomes
        
        Please navigate using the sidebar to explore different functionalities.
        """)
    else:
        st.error("Could not connect to the backend API. Please ensure it is running.")

elif page == "Patient Risk Analysis":
    st.title("Patient Risk Prediction")
    st.markdown("Enter patient details to predict their risk of hospital readmission within 30 days.")
    
    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Demographics & Vitals")
            age = st.number_input("Age", min_value=18, max_value=120, value=65, help="Patient's age in years.")
            gender = st.selectbox("Gender", ["Male", "Female"], help="Biological gender of the patient.")
            weight = st.number_input("Weight (kg)", value=75.0, help="Weight in kilograms.")
            height = st.number_input("Height (cm)", value=170.0, help="Height in centimeters.")
            bmi = weight / ((height/100)**2)
            st.info(f"Calculated BMI: {bmi:.1f}")
            heart_rate = st.number_input("Heart Rate (bpm)", value=75, help="Average heart rate.")
            sys_bp = st.number_input("Systolic BP", value=120, help="Systolic blood pressure (top number).")
            dia_bp = st.number_input("Diastolic BP", value=80, help="Diastolic blood pressure (bottom number).")
            blood_pressure = f"{int(sys_bp)}/{int(dia_bp)}"
            
        with col2:
            st.subheader("Medical History")
            diabetes = st.selectbox("Diabetes", ["Yes", "No"], help="Does the patient have a history of diabetes?")
            hypertension = st.selectbox("Hypertension", ["Yes", "No"], help="Does the patient have hypertension?")
            heart_disease = st.selectbox("Heart Disease", ["Yes", "No"], help="History of heart disease?")
            diagnosis = st.selectbox("Diagnosis", ['Pneumonia', 'Heart Failure', 'COPD', 'Diabetes Complication', 'Sepsis', 'Kidney Failure', 'Stroke', 'Other'], help="Primary diagnosis on admission.")
            lab_result = st.selectbox("Lab Result", ["Normal", "Abnormal"], help="Overall assessment of lab results.")
            cholesterol = st.selectbox("Cholesterol Level", ["Normal", "Borderline", "High"], help="Cholesterol category.")
            glucose = st.number_input("Glucose Level", value=100, help="Fasting blood glucose level.")
            
        with col3:
            st.subheader("Lifestyle & Admission")
            smoking = st.selectbox("Smoking Status", ["Never", "Former", "Current"], help="Patient's smoking habits.")
            alcohol = st.selectbox("Alcohol Use", ["None", "Occasional", "Frequent"], help="Patient's alcohol consumption.")
            prev_admissions = st.number_input("Previous Admissions", min_value=0, value=1, help="Number of times admitted in the past year.")
            los = st.number_input("Length of Stay (days)", min_value=1, value=4, help="Duration of current hospital stay in days.")
            med_adherence = st.selectbox("Medication Adherence", ["Low", "Medium", "High"], help="How well the patient adheres to prescribed medication.")
            insurance = st.selectbox("Insurance Type", ['Private', 'Medicare', 'Medicaid', 'Uninsured'], help="Primary health insurance.")
            discharge = st.selectbox("Discharge Type", ['Home', 'Skilled Nursing', 'Rehabilitation', 'Against Medical Advice'], help="Planned discharge destination.")
            follow_up = st.selectbox("Follow Up Required", ["Yes", "No"], help="Is a follow-up appointment scheduled?")
            
        submit = st.form_submit_button("Predict Risk", use_container_width=True)
        
    if submit:
        data = {
            "Age": age, "Gender": gender, "Weight_kg": weight, "Height_cm": height, "BMI": bmi,
            "Blood_Pressure": blood_pressure, "Heart_Rate": heart_rate, "Diabetes": diabetes,
            "Hypertension": hypertension, "Heart_Disease": heart_disease, "Smoking_Status": smoking,
            "Alcohol_Use": alcohol, "Previous_Admissions": prev_admissions, "Length_of_Stay": los,
            "Diagnosis": diagnosis, "Lab_Result": lab_result, "Cholesterol_Level": cholesterol,
            "Glucose_Level": glucose, "Medication_Adherence": med_adherence, "Insurance_Type": insurance,
            "Discharge_Type": discharge, "Follow_Up_Required": follow_up
        }
        
        with st.spinner("Analyzing patient data..."):
            result = get_prediction(data)
            
        if result:
            st.divider()
            st.subheader("Prediction Results")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                risk_cat = result["risk_category"]
                color = "green" if risk_cat == "Low Risk" else "orange" if risk_cat == "Medium Risk" else "red"
                
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; background-color: {color}; color: white; border-radius: 10px;">
                    <h2>{risk_cat}</h2>
                    <h1>{result['probability']:.1%}</h1>
                    <p>Probability of Readmission</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                st.markdown("#### Key Risk Factors (Explainable AI)")
                factors = result["feature_importance"]
                
                # Create horizontal bar chart for SHAP values
                df_factors = pd.DataFrame({
                    "Feature": list(factors.keys()),
                    "Impact": list(factors.values())
                })
                df_factors["Impact_Pct"] = df_factors["Impact"] * 100
                df_factors["Color"] = df_factors["Impact"].apply(lambda x: "Increases Risk" if x > 0 else "Decreases Risk")
                
                fig = px.bar(df_factors, x="Impact_Pct", y="Feature", color="Color",
                             color_discrete_map={"Increases Risk": "#ef553b", "Decreases Risk": "#00cc96"},
                             orientation='h', title="Top Contributing Factors",
                             text=df_factors["Impact_Pct"].apply(lambda x: f"{x:+.1f}%"))
                fig.update_layout(yaxis={'categoryorder':'total ascending'}, xaxis_title="Impact on Readmission Risk (%)")
                st.plotly_chart(fig, use_container_width=True)

elif page == "Analytics Dashboard":
    st.title("Analytics Dashboard")
    try:
        df = pd.read_csv("data/synthetic_hospital_data.csv")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Readmission by Diagnosis")
            diag_rates = df.groupby('Diagnosis')['Readmitted'].apply(lambda x: (x=='Yes').mean()).sort_values()
            fig = px.bar(x=diag_rates.values, y=diag_rates.index, orientation='h', color=diag_rates.index, labels={'x': 'Readmission Rate', 'y': 'Diagnosis'}, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(xaxis_tickformat='.0%', showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Age Distribution")
            fig = px.histogram(df, x="Age", color="Readmitted", barmode="overlay", nbins=30, color_discrete_sequence=["#00cc96", "#ef553b"])
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("Impact of Previous Admissions")
            prev_rates = df.groupby('Previous_Admissions')['Readmitted'].apply(lambda x: (x=='Yes').mean()).reset_index()
            fig = px.bar(prev_rates, x='Previous_Admissions', y='Readmitted', color='Previous_Admissions', labels={'Readmitted': 'Readmission Rate'}, color_continuous_scale='Viridis')
            fig.update_layout(yaxis_tickformat='.0%')
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Length of Stay vs Risk")
            fig = px.box(df, x="Readmitted", y="Length_of_Stay", color="Readmitted", color_discrete_sequence=["#00cc96", "#ef553b"])
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
        col5.metric("ROC AUC", f"{metrics['roc_auc']:.2f}")
        
        st.divider()
        st.subheader("Global Feature Importance")
        st.markdown("The following chart shows the most important features learned by the Random Forest model across all patients.")
        
        # Load the model and get feature importances
        import joblib
        model = joblib.load("models/random_forest_model.joblib")
        with open("models/feature_names.json", "r") as f:
            feature_names = json.load(f)
            
        importances = model.feature_importances_
        indices = np.argsort(importances)[-15:]
        
        import plotly.graph_objects as go
        
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
