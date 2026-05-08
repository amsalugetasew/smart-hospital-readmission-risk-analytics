# 🏥 Smart Hospital Readmission Risk Analytics

An end-to-end AI-powered healthcare analytics platform that predicts hospital readmission risk using machine learning and provides actionable insights through an interactive web dashboard.

## 📋 Table of Contents
- [What This System Does](#-what-this-system-does)
- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
- [System Architecture](#-system-architecture)
- [Deployment](#-deployment)
- [Batch Predictions](#-batch-predictions)
- [Analytics Dashboard](#-analytics-dashboard)
- [Risk Categories](#-risk-categories)
- [Dataset Information](#-dataset-information)
- [API Endpoints](#-api-endpoints)
- [Troubleshooting](#-troubleshooting)
- [CORS Configuration](#-cors-configuration)

---

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

**Hospital-Themed Visualizations:**
- 12+ interactive chart types (donut, gauge, bar, area, violin, scatter, heatmap, funnel, line)
- Hospital-themed color palette (Medical Blue, Green, Red, Orange, Teal, Purple)
- Color meanings: Green = Safe/Not Readmitted, Red = Risk/Readmitted

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

#### CORS Configuration for Deployment

The backend is configured to work with Streamlit Cloud deployments:

```python
# backend/main.py CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",      # Local development
        "http://127.0.0.1:8501",
    ],
    allow_origin_regex=r"https://.*\.streamlit\.app|https://.*\.streamlitapp\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Important**: FastAPI's `allow_origins` does NOT support wildcards like `"https://*.streamlit.app"`. Use `allow_origin_regex` with regex patterns instead.

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

## 📤 Data Upload & Management

### Upload Your Own Dataset

The application supports **dynamic dataset switching**. When you upload a custom dataset, **all pages** (Overview, EDA, Preprocessing, Model Training, Analytics Dashboard) will automatically use your data.

**How to Upload:**
1. Navigate to **Overview** page
2. Go to **"Upload Custom Dataset"** tab
3. Upload CSV or Excel file with 14 required columns
4. Click **"Save & Activate Dataset"**
5. ✅ Your data is now active across all pages!

**Visual Indicators:**
- **Sidebar** shows active dataset: "📊 Active Dataset: Uploaded Data" or "Default Data"
- **Overview page** shows current dataset status with switch button
- Easy switching between uploaded and default datasets

**Required Columns for Upload:**
- All 14 feature columns (see Dataset Information section)
- `label` column (0 = Not Readmitted, 1 = Readmitted) - Required for training
- Optional: `patient_id`, `admission_date` (excluded from training)

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

---

## 📊 Analytics Dashboard Guide

### Hospital-Themed Color Palette

**Primary Colors:**
- **Medical Blue** (#0066CC) - Trust, information
- **Medical Green** (#00A86B) - Success, safe outcomes
- **Medical Red** (#DC143C) - Danger, high risk
- **Medical Orange** (#FF6B35) - Warning, attention
- **Medical Teal** (#20B2AA) - Information, calm
- **Medical Purple** (#9370DB) - Special categories

**Color Meanings:**
- 🟢 Green = Not Readmitted, Safe, Low Risk
- 🔴 Red = Readmitted, Danger, High Risk
- 🟡 Yellow/Orange = Warning, Medium Risk
- 🔵 Blue = Neutral, Information

### Available Chart Types

The dashboard includes 12+ interactive chart types:

1. **Donut Charts** - Part-to-whole relationships (readmission distribution)
2. **Gauge Charts** - Performance indicators with color zones
3. **Horizontal Bar Charts** - Sorted comparisons (diagnosis rates)
4. **Stacked Bar Charts** - Composition analysis (treatment types)
5. **Area Charts** - Age distribution trends
6. **Violin Plots** - Length of stay distributions
7. **Scatter Plots** - Comorbidities vs medications relationships
8. **Heatmaps** - Risk factor correlations
9. **Funnel Charts** - Insurance type distribution
10. **Line Charts** - Previous readmissions trends
11. **Pie Charts** - Regional distribution
12. **Combination Charts** - Line + bar for dual metrics

### Dashboard Sections

**1. Key Performance Indicators (KPIs)**
- Total Patients
- Readmission Rate (with delta)
- Average Length of Stay
- High Risk Patients (%)
- Average Age

**2. Readmission Overview**
- Overall distribution donut chart
- Readmission rate gauge with zones (Green: 0-30%, Orange: 30-60%, Red: 60-100%)

**3. Clinical Analysis**
- Readmission rate by primary diagnosis (sorted horizontal bar)
- Treatment type distribution (stacked bar showing readmitted vs not)

**4. Demographics & Stay Duration**
- Age distribution by readmission status (area chart)
- Length of stay distribution (violin plot with box plot overlay)

**5. Geographic & Seasonal Patterns**
- Regional distribution (donut chart)
- Seasonal readmission patterns (bar chart with season-specific colors)
- Insurance type distribution (funnel chart)

**6. Risk Factors Analysis**
- Comorbidities vs medications scatter plot (bubble size = risk score)
- Risk factor correlation heatmap
- Previous readmissions trend (line + bar combination)

**7. Summary Statistics**
- Age statistics (min, max, median, std dev)
- Length of stay statistics
- Comorbidities statistics
- Medications statistics

### Interactive Features

**All charts support:**
- **Hover**: View detailed information
- **Click**: Filter by category (legend items)
- **Zoom**: Box select or scroll to zoom
- **Pan**: Drag to pan across data
- **Reset**: Double-click to reset view
- **Responsive**: Adapts to screen size

---

### Testing CORS

**Local Testing:**
```bash
# Start backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Start frontend
streamlit run frontend/app.py



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

---

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### 1. Batch Prediction Fails

**Symptoms:**
- "Missing required columns" error
- "Error processing file" message

**Solutions:**
- Ensure file has all 14 required columns
- Check column names match exactly (case-insensitive)
- Verify data types (numbers in numeric columns)
- Remove special characters from categorical values
- Use CSV instead of Excel for large files
- Check file size (max 10,000 rows recommended)

#### 2. Visualizations Not Showing

**Symptoms:**
- Blank charts or missing visualizations
- "Error loading data" messages

**Solutions:**
```bash
# Verify dataset exists
dir data\hospital_readmission_dataset.csv

# Check plotly is installed
pip install plotly

# Verify data structure
python -c "import pandas as pd; df = pd.read_csv('data/hospital_readmission_dataset.csv'); print(df.shape)"

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
