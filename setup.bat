@echo off
echo ====================================
echo Django E-Commerce Application Setup
echo ====================================
echo.

echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error creating virtual environment!
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error installing dependencies!
    pause
    exit /b 1
)

echo [4/5] Creating database...
python manage.py migrate
if errorlevel 1 (
    echo Error creating database!
    pause
    exit /b 1
)

echo [5/5] Loading sample data...
python manage.py load_sample_data
if errorlevel 1 (
    echo Error loading sample data!
    pause
    exit /b 1
)

echo.
echo ====================================
echo Setup completed successfully!
echo ====================================
echo.
echo To start the application, run:
echo   python manage.py runserver
echo.
echo To run at a different address (e.g. port 8080 or 0.0.0.0 for LAN access):
echo   set RUN_PORT=8080
echo   run.bat
echo   Or: python manage.py runserver 0.0.0.0:8080
echo.
echo Test credentials:
echo   Admin: admin / admin123
echo   User: testuser / test123
echo.
pause

