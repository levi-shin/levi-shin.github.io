import json
import os
import re
import requests
from bs4 import BeautifulSoup

DATA_FILE = os.path.join("data", "patchnotes.json")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

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

# diablo2 허브에 D4/D5/블리즈컨 교차 홍보 글이 먼저 뜨는 경우가 있어 D2R만 통과시킴
D2R_TITLE_ALLOW = re.compile(
    r"(디아블로\s*II|디아블로\s*2|레저렉션|Diablo\s*II|D2R|래더\s*\d+\s*시즌)",
    re.I,
)
NON_D2R_TITLE = re.compile(
    r"(디아블로\s*V\b|디아블로\s*IV\b|디아블로\s*4\b|Diablo\s*V\b|Diablo\s*IV\b|"
    r"Immortal|블리즈컨|다음\s*시대)",
    re.I,
)
D2R_SLUG = re.compile(r"(?:^|/)(ii(?:-|$)|diablo-?ii|resurrected)", re.I)
NON_D2R_SLUG = re.compile(r"(?:^|/)(v(?:-\d+)?$|immortal|diablo-?[45])", re.I)


def fetch_article_title(url: str) -> str:
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        title_el = soup.select_one("h1, .Article-title, .NewsBlog-title, .article-headline, header h1")
        if title_el:
            return clean_text(title_el.get_text())
        if soup.title:
            return clean_text(soup.title.get_text().split(" - ")[0].split(" — ")[0])
    except Exception as e:
        print(f"제목 조회 실패 ({url}): {e}")
    return ""


def is_d2r_article(url: str, title: str = "") -> bool:
    path = url.rsplit("/article/", 1)[-1]
    slug = path.split("/", 1)[-1] if "/" in path else path
    if NON_D2R_SLUG.search(slug) and not D2R_SLUG.search(slug):
        return False
    if D2R_SLUG.search(slug):
        # URL이 D2R처럼 보여도 제목이 타 작품이면 제외
        if title and NON_D2R_TITLE.search(title) and not D2R_TITLE_ALLOW.search(title):
            return False
        return True
    if not title:
        title = fetch_article_title(url)
    if not title:
        return False
    if NON_D2R_TITLE.search(title) and not D2R_TITLE_ALLOW.search(title):
        return False
    return bool(D2R_TITLE_ALLOW.search(title))


def fetch_latest_patch_url():
    list_url = "https://news.blizzard.com/ko-kr/diablo2"
    fallback = "https://news.blizzard.com/ko-kr/article/24296140/ii-15"
    try:
        res = requests.get(list_url, headers=HEADERS, timeout=15)
        matches = re.findall(r'/ko-kr/article/(\d+/[^"\'\s<>\)]+)', res.text)
        seen = set()
        unique = []
        for path in matches:
            if path not in seen:
                seen.add(path)
                unique.append(path)

        for path in unique:
            url = f"https://news.blizzard.com/ko-kr/article/{path}"
            title = ""
            # 슬러그만으로 명확히 탈락/통과 가능한 경우 네트워크 절약
            slug = path.split("/", 1)[-1]
            if NON_D2R_SLUG.search(slug) and not D2R_SLUG.search(slug):
                print(f"⏭️ D2R 아님(슬러그 스킵): {path}")
                continue
            if not D2R_SLUG.search(slug):
                title = fetch_article_title(url)
            if is_d2r_article(url, title):
                if title:
                    print(f"✅ D2R 후보 선택: {title} ({url})")
                else:
                    print(f"✅ D2R 후보 선택: {url}")
                return url
            if not title:
                title = fetch_article_title(url)
            print(f"⏭️ D2R 아님(스킵): {title or path}")
    except Exception as e:
        print(f"목록 파싱 오류: {e}")
    return fallback

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def strip_html_tags(text):
    text = re.sub(r'<b>(.*?)</b>', r'*\1*', text)
    return re.sub(r'<[^>]+>', '', text).strip()

def send_slack_notification(patch_data):
    if not SLACK_WEBHOOK_URL:
        return

    schedule_lines = "\n".join([f"• {strip_html_tags(s)}" for s in patch_data.get("schedule", [])])
    if not schedule_lines:
        schedule_lines = "• 별도 공지 일정 없음"

    changes_lines = "\n".join([f"• {strip_html_tags(c)}" for c in patch_data.get("changes", [])])

    slack_message = {
        "text": f"🚀 *디아블로 II: 레저렉션 신규 패치 등록!*\n*{patch_data['version']}*",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"🚀 {patch_data['version']}", "emoji": True}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"🔗 *공식 공지 전문 확인:*\n<{patch_data['link']}|{patch_data['link']}>"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"📅 *시즌 및 패치 일정*\n{schedule_lines}"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"🛡️ *핵심 주요 변경 사항 요약*\n{changes_lines}"}
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": "🤖 `data/patchnotes.json` 파일에 자동 반영 완료되었습니다."}]
            }
        ]
    }
    try:
        requests.post(SLACK_WEBHOOK_URL, json=slack_message, timeout=10)
    except Exception as e:
        print(f"Slack 에러: {e}")

def parse_patch_detail(url):
    print(f"🔍 본문 분석 중: {url}")
    res = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")

    for tag in soup(["script", "style", "noscript", "iframe", "header", "footer", "nav"]):
        tag.decompose()

    article_body = soup.select_one(".Article-content, .NewsBlog-content, article, main") or soup.body

    raw_lines = [clean_text(line) for line in article_body.get_text("\n").splitlines()]
    lines = [l for l in raw_lines if l and len(l) > 1]
    full_text = " ".join(lines)

    # 1. 실제 글 제목 및 버전 동적 추출
    title_el = soup.select_one("h1, .Article-title, .NewsBlog-title, .article-headline, header h1")
    title_text = clean_text(title_el.get_text()) if title_el else ""
    
    if not title_text and soup.title:
        title_text = clean_text(soup.title.get_text().split(" - ")[0].split(" — ")[0])

    version_match = re.search(r'(\d+\.\d+(\.\d+)?)', title_text + " " + full_text[:1000])
    version_num = version_match.group(1) if version_match else "3.3"

    season_match = re.search(r'(?:래더\s*(\d+)\s*시즌|시즌\s*(\d+)|-(\d+)$)', title_text + " " + url)
    season_num = season_match.group(1) if season_match else ""
    season_str = f" (래더 시즌 {season_num} 적용)" if season_num else ""

    if title_text and title_text != f"{version_num} 패치":
        version_title = f"{version_num} 패치{season_str} - {title_text}"
    else:
        version_title = f"{version_num} 패치{season_str}"

    # 2. 일정 파싱 (종료/배포/시작 문장)
    schedules = []
    for line in lines:
        if len(line) < 8 or any(bad in line for bad in ["window.", "dataLayer", "목차", "일정:", "시작되는 래더", "유럽", "북미", "PDT", "BST"]):
            continue
        if any(term in line for term in ["종료", "배포", "시작"]) and any(d in line for d in ["월", "일", "/", "시"]):
            if "시작" in line and "배포" not in line:
                schedules.append(f"<b>{line}</b>")
            else:
                schedules.append(line)
        if len(schedules) >= 3:
            break

    # 3. 핵심 4대 카테고리 자동 압축 요약
    changes = []
    
    # ① 비래더/룬어 이관 자동 요약
    for idx, line in enumerate(lines):
        if "비래더" in line and any(v in line for v in ["이용할 수 있습니다", "적용됩니다", "이관"]):
            unlocked = []
            for sub in lines[idx + 1:idx + 15]:
                if len(sub) > 10 or any(stop in sub for stop in ["변경된 아이템", "공포의 영역", "버그 수정", "추가했습니다", "감소했습니다"]):
                    break
                unlocked.append(sub)
            
            if unlocked:
                changes.append(f"<b>비레더(스탠다드) 이관:</b> 이전 래더 전용 아이템/룬어({', '.join(unlocked)})를 이제 비레더 환경에서도 제작 및 사용 가능")
            else:
                changes.append("<b>비레더(스탠다드) 이관:</b> 이전 래더 전용 아이템 및 룬어의 비래더(스탠다드) 제작 및 사용 가능")
            break

    # ② 변경된 아이템들 자동 수집 후 1줄 요약
    changed_items = []
    for i, line in enumerate(lines):
        if 2 <= len(line) <= 12 and not any(k in line for k in ["아이템", "공포", "버그", "패치", "시즌", "일정", "보너스"]):
            if i + 1 < len(lines):
                next_l = lines[i + 1]
                if any(verb in next_l for verb in ["추가했습니다", "감소했습니다", "증가했습니다", "제거했습니다"]):
                    clean_name = line.replace("의 형상", "").replace(" 치유 반지", "").strip()
                    if clean_name not in changed_items and clean_name not in ["광기", "발작", "탈태", "접지", "담금질", "화로", "치료", "방벽"]:
                        changed_items.append(clean_name)

    if changed_items:
        items_preview = ", ".join(changed_items[:4])
        changes.append(f"<b>장비 및 세트 밸런스 개편:</b> 일부 고유 장비({items_preview} 등) 및 세트 아이템 옵션/요구레벨 상향 조정")
    elif "아이템" in full_text and any(v in full_text for v in ["추가했습니다", "감소했습니다"]):
        changes.append("<b>아이템 밸런스 조정:</b> 일부 고유 및 세트 장비의 옵션 상향과 요구 레벨 조정 적용")

    # ③ 공포의 영역 / 파괴참 / 드랍 시스템 1줄 요약
    for line in lines:
        if any(k in line for k in ["파괴 부적", "파괴참", "전령", "세계석"]):
            if any(verb in line for verb in ["증가했습니다", "감소했습니다", "떨어집니다", "변경되었습니다"]):
                changes.append(f"<b>공포의 영역/드랍 조정:</b> {line}")
                break

    # ④ 버그 수정 및 시스템 안정성 1줄 요약
    for line in lines:
        if "버그 수정" in line or "문제를 수정했습니다" in line or "성능이 다양하게" in line:
            if len(line) > 10 and not any(bad in line for bad in ["목차", "댓글"]):
                changes.append(f"<b>시스템 및 버그 수정:</b> {line}")
                break

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

    if not url:
        print("❌ 공지 URL을 가져오지 못했습니다.")
        return

    print(f"🎯 파싱 대상 URL: {url}")

    if not is_d2r_article(url):
        print(f"❌ D2R 패치가 아닌 글로 판단되어 중단: {url}")
        return

    existing_links = [p.get("link") for p in patches]
    if url in existing_links:
        print("✅ 이미 최신 패치 노트가 반영되어 있습니다. (종료)")
        return

    new_patch = parse_patch_detail(url)

    # 파싱 후에도 제목 기준으로 한 번 더 검증 (교차 홍보 기사 방어)
    if not is_d2r_article(url, new_patch.get("version", "")):
        print(f"❌ 파싱 결과가 D2R이 아니라 저장하지 않습니다: {new_patch.get('version')}")
        return

    for item in patches:
        item["isActive"] = False
        item["isOpen"] = False
        item["badge"] = "📜"

    patches.insert(0, new_patch)
    save_patch_notes(patches)
    print(f"🎉 성공: '{new_patch['version']}' 항목이 완벽하게 추가되었습니다!")

    send_slack_notification(new_patch)

if __name__ == "__main__":
    main()
