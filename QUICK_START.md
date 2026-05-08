# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start Backend
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Start Frontend (in new terminal)
```bash
streamlit run frontend/app.py
```

### Step 4: Open Browser
Navigate to: **http://localhost:8501**

---

## 📊 What You'll See

### Overview Page (First Page)
- **Data Management**: Upload custom CSV/Excel files
- **Quick Metrics**: Total patients, readmission rate, avg length of stay, high risk %
- **Dataset Overview**: Statistics, feature categories, quick insights
- **📊 NEW: Data Visualizations**:
  - Age Distribution histogram
  - Readmission by Gender (count + rate charts)
  - Readmission by Primary Diagnosis (grouped bar chart)
  - Additional Insights (expandable section)
- **Model Information**: Current model metrics

### Other Pages
- **EDA**: Interactive exploratory data analysis
- **Preprocessing**: Data preprocessing options
- **Model Training**: Train new models with different algorithms
- **Patient Risk Analysis**: Predict individual patient risk
- **Analytics Dashboard**: Hospital-wide analytics
- **Model Performance**: Detailed model metrics and SHAP analysis

---

## 🔧 Common Commands

### Check Backend Health
```bash
curl http://localhost:8000/health
```

### Run Diagnostic
```bash
python diagnose_connection.py
```

### Verify Data Structure
```bash
python verify_data_structure.py
```

### Start Both Services (Alternative)
```bash
python start_full_app.py
```

---

## ✅ Verification Checklist

After starting the application:

- [ ] Backend running on port 8000
- [ ] Frontend running on port 8501
- [ ] Backend status shows "🟢 Backend Connected" in sidebar
- [ ] Overview page displays all visualizations
- [ ] Can navigate between pages
- [ ] Model metrics display correctly
- [ ] Predictions work (try Patient Risk Analysis page)

---

## 🆘 Quick Troubleshooting

### "Backend Disconnected" Warning
**Solution**: Backend is starting up. Wait 5-10 seconds and refresh the page.

### "Module not found" Error
**Solution**: Install dependencies: `pip install -r requirements.txt`

### Port Already in Use
**Solution**: 
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

### Visualizations Not Showing
**Solution**: 
1. Check dataset exists: `data/hospital_readmission_dataset.csv`
2. Verify data: `python verify_data_structure.py`
3. Ensure plotly installed: `pip install plotly`

---

## 📱 Features at a Glance

| Feature | Status | Location |
|---------|--------|----------|
| Age Distribution Chart | ✅ | Overview page |
| Gender Analysis Charts | ✅ | Overview page |
| Diagnosis Analysis Chart | ✅ | Overview page |
| Additional Insights | ✅ | Overview page (expandable) |
| Backend Retry Logic | ✅ | All prediction calls |
| Model Reload Retry | ✅ | Model Training page |
| Data Upload | ✅ | Overview page |
| Interactive EDA | ✅ | EDA page |
| Model Training | ✅ | Model Training page |
| Risk Predictions | ✅ | Patient Risk Analysis page |
| SHAP Explanations | ✅ | Patient Risk Analysis page |
| Analytics Dashboard | ✅ | Analytics Dashboard page |

---

## 🎯 What's New

### Latest Updates:
1. **Overview Page Visualizations** (NEW)
   - Age distribution histogram with 30 bins
   - Gender analysis with count and rate charts
   - Diagnosis analysis with rotated labels
   - Additional insights section

2. **Backend Connection Reliability** (IMPROVED)
   - 3 retry attempts for predictions
   - 3 retry attempts for model reload
   - 30-second timeout per attempt
   - Progress indicators
   - Embedded model fallback

3. **Error Messages** (IMPROVED)
   - Clear, informative messages
   - Troubleshooting tips included
   - No more scary error messages

---

## 📞 Need Help?

1. Check `CURRENT_STATUS.md` for system status
2. Check `TROUBLESHOOTING.md` for common issues
3. Check `BACKEND_CONNECTION_FIX.md` for connection issues
4. Check `VISUALIZATION_UPDATE.md` for visualization details
5. Run diagnostic: `python diagnose_connection.py`

---

**Ready to go!** 🚀

Start with the Overview page to see the new visualizations, then explore other pages for more features.
