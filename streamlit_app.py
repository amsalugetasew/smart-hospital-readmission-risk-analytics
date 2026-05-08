"""
Ultra-minimal Streamlit app for Streamlit Cloud deployment
This file is completely self-contained with no external dependencies
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="Hospital Readmission Analytics",
    page_icon="🏥",
    layout="wide"
)

# Title
st.title("🏥 Hospital Readmission Risk Analytics")

# Navigation
page = st.sidebar.selectbox(
    "Choose a page:",
    ["🏠 Overview", "📊 Data Analysis", "📤 Upload Data", "📈 Dashboard"]
)

# Generate sample data
@st.cache_data
def create_sample_data():
    """Create sample hospital data"""
    np.random.seed(42)
    n = 1000
    
    data = {
        'patient_id': range(1, n+1),
        'age': np.random.randint(18, 90, n),
        'gender': np.random.choice(['Male', 'Female'], n),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n),
        'diagnosis': np.random.choice(['Diabetes', 'Heart Disease', 'Pneumonia', 'COPD'], n),
        'length_of_stay': np.random.randint(1, 15, n),
        'medications': np.random.randint(1, 10, n),
        'risk_score': np.random.uniform(0, 1, n),
        'readmitted': np.random.choice([0, 1], n, p=[0.75, 0.25])
    }
    
    return pd.DataFrame(data)

# Load data
df = create_sample_data()

if page == "🏠 Overview":
    st.markdown("""
    ## Welcome to Hospital Readmission Analytics
    
    This platform helps healthcare professionals analyze patient readmission patterns and risks.
    
    ### Key Features:
    - 📊 Interactive data analysis
    - 📤 Data upload capabilities  
    - 📈 Real-time dashboards
    - 🎯 Risk prediction insights
    """)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Patients", f"{len(df):,}")
    
    with col2:
        readmission_rate = df['readmitted'].mean()
        st.metric("Readmission Rate", f"{readmission_rate:.1%}")
    
    with col3:
        avg_stay = df['length_of_stay'].mean()
        st.metric("Avg Stay", f"{avg_stay:.1f} days")
    
    with col4:
        high_risk = (df['risk_score'] > 0.7).sum()
        st.metric("High Risk Patients", high_risk)
    
    # Sample data preview
    st.subheader("📋 Sample Data")
    st.dataframe(df.head(10), use_container_width=True)

elif page == "📊 Data Analysis":
    st.header("Data Analysis")
    
    # Basic statistics
    st.subheader("Dataset Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Dataset Shape:**", df.shape)
        st.write("**Missing Values:**", df.isnull().sum().sum())
        st.write("**Readmission Rate:**", f"{df['readmitted'].mean():.1%}")
    
    with col2:
        st.write("**Age Range:**", f"{df['age'].min()} - {df['age'].max()}")
        st.write("**Avg Length of Stay:**", f"{df['length_of_stay'].mean():.1f} days")
        st.write("**Avg Risk Score:**", f"{df['risk_score'].mean():.2f}")
    
    # Visualizations
    st.subheader("📈 Visualizations")
    
    # Age distribution
    fig1 = px.histogram(df, x='age', title='Age Distribution', nbins=20)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Readmission by region
    region_stats = df.groupby('region')['readmitted'].agg(['count', 'mean']).reset_index()
    region_stats.columns = ['Region', 'Total', 'Readmission_Rate']
    
    fig2 = px.bar(region_stats, x='Region', y='Readmission_Rate', 
                  title='Readmission Rate by Region')
    st.plotly_chart(fig2, use_container_width=True)

elif page == "📤 Upload Data":
    st.header("Upload Your Data")
    
    st.markdown("""
    Upload a CSV file with patient data to analyze readmission patterns.
    
    **Expected columns:**
    - patient_id, age, gender, region, diagnosis
    - length_of_stay, medications, risk_score, readmitted
    """)
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            # Read uploaded data
            user_df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ File uploaded successfully!")
            st.write(f"**Shape:** {user_df.shape}")
            
            # Show preview
            st.subheader("Data Preview")
            st.dataframe(user_df.head(), use_container_width=True)
            
            # Basic analysis
            if 'readmitted' in user_df.columns:
                st.subheader("Quick Analysis")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total Records", len(user_df))
                    if 'age' in user_df.columns:
                        st.metric("Avg Age", f"{user_df['age'].mean():.1f}")
                
                with col2:
                    readmit_rate = user_df['readmitted'].mean()
                    st.metric("Readmission Rate", f"{readmit_rate:.1%}")
                    if 'length_of_stay' in user_df.columns:
                        st.metric("Avg Stay", f"{user_df['length_of_stay'].mean():.1f}")
                
                # Simple visualization
                if 'age' in user_df.columns:
                    fig = px.histogram(user_df, x='age', title='Age Distribution (Your Data)')
                    st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.info("Please make sure your file is a valid CSV format.")
    
    else:
        st.info("👆 Upload a CSV file to get started")

elif page == "📈 Dashboard":
    st.header("Analytics Dashboard")
    
    # Key metrics row
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Admissions", f"{len(df):,}")
    with col2:
        st.metric("Readmission Rate", f"{df['readmitted'].mean():.1%}")
    with col3:
        st.metric("Avg Risk Score", f"{df['risk_score'].mean():.2f}")
    with col4:
        high_risk_pct = (df['risk_score'] > 0.7).mean()
        st.metric("High Risk %", f"{high_risk_pct:.1%}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Risk Score Distribution")
        fig1 = px.histogram(df, x='risk_score', nbins=20, 
                           title='Patient Risk Score Distribution')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("Readmission by Gender")
        gender_stats = df.groupby('gender')['readmitted'].mean().reset_index()
        fig2 = px.bar(gender_stats, x='gender', y='readmitted',
                     title='Readmission Rate by Gender')
        st.plotly_chart(fig2, use_container_width=True)
    
    # Scatter plot
    st.subheader("Risk vs Length of Stay")
    fig3 = px.scatter(df, x='length_of_stay', y='risk_score', 
                     color='readmitted', 
                     title='Risk Score vs Length of Stay',
                     labels={'readmitted': 'Readmitted'})
    st.plotly_chart(fig3, use_container_width=True)
    
    # Data table
    st.subheader("High Risk Patients")
    high_risk_patients = df[df['risk_score'] > 0.8].sort_values('risk_score', ascending=False)
    st.dataframe(high_risk_patients[['patient_id', 'age', 'gender', 'diagnosis', 'risk_score', 'readmitted']].head(10),
                use_container_width=True)

# Footer
st.markdown("---")
st.markdown("🏥 **Hospital Readmission Risk Analytics** | Built with Streamlit")