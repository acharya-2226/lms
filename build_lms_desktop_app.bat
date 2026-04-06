@echo off
setlocal
cd /d %~dp0

set APP_NAME=LMS-Desktop
set APP_VERSION=
if exist APP_VERSION.txt (
    set /p APP_VERSION=<APP_VERSION.txt
)
if "%APP_VERSION%"=="" set APP_VERSION=2.0.0
set EXE_BASENAME=%APP_NAME%-v%APP_VERSION%

if exist env\Scripts\python.exe (
    set PYTHON_EXE=env\Scripts\python.exe
) else if exist .venv\Scripts\python.exe (
    set PYTHON_EXE=.venv\Scripts\python.exe
) else (
    set PYTHON_EXE=python
)

echo Using Python: %PYTHON_EXE%
%PYTHON_EXE% -m pip install --upgrade pip pyinstaller
if errorlevel 1 (
    echo Failed to install PyInstaller.
    pause
    exit /b 1
)

%PYTHON_EXE% -m PyInstaller --noconfirm --clean --onefile --windowed --name %EXE_BASENAME% lms_desktop_app.py
if errorlevel 1 (
    echo EXE build failed.
    pause
    exit /b 1
)

if exist dist\%APP_NAME%-latest.exe del /f /q dist\%APP_NAME%-latest.exe
copy /y dist\%EXE_BASENAME%.exe dist\%APP_NAME%-latest.exe >nul

echo.
echo Build complete.
echo Versioned EXE: dist\%EXE_BASENAME%.exe
echo Latest alias : dist\%APP_NAME%-latest.exe
echo Keep the EXE in this LMS project folder so it can find manage.py and env.
pause
