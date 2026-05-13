@echo off
cls
echo ================================================================================
echo  RESTARTING BACKEND WITH DEBUG OUTPUT
echo ================================================================================
echo.

echo [1/4] Stopping existing backend processes...
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul
echo Done.
echo.

echo [2/4] Waiting 3 seconds...
timeout /t 3 /nobreak >nul
echo Done.
echo.

echo [3/4] Starting backend server with debug output...
echo.
echo ================================================================================
echo  LOOK FOR THESE SUCCESS MESSAGES:
echo  - "GROQ_API_KEY found: Yes"
echo  - "Environment check: GROQ_API_KEY=found"
echo  - "LLM Medical Advisor: using Groq API"
echo  - "mode=groq, available=True"
echo ================================================================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting backend with venv Python...
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo [4/4] Backend stopped.
pause
