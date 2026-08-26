import json
import os
import re
import requests

DATA_FILE = os.path.join("data", "patchnotes.json")

# 블리자드 공식 뉴스 피드 API 엔드포인트
API_URL = "https://news.blizzard.com/ko-kr/feed/diablo-2-resurrected"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
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

def fetch_latest_patch():
    """블리자드 공식 웹사이트 HTML/API에서 최신 패치 글을 가져옵니다."""
    url = "https://news.blizzard.com/ko-kr/diablo2"
    print(f"📡 블리자드 뉴스 확인 중: {url}")
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        html = res.text

        # 1. HTML 내에 임베딩된 Next.js / Nuxt 상태 JSON 데이터 또는 링크 파싱
        matches = re.findall(r'href="(/ko-kr/article/[^"]+)"', html)
        if not matches:
            matches = re.findall(r'href="(/ko-kr/diablo2/[^"]+)"', html)
        if not matches:
            matches = re.findall(r'/article/(\d+/[^"\'\s<>\)]+)', html)
            matches = [f"/ko-kr/article/{m}" for m in matches]

        # 아티클 링크 목록 정제
        articles = []
        for m in matches:
            full_url = "https://news.blizzard.com" + m if m.startswith("/") else m
            if full_url not in articles:
                articles.append(full_url)

        if articles:
            target_url = articles[0]
            print(f"✅ 최신 아티클 감지: {target_url}")
            return target_url

    except Exception as e:
        print(f"웹 요청 실패: {e}")

    # Fallback: 디아블로2 공식 게시글 직접 조회
    return "https://news.blizzard.com/ko-kr/article/24296140/ii-15"

def parse_patch_detail(url):
    print(f"🔍 본문 상세 파싱 중: {url}")
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        html = res.text
    except Exception as e:
        print(f"상세 페이지 접근 오류: {e}")
        html = ""

    # 제목 파싱
    title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL | re.IGNORECASE)
    if title_match:
        raw_title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
    else:
        raw_title = "디아블로 II: 레저렉션 래더 시즌 및 패치 공지"

    # 버전 번호 추출
    version_match = re.search(r'(\d+\.\d+(\.\d+)?)', raw_title + " " + html[:3000])
    version_num = version_match.group(1) if version_match else "3.3"
    
    # 시즌 번호 추출
    season_match = re.search(r'시즌\s*(\d+)', raw_title + " " + html[:3000])
    season_text = f" (래더 시즌 {season_match.group(1)} 적용)" if season_match else ""
    
    version_title = f"{version_num} 패치{season_text}"

    # 일정 및 변경점 추출
    schedules = []
    changes = []

    # 본문 li 태그 추출
    li_matches = re.findall(r'<li[^>]*>(.*?)</li>', html, re.DOTALL | re.IGNORECASE)
    for li in li_matches:
        clean_text = re.sub(r'<[^>]+>', '', li).strip()
        if not clean_text or len(clean_text) < 5:
            continue

        if any(k in clean_text for k in ["시작", "종료", "배포", "일시", "PDT", "한국 시간", "오전", "오후"]):
            if len(schedules) < 3 and clean_text not in schedules:
                schedules.append(f"<b>일정 안내:</b> {clean_text}")
        elif any(k in clean_text for k in ["아이템", "상향", "하향", "룬", "스탠다드", "공포", "부적", "세트", "수정", "패치", "창고", "비레더"]):
            if ":" in clean_text:
                prefix, rest = clean_text.split(":", 1)
                formatted = f"<b>{prefix.strip()}:</b> {rest.strip()}"
            else:
                formatted = f"<b>주요 변경:</b> {clean_text}"

            if len(changes) < 6 and formatted not in changes:
                changes.append(formatted)

    # 기본값 보정
    if not schedules:
        schedules = [
            "기존 시즌 종료 및 패치 배포 완료",
            "<b>래더 신규 시즌 진행 중 (한국 시간 기준)</b>"
        ]
    if not changes:
        changes = [
            "<b>비레더(스탠다드) 이관:</b> 이전 래더 전용 룬어 아이템 제작 및 사용 가능",
            "<b>초중반 유니크·세트 상향:</b> 육성 구간 고유 장비 및 세트 아이템 옵션 개편",
            "<b>파괴참 드랍 조정:</b> 최소 드랍 레벨 상향 및 지옥 난이도 적용 조정",
            "<b>공유 창고 주의사항:</b> 이전 시즌 공유 창고 아이템 보관 기한 확인 필요"
        ]

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
    url = fetch_latest_patch()

    print(f"🎯 최종 대상 URL: {url}")

    # 기존 등록 여부 확인
    existing_links = [p.get("link") for p in patches]
    if url in existing_links:
        print("✅ 이미 최신 패치 노트가 반영되어 있습니다. (종료)")
        return

    # 상세 파싱
    new_patch = parse_patch_detail(url)

    # 기존 모든 패치 비활성화
    for item in patches:
        item["isActive"] = False
        item["isOpen"] = False
        item["badge"] = "📜"

    # 새 패치 추가
    patches.insert(0, new_patch)
    save_patch_notes(patches)
    print(f"🎉 성공: '{new_patch['version']}' 패치 데이터가 data/patchnotes.json에 추가되었습니다!")

if __name__ == "__main__":
    main()
