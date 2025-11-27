@echo off
chcp 65001 >nul 2>&1
REM GitHub 릴리즈 생성 스크립트 (Windows)
REM 사용법: create_release.bat [버전] [릴리즈 노트]
REM 예시: create_release.bat v1.0.0 "첫 번째 릴리즈"

setlocal enabledelayedexpansion

set VERSION=%1
if "%VERSION%"=="" set VERSION=v1.0.0

set RELEASE_NOTES=%2
if "%RELEASE_NOTES%"=="" set RELEASE_NOTES=드보락 타자연습 프로그램 릴리즈

echo ==========================================
echo GitHub 릴리즈 생성
echo ==========================================
echo 버전: %VERSION%
echo 릴리즈 노트: %RELEASE_NOTES%
echo.

REM 변경사항이 있는지 확인
git status --porcelain >nul 2>&1
if %errorlevel% equ 0 (
    echo 경고: 커밋되지 않은 변경사항이 있습니다.
    set /p CONTINUE="계속하시겠습니까? (y/n): "
    if /i not "!CONTINUE!"=="y" exit /b 1
)

REM 현재 브랜치 확인
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
echo 현재 브랜치: !CURRENT_BRANCH!

REM 태그가 이미 존재하는지 확인
git rev-parse "%VERSION%" >nul 2>&1
if %errorlevel% equ 0 (
    echo 오류: 태그 %VERSION%이 이미 존재합니다.
    exit /b 1
)

REM 태그 생성
echo.
echo 태그 생성 중: %VERSION%
git tag -a "%VERSION%" -m "%RELEASE_NOTES%"

if %errorlevel% neq 0 (
    echo 태그 생성 실패!
    exit /b 1
)

REM 태그를 원격 저장소에 푸시
echo.
echo 태그를 원격 저장소에 푸시 중...
git push origin "%VERSION%"

if %errorlevel% neq 0 (
    echo 태그 푸시 실패!
    exit /b 1
)

echo.
echo ==========================================
echo 태그 생성 완료!
echo ==========================================
echo.
echo 다음 단계:
echo 1. https://github.com/TaeHo-Yoon1/BISC-D/releases/new 로 이동
echo 2. 'Choose a tag'에서 '%VERSION%' 선택
echo 3. 릴리즈 제목 입력 (예: %VERSION%^)
echo 4. 릴리즈 노트 입력:
echo    %RELEASE_NOTES%
echo.
echo 5. (선택사항) 빌드된 실행 파일을 첨부하려면:
echo    - dist\DvorakTypingTrainer.exe (Windows^)
echo    - dist\DvorakTypingTrainer (Linux/Mac^)
echo.
echo 6. 'Publish release' 버튼 클릭
echo.

pause

