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

def fetch_latest_patch_url():
    url = "https://news.blizzard.com/ko-kr/diablo2"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        matches = re.findall(r'/ko-kr/article/(\d+/[^"\'\s<>\)]+)', res.text)
        if matches:
            return f"https://news.blizzard.com/ko-kr/article/{matches[0]}"
    except Exception as e:
        print(f"목록 파싱 오류: {e}")

    return "https://news.blizzard.com/ko-kr/article/24296140/ii-15"

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def strip_html_tags(text):
    text = re.sub(r'<b>(.*?)</b>', r'*\1*', text)
    return re.sub(r'<[^>]+>', '', text).strip()

def send_slack_notification(patch_data):
    if not SLACK_WEBHOOK_URL:
        print("⚠️ SLACK_WEBHOOK_URL이 설정되지 않아 슬랙 알림을 건너뜁니다.")
        return

    schedule_lines = "\n".join([f"• {strip_html_tags(s)}" for s in patch_data.get("schedule", [])])
    changes_lines = "\n".join([f"• {strip_html_tags(c)}" for c in patch_data.get("changes", [])])

    slack_message = {
        "text": f"🚀 *디아블로 II: 레저렉션 신규 패치 노트 등록!*\n*{patch_data['version']}*",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚀 {patch_data['version']} 업데이트",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🔗 *공식 공지 바로가기:*\n<{patch_data['link']}|{patch_data['link']}>"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📅 *시즌 및 패치 일정*\n{schedule_lines}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🛡️ *주요 변경 사항*\n{changes_lines}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🤖 `data/patchnotes.json` 파일에 자동 반영 완료되었습니다."
                    }
                ]
            }
        ]
    }

    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json=slack_message, timeout=10)
        if resp.status_code == 200:
            print("🔔 Slack 알림 전송 성공!")
    except Exception as e:
        print(f"⚠️ Slack 전송 중 에러: {e}")

def parse_patch_detail(url):
    print(f"🔍 본문 상세 파싱 중: {url}")
    res = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")

    for tag in soup(["script", "style", "noscript", "iframe", "header", "footer", "nav"]):
        tag.decompose()

    article_body = soup.select_one(".Article-content, .NewsBlog-content, article, main")
    if not article_body:
        article_body = soup.body

    lines = [clean_text(line) for line in article_body.get_text("\n").splitlines()]
    lines = [l for l in lines if l and len(l) > 1]

    # 버전 번호 추출
    h1 = soup.select_one("h1, .Article-title")
    title_text = clean_text(h1.get_text()) if h1 else ""
    version_match = re.search(r'(\d+\.\d+(\.\d+)?)', title_text + " " + " ".join(lines[:30]))
    version_num = version_match.group(1) if version_match else "3.3"
    
    season_match = re.search(r'시즌\s*(\d+)', title_text + " " + " ".join(lines[:30]))
    season_str = f" (래더 시즌 {season_match.group(1)} 적용)" if season_match else ""
    version_title = f"{version_num} 패치{season_str}"

    # 1. 일정(Schedule) 정밀 파싱: 날짜/시간이 포함된 실제 일정 문장만 필터링
    schedules = []
    for line in lines:
        # "일정:", "래더 15시즌" 같은 단순 제목 행 제외하고 실제 일정(종료/배포/시작 + 날짜 표기)만 수집
        if any(term in line for term in ["종료", "배포", "시작"]) and any(d in line for d in ["월", "일", "/", "시"]):
            if any(bad in line for bad in ["window.", "dataLayer", "목차", "일정:"]):
                continue
            
            clean_s = line.strip()
            # 가장 중요한 시즌 시작 일정은 볼드 처리
            if "시작" in clean_s:
                schedules.append(f"<b>{clean_s}</b>")
            else:
                schedules.append(clean_s)
        
        if len(schedules) >= 3:
            break

    # 2. 변경 사항(Changes) 파싱
    changes = []
    if "비래더" in " ".join(lines) or "스탠다드" in " ".join(lines):
        runewords = [w for w in ["광기", "발작", "탈태", "접지", "담금질", "화로", "치료", "방벽"] if w in " ".join(lines)]
        if runewords:
            changes.append(f"<b>비레더(스탠다드) 이관:</b> 이전 래더 전용이었던 룬어 아이템들({', '.join(runewords)})을 이제 비레더 환경에서도 제작 및 사용 가능")

    if any(k in " ".join(lines) for k in ["천사의 의복", "점멸박쥐", "재앙의 재", "전투가지", "마날드"]):
        changes.append("<b>초중반 유니크·세트 상향:</b> 육성 구간에 쓰이는 일부 고유 장비(점멸박쥐, 재앙의 재, 전투가지 등) 및 천사의 의복 세트 대거 상향")

    if "파괴 부적" in " ".join(lines) or "공포의 영역" in " ".join(lines) or "파괴참" in " ".join(lines):
        changes.append("<b>파괴참 드랍 조정:</b> '잠복하는 파괴 부적' 최소 드랍 레벨 상향(75LV) 및 매찬 적용 드랍률 조정, 지옥 난이도 한정 드랍으로 변경")

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

    for item in patches:
        item["isActive"] = False
        item["isOpen"] = False
        item["badge"] = "📜"

    patches.insert(0, new_patch)
    save_patch_notes(patches)
    print(f"🎉 성공: '{new_patch['version']}' 항목이 추가되었습니다!")

    send_slack_notification(new_patch)

if __name__ == "__main__":
    main()
