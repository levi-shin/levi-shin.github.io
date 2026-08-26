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
        return

    schedule_lines = "\n".join([f"• {strip_html_tags(s)}" for s in patch_data.get("schedule", [])])
    if not schedule_lines:
        schedule_lines = "• 별도 공지 일정 없음"

    # Slack 메시지 길이 제한(4000자) 고려하여 본문 포맷팅
    changes_preview = "\n".join([f"• {strip_html_tags(c)}" for c in patch_data.get("changes", [])[:20]])
    if len(patch_data.get("changes", [])) > 20:
        changes_preview += f"\n• ... 외 {len(patch_data['changes']) - 20}개 변경 사항 (링크 확인)"

    slack_message = {
        "text": f"🚀 *디아블로 II: 레저렉션 신규 패치 노트 등록!*\n*{patch_data['version']}*",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"🚀 {patch_data['version']} 업데이트", "emoji": True}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"🔗 *공식 공지 바로가기:*\n<{patch_data['link']}|{patch_data['link']}>"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"📅 *시즌 및 패치 일정*\n{schedule_lines}"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"🛡️ *주요 변경 사항*\n{changes_preview}"}
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
    print(f"🔍 본문 파싱 중: {url}")
    res = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")

    # 스크립트/불필요 태그 제거
    for tag in soup(["script", "style", "noscript", "iframe", "header", "footer", "nav"]):
        tag.decompose()

    article_body = soup.select_one(".Article-content, .NewsBlog-content, article, main") or soup.body

    # 줄바꿈 단위로 텍스트 분리
    raw_lines = [clean_text(line) for line in article_body.get_text("\n").splitlines()]
    lines = [l for l in raw_lines if l and len(l) > 1]
    full_text = " ".join(lines)

    # 1. 버전 및 시즌 번호 추출
    h1 = soup.select_one("h1, .Article-title")
    title_text = clean_text(h1.get_text()) if h1 else ""
    version_match = re.search(r'(\d+\.\d+(\.\d+)?)', title_text + " " + full_text[:1000])
    version_num = version_match.group(1) if version_match else "3.3"

    season_match = re.search(r'(?:래더\s*(\d+)\s*시즌|시즌\s*(\d+)|-(\d+)$)', title_text + " " + url)
    season_num = season_match.group(1) if season_match else ""
    season_str = f" (래더 시즌 {season_num} 적용)" if season_num else ""
    version_title = f"{version_num} 패치{season_str}"

    # 2. 일정 파싱 (종료/배포/시작 문장)
    schedules = []
    for line in lines:
        if len(line) < 8 or any(bad in line for bad in ["window.", "dataLayer", "목차", "일정:", "시작되는 래더"]):
            continue
        if any(term in line for term in ["종료", "배포", "시작"]) and any(d in line for d in ["월", "일", "/", "시"]):
            if "시작" in line and "배포" not in line:
                schedules.append(f"<b>{line}</b>")
            else:
                schedules.append(line)
        if len(schedules) >= 3:
            break

    # 3. 본문 패치 노트 전체를 그대로 수집
    changes = []
    start_collecting = False

    for line in lines:
        # 본문 패치 노트 시작 지점 감지
        if "패치 노트" in line or "아이템" in line:
            start_collecting = True

        if not start_collecting:
            continue

        # 목차나 날짜 안내 같은 불필요한 메타 줄 제외
        if any(bad in line for bad in ["목차", "댓글", "디아블로 II: 레저렉션 래더", "지금 진행 중", "일정:"]):
            continue

        # 소제목(아이템, 공포의 영역, 버그 수정, 유혈자 등 단독 명사)은 굵게 표시
        if len(line) <= 20 and not any(v in line for v in ["했습니다", "있습니다", "됩니다", "않음", "경우"]):
            changes.append(f"<b>{line}</b>")
        else:
            changes.append(line)

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
    print(f"🎉 성공: '{new_patch['version']}' 본문 전체가 그대로 data/patchnotes.json에 추가되었습니다!")

    send_slack_notification(new_patch)

if __name__ == "__main__":
    main()
