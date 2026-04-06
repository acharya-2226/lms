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
%PYTHON_EXE% lms_desktop_app.py
