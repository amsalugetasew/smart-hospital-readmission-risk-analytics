# 🏥 Smart Hospital Readmission Risk Analytics

An end-to-end AI-powered healthcare analytics platform that predicts hospital readmission risk using machine learning and provides actionable insights through an interactive web dashboard.



## ✨ Key Features

### 1. 🎯 Patient Risk Prediction
- Input patient data (demographics, diagnosis, treatment, medical history)
- Get instant readmission risk prediction (Readmitted / Not Readmitted)
- View probability score (0-100%) and risk category (Low/Medium/High)
- See feature importance using SHAP explainability

**Risk Category Ranges:**
- 🟢 **Low Risk**: 0% - 33% probability of readmission
- 🟡 **Medium Risk**: 33% - 66% probability of readmission
- 🔴 **High Risk**: 66% - 100% probability of readmission

**Prediction Modes:**
- **📝 Single Patient**: Manual form entry for individual predictions
- **📊 Batch Prediction**: Upload CSV/Excel files for multiple patients at once
  - Process 100s-1000s of patients in minutes
  - Download results in CSV or Excel format
  - View summary statistics and visualizations
  - Color-coded results table (green/yellow/red)

### 2. 📊 Interactive Analytics Dashboard

**Dashboard Sections:**
1. **KPIs**: Total patients, readmission rate, avg length of stay, high-risk patients
2. **Readmission Overview**: Donut charts and gauge charts
3. **Clinical Analysis**: Diagnosis and treatment type distributions
4. **Demographics**: Age distribution and length of stay analysis
5. **Geographic & Seasonal**: Regional and seasonal patterns
6. **Risk Factors**: Correlation heatmaps and scatter plots

**Interactive Features:**
- Hover for details
- Click to filter
- Zoom and pan
- Responsive design

### 3. 🔍 Exploratory Data Analysis (EDA)
- Feature distribution visualizations
- Correlation heatmap
- Missing value analysis
- Statistical summaries
- Target variable distribution

### 4. ⚙️ Data Preprocessing Pipeline
- View raw dataset (8,000 patient records)
- **📤 Upload custom CSV/Excel datasets**
- **🔍 Automatic data validation and standardization**
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
└────────────────────────────────────────────────────────────┘
```

---

## 🌐 Deployment

#### Recommended: Streamlit Cloud + Railway

1. **Deploy Backend to Railway:**
   - Push code to GitHub
   - Connect Railway to your repository
   - Railway auto-deploys using `Procfile`
   - Get your backend URL: `https://your-app.railway.app`

2. **Deploy Frontend to Streamlit Cloud:**
   - Connect Streamlit Cloud to your GitHub repository
   - Set main file: `frontend/app.py`
   - Add backend URL to secrets:
     ```toml
     API_URL = "https://your-app.railway.app"
     ```

3. **Access Your Live Application:**
   - Frontend: `https://your-app.streamlit.app`
   - Backend: `https://your-app.railway.app`



**Important**: FastAPI's `allow_origins` does NOT support wildcards like `"https://*.streamlit.app"`. Use `allow_origin_regex` with regex patterns instead.

---

## 📁 Project Structure

```
├── backend/              # FastAPI application
|   |__llm_advisor.py     # LLM endpoint
│   ├── main.py          # API endpoints
│   ├── models.py        # Pydantic models
│   └── predictor.py     # Prediction logic
├── frontend/            # Streamlit dashboard
|   ├── app.py          # Interactive UI
│   ├── embedded_predictor.py # To load Embedded Model
|   |__llm_advisor_page.py  # AI Advisiory Dashboard
├── utils/              # Utilities
│   ├── preprocess.py   # Data preprocessing
├── data/               # Dataset
│   └── hospital_readmission_dataset.csv
├── models/             # Trained models
│   ├── random_forest_model.joblib
│   ├── preprocessor.joblib
│   └── ...
└── notebooks/          # Jupyter notebooks
```

---

## 📤 Data Upload & Management

### Upload Your Own Dataset

The application supports **dynamic dataset switching**. When you upload a custom dataset, **all pages** (Overview, EDA, Preprocessing, Model Training, Analytics Dashboard) will automatically use your data.

**How to Upload:**
1. Navigate to **Overview** page
2. Go to **"Upload Custom Dataset"** tab
3. Upload CSV or Excel file with 14 required columns
4. Click **"Save & Activate Dataset"**
5. ✅ Your data is now active across all pages!

---

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### Installation & Setup

**Step 1: Install Dependencies**
```cmd
pip install -r requirements.txt
```

**Step 2: Train the Model**
```cmd
python train_model.py
```

**Step 3: Start the Application**

**Option A: Using Batch File (Windows)**
```cmd
start_app_properly.bat
```

**Option B: Manual Start**
```cmd
# Terminal 1 - Start Backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Start Frontend
streamlit run frontend/app.py
```

**Option C: Docker**
```cmd
docker build -t smart-hospital .
docker run -p 8000:8000 -p 8501:8501 smart-hospital
```

**Step 4: Access the Application**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📊 Risk Category Classification

The system classifies patients into three risk categories based on their predicted readmission probability:

### 🟢 Low Risk (0% - 33%)
- **Interpretation**: Patient has a low probability of readmission
- **Recommendation**: Standard discharge planning and follow-up care
- **Action**: Monitor as per normal protocol
- **Example**: Probability = 25% → Low Risk

### 🟡 Medium Risk (33% - 66%)
- **Interpretation**: Patient has a moderate probability of readmission
- **Recommendation**: Enhanced discharge planning and closer follow-up
- **Action**: Consider additional patient education and support services
- **Example**: Probability = 50% → Medium Risk

### 🔴 High Risk (66% - 100%)
- **Interpretation**: Patient has a high probability of readmission
- **Recommendation**: Intensive discharge planning and intervention
- **Action**: Implement readmission prevention strategies:
  - Schedule early follow-up appointments
  - Arrange home health services
  - Provide medication reconciliation
  - Ensure patient/family education
  - Consider care coordination programs
- **Example**: Probability = 75% → High Risk

### Risk Calculation Logic

```python
if probability < 0.33:
    risk_category = "Low Risk"
elif probability < 0.66:
    risk_category = "Medium Risk"
else:
    risk_category = "High Risk"
```

### Visual Indicators

The system uses color coding throughout the interface:
- 🟢 **Green** = Low Risk (Safe)
- 🟡 **Yellow/Orange** = Medium Risk (Caution)
- 🔴 **Red** = High Risk (Alert)

This color scheme is consistent across:
- Single patient predictions
- Batch prediction results
- Analytics dashboard
- Risk distribution charts

---

## 📊 Batch Predictions Guide

### Overview
Process multiple patients at once using CSV or Excel files. Perfect for daily risk assessments, discharge planning, and population health management.

### How to Use

**Step 1: Prepare Your Data**
- Download template from the app or use `sample_dataset_template.csv`
- Include 14 required columns (see Dataset Information section)
- Optional: Add `patient_id` column for tracking

**Step 2: Upload File**
- Navigate to "Patient Risk Analysis" page
- Switch to "Batch Prediction (Upload File)" tab
- Upload CSV or Excel file (.csv, .xlsx, .xls)

**Step 3: Process & Download**
- Click "Predict for All Patients"
- View summary statistics and visualizations
- Download results in CSV or Excel format

### Output Format

**Results Include:**
- `prediction` - "Readmitted" or "Not Readmitted"
- `probability` - Readmission probability (0.0 to 1.0)
- `risk_category` - "Low Risk", "Medium Risk", or "High Risk"
- All original patient data
- `patient_id` (if provided in input)

### Performance
- 100 patients: ~30 seconds
- 1,000 patients: ~5 minutes
- Supports up to 10,000 rows

### Use Cases
- **Daily Risk Assessment**: Upload today's admissions, identify high-risk patients
- **Discharge Planning**: Upload patients scheduled for discharge, plan follow-up care
- **Population Health**: Upload entire patient cohort, analyze risk distribution
- **Research**: Retrospective analysis, what-if scenarios

### Testing CORS

**Local Testing:**
```bash
# Start backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Start frontend
streamlit run frontend/app.py

# Clear Streamlit cache
streamlit cache clear
```
\


## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request


## 📝 License

This project is for educational and research purposes.
