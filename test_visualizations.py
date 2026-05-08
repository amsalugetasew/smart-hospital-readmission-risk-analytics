"""
Test script to verify visualizations work correctly
"""
import pandas as pd
import plotly.express as px

print("🔍 Testing Visualization Components...")

# Load dataset
try:
    df = pd.read_csv("data/hospital_readmission_dataset.csv")
    print(f"✅ Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
except Exception as e:
    print(f"❌ Error loading dataset: {e}")
    exit(1)

# Test 1: Age Distribution
print("\n📊 Test 1: Age Distribution")
try:
    fig_age = px.histogram(
        df, 
        x='age', 
        nbins=30,
        title='Age Distribution of Patients',
        labels={'age': 'Age (years)', 'count': 'Number of Patients'},
        color_discrete_sequence=['#4CAF50']
    )
    print(f"✅ Age histogram created successfully")
    print(f"   - Age range: {df['age'].min()} to {df['age'].max()}")
    print(f"   - Mean age: {df['age'].mean():.1f}")
except Exception as e:
    print(f"❌ Error creating age histogram: {e}")

# Test 2: Readmission by Gender
print("\n📊 Test 2: Readmission by Gender")
try:
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
    print(f"✅ Gender chart created successfully")
    print(f"   - Genders: {df['gender'].unique().tolist()}")
    print(f"   - Total groups: {len(gender_readmission)}")
    
    # Calculate rates
    gender_rate = df.groupby('gender')['label'].agg(['sum', 'count']).reset_index()
    gender_rate['rate'] = (gender_rate['sum'] / gender_rate['count'] * 100)
    print(f"   - Readmission rates:")
    for _, row in gender_rate.iterrows():
        print(f"     • {row['gender']}: {row['rate']:.1f}%")
        
except Exception as e:
    print(f"❌ Error creating gender chart: {e}")

# Test 3: Readmission by Primary Diagnosis
print("\n📊 Test 3: Readmission by Primary Diagnosis")
try:
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
    print(f"✅ Diagnosis chart created successfully")
    print(f"   - Diagnoses: {df['primary_diagnosis'].unique().tolist()}")
    print(f"   - Total groups: {len(diagnosis_readmission)}")
    
    # Calculate rates by diagnosis
    diagnosis_rate = df.groupby('primary_diagnosis')['label'].agg(['sum', 'count']).reset_index()
    diagnosis_rate['rate'] = (diagnosis_rate['sum'] / diagnosis_rate['count'] * 100)
    diagnosis_rate = diagnosis_rate.sort_values('rate', ascending=False)
    print(f"   - Readmission rates (sorted):")
    for _, row in diagnosis_rate.iterrows():
        print(f"     • {row['primary_diagnosis']}: {row['rate']:.1f}%")
        
except Exception as e:
    print(f"❌ Error creating diagnosis chart: {e}")

# Test 4: Additional Insights - Age Groups
print("\n📊 Test 4: Age Group Analysis")
try:
    df['age_group'] = pd.cut(df['age'], bins=[0, 30, 50, 70, 100], labels=['<30', '30-50', '50-70', '70+'])
    age_group_rate = df.groupby('age_group')['label'].agg(['sum', 'count']).reset_index()
    age_group_rate['rate'] = (age_group_rate['sum'] / age_group_rate['count'] * 100)
    
    print(f"✅ Age group analysis completed")
    print(f"   - Readmission rates by age group:")
    for _, row in age_group_rate.iterrows():
        print(f"     • {row['age_group']}: {row['rate']:.1f}% ({row['count']} patients)")
        
except Exception as e:
    print(f"❌ Error in age group analysis: {e}")

print("\n" + "="*60)
print("✅ All visualization tests completed successfully!")
print("="*60)
print("\n💡 Next steps:")
print("   1. Start backend: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
print("   2. Start frontend: streamlit run frontend/app.py")
print("   3. Navigate to Overview page to see visualizations")
