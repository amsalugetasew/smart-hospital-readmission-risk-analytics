@echo off
echo ========================================
echo  Restarting Backend Server
echo ========================================
echo.

echo Stopping existing backend processes...
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul
timeout /t 3 /nobreak >nul

echo.
echo Starting backend server...
echo Look for: "GROQ_API_KEY found: Yes"
echo Look for: "LLM Medical Advisor: using Groq API"
echo.
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

pause
