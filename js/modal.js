/**
 * 악군 데이터 모달 렌더러
 * 데이터는 JSON에서 로드되며, 화면 간 연결은 숫자 ID를 사용합니다.
 */
import { DATA, getRecord } from './data.js';

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

export function openPaperDollModal(buildId) {
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

export function closePaperDollModal() {
    document.getElementById("paperDollModal")?.classList.remove("open");
    document.body.style.overflow = "";
}

export function copyPaperDollValue() {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(currentPaperDollText).then(() => {
            alert("종결 빌드 및 용병 세팅 정보가 클립보드에 복사되었습니다!");
        });
    } else {
        alert("복사하기 기능이 지원되지 않는 브라우저입니다.");
    }
}

export function openRuneModal(runewordId) {
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

export function openUniqueModal(uniqueId) {
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

export function openSunderModal(sunderId) {
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

export function openCharmModal(charmId) {
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

export function openUberModal(uberId) {
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

export function openHistoryModal() {
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

export function closeHistoryModal() {
    const modal = document.getElementById("historyModal");
    if (modal) modal.style.display = "none";
    document.body.style.overflow = "";
}

export function closeDatabaseModal() {
    document.getElementById("databaseItemModal")?.classList.remove("open");
    document.body.style.overflow = "";
}

export function copyDatabaseValue() {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(databaseCopyText).then(() => {
            alert("정보를 클립보드에 복사했습니다!");
        }).catch(() => alert(databaseCopyText));
    } else {
        alert(databaseCopyText);
    }
}

export function openItemModal(itemId) {
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

export function closeItemModal() {
    const modal = document.getElementById("itemModal");
    if (modal) modal.classList.remove("open");
    document.body.style.overflow = "";
}

export function copyItemRecipe() {
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
