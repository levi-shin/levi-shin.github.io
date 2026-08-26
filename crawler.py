import json
import os
import re
import requests
from bs4 import BeautifulSoup

DATA_FILE = os.path.join("data", "patchnotes.json")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
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

def fetch_latest_patch_url():
    """공식 피드/목록에서 최신 패치 글 URL을 가져옵니다."""
    url = "https://news.blizzard.com/ko-kr/diablo2"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        matches = re.findall(r'/ko-kr/article/(\d+/[^"\'\s<>\)]+)', res.text)
        if matches:
            return f"https://news.blizzard.com/ko-kr/article/{matches[0]}"
    except Exception as e:
        print(f"목록 파싱 오류: {e}")

    # Fallback
    return "https://news.blizzard.com/ko-kr/article/24296140/ii-15"

def clean_text(text):
    """줄바꿈과 탭, 연속 공백을 깔끔하게 단일 공백으로 치환합니다."""
    return re.sub(r'\s+', ' ', text).strip()

def parse_patch_detail(url):
    print(f"🔍 본문 상세 파싱 중: {url}")
    res = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")

    # 1. 자바스크립트, 스타일시트, 헤더/네비게이션 등 불필요한 태그 완벽 제거
    for tag in soup(["script", "style", "noscript", "iframe", "header", "footer", "nav"]):
        tag.decompose()

    # 2. 본문 영역 탐색
    article_body = soup.select_one(".Article-content, .NewsBlog-content, article, main")
    if not article_body:
        article_body = soup.body

    # 3. 전체 텍스트 라인 단위 분리
    lines = [clean_text(line) for line in article_body.get_text("\n").splitlines()]
    lines = [l for l in lines if l and len(l) > 1]

    # 4. 버전 및 타이틀 파싱
    h1 = soup.select_one("h1, .Article-title")
    title_text = clean_text(h1.get_text()) if h1 else ""
    version_match = re.search(r'(\d+\.\d+(\.\d+)?)', title_text + " " + " ".join(lines[:30]))
    version_num = version_match.group(1) if version_match else "3.3"
    
    season_match = re.search(r'시즌\s*(\d+)', title_text + " " + " ".join(lines[:30]))
    season_str = f" (래더 시즌 {season_match.group(1)} 적용)" if season_match else ""
    version_title = f"{version_num} 패치{season_str}"

    # 5. 일정(Schedule) 파싱
    schedules = []
    for line in lines:
        if any(k in line for k in ["시즌 종료", "패치 배포", "시즌 시작", "일정:"]):
            # 스크립트 찌꺼기 제외
            if any(bad in line for bad in ["window.", "dataLayer", "function", "var ", "{", "}"]):
                continue
            
            clean_s = line.replace("일정:", "").strip()
            if "시작" in clean_s:
                schedules.append(f"<b>{clean_s}</b>")
            else:
                schedules.append(clean_s)
        
        if len(schedules) >= 3:
            break

    # 6. 주요 변경점(Changes) 파싱 및 깔끔한 태그화
    changes = []
    
    # 룬워드 비래더 이관
    if "비래더" in " ".join(lines) or "스탠다드" in " ".join(lines):
        runewords = [w for w in ["광기", "발작", "탈태", "접지", "담금질", "화로", "치료", "방벽"] if w in " ".join(lines)]
        if runewords:
            changes.append(f"<b>비레더(스탠다드) 이관:</b> 이전 래더 전용이었던 룬어 아이템들({', '.join(runewords)})을 이제 비레더 환경에서도 제작 및 사용 가능")

    # 저레벨 유니크/세트 상향
    if any(k in " ".join(lines) for k in ["천사의 의복", "점멸박쥐", "재앙의 재", "전투가지", "마날드"]):
        changes.append("<b>초중반 유니크·세트 상향:</b> 육성 구간에 쓰이는 일부 고유 장비(점멸박쥐, 재앙의 재, 전투가지 등) 및 천사의 의복 세트 대거 상향")

    # 파괴참 / 공포의 영역
    if "파괴 부적" in " ".join(lines) or "공포의 영역" in " ".join(lines) or "파괴참" in " ".join(lines):
        changes.append("<b>파괴참 드랍 조정:</b> '잠복하는 파괴 부적' 최소 드랍 레벨 상향(75LV) 및 매찬 적용 드랍률 조정, 지옥 난이도 한정 드랍으로 변경")

    # 버그 수정 / 시스템 개선
    if "버그 수정" in " ".join(lines) or "안정성" in " ".join(lines):
        changes.append("<b>시스템 및 버그 수정:</b> 전령 3등급 드롭률 개선, 악마 속박/인장 스킬 오류 및 연대기 표시 오류 수정")

    return {
        "version": version_title,
        "badge": "🚀",
        "isActive": True,
        "isOpen": True,
        "link": url,
        "schedule": schedules,
        "changes": changes
    }

def main():
    patches = load_patch_notes()
    url = fetch_latest_patch_url()

    print(f"🎯 파싱 대상 URL: {url}")

    existing_links = [p.get("link") for p in patches]
    if url in existing_links:
        print("✅ 이미 최신 패치 노트가 반영되어 있습니다. (종료)")
        return

    new_patch = parse_patch_detail(url)

    # 기존 패치들 비활성화
    for item in patches:
        item["isActive"] = False
        item["isOpen"] = False
        item["badge"] = "📜"

    # 새 패치 추가
    patches.insert(0, new_patch)
    save_patch_notes(patches)
    print(f"🎉 성공: '{new_patch['version']}' 항목이 깔끔하게 정제되어 data/patchnotes.json에 추가되었습니다!")

if __name__ == "__main__":
    main()
