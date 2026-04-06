@echo off
setlocal
cd /d %~dp0

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

%PYTHON_EXE% -m PyInstaller --noconfirm --clean --onefile --windowed --name LMS-Launcher lms_launcher.py
if errorlevel 1 (
    echo EXE build failed.
    pause
    exit /b 1
)

echo.
echo Build complete.
echo EXE path: dist\LMS-Launcher.exe
echo Keep dist\LMS-Launcher.exe in this LMS project folder so it can find manage.py and env.
pause
