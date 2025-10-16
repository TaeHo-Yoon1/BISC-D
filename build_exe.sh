#!/bin/bash

echo "드보락 타자연습 프로그램 빌드 시작..."

# 가상환경 생성 (없는 경우)
if [ ! -d "venv" ]; then
    echo "가상환경 생성 중..."
    python3 -m venv venv
fi

# 가상환경 활성화
source venv/bin/activate

# 필요한 패키지 설치
echo "필요한 패키지 설치 중..."
pip install -r requirements.txt

# 기존 빌드 폴더 삭제
rm -rf dist build

# PyInstaller로 exe 파일 생성
echo "exe 파일 빌드 중..."
pyinstaller --onefile --windowed --name="DvorakTypingTrainer" main.py

# 빌드 완료 메시지
if [ -f "dist/DvorakTypingTrainer" ]; then
    echo ""
    echo "========================================"
    echo "빌드 완료!"
    echo "실행 파일 위치: dist/DvorakTypingTrainer"
    echo "========================================"
else
    echo "빌드 실패!"
fi
