import { t, SITE_LANG, submitFeedbackArchive } from './site.js';
/**
 * @file feedback.js
 * @description 사용자 제보 및 피드백 모달 창 조작과 Slack 백그라운드 웹훅 전송 모듈
 * @author LEVI SHIN (악군 패키지 백과사전 프로젝트)
 */

export function openFeedbackModal() {
    const modal = document.getElementById('feedbackModal');
    if (modal) modal.style.display = 'flex';
    const nickInput = document.getElementById('fbNick');
    if (nickInput && !nickInput.value) {
        nickInput.value = localStorage.getItem("d2_fb_nick") || "";
    }
}

export function closeFeedbackModal() {
    const modal = document.getElementById('feedbackModal');
    if (modal) modal.style.display = 'none';
}

export function handleFeedbackSubmit(e) {
    e.preventDefault();
    
    const TODAY_KEY = "d2_fb_date";
    const COUNT_KEY = "d2_fb_count";
    const MAX_DAILY_LIMIT = 2;

    const todayStr = new Date().toISOString().slice(0, 10);
    const savedDate = localStorage.getItem(TODAY_KEY);
    let currentCount = parseInt(localStorage.getItem(COUNT_KEY) || "0", 10);

    if (savedDate !== todayStr) {
        localStorage.setItem(TODAY_KEY, todayStr);
        currentCount = 0;
        localStorage.setItem(COUNT_KEY, "0");
    }

    if (currentCount >= MAX_DAILY_LIMIT) {
        alert(t().feedback.limit(MAX_DAILY_LIMIT));
        closeFeedbackModal();
        return;
    }

    const type = document.getElementById('fbType').value;
    const content = document.getElementById('fbContent').value;
    const nickInput = document.getElementById('fbNick');
    const nickname = (nickInput?.value || "").trim().slice(0, 20);
    if (nickname) localStorage.setItem("d2_fb_nick", nickname);
    
    const part1 = "https://hooks.slack.com/services/";
    const part2 = "T02Q2UZ4WAE/B083RNE4GFK/";
    const part3 = "02V4MZCllgY6Vb1tC8oHM9fR";
    const SLACK_WEBHOOK_URL = part1 + part2 + part3;

    const nextCount = currentCount + 1;
    const fb = t().feedback;

    const payload = {
        text: `${fb.slackTitle(nextCount, MAX_DAILY_LIMIT)} [${fb.langTag}]`,
        attachments: [
            {
                color: "#dfb15b",
                fields: [
                    { title: fb.nick, value: nickname || fb.anon, short: true },
                    { title: fb.type, value: type, short: true },
                    { title: fb.time, value: new Date().toLocaleString(), short: true },
                    { title: fb.detail, value: content, short: false }
                ]
            }
        ]
    };

    localStorage.setItem(COUNT_KEY, nextCount.toString());

    const remaining = MAX_DAILY_LIMIT - nextCount;
    alert(fb.ok(type, remaining));
    document.getElementById('feedbackForm').reset();
    closeFeedbackModal();

    fetch(SLACK_WEBHOOK_URL, {
        method: "POST",
        mode: "no-cors",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    }).catch(err => console.error("Slack 백그라운드 전송 에러:", err));

    submitFeedbackArchive({
        nick: nickname,
        type,
        content,
        lang: SITE_LANG
    });
}
