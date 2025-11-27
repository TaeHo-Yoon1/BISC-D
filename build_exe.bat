@echo off
chcp 949 >nul 2>&1
echo Building Dvorak Typing Trainer...

REM Create virtual environment if not exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install required packages
echo Installing required packages...
pip install -r requirements.txt

REM Remove existing build folders
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM Build exe file with PyInstaller
echo Building exe file...
pyinstaller --onefile --windowed --name="DvorakTypingTrainer" --icon=icon.ico main.py

REM Build completion message
if exist "dist\DvorakTypingTrainer.exe" (
    echo.
    echo ========================================
    echo Build Complete!
    echo Executable location: dist\DvorakTypingTrainer.exe
    echo ========================================
) else (
    echo Build failed!
)

pause
