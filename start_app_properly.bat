@echo off
echo ========================================
echo Smart Hospital Readmission Risk Analytics
echo ========================================
echo.

echo [1/4] Checking if backend is already running...
netstat -ano | findstr :8000 > nul
if %errorlevel% == 0 (
    echo ✅ Backend is already running on port 8000
) else (
    echo ⚠️ Backend is not running. Starting backend...
    echo.
    start "Backend Server" cmd /k "echo Starting Backend Server... && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
    echo ✅ Backend server started in new window
    echo ⏳ Waiting 5 seconds for backend to initialize...
    timeout /t 5 /nobreak > nul
)

echo.
echo [2/4] Testing backend connection...
python -c "import requests; r = requests.get('http://localhost:8000/health', timeout=5); print('✅ Backend is healthy:', r.json())" 2>nul
if %errorlevel% == 0 (
    echo ✅ Backend connection successful
) else (
    echo ❌ Backend connection failed
    echo    Please check the backend window for errors
    pause
    exit /b 1
)

echo.
echo [3/4] Checking if frontend is already running...
netstat -ano | findstr :8501 > nul
if %errorlevel% == 0 (
    echo ⚠️ Frontend is already running on port 8501
    echo    Please close it first or use the existing instance
) else (
    echo Starting frontend...
    echo.
    start "Frontend (Streamlit)" cmd /k "echo Starting Streamlit Frontend... && streamlit run frontend/app.py"
    echo ✅ Frontend started in new window
)

echo.
echo [4/4] Opening browser...
timeout /t 3 /nobreak > nul
start http://localhost:8501

echo.
echo ========================================
echo ✅ Application started successfully!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8501
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to close this window...
pause > nul
