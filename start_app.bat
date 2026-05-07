@echo off
echo ========================================
echo Smart Hospital Readmission Risk Analytics
echo ========================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
    echo Using system Python...
)

echo.
echo Checking dependencies...
pip install -r requirements.txt --quiet

echo.
echo Testing model...
python test_model.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo ERROR: Model test failed!
    echo Please train the model first.
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting Backend Server...
echo ========================================
start "Backend API" cmd /k "uvicorn backend.main:app --host 0.0.0.0 --port 8000"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo ========================================
echo Starting Frontend Application...
echo ========================================
start "Frontend App" cmd /k "streamlit run frontend/app.py"

echo.
echo ========================================
echo Application started successfully!
echo ========================================
echo Backend API: http://127.0.0.1:8000
echo Frontend: http://localhost:8501
echo.
echo Press any key to stop all services...
pause > nul

echo Stopping services...
taskkill /FI "WindowTitle eq Backend API*" /T /F
taskkill /FI "WindowTitle eq Frontend App*" /T /F
