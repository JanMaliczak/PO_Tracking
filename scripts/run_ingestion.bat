@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

call "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
if errorlevel 1 exit /b 1

python "%PROJECT_ROOT%\manage.py" run_ingestion --settings=po_tracking.settings.production %*
exit /b %errorlevel%
