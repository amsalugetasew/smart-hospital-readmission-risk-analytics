"""
Minimal Streamlit app for deployment testing
Only uses basic packages: streamlit, pandas, numpy, plotly, requests
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import json

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
</style>
""", unsafe_allow_html=True)

# Navigation
page = st.selectbox(
    "Navigate to:",
    ["Overview", "EDA", "Data Upload", "Analytics Dashboard"]
)

# Sample data for demonstration
@st.cache_data
def load_sample_data():
    """Load sample hospital readmission data"""
    np.random.seed(42)
    n_samples = 1000
    
    data = {
        'age': np.random.randint(18, 90, n_samples),
        'gender': np.random.choice(['Male', 'Female'], n_samples),
        'region': np.random.choice(['North', 'South', 'East', 'West', 'Central'], n_samples),
        'length_of_stay': np.random.randint(1, 15, n_samples),
        'comorbidities_count': np.random.randint(0, 5, n_samples),
        'medications_count': np.random.randint(1, 20, n_samples),
        'readmission_risk_score': np.random.uniform(0, 1, n_samples),
        'label': np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    }
    
    return pd.DataFrame(data)

# Main content
if page == "Overview":
    st.title("🏥 Smart Hospital Readmission Risk Analytics")
    
    st.markdown("""
    ### Welcome to the Hospital Readmission Analytics Platform
    
    This AI-powered platform helps healthcare professionals:
    - 🎯 Predict patient readmission risks using machine learning
    - 📊 Monitor hospital performance indicators
    - 💡 Make data-driven decisions to improve patient outcomes
    
    **Note:** This is a minimal deployment version with basic functionality.
    """)
    
    # Load sample data
    df = load_sample_data()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Patients", f"{len(df):,}")
    with col2:
        readmission_rate = df['label'].mean()
        st.metric("Readmission Rate", f"{readmission_rate:.1%}")
    with col3:
        avg_stay = df['length_of_stay'].mean()
        st.metric("Avg Length of Stay", f"{avg_stay:.1f} days")
    with col4:
        high_risk = (df['readmission_risk_score'] > 0.7).mean()
        st.metric("High Risk Patients", f"{high_risk:.1%}")

elif page == "EDA":
    st.title("📊 Exploratory Data Analysis")
    
    df = load_sample_data()
    
    st.write("### Dataset Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows", len(df))
    col2.metric("Total Features", len(df.columns))
    col3.metric("Readmission Rate", f"{df['label'].mean():.1%}")
    
    # Show data
    st.write("### Sample Data")
    st.dataframe(df.head(10))
    
    # Visualizations
    st.write("### Age Distribution")
    fig = px.histogram(df, x='age', nbins=20, title="Patient Age Distribution")
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("### Readmission by Region")
    region_stats = df.groupby('region')['label'].agg(['count', 'mean']).reset_index()
    region_stats.columns = ['Region', 'Total Patients', 'Readmission Rate']
    
    fig = px.bar(region_stats, x='Region', y='Readmission Rate', 
                 title="Readmission Rate by Region")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Data Upload":
    st.title("📤 Data Upload")
    
    st.markdown("""
    Upload your own CSV file to analyze hospital readmission data.
    
    **Required columns:**
    - age, gender, region, length_of_stay, comorbidities_count
    - medications_count, readmission_risk_score, label
    """)
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df_uploaded = pd.read_csv(uploaded_file)
            st.success(f"✅ File loaded successfully! ({len(df_uploaded)} rows, {len(df_uploaded.columns)} columns)")
            
            # Show preview
            st.write("### Data Preview")
            st.dataframe(df_uploaded.head(10))
            
            # Basic statistics
            if 'label' in df_uploaded.columns:
                st.write("### Basic Statistics")
                col1, col2 = st.columns(2)
                col1.metric("Total Patients", len(df_uploaded))
                col2.metric("Readmission Rate", f"{df_uploaded['label'].mean():.1%}")
                
        except Exception as e:
            st.error(f"Error loading file: {e}")
    else:
        st.info("Please upload a CSV file to get started.")

elif page == "Analytics Dashboard":
    st.title("📈 Analytics Dashboard")
    
    df = load_sample_data()
    
    # Key Performance Indicators
    st.write("### Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Admissions", f"{len(df):,}")
    col2.metric("Readmission Rate", f"{df['label'].mean():.1%}")
    col3.metric("Avg Risk Score", f"{df['readmission_risk_score'].mean():.2f}")
    col4.metric("High Risk %", f"{(df['readmission_risk_score'] > 0.7).mean():.1%}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### Risk Score Distribution")
        fig = px.histogram(df, x='readmission_risk_score', nbins=20)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("#### Readmission by Gender")
        gender_stats = df.groupby('gender')['label'].mean().reset_index()
        fig = px.bar(gender_stats, x='gender', y='label', 
                     title="Readmission Rate by Gender")
        st.plotly_chart(fig, use_container_width=True)
    
    # Risk vs Length of Stay
    st.write("#### Risk Score vs Length of Stay")
    fig = px.scatter(df, x='length_of_stay', y='readmission_risk_score', 
                     color='label', title="Risk Score vs Length of Stay")
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("🏥 **Smart Hospital Readmission Risk Analytics** - Minimal Deployment Version")