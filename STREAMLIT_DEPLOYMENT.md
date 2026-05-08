# 🚀 Streamlit Cloud Deployment Guide

## 🎯 Quick Fix for Deployment Errors

If you're getting "Error installing requirements" on Streamlit Cloud, follow these steps:

### Step 1: Use Minimal Requirements
The current `requirements.txt` has been optimized for Streamlit Cloud with minimal dependencies:

```txt
# Core packages for Streamlit deployment
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
plotly==5.15.0
streamlit==1.25.0
streamlit-option-menu==0.3.6
requests==2.31.0
joblib==1.3.2
openpyxl==3.1.2
```

### Step 2: Deployment Settings

**Repository Settings:**
- **Main file path:** `frontend/app.py`
- **Python version:** 3.9 or 3.10 (recommended)
- **Requirements file:** `requirements.txt` (in root directory)

**Advanced Settings (if needed):**
- **Packages file:** `packages.txt` (for system dependencies)
- **Secrets:** Add `API_URL` if using external backend

### Step 3: Troubleshooting Common Issues

#### Issue 1: Package Version Conflicts
**Solution:** Use the exact versions specified in requirements.txt

#### Issue 2: Missing System Dependencies
**Solution:** The `packages.txt` file includes necessary system packages

#### Issue 3: Import Errors
**Solution:** The app now handles missing packages gracefully:
- XGBoost is optional (will show fewer algorithm options if missing)
- Matplotlib/Seaborn are optional (will use Plotly instead)
- SHAP is optional (will show simpler feature importance)

#### Issue 4: Memory Issues
**Solution:** Streamlit Cloud has memory limits. The app is optimized to:
- Load data efficiently
- Use minimal dependencies
- Handle large datasets gracefully

### Step 4: Alternative Minimal Requirements

If you still have issues, try this ultra-minimal version:

```txt
# Ultra-minimal for troubleshooting
streamlit==1.25.0
pandas==2.0.3
numpy==1.24.3
plotly==5.15.0
requests==2.31.0
streamlit-option-menu==0.3.6
```

### Step 5: Frontend-Only Deployment

The app is designed to work in frontend-only mode:
- ✅ Data upload and validation
- ✅ Basic analytics and visualizations  
- ✅ EDA (Exploratory Data Analysis)
- ✅ Data preprocessing configuration
- ⚠️ Model training (limited to basic algorithms)
- ⚠️ Predictions (will show "Backend Disconnected" but still functional)

### Step 6: Deployment Checklist

- [ ] Repository is public or you have Streamlit Cloud access
- [ ] `frontend/app.py` exists and is the main file
- [ ] `requirements.txt` uses minimal dependencies
- [ ] No sensitive data in the repository
- [ ] Test locally first: `streamlit run frontend/app.py`

### Step 7: Expected Behavior

**✅ What Works:**
- Data upload and validation
- Dataset overview and statistics
- Interactive data exploration (EDA)
- Data preprocessing configuration
- Basic model training (Random Forest, Logistic Regression)
- Analytics dashboard with sample data

**⚠️ What May Be Limited:**
- Advanced algorithms (XGBoost) if not available
- Backend API features (will show disconnected status)
- Complex visualizations (will fallback to Plotly)

### Step 8: Monitoring Deployment

1. **Check Build Logs:** Click "Manage App" → "Logs" to see detailed error messages
2. **Common Error Messages:**
   - `No module named 'xyz'` → Add to requirements.txt
   - `Memory limit exceeded` → Use minimal requirements
   - `Build timeout` → Reduce dependencies

### Step 9: Success Indicators

When deployment succeeds, you should see:
- ✅ App loads without errors
- ✅ Navigation menu works
- ✅ Data upload functionality available
- ✅ Sample data displays correctly
- ⚠️ "Backend Disconnected" message (expected for frontend-only)

### Step 10: Getting Help

If you still have issues:
1. **Check the exact error message** in Streamlit Cloud logs
2. **Try the ultra-minimal requirements** first
3. **Test locally** to ensure the app works
4. **Remove optional features** temporarily (XGBoost, SHAP, etc.)

---

## 🔧 Advanced Configuration

### Custom Domain (Optional)
Once deployed, you can configure a custom domain in Streamlit Cloud settings.

### Environment Variables
Add these in Streamlit Cloud secrets if needed:
```toml
API_URL = "your-backend-url-here"
```

### Performance Optimization
- The app automatically handles missing packages
- Uses efficient data loading
- Minimal memory footprint
- Graceful degradation for missing features

---

## 📞 Support

If deployment still fails:
1. Share the exact error message from Streamlit Cloud logs
2. Verify all files are in the correct locations
3. Test with the ultra-minimal requirements first
4. Consider deploying only the essential features initially

**The app is designed to work even with minimal dependencies!** 🚀