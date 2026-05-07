# 🏥 Smart Hospital Readmission Risk Analytics

An end-to-end AI-powered healthcare analytics platform that predicts hospital readmission risk using machine learning and provides actionable insights through an interactive web dashboard.

## 🎯 What This System Does

This platform helps healthcare professionals:
- **Predict** which patients are at risk of hospital readmission within 30 days
- **Identify** key risk factors contributing to readmission using explainable AI (SHAP)
- **Monitor** hospital-wide readmission trends and performance metrics
- **Analyze** patient demographics, diagnoses, and treatment patterns
- **Make** data-driven decisions to improve patient outcomes and reduce costs

---

## ✨ Key Features

### 1. 🎯 Patient Risk Prediction
- Input patient data (demographics, diagnosis, treatment, medical history)
- Get instant readmission risk prediction (Readmitted / Not Readmitted)
- View probability score (0-100%) and risk category (Low/Medium/High)
- See feature importance using SHAP explainability

### 2. 📊 Interactive Analytics Dashboard
- Real-time hospital statistics (total patients, readmission rate, avg length of stay)
- High-risk patient identification (risk score > 0.7)
- Regional distribution analysis
- Diagnosis breakdown and trends
- Treatment type effectiveness

### 3. 🔍 Exploratory Data Analysis (EDA)
- Feature distribution visualizations
- Correlation heatmap
- Missing value analysis
- Statistical summaries
- Target variable distribution

### 4. ⚙️ Data Preprocessing Pipeline
- View raw dataset (8,000 patient records)
- Automatic handling of missing values
- Feature scaling (StandardScaler for numerical features)
- One-hot encoding (categorical features)
- Consistent preprocessing for training and prediction

### 5. 🤖 Model Training & Evaluation
- Train Random Forest classifier on hospital data
- Configurable hyperparameters (n_estimators, max_depth, etc.)
- Automatic train/test split (80/20)
- Class balancing for imbalanced data
- Real-time training progress

### 6. 📈 Model Performance Metrics
- Accuracy, Precision, Recall, F1 Score, ROC AUC
- Confusion matrix visualization
- Classification report
- Feature importance ranking
- Model comparison capabilities

### 7. 📋 Dataset Overview
- 8,000 patient records
- 14 predictive features (7 categorical + 7 numerical)
- Target: Readmission within 30 days (Yes/No)
- Comprehensive statistics and insights

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                        │
│         (Interactive Web Dashboard - Port 8501)              │
│                                                              │
│  Pages:                                                      │
│  • Overview          • EDA                • Preprocessing    │
│  • Model Training    • Patient Analysis  • Analytics        │
│  • Model Performance                                         │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP REST API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                           │
│              (REST API Server - Port 8000)                   │
│                                                              │
│  Endpoints:                                                  │
│  • POST /predict      - Predict readmission risk            │
│  • GET  /analytics    - Get hospital statistics             │
│  • GET  /health       - Check API health                    │
│  • POST /reload-model - Reload trained model                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   ML PREDICTION PIPELINE                     │
│                                                              │
│  1. Load patient data                                        │
│  2. Apply preprocessing (same as training)                   │
│  3. Random Forest prediction                                 │
│  4. Calculate SHAP values (feature importance)               │
│  5. Return prediction + probability + explanations           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA & MODELS                           │
│                                                              │
│  • hospital_readmission_dataset.csv (8,000 patients)        │
│  • random_forest_model.joblib (trained classifier)          │
│  • preprocessor.joblib (fitted preprocessing pipeline)      │
│  • label_encoder.joblib (target encoding)                   │
│  • feature_names.json (feature list after encoding)         │
│  • metrics.json (model performance metrics)                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
├── backend/              # FastAPI application
│   ├── main.py          # API endpoints
│   ├── models.py        # Pydantic models
│   └── predictor.py     # Prediction logic
├── frontend/            # Streamlit dashboard
│   └── app.py          # Interactive UI
├── utils/              # Utilities
│   ├── preprocess.py   # Data preprocessing
│   └── generate_data.py # Data generation
├── data/               # Dataset
│   └── hospital_readmission_dataset.csv
├── models/             # Trained models
│   ├── random_forest_model.joblib
│   ├── preprocessor.joblib
│   └── ...
└── notebooks/          # Jupyter notebooks
```

---

## 🚀 Quick Start

### Option 1: Using Batch Files (Easiest)

1. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

2. **Train the model:**
   ```cmd
   python train_model.py
   ```

3. **Start the application:**
   - Double-click `start_backend_with_reload.bat` (starts backend)
   - Double-click `start_app.bat` (starts both frontend and backend)

### Option 2: Manual Setup

1. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

2. **Train the model:**
   ```cmd
   python train_model.py
   ```

3. **Start backend (Terminal 1):**
   ```cmd
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Start frontend (Terminal 2):**
   ```cmd
   streamlit run frontend/app.py
   ```

5. **Access the application:**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 3: Docker

```cmd
docker build -t smart-hospital .
docker run -p 8000:8000 -p 8501:8501 smart-hospital
```

---

## 📊 Dataset Information

**Current Dataset:** `hospital_readmission_dataset.csv`

- **Total Patients:** 8,000
- **Total Features:** 14 (+ 2 identifiers excluded from training)
- **Target Variable:** `label` (0 = Not Readmitted, 1 = Readmitted)

### Features

**Categorical (7):**
- season, gender, region
- primary_diagnosis, treatment_type
- insurance_type, discharge_disposition

**Numerical (7):**
- age, comorbidities_count, length_of_stay
- medications_count, followup_visits_last_year
- prev_readmissions, readmission_risk_score

**Excluded from Training:**
- patient_id (identifier)
- admission_date (identifier)

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check API and model health |
| POST | `/predict` | Predict readmission risk |
| GET | `/analytics` | Get aggregated analytics |
| POST | `/reload-model` | Reload model from disk |

### Example Prediction Request

```json
{
  "season": "Spring",
  "age": 65,
  "gender": "Male",
  "region": "North",
  "primary_diagnosis": "Diabetes",
  "comorbidities_count": 2,
  "length_of_stay": 5,
  "treatment_type": "Medical",
  "medications_count": 5,
  "followup_visits_last_year": 3,
  "prev_readmissions": 1,
  "insurance_type": "Private",
  "discharge_disposition": "Home",
  "readmission_risk_score": 0.5
}
```

---

## 🛠️ Troubleshooting

### Common Issues

**422 Error (Field required):**
- Backend server needs to be restarted
- Solution: Stop backend (Ctrl+C) and restart with `--reload` flag
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for details

**Model not loaded:**
- Train the model first: `python train_model.py`
- Verify model files exist in `models/` folder

**Backend connection error:**
- Ensure backend is running on port 8000
- Check: http://localhost:8000/health

**For detailed troubleshooting:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 🧪 Testing

**Verify backend and model:**
```cmd
python verify_backend.py
```

This checks:
- ✅ Backend files have correct structure
- ✅ Backend server is running
- ✅ Server accepts new dataset fields

---

## 🔄 Preprocessing Pipeline

The preprocessing pipeline ensures consistency between training and prediction:

**Training Phase:**
1. Load data from `hospital_readmission_dataset.csv`
2. Exclude `patient_id` and `admission_date` (identifiers)
3. Split features into categorical and numerical
4. Apply preprocessing:
   - **Numerical:** Impute missing values (median) → Scale (StandardScaler)
   - **Categorical:** Impute missing values (most frequent) → One-hot encode
5. Fit preprocessor on training data
6. Save to `models/preprocessor.joblib`

**Prediction Phase:**
1. Load saved preprocessor from `models/preprocessor.joblib`
2. Apply same transformations via `.transform()` (not `.fit_transform()`)
3. Guarantees identical preprocessing (same imputation values, scaling parameters, encoding)

This ensures the model receives data in the exact same format during prediction as it saw during training.

---

## 🎯 Model Performance

The trained Random Forest model achieves:
- **Accuracy:** ~85-90%
- **Precision:** ~80-85%
- **Recall:** ~85-90%
- **F1 Score:** ~82-87%
- **ROC AUC:** ~90-95%

*Metrics vary based on training data and hyperparameters*

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

This project is for educational and research purposes.

---

## 🆘 Need Help?

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
2. Run `python verify_backend.py` for diagnostics
3. Check backend console for error messages
4. Review API docs at http://localhost:8000/docs

---

## 📝 License

This project is for educational and research purposes.
