import { t, SITE_LANG, submitFeedbackArchive } from './site.js';
/**
 * @file feedback.js
 * @description 피드백 모달 — JSON 아카이브(repository_dispatch) 후 GHA가 Slack 알림
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

    const nextCount = currentCount + 1;

    localStorage.setItem(COUNT_KEY, nextCount.toString());

    const remaining = MAX_DAILY_LIMIT - nextCount;
    alert(t().feedback.ok(type, remaining));
    document.getElementById('feedbackForm').reset();
    closeFeedbackModal();

    submitFeedbackArchive({
        nick: nickname,
        type,
        content,
        lang: SITE_LANG
    });
}
