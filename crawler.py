import json
import os
import re
import requests
from bs4 import BeautifulSoup

DATA_FILE = os.path.join("data", "patchnotes.json")

# 블리자드 디아블로2 공식 뉴스 페이지들
TARGET_URLS = [
    "https://news.blizzard.com/ko-kr/diablo2",
    "https://news.blizzard.com/ko-kr/feed/diablo-2-resurrected"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
}

def load_patch_notes():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_patch_notes(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_latest_article_url():
    """페이지 내 모든 아티클 링크 패턴(/article/숫자/...)을 정규식으로 직접 추출합니다."""
    for url in TARGET_URLS:
        try:
            print(f"📡 대상 URL 확인 중: {url}")
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                print(f"응답 코드: {res.status_code}")
                continue

            html = res.text
            # /ko-kr/article/숫자/문자열 패턴 매칭
            article_matches = re.findall(r'/ko-kr/article/(\d+/[^"\'\s<>\)]+)', html)
            
            if not article_matches:
                # 상대 경로 article/숫자 매칭
                article_matches = re.findall(r'/article/(\d+/[^"\'\s<>\)]+)', html)

            # 중복 제거하며 순서 유지
            unique_articles = []
            for path in article_matches:
                full_url = f"https://news.blizzard.com/ko-kr/article/{path}"
                if full_url not in unique_articles:
                    unique_articles.append(full_url)

            if unique_articles:
                print(f"✅ 아티클 {len(unique_articles)}개 발견! 최신 아티클: {unique_articles[0]}")
                return unique_articles[0]

        except Exception as e:
            print(f"URL 접근 중 에러 ({url}): {e}")

    return None

def parse_patch_detail(url):
    """상세 페이지에서 실제 제목과 일정/변경점을 파싱합니다."""
    res = requests.get(url, headers=HEADERS, timeout=15)
    if res.status_code != 200:
        print(f"상세 페이지 로드 실패: {res.status_code}")
        return None

    soup = BeautifulSoup(res.text, "html.parser")

    # 1. 제목 추출 (h1 태그 또는 title 메타 태그)
    title_elem = soup.select_one("h1, .Article-title, title")
    raw_title = title_elem.get_text(strip=True) if title_elem else "디아블로 II: 레저렉션 패치 공지"
    # 타이틀에서 사이트 이름 꼬리표 제거
    raw_title = re.sub(r'\s*[-|—]\s*블리자드 소식.*$', '', raw_title).strip()

    schedules = []
    changes = []

    # 2. 본문 리스트 및 주요 문장 파싱
    for li in soup.select("li, p"):
        text = li.get_text(strip=True)
        if not text or len(text) < 4:
            continue

        # 일정 관련 텍스트 추출
        if any(k in text for k in ["시작", "종료", "배포", "일정", "한국 시간", "PDT", "오전", "오후"]):
            if len(schedules) < 3 and text not in schedules:
                schedules.append(f"<b>일정 안내:</b> {text}")
        
        # 주요 아이템 / 밸런스 변경점 추출
        elif any(k in text for k in ["아이템", "상향", "하향", "룬어", "적용", "스탠다드", "공포의 영역", "부적", "세트", "수정"]):
            if ":" in text:
                prefix, rest = text.split(":", 1)
                formatted = f"<b>{prefix.strip()}:</b> {rest.strip()}"
            else:
                formatted = f"<b>주요 변경:</b> {text}"

            if len(changes) < 6 and formatted not in changes:
                changes.append(formatted)

    # 3. 버전 번호 생성 (본문 또는 제목에서 추출)
    version_match = re.search(r'(\d+\.\d+(\.\d+)?)', raw_title + " " + res.text[:2000])
    version_num = version_match.group(1) if version_match else "최신"
    
    version_title = f"{version_num} 패치 ({raw_title})"

    if not schedules:
        schedules.append("<b>일정 안내:</b> 공식 블로그 세부 일정 공지를 확인하세요.")
    if not changes:
        changes.append(f"<b>세부 내역:</b> {raw_title} 상세 패치 내역은 공식 공지 링크를 참고하세요.")

    return {
        "version": version_title,
        "badge": "🚀",
        "isActive": True,
        "isOpen": True,
        "link": url,
        "schedule": schedules[:3],
        "changes": changes[:6]
    }

def main():
    patches = load_patch_notes()
    latest_url = find_latest_article_url()

    if not latest_url:
        print("❌ 에러: 최신 공지 링크를 찾지 못했습니다.")
        return

    print(f"🔍 최신 아티클 분석 중: {latest_url}")

    # 기존 등록 링크와 비교 (중복 체크)
    existing_links = [p.get("link") for p in patches]
    if latest_url in existing_links:
        print("✅ 이미 최신 패치 노트가 반영되어 있습니다. (종료)")
        return

    # 상세 내용 크롤링
    new_patch = parse_patch_detail(latest_url)
    if not new_patch:
        print("❌ 본문 파싱 실패")
        return

    # 기존 모든 패치 비활성화
    for item in patches:
        item["isActive"] = False
        item["isOpen"] = False
        item["badge"] = "📜"

    # 새 패치 최상단 삽입
    patches.insert(0, new_patch)
    save_patch_notes(patches)
    print(f"🎉 성공: '{new_patch['version']}' 항목이 data/patchnotes.json에 추가되었습니다!")

if __name__ == "__main__":
    main()
