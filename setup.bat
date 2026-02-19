@echo off
REM Goat Farm Management - Setup Script for Windows
REM Enhanced version with better error handling

echo.
echo 🐐 Goat Farm Management - Django Ninja v5.0
echo ==========================================
echo.

REM Check Python
echo ✓ Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python not found. Please install Python from https://www.python.org/
    pause
    exit /b 1
)
echo ✓ Python found

REM Create virtual environment
echo.
echo ✓ Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
)

REM Activate virtual environment
echo ✓ Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo ✓ Installing dependencies...
python -m pip install --upgrade pip setuptools wheel
echo Installing Django...
pip install Django==4.2.10
echo Installing Django Ninja...
pip install django-ninja==1.3.0
echo Installing other dependencies...
pip install python-dateutil==2.8.2 pytz==2024.1

echo.
echo ⚠️  Note: Pillow (image support) is optional
echo If you need image uploads, install with:
echo   pip install Pillow
echo.

REM Create database
echo.
echo ✓ Creating database...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo ✗ Makemigrations failed!
    pause
    exit /b 1
)

python manage.py migrate
if %errorlevel% neq 0 (
    echo ✗ Migration failed!
    pause
    exit /b 1
)

REM Create static files (optional)
echo ✓ Collecting static files...
python manage.py collectstatic --noinput 2>nul

REM Create superuser
echo.
echo ✓ Creating admin user...
echo Enter admin credentials below:
echo.
python manage.py createsuperuser
if %errorlevel% neq 0 (
    echo ⚠️  Superuser creation skipped or failed
)

REM Complete
echo.
echo ✅ Setup complete!
echo.
echo To start the server, run:
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
echo Then visit:
echo   Dashboard: http://127.0.0.1:8000/
echo   API Docs: http://127.0.0.1:8000/api/
echo   Admin: http://127.0.0.1:8000/admin/
echo.
echo If you need image upload support, run:
echo   pip install Pillow
echo.
pause
