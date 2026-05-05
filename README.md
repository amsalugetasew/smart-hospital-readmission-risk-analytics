# Smart Hospital Readmission & Risk Analytics

This is a full-stack AI-powered healthcare analytics platform that predicts patient hospital readmission risk and provides explainable insights through an interactive dashboard.

## Project Structure
- `backend/`: FastAPI application handling ML model inference and data serving.
- `frontend/`: Streamlit dashboard for visualizations and interaction.
- `models/`: Pre-trained Random Forest model, preprocessing pipeline, and metrics.
- `utils/`: Data generation and preprocessing scripts.
- `data/`: Synthetically generated hospital patient data.

## Features
1. **Prediction API**: Predicts whether a patient is likely to be readmitted after discharge and provides a probability score and risk category.
2. **Explainable AI**: Utilizes SHAP values to explain which features contributed the most to the prediction.
3. **Analytics Dashboard**: Interactive Streamlit dashboard to monitor KPIs, readmission trends, and model performance.

## Installation and Running Locally

### Option 1: Docker
```bash
docker build -t smart-hospital .
docker run -p 8000:8000 -p 8501:8501 smart-hospital
```
The FastAPI backend will be available at `http://localhost:8000` and the Streamlit dashboard at `http://localhost:8501`.

### Option 2: Python Virtual Environment
1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the FastAPI Backend:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
4. Run the Streamlit Frontend (in a new terminal):
```bash
streamlit run frontend/app.py
```

## Setup Data & Model (If starting from scratch)
1. Generate data: `python utils/generate_data.py`
2. Train model: `python train_model.py`
