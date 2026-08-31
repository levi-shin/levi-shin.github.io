/**
 * 매찬 대비 유니크 드랍 확률 계산기
 * 매찬을 입력하면 아이템별 확률이 목록으로 나옵니다.
 */
import { dataUrl } from './site.js';

const UNIQUE_MF_FACTOR = 250;
const SET_MF_FACTOR = 500;
const RARE_MF_FACTOR = 600;
const DROP_CALC_VER = "2";

let dropCalcData = null;

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
    const response = await fetch(dataUrl('dropcalc.json', DROP_CALC_VER));
    dropCalcData = await response.json();
    return dropCalcData;
}

function matchesItemFilter(item, query) {
    if (!query) return true;
    const haystack = `${item.name || ""} ${item.farm || ""}`.toLowerCase();
    return haystack.includes(query);
}

export async function calculateDropOdds(event) {
    if (event) event.preventDefault();

    const results = document.getElementById("dropcalcResults");
    const mf = clampMf(document.getElementById("dropcalcMf")?.value);
    const query = (document.getElementById("dropcalcItemFilter")?.value || "").trim().toLowerCase();

    try {
        const data = await loadDropCalcData();
        const uniqMf = effectiveMf(mf, UNIQUE_MF_FACTOR);
        const setMf = effectiveMf(mf, SET_MF_FACTOR);
        const rareMf = effectiveMf(mf, RARE_MF_FACTOR);
        const uniqMult = uniqueMultiplier(mf);

        const rows = (data.items || [])
            .filter(item => matchesItemFilter(item, query))
            .map(item => {
                const oneIn = scaleOneIn(item.oneIn0, uniqMult);
                return {
                    ...item,
                    oneIn,
                    chance: 1 / oneIn,
                    multiplier: uniqMult
                };
            })
            .sort((a, b) => a.oneIn - b.oneIn);

        const tableBody = rows.length
            ? rows.map(row => `
                <tr class="searchable-item">
                    <td class="unique">
                        <span class="item-inline unique" onclick="openUniqueModal(${Number(row.id)})" style="cursor:pointer;">${row.name}</span>
                        <div class="dropcalc-sub">${row.farm} 1킬 기준 · 0매찬 대비 ${row.multiplier.toFixed(2)}배</div>
                    </td>
                    <td>1 / ${formatOneIn(row.oneIn)}</td>
                    <td>${formatPercent(row.chance)}</td>
                    <td>약 ${expectedKillsForHalf(row.chance).toLocaleString("ko-KR")}회</td>
                    <td>1 / ${formatOneIn(row.oneIn0)}</td>
                </tr>
            `).join("")
            : `<tr><td colspan="5" style="color:#888;">검색하신 아이템이 목록에 없습니다.</td></tr>`;

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
            <h3 class="dropcalc-h">유니크 드랍 확률</h3>
            <table>
                <thead>
                    <tr>
                        <th>아이템</th>
                        <th>현재 확률</th>
                        <th>퍼센트</th>
                        <th>절반 확률</th>
                        <th>0매찬</th>
                    </tr>
                </thead>
                <tbody>${tableBody}</tbody>
            </table>
        `;
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
    try {
        await loadDropCalcData();
        document.getElementById("dropcalcItemFilter")?.addEventListener("input", () => {
            const results = document.getElementById("dropcalcResults");
            if (results && !results.hidden) calculateDropOdds();
        });
    } catch (error) {
        console.error("매찬 계산기 데이터를 미리 불러오지 못했습니다:", error);
    }
}
