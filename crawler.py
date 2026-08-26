import json
import os
import re
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup

DATA_FILE = os.path.join("data", "patchnotes.json")
# 블리자드 디아블로2 공식 RSS 피드
RSS_URL = "https://news.blizzard.com/ko-kr/feed/news/diablo2"
LIST_URL = "https://news.blizzard.com/ko-kr/diablo2"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
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
    """1차로 RSS 피드를 시도하고, 실패 시 HTML 크롤링으로 대체합니다."""
    try:
        res = requests.get(RSS_URL, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            items = root.findall("./channel/item")
            for item in items:
                title_elem = item.find("title")
                link_elem = item.find("link")
                if title_elem is not None and link_elem is not None:
                    title = title_elem.text.strip()
                    link = link_elem.text.strip()
                    # 패치, 래더, 시즌, 업데이트 등 관련 키워드 확인
                    if any(k in title for k in ["패치", "래더", "시즌", "공지", "업데이트", "배포"]):
                        return title, link
    except Exception as e:
        print(f"RSS 파싱 오류 (HTML 폴백 시도): {e}")

    # RSS가 안 될 경우 HTML 파싱 시도
    try:
        res = requests.get(LIST_URL, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            # 모든 링크 태그 탐색
            for a in soup.find_all("a", href=True):
                href = a["href"]
                title = a.get_text(strip=True)
                if "/article/" in href and any(k in title for k in ["패치", "래더", "시즌", "공지"]):
                    if href.startswith("/"):
                        href = "https://news.blizzard.com" + href
                    return title, href
    except Exception as e:
        print(f"HTML 파싱 오류: {e}")

    return None

def parse_patch_detail(url, raw_title):
    schedules = []
    changes = []
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            
            # 본문 리스트 아이템 탐색
            for li in soup.select("li"):
                text = li.get_text(strip=True)
                if not text or len(text) < 5:
                    continue
                
                if any(k in text for k in ["시작", "종료", "배포", "일시", "PDT", "한국 시간"]):
                    schedules.append(f"<b>일정:</b> {text}")
                else:
                    if ":" in text:
                        prefix, rest = text.split(":", 1)
                        changes.append(f"<b>{prefix.strip()}:</b> {rest.strip()}")
                    elif len(changes) < 6:
                        changes.append(f"<b>주요 내용:</b> {text}")
    except Exception as e:
        print(f"상세 페이지 파싱 중 오류: {e}")

    # 버전 정규식 추출 (예: 3.3, 3.4 등)
    version_match = re.search(r'(\d+\.\d+(\.\d+)?)', raw_title)
    version_num = version_match.group(1) if version_match else "최신"
    version_title = f"{version_num} 패치 ({raw_title})"

    if not changes:
        changes.append(f"<b>세부 내역:</b> {raw_title} 상세 내용은 공식 공지 링크를 참고하세요.")

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
        print("❌ 에러: 최신 공지/패치 글을 찾지 못했습니다. 사이트 구조나 URL을 점검하세요.")
        return

    title, url = latest
    print(f"🔍 감지된 최신 글: {title}")
    print(f"🔗 링크: {url}")

    # 기존 등록 링크 확인 (중복 체크)
    existing_links = [p.get("link") for p in patches]
    if url in existing_links:
        print("✅ 이미 최신 패치 노트가 등록되어 있습니다. (변경 사항 없음)")
        return

    # 신규 패치 데이터 생성
    new_patch = parse_patch_detail(url, title)
    
    # 기존 모든 패치 비활성화
    for item in patches:
        item["isActive"] = False
        item["isOpen"] = False
        item["badge"] = "📜"

    # 최상단 삽입
    patches.insert(0, new_patch)
    save_patch_notes(patches)
    print(f"🎉 성공: {new_patch['version']} 패치 데이터가 data/patchnotes.json에 추가되었습니다!")

if __name__ == "__main__":
    main()
