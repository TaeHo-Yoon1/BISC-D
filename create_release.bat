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
echo ✅ GitHub Actions가 자동으로 실행됩니다:
echo    1. Windows에서 자동 빌드
echo    2. 빌드된 exe 파일을 릴리즈에 자동 첨부
echo    3. 릴리즈 자동 생성
echo.
echo 📊 진행 상황 확인:
echo    https://github.com/TaeHo-Yoon1/BISC-D/actions
echo.
echo 📦 릴리즈 확인 (빌드 완료 후^):
echo    https://github.com/TaeHo-Yoon1/BISC-D/releases
echo.
echo ⏱️  빌드는 보통 2-5분 정도 소요됩니다.
echo.

pause

