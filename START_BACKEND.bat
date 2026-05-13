@echo off
cls
echo ================================================================================
echo  STARTING BACKEND WITH VIRTUAL ENVIRONMENT
echo ================================================================================
echo.

echo [1/3] Killing existing Python processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
echo Done.
echo.

echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat
echo Done.
echo.

echo [3/3] Starting backend server...
echo.
echo ================================================================================
echo  WATCH FOR SUCCESS INDICATORS:
echo  ✓ "GROQ_API_KEY found: Yes"
echo  ✓ "Environment check: GROQ_API_KEY=found"
echo  ✓ "LLM Medical Advisor: using Groq API"
echo  ✓ "mode=groq, available=True"
echo ================================================================================
echo.

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo Backend stopped.
pause
