# ✅ SOLUTION: Fix "LLM advisor not configured" Error

## The Problem
You're seeing this error:
```
INFO: 127.0.0.1:61380 - "POST /llm-advisor/analyze HTTP/1.1" 503 Service Unavailable
```

And the frontend shows: "LLM provider not configured yet"

## Why This Happens
Your backend process (PID 8404) is still running with the **old code** from before we added the .env loading logic. Even though the .env file is correct and the code is correct, the **running process** hasn't been restarted.

## The Solution (3 Steps)

### Step 1: Kill the Old Backend Process

Open a **new terminal** (CMD or PowerShell) and run:

```cmd
taskkill /F /IM python.exe
```

This will kill ALL Python processes. If you have other Python programs running, you can be more specific:

```cmd
taskkill /F /PID 8404
```

### Step 2: Verify Port is Free

```cmd
netstat -ano | findstr :8000
```

If you see any output, there's still a process on port 8000. Kill it:

```cmd
for /f "tokens=5" %a in ('netstat -ano ^| findstr :8000') do taskkill /F /PID %a
```

### Step 3: Start Backend Fresh

Run the automated restart script:

```cmd
FORCE_RESTART_BACKEND.bat
```

Or manually:

```cmd
cd "D:\AI Project\llm\Smart-Hospital-Readmission-Risk-Analytics"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## What You Should See

When the backend starts correctly, you'll see this output:

```
================================================================================
BACKEND STARTING - Loading environment variables...
================================================================================
Loading .env from: D:\AI Project\llm\Smart-Hospital-Readmission-Risk-Analytics\.env
load_dotenv() result: True
GROQ_API_KEY found: Yes
GROQ_API_KEY value: gsk_KrvX4ItPRpVZgjkS...
================================================================================
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
============================================================
Starting LLM Medical Advisor initialization...
============================================================
INFO:backend.llm_advisor:load_model() called - checking environment variables...
INFO:backend.llm_advisor:Environment check: GROQ_API_KEY=found
INFO:backend.llm_advisor:LLM Medical Advisor: using Groq API (model=llama-3.3-70b-versatile)
INFO:backend.llm_advisor:LLM Advisor Status: mode=groq, available=True
============================================================
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Key success indicators:**
- ✅ `GROQ_API_KEY found: Yes`
- ✅ `Environment check: GROQ_API_KEY=found`
- ✅ `LLM Medical Advisor: using Groq API`
- ✅ `mode=groq, available=True`

## Verify It's Working

### Test 1: Check API Status

Open a new terminal and run:

```cmd
python test_backend_api.py
```

Expected output:
```
✅ Root endpoint working
✅ LLM advisor status endpoint working
   Mode: groq
   Model Name: llama-3.3-70b-versatile
   Available: True
✅ LLM advisor is properly configured!
✅ ALL TESTS PASSED
```

### Test 2: Check Frontend

1. Refresh your Streamlit app (press R in the browser)
2. Navigate to: **Prediction** → **Readmission Prediction** → **🤖 LLM Medical Advisor** tab
3. You should see at the top:
   ```
   ✅ Provider: ☁️ Groq API — llama-3.3-70b-versatile
   ```
4. Enter some clinical notes and click "Analyze"
5. You should get a response with admission recommendation

## If It Still Doesn't Work

### Check 1: Is .env in the right place?

```cmd
dir .env
```

Should show:
```
D:\AI Project\llm\Smart-Hospital-Readmission-Risk-Analytics\.env
```

### Check 2: Does .env have the API key?

```cmd
type .env | findstr GROQ_API_KEY
```

Should show:
```
GROQ_API_KEY=your_actual_api_key_here
```

### Check 3: Is python-dotenv installed?

```cmd
pip show python-dotenv
```

Should show version 1.0.1 or similar.

### Check 4: Test environment loading

```cmd
python test_env.py
```

Should show:
```
✅ GROQ_API_KEY: gsk_KrvX4ItPRpVZgjkS... (length: 56)
After load_model():
   Mode: groq
   Model available: True
   Model name: llama-3.3-70b-versatile
```

## Common Mistakes

| Mistake | Solution |
|---------|----------|
| Edited .env but didn't restart backend | Kill Python process and restart |
| Backend started from wrong directory | Must start from project root |
| Multiple Python processes running | Kill all: `taskkill /F /IM python.exe` |
| Using old terminal with old environment | Open fresh terminal |
| .env file in wrong location | Must be in project root, not in backend/ |

## Quick Command Reference

```cmd
# Kill all Python processes
taskkill /F /IM python.exe

# Check if port 8000 is in use
netstat -ano | findstr :8000

# Start backend
cd "D:\AI Project\llm\Smart-Hospital-Readmission-Risk-Analytics"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Test backend
python test_backend_api.py

# Test environment loading
python test_env.py
```

## Summary

The code is correct. The .env file is correct. You just need to:

1. **Kill the old backend process** (it's still running with old code)
2. **Start a fresh backend process** (it will load the .env file correctly)
3. **Verify it works** (check console output and test with test_backend_api.py)

That's it! The issue is simply that the running process needs to be restarted.
