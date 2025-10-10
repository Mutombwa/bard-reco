@echo off
REM ========================================================================
REM  BARD-RECO - UNIVERSAL PORTABLE LAUNCHER
REM  Ultra-Fast Launch for Any Machine - No Configuration Required
REM ========================================================================
REM  Version: 2.0
REM  Date: October 9, 2025
REM  Features:
REM    - Auto-detects Python installation
REM    - Checks and installs missing dependencies
REM    - Works on any Windows machine
REM    - No hardcoded paths
REM    - Intelligent error handling
REM ========================================================================

title BARD-RECO - Universal Launcher
color 0A
cls

echo.
echo ========================================================================
echo   ____    _    ____  ____       ____  _____ ____ ___  
echo  / ___|  / \  ^|  _ \^|  _ \     ^|  _ \^| ____/ ___/ _ \ 
echo ^| ^|     / _ \ ^| ^|_) ^| ^| ^| ^|____^| ^|_) ^|  _^|^| ^|  ^| ^| ^| ^|
echo ^| ^|___ / ___ \^|  _ ^<^| ^|_^| ^|____^|  _ ^<^| ^|__^| ^|__^| ^|_^| ^|
echo  \____/_/   \_\_^| \_\____/     ^|_^| \_\_____\____\___/ 
echo.
echo  Professional Banking Reconciliation System
echo  Universal Portable Launcher - Works Anywhere
echo ========================================================================
echo.

REM ========================================================================
REM  STEP 1: Navigate to App Directory
REM ========================================================================
cd /d "%~dp0"
set "APP_ROOT=%CD%"
set "SRC_DIR=%APP_ROOT%\src"

echo [1/5] Initializing application...
echo      App Root: %APP_ROOT%
if not exist "%SRC_DIR%" (
    echo.
    echo [ERROR] Source directory not found: %SRC_DIR%
    echo Please ensure you're running this from the reconciliation-app folder.
    pause
    exit /b 1
)

REM ========================================================================
REM  STEP 2: Detect Python Installation
REM ========================================================================
echo.
echo [2/5] Detecting Python installation...

set "PYTHON_CMD="
set "PYTHON_VERSION="

REM Check 1: Try python command (most common)
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    for /f "tokens=2" %%v in ('python --version 2^>^&^1') do set "PYTHON_VERSION=%%v"
    goto :python_found
)

REM Check 2: Try python3 command
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python3"
    for /f "tokens=2" %%v in ('python3 --version 2^>^&^1') do set "PYTHON_VERSION=%%v"
    goto :python_found
)

REM Check 3: Try py launcher (Windows Python Launcher)
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
    for /f "tokens=2" %%v in ('py --version 2^>^&^1') do set "PYTHON_VERSION=%%v"
    goto :python_found
)

REM Check 4: Try common Anaconda locations
if exist "C:\Users\%USERNAME%\anaconda3\python.exe" (
    set "PYTHON_CMD=C:\Users\%USERNAME%\anaconda3\python.exe"
    for /f "tokens=2" %%v in ('"C:\Users\%USERNAME%\anaconda3\python.exe" --version 2^>^&^1') do set "PYTHON_VERSION=%%v"
    goto :python_found
)

if exist "C:\ProgramData\Anaconda3\python.exe" (
    set "PYTHON_CMD=C:\ProgramData\Anaconda3\python.exe"
    for /f "tokens=2" %%v in ('"C:\ProgramData\Anaconda3\python.exe" --version 2^>^&^1') do set "PYTHON_VERSION=%%v"
    goto :python_found
)

REM Check 5: Try Anaconda MASTER environment
if exist "C:\Users\%USERNAME%\anaconda3\envs\MASTER\python.exe" (
    set "PYTHON_CMD=C:\Users\%USERNAME%\anaconda3\envs\MASTER\python.exe"
    for /f "tokens=2" %%v in ('"C:\Users\%USERNAME%\anaconda3\envs\MASTER\python.exe" --version 2^>^&^1') do set "PYTHON_VERSION=%%v"
    goto :python_found
)

REM Check 6: Search PATH for python.exe
for %%p in (python.exe) do (
    if exist "%%~$PATH:p" (
        set "PYTHON_CMD=%%~$PATH:p"
        for /f "tokens=2" %%v in ('"%%~$PATH:p" --version 2^>^&^1') do set "PYTHON_VERSION=%%v"
        goto :python_found
    )
)

REM Python not found - show error with instructions
echo.
echo ========================================================================
echo [ERROR] Python Not Found!
echo ========================================================================
echo.
echo Python is required to run BARD-RECO but was not detected on this system.
echo.
echo SOLUTIONS:
echo.
echo 1. Install Python from python.org:
echo    https://www.python.org/downloads/
echo    (Recommended: Python 3.9 or higher)
echo    IMPORTANT: Check "Add Python to PATH" during installation!
echo.
echo 2. If Python is installed but not detected:
echo    - Restart your computer
echo    - Reinstall Python with "Add to PATH" option
echo    - Or manually add Python to your system PATH
echo.
echo 3. If using Anaconda:
echo    - Open Anaconda Prompt
echo    - Navigate to: %APP_ROOT%
echo    - Run: conda activate base
echo    - Run: python src\gui.py
echo.
echo ========================================================================
pause
exit /b 1

:python_found
echo      Python Found: %PYTHON_CMD%
echo      Version: %PYTHON_VERSION%

REM ========================================================================
REM  STEP 3: Check Required Dependencies
REM ========================================================================
echo.
echo [3/5] Checking dependencies...

set "MISSING_DEPS=0"
set "DEPS_LIST="

REM Check each required package
for %%p in (pandas openpyxl fuzzywuzzy numpy rapidfuzz flask tkinter) do (
    echo      Checking %%p...
    "%PYTHON_CMD%" -c "import %%p" >nul 2>&1
    if errorlevel 1 (
        set "MISSING_DEPS=1"
        set "DEPS_LIST=!DEPS_LIST! %%p"
        echo        [MISSING] %%p
    ) else (
        echo        [OK] %%p
    )
)

REM If dependencies are missing, offer to install
if "%MISSING_DEPS%"=="1" (
    echo.
    echo ========================================================================
    echo [WARNING] Missing Dependencies Detected
    echo ========================================================================
    echo.
    echo The following packages are required but not installed:
    echo %DEPS_LIST%
    echo.
    set /p INSTALL_DEPS="Would you like to install missing packages now? (Y/N): "
    if /i "%INSTALL_DEPS%"=="Y" (
        echo.
        echo [4/5] Installing dependencies...
        echo      This may take a few minutes...
        
        REM Check if requirements.txt exists
        if exist "%APP_ROOT%\requirements.txt" (
            echo      Installing from requirements.txt...
            "%PYTHON_CMD%" -m pip install --upgrade pip
            "%PYTHON_CMD%" -m pip install -r "%APP_ROOT%\requirements.txt"
            
            if errorlevel 1 (
                echo.
                echo [ERROR] Failed to install dependencies automatically.
                echo.
                echo Please install manually using:
                echo %PYTHON_CMD% -m pip install pandas openpyxl fuzzywuzzy python-Levenshtein numpy rapidfuzz flask flask-socketio eventlet psutil xlsxwriter pillow
                echo.
                pause
                exit /b 1
            )
        ) else (
            echo      Installing individual packages...
            "%PYTHON_CMD%" -m pip install pandas openpyxl fuzzywuzzy python-Levenshtein numpy rapidfuzz flask flask-socketio eventlet psutil xlsxwriter pillow
        )
        
        echo      [SUCCESS] All dependencies installed!
    ) else (
        echo.
        echo [ERROR] Cannot run application without required dependencies.
        echo.
        echo Please install them manually using:
        echo %PYTHON_CMD% -m pip install -r requirements.txt
        echo.
        echo Or install individually:
        echo %PYTHON_CMD% -m pip install pandas openpyxl fuzzywuzzy python-Levenshtein numpy rapidfuzz flask
        echo.
        pause
        exit /b 1
    )
) else (
    echo      [SUCCESS] All dependencies are installed!
)

REM ========================================================================
REM  STEP 4: Final Pre-Launch Checks
REM ========================================================================
echo.
echo [4/5] Performing pre-launch checks...

REM Verify gui.py exists
if not exist "%SRC_DIR%\gui.py" (
    echo.
    echo [ERROR] Main application file not found: %SRC_DIR%\gui.py
    echo Please ensure all application files are present.
    pause
    exit /b 1
)
echo      [OK] Application files verified

REM Check if utils directory exists (for data_cleaner)
if not exist "%SRC_DIR%\utils" (
    echo      [WARNING] Utils directory not found - some features may be limited
) else (
    echo      [OK] Utils directory found
)

REM ========================================================================
REM  STEP 5: Launch Application
REM ========================================================================
echo.
echo [5/5] Launching BARD-RECO...
echo.
echo ========================================================================
echo  Starting Professional Banking Reconciliation System
echo ========================================================================
echo.
echo  Python: %PYTHON_CMD%
echo  Version: %PYTHON_VERSION%
echo  Working Directory: %SRC_DIR%
echo.
echo  The application window will open shortly...
echo  (This console will close automatically)
echo.
echo ========================================================================
echo.

REM Give user a moment to read the info
timeout /t 2 /nobreak >nul

REM Change to src directory and launch
cd /d "%SRC_DIR%"

REM Try to launch with optimizations
"%PYTHON_CMD%" -OO gui.py

REM If launch fails, try without optimizations
if errorlevel 1 (
    echo.
    echo [RETRY] Launching without optimizations...
    "%PYTHON_CMD%" gui.py
)

REM Check if launch was successful
if errorlevel 1 (
    echo.
    echo ========================================================================
    echo [ERROR] Application Failed to Launch
    echo ========================================================================
    echo.
    echo Please check the error messages above for details.
    echo.
    echo COMMON SOLUTIONS:
    echo 1. Ensure all dependencies are installed
    echo 2. Check that Python version is 3.7 or higher
    echo 3. Verify all application files are present
    echo 4. Try running from Anaconda Prompt if using Anaconda
    echo.
    echo For support, please review the error messages and check:
    echo - README.md
    echo - AMOUNT_PARSING_FIX_GUIDE.md
    echo.
    pause
    exit /b 1
)

REM Success - application is running
exit /b 0

REM ========================================================================
REM  ERROR HANDLER (fallback)
REM ========================================================================
:error
echo.
echo ========================================================================
echo [CRITICAL ERROR]
echo ========================================================================
echo.
echo An unexpected error occurred during launch.
echo Error Level: %errorlevel%
echo.
echo Please try:
echo 1. Restarting your computer
echo 2. Reinstalling Python
echo 3. Running as Administrator
echo.
pause
exit /b 1
