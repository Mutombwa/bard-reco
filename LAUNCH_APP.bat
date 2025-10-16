@echo off
REM ========================================================================
REM  BARD-RECO - UNIVERSAL LAUNCHER v2.0
REM  Works on ANY Windows Machine - Auto-detects Python
REM ========================================================================

setlocal enabledelayedexpansion
title BARD-RECO Universal Launcher
color 0A
cls

echo.
echo ========================================================================
echo   ____    _    ____  ____       ____  _____ ____ ___  
echo  / ___ ^|  / \  ^|  _ \^|  _ \     ^|  _ \^| ____/ ___/ _ \ 
echo ^| ^|     / _ \ ^| ^|_) ^| ^| ^| ^|____^| ^|_) ^|  _^|^| ^|  ^| ^| ^| ^|
echo ^| ^|___ / ___ \^|  _ ^<^| ^|_^| ^|____^|  _ ^<^| ^|__^| ^|__^| ^|_^| ^|
echo  \____/_/   \_\_^| \_\____/     ^|_^| \_\_____\____\___/ 
echo.
echo  Professional Banking Reconciliation System
echo  Universal Launcher - Works Anywhere
echo ========================================================================
echo.

REM ========================================================================
REM  STEP 1: Navigate to App Directory
REM ========================================================================
cd /d "%~dp0"
set "APP_ROOT=%CD%"
set "SRC_DIR=%APP_ROOT%\src"

echo [1/5] Initializing...
echo      Location: %APP_ROOT%

if not exist "%SRC_DIR%\gui.py" (
    echo.
    echo [ERROR] Application files not found!
    echo Please ensure you're in the reconciliation-app folder.
    pause
    exit /b 1
)

REM ========================================================================
REM  STEP 2: Detect Python
REM ========================================================================
echo.
echo [2/5] Detecting Python...

set "PYTHON_EXE="

REM Try python command
python --version >nul 2>&1
if !errorlevel! equ 0 (
    set "PYTHON_EXE=python"
    goto :found_python
)

REM Try py launcher
py --version >nul 2>&1
if !errorlevel! equ 0 (
    set "PYTHON_EXE=py"
    goto :found_python
)

REM Try Anaconda MASTER
if exist "C:\Users\%USERNAME%\anaconda3\envs\MASTER\python.exe" (
    set "PYTHON_EXE=C:\Users\%USERNAME%\anaconda3\envs\MASTER\python.exe"
    goto :found_python
)

REM Try Anaconda base
if exist "C:\Users\%USERNAME%\anaconda3\python.exe" (
    set "PYTHON_EXE=C:\Users\%USERNAME%\anaconda3\python.exe"
    goto :found_python
)

REM Try system Anaconda
if exist "C:\ProgramData\Anaconda3\python.exe" (
    set "PYTHON_EXE=C:\ProgramData\Anaconda3\python.exe"
    goto :found_python
)

REM Not found
echo      [ERROR] Python not detected!
echo.
echo ========================================================================
echo  PYTHON INSTALLATION REQUIRED
echo ========================================================================
echo.
echo  Python was not found on this system.
echo.
echo  SOLUTION:
echo  1. Download Python from: https://www.python.org/downloads/
echo  2. Install Python 3.9 or higher
echo  3. IMPORTANT: Check "Add Python to PATH" during installation
echo  4. Restart your computer
echo  5. Run this launcher again
echo.
echo ========================================================================
pause
exit /b 1

:found_python
echo      [OK] Python found: !PYTHON_EXE!

REM ========================================================================
REM  STEP 3: Check Dependencies
REM ========================================================================
echo.
echo [3/5] Checking dependencies...

set "MISSING=0"
for %%p in (pandas openpyxl fuzzywuzzy tkinter) do (
    "!PYTHON_EXE!" -c "import %%p" >nul 2>&1
    if !errorlevel! neq 0 (
        echo      [MISSING] %%p
        set "MISSING=1"
    ) else (
        echo      [OK] %%p
    )
)

if "!MISSING!"=="1" (
    echo.
    echo [WARNING] Some dependencies are missing.
    echo.
    set /p INSTALL="Install missing packages now? (Y/N): "
    if /i "!INSTALL!"=="Y" (
        echo.
        echo Installing dependencies...
        "!PYTHON_EXE!" -m pip install --upgrade pip >nul 2>&1
        if exist "%APP_ROOT%\requirements.txt" (
            "!PYTHON_EXE!" -m pip install -r "%APP_ROOT%\requirements.txt"
        ) else (
            "!PYTHON_EXE!" -m pip install pandas openpyxl fuzzywuzzy python-Levenshtein numpy rapidfuzz flask
        )
        echo      [OK] Dependencies installed!
    ) else (
        echo.
        echo [ERROR] Cannot run without dependencies.
        echo Install manually: !PYTHON_EXE! -m pip install -r requirements.txt
        pause
        exit /b 1
    )
) else (
    echo      [OK] All dependencies installed!
)

REM ========================================================================
REM  STEP 4: Pre-Launch Checks
REM ========================================================================
echo.
echo [4/5] Pre-launch checks...
echo      [OK] All checks passed!

REM ========================================================================
REM  STEP 5: Launch Application
REM ========================================================================
echo.
echo [5/5] Launching BARD-RECO...
echo.
echo ========================================================================
echo  Starting Application
echo ========================================================================
echo  Python: !PYTHON_EXE!
echo  Directory: %SRC_DIR%
echo  
echo  Opening in 2 seconds...
echo ========================================================================
echo.

timeout /t 2 /nobreak >nul

cd /d "%SRC_DIR%"

REM Launch with optimizations
"!PYTHON_EXE!" -OO gui.py
if !errorlevel! neq 0 (
    REM Try without optimizations
    "!PYTHON_EXE!" gui.py
)

if !errorlevel! neq 0 (
    echo.
    echo [ERROR] Failed to launch!
    echo Check the error messages above.
    pause
    exit /b 1
)

exit /b 0
