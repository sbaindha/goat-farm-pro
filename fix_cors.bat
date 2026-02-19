@echo off
chcp 65001 >nul
title Fix CORS Error

echo.
echo  Fixing: No module named 'corsheaders'
echo.

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo OK: using venv
) else (
    echo NOTE: No venv found, installing globally
)

echo Installing django-cors-headers...
pip install django-cors-headers==4.3.1

if %errorlevel% neq 0 (
    echo ERROR: Install failed!
    echo Try manually: pip install django-cors-headers
    pause
    exit /b 1
)

echo.
echo  FIXED! Now run: python manage.py runserver
echo  Or double-click: start.bat
echo.
pause
