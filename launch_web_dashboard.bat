@echo off
REM 🌐 BARD-RECO - Web Dashboard Launcher
echo.
echo ================================
echo  BARD-RECO Web Dashboard
echo ================================
echo.
echo Starting web dashboard server...
echo.

cd /d "%~dp0"
start "BARD-RECO Dashboard" C:\Users\Tatenda\anaconda3\envs\MASTER\python.exe web_dashboard_server.py

echo.
echo ✅ Dashboard server starting...
echo 🌐 Opening http://127.0.0.1:5000 in your browser
echo.
echo Press any key to close this window...
pause >nul
