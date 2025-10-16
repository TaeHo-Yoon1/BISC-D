@echo off
echo 드보락 타자연습 프로그램 빌드 시작...

REM 가상환경 생성 (없는 경우)
if not exist "venv" (
    echo 가상환경 생성 중...
    python -m venv venv
)

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM 필요한 패키지 설치
echo 필요한 패키지 설치 중...
pip install -r requirements.txt

REM 기존 빌드 폴더 삭제
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

REM PyInstaller로 exe 파일 생성
echo exe 파일 빌드 중...
pyinstaller --onefile --windowed --name="DvorakTypingTrainer" --icon=icon.ico main.py

REM 빌드 완료 메시지
if exist "dist\DvorakTypingTrainer.exe" (
    echo.
    echo ========================================
    echo 빌드 완료!
    echo 실행 파일 위치: dist\DvorakTypingTrainer.exe
    echo ========================================
) else (
    echo 빌드 실패!
)

pause
