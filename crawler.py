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
    if not schedule_lines:
        schedule_lines = "• 별도 공지 일정 없음"

    changes_lines = "\n".join([f"• {strip_html_tags(c)}" for c in patch_data.get("changes", [])])
    if not changes_lines:
        changes_lines = "• 상세 내용은 링크를 확인하세요."

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

    # 전체 텍스트 수집
    raw_lines = [clean_text(line) for line in article_body.get_text("\n").splitlines()]
    lines = [l for l in raw_lines if l and len(l) > 1]
    full_text = " ".join(lines)

    # 1. 버전 및 시즌 번호 동적 파싱
    h1 = soup.select_one("h1, .Article-title")
    title_text = clean_text(h1.get_text()) if h1 else ""
    
    version_match = re.search(r'(\d+\.\d+(\.\d+)?)', title_text + " " + full_text[:1000])
    version_num = version_match.group(1) if version_match else "최신"

    season_match = re.search(r'(?:래더\s*(\d+)\s*시즌|시즌\s*(\d+)|-(\d+)$)', title_text + " " + url)
    season_num = None
    if season_match:
        season_num = season_match.group(1) or season_match.group(2) or season_match.group(3)
    else:
        body_season = re.search(r'래더\s*(\d+)\s*시즌', full_text[:1500])
        if body_season:
            season_num = body_season.group(1)

    season_str = f" (래더 시즌 {season_num} 적용)" if season_num else ""
    version_title = f"{version_num} 패치{season_str}"

    # 2. 일정(Schedule) 동적 추출
    schedules = []
    for line in lines:
        if len(line) < 10 or any(bad in line for bad in ["window.", "dataLayer", "목차", "일정:", "시작되는 래더"]):
            continue
        
        # '종료', '배포', '시작' 키워드와 함께 실제 시간/날짜가 들어있는 행 추출
        if ("종료" in line or "배포" in line or "시작" in line) and any(d in line for d in ["월", "일", "/", "시", "오전", "오후", "PDT"]):
            clean_s = line.strip()
            if "시작" in clean_s and "배포" not in clean_s:
                schedules.append(f"<b>{clean_s}</b>")
            else:
                schedules.append(clean_s)

        if len(schedules) >= 3:
            break

    # 3. 주요 변경 사항(Changes) 실제 페이지 내용 기반 동적 추출
    changes = []
    
    # 본문 내의 li 태그나 단락(p)들을 순회하며 실제 변경 문장을 추출
    elements = article_body.find_all(['h2', 'h3', 'h4', 'p', 'li'])
    current_category = ""

    for el in elements:
        text = clean_text(el.get_text())
        if not text or len(text) < 4 or any(bad in text for bad in ["목차", "댓글", "디아블로", "블리자드", "일정"]):
            continue

        # 소제목 카테고리 감지 (아이템, 버그 수정, 편의성 개선 등)
        if el.name in ['h2', 'h3', 'h4'] or (len(text) <= 15 and not any(punc in text for punc in ['.', ':', '다'])):
            if any(k in text for k in ["아이템", "공포의 영역", "버그 수정", "직업", "밸런스", "품질", "시스템", "래더", "룬"]):
                current_category = text
            continue

        # 변경 항목 문장 선별
        is_change_statement = any(verb in text for verb in [
            "추가했습니다", "감소했습니다", "증가했습니다", "제거했습니다", 
            "수정했습니다", "개선되었습니다", "변경되었습니다", "이용할 수 있습니다", "적용됩니다"
        ])

        if is_change_statement:
            # 카테고리가 있으면 카테고리 볼드 태그 추가
            prefix = f"<b>{current_category}:</b> " if current_category else "<b>주요 변경:</b> "
            formatted_change = f"{prefix}{text}"
            
            # 중복 방지 및 최대 6개 추출
            if formatted_change not in changes and len(changes) < 6:
                changes.append(formatted_change)

    # 본문 구조가 달라서 못 찾았을 경우 대비한 백업 텍스트 파싱
    if not changes:
        for line in lines:
            if any(verb in line for verb in ["추가했습니다", "감소했습니다", "증가했습니다", "수정했습니다", "개선되었습니다"]):
                if len(line) > 10 and line not in changes:
                    changes.append(f"<b>주요 내용:</b> {line}")
                if len(changes) >= 5:
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
    print(f"🎉 성공: '{new_patch['version']}' 항목이 실제 데이터 기반으로 추가되었습니다!")

    send_slack_notification(new_patch)

if __name__ == "__main__":
    main()
