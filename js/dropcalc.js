/**
 * 매찬 대비 드랍 확률 계산기
 * 유니크는 유효 매찬 배율을 적용하고, 룬은 매찬 영향을 받지 않습니다.
 */

const UNIQUE_MF_FACTOR = 250;
const SET_MF_FACTOR = 500;
const RARE_MF_FACTOR = 600;
const DROP_CALC_VER = "1";

let dropCalcData = null;
let dropCalcReady = false;

function clampMf(value) {
    const n = Number(value);
    if (!Number.isFinite(n) || n < 0) return 0;
    return Math.min(2000, Math.floor(n));
}

function effectiveMf(rawMf, factor) {
    const mf = clampMf(rawMf);
    if (!factor) return mf;
    return Math.floor((mf * factor) / (mf + factor));
}

function uniqueMultiplier(rawMf) {
    return (100 + effectiveMf(rawMf, UNIQUE_MF_FACTOR)) / 100;
}

function playerFactor(players, scaleWithPlayers) {
    if (!scaleWithPlayers) return 1;
    const n = Math.min(8, Math.max(1, Number(players) || 1));
    const odd = n % 2 === 0 ? n - 1 : n;
    if (odd >= 7) return 2.05;
    if (odd >= 5) return 1.86;
    if (odd >= 3) return 1.62;
    return 1;
}

function formatOneIn(value) {
    if (!Number.isFinite(value) || value <= 0) return "-";
    if (value < 10) return value.toFixed(1);
    return String(Math.round(value));
}

function formatPercent(chance) {
    const pct = chance * 100;
    if (pct >= 10) return `${pct.toFixed(1)}%`;
    if (pct >= 1) return `${pct.toFixed(2)}%`;
    if (pct >= 0.1) return `${pct.toFixed(2)}%`;
    return `${pct.toFixed(3)}%`;
}

function expectedKillsForHalf(chance) {
    if (!(chance > 0) || chance >= 1) return chance >= 1 ? 1 : "-";
    return Math.max(1, Math.ceil(Math.log(0.5) / Math.log(1 - chance)));
}

function scaleOneIn(oneIn0, multiplier) {
    const base = Number(oneIn0);
    if (!Number.isFinite(base) || base <= 0 || !(multiplier > 0)) return Infinity;
    return base / multiplier;
}

async function loadDropCalcData() {
    if (dropCalcData) return dropCalcData;
    const response = await fetch(`./data/dropcalc.json?v=${DROP_CALC_VER}`);
    dropCalcData = await response.json();
    return dropCalcData;
}

function renderDropRows(rows, { mfAffects, uniqueIdAttr }) {
    if (!rows.length) {
        return `<tr><td colspan="5" style="color:#888;">이 사냥터에는 표시할 항목이 없습니다.</td></tr>`;
    }

    return rows.map(row => {
        const nameHtml = row.id
            ? `<span class="item-inline unique" onclick="openUniqueModal(${Number(row.id)})" style="cursor:pointer;">${row.name}</span>`
            : row.name;
        const badge = mfAffects
            ? `<span class="dropcalc-mult">0매찬 대비 ${row.multiplier.toFixed(2)}배</span>`
            : `<span class="dropcalc-badge dropcalc-badge-ok">매찬 영향 없음</span>`;
        const nameCell = uniqueIdAttr ? ` class="unique"` : "";

        return `
            <tr class="searchable-item">
                <td${nameCell}>${nameHtml}<div class="dropcalc-sub">${badge}</div></td>
                <td>1 / ${formatOneIn(row.oneIn)}</td>
                <td>${formatPercent(row.chance)}</td>
                <td>약 ${expectedKillsForHalf(row.chance).toLocaleString("ko-KR")}킬</td>
                <td>1 / ${formatOneIn(row.oneIn0)}</td>
            </tr>
        `;
    }).join("");
}

export async function calculateDropOdds(event) {
    if (event) event.preventDefault();

    const results = document.getElementById("dropcalcResults");
    const mf = clampMf(document.getElementById("dropcalcMf")?.value);
    const sourceId = document.getElementById("dropcalcSource")?.value;
    const players = Number(document.getElementById("dropcalcPlayers")?.value) || 1;

    try {
        const data = await loadDropCalcData();
        const source = (data.sources || []).find(entry => entry.id === sourceId);
        if (!source) {
            if (results) results.innerHTML = `<p class="item-click-hint">사냥터를 선택해 주세요.</p>`;
            return;
        }

        const uniqMf = effectiveMf(mf, UNIQUE_MF_FACTOR);
        const setMf = effectiveMf(mf, SET_MF_FACTOR);
        const rareMf = effectiveMf(mf, RARE_MF_FACTOR);
        const uniqMult = uniqueMultiplier(mf);
        const pFactor = playerFactor(players, source.scaleWithPlayers);

        const itemRows = (source.items || []).map(item => {
            const oneIn = scaleOneIn(item.oneIn0, uniqMult * pFactor);
            return {
                ...item,
                oneIn,
                oneIn0: item.oneIn0,
                chance: 1 / oneIn,
                multiplier: uniqMult
            };
        }).sort((a, b) => a.oneIn - b.oneIn);

        const runeRows = (source.runes || []).map(rune => {
            const oneIn = scaleOneIn(rune.oneIn0, pFactor);
            return {
                ...rune,
                oneIn,
                oneIn0: rune.oneIn0,
                chance: 1 / oneIn,
                multiplier: 1
            };
        }).sort((a, b) => a.oneIn - b.oneIn);

        const playerNote = source.scaleWithPlayers
            ? `플레이어 ${players}인 보정이 룬·일부 드랍에 반영되었습니다.`
            : "액트 보스/핀들/카운테스는 본인 드랍에 플레이어 수 영향이 거의 없어 1인 기준으로 계산합니다.";

        results.hidden = false;
        results.innerHTML = `
            <div class="dropcalc-summary">
                <div class="dropcalc-stat">
                    <span>입력 매찬</span>
                    <strong>${mf}%</strong>
                </div>
                <div class="dropcalc-stat">
                    <span>유니크 유효 매찬</span>
                    <strong>${uniqMf}%</strong>
                    <em>체감 ${uniqMult.toFixed(2)}배</em>
                </div>
                <div class="dropcalc-stat">
                    <span>세트 유효 매찬</span>
                    <strong>${setMf}%</strong>
                </div>
                <div class="dropcalc-stat">
                    <span>레어 유효 매찬</span>
                    <strong>${rareMf}%</strong>
                </div>
            </div>
            <p class="dropcalc-source-note">${source.note || ""} ${playerNote}</p>
            ${itemRows.length ? `
            <h3 class="dropcalc-h">유니크 아이템 (1킬 기준)</h3>
            <table>
                <thead>
                    <tr>
                        <th>아이템</th>
                        <th>현재 확률</th>
                        <th>퍼센트</th>
                        <th>절반 확률 킬수</th>
                        <th>0매찬</th>
                    </tr>
                </thead>
                <tbody>
                    ${renderDropRows(itemRows, { mfAffects: true, uniqueIdAttr: true })}
                </tbody>
            </table>
            ` : ""}
            ${runeRows.length ? `
            <h3 class="dropcalc-h">룬 (1킬 기준)</h3>
            <table>
                <thead>
                    <tr>
                        <th>룬</th>
                        <th>현재 확률</th>
                        <th>퍼센트</th>
                        <th>절반 확률 킬수</th>
                        <th>0매찬</th>
                    </tr>
                </thead>
                <tbody>
                    ${renderDropRows(runeRows, { mfAffects: false, uniqueIdAttr: false })}
                </tbody>
            </table>
            ` : `<p class="item-click-hint">이 사냥터는 유니크 위주라 룬 목록을 따로 넣지 않았습니다.</p>`}
        `;
        results.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
        console.error("매찬 계산기를 불러오지 못했습니다:", error);
        if (results) {
            results.hidden = false;
            results.innerHTML = `<p class="item-click-hint">계산 데이터를 불러오지 못했습니다. 잠시 후 다시 눌러 주세요.</p>`;
        }
    }
}

export function setDropCalcMf(value) {
    const input = document.getElementById("dropcalcMf");
    if (input) input.value = String(value);
    calculateDropOdds();
}

export async function initDropCalc() {
    if (dropCalcReady) return;
    const select = document.getElementById("dropcalcSource");
    if (!select) return;

    try {
        const data = await loadDropCalcData();
        select.innerHTML = (data.sources || []).map(source =>
            `<option value="${source.id}">${source.name}</option>`
        ).join("");
        dropCalcReady = true;
    } catch (error) {
        console.error("매찬 계산기 사냥터 목록을 불러오지 못했습니다:", error);
        select.innerHTML = `<option value="">목록을 불러오지 못했습니다</option>`;
    }
}
