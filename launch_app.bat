@echo off
setlocal
cd /d %~dp0

if not exist env\Scripts\python.exe (
    echo Virtual environment not found.
    echo Please run install_app.bat first.
    pause
    exit /b 1
)

set PYTHON_EXE=env\Scripts\python.exe
echo Starting LMS...
start "" http://127.0.0.1:8000/
%PYTHON_EXE% manage.py runserver 127.0.0.1:8000
