@echo off
echo ========================================
echo  Smart Hospital Readmission Analytics
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Starting application...
echo.
echo Backend will start on: http://localhost:8000
echo Frontend will start on: http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

echo Starting backend server...
start "Backend Server" cmd /k "venv\Scripts\activate && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Starting frontend server...
venv\Scripts\activate && streamlit run frontend/app.py

pause