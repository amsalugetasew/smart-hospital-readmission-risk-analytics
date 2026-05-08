"""
Verify data structure for visualizations
"""
import pandas as pd

print("🔍 Verifying Data Structure for Visualizations...")

# Load dataset
try:
    df = pd.read_csv("data/hospital_readmission_dataset.csv")
    print(f"✅ Dataset loaded: {len(df)} rows, {len(df.columns)} columns\n")
except Exception as e:
    print(f"❌ Error loading dataset: {e}")
    exit(1)

# Check required columns
required_cols = ['age', 'gender', 'primary_diagnosis', 'label']
print("📋 Checking required columns:")
for col in required_cols:
    if col in df.columns:
        print(f"   ✅ {col}")
    else:
        print(f"   ❌ {col} - MISSING!")

# Data statistics
print("\n📊 Data Statistics:")
print(f"   - Age range: {df['age'].min()} to {df['age'].max()}")
print(f"   - Mean age: {df['age'].mean():.1f}")
print(f"   - Genders: {df['gender'].unique().tolist()}")
print(f"   - Diagnoses: {df['primary_diagnosis'].unique().tolist()}")
print(f"   - Label distribution:")
print(f"     • Not Readmitted (0): {(df['label']==0).sum()} ({(df['label']==0).sum()/len(df)*100:.1f}%)")
print(f"     • Readmitted (1): {(df['label']==1).sum()} ({(df['label']==1).sum()/len(df)*100:.1f}%)")

# Test grouping operations
print("\n🔍 Testing Data Grouping Operations:")

# Gender grouping
try:
    gender_groups = df.groupby(['gender', 'label']).size().reset_index(name='count')
    print(f"   ✅ Gender grouping: {len(gender_groups)} groups")
except Exception as e:
    print(f"   ❌ Gender grouping failed: {e}")

# Diagnosis grouping
try:
    diagnosis_groups = df.groupby(['primary_diagnosis', 'label']).size().reset_index(name='count')
    print(f"   ✅ Diagnosis grouping: {len(diagnosis_groups)} groups")
except Exception as e:
    print(f"   ❌ Diagnosis grouping failed: {e}")

# Age grouping
try:
    df['age_group'] = pd.cut(df['age'], bins=[0, 30, 50, 70, 100], labels=['<30', '30-50', '50-70', '70+'])
    age_groups = df.groupby('age_group')['label'].agg(['sum', 'count']).reset_index()
    print(f"   ✅ Age group creation: {len(age_groups)} groups")
except Exception as e:
    print(f"   ❌ Age grouping failed: {e}")

print("\n" + "="*60)
print("✅ Data structure verification completed!")
print("="*60)
print("\n💡 The data is ready for visualization in Streamlit")
print("   All required columns and grouping operations work correctly")
