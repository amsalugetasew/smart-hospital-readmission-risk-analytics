#!/usr/bin/env python3
"""
Startup script to run both backend and frontend together
This allows deployment of the complete application on platforms like Railway, Render, etc.
"""

import subprocess
import threading
import time
import os
import sys

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting Backend Server...")
    try:
        # Change to project root directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Start backend with uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
    except Exception as e:
        print(f"❌ Backend startup failed: {e}")

def start_frontend():
    """Start the Streamlit frontend"""
    print("🎨 Starting Frontend Server...")
    try:
        # Wait for backend to start
        time.sleep(5)
        
        # Change to project root directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Start frontend with streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ])
    except Exception as e:
        print(f"❌ Frontend startup failed: {e}")

def main():
    """Main function to start both services"""
    print("=" * 60)
    print("🏥 SMART HOSPITAL READMISSION RISK ANALYTICS")
    print("🚀 Starting Full-Stack Application...")
    print("=" * 60)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Start frontend in main thread
    start_frontend()

if __name__ == "__main__":
    main()