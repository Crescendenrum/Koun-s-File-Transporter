@echo off
setlocal enabledelayedexpansion

echo Checking Python installation...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Downloading the latest version...
    
    :: Download latest Python installer
    curl -o python_installer.exe https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe
    
    echo Installing Python...
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    
    echo Python installation complete. Restarting script...
    start /b "" "%~f0" %*
    exit
) else (
    echo Python is already installed.
)

:: Ensure pip is up to date
echo Updating pip...
python -m ensurepip
python -m pip install --upgrade pip

:: Install FreeSimpleGUI (the only external library you need)
echo Installing FreeSimpleGUI...
python -m pip install FreeSimpleGUI

echo All done! Press any key to exit.
pause
