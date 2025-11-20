@echo off
echo ====================================
echo Setup Aplicatie E-Commerce Django
echo ====================================
echo.

echo [1/5] Creare mediu virtual...
python -m venv venv
if errorlevel 1 (
    echo Eroare la crearea mediului virtual!
    pause
    exit /b 1
)

echo [2/5] Activare mediu virtual...
call venv\Scripts\activate.bat

echo [3/5] Instalare dependinte...
pip install -r requirements.txt
if errorlevel 1 (
    echo Eroare la instalarea dependintelor!
    pause
    exit /b 1
)

echo [4/5] Creare baza de date...
python manage.py migrate
if errorlevel 1 (
    echo Eroare la crearea bazei de date!
    pause
    exit /b 1
)

echo [5/5] Incarcare date de test...
python manage.py load_sample_data
if errorlevel 1 (
    echo Eroare la incarcarea datelor de test!
    pause
    exit /b 1
)

echo.
echo ====================================
echo Setup completat cu succes!
echo ====================================
echo.
echo Pentru a porni aplicatia, ruleaza:
echo   python manage.py runserver
echo.
echo Credentiale de test:
echo   Admin: admin / admin123
echo   User: testuser / test123
echo.
pause

