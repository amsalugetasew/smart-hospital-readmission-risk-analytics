# 🛠️ Troubleshooting Guide

## 🚨 Most Common Issues

### 1. Backend Connection Error

**Problem:** Frontend shows "Cannot connect to backend API"

**Symptoms:**
- ❌ Cannot connect to backend API at http://127.0.0.1:8000
- ❌ Connection refused or timeout errors
- ❌ Prediction page doesn't work

**Solution:**

1. **Check if backend is running:**
   ```cmd
   python verify_backend.py
   ```

2. **Start the backend server:**
   ```cmd
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   
   Or double-click: `start_backend_with_reload.bat`

3. **Verify backend health:**
   - Open: http://localhost:8000/health
   - Should return: `{"status": "healthy", "model_loaded": true}`

4. **Check API documentation:**
   - Open: http://localhost:8000/docs
   - Should show FastAPI interactive documentation

---

### 2. Model Not Loaded Error

**Problem:** Backend returns "Model not loaded" (503 error)

**Symptoms:**
- ❌ "Model not loaded. Please train a model first"
- ❌ Missing model files in `models/` directory
- ❌ Backend health check fails

**Solution:**

1. **Train the model:**
   ```cmd
   python train_model.py
   ```

2. **Verify model files exist:**
   Check that these files are in `models/` folder:
   - `random_forest_model.joblib`
   - `preprocessor.joblib`
   - `label_encoder.joblib`
   - `feature_names.json`
   - `metrics.json`

3. **Reload the model (if files exist):**
   ```cmd
   curl -X POST http://localhost:8000/reload-model
   ```

4. **Restart backend after training:**
   ```cmd
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

### 3. 422 Validation Error

**Problem:** Getting 422 error with "Field required"

**Symptoms:**
- ❌ API Error (422): Field required for specific patient data fields
- ❌ Frontend form submission fails
- ❌ Missing or incorrect patient data format

**Cause:** Patient data doesn't match the expected format or missing required fields.

**Solution:**

1. **Check required fields:** All 14 fields must be provided:
   
   **Categorical Fields:**
   - season (Spring, Summer, Fall, Winter)
   - gender (Male, Female)
   - region (North, South, East, West)
   - primary_diagnosis (Diabetes, Hypertension, Heart Disease, etc.)
   - treatment_type (Medical, Surgical)
   - insurance_type (Private, Medicare, Medicaid)
   - discharge_disposition (Home, Rehab, SNF)

   **Numerical Fields:**
   - age (integer, years)
   - comorbidities_count (integer)
   - length_of_stay (integer, days)
   - medications_count (integer)
   - followup_visits_last_year (integer)
   - prev_readmissions (integer)
   - readmission_risk_score (float, 0.0-1.0)

2. **Use the frontend form:** The Streamlit form automatically formats data correctly

3. **Check API documentation:** Visit http://localhost:8000/docs for exact field requirements

---

### 4. Frontend Pages Not Loading

**Problem:** Streamlit pages show errors or don't display correctly

**Symptoms:**
- ❌ "FileNotFoundError" when loading dataset
- ❌ Empty charts or missing data
- ❌ Analytics dashboard shows no data

**Solution:**

1. **Check dataset exists:**
   ```cmd
   dir data\hospital_readmission_dataset.csv
   ```

2. **Verify working directory:**
   - Run Streamlit from project root directory
   - Ensure you're in: `Smart-Hospital-Readmission-Risk-Analytics/`

3. **Restart Streamlit:**
   ```cmd
   streamlit run frontend/app.py
   ```

4. **Clear Streamlit cache:**
   - In the web interface: Settings → Clear Cache
   - Or restart Streamlit completely

---

### 5. Port Already in Use

**Problem:** Cannot start backend or frontend due to port conflicts

**Symptoms:**
- ❌ "Port 8000 is already in use"
- ❌ "Port 8501 is already in use"
- ❌ Address already in use error

**Solution:**

1. **Find and kill processes using the ports:**
   ```cmd
   # Check what's using port 8000 (backend)
   netstat -ano | findstr :8000
   
   # Check what's using port 8501 (frontend)
   netstat -ano | findstr :8501
   ```

2. **Kill the process (replace PID with actual process ID):**
   ```cmd
   taskkill /PID <PID> /F
   ```

3. **Or use different ports:**
   ```cmd
   # Backend on different port
   uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
   
   # Frontend on different port
   streamlit run frontend/app.py --server.port 8502
   ```

4. **Update API_URL in frontend if using different backend port:**
   - Edit `frontend/app.py`
   - Change `API_URL = "http://127.0.0.1:8000"` to new port

---

### 6. SHAP Explainer Errors

**Problem:** Feature importance/SHAP values not showing

**Symptoms:**
- ❌ "Feature importance unavailable"
- ❌ SHAP explainer fails
- ❌ Prediction works but no explanations

**Solution:**

The system has built-in fallbacks:
1. **Primary:** SHAP TreeExplainer for Random Forest
2. **Fallback 1:** Model's built-in feature_importances_
3. **Fallback 2:** "Feature importance unavailable" message

If SHAP consistently fails:
1. **Reinstall SHAP:**
   ```cmd
   pip uninstall shap
   pip install shap
   ```

2. **Check model type:** SHAP works best with tree-based models (Random Forest, XGBoost)

3. **Retrain model:**
   ```cmd
   python train_model.py
   ```

---

## 🔧 Installation Issues

### Missing Dependencies

**Problem:** ModuleNotFoundError for various packages

**Solution:**
```cmd
# Install all dependencies
pip install -r requirements.txt

# Or install individually if needed
pip install streamlit fastapi uvicorn pandas scikit-learn plotly shap joblib
```

### Python Version Issues

**Problem:** Compatibility errors or syntax issues

**Solution:**
- **Minimum Python version:** 3.8+
- **Recommended:** Python 3.9 or 3.10
- Check version: `python --version`

### Virtual Environment Issues

**Problem:** Package conflicts or permission errors

**Solution:**
```cmd
# Create new virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## ⚡ Quick Start Commands

### Complete Setup (First Time)
```cmd
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train the model
python train_model.py

# 3. Start backend (Terminal 1)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Start frontend (Terminal 2)
streamlit run frontend/app.py
```

### Daily Usage
```cmd
# Option 1: Use batch files (Windows)
start_backend_with_reload.bat    # Terminal 1
streamlit run frontend/app.py    # Terminal 2

# Option 2: Manual commands
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
streamlit run frontend/app.py
```

### Verification & Testing
```cmd
# Verify backend is working
python verify_backend.py

# Check backend health
curl http://localhost:8000/health

# Check API documentation
# Open: http://localhost:8000/docs

# Access frontend
# Open: http://localhost:8501
```

---

## 🌐 Application URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:8501 | Main web dashboard |
| **Backend API** | http://localhost:8000 | REST API endpoints |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/health | Backend status |

---

## 📊 Understanding the System

### Frontend Pages (7 Total)

1. **Overview** - Dataset statistics and key metrics
2. **EDA** - Exploratory data analysis with charts
3. **Preprocessing** - Data preprocessing pipeline
4. **Model Training** - Train and configure ML models
5. **Patient Risk Analysis** - Predict individual patient risk
6. **Analytics Dashboard** - Hospital-wide analytics
7. **Model Performance** - Model evaluation metrics

### Backend Endpoints (4 Total)

1. **GET /health** - Check if API and model are loaded
2. **POST /predict** - Predict readmission risk for a patient
3. **GET /analytics** - Get hospital statistics
4. **POST /reload-model** - Reload model from disk

### Data Flow

1. **Training:** `train_model.py` → processes data → saves model files
2. **Backend:** Loads model files → serves predictions via API
3. **Frontend:** Calls backend API → displays results to users

---

## 🔍 Diagnostic Commands

### Check System Status
```cmd
# Verify all components
python verify_backend.py

# Check if ports are in use
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# Check Python packages
pip list | findstr "streamlit\|fastapi\|scikit-learn"
```

### Check Files
```cmd
# Verify dataset exists
dir data\hospital_readmission_dataset.csv

# Verify model files exist
dir models\*.joblib
dir models\*.json

# Check project structure
tree /F
```

### Test API Manually
```cmd
# Test health endpoint
curl http://localhost:8000/health

# Test prediction endpoint (example)
curl -X POST http://localhost:8000/predict ^
  -H "Content-Type: application/json" ^
  -d "{\"season\":\"Spring\",\"age\":65,\"gender\":\"Male\",\"region\":\"North\",\"primary_diagnosis\":\"Diabetes\",\"comorbidities_count\":2,\"length_of_stay\":5,\"treatment_type\":\"Medical\",\"medications_count\":5,\"followup_visits_last_year\":3,\"prev_readmissions\":1,\"insurance_type\":\"Private\",\"discharge_disposition\":\"Home\",\"readmission_risk_score\":0.5}"
```

---

## 📋 Dataset Information

### Current Dataset: `hospital_readmission_dataset.csv`

**Overview:**
- **Total Records:** 8,000 patients
- **Total Columns:** 17 (14 features + 2 identifiers + 1 target)
- **Target Variable:** `label` (0 = Not Readmitted, 1 = Readmitted)
- **Class Distribution:** ~77% readmitted, ~23% not readmitted

### Features Used for Prediction (14 total)

**Categorical Features (7):**
- `season` - Spring, Summer, Fall, Winter
- `gender` - Male, Female
- `region` - North, South, East, West
- `primary_diagnosis` - Diabetes, Hypertension, Heart Disease, Pneumonia, etc.
- `treatment_type` - Medical, Surgical
- `insurance_type` - Private, Medicare, Medicaid
- `discharge_disposition` - Home, Rehab, SNF (Skilled Nursing Facility)

**Numerical Features (7):**
- `age` - Patient age in years (18-95)
- `comorbidities_count` - Number of comorbid conditions (0-8)
- `length_of_stay` - Hospital stay duration in days (1-30)
- `medications_count` - Number of medications (1-15)
- `followup_visits_last_year` - Follow-up visits in past year (0-12)
- `prev_readmissions` - Previous readmissions count (0-5)
- `readmission_risk_score` - Pre-calculated risk score (0.0-1.0)

### Excluded from Training
- `patient_id` - Unique identifier (not predictive)
- `admission_date` - Date of admission (not used for prediction)

### Data Quality
- **Missing Values:** 0 (dataset is complete)
- **Data Types:** Mixed (categorical strings, integers, floats)
- **Preprocessing:** Automatic scaling and encoding applied

---

## 🚨 Common Error Messages

### Backend Errors

| Error | Meaning | Solution |
|-------|---------|----------|
| `Model not loaded` | No trained model available | Run `python train_model.py` |
| `Preprocessor not loaded` | Missing preprocessing pipeline | Train model (creates preprocessor) |
| `503 Service Unavailable` | Backend server issue | Check backend is running |
| `422 Unprocessable Entity` | Invalid input data format | Check all 14 fields are provided |
| `Connection refused` | Backend not running | Start backend server |

### Frontend Errors

| Error | Meaning | Solution |
|-------|---------|----------|
| `Cannot connect to backend API` | Frontend can't reach backend | Start backend server |
| `FileNotFoundError` | Dataset file missing | Check `data/` folder exists |
| `Request timed out` | Backend taking too long | Restart backend, check model |
| `Empty charts` | No data to display | Check dataset and backend connection |

### Training Errors

| Error | Meaning | Solution |
|-------|---------|----------|
| `FileNotFoundError: dataset` | Dataset file missing | Check `data/hospital_readmission_dataset.csv` |
| `Permission denied` | Cannot write model files | Check `models/` folder permissions |
| `Memory error` | Insufficient RAM | Close other applications |
| `Import error` | Missing packages | Run `pip install -r requirements.txt` |

---

## 🆘 Getting Help

### Step-by-Step Debugging

1. **Check Python and packages:**
   ```cmd
   python --version
   pip list | findstr "streamlit\|fastapi\|scikit-learn"
   ```

2. **Verify project structure:**
   ```cmd
   dir data\hospital_readmission_dataset.csv
   dir models\
   dir backend\
   dir frontend\
   ```

3. **Test backend independently:**
   ```cmd
   python verify_backend.py
   ```

4. **Check logs:**
   - Backend: Look at terminal where `uvicorn` is running
   - Frontend: Look at terminal where `streamlit` is running
   - Browser: Open Developer Tools (F12) → Console tab

5. **Test step by step:**
   - Train model: `python train_model.py`
   - Start backend: `uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`
   - Test health: Open http://localhost:8000/health
   - Start frontend: `streamlit run frontend/app.py`
   - Test prediction: Use the Patient Risk Analysis page

### Still Having Issues?

1. **Check system requirements:**
   - Python 3.8+ (recommended: 3.9 or 3.10)
   - 4GB+ RAM available
   - 1GB+ disk space

2. **Try clean installation:**
   ```cmd
   # Create new virtual environment
   python -m venv fresh_env
   fresh_env\Scripts\activate
   pip install -r requirements.txt
   python train_model.py
   ```

3. **Check firewall/antivirus:**
   - Ensure ports 8000 and 8501 are not blocked
   - Add Python to firewall exceptions if needed

4. **Review error messages carefully:**
   - Copy exact error message
   - Check which component is failing (backend/frontend/training)
   - Look for specific file or function names in error

---

## 📝 Performance Tips

### For Better Performance

1. **Use SSD storage** for faster model loading
2. **Close unnecessary applications** to free RAM
3. **Use `--reload` flag only in development** (remove in production)
4. **Consider smaller model** if memory is limited
5. **Use batch predictions** for multiple patients

### For Development

1. **Use auto-reload** for both backend and frontend during development
2. **Keep browser developer tools open** to catch JavaScript errors
3. **Monitor system resources** (Task Manager) during training
4. **Use virtual environment** to avoid package conflicts
5. **Regularly clear Streamlit cache** if data changes frequently

---

**Last Updated:** May 7, 2026  
**Compatible with:** Python 3.8+, Windows 10+  
**Tested on:** Windows 11, Python 3.10

