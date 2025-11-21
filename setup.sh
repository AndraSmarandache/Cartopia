#!/bin/bash

echo "===================================="
echo "Django E-Commerce Application Setup"
echo "===================================="
echo ""

echo "[1/5] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error creating virtual environment!"
    exit 1
fi

echo "[2/5] Activating virtual environment..."
source venv/bin/activate

echo "[3/5] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error installing dependencies!"
    exit 1
fi

echo "[4/5] Creating database..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "Error creating database!"
    exit 1
fi

echo "[5/5] Loading sample data..."
python manage.py load_sample_data
if [ $? -ne 0 ]; then
    echo "Error loading sample data!"
    exit 1
fi

echo ""
echo "===================================="
echo "Setup completed successfully!"
echo "===================================="
echo ""
echo "To start the application, run:"
echo "  python manage.py runserver"
echo ""
echo "Test credentials:"
echo "  Admin: admin / admin123"
echo "  User: testuser / test123"
echo ""

