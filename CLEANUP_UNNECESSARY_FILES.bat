@echo off
echo ========================================
echo  CLEANUP UNNECESSARY FILES
echo  Removing redundant documentation and files
echo ========================================
echo.

cd /d "%~dp0"

echo Creating backup list...
echo DELETED FILES - %date% %time% > DELETED_FILES_LIST.txt
echo ======================================= >> DELETED_FILES_LIST.txt
echo.

REM ===== REDUNDANT DOCUMENTATION FILES =====
echo [1/4] Removing redundant documentation files...

del /F /Q "ALWAYS_ON_QUICK_START.txt" 2>nul && echo ALWAYS_ON_QUICK_START.txt >> DELETED_FILES_LIST.txt
del /F /Q "ALWAYS_ON_SERVICE_GUIDE.md" 2>nul && echo ALWAYS_ON_SERVICE_GUIDE.md >> DELETED_FILES_LIST.txt
del /F /Q "BATCH_HISTORY_GUIDE.md" 2>nul && echo BATCH_HISTORY_GUIDE.md >> DELETED_FILES_LIST.txt
del /F /Q "BATCH_HISTORY_IMPLEMENTATION.md" 2>nul && echo BATCH_HISTORY_IMPLEMENTATION.md >> DELETED_FILES_LIST.txt
del /F /Q "BATCH_HISTORY_IMPROVEMENTS.md" 2>nul && echo BATCH_HISTORY_IMPROVEMENTS.md >> DELETED_FILES_LIST.txt
del /F /Q "BATCH_HISTORY_QUICK_REFERENCE.md" 2>nul && echo BATCH_HISTORY_QUICK_REFERENCE.md >> DELETED_FILES_LIST.txt
del /F /Q "COLLABORATIVE_DASHBOARD_README.md" 2>nul && echo COLLABORATIVE_DASHBOARD_README.md >> DELETED_FILES_LIST.txt
del /F /Q "COLUMN_EXPLANATION.md" 2>nul && echo COLUMN_EXPLANATION.md >> DELETED_FILES_LIST.txt
del /F /Q "COLUMN_NAMES_FIX_GUIDE.md" 2>nul && echo COLUMN_NAMES_FIX_GUIDE.md >> DELETED_FILES_LIST.txt
del /F /Q "CORPORATE_SETTLEMENTS_README.md" 2>nul && echo CORPORATE_SETTLEMENTS_README.md >> DELETED_FILES_LIST.txt
del /F /Q "DASHBOARD_COMPLETE_FIX_SUMMARY.md" 2>nul && echo DASHBOARD_COMPLETE_FIX_SUMMARY.md >> DELETED_FILES_LIST.txt
del /F /Q "DASHBOARD_GUIDE.md" 2>nul && echo DASHBOARD_GUIDE.md >> DELETED_FILES_LIST.txt
del /F /Q "DASHBOARD_IMPROVEMENTS_SUMMARY.md" 2>nul && echo DASHBOARD_IMPROVEMENTS_SUMMARY.md >> DELETED_FILES_LIST.txt
del /F /Q "DASHBOARD_QUICK_START.md" 2>nul && echo DASHBOARD_QUICK_START.md >> DELETED_FILES_LIST.txt
del /F /Q "DASHBOARD_README.md" 2>nul && echo DASHBOARD_README.md >> DELETED_FILES_LIST.txt
del /F /Q "DASHBOARD_TRANSACTIONS_VIEW_UPDATE.md" 2>nul && echo DASHBOARD_TRANSACTIONS_VIEW_UPDATE.md >> DELETED_FILES_LIST.txt
del /F /Q "DEPLOYMENT_GUIDE.md" 2>nul && echo DEPLOYMENT_GUIDE.md >> DELETED_FILES_LIST.txt
del /F /Q "DEPLOYMENT_SUMMARY.md" 2>nul && echo DEPLOYMENT_SUMMARY.md >> DELETED_FILES_LIST.txt
del /F /Q "DEPLOY_WITH_PYTHON.txt" 2>nul && echo DEPLOY_WITH_PYTHON.txt >> DELETED_FILES_LIST.txt
del /F /Q "ENHANCED_DATA_EDITOR_GUIDE.md" 2>nul && echo ENHANCED_DATA_EDITOR_GUIDE.md >> DELETED_FILES_LIST.txt
del /F /Q "ENHANCED_OUTSTANDING_QUICK_REFERENCE.txt" 2>nul && echo ENHANCED_OUTSTANDING_QUICK_REFERENCE.txt >> DELETED_FILES_LIST.txt
del /F /Q "ERRORS_FIXED_VISUAL_GUIDE.txt" 2>nul && echo ERRORS_FIXED_VISUAL_GUIDE.txt >> DELETED_FILES_LIST.txt
del /F /Q "ERROR_FIXES_SUMMARY.txt" 2>nul && echo ERROR_FIXES_SUMMARY.txt >> DELETED_FILES_LIST.txt
del /F /Q "FIX_MODULE_ERRORS.txt" 2>nul && echo FIX_MODULE_ERRORS.txt >> DELETED_FILES_LIST.txt
del /F /Q "HOW_TO_ACCESS_TRANSACTIONS_VIEW.md" 2>nul && echo HOW_TO_ACCESS_TRANSACTIONS_VIEW.md >> DELETED_FILES_LIST.txt
del /F /Q "IMPLEMENTATION_SUMMARY.md" 2>nul && echo IMPLEMENTATION_SUMMARY.md >> DELETED_FILES_LIST.txt
del /F /Q "INSTALLATION_CHECKLIST.txt" 2>nul && echo INSTALLATION_CHECKLIST.txt >> DELETED_FILES_LIST.txt
del /F /Q "INSTALLATION_GUIDE.md" 2>nul && echo INSTALLATION_GUIDE.md >> DELETED_FILES_LIST.txt
del /F /Q "OUTSTANDING_TRANSACTIONS_FEATURE_GUIDE.md" 2>nul && echo OUTSTANDING_TRANSACTIONS_FEATURE_GUIDE.md >> DELETED_FILES_LIST.txt
del /F /Q "QUICK_DEPLOY.txt" 2>nul && echo QUICK_DEPLOY.txt >> DELETED_FILES_LIST.txt
del /F /Q "QUICK_REFERENCE_CARD.txt" 2>nul && echo QUICK_REFERENCE_CARD.txt >> DELETED_FILES_LIST.txt
del /F /Q "QUICK_START.txt" 2>nul && echo QUICK_START.txt >> DELETED_FILES_LIST.txt
del /F /Q "QUICK_START_GUIDE.txt" 2>nul && echo QUICK_START_GUIDE.txt >> DELETED_FILES_LIST.txt
del /F /Q "README_DASHBOARD_SETUP.txt" 2>nul && echo README_DASHBOARD_SETUP.txt >> DELETED_FILES_LIST.txt
del /F /Q "READ_IF_ERROR.txt" 2>nul && echo READ_IF_ERROR.txt >> DELETED_FILES_LIST.txt
del /F /Q "SMART_COPY_COLUMN_CLEANUP.md" 2>nul && echo SMART_COPY_COLUMN_CLEANUP.md >> DELETED_FILES_LIST.txt
del /F /Q "START_HERE.txt" 2>nul && echo START_HERE.txt >> DELETED_FILES_LIST.txt
del /F /Q "START_WITH_THIS_GUIDE.txt" 2>nul && echo START_WITH_THIS_GUIDE.txt >> DELETED_FILES_LIST.txt
del /F /Q "TRANSFER_CHECKLIST.txt" 2>nul && echo TRANSFER_CHECKLIST.txt >> DELETED_FILES_LIST.txt
del /F /Q "WEB_DASHBOARD_README.md" 2>nul && echo WEB_DASHBOARD_README.md >> DELETED_FILES_LIST.txt

echo   ✓ Documentation files removed

REM ===== REDUNDANT BATCH FILES =====
echo [2/4] Removing redundant batch files...

del /F /Q "automated_setup.bat" 2>nul && echo automated_setup.bat >> DELETED_FILES_LIST.txt
del /F /Q "BARD_RECO_FAST.bat" 2>nul && echo BARD_RECO_FAST.bat >> DELETED_FILES_LIST.txt
del /F /Q "build_with_pyinstaller.bat" 2>nul && echo build_with_pyinstaller.bat >> DELETED_FILES_LIST.txt
del /F /Q "CLEANUP_OLD_FILES.bat" 2>nul && echo CLEANUP_OLD_FILES.bat >> DELETED_FILES_LIST.txt
del /F /Q "DEBUG_LAUNCHER.bat" 2>nul && echo DEBUG_LAUNCHER.bat >> DELETED_FILES_LIST.txt
del /F /Q "FIX_ALL_ERRORS.bat" 2>nul && echo FIX_ALL_ERRORS.bat >> DELETED_FILES_LIST.txt
del /F /Q "FIX_MISSING_MODULES.bat" 2>nul && echo FIX_MISSING_MODULES.bat >> DELETED_FILES_LIST.txt
del /F /Q "INSTALL_ON_NEW_MACHINE.bat" 2>nul && echo INSTALL_ON_NEW_MACHINE.bat >> DELETED_FILES_LIST.txt
del /F /Q "install_service.bat" 2>nul && echo install_service.bat >> DELETED_FILES_LIST.txt
del /F /Q "INSTALL_SERVICE_ADMIN.bat" 2>nul && echo INSTALL_SERVICE_ADMIN.bat >> DELETED_FILES_LIST.txt
del /F /Q "launch_dashboard.bat" 2>nul && echo launch_dashboard.bat >> DELETED_FILES_LIST.txt
del /F /Q "PORTABLE_SETUP.bat" 2>nul && echo PORTABLE_SETUP.bat >> DELETED_FILES_LIST.txt
del /F /Q "RUN_ANYWHERE.bat" 2>nul && echo RUN_ANYWHERE.bat >> DELETED_FILES_LIST.txt
del /F /Q "run_app.bat" 2>nul && echo run_app.bat >> DELETED_FILES_LIST.txt
del /F /Q "run_bard_reco.bat" 2>nul && echo run_bard_reco.bat >> DELETED_FILES_LIST.txt
del /F /Q "RUN_TEST.bat" 2>nul && echo RUN_TEST.bat >> DELETED_FILES_LIST.txt
del /F /Q "RUN_TEST_FIXED.bat" 2>nul && echo RUN_TEST_FIXED.bat >> DELETED_FILES_LIST.txt
del /F /Q "run_with_master_env.bat" 2>nul && echo run_with_master_env.bat >> DELETED_FILES_LIST.txt
del /F /Q "setup.bat" 2>nul && echo setup.bat >> DELETED_FILES_LIST.txt
del /F /Q "setup_web_dashboard.bat" 2>nul && echo setup_web_dashboard.bat >> DELETED_FILES_LIST.txt
del /F /Q "START_DASHBOARD_SIMPLE.bat" 2>nul && echo START_DASHBOARD_SIMPLE.bat >> DELETED_FILES_LIST.txt

echo   ✓ Redundant batch files removed

REM ===== OLD TEST AND DEBUG FILES =====
echo [3/4] Removing old test and debug files...

del /F /Q "check_export_data.py" 2>nul && echo check_export_data.py >> DELETED_FILES_LIST.txt
del /F /Q "core_reconciliation.py" 2>nul && echo core_reconciliation.py >> DELETED_FILES_LIST.txt
del /F /Q "debug_app.py" 2>nul && echo debug_app.py >> DELETED_FILES_LIST.txt
del /F /Q "launch_web_dashboard.py" 2>nul && echo launch_web_dashboard.py >> DELETED_FILES_LIST.txt
del /F /Q "persistent_dashboard_service.py" 2>nul && echo persistent_dashboard_service.py >> DELETED_FILES_LIST.txt
del /F /Q "test_dashboard.py" 2>nul && echo test_dashboard.py >> DELETED_FILES_LIST.txt
del /F /Q "test_dashboard_fixed.py" 2>nul && echo test_dashboard_fixed.py >> DELETED_FILES_LIST.txt
del /F /Q "test_dashboard_integration.py" 2>nul && echo test_dashboard_integration.py >> DELETED_FILES_LIST.txt
del /F /Q "web_dashboard_server.py" 2>nul && echo web_dashboard_server.py >> DELETED_FILES_LIST.txt
del /F /Q "nul" 2>nul && echo nul >> DELETED_FILES_LIST.txt
del /F /Q "start_dashboard_hidden.vbs" 2>nul && echo start_dashboard_hidden.vbs >> DELETED_FILES_LIST.txt

echo   ✓ Old test and debug files removed

REM ===== BACKUP FILES IN SRC =====
echo [4/4] Removing backup files in src folder...

del /F /Q "src\outstanding_transactions_manager_OLD_BACKUP.py" 2>nul && echo src\outstanding_transactions_manager_OLD_BACKUP.py >> DELETED_FILES_LIST.txt
del /F /Q "src\bidvest_debug_matches.json" 2>nul && echo src\bidvest_debug_matches.json >> DELETED_FILES_LIST.txt

echo   ✓ Backup files removed

echo.
echo ========================================
echo  CLEANUP COMPLETE!
echo ========================================
echo.
echo Files deleted: See DELETED_FILES_LIST.txt
echo.
echo KEPT FILES:
echo   ✓ README.md (main documentation)
echo   ✓ requirements.txt
echo   ✓ src/ folder (all core Python files)
echo   ✓ Ultra_Fast.bat (launcher)
echo   ✓ INSTANT_LAUNCH.bat (launcher)
echo   ✓ launch_web_dashboard.bat (dashboard)
echo   ✓ All .db files (databases)
echo   ✓ pyrightconfig.json
echo   ✓ ReconciliationApp.spec
echo   ✓ .vscode/ and .claude/ folders
echo   ✓ backend/, static/, templates/ folders
echo.
echo Your workspace is now clean and organized!
echo.
pause
