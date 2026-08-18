
/* ===== data.js ===== */
/**
 * 악군 데이터 로더
 * GitHub Pages의 정적 환경에서 JSON만 읽어 사이트 데이터를 구성합니다.
 */
const DATA = {
    meta: null,
    items: [],
    uniques: [],
    runewords: [],
    sunders: [],
    charms: [],
    ubers: [],
    builds: [],
    indexes: {
        item: new Map(),
        unique: new Map(),
        runeword: new Map(),
        sunder: new Map(),
        charm: new Map(),
        uber: new Map(),
        build: new Map()
    }
};

let loadPromise = null;

function indexRecords(type, records) {
    const map = DATA.indexes[type];
    map.clear();

    records.forEach(record => {
        map.set(Number(record.id), record);
        if (record.legacyKey) map.set(record.legacyKey, record);
        if (record.name) map.set(record.name, record);
    });
}
async function loadData() {
    if (loadPromise) return loadPromise;

    loadPromise = Promise.all([
        fetch('./data/meta.json').then(r => r.json()),
        fetch('./data/items.json').then(r => r.json()),
        fetch('./data/uniques.json').then(r => r.json()),
        fetch('./data/runewords.json').then(r => r.json()),
        fetch('./data/sunders.json').then(r => r.json()),
        fetch('./data/charms.json').then(r => r.json()),
        fetch('./data/ubers.json').then(r => r.json()),
        fetch('./data/builds.json').then(r => r.json())
    ]).then(([meta, items, uniques, runewords, sunders, charms, ubers, builds]) => {
        DATA.meta = meta;
        DATA.items = items;
        DATA.uniques = uniques;
        DATA.runewords = runewords;
        DATA.sunders = sunders;
        DATA.charms = charms;
        DATA.ubers = ubers;
        DATA.builds = builds.items ?? builds;

        indexRecords('item', DATA.items);
        indexRecords('unique', DATA.uniques);
        indexRecords('runeword', DATA.runewords);
        indexRecords('sunder', DATA.sunders);
        indexRecords('charm', DATA.charms);
        indexRecords('uber', DATA.ubers);
        indexRecords('build', DATA.builds);

        // 이름으로 남아 있던 기존 빌드 링크도 최종적으로 숫자 ID로 정규화합니다.
        resolveSegmentIds();

        return DATA;
    }).catch(error => {
        console.error('악군 JSON 데이터를 불러오지 못했습니다.', error);
        loadPromise = null;
        throw error;
    });

    return loadPromise;
}
function getRecord(type, id) {
    return DATA.indexes[type]?.get(Number(id)) ?? DATA.indexes[type]?.get(id) ?? null;
}

// 기존 빌드 데이터에 남아 있는 이름 기반/변형 표기를 안정적인 숫자 ID로 연결합니다.
// 예: "안다리엘의 두개골 (에테)" / "에테르형 안다리엘의 두개골"
// -> uniques.json의 legacyKey "안다리엘의 두개골|Andariel's Visage" -> ID 20007
function normalizeLookupName(value = "") {
    return String(value)
        .replace(/\s*\(에테\)\s*$/i, "")
        .replace(/^에테르형\s*/i, "")
        .replace(/^에테리얼\s*/i, "")
        .trim();
}

function resolveSegmentIds() {
    const types = ['unique', 'runeword', 'item', 'sunder', 'charm', 'uber'];

    DATA.builds.forEach(build => {
        const walk = segments => {
            if (!Array.isArray(segments)) return;
            segments.forEach(segment => {
                if (!segment || segment.type !== 'link' || segment.id != null) return;

                const target = normalizeLookupName(segment.target || segment.name || '');
                if (!target) return;

                for (const dataType of types) {
                    const record = DATA.indexes[dataType]?.get(target);
                    if (record) {
                        segment.id = Number(record.id);
                        segment.dataType = dataType;
                        segment.unresolved = false;
                        return;
                    }

                    const records = DATA[dataType === 'unique' ? 'uniques' : dataType === 'runeword' ? 'runewords' : dataType + 's'] || [];
                    const matched = records.find(record => {
                        const legacyName = String(record.legacyKey || '').split('|')[0].trim();
                        return normalizeLookupName(legacyName) === target;
                    });
                    if (matched) {
                        segment.id = Number(matched.id);
                        segment.dataType = dataType;
                        segment.unresolved = false;
                        return;
                    }
                }
            });
        };

        build.slots?.forEach(slot => walk(slot.content));
        build.merc?.gear?.forEach(gear => walk(gear.content));
    });
}


/* ===== ui.js ===== */
/**
 * @file ui.js
 * @description 섹션 탭 전환 및 아코디언 토글 등 기본 화면 UI 인터랙션 제어 모듈
 * @author LEVI SHIN (악군 패키지 백과사전 프로젝트)
 */
function switchSection(evt, sectionId) {
    document.querySelectorAll('.content-section').forEach(sec => sec.classList.remove('active'));
    document.querySelectorAll('.nav-menu button').forEach(btn => btn.classList.remove('active'));
    document.getElementById(sectionId)?.classList.add('active');
    if (evt && evt.currentTarget) evt.currentTarget.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
function toggleAccordion(headerEl) { 
    headerEl.parentElement.classList.toggle('open'); 
}


/* ===== search.js ===== */
/**
 * @file search.js
 * @description 사이드바 실시간 검색/필터링 및 빌드 태그 필터 기능 제어 모듈
 * @author LEVI SHIN (악군 패키지 백과사전 프로젝트)
 */
function filterBuilds(evt, tag) {
    document.querySelectorAll('.filter-tags .filter-btn').forEach(b => b.classList.remove('active'));
    if (evt && evt.currentTarget) evt.currentTarget.classList.add('active');
    const cards = document.querySelectorAll('#buildCardsGrid .card');
    cards.forEach(card => {
        const tags = card.getAttribute('data-tags');
        if (tag === 'all' || (tags && tags.includes(tag))) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
}
function filterContent() {
    const filter = document.getElementById('searchInput').value.toLowerCase().trim();
    const items = document.getElementsByClassName('searchable-item');
    for (let i = 0; i < items.length; i++) {
        const text = items[i].textContent || items[i].innerText;
        if (text.toLowerCase().indexOf(filter) > -1) {
            if (items[i].tagName === 'TR') items[i].style.display = 'table-row';
            else if (items[i].classList.contains('card')) items[i].style.display = 'flex';
            else items[i].style.display = 'block';
        } else {
            items[i].style.display = 'none';
        }
    }
}


/* ===== modal.js ===== */
/**
 * 악군 데이터 모달 렌더러
 * 데이터는 JSON에서 로드되며, 화면 간 연결은 숫자 ID를 사용합니다.
 */
let currentPaperDollText = "";
let databaseCopyText = "";

function escapeHtml(value = "") {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function openDatabaseModal() {
    document.getElementById("databaseItemModal")?.classList.add("open");
    document.body.style.overflow = "hidden";
}

function renderBuildContent(content = []) {
    return content.map(segment => {
        if (segment.type === "text") return escapeHtml(segment.value);

        if (segment.type === "link" && !segment.unresolved) {
            const fnMap = {
                unique: "openUniqueModal",
                runeword: "openRuneModal",
                item: "openItemModal",
                sunder: "openSunderModal",
                charm: "openCharmModal",
                uber: "openUberModal"
            };
            const fn = fnMap[segment.dataType];
            const className = segment.dataType === "unique" ? "unique-orange" :
                segment.dataType === "runeword" ? "rune-orange" : "gold-light";

            if (fn) {
                return `<span class="item-inline ${className}" onclick="event.stopPropagation(); ${fn}(${Number(segment.id)})">${escapeHtml(segment.name)}</span>`;
            }
        }

        return escapeHtml(segment.name || segment.target || "");
    }).join("");
}
function openPaperDollModal(buildId) {
    const data = getRecord("build", buildId);
    if (!data) {
        console.error("빌드 데이터를 찾을 수 없습니다:", buildId);
        return;
    }

    document.getElementById("pdModalTitle").textContent = data.title;
    document.getElementById("pdModalSubtitle").textContent = data.subtitle;

    const gridEl = document.getElementById("pdModalGrid");
    if (!gridEl) return;

    let htmlContent = "";

    data.slots.forEach(slot => {
        htmlContent += `
            <div class="paperdoll-slot">
                <div class="slot-title">${escapeHtml(slot.slot)}</div>
                <div class="slot-item">${renderBuildContent(slot.content)}</div>
            </div>
        `;
    });

    if (data.merc) {
        let mercHtml = `
            <div class="merc-doll-section desktop-only" style="grid-column: 1 / -1; margin-top: 15px; border-top: 1px dashed #444; padding-top: 10px;">
                <div style="color: var(--gold-light); font-weight: bold; margin-bottom: 8px; font-size: 0.9rem;">🛡️ ${escapeHtml(data.merc.title)}</div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;">`;

        data.merc.gear.forEach(gear => {
            mercHtml += `
                <div class="paperdoll-slot" style="background: #1a1a22; padding: 6px;">
                    <div class="slot-title" style="font-size:0.75rem; color:#888;">${escapeHtml(gear.slot)}</div>
                    <div class="slot-item" style="font-size:0.85rem;">${renderBuildContent(gear.content)}</div>
                </div>
            `;
        });

        mercHtml += `</div></div>`;
        htmlContent += mercHtml;
    }

    gridEl.innerHTML = htmlContent;
    document.getElementById("pdModalStats").innerHTML = `<div class="item-stat">${data.info || ""}</div>`;

    currentPaperDollText = `[${data.title}] ${data.subtitle}\n\n`;
    data.slots.forEach(slot => {
        currentPaperDollText += `● ${slot.slot}: ${slot.content.map(x => x.value || x.name || x.target || "").join("")}\n`;
    });

    document.getElementById("paperDollModal").classList.add("open");
    document.body.style.overflow = "hidden";
}
function closePaperDollModal() {
    document.getElementById("paperDollModal")?.classList.remove("open");
    document.body.style.overflow = "";
}
function copyPaperDollValue() {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(currentPaperDollText).then(() => {
            alert("종결 빌드 및 용병 세팅 정보가 클립보드에 복사되었습니다!");
        });
    } else {
        alert("복사하기 기능이 지원되지 않는 브라우저입니다.");
    }
}
function openRuneModal(runewordId) {
    const item = getRecord("runeword", runewordId);
    if (!item) {
        console.error("룬어 데이터를 찾을 수 없습니다:", runewordId);
        return;
    }

    document.getElementById("dbModalTitle").textContent = item.name || item.legacyKey;
    document.getElementById("dbModalSubtitle").textContent = "룬어 · " + (item.name || item.legacyKey);
    document.getElementById("dbModalIntro").textContent = "룬 조합 순서와 추천 종결 베이스, 그리고 으뜸 수치를 확인합니다.";
    document.getElementById("dbModalStats").innerHTML =
        `<div class="item-stat"><strong>룬 조합 순서</strong><br><span style="color:var(--rune-orange); font-weight:bold;">${item.recipe}</span></div>
         <div class="item-stat"><strong>종결 권장 베이스</strong><br>${item.base}</div>
         <div class="item-stat"><strong>으뜸(최상급) 변동 옵션</strong><br>${item.stats}</div>`;

    document.getElementById("dbModalRecipeBtn").textContent = "📋 룬 조합 복사";
    databaseCopyText = item.recipe;
    document.getElementById("dbModalArt").classList.remove("unique-art");
    openDatabaseModal();
}
function openUniqueModal(uniqueId) {
    const item = getRecord("unique", uniqueId);
    if (!item) {
        console.error("유니크 데이터를 찾을 수 없습니다:", uniqueId);
        return;
    }

    document.getElementById("dbModalTitle").textContent = item.name;
    document.getElementById("dbModalSubtitle").textContent = "유니크 · " + (item.eng || "Unique Item");
    document.getElementById("dbModalIntro").textContent = "유니크 아이템의 최상급(으뜸) 옵션 정보입니다.";
    document.getElementById("dbModalStats").innerHTML =
        `<div class="item-stat"><strong>아이템 종류 / 베이스</strong><br>${item.base}</div>
         <div class="item-stat"><strong>대표 드랍 장소</strong><br>${item.drop || "정보 없음"}</div>
         <div class="item-stat"><strong>으뜸(최상급) 옵션 스펙</strong><br><span style="color:var(--unique-orange);">${item.stats}</span></div>`;

    document.getElementById("dbModalRecipeBtn").textContent = "📋 아이템 정보 복사";
    databaseCopyText = `${item.name} (${item.eng || ""}) - ${String(item.stats).replace(/<[^>]+>/g, "")}`;
    document.getElementById("dbModalArt").classList.add("unique-art");
    openDatabaseModal();
}
function openSunderModal(sunderId) {
    const item = getRecord("sunder", sunderId);
    if (!item) return;

    document.getElementById("dbModalTitle").textContent = item.name;
    document.getElementById("dbModalSubtitle").textContent = "신 파괴참 · " + item.legacyKey + " 속성";
    document.getElementById("dbModalIntro").textContent = "드랍 장소: " + item.drop;
    document.getElementById("dbModalStats").innerHTML =
        `<div class="item-stat"><strong>업그레이드 큐빙 공식 (호라드림의 함)</strong><br><span style="color:var(--rune-orange);">${item.recipe}</span></div>
         <div class="item-stat"><strong>새로워진 파괴참 상세 스펙</strong><br><span style="color:var(--gold-light);">${item.stats}</span></div>`;

    document.getElementById("dbModalRecipeBtn").textContent = "📋 큐빙 공식 복사";
    databaseCopyText = `${item.name} 공식: ${item.recipe}`;
    document.getElementById("dbModalArt").classList.remove("unique-art");
    openDatabaseModal();
}
function openCharmModal(charmId) {
    const item = getRecord("charm", charmId);
    if (!item) return;

    document.getElementById("dbModalTitle").textContent = item.name;
    document.getElementById("dbModalSubtitle").textContent = "종결 부적 정보";
    document.getElementById("dbModalIntro").textContent = "획득 방법: " + item.drop;
    document.getElementById("dbModalStats").innerHTML =
        `<div class="item-stat"><strong>부적 고유 옵션 스펙</strong><br><span style="color:var(--gold-light);">${item.stats}</span></div>`;

    document.getElementById("dbModalRecipeBtn").textContent = "📋 정보 복사";
    databaseCopyText = `${item.name} - ${String(item.stats).replace(/<[^>]+>/g, "")}`;
    document.getElementById("dbModalArt").classList.remove("unique-art");
    openDatabaseModal();
}
function openUberModal(uberId) {
    const item = getRecord("uber", uberId);
    if (!item) return;

    document.getElementById("dbModalTitle").textContent = item.name;
    document.getElementById("dbModalSubtitle").textContent = "우버 바바 · 전용 주얼 족보";
    document.getElementById("dbModalIntro").textContent = item.summon;
    document.getElementById("dbModalStats").innerHTML =
        `<div class="item-stat"><strong>드랍 주얼 및 부적 상세 스펙</strong><br>${item.stats}</div>`;

    document.getElementById("dbModalRecipeBtn").textContent = "📋 정보 복사";
    databaseCopyText = `${item.name} - 드랍 보상 스펙 정보`;
    document.getElementById("dbModalArt").classList.remove("unique-art");
    openDatabaseModal();
}
function openHistoryModal() {
    const bodyEl = document.getElementById("historyModalBody");
    if (!bodyEl || !DATA.meta) return;

    bodyEl.innerHTML = DATA.meta.history.map(history => `
        <div style="border-bottom: 1px solid #262630; padding: 10px 0;">
            <strong style="color:var(--gold-light);">${history.version}</strong>
            <span style="font-size:0.8rem; color:#888;">(${history.date})</span><br>
            <span>- ${history.desc}</span>
        </div>
    `).join("");

    document.getElementById("historyModal").style.display = "flex";
    document.body.style.overflow = "hidden";
}
function closeHistoryModal() {
    const modal = document.getElementById("historyModal");
    if (modal) modal.style.display = "none";
    document.body.style.overflow = "";
}
function closeDatabaseModal() {
    document.getElementById("databaseItemModal")?.classList.remove("open");
    document.body.style.overflow = "";
}
function copyDatabaseValue() {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(databaseCopyText).then(() => {
            alert("정보를 클립보드에 복사했습니다!");
        }).catch(() => alert(databaseCopyText));
    } else {
        alert(databaseCopyText);
    }
}
function openItemModal(itemId) {
    const item = getRecord("item", itemId);
    const modal = document.getElementById("itemModal");
    if (!item || !modal) {
        console.error("아이템 데이터를 찾을 수 없습니다:", itemId);
        return;
    }

    document.getElementById("itemModalTitle").textContent = item.title;
    document.getElementById("itemModalSubtitle").textContent = item.subtitle;
    document.getElementById("itemModalIntro").textContent = item.intro;
    document.getElementById("itemModalNote").textContent = item.note;

    const stats = document.getElementById("itemModalStats");
    stats.innerHTML = item.stats.map(([label, value]) =>
        `<div class="item-stat"><strong>${label}</strong><br>${value}</div>`
    ).join("");

    modal.dataset.recipe = item.recipe;
    modal.classList.add("open");
    document.body.style.overflow = "hidden";
}
function closeItemModal() {
    const modal = document.getElementById("itemModal");
    if (modal) modal.classList.remove("open");
    document.body.style.overflow = "";
}
function copyItemRecipe() {
    const modal = document.getElementById("itemModal");
    const recipe = modal?.dataset.recipe || "";
    if (!recipe) return;

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(recipe).then(() => {
            alert(`조합 순서를 복사했습니다.\n${recipe}`);
        }).catch(() => alert(`조합 순서: ${recipe}`));
    } else {
        alert(`조합 순서: ${recipe}`);
    }
}


/* ===== feedback.js ===== */
/**
 * @file feedback.js
 * @description 사용자 제보 및 피드백 모달 창 조작과 Slack 백그라운드 웹훅 전송 모듈
 * @author LEVI SHIN (악군 패키지 백과사전 프로젝트)
 */
function openFeedbackModal() {
    const modal = document.getElementById('feedbackModal');
    if (modal) modal.style.display = 'flex';
}
function closeFeedbackModal() {
    const modal = document.getElementById('feedbackModal');
    if (modal) modal.style.display = 'none';
}
function handleFeedbackSubmit(e) {
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
        alert(`⚠️ 오늘의 제보 한도(${MAX_DAILY_LIMIT}회)를 모두 사용하셨습니다.\n내일 자정 이후 다시 제보해 주세요. 감사합니다!`);
        closeFeedbackModal();
        return;
    }

    const type = document.getElementById('fbType').value;
    const content = document.getElementById('fbContent').value;
    
    const part1 = "https://hooks.slack.com/services/";
    const part2 = "T02Q2UZ4WAE/B083RNE4GFK/";
    const part3 = "Dmve8CyTAJwHKFYZ2UGk4hbs";
    const SLACK_WEBHOOK_URL = part1 + part2 + part3;

    const nextCount = currentCount + 1;

    const payload = {
        text: `📢 *[디아2 백과사전] 새로운 제보/피드백이 접수되었습니다! (오늘 유저 제보 ${nextCount}/${MAX_DAILY_LIMIT}회)*`,
        attachments: [
            {
                color: "#dfb15b",
                fields: [
                    { title: "📌 제보 유형", value: type, short: true },
                    { title: "⏰ 접수 시간", value: new Date().toLocaleString(), short: true },
                    { title: "📝 상세 내용", value: content, short: false }
                ]
            }
        ]
    };

    localStorage.setItem(COUNT_KEY, nextCount.toString());

    const remaining = MAX_DAILY_LIMIT - nextCount;
    alert(`[${type}] 제보가 정상 수신되었습니다! (오늘 남은 제보 횟수: ${remaining}회)\n소중한 의견 감사합니다.`);
    document.getElementById('feedbackForm').reset();
    closeFeedbackModal();

    fetch(SLACK_WEBHOOK_URL, {
        method: "POST",
        mode: "no-cors",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    }).catch(err => console.error("Slack 백그라운드 전송 에러:", err));
}


/* ===== main bootstrap ===== */
/**
 * 악군 사이트 메인 진입점
 * JSON 데이터 로딩 후 공통 UI와 전역 이벤트를 연결합니다.
 */
function bindGlobalFunctions() {
    window.switchSection = switchSection;
    window.toggleAccordion = toggleAccordion;
    window.filterBuilds = filterBuilds;
    window.filterContent = filterContent;
    window.openPaperDollModal = openPaperDollModal;
    window.closePaperDollModal = closePaperDollModal;
    window.openRuneModal = openRuneModal;
    window.openUniqueModal = openUniqueModal;
    window.openSunderModal = openSunderModal;
    window.openCharmModal = openCharmModal;
    window.openUberModal = openUberModal;
    window.closeDatabaseModal = closeDatabaseModal;
    window.copyDatabaseValue = copyDatabaseValue;
    window.openItemModal = openItemModal;
    window.closeItemModal = closeItemModal;
    window.copyItemRecipe = copyItemRecipe;
    window.openFeedbackModal = openFeedbackModal;
    window.closeFeedbackModal = closeFeedbackModal;
    window.handleFeedbackSubmit = handleFeedbackSubmit;
    window.openHistoryModal = openHistoryModal;
    window.closeHistoryModal = closeHistoryModal;
}

// inline onclick가 DOMContentLoaded보다 먼저 실행되더라도 접근할 수 있도록
// 모듈 평가 시점에 즉시 전역 함수로 노출합니다.
bindGlobalFunctions();

function renderUniqueTable() {
    const tbody = document.getElementById('uniqueTbody');
    if (!tbody) return;

    tbody.innerHTML = DATA.uniques.map(item => `
        <tr class="searchable-item">
            <td class="unique">
                <span class="item-inline" onclick="openUniqueModal(${Number(item.id)})">${item.name}</span>
            </td>
            <td>${item.base}</td>
            <td>${item.drop || '-'}</td>
        </tr>
    `).join('');
}

function renderSiteMetadata() {
    const footerSpan = document.getElementById('siteVersionDisplay');
    if (!footerSpan || !DATA.meta) return;

    footerSpan.innerHTML =
        `<span onclick="openHistoryModal()" style="color: var(--gold-light); cursor: pointer; text-decoration: underline;">${DATA.meta.siteVersion}</span> (Updated: ${DATA.meta.lastUpdated})`;
}

window.copyPaperDollValue = function () {
    const title = document.getElementById('pdModalTitle')?.innerText || "빌드 정보";
    const subtitle = document.getElementById('pdModalSubtitle')?.innerText || "";
    const grid = document.getElementById('pdModalGrid');

    if (!grid) return;

    let textToCopy = `[${title}] ${subtitle}\n\n`;
    grid.querySelectorAll('.paperdoll-slot').forEach(slot => {
        const slotName = slot.querySelector('.slot-title')?.innerText || "";
        const itemInfo = slot.querySelector('.slot-item')?.innerText || "";
        textToCopy += `● ${slotName}: ${itemInfo}\n`;
    });

    navigator.clipboard.writeText(textToCopy)
        .then(() => alert("빌드 정보가 복사되었습니다!"))
        .catch(err => console.error("복사 실패:", err));
};

async function initialize() {
    // HTML의 inline onclick가 JSON 로딩 실패 여부와 관계없이
    // 정상적으로 함수에 접근할 수 있도록 먼저 전역 함수를 연결합니다.
    bindGlobalFunctions();

    try {
        await loadData();
        renderUniqueTable();
        renderSiteMetadata();
    } catch (error) {
        console.error('악군 데이터 초기화 실패:', error);

        // file:// 로 직접 index.html을 열면 브라우저 보안 정책상
        // JSON fetch가 차단될 수 있습니다.
        if (location.protocol === 'file:') {
            console.warn(
                'JSON 데이터는 file:// 환경에서 fetch할 수 없습니다. ' +
                'VS Code Live Server 또는 GitHub Pages에서 실행하세요.'
            );
        }
    }
}

document.addEventListener('DOMContentLoaded', initialize);

window.addEventListener("click", event => {
    if (event.target.id === "databaseItemModal") closeDatabaseModal();
    if (event.target.id === "itemModal") closeItemModal();
    if (event.target.id === "paperDollModal") closePaperDollModal();
    if (event.target.id === "feedbackModal") closeFeedbackModal();
    if (event.target.id === "historyModal") closeHistoryModal();
});

window.addEventListener("keydown", event => {
    if (event.key === "Escape") {
        closeDatabaseModal();
        closeItemModal();
        closePaperDollModal();
        closeFeedbackModal();
        closeHistoryModal();
    }
});
