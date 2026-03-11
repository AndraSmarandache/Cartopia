@echo off
REM Run the app at a custom URL (host:port)
REM Set RUN_HOST and RUN_PORT before running, or edit defaults below.
REM Examples:
REM   set RUN_PORT=8080    then run.bat     -> http://127.0.0.1:8080
REM   set RUN_HOST=0.0.0.0 set RUN_PORT=8080 then run.bat  -> accessible on LAN (set ALLOWED_HOSTS=* if needed)

if "%RUN_HOST%"=="" set RUN_HOST=127.0.0.1
if "%RUN_PORT%"=="" set RUN_PORT=8000

echo Starting Cartopia at http://%RUN_HOST%:%RUN_PORT%
echo.
call venv\Scripts\activate.bat 2>nul
python manage.py runserver %RUN_HOST%:%RUN_PORT%
