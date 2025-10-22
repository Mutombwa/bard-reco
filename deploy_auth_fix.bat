@echo off
REM Deployment script for authentication fixes (Windows)
REM Run this to deploy persistent authentication to Streamlit Cloud

echo.
echo ========================================================
echo  Deploying Authentication Fixes to Streamlit Cloud
echo ========================================================
echo.

REM Check if we're in the right directory
if not exist "app.py" (
    echo [ERROR] app.py not found. Please run this script from the repository root.
    pause
    exit /b 1
)

REM Check if database exists
if not exist "data\users.db" (
    echo [WARNING] data\users.db not found. Creating database...
    python -c "from auth.persistent_auth import PersistentAuthentication; PersistentAuthentication()"
    echo [OK] Database created
)

echo [OK] Database file exists
echo.

REM Show what will be committed
echo Files to be committed:
echo ----------------------
git status --short
echo.

REM Confirm
set /p CONFIRM="Continue with deployment? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo [CANCELLED] Deployment cancelled
    pause
    exit /b 1
)

REM Add files
echo.
echo [STEP 1/3] Adding files to Git...
git add .gitignore
git add app.py
git add auth\persistent_auth.py
git add data\users.db
git add data\.gitkeep
git add AUTHENTICATION_FIX_GUIDE.md
git add deploy_auth_fix.bat
git add deploy_auth_fix.sh

REM Commit
echo [STEP 2/3] Creating commit...
git commit -m "Fix: Persistent authentication + secure registration" -m "" -m "- Migrate from JSON to SQLite for user persistence" -m "- Database tracked in Git to survive app restarts" -m "- Remove email domain hint to prevent fake registrations" -m "- Add comprehensive deployment documentation" -m "" -m "Fixes:" -m "- Users no longer lost when app goes to sleep" -m "- Fake registrations prevented (domain not shown)" -m "- Better performance with indexed database queries" -m "- Thread-safe concurrent user support"

REM Push
echo [STEP 3/3] Pushing to GitHub...
git push origin main

echo.
echo ========================================================
echo  Deployment Complete!
echo ========================================================
echo.
echo Next Steps:
echo 1. Go to your Streamlit Cloud dashboard
echo 2. App will automatically rebuild (takes ~2-3 minutes)
echo 3. Test registration with generic message (no domain hint)
echo 4. Test that users persist after app restart
echo.
echo Documentation: AUTHENTICATION_FIX_GUIDE.md
echo.
echo Your app now has persistent authentication!
echo.
pause
