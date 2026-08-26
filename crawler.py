import json
import os
import re
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup

DATA_FILE = os.path.join("data", "patchnotes.json")

# 정확한 블리자드 디아블로2 레저렉션 뉴스 피드 및 목록 URL
FEED_URLS = [
    "https://news.blizzard.com/ko-kr/feed/diablo-2-resurrected",
    "https://news.blizzard.com/ko-kr/feed/news/diablo-2-resurrected"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
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

def get_latest_article():
    """블리자드 공식 디아2 피드에서 최신 패치/시즌 글을 추출합니다."""
    for feed_url in FEED_URLS:
        try:
            res = requests.get(feed_url, headers=HEADERS, timeout=10)
            if res.status_code != 200:
                continue

            # 1. RSS/XML 포맷 파싱 시도
            try:
                root = ET.fromstring(res.content)
                items = root.findall(".//item")
                for item in items:
                    title_elem = item.find("title")
                    link_elem = item.find("link")
                    if title_elem is not None and link_elem is not None:
                        title = title_elem.text.strip()
                        link = link_elem.text.strip()
                        if any(k in title for k in ["래더", "패치", "시즌", "공지", "업데이트", "배포"]):
                            return title, link
            except ET.ParseError:
                pass

            # 2. HTML 피드 목록 파싱 시도
            soup = BeautifulSoup(res.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                title = a.get_text(strip=True)
                if "/article/" in href:
                    if not title:
                        # 자식 태그에서 제목 텍스트 탐색
                        title = a.get("aria-label", "") or a.get("title", "")
                    
                    if href.startswith("/"):
                        href = "https://news.blizzard.com" + href
                    
                    if any(k in title for k in ["래더", "패치", "시즌", "공지", "업데이트"]) or "article" in href:
                        return title if title else "디아블로 II: 레저렉션 최신 패치 공지", href

        except Exception as e:
            print(f"피드 로드 실패 ({feed_url}): {e}")

    return None

def parse_patch_detail(url, raw_title):
    schedules = []
    changes = []
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            
            # 본문 내 리스트 및 텍스트 파싱
            for li in soup.select("li, p"):
                text = li.get_text(strip=True)
                if not text or len(text) < 4:
                    continue
                
                # 일정 관련 구문 분류
                if any(k in text for k in ["시작", "종료", "배포", "일정", "한국 시간", "PDT"]):
                    if len(schedules) < 3 and text not in schedules:
                        schedules.append(f"<b>일정 안내:</b> {text}")
                # 주요 변경점 분류
                elif any(k in text for k in ["패치", "아이템", "상향", "하향", "적용", "스탠다드", "공포의 영역", "부적", "수정"]):
                    if ":" in text:
                        prefix, rest = text.split(":", 1)
                        formatted = f"<b>{prefix.strip()}:</b> {rest.strip()}"
                    else:
                        formatted = f"<b>주요 변경:</b> {text}"
                    
                    if len(changes) < 6 and formatted not in changes:
                        changes.append(formatted)
    except Exception as e:
        print(f"본문 파싱 중 오류: {e}")

    # 버전 번호 추출 (예: 3.3, 3.4 등 추출 실패 시 시즌 번호나 기본값 설정)
    version_match = re.search(r'(\d+\.\d+(\.\d+)?)', raw_title)
    season_match = re.search(r'(시즌\s*\d+|래더\s*\d+)', raw_title)
    
    if version_match:
        version_title = f"{version_match.group(1)} 패치 ({raw_title})"
    elif season_match:
        version_title = f"최신 패치 ({season_match.group(1)} 적용)"
    else:
        version_title = f"최신 패치 ({raw_title})"

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
    latest = get_latest_article()

    if not latest:
        print("❌ 에러: 최신 공지/패치 글을 찾지 못했습니다.")
        return

    title, url = latest
    print(f"🔍 최신 글 감지: {title}")
    print(f"🔗 링크: {url}")

    # 기존 등록 여부 확인 (중복 체크)
    existing_links = [p.get("link") for p in patches]
    if url in existing_links:
        print("✅ 이미 최신 패치 노트가 반영되어 있습니다. (종료)")
        return

    # 신규 패치 데이터 생성
    new_patch = parse_patch_detail(url, title)

    # 기존 모든 패치 비활성화
    for item in patches:
        item["isActive"] = False
        item["isOpen"] = False
        item["badge"] = "📜"

    # 최신 패치를 맨 위에 추가
    patches.insert(0, new_patch)
    save_patch_notes(patches)
    print(f"🎉 성공: '{new_patch['version']}' 패치 데이터가 data/patchnotes.json에 추가되었습니다!")

if __name__ == "__main__":
    main()
