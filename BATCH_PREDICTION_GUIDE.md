# Batch Prediction Guide

## 🎯 Overview

The Patient Risk Analysis page now supports **two prediction modes**:

1. **📝 Single Patient Prediction** - Enter data manually for one patient
2. **📊 Batch Prediction** - Upload CSV/Excel file for multiple patients

---

## 📝 Mode 1: Single Patient Prediction

### How to Use:
1. Navigate to "Patient Risk Analysis" page
2. Stay on "Single Patient Prediction" tab
3. Fill in the form with patient details
4. Click "🔮 Predict Risk"
5. View results with risk category and feature importance

### Features:
- ✅ Manual data entry
- ✅ Real-time prediction
- ✅ Explainable AI (SHAP values)
- ✅ Risk categorization (Low/Medium/High)
- ✅ Visual risk display

---

## 📊 Mode 2: Batch Prediction (File Upload)

### How to Use:

#### Step 1: Prepare Your Data File

**Option A: Download Template**
1. Click "📥 Download Template" button
2. Open the template file
3. Fill in your patient data
4. Save the file

**Option B: Create Your Own File**

Your file must have these **14 required columns**:

**Categorical Columns:**
- `season` - winter, spring, summer, fall
- `gender` - male, female
- `region` - north, south, east, west
- `primary_diagnosis` - Diabetes, Hypertension, Heart Failure, Stroke, COPD, Pneumonia, Kidney Disease, Cancer, Other
- `treatment_type` - medical, surgical, interventional
- `insurance_type` - private, medicare, medicaid, self-pay
- `discharge_disposition` - home, home health, skilled nursing, rehab, other

**Numerical Columns:**
- `age` - 18 to 120
- `comorbidities_count` - 0 to 20
- `length_of_stay` - 1 to 90 days
- `medications_count` - 0 to 50
- `followup_visits_last_year` - 0 to 50
- `prev_readmissions` - 0 to 20
- `readmission_risk_score` - 0.0 to 1.0

**Optional Column:**
- `patient_id` - Any identifier (will be included in results)

#### Step 2: Upload File
1. Switch to "Batch Prediction (Upload File)" tab
2. Click "Choose a CSV or Excel file"
3. Select your file (.csv, .xlsx, or .xls)
4. File will be loaded and validated

#### Step 3: Review Data
1. Check the data preview
2. Verify all required columns are present
3. Ensure data looks correct

#### Step 4: Run Predictions
1. Click "🔮 Predict for All Patients"
2. Wait for processing (progress bar shows status)
3. View results summary and detailed table

#### Step 5: Download Results
1. Choose download format:
   - **CSV** - Universal format
   - **Excel** - Formatted spreadsheet
2. Click download button
3. File includes all original data + predictions

---

## 📋 File Format Examples

### CSV Format:
```csv
patient_id,season,age,gender,region,primary_diagnosis,comorbidities_count,length_of_stay,treatment_type,medications_count,followup_visits_last_year,prev_readmissions,insurance_type,discharge_disposition,readmission_risk_score
P001,winter,65,male,north,Diabetes,2,5,medical,5,3,1,private,home,0.5
P002,spring,72,female,south,Hypertension,3,7,surgical,8,2,0,medicare,home health,0.6
P003,summer,58,male,east,Heart Failure,1,3,medical,4,4,2,medicaid,home,0.7
```

### Excel Format:
Same columns as CSV, but in Excel spreadsheet format (.xlsx or .xls)

---

## 📊 Results Format

### Output Columns:

**Prediction Results:**
- `prediction` - "Readmitted" or "Not Readmitted"
- `probability` - Probability of readmission (0.0 to 1.0)
- `risk_category` - "Low Risk", "Medium Risk", or "High Risk"

**Original Data:**
- All 14 input columns
- `patient_id` (if provided)

### Example Output:
```csv
patient_id,prediction,probability,risk_category,season,age,gender,...
P001,Readmitted,0.75,High Risk,winter,65,male,...
P002,Not Readmitted,0.35,Medium Risk,spring,72,female,...
P003,Readmitted,0.82,High Risk,summer,58,male,...
```

---

## 📈 Results Visualization

After batch prediction, you'll see:

### Summary Statistics:
- **Total Patients** - Number of patients processed
- **Predicted Readmissions** - Count and percentage
- **High Risk Patients** - Count and percentage
- **Average Probability** - Mean readmission probability

### Detailed Results Table:
- Color-coded by risk:
  - 🟢 Green = Low Risk
  - 🟡 Yellow = Medium Risk
  - 🔴 Red = High Risk
- Sortable and filterable
- Shows all data and predictions

### Charts:
1. **Pie Chart** - Risk category distribution
2. **Histogram** - Probability distribution

---

## 🎯 Use Cases

### Clinical Workflow:
1. **Daily Risk Assessment**
   - Upload today's admissions
   - Identify high-risk patients
   - Prioritize interventions

2. **Discharge Planning**
   - Upload patients scheduled for discharge
   - Predict readmission risk
   - Plan follow-up care

3. **Population Health**
   - Upload entire patient cohort
   - Analyze risk distribution
   - Allocate resources

### Research:
1. **Retrospective Analysis**
   - Upload historical data
   - Compare predictions to actual outcomes
   - Validate model performance

2. **What-If Scenarios**
   - Modify patient parameters
   - Re-run predictions
   - Analyze impact of interventions

---

## ⚡ Performance

### Processing Speed:
- **Single prediction**: < 1 second
- **Batch (100 patients)**: ~30 seconds
- **Batch (1000 patients)**: ~5 minutes

### File Size Limits:
- **CSV**: Up to 10,000 rows recommended
- **Excel**: Up to 5,000 rows recommended
- Larger files may take longer to process

---

## 🔧 Troubleshooting

### "Missing required columns" error
**Solution**: Ensure your file has all 14 required columns with exact names (case-insensitive)

### "Error processing file" message
**Solution**: 
- Check data types (numbers in numeric columns, text in categorical)
- Ensure no special characters in categorical values
- Verify date formats if using dates

### Slow processing
**Solution**:
- Reduce file size (split into smaller batches)
- Close other applications
- Use CSV instead of Excel (faster)

### Excel download not available
**Solution**: 
- `openpyxl` package not installed
- Use CSV download instead
- Or install: `pip install openpyxl`

### Predictions seem incorrect
**Solution**:
- Verify input data is correct
- Check data ranges (age 18-120, etc.)
- Ensure categorical values match expected format
- Review model metrics on Model Performance page

---

## 💡 Tips & Best Practices

### Data Preparation:
- ✅ Use the template as a starting point
- ✅ Keep column names lowercase
- ✅ Use consistent categorical values
- ✅ Include patient_id for tracking
- ✅ Validate data before upload

### File Management:
- ✅ Name files descriptively (e.g., `admissions_2024_01_15.csv`)
- ✅ Keep original files as backup
- ✅ Save results with timestamps
- ✅ Use version control for data files

### Workflow:
- ✅ Start with small test file (5-10 patients)
- ✅ Verify results look correct
- ✅ Then process full dataset
- ✅ Download and archive results
- ✅ Use results for clinical decisions

### Quality Control:
- ✅ Review summary statistics
- ✅ Check for unexpected patterns
- ✅ Validate high-risk predictions
- ✅ Compare to clinical judgment
- ✅ Document any discrepancies

---

## 📞 Support

### Documentation:
- **This guide** - Batch prediction instructions
- **QUICK_START.md** - General usage
- **TROUBLESHOOTING.md** - Common issues

### Test Files:
- Download template from the app
- Use sample data for testing
- Verify format before production use

---

## 🎉 Summary

**Batch Prediction Features:**
- ✅ Upload CSV or Excel files
- ✅ Process multiple patients at once
- ✅ Download results in CSV or Excel
- ✅ View summary statistics
- ✅ Visualize risk distribution
- ✅ Color-coded results table
- ✅ Include patient IDs
- ✅ Progress tracking
- ✅ Error handling

**Benefits:**
- ⚡ Fast processing (100s of patients in seconds)
- 📊 Comprehensive results
- 💾 Easy export
- 🎨 Visual insights
- 🔄 Repeatable workflow
- 📈 Scalable solution

**Perfect for:**
- Daily risk assessments
- Discharge planning
- Population health management
- Research studies
- Quality improvement projects

---

**Start using batch prediction today to streamline your readmission risk assessment workflow!** 🚀
