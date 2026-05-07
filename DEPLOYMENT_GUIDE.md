# 🚀 Complete Deployment Guide

## Overview

This guide shows how to deploy both the frontend (Streamlit) and backend (FastAPI) components of the Smart Hospital Readmission Risk Analytics platform.

---

## 🎯 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT CLOUD                           │
│                  (Frontend Dashboard)                        │
│                https://your-app.streamlit.app               │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS API Calls
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      RAILWAY                                 │
│                   (Backend API)                              │
│              https://your-app.railway.app                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

1. **GitHub Account** - To store your code
2. **Railway Account** - For backend deployment (free tier available)
3. **Streamlit Cloud Account** - For frontend deployment (free)

---

## 🔧 Step 1: Deploy Backend to Railway

### 1.1 Prepare Your Repository

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

### 1.2 Deploy to Railway

1. **Go to [Railway.app](https://railway.app)**
2. **Sign up/Login** with GitHub
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your repository**
6. **Railway will automatically detect it's a Python project**

### 1.3 Configure Railway Environment

1. **In Railway dashboard, go to your project**
2. **Click on "Variables" tab**
3. **Add these environment variables:**
   ```
   PORT=8000
   PYTHONPATH=/app
   ```

### 1.4 Configure Build Settings

Railway should automatically use the `Procfile`, but if needed:

1. **Go to "Settings" tab**
2. **In "Build" section, set:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python train_model.py && uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### 1.5 Get Your Backend URL

1. **After deployment, Railway will provide a URL like:**
   ```
   https://your-app-name.railway.app
   ```
2. **Test it by visiting:**
   ```
   https://your-app-name.railway.app/health
   ```
3. **Should return:** `{"status": "healthy", "model_loaded": true}`

---

## 🎨 Step 2: Deploy Frontend to Streamlit Cloud

### 2.1 Update Streamlit Secrets

1. **Create `.streamlit/secrets.toml` (already created):**
   ```toml
   # Replace with your actual Railway URL
   API_URL = "https://your-app-name.railway.app"
   ```

### 2.2 Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign up/Login** with GitHub
3. **Click "New app"**
4. **Fill in the details:**
   - **Repository:** `your-username/Smart-Hospital-Readmission-Risk-Analytics`
   - **Branch:** `main`
   - **Main file path:** `frontend/app.py`
   - **App URL:** Choose a custom URL (optional)

### 2.3 Configure Streamlit Secrets

1. **In Streamlit Cloud dashboard:**
2. **Go to "Settings" → "Secrets"**
3. **Add your Railway backend URL:**
   ```toml
   API_URL = "https://your-app-name.railway.app"
   ```

### 2.4 Advanced Settings (if needed)

1. **Python version:** 3.10
2. **Requirements file:** `requirements.txt`
3. **Packages file:** `packages.txt` (for system dependencies)

---

## ✅ Step 3: Verify Deployment

### 3.1 Test Backend

1. **Visit your Railway URL:**
   ```
   https://your-app-name.railway.app
   ```

2. **Test API endpoints:**
   - **Health:** `https://your-app-name.railway.app/health`
   - **API Docs:** `https://your-app-name.railway.app/docs`

### 3.2 Test Frontend

1. **Visit your Streamlit app:**
   ```
   https://your-app.streamlit.app
   ```

2. **Test all pages:**
   - ✅ Overview (should show analytics)
   - ✅ EDA (should show charts)
   - ✅ Patient Risk Analysis (should make predictions)
   - ✅ Analytics Dashboard (should show data)

### 3.3 Test Integration

1. **Go to "Patient Risk Analysis" page**
2. **Fill in patient data**
3. **Click "Predict Readmission Risk"**
4. **Should see prediction results**

---

## 🔧 Alternative Deployment Options

### Option 2: Render (Alternative to Railway)

1. **Go to [render.com](https://render.com)**
2. **Create Web Service**
3. **Connect GitHub repository**
4. **Use these settings:**
   - **Build Command:** `pip install -r requirements.txt && python train_model.py`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Option 3: Heroku

1. **Install Heroku CLI**
2. **Create Heroku app:**
   ```bash
   heroku create your-app-name
   ```
3. **Deploy:**
   ```bash
   git push heroku main
   ```

### Option 4: Docker (Any Platform)

1. **Build Docker image:**
   ```bash
   docker build -t hospital-analytics .
   ```

2. **Run locally:**
   ```bash
   docker run -p 8000:8000 -p 8501:8501 hospital-analytics
   ```

3. **Deploy to any Docker platform** (AWS ECS, Google Cloud Run, etc.)

---

## 🛠️ Troubleshooting Deployment

### Backend Issues

**Problem:** Model not loading
```bash
# Check Railway logs
railway logs
```
**Solution:** Ensure `train_model.py` runs successfully during build

**Problem:** CORS errors
**Solution:** Backend is configured for Streamlit Cloud domains

**Problem:** 503 errors
**Solution:** Check if model files are created during deployment

### Frontend Issues

**Problem:** "Cannot connect to backend"
**Solution:** Check API_URL in Streamlit secrets

**Problem:** Import errors
**Solution:** Ensure all dependencies are in `requirements.txt`

**Problem:** File not found errors
**Solution:** Check file paths are relative to project root

---

## 📊 Monitoring & Maintenance

### Railway Monitoring

1. **Check logs:** Railway dashboard → Logs
2. **Monitor usage:** Railway dashboard → Metrics
3. **Set up alerts:** Railway dashboard → Settings

### Streamlit Monitoring

1. **Check app status:** Streamlit Cloud dashboard
2. **View logs:** Streamlit Cloud → App → Logs
3. **Monitor usage:** Streamlit Cloud → Analytics

### Updates

1. **Push to GitHub:** Changes auto-deploy to both platforms
2. **Railway:** Auto-deploys on git push
3. **Streamlit:** Auto-deploys on git push

---

## 💰 Cost Considerations

### Railway (Backend)
- **Free Tier:** $5 credit/month (usually sufficient)
- **Pro Plan:** $20/month for production apps

### Streamlit Cloud (Frontend)
- **Community:** Free (public repos)
- **Teams:** $20/user/month (private repos)

### Total Cost
- **Development/Demo:** Free
- **Production:** ~$20-40/month

---

## 🔒 Security Considerations

### Production Checklist

- [ ] Use HTTPS for all communications
- [ ] Set proper CORS origins (not "*")
- [ ] Add authentication if needed
- [ ] Monitor API usage
- [ ] Set up proper logging
- [ ] Use environment variables for secrets
- [ ] Regular security updates

---

## 📝 Quick Commands

```bash
# Test backend locally
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Test frontend locally
streamlit run frontend/app.py

# Deploy to Railway (after setup)
git push origin main

# Check Railway logs
railway logs

# Test deployed backend
curl https://your-app.railway.app/health

# Test deployed API
curl -X POST https://your-app.railway.app/predict \
  -H "Content-Type: application/json" \
  -d '{"season":"Spring","age":65,"gender":"Male",...}'
```

---

## 🎉 Success!

After following this guide, you'll have:

✅ **Backend API** running on Railway  
✅ **Frontend Dashboard** running on Streamlit Cloud  
✅ **Full integration** between both components  
✅ **Public URLs** for sharing your application  
✅ **Automatic deployments** on code changes  

Your Smart Hospital Readmission Risk Analytics platform is now live! 🚀