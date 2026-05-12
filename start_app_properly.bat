@echo off
setlocal enabledelayedexpansion

echo ========================================
echo  Smart Hospital Readmission Risk Analytics
echo  + LLM Medical Advisor
echo ========================================
echo.

:: ── Detect Python ────────────────────────────────────────────────────────────
set PYTHON=
where py >nul 2>&1 && set PYTHON=py
if "!PYTHON!"=="" (
    where python >nul 2>&1 && set PYTHON=python
)
if "!PYTHON!"=="" (
    where python3 >nul 2>&1 && set PYTHON=python3
)
if "!PYTHON!"=="" (
    echo [ERROR] Python not found. Install Python 3.9+ and try again.
    pause
    exit /b 1
)
echo [OK] Using Python: !PYTHON!
echo.

:: ── Kill any existing processes on ports 8000 / 8501 ─────────────────────────
echo [1/4] Clearing ports 8000 and 8501...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 " 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8501 " 2^>nul') do (
    taskkill /PID %%a /F >nul 2>&1
)
echo [OK] Ports cleared.
echo.

:: ── Start Backend ─────────────────────────────────────────────────────────────
echo [2/4] Starting Backend (FastAPI on port 8000)...
start "Backend - FastAPI" cmd /k "title Backend - FastAPI && echo Starting backend... && !PYTHON! -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
echo [OK] Backend window opened.
echo      Waiting 6 seconds for backend to initialise...
timeout /t 6 /nobreak >nul
echo.

:: ── Health check ──────────────────────────────────────────────────────────────
echo [3/4] Checking backend health...
!PYTHON! -c "import requests; r=requests.get('http://localhost:8000/health',timeout=8); print('[OK] Backend healthy:', r.json())" 2>nul
if !errorlevel! neq 0 (
    echo [WARN] Backend health check failed - it may still be starting.
    echo        Check the Backend window for errors.
)
echo.

:: ── Start Frontend ────────────────────────────────────────────────────────────
echo [4/4] Starting Frontend (Streamlit on port 8501)...
start "Frontend - Streamlit" cmd /k "title Frontend - Streamlit && echo Starting Streamlit... && !PYTHON! -m streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0"
echo [OK] Frontend window opened.
echo      Waiting 4 seconds then opening browser...
timeout /t 4 /nobreak >nul
echo.

:: ── Open browser ─────────────────────────────────────────────────────────────
start http://localhost:8501

echo ========================================
echo  Application is running!
echo ========================================
echo.
echo   Frontend  : http://localhost:8501
echo   Backend   : http://localhost:8000
echo   API Docs  : http://localhost:8000/docs
echo.
echo   Navigate to "LLM Medical Advisor" in the sidebar
echo   to access the AI clinical advisor feature.
echo.
echo   NOTE: LLM inference requires LLM_MODEL_PATH to be
echo   set in your .env file pointing to a GGUF model.
echo   Without it, all other features work normally.
echo.
echo   Close the Backend and Frontend windows to stop.
echo ========================================
echo.
pause
