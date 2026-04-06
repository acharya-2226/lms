@echo off
setlocal
cd /d %~dp0

echo ================================
echo LMS One-Time Installer
echo ================================
echo.

if not exist env\Scripts\python.exe (
    echo Creating virtual environment...
    python -m venv env
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

set PYTHON_EXE=env\Scripts\python.exe
echo Using Python: %PYTHON_EXE%

echo Installing runtime dependencies...
%PYTHON_EXE% -m pip install --upgrade pip
%PYTHON_EXE% -m pip install -r requirements_runtime.txt
if errorlevel 1 (
    echo Failed to install runtime dependencies.
    pause
    exit /b 1
)

echo Applying migrations...
%PYTHON_EXE% manage.py migrate --noinput
if errorlevel 1 (
    echo Migration failed.
    pause
    exit /b 1
)

echo.
echo Installation complete.
echo Next time, run launch_app.bat or LMS-Launcher.exe to start quickly.
pause
