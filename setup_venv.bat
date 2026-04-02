@echo off
echo ========================================
echo   MusicalMe - Virtual Environment Setup
echo ========================================
echo.
echo This will create an isolated environment for MusicalMe
echo to avoid conflicts with other Python packages.
echo.

REM Check if venv already exists
if exist "venv" (
    echo Virtual environment already exists. Deleting old one...
    rmdir /s /q venv
)

echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing MusicalMe dependencies...
python -m pip install --upgrade pip

echo Installing packages (this may take a few minutes)...
pip install protobuf==3.20.3
pip install numpy==1.24.3
pip install opencv-python==4.8.1.78
pip install mediapipe==0.10.8
pip install pygame==2.5.2

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo To run MusicalMe, use: run.bat
echo (Do NOT run python main.py directly)
echo.
pause
