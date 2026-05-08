# How to Change the Embedded Model

## 📁 Where is the Embedded Model?

The embedded model is stored in the **`models/`** directory with 5 files:

```
models/
├── random_forest_model.joblib    ← The trained ML model (MAIN FILE)
├── preprocessor.joblib            ← Data preprocessing pipeline
├── label_encoder.joblib           ← Label encoder
├── feature_names.json             ← Feature names list
└── metrics.json                   ← Model performance metrics
```

**These files are used by:**
- `frontend/embedded_predictor.py` - For frontend-only deployment
- `backend/predictor.py` - For backend API predictions

---

## 🔄 Method 1: Train via Streamlit UI (Easiest)

### Step 1: Start the App Locally
```bash
streamlit run frontend/app.py
```

### Step 2: Navigate to "Model Training" Page
- Click "Model Training" in the sidebar

### Step 3: Choose Your Algorithm
- **Random Forest** (current - best for this dataset)
- **Logistic Regression** (faster, simpler)
- **Decision Tree** (interpretable)
- **XGBoost** (advanced, requires xgboost package)

### Step 4: Configure Parameters (Optional)
For Random Forest:
- **n_estimators**: Number of trees (default: 100)
- **max_depth**: Maximum tree depth (default: 15)
- **min_samples_split**: Min samples to split (default: 5)
- **min_samples_leaf**: Min samples per leaf (default: 2)

### Step 5: Train the Model
1. Click "Train Model" button
2. Wait for training to complete (30-60 seconds)
3. See metrics displayed:
   - Accuracy
   - Precision
   - Recall
   - F1 Score
   - ROC AUC

### Step 6: Verify New Model
- New files are saved to `models/` directory
- Model is automatically reloaded
- Check metrics.json for performance

### Step 7: Deploy to Streamlit Cloud
1. Commit changes to Git:
   ```bash
   git add models/
   git commit -m "Updated model"
   git push
   ```
2. Streamlit Cloud will auto-redeploy with new model

---

## 🔄 Method 2: Train via Python Script

### Step 1: Run Training Script
```bash
python train_model.py
```

This will:
- Load data from `data/hospital_readmission_dataset.csv`
- Preprocess the data
- Train a Random Forest model
- Evaluate performance
- Save all 5 files to `models/` directory

### Step 2: Customize the Script (Optional)

Edit `train_model.py` to change model parameters:

```python
# Change these parameters
rf_model = RandomForestClassifier(
    n_estimators=200,      # More trees (default: 100)
    max_depth=20,          # Deeper trees (default: 15)
    min_samples_split=10,  # More samples needed (default: 5)
    min_samples_leaf=4,    # More samples per leaf (default: 2)
    random_state=42,
    class_weight='balanced',
    n_jobs=-1
)
```

### Step 3: Deploy
```bash
git add models/
git commit -m "Updated model with new parameters"
git push
```

---

## 🔄 Method 3: Use a Different Algorithm

### Option A: Logistic Regression

Create `train_logistic.py`:

```python
from sklearn.linear_model import LogisticRegression
from utils.preprocess import load_data, preprocess_data
import joblib
import json

# Load and preprocess data
df = load_data()
X_train, X_test, y_train, y_test, feature_names, preprocessor = preprocess_data(df)

# Train Logistic Regression
model = LogisticRegression(
    max_iter=1000,
    class_weight='balanced',
    random_state=42
)
model.fit(X_train, y_train)

# Evaluate
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

metrics = {
    "accuracy": float(accuracy_score(y_test, y_pred)),
    "precision": float(precision_score(y_test, y_pred)),
    "recall": float(recall_score(y_test, y_pred)),
    "f1_score": float(f1_score(y_test, y_pred)),
    "roc_auc": float(roc_auc_score(y_test, y_proba))
}

# Save
joblib.dump(model, "models/random_forest_model.joblib")  # Keep same name
joblib.dump(preprocessor, "models/preprocessor.joblib")
with open("models/feature_names.json", "w") as f:
    json.dump(feature_names, f)
with open("models/metrics.json", "w") as f:
    json.dump(metrics, f)

print("Logistic Regression model saved!")
print(f"Accuracy: {metrics['accuracy']:.2%}")
```

Run:
```bash
python train_logistic.py
```

### Option B: XGBoost

First install:
```bash
pip install xgboost
```

Create `train_xgboost.py`:

```python
from xgboost import XGBClassifier
from utils.preprocess import load_data, preprocess_data
import joblib
import json

# Load and preprocess data
df = load_data()
X_train, X_test, y_train, y_test, feature_names, preprocessor = preprocess_data(df)

# Train XGBoost
model = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)
model.fit(X_train, y_train)

# Evaluate and save (same as above)
# ... (same evaluation and saving code)
```

---

## 🔄 Method 4: Use Your Own Custom Model

### Step 1: Train Your Model

```python
import joblib
import json
from utils.preprocess import load_data, preprocess_data

# Load data
df = load_data()
X_train, X_test, y_train, y_test, feature_names, preprocessor = preprocess_data(df)

# Train YOUR model
from your_library import YourModel
model = YourModel(your_parameters)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

# Calculate metrics
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
metrics = {
    "accuracy": float(accuracy_score(y_test, y_pred)),
    "precision": float(precision_score(y_test, y_pred)),
    "recall": float(recall_score(y_test, y_pred)),
    "f1_score": float(f1_score(y_test, y_pred)),
    "roc_auc": float(roc_auc_score(y_test, y_proba))
}

# Save (IMPORTANT: Keep these exact filenames)
joblib.dump(model, "models/random_forest_model.joblib")
joblib.dump(preprocessor, "models/preprocessor.joblib")
with open("models/feature_names.json", "w") as f:
    json.dump(feature_names, f)
with open("models/metrics.json", "w") as f:
    json.dump(metrics, f)

print("Custom model saved!")
```

### Step 2: Update embedded_predictor.py (if needed)

If your model doesn't have `feature_importances_` or `coef_`, update:

**File**: `frontend/embedded_predictor.py`

Find the `predict` method and update the feature importance section:

```python
# Get feature importance (handle different model types)
feature_importance = {}
if hasattr(self.model, 'feature_importances_') and self.feature_names:
    # Tree-based models
    importances = self.model.feature_importances_
    for i, importance in enumerate(importances):
        if i < len(self.feature_names):
            feature_importance[self.feature_names[i]] = float(importance)
elif hasattr(self.model, 'coef_') and self.feature_names:
    # Linear models
    importances = np.abs(self.model.coef_[0])
    for i, importance in enumerate(importances):
        if i < len(self.feature_names):
            feature_importance[self.feature_names[i]] = float(importance)
elif hasattr(self.model, 'your_custom_importance_method'):
    # YOUR CUSTOM MODEL
    importances = self.model.your_custom_importance_method()
    # ... process importances
else:
    # Fallback
    feature_importance = {"Feature importance unavailable": 0.0}
```

---

## 📊 Compare Models

### Step 1: Train Multiple Models

```bash
# Train Random Forest
python train_model.py

# Save metrics
cp models/metrics.json models/metrics_rf.json

# Train Logistic Regression
python train_logistic.py

# Save metrics
cp models/metrics.json models/metrics_lr.json

# Compare
python -c "
import json
with open('models/metrics_rf.json') as f:
    rf = json.load(f)
with open('models/metrics_lr.json') as f:
    lr = json.load(f)
print('Random Forest:', rf['accuracy'])
print('Logistic Regression:', lr['accuracy'])
"
```

### Step 2: Choose Best Model

Keep the model files from the best performing algorithm.

---

## 🚀 Deploy Updated Model

### For Local Development:
1. Train new model (any method above)
2. Restart Streamlit: `streamlit run frontend/app.py`
3. Model is automatically loaded

### For Streamlit Cloud (Embedded Mode):
1. Train new model locally
2. Commit to Git:
   ```bash
   git add models/
   git commit -m "Updated model to [algorithm] with [accuracy]% accuracy"
   git push
   ```
3. Streamlit Cloud auto-redeploys
4. New model is used automatically

### For Full-Stack Deployment:
1. Train new model locally
2. Commit and push to Git
3. Backend auto-redeploys (Railway/Render)
4. Frontend auto-redeploys (Streamlit Cloud)
5. Both use new model

---

## ✅ Verification Checklist

After changing the model:

- [ ] All 5 files exist in `models/` directory
- [ ] `metrics.json` shows new performance metrics
- [ ] Local app loads without errors
- [ ] Predictions work correctly
- [ ] Feature importance displays (if supported)
- [ ] Git committed and pushed
- [ ] Deployment successful
- [ ] Deployed app uses new model

---

## 🔍 Troubleshooting

### "Model not found" error
**Solution**: Ensure all 5 files are in `models/` directory

### "Feature mismatch" error
**Solution**: Retrain preprocessor with the model:
```python
# Always save preprocessor when training
joblib.dump(preprocessor, "models/preprocessor.joblib")
```

### "Feature importance not available"
**Solution**: Your model doesn't support feature importance. Update `embedded_predictor.py` to handle your model type.

### Model performs poorly
**Solution**: 
- Try different algorithms
- Tune hyperparameters
- Check data quality
- Increase training data

---

## 📝 Quick Reference

### Current Model Location:
```
models/random_forest_model.joblib
```

### Train New Model:
```bash
# Via UI
streamlit run frontend/app.py → Model Training page

# Via Script
python train_model.py
```

### Deploy New Model:
```bash
git add models/
git commit -m "Updated model"
git push
```

### Check Model Performance:
```bash
cat models/metrics.json
```

---

## 🎯 Recommended Workflow

1. **Experiment locally** with different algorithms
2. **Compare metrics** (accuracy, precision, recall, F1)
3. **Choose best model** based on your priority (accuracy vs speed)
4. **Test predictions** locally
5. **Commit and push** to Git
6. **Verify deployment** on Streamlit Cloud

---

**Need help?** Check the training script output for detailed metrics and feature importance rankings.
