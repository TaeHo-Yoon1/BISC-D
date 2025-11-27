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
echo "다음 단계:"
echo "1. https://github.com/TaeHo-Yoon1/BISC-D/releases/new 로 이동"
echo "2. 'Choose a tag'에서 '$VERSION' 선택"
echo "3. 릴리즈 제목 입력 (예: $VERSION)"
echo "4. 릴리즈 노트 입력:"
echo "   $RELEASE_NOTES"
echo ""
echo "5. (선택사항) 빌드된 실행 파일을 첨부하려면:"
echo "   - dist/DvorakTypingTrainer.exe (Windows)"
echo "   - dist/DvorakTypingTrainer (Linux/Mac)"
echo ""
echo "6. 'Publish release' 버튼 클릭"
echo ""

