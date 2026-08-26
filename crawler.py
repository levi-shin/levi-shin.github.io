import json
import os
import re
from curl_cffi import requests
from bs4 import BeautifulSoup

DATA_FILE = os.path.join("data", "patchnotes.json")

# 블리자드 디아블로2 공식 한국어 피드 URL
URL = "https://news.blizzard.com/ko-kr/feed/diablo-2-resurrected"

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

def fetch_latest_patch_article():
    """Chrome 브라우저 TLS 지문으로 요청하여 Cloudflare 차단을 우회합니다."""
    session = requests.Session(impersonate="chrome120")
    
    print(f"📡 블리자드 피드 요청 중: {URL}")
    res = session.get(URL, timeout=15)
    
    if res.status_code != 200:
        print(f"❌ 요청 실패. 상태 코드: {res.status_code}")
        return None, None

    soup = BeautifulSoup(res.text, "html.parser")
    
    # 1. RSS 형식일 경우
    items = soup.find_all("item")
    for it in items:
        title = it.find("title").get_text(strip=True) if it.find("title") else ""
        link = it.find("link").get_text(strip=True) if it.find("link") else ""
        if any(k in title for k in ["래더", "패치", "시즌", "공지"]):
            return title, link

    # 2. HTML 피드 형식일 경우 (모든 링크 탐색)
    for a in soup.find_all("a", href=True):
        href = a["href"]
        title = a.get_text(strip=True)
        
        # /article/숫자/ 패턴 링크 탐색
        if "/article/" in href:
            if href.startswith("/"):
                href = "https://news.blizzard.com" + href
            if not title:
                title = a.get("title", "") or a.get("aria-label", "")
            return title if title else "디아블로 II: 레저렉션 패치 공지", href

    # 3. 정규식 백업 매칭
    matches = re.findall(r'href="([^"]*article/\d+/[^"]*)"', res.text)
    if matches:
        first = matches[0]
        if first.startswith("/"):
            first = "https://news.blizzard.com" + first
        return "디아블로 II: 레저렉션 패치 공지", first

    return None, None

def parse_patch_detail(url, raw_title):
    session = requests.Session(impersonate="chrome120")
    res = session.get(url, timeout=15)
    
    if res.status_code != 200:
        return None

    soup = BeautifulSoup(res.text, "html.parser")
    
    # 제목 추출
    h1 = soup.select_one("h1, .Article-title")
    title = h1.get_text(strip=True) if h1 else raw_title
    title = re.sub(r'\s*[-|—]\s*블리자드 소식.*$', '', title).strip()

    schedules = []
    changes = []

    # 본문 추출
    for li in soup.select("li, p"):
        text = li.get_text(strip=True)
        if not text or len(text) < 4:
            continue

        if any(k in text for k in ["시작", "종료", "배포", "일정", "한국 시간", "PDT"]):
            if len(schedules) < 3 and text not in schedules:
                schedules.append(f"<b>일정 안내:</b> {text}")
        elif any(k in text for k in ["아이템", "상향", "하향", "룬어", "적용", "스탠다드", "공포의 영역", "부적", "세트", "수정", "패치"]):
            if ":" in text:
                prefix, rest = text.split(":", 1)
                formatted = f"<b>{prefix.strip()}:</b> {rest.strip()}"
            else:
                formatted = f"<b>주요 변경:</b> {text}"

            if len(changes) < 6 and formatted not in changes:
                changes.append(formatted)

    # 버전 번호 파싱
    version_match = re.search(r'(\d+\.\d+(\.\d+)?)', title + " " + res.text[:1500])
    version_num = version_match.group(1) if version_match else "최신"
    version_title = f"{version_num} 패치 ({title})"

    if not schedules:
        schedules.append("<b>일정 안내:</b> 공식 블로그 세부 일정 공지를 확인하세요.")
    if not changes:
        changes.append(f"<b>세부 내역:</b> {title} 상세 패치 내역은 공식 공지 링크를 참고하세요.")

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
    title, url = fetch_latest_patch_article()

    if not url:
        print("❌ 에러: 최신 공지 링크를 찾지 못했습니다.")
        return

    print(f"✅ 최신 글 발견: {title}")
    print(f"🔗 링크: {url}")

    # 중복 체크
    existing_links = [p.get("link") for p in patches]
    if url in existing_links:
        print("✅ 이미 최신 패치 노트가 반영되어 있습니다. (종료)")
        return

    # 상세 내용 파싱
    new_patch = parse_patch_detail(url, title)
    if not new_patch:
        print("❌ 본문 파싱 실패")
        return

    # 기존 패치 비활성화
    for item in patches:
        item["isActive"] = False
        item["isOpen"] = False
        item["badge"] = "📜"

    # 새 패치 추가
    patches.insert(0, new_patch)
    save_patch_notes(patches)
    print(f"🎉 성공: '{new_patch['version']}' 항목이 data/patchnotes.json에 추가되었습니다!")

if __name__ == "__main__":
    main()
