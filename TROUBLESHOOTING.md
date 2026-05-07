# Troubleshooting Guide

## 🚨 Most Common Issue: 422 Error (Backend Not Restarted)

### Problem: Getting 422 error with "Field required" for old dataset fields

**Symptoms:**
- Error mentions fields like `Age`, `Gender`, `Weight_kg` (capitalized, old dataset)
- Frontend is sending new fields like `age`, `gender`, `season` (lowercase, new dataset)

**Cause:** Backend server is running with OLD code in memory, even though files are updated.

**Solution:**

1. **Stop the backend server:**
   - Go to terminal where backend is running
   - Press `Ctrl+C`

2. **Restart with auto-reload:**
   ```cmd
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   
   Or double-click: `start_backend_with_reload.bat`

3. **Verify it's working:**
   ```cmd
   python verify_backend.py
   ```
   
   Should show: ✅ "Server accepts NEW dataset fields"

**Why this happens:** Python loads code into memory once at startup. File changes don't take effect until you restart the server. The `--reload` flag auto-reloads on future changes.

---

## Model Prediction Issues

### Problem: "Model not loaded" or prediction fails

**Solution Steps:**

1. **Install all dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

2. **Train the model:**
   ```cmd
   python train_model.py
   ```

3. **Verify model files exist:**
   Check that these files are in the `models/` folder:
   - `random_forest_model.joblib`
   - `preprocessor.joblib`
   - `label_encoder.joblib`
   - `feature_names.json`
   - `metrics.json`

4. **Check backend health:**
   ```cmd
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   
   Visit: http://localhost:8000/health
   
   Should return: `{"status": "healthy", "model_loaded": true}`

### Problem: Backend API connection error

**Solution:**

1. Ensure backend is running:
   ```cmd
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Check if port 8000 is available:
   ```cmd
   netstat -ano | findstr :8000
   ```

3. If port is in use, kill the process or use a different port:
   ```cmd
   uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
   ```
   
   Then update `API_URL` in `frontend/app.py`

### Problem: Column mismatch errors

**Cause:** Input data doesn't match training data columns

**Solution:**

Ensure all required fields are provided (using NEW dataset structure):

**Categorical Features:**
- season, gender, region
- primary_diagnosis, treatment_type
- insurance_type, discharge_disposition

**Numerical Features:**
- age, comorbidities_count, length_of_stay
- medications_count, followup_visits_last_year
- prev_readmissions, readmission_risk_score

**Note:** `patient_id` and `admission_date` are automatically excluded from training and prediction.

## Quick Start Commands

```cmd
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train the model
python train_model.py

# 3. Start backend (Terminal 1)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Start frontend (Terminal 2)
streamlit run frontend/app.py

# 5. Verify backend (Optional)
python verify_backend.py
```

Or use the batch files:
- `start_backend_with_reload.bat` - Start backend with auto-reload
- `start_app.bat` - Start both frontend and backend

---

## Common Error Messages

### "ModuleNotFoundError: No module named 'X'"
**Fix:** `pip install -r requirements.txt`

### "Model file not found"
**Fix:** Train the model: `python train_model.py`

### "Preprocessor not loaded"
**Fix:** Train the model (it creates the preprocessor): `python train_model.py`

### "503 Service Unavailable"
**Fix:** Backend server is not running or model is not loaded

### "422 Unprocessable Entity"
**Fix:** Backend needs to be restarted (see top of this guide)

---

## Dataset Information

**Current Dataset:** `data/hospital_readmission_dataset.csv`

**Features (14 total):**
- **Categorical (7):** season, gender, region, primary_diagnosis, treatment_type, insurance_type, discharge_disposition
- **Numerical (7):** age, comorbidities_count, length_of_stay, medications_count, followup_visits_last_year, prev_readmissions, readmission_risk_score

**Target:** `label` (0 = Not Readmitted, 1 = Readmitted)

**Excluded:** `patient_id`, `admission_date` (identifiers, not features)

---

## Getting Help

If issues persist:
1. Check the backend console for detailed error messages
2. Check the frontend console (browser developer tools)
3. Run `python verify_backend.py` for diagnostic information
4. Review `SETUP_INSTRUCTIONS.md` for detailed setup steps
5. Review `NEW_DATASET_GUIDE.md` for dataset details

