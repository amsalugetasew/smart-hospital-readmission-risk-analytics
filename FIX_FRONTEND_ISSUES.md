# 🔧 Fix Frontend Connection Issues

## 🎯 Current Issues

1. **Model Training:** "Random Forest trained successfully, but backend API failed to reload"
2. **Prediction:** "API Error (404): Not Found"

## ✅ Backend Status: Working ✅

The backend is confirmed working:
- ✅ Health endpoint: `http://localhost:8000/health`
- ✅ Analytics endpoint: `http://localhost:8000/analytics`
- ✅ Prediction endpoint: `http://localhost:8000/predict`
- ✅ Reload endpoint: `http://localhost:8000/reload-model`

## 🔧 Solutions

### Solution 1: Clear Streamlit Cache

1. **In the Streamlit web interface:**
   - Click the hamburger menu (☰) in top right
   - Click "Clear cache"
   - Refresh the page

2. **Or restart Streamlit:**
   ```cmd
   # Stop Streamlit (Ctrl+C)
   # Then restart:
   streamlit run frontend/app.py
   ```

### Solution 2: Check Debug Panel

1. **Go to "Patient Risk Analysis" page**
2. **Expand "🔧 Debug Information"**
3. **Check Backend URL and Status**
4. **Click "Test Backend Connection"**

### Solution 3: Manual Backend Restart

Even though backend is working, restart it to be sure:

```cmd
# Stop backend (Ctrl+C in backend terminal)
# Restart:
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Solution 4: Test Connection Manually

```cmd
# Run the connection test
python test_connection.py
```

Should show all ✅ green checkmarks.

### Solution 5: Check Browser Console

1. **Open browser Developer Tools (F12)**
2. **Go to Console tab**
3. **Look for any JavaScript errors**
4. **Refresh the page and check for new errors**

## 🎯 Expected Behavior

### Model Training Page
- After training completes
- Should show: "✅ Random Forest trained successfully and backend API reloaded!"

### Patient Risk Analysis Page
- After filling form and clicking "Predict Risk"
- Should show prediction results with probability and risk factors

## 🔍 Debugging Steps

### Step 1: Verify Backend
```cmd
# Test all endpoints
python test_connection.py
```

### Step 2: Check Streamlit
1. Look at Streamlit terminal for errors
2. Check browser console for JavaScript errors
3. Try clearing cache and refreshing

### Step 3: Check URLs
- Backend should be: `http://127.0.0.1:8000`
- Frontend should be: `http://localhost:8501`
- Check debug panel shows correct backend URL

### Step 4: Test Individual Endpoints

**Health Check:**
```cmd
curl http://localhost:8000/health
```

**Prediction Test:**
```cmd
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d "{\"season\":\"Spring\",\"age\":65,\"gender\":\"Male\",\"region\":\"North\",\"primary_diagnosis\":\"Diabetes\",\"comorbidities_count\":2,\"length_of_stay\":5,\"treatment_type\":\"Medical\",\"medications_count\":5,\"followup_visits_last_year\":3,\"prev_readmissions\":1,\"insurance_type\":\"Private\",\"discharge_disposition\":\"Home\",\"readmission_risk_score\":0.5}"
```

## 🚨 If Still Not Working

### Check These Common Issues:

1. **Port Conflicts:**
   ```cmd
   netstat -ano | findstr :8000
   netstat -ano | findstr :8501
   ```

2. **Firewall/Antivirus:**
   - Temporarily disable to test
   - Add Python to firewall exceptions

3. **Virtual Environment:**
   - Ensure you're in the correct venv
   - Check all packages are installed

4. **File Permissions:**
   - Check models/ folder exists and is writable
   - Verify model files were created after training

## 💡 Quick Fixes

### Fix 1: Force Reload Everything
```cmd
# Terminal 1: Stop and restart backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Stop and restart frontend
streamlit run frontend/app.py

# Browser: Clear cache and refresh
```

### Fix 2: Retrain Model
```cmd
# Retrain to ensure model files are fresh
python train_model.py

# Then test prediction
python test_connection.py
```

### Fix 3: Check Model Files
```cmd
# Verify model files exist
dir models\
```

Should show:
- `random_forest_model.joblib`
- `preprocessor.joblib`
- `label_encoder.joblib`
- `feature_names.json`
- `metrics.json`

## ✅ Success Indicators

When everything is working:

1. **Sidebar shows:** 🟢 Backend Connected
2. **Model Training:** Shows success message with ✅
3. **Prediction:** Returns results with probability and risk factors
4. **Debug Panel:** Shows backend as healthy
5. **No errors** in browser console or Streamlit terminal

---

**Most likely fix:** Clear Streamlit cache and refresh the page! 🔄