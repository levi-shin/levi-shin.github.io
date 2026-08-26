import json
import os
import re
import requests
from bs4 import BeautifulSoup

# 대상 파일 경로 수정
DATA_FILE = os.path.join("data", "patchnotes.json")
LIST_URL = "https://news.blizzard.com/ko-kr/diablo2"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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
    # data 폴더가 없을 경우 자동 생성
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_latest_article_link():
    res = requests.get(LIST_URL, headers=HEADERS)
    if res.status_code != 200:
        print(f"뉴스 목록 로드 실패: {res.status_code}")
        return None
    
    soup = BeautifulSoup(res.text, "html.parser")
    articles = soup.select(".ArticleListItem, article, .NewsBlog-link")
    
    for art in articles:
        link_elem = art if art.name == "a" else art.select_one("a")
        title_elem = art.select_one(".ArticleListItem-title, h3, .NewsBlog-title")
        
        if link_elem and title_elem:
            title = title_elem.get_text(strip=True)
            href = link_elem["href"]
            if href.startswith("/"):
                href = "https://news.blizzard.com" + href
            
            if any(k in title for k in ["패치", "래더", "시즌", "공지"]):
                return title, href
                
    return None

def parse_patch_detail(url, raw_title):
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        return None

    soup = BeautifulSoup(res.text, "html.parser")
    content_area = soup.select_one(".Article-content, .NewsBlog-content, article")
    
    version_match = re.search(r'(\d+\.\d+(\.\d+)?)', raw_title)
    version_num = version_match.group(1) if version_match else "최신"
    version_title = f"{version_num} 패치 ({raw_title})"

    schedules = []
    changes = []

    if content_area:
        list_items = content_area.select("li")
        for li in list_items:
            text = li.get_text(strip=True)
            if not text:
                continue
            
            if any(k in text for k in ["시작", "종료", "배포", "일시", "PDT", "한국 시간"]):
                schedules.append(f"<b>일정 안내:</b> {text}")
            else:
                if ":" in text:
                    prefix, rest = text.split(":", 1)
                    changes.append(f"<b>{prefix.strip()}:</b> {rest.strip()}")
                elif len(changes) < 6:
                    changes.append(f"<b>주요 변경:</b> {text}")

    if not changes:
        changes.append(f"<b>세부 내역:</b> {raw_title} 상세 내용은 공식 공지 링크를 확인하세요.")

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
    latest = get_latest_article_link()

    if not latest:
        print("최신 공지 링크를 가져오지 못했습니다.")
        return

    title, url = latest
    print(f"가장 최근 공지: {title} ({url})")

    # 기존 등록 링크 확인 (중복 체크)
    existing_links = [p.get("link") for p in patches]
    if url in existing_links:
        print("이미 최신 패치 노트가 반영되어 있습니다. 변경 없음.")
        return

    # 신규 패치 데이터 파싱
    new_patch_data = parse_patch_detail(url, title)
    if not new_patch_data:
        print("패치 본문 파싱 실패.")
        return

    # 기존 모든 패치 비활성화
    for item in patches:
        item["isActive"] = False
        item["isOpen"] = False
        item["badge"] = "📜"

    # 새 패치를 맨 앞에 추가
    patches.insert(0, new_patch_data)
    save_patch_notes(patches)
    print(f"성공적으로 {new_patch_data['version']} 항목이 data/patchnotes.json 에 추가되었습니다.")

if __name__ == "__main__":
    main()
