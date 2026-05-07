@echo off
echo ========================================
echo Starting Backend Server with Auto-Reload
echo ========================================
echo.
echo This will start the backend server with auto-reload enabled.
echo The server will automatically restart when you make code changes.
echo.
echo Press Ctrl+C to stop the server when needed.
echo.
echo ========================================
echo.

uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
