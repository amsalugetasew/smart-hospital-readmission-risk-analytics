# Backend Connection Fix Guide

## 🔍 Problem

You're seeing these errors in Streamlit:
```
🔄 Reloading backend model (attempt 1/3)...
Connection failed, retrying... (1/3)
🔄 Reloading backend model (attempt 2/3)...
Connection failed, retrying... (2/3)
🔄 Reloading backend model (attempt 3/3)...
❌ Could not connect to backend after 3 attempts
```

## ✅ Solution

The backend IS running and working (we tested it), but Streamlit can't connect to it. Here's how to fix it:

---

## 🚀 Quick Fix (Recommended)

### Option 1: Use the Startup Script

1. **Close all terminals** running backend or frontend
2. **Run the startup script:**
   ```bash
   start_app_properly.bat
   ```
3. This will:
   - Check if backend is running
   - Start backend if needed
   - Wait for backend to initialize
   - Test the connection
   - Start frontend
   - Open browser

### Option 2: Manual Restart

1. **Stop Streamlit** (Ctrl+C in the terminal)
2. **Stop Backend** (Ctrl+C in the backend terminal)
3. **Start Backend first:**
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```
4. **Wait 5 seconds** for backend to fully start
5. **Test backend:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy","model_loaded":true}`
6. **Start Frontend:**
   ```bash
   streamlit run frontend/app.py
   ```
7. **Refresh browser** (Ctrl+F5 to clear cache)

---

## 🔧 Detailed Troubleshooting

### Step 1: Verify Backend is Running

```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000
```

**Expected output:** Should show a process listening on port 8000

**If no output:** Backend is not running. Start it:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Test Backend Connection

```bash
# Test health endpoint
python test_backend_connection.py
```

**Expected output:** All tests should pass ✅

**If tests fail:** 
- Check if backend terminal shows errors
- Check if port 8000 is blocked by firewall
- Try using 127.0.0.1 instead of localhost

### Step 3: Test Streamlit Connection

```bash
# Test connection exactly as Streamlit does
python test_streamlit_connection.py
```

**Expected output:** All tests should pass ✅

**If tests pass but Streamlit still fails:**
- Streamlit is using a cached connection
- Streamlit is using a different Python environment
- Browser cache needs clearing

### Step 4: Clear Streamlit Cache

1. Stop Streamlit (Ctrl+C)
2. Clear Streamlit cache:
   ```bash
   streamlit cache clear
   ```
3. Restart Streamlit:
   ```bash
   streamlit run frontend/app.py
   ```
4. Hard refresh browser (Ctrl+Shift+R or Ctrl+F5)

### Step 5: Check Python Environment

```bash
# Check if requests is installed
python -c "import requests; print(requests.__version__)"
```

**Expected output:** Version number (e.g., 2.31.0)

**If error:** Install requests:
```bash
pip install requests
```

---

## 🧪 Diagnostic Commands

### Test Backend Health
```bash
curl http://localhost:8000/health
```
**Expected:** `{"status":"healthy","model_loaded":true}`

### Test Model Reload
```bash
curl -X POST http://localhost:8000/reload-model
```
**Expected:** `{"status":"success","message":"Models reloaded successfully"}`

### Test Prediction
```bash
python test_backend_connection.py
```
**Expected:** All 4 tests pass

### Full Diagnostic
```bash
python test_streamlit_connection.py
```
**Expected:** All tests pass with retry logic

---

## 🎯 Common Issues and Solutions

### Issue 1: "Connection refused"
**Cause:** Backend is not running
**Solution:** Start backend first, wait 5 seconds, then start frontend

### Issue 2: "Connection timeout"
**Cause:** Backend is slow to respond or firewall blocking
**Solution:** 
- Increase timeout (already done - now 10s for health, 30s for operations)
- Check firewall settings
- Try 127.0.0.1 instead of localhost

### Issue 3: "Backend shows as connected but operations fail"
**Cause:** Streamlit cached old connection state
**Solution:**
- Stop Streamlit
- Run: `streamlit cache clear`
- Restart Streamlit
- Hard refresh browser (Ctrl+Shift+R)

### Issue 4: "Works in Python but not in Streamlit"
**Cause:** Different Python environments
**Solution:**
- Check which Python Streamlit is using: `streamlit --version`
- Ensure requests is installed in that environment
- Use the same terminal/environment for both

### Issue 5: "Backend connected but model reload fails"
**Cause:** Model files not found or corrupted
**Solution:**
- Check if model files exist in `models/` directory
- Retrain the model from Model Training page
- Check backend terminal for error messages

---

## 📊 What We've Improved

### 1. Increased Timeouts
- Health check: 3s → 10s
- Model reload: 10s → 30s
- Predictions: 10s → 30s

### 2. Better Error Messages
- Shows exact error type
- Provides troubleshooting steps
- Shows connection URL being used

### 3. Enhanced Retry Logic
- 3 attempts for all operations
- Progress indicators
- Delays between retries (1-2 seconds)

### 4. Connection Diagnostics
- Test Connection button in sidebar
- Detailed connection troubleshooting
- Real-time connection status

### 5. Startup Script
- Ensures correct startup order
- Tests connection before starting frontend
- Opens browser automatically

---

## ✅ Verification Checklist

After applying the fix:

- [ ] Backend starts without errors
- [ ] `curl http://localhost:8000/health` returns healthy
- [ ] `python test_backend_connection.py` passes all tests
- [ ] `python test_streamlit_connection.py` passes all tests
- [ ] Streamlit sidebar shows "🟢 Backend Connected"
- [ ] Model training completes and reloads backend successfully
- [ ] Predictions work without falling back to embedded model
- [ ] No "Connection failed" messages appear

---

## 🆘 Still Having Issues?

If you've tried everything above and still have connection issues:

1. **Check backend terminal** for error messages
2. **Check Streamlit terminal** for error messages
3. **Try different ports:**
   ```bash
   # Backend on port 8001
   uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
   
   # Update API_URL in frontend/app.py or set environment variable
   set API_URL=http://localhost:8001
   streamlit run frontend/app.py
   ```

4. **Check firewall/antivirus:**
   - Temporarily disable to test
   - Add exceptions for Python and ports 8000, 8501

5. **Try 127.0.0.1 instead of localhost:**
   - Edit `frontend/app.py` line 144:
   ```python
   API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
   ```

6. **Reinstall dependencies:**
   ```bash
   pip uninstall requests
   pip install requests
   ```

---

## 📝 Summary

**The backend IS working** - all our tests confirm this.

**The issue is:** Streamlit needs to be restarted properly to establish the connection.

**The fix:** Use `start_app_properly.bat` or follow the manual restart steps above.

**After the fix:** You should see "🟢 Backend Connected" in the sidebar and all operations should work without retry errors.

---

**Need more help?** Check the diagnostic output from the test scripts and look for specific error messages.
