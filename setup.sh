#!/bin/bash

# Goat Farm Management - Setup Script for Linux/Mac
# Enhanced version with better error handling

echo ""
echo "🐐 Goat Farm Management - Django Ninja v5.0"
echo "=========================================="
echo ""

# Check Python
echo "✓ Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python3 not found. Please install Python3."
    exit 1
fi
echo "✓ Python3 found: $(python3 --version)"

# Create virtual environment
echo ""
echo "✓ Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    python3 -m venv venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "✓ Installing dependencies..."
pip install --upgrade pip setuptools wheel
echo "Installing Django..."
pip install Django==4.2.10
echo "Installing Django Ninja..."
pip install django-ninja==1.3.0
echo "Installing other dependencies..."
pip install python-dateutil==2.8.2 pytz==2024.1

echo ""
echo "⚠️  Note: Pillow (image support) is optional"
echo "If you need image uploads, install with:"
echo "   pip install Pillow"
echo ""

# Create database
echo ""
echo "✓ Creating database..."
python manage.py makemigrations
if [ $? -ne 0 ]; then
    echo "✗ Makemigrations failed!"
    exit 1
fi

python manage.py migrate
if [ $? -ne 0 ]; then
    echo "✗ Migration failed!"
    exit 1
fi

# Create static files (optional)
echo "✓ Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null

# Create superuser
echo ""
echo "✓ Creating admin user..."
echo "Enter admin credentials below:"
echo ""
python manage.py createsuperuser
if [ $? -ne 0 ]; then
    echo "⚠️  Superuser creation skipped or failed"
fi

# Complete
echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server, run:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Then visit:"
echo "  Dashboard: http://127.0.0.1:8000/"
echo "  API Docs: http://127.0.0.1:8000/api/"
echo "  Admin: http://127.0.0.1:8000/admin/"
echo ""
echo "If you need image upload support, run:"
echo "  pip install Pillow"
echo ""
