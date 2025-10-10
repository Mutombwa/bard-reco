@echo off
REM Quick Start Script for BARD-RECO on Windows
REM ============================================

echo.
echo ========================================
echo    BARD-RECO - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from python.org
    pause
    exit /b 1
)

echo [1/3] Checking Python installation...
python --version

echo.
echo [2/3] Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [3/3] Starting BARD-RECO...
echo.
echo ========================================
echo    Application starting...
echo    Default login: admin / admin123
echo    URL: http://localhost:8501
echo ========================================
echo.

streamlit run app.py

pause
