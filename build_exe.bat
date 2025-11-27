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
REM spec 파일이 있으면 spec 파일 사용, 없으면 생성
if exist "DvorakTypingTrainer.spec" (
    if exist "icon.ico" (
        pyinstaller --clean DvorakTypingTrainer.spec
    ) else (
        REM icon.ico가 없으면 spec 파일에서 icon 제거하고 빌드
        pyinstaller --onefile --windowed --name="DvorakTypingTrainer" --add-data "coding_templates.json;." main.py
    )
) else (
    if exist "icon.ico" (
        pyinstaller --onefile --windowed --name="DvorakTypingTrainer" --icon=icon.ico --add-data "coding_templates.json;." main.py
    ) else (
        pyinstaller --onefile --windowed --name="DvorakTypingTrainer" --add-data "coding_templates.json;." main.py
    )
)

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
