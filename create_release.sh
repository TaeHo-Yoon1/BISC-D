#!/bin/bash

# GitHub 릴리즈 생성 스크립트
# 사용법: ./create_release.sh [버전] [릴리즈 노트]
# 예시: ./create_release.sh v1.0.0 "첫 번째 릴리즈"

VERSION=${1:-v1.0.0}
RELEASE_NOTES=${2:-"드보락 타자연습 프로그램 릴리즈"}

echo "=========================================="
echo "GitHub 릴리즈 생성"
echo "=========================================="
echo "버전: $VERSION"
echo "릴리즈 노트: $RELEASE_NOTES"
echo ""

# 변경사항이 있는지 확인
if [ -n "$(git status --porcelain)" ]; then
    echo "경고: 커밋되지 않은 변경사항이 있습니다."
    read -p "계속하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 현재 브랜치 확인
CURRENT_BRANCH=$(git branch --show-current)
echo "현재 브랜치: $CURRENT_BRANCH"

# 태그가 이미 존재하는지 확인
if git rev-parse "$VERSION" >/dev/null 2>&1; then
    echo "오류: 태그 $VERSION이 이미 존재합니다."
    exit 1
fi

# 태그 생성
echo ""
echo "태그 생성 중: $VERSION"
git tag -a "$VERSION" -m "$RELEASE_NOTES"

if [ $? -ne 0 ]; then
    echo "태그 생성 실패!"
    exit 1
fi

# 태그를 원격 저장소에 푸시
echo ""
echo "태그를 원격 저장소에 푸시 중..."
git push origin "$VERSION"

if [ $? -ne 0 ]; then
    echo "태그 푸시 실패!"
    exit 1
fi

echo ""
echo "=========================================="
echo "태그 생성 완료!"
echo "=========================================="
echo ""
echo "✅ GitHub Actions가 자동으로 실행됩니다:"
echo "   1. Windows에서 자동 빌드"
echo "   2. 빌드된 exe 파일을 릴리즈에 자동 첨부"
echo "   3. 릴리즈 자동 생성"
echo ""
echo "📊 진행 상황 확인:"
echo "   https://github.com/TaeHo-Yoon1/BISC-D/actions"
echo ""
echo "📦 릴리즈 확인 (빌드 완료 후):"
echo "   https://github.com/TaeHo-Yoon1/BISC-D/releases"
echo ""
echo "⏱️  빌드는 보통 2-5분 정도 소요됩니다."
echo ""

