# Streamlit Cloud Deployment Guide

## 🎯 Deployment Options

You have **two options** for deploying on Streamlit Cloud:

### Option 1: Frontend-Only (Embedded Model) ✅ EASIEST
- Deploy only the Streamlit frontend
- Uses embedded ML model (no separate backend needed)
- **Pros**: Simple, one-click deployment
- **Cons**: Limited features (no SHAP, no model reloading)

### Option 2: Full-Stack (Frontend + Backend) 🚀 RECOMMENDED
- Deploy frontend on Streamlit Cloud
- Deploy backend on Railway/Render/Heroku
- Connect them via API_URL
- **Pros**: All features available
- **Cons**: Requires two deployments

---

## 📦 Option 1: Frontend-Only Deployment (Embedded Model)

### Step 1: Prepare Repository

Your repository is already configured for this! The app will automatically detect Streamlit Cloud and use the embedded model.

### Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Set:
   - **Main file path**: `frontend/app.py`
   - **Python version**: 3.9 or higher
5. Click "Deploy"

### Step 3: Verify Deployment

After deployment:
- Sidebar should show "🔵 Embedded Mode"
- All visualizations should work
- Predictions should work (using embedded model)
- EDA and analytics should work

### What Works in Embedded Mode:
- ✅ Data visualizations (Overview page)
- ✅ Predictions (embedded Random Forest model)
- ✅ EDA and analytics
- ✅ Data upload
- ⚠️ Model training (saves locally, doesn't persist)
- ❌ SHAP explanations (requires backend)
- ❌ Model reloading (requires backend)

---

## 🚀 Option 2: Full-Stack Deployment (Recommended)

### Part A: Deploy Backend

#### Option A1: Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Configure:
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: None needed (PORT is auto-set)
5. Deploy and wait for URL (e.g., `https://your-app.railway.app`)

#### Option A2: Render

1. Go to [render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: None needed
5. Deploy and wait for URL (e.g., `https://your-app.onrender.com`)

#### Option A3: Heroku

1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Deploy:
   ```bash
   git push heroku main
   ```
5. Your backend URL: `https://your-app-name.herokuapp.com`

### Part B: Deploy Frontend

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Set:
   - **Main file path**: `frontend/app.py`
   - **Python version**: 3.9 or higher
5. **Before deploying**, add secrets:
   - Click "Advanced settings"
   - Add to secrets:
     ```toml
     API_URL = "https://your-backend-url.railway.app"
     ```
   Replace with your actual backend URL from Part A
6. Click "Deploy"

### Part C: Verify Full-Stack Deployment

After deployment:
- Sidebar should show "🟢 Backend Connected"
- Click "Test Connection" to verify
- All features should work:
  - ✅ Predictions with SHAP explanations
  - ✅ Model training and reloading
  - ✅ All visualizations
  - ✅ Full analytics

---

## 🔧 Configuration Files

### For Streamlit Cloud

**File**: `.streamlit/secrets.toml` (add via Streamlit Cloud UI)
```toml
# Add your backend URL here
API_URL = "https://your-backend-url.railway.app"
```

### For Railway

**File**: `railway.json` (already in repo)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn backend.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### For Heroku

**File**: `Procfile` (already in repo)
```
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

---

## 🧪 Testing Your Deployment

### Test Frontend-Only (Embedded Mode)

1. Open your Streamlit Cloud URL
2. Check sidebar shows "🔵 Embedded Mode"
3. Navigate to "Patient Risk Analysis"
4. Fill in patient details
5. Click "Predict"
6. Should see prediction results

### Test Full-Stack Deployment

1. Open your Streamlit Cloud URL
2. Check sidebar shows "🟢 Backend Connected"
3. Click "Test Connection" button
4. Should see: `{"status": "healthy", "model_loaded": true}`
5. Navigate to "Patient Risk Analysis"
6. Make a prediction
7. Should see SHAP feature importance

---

## 🐛 Troubleshooting

### Issue: "Backend Disconnected" on Streamlit Cloud

**Cause**: Backend URL not configured or backend not deployed

**Solution**:
1. Check if you added `API_URL` to Streamlit secrets
2. Verify backend is deployed and running
3. Test backend URL directly: `https://your-backend-url/health`
4. If backend URL is correct, app will use embedded model as fallback

### Issue: "Module not found" errors

**Cause**: Missing dependencies

**Solution**:
1. Ensure `requirements.txt` includes all packages
2. Check Streamlit Cloud logs for specific missing modules
3. Add missing packages to `requirements.txt`
4. Redeploy

### Issue: Backend works locally but not on deployment

**Cause**: CORS configuration or environment variables

**Solution**:
1. Check backend CORS settings in `backend/main.py`
2. Ensure it allows your Streamlit Cloud domain
3. Check backend logs for errors
4. Verify environment variables are set correctly

### Issue: Predictions work but SHAP doesn't

**Cause**: Running in embedded mode (no backend)

**Solution**:
1. Deploy backend separately (Option 2)
2. Add backend URL to Streamlit secrets
3. Redeploy frontend

---

## 📊 Feature Comparison

| Feature | Embedded Mode | Full-Stack |
|---------|--------------|------------|
| Data Visualizations | ✅ | ✅ |
| Predictions | ✅ | ✅ |
| EDA & Analytics | ✅ | ✅ |
| Data Upload | ✅ | ✅ |
| Model Training | ⚠️ (local only) | ✅ |
| SHAP Explanations | ❌ | ✅ |
| Model Reloading | ❌ | ✅ |
| Backend API | ❌ | ✅ |
| Deployment Complexity | Easy | Medium |
| Cost | Free | Free (with limits) |

---

## 💰 Cost Considerations

### Streamlit Cloud (Frontend)
- **Free tier**: 1 app, unlimited viewers
- **Pro**: $20/month for more apps

### Railway (Backend)
- **Free tier**: $5 credit/month (enough for small apps)
- **Pro**: Pay as you go

### Render (Backend)
- **Free tier**: Available (with limitations)
- **Paid**: Starting at $7/month

### Heroku (Backend)
- **Free tier**: Discontinued
- **Paid**: Starting at $7/month

**Recommendation**: Use Streamlit Cloud (free) + Railway (free tier) for testing

---

## ✅ Deployment Checklist

### For Embedded Mode:
- [ ] Repository pushed to GitHub
- [ ] `requirements.txt` includes all dependencies
- [ ] Model files exist in `models/` directory
- [ ] Deploy to Streamlit Cloud
- [ ] Verify "🔵 Embedded Mode" shows in sidebar
- [ ] Test predictions

### For Full-Stack:
- [ ] Repository pushed to GitHub
- [ ] Backend deployed to Railway/Render/Heroku
- [ ] Backend URL obtained and tested
- [ ] Backend URL added to Streamlit secrets
- [ ] Frontend deployed to Streamlit Cloud
- [ ] Verify "🟢 Backend Connected" shows in sidebar
- [ ] Test connection button works
- [ ] Test predictions with SHAP

---

## 🎉 Success Criteria

### Embedded Mode Success:
- Sidebar shows "🔵 Embedded Mode"
- Predictions work
- Visualizations display
- No errors in logs

### Full-Stack Success:
- Sidebar shows "🟢 Backend Connected"
- Test connection passes
- Predictions include SHAP explanations
- Model training works
- No connection errors

---

## 📞 Support

**Documentation**:
- This guide
- `CONNECTION_FIX_GUIDE.md` - Connection troubleshooting
- `DEPLOYMENT_GUIDE.md` - General deployment guide

**Test Scripts**:
- `test_backend_connection.py` - Test backend locally
- `test_streamlit_connection.py` - Test connection logic

**Quick Commands**:
```bash
# Test backend locally
python test_backend_connection.py

# Test Streamlit connection
python test_streamlit_connection.py

# Start locally
start_app_properly.bat
```

---

**Choose your deployment option and follow the steps above. Good luck! 🚀**
