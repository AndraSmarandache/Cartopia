#!/bin/bash

echo "===================================="
echo "Setup Aplicatie E-Commerce Django"
echo "===================================="
echo ""

echo "[1/5] Creare mediu virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Eroare la crearea mediului virtual!"
    exit 1
fi

echo "[2/5] Activare mediu virtual..."
source venv/bin/activate

echo "[3/5] Instalare dependinte..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Eroare la instalarea dependintelor!"
    exit 1
fi

echo "[4/5] Creare baza de date..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "Eroare la crearea bazei de date!"
    exit 1
fi

echo "[5/5] Incarcare date de test..."
python manage.py load_sample_data
if [ $? -ne 0 ]; then
    echo "Eroare la incarcarea datelor de test!"
    exit 1
fi

echo ""
echo "===================================="
echo "Setup completat cu succes!"
echo "===================================="
echo ""
echo "Pentru a porni aplicatia, ruleaza:"
echo "  python manage.py runserver"
echo ""
echo "Credentiale de test:"
echo "  Admin: admin / admin123"
echo "  User: testuser / test123"
echo ""

