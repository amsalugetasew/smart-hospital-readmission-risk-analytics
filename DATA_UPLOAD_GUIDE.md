# 📤 Data Upload Guide

## 🎯 Overview

The Smart Hospital Readmission Risk Analytics platform now supports custom dataset uploads! You can upload your own CSV or Excel files to train models on your specific hospital data.

---

## 📋 Required Columns

Your dataset must include these **14 required columns**:

### Categorical Features (7)
| Column | Description | Valid Values |
|--------|-------------|--------------|
| `season` | Season of admission | Spring, Summer, Fall, Winter |
| `gender` | Patient gender | Male, Female (also accepts M, F, Man, Woman) |
| `region` | Geographic region | North, South, East, West, Central, Northeast, Northwest, Southeast, Southwest, Midwest |
| `primary_diagnosis` | Primary diagnosis | Diabetes, Hypertension, Heart Disease, Pneumonia, COPD, etc. (flexible) |
| `treatment_type` | Type of treatment | Medical, Surgical, Interventional, Emergency, Outpatient, Inpatient |
| `insurance_type` | Insurance type | Private, Medicare, Medicaid, Self-Pay, Commercial, Government, Uninsured |
| `discharge_disposition` | Discharge destination | Home, Home Health, Skilled Nursing, Rehab, Other, Nursing Home, Hospice, Transfer |

### Numerical Features (7)
| Column | Description | Valid Range |
|--------|-------------|-------------|
| `age` | Patient age in years | 0-150 |
| `comorbidities_count` | Number of comorbid conditions | 0+ |
| `length_of_stay` | Hospital stay duration in days | 1+ |
| `medications_count` | Number of medications | 0+ |
| `followup_visits_last_year` | Follow-up visits in past year | 0+ |
| `prev_readmissions` | Previous readmissions count | 0+ |
| `readmission_risk_score` | Pre-calculated risk score | 0.0-1.0 |

### Optional Columns
| Column | Description | Notes |
|--------|-------------|-------|
| `label` | Target variable | 0=Not Readmitted, 1=Readmitted (for training) |
| `patient_id` | Unique identifier | Excluded from training |
| `admission_date` | Date of admission | Excluded from training |

---

## 📁 Supported File Formats

- **CSV files** (`.csv`)
- **Excel files** (`.xlsx`, `.xls`)

---

## 🔧 How to Upload

### Step 1: Prepare Your Data
1. **Format your data** according to the required columns above
2. **Save as CSV or Excel** file
3. **Ensure data quality** (no excessive missing values)

### Step 2: Upload in the App
1. **Go to "Overview" page** (first page)
2. **Click on "Upload Custom Dataset" tab**
3. **Click "Choose a CSV or Excel file"**
4. **Upload your file**

### Step 3: Validation & Processing
1. **System validates** your dataset automatically (flexible validation)
2. **View validation results** and dataset summary
3. **Review any warnings** (won't prevent processing)
4. **Save dataset** for use in other pages
5. **Proceed to Preprocessing** to configure data processing

### Step 4: Train Your Model
1. **Go to "Preprocessing" page** to configure data processing
2. **Go to "Model Training" page** to train your model
3. **Select your algorithm** and parameters
4. **Train the model** on your data
5. **Evaluate performance** metrics

---

## 📊 Sample Dataset Template

Download and use this template: [`sample_dataset_template.csv`](sample_dataset_template.csv)

```csv
season,age,gender,region,primary_diagnosis,comorbidities_count,length_of_stay,treatment_type,medications_count,followup_visits_last_year,prev_readmissions,insurance_type,discharge_disposition,readmission_risk_score,label
Spring,65,Male,North,Diabetes,2,5,Medical,5,3,1,Private,Home,0.5,1
Summer,45,Female,South,Hypertension,1,3,Surgical,3,2,0,Medicare,Rehab,0.3,0
Fall,78,Male,Central,Heart Disease,3,7,Medical,8,4,2,Medicaid,Home,0.8,1
Winter,52,Female,West,Pneumonia,1,4,Medical,4,1,0,Private,Home Health,0.4,0
Spring,69,Male,Northeast,COPD,2,6,Medical,6,3,1,Medicare,Skilled Nursing,0.6,1
```

---

## ✅ Data Quality Guidelines

### Minimum Requirements
- **At least 100 rows** for meaningful training
- **No more than 20% missing values** per column
- **Balanced target distribution** (if including labels)

### Best Practices
- **1000+ rows** for robust model training
- **Clean, consistent data** formatting
- **Representative sample** of your patient population
- **Recent data** (within last 2-3 years)

### Data Preprocessing
The system automatically:
- ✅ **Standardizes formats** (capitalizes categorical values)
- ✅ **Handles missing values** (median for numerical, mode for categorical)
- ✅ **Validates ranges** (age 0-150, risk score 0-1)
- ✅ **Encodes categories** (one-hot encoding)
- ✅ **Scales features** (standardization)

---

## 🚨 Common Issues & Solutions

### Issue: "Missing required columns"
**Solution:** Ensure all 14 required columns are present with exact names (case-insensitive)

### Issue: "Invalid values in column"
**Solution:** Check that categorical values match the valid options listed above

### Issue: "Age values should be between 0-150"
**Solution:** Review age column for unrealistic values or data entry errors

### Issue: "Readmission risk score should be between 0-1"
**Solution:** Ensure risk scores are decimal values between 0.0 and 1.0

### Issue: File upload fails
**Solutions:**
- Check file format (CSV or Excel only)
- Ensure file size is reasonable (<50MB)
- Verify file is not corrupted
- Try saving Excel as CSV first

---

## 🔍 Validation Process

When you upload a file, the system:

1. **📁 Loads the file** (CSV/Excel parsing)
2. **🔍 Validates structure** (required columns present)
3. **📊 Checks data types** (numerical vs categorical)
4. **⚖️ Validates ranges** (age, risk scores, etc.)
5. **🧹 Standardizes format** (consistent capitalization)
6. **💾 Saves processed data** (for training)
7. **📈 Shows summary** (statistics and preview)

---

## 📈 After Upload

Once your data is uploaded and validated:

1. **✅ Preprocessing configured** - Set imputation and scaling methods
2. **🤖 Model training ready** - Train on your custom data
3. **🎯 Make predictions** - Use trained model for new patients
4. **📊 View analytics** - Analyze your hospital's data patterns
5. **📉 Evaluate performance** - Check model accuracy on your data

---

## 💡 Tips for Best Results

### Data Collection
- **Include diverse cases** (different ages, diagnoses, treatments)
- **Ensure data quality** (accurate, complete records)
- **Recent timeframe** (last 2-3 years for relevance)

### Feature Engineering
- **Calculate risk scores** based on clinical guidelines
- **Standardize diagnoses** (use consistent terminology)
- **Clean categorical data** (consistent spelling/formatting)

### Model Training
- **Start with default settings** for initial training
- **Experiment with algorithms** (Random Forest, Logistic Regression)
- **Validate on holdout data** to avoid overfitting

---

## 🆘 Need Help?

### Troubleshooting
1. **Check validation messages** for specific issues
2. **Review sample template** for correct format
3. **Use debug panel** in Patient Risk Analysis page
4. **Check TROUBLESHOOTING.md** for common issues

### Support
- **Validation errors** are shown with specific guidance
- **Sample data format** provided for reference
- **Automatic data cleaning** handles most formatting issues
- **Preview functionality** lets you verify data before training

---

## 🎯 Success Checklist

- [ ] Dataset has all 14 required columns
- [ ] Categorical values match valid options
- [ ] Numerical values are in valid ranges
- [ ] File uploads without errors
- [ ] Validation shows "Dataset validation successful!"
- [ ] Preview shows data correctly formatted
- [ ] Preprocessing completes successfully
- [ ] Model training works with uploaded data

---

**Ready to upload your data? Go to the Preprocessing page and select "Upload Custom Dataset"!** 🚀