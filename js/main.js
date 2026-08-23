import { initDropCalc, calculateDropOdds, setDropCalcMf } from './dropcalc.js?v=2';

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
    leveling: null,
    runes: [],
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

// 🌟 브라우저 전역 객체에 DATA를 확실하게 바인딩합니다.
window.DATA = DATA;

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

    const dataVer = "16";
    loadPromise = Promise.all([
        fetch(`./data/meta.json?v=${dataVer}`).then(r => r.json()),
        fetch(`./data/items.json?v=${dataVer}`).then(r => r.json()),
        fetch(`./data/uniques.json?v=${dataVer}`).then(r => r.json()),
        fetch(`./data/runewords.json?v=${dataVer}`).then(r => r.json()),
        fetch(`./data/sunders.json?v=${dataVer}`).then(r => r.json()),
        fetch(`./data/charms.json?v=${dataVer}`).then(r => r.json()),
        fetch(`./data/ubers.json?v=${dataVer}`).then(r => r.json()),
        fetch(`./data/builds.json?v=${dataVer}`).then(r => r.json())
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
// 예: "안다리엘의 두건 (에테)" / "에테르형 안다리엘의 두건"
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
    document.querySelectorAll('.nav-menu button').forEach(btn => {
        btn.classList.remove('active');
        const onclick = btn.getAttribute('onclick') || '';
        if (onclick.includes(`'${sectionId}'`) || onclick.includes(`"${sectionId}"`)) {
            btn.classList.add('active');
        }
    });
    document.getElementById(sectionId)?.classList.add('active');
    if (evt && evt.currentTarget) evt.currentTarget.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
function toggleAccordion(headerEl) { 
    headerEl.parentElement.classList.toggle('open'); 
}


/* ===== search.js (통합 검색 로직 적용 버전) ===== */
/**
 * @file search.js
 * @description 전역 DATA 객체 기반 실시간 통합 검색 (룬어, 유니크, 연관 빌드 매칭) 및 태그 필터
 * @author LEVI SHIN (악군 패키지 백과사전 프로젝트)
 */
function cardHasTag(card, tag) {
    const tags = (card.getAttribute('data-tags') || '').split(',').map(t => t.trim()).filter(Boolean);
    return tags.includes(tag);
}

function filterBuilds(evt, tag) {
    document.querySelectorAll('.filter-tags .filter-btn').forEach(b => b.classList.remove('active'));
    if (evt && evt.currentTarget) evt.currentTarget.classList.add('active');
    const cards = document.querySelectorAll('#buildCardsGrid .card');
    cards.forEach(card => {
        card.style.display = (tag === 'all' || cardHasTag(card, tag)) ? 'flex' : 'none';
    });
}

// ==========================================
// 🛡️ 빌드 검색 전용 유틸리티 함수 (main.js 하단 추가)
// ==========================================
window.findRelatedBuilds = function(keyword) {
    if (!window.DATA || !window.DATA.builds) {
        console.warn("⚠️ window.DATA.builds가 없습니다!");
        return [];
    }
    const results = [];
    const lowerKeyword = keyword.toLowerCase();

    window.DATA.builds.forEach(build => {
        const titleText = (build.title || "").toLowerCase();
        const subtitleText = (build.subtitle || "").toLowerCase();
        
        let isMatched = titleText.includes(lowerKeyword) || subtitleText.includes(lowerKeyword);

        const checkSegments = (segments) => {
            if (Array.isArray(segments)) {
                segments.forEach(seg => {
                    const segText = (seg.name || seg.target || seg.value || "").toLowerCase();
                    if (segText.includes(lowerKeyword)) isMatched = true;
                });
            }
        };

        build.slots?.forEach(slot => checkSegments(slot.content));
        build.merc?.gear?.forEach(gear => checkSegments(gear.content));

        if (isMatched) {
            results.push({ 
                title: build.title, 
                subtitle: build.subtitle, 
                id: build.id 
            });
        }
    });

    return results;
};

// 드롭다운 렌더링 함수 오버라이드 (아이템 카드 + 종결 빌드 카드 통합)
window.renderGlobalSearchResults = function(keyword, primaries, builds) {
    let dropdown = document.getElementById('global-search-dropdown');
    if (!dropdown) {
        const searchInput = document.getElementById('searchInput');
        if (!searchInput) return;
        dropdown = document.createElement('div');
        dropdown.id = 'global-search-dropdown';
        dropdown.style.cssText = `position: absolute; top: calc(100% + 6px); left: 0; right: 0; background: #15151a; border: 1px solid var(--gold); border-radius: 8px; max-height: 400px; overflow-y: auto; z-index: 99999; box-shadow: 0 15px 35px rgba(0,0,0,0.9); padding: 10px; font-size: 0.9rem;`;
        searchInput.parentElement.style.position = 'relative';
        searchInput.parentElement.appendChild(dropdown);
    }

    if (primaries.length === 0 && builds.length === 0) {
        dropdown.innerHTML = `<div style="padding: 12px; text-align: center; color: #888;">검색 결과가 없습니다.</div>`;
    } else {
        let html = `<div style="padding: 6px 10px; font-size: 0.8rem; color: #aaa; border-bottom: 1px solid #262630; margin-bottom: 6px;">🔍 '${keyword}' 통합 검색 결과</div>`;
        
        // 1. 유니크 / 룬어 아이템 결과
        if (primaries.length > 0) {
            html += `<div style="font-size: 0.75rem; color: var(--gold); margin: 6px 4px 4px; font-weight: bold;">✨ 핵심 정보 (조합 및 스크립트)</div>`;
            primaries.forEach(item => {
                html += `
                <div onclick="open${item.type === 'runeword' ? 'Rune' : 'Unique'}Modal(${item.id}); window.closeGlobalSearch();" 
                     style="background: #1e1e24; border: 1px solid #333; border-radius: 6px; padding: 10px; margin-bottom: 6px; cursor: pointer;"
                     onmouseover="this.style.borderColor='var(--gold)'" onmouseout="this.style.borderColor='#333'">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="color: #f39c12; font-weight: bold;">${item.title}</span>
                        <span style="font-size: 0.7rem; background: #2a2a35; color: #aaa; padding: 2px 6px; border-radius: 4px;">${item.category}</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #ccc;">${item.highlight}</div>
                </div>`;
            });
        }

        // 2. 추천 종결 빌드 결과 (성공적으로 매칭된 햄딘 등 출력)
        if (builds.length > 0) {
            html += `<div style="font-size: 0.75rem; color: #38bdf8; margin: 10px 4px 4px; font-weight: bold;">🛡️ 추천 종결 빌드</div>`;
            builds.forEach(build => {
                html += `
                <div onclick="switchSection(null, 'builds'); openPaperDollModal(${build.id}); window.closeGlobalSearch();" 
                     style="background: #1e1e24; border: 1px solid #333; border-radius: 6px; padding: 10px; margin-bottom: 6px; cursor: pointer;"
                     onmouseover="this.style.borderColor='#38bdf8'" onmouseout="this.style.borderColor='#333'">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="color: #38bdf8; font-weight: bold;">${build.title}</span>
                        <span style="font-size: 0.7rem; background: #1e293b; color: #38bdf8; padding: 2px 6px; border-radius: 4px;">종결 빌드</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #ccc;">${build.subtitle}</div>
                </div>`;
            });
        }

        dropdown.innerHTML = html;
    }
    dropdown.style.display = 'block';
};

function filterContent() {
    const inputEl = document.getElementById('searchInput');
    if (!inputEl) return;
    
    const filter = inputEl.value.toLowerCase().trim();
    
    // 1. 검색어가 없을 때: 드롭다운 닫기
    if (!filter) {
        if (typeof clearSearchResultsUI === 'function') clearSearchResultsUI();
        return;
    }

    if (!window.DATA) return;

    const primaryMatches = [];

    // 2. 룬어 검색
    if (Array.isArray(window.DATA.runewords)) {
        window.DATA.runewords.forEach(rw => {
            if (matchesSearchText(rw, filter)) {
                primaryMatches.push({
                    type: 'runeword',
                    title: rw.legacyKey || rw.name,
                    category: '룬어 조합식',
                    highlight: `조합: ${rw.recipe || '-'}`,
                    id: rw.id,
                    isLadder: rw.isLadder
                });
            }
        });
    }

    // 3. 유니크 아이템 검색
    if (Array.isArray(window.DATA.uniques)) {
        window.DATA.uniques.forEach(uni => {
            if (matchesSearchText(uni, filter)) {
                primaryMatches.push({
                    type: 'unique',
                    title: uni.name || uni.legacyKey,
                    category: '유니크 아이템',
                    highlight: `베이스: ${uni.base || '-'}`,
                    id: uni.id
                });
            }
        });
    }

    // 4. 신 파괴참 검색
    if (Array.isArray(window.DATA.sunders)) {
        window.DATA.sunders.forEach(item => {
            const name = String(item.name || "").toLowerCase();
            const legacyKey = String(item.legacyKey || "").toLowerCase();
            const stats = String(item.stats || "").toLowerCase();
            
            if (name.includes(filter) || legacyKey.includes(filter) || stats.includes(filter)) {
                primaryMatches.push({
                    type: 'sunder',
                    title: item.name,
                    category: '신 파괴참',
                    highlight: `드랍: ${item.drop || '-'}`,
                    id: item.id
                });
            }
        });
    }

    // 5. 종결 부적 검색
    if (Array.isArray(window.DATA.charms)) {
        window.DATA.charms.forEach(item => {
            const name = String(item.name || "").toLowerCase();
            const stats = String(item.stats || "").toLowerCase();
            
            if (name.includes(filter) || stats.includes(filter)) {
                primaryMatches.push({
                    type: 'charm',
                    title: item.name,
                    category: '종결 부적',
                    highlight: `획득: ${item.drop || '-'}`,
                    id: item.id
                });
            }
        });
    }

    // 6. 우버 바바/주얼 검색
    if (Array.isArray(window.DATA.ubers)) {
        window.DATA.ubers.forEach(item => {
            const name = String(item.name || "").toLowerCase();
            const summon = String(item.summon || "").toLowerCase();
            const stats = String(item.stats || "").toLowerCase();
            
            if (name.includes(filter) || summon.includes(filter) || stats.includes(filter)) {
                primaryMatches.push({
                    type: 'uber',
                    title: item.name,
                    category: '우버 바바/주얼',
                    highlight: `소환/효과: ${item.summon || '-'}`,
                    id: item.id
                });
            }
        });
    }

    // 7. 육성 가이드
    if (DATA.leveling && levelingGuideMatches(DATA.leveling, filter)) {
        primaryMatches.push({
            type: 'leveling',
            title: DATA.leveling.title,
            category: '육성 가이드',
            highlight: '노말부터 지옥 자립 순서',
            id: 0
        });
    }

    // 8. 연관 빌드 탐색 ('햄' 입력 시 햄딘 빌드 수집)
    const relatedBuilds = (typeof findRelatedBuilds === 'function') ? findRelatedBuilds(filter) : [];

    // 8. 드롭다운 결과 렌더링 (메인 화면 카드는 절대 건드리지 않음)
    if (primaryMatches.length === 0 && relatedBuilds.length === 0) {
        if (typeof clearSearchResultsUI === 'function') clearSearchResultsUI();
    } else {
        if (typeof renderGlobalSearchResults === 'function') {
            renderGlobalSearchResults(filter, primaryMatches, relatedBuilds);
        }
    }
}

function renderGlobalSearchResults(keyword, primaries, builds) {
    let dropdown = document.getElementById('global-search-dropdown');
    
    if (!dropdown) {
        const searchInput = document.getElementById('searchInput');
        if (!searchInput) return;
        
        dropdown = document.createElement('div');
        dropdown.id = 'global-search-dropdown';
        dropdown.style.cssText = `
            position: absolute; top: calc(100% + 6px); left: 0; right: 0;
            background: #15151a; border: 1px solid var(--gold, #dfb15b);
            border-radius: 8px; max-height: 400px; overflow-y: auto; z-index: 99999;
            box-shadow: 0 15px 35px rgba(0,0,0,0.9); padding: 10px; font-size: 0.9rem;
        `;
        searchInput.parentElement.style.position = 'relative';
        searchInput.parentElement.appendChild(dropdown);
    }

    if (primaries.length === 0 && builds.length === 0) {
        dropdown.innerHTML = `<div style="padding: 12px; text-align: center; color: #888;">검색 결과가 없습니다.</div>`;
        dropdown.style.display = 'block';
        return;
    }

    let html = `<div style="padding: 6px 10px; font-size: 0.8rem; color: #aaa; border-bottom: 1px solid #262630; margin-bottom: 6px;">🔍 '${keyword}' 통합 검색 결과</div>`;

    if (primaries.length > 0) {
        html += `<div style="margin-bottom: 8px;"><div style="font-size: 0.75rem; color: var(--gold-light, #f3e5ab); font-weight: bold; margin-bottom: 4px;">✨ 핵심 정보 (조합 및 스펙)</div>`;
        primaries.slice(0, 5).forEach(item => {
            // 🌟 아이템 타입별 올바른 모달 함수 매핑
            let clickAction = `openUniqueModal(${item.id})`;
            if (item.type === 'runeword') clickAction = `openRuneModal(${item.id})`;
            else if (item.type === 'sunder') clickAction = `openSunderModal(${item.id})`;
            else if (item.type === 'charm') clickAction = `openCharmModal(${item.id})`;
            else if (item.type === 'uber') clickAction = `openUberModal(${item.id})`;
            else if (item.type === 'leveling') clickAction = `switchSection(null, 'leveling')`;

            // 🌟 래더 전용 여부 확인 및 배지 생성 (item 데이터에 isLadder 또는 ladder 속성이 true일 때)
            let ladderBadge = '';
            if (item.isLadder || item.ladder) {
                ladderBadge = `<span style="font-size: 0.65rem; background: #7f1d1d; color: #fca5a5; padding: 1px 5px; border-radius: 4px; margin-left: 6px; font-weight: normal; vertical-align: middle;">래더전용</span>`;
            }

            html += `
                <div onclick="${clickAction}; closeGlobalSearch();" style="padding: 8px; border-radius: 6px; cursor: pointer; background: rgba(255,255,255,0.03); margin-bottom: 4px; transition: background 0.2s;" onmouseover="this.style.background='rgba(196,154,69,0.15)'" onmouseout="this.style.background='rgba(255,255,255,0.03)'">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="color: var(--gold, #dfb15b); font-weight: bold;">${item.title}</span>
                            ${ladderBadge}
                        </div>
                        <span style="font-size: 0.75rem; color: #888; background: #222; padding: 2px 6px; border-radius: 4px;">${item.category}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #ddd; margin-top: 2px;">${item.highlight}</div>
                </div>
            `;
        });
        html += `</div>`;
    }

    if (builds.length > 0) {
        html += `<div><div style="font-size: 0.75rem; color: #38bdf8; font-weight: bold; margin-bottom: 4px;">🛡️ 연관 사용처 (종결 빌드 세팅)</div>`;
        builds.slice(0, 5).forEach(build => {
            html += `
                <div onclick="switchSection(null, 'builds'); openPaperDollModal(${build.id}); closeGlobalSearch();" style="padding: 8px; border-radius: 6px; cursor: pointer; background: rgba(255,255,255,0.03); margin-bottom: 4px; transition: background 0.2s;" onmouseover="this.style.background='rgba(56,189,248,0.1)'" onmouseout="this.style.background='rgba(255,255,255,0.03)'">
                    <div style="color: #38bdf8; font-weight: bold;">${build.title}</div>
                    <div style="font-size: 0.8rem; color: #aaa;">${build.subtitle}</div>
                </div>
            `;
        });
        html += `</div>`;
    }

    dropdown.innerHTML = html;
    dropdown.style.display = 'block';
}

// ==========================================
// 🛡️ 빌드 검색 전용 유틸리티 함수
// ==========================================
window.findRelatedBuilds = function(keyword) {
    if (!window.DATA || !window.DATA.builds) {
        console.warn("⚠️ window.DATA.builds가 없습니다!");
        return [];
    }
    const results = [];
    const lowerKeyword = keyword.toLowerCase();

    window.DATA.builds.forEach(build => {
        const titleText = (build.title || "").toLowerCase();
        const subtitleText = (build.subtitle || "").toLowerCase();
        
        let isMatched = titleText.includes(lowerKeyword) || subtitleText.includes(lowerKeyword);

        const checkSegments = (segments) => {
            if (Array.isArray(segments)) {
                segments.forEach(seg => {
                    const segText = (seg.name || seg.target || seg.value || "").toLowerCase();
                    if (segText.includes(lowerKeyword)) isMatched = true;
                });
            }
        };

        build.slots?.forEach(slot => checkSegments(slot.content));
        build.merc?.gear?.forEach(gear => checkSegments(gear.content));

        if (isMatched) {
            results.push({ 
                title: build.title, 
                subtitle: build.subtitle, 
                id: build.id 
            });
        }
    });

    return results;
};

function clearSearchResultsUI() {
    const dropdown = document.getElementById('global-search-dropdown');
    if (dropdown) {
        dropdown.style.display = 'none';
        dropdown.innerHTML = '';
    }
}

window.closeGlobalSearch = function() {
    clearSearchResultsUI();
    const inputEl = document.getElementById('searchInput');
    if (inputEl) inputEl.value = '';
};

window.addEventListener('click', (e) => {
    const dropdown = document.getElementById('global-search-dropdown');
    const searchInput = document.getElementById('searchInput');
    if (dropdown && searchInput) {
        if (!dropdown.contains(e.target) && !searchInput.contains(e.target)) {
            clearSearchResultsUI();
        }
    }
});


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

function setDbModalImage(imagePath) {
    const artEl = document.getElementById("dbModalArt");
    if (!artEl) return;

    const fallback = () => { artEl.innerHTML = '<div class="d2-item-art"><div class="d2-armor"></div></div>'; };

    if (!imagePath) { fallback(); return; }

    const img = document.createElement("img");
    img.className = "db-modal-img";
    img.src = `items/${imagePath}`;
    img.alt = "";
    img.onerror = fallback;
    artEl.innerHTML = "";
    artEl.appendChild(img);
}

function matchesSearchText(item, filter) {
    const fields = [
        item.name,
        item.eng,
        item.legacyKey,
        item.drop,
        item.recipe,
        item.base,
        item.summon,
        item.stats
    ];
    if (fields.some(v => String(v || "").toLowerCase().includes(filter))) return true;
    if (Array.isArray(item.aliases)) {
        return item.aliases.some(alias => String(alias).toLowerCase().includes(filter));
    }
    return false;
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
function renderBuildGuide(data) {
    const rows = [];
    const pushRow = (label, value, extraClass = "") => {
        if (!value) return;
        rows.push(`<div class="item-stat${extraClass ? ` ${extraClass}` : ""}"><strong>${label}</strong><br>${escapeHtml(value)}</div>`);
    };

    pushRow("📊 스탯", data.stats);
    pushRow("🎒 인벤토리", data.inventory);
    pushRow("⚡ 스킬", data.skills);
    pushRow("🎮 운영법", data.playstyle, "build-playstyle");

    if (rows.length) return rows.join("");
    return `<div class="item-stat">${data.info || ""}</div>`;
}

function buildPaperDollCopyText(data) {
    let text = `[${data.title}] ${data.subtitle}\n\n`;
    (data.slots || []).forEach(slot => {
        text += `● ${slot.slot}: ${(slot.content || []).map(x => x.value || x.name || x.target || "").join("")}\n`;
    });
    if (data.stats) text += `\n📊 스탯: ${data.stats}`;
    if (data.inventory) text += `\n🎒 인벤토리: ${data.inventory}`;
    if (data.skills) text += `\n⚡ 스킬: ${data.skills}`;
    if (data.playstyle) text += `\n🎮 운영법: ${data.playstyle}`;
    return text;
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
            <div class="merc-doll-section">
                <div class="merc-doll-title">🛡️ ${escapeHtml(data.merc.title)}</div>
                <div class="merc-doll-gear">`;

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
    document.getElementById("pdModalStats").innerHTML = renderBuildGuide(data);

    currentPaperDollText = buildPaperDollCopyText(data);

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
function runewordLadderBadge(item) {
    return (item.isLadder || item.ladder)
        ? '<span class="ladder-badge ladder-only">🔥 래더 전용</span>'
        : '<span class="ladder-badge ladder-ok">✨ 비래더가능</span>';
}

function openRuneModal(runewordId) {
    const item = getRecord("runeword", runewordId);
    if (!item) {
        console.error("룬어 데이터를 찾을 수 없습니다:", runewordId);
        return;
    }

    const name = item.name || item.legacyKey;
    const eng = item.eng ? `<span class="item-modal-eng">(${escapeHtml(item.eng)})</span>` : "";
    const ladderBadge = runewordLadderBadge(item);
    document.getElementById("dbModalTitle").innerHTML = `${escapeHtml(name)} ${eng}`;
    document.getElementById("dbModalSubtitle").textContent = "룬어 · " + (item.eng || name);
    document.getElementById("dbModalIntro").textContent = "룬 조합 순서와 추천 종결 베이스, 그리고 으뜸 수치를 확인합니다.";
    document.getElementById("dbModalStats").innerHTML =
        `<div class="item-stat"><strong>래더 여부</strong><br>${ladderBadge}</div>
         <div class="item-stat"><strong>룬 조합 순서</strong><br><span style="color:var(--rune-orange); font-weight:bold;">${item.recipe}</span></div>
         <div class="item-stat"><strong>종결 권장 베이스</strong><br>${item.base}</div>
         <div class="item-stat"><strong>으뜸(최상급) 변동 옵션</strong><br>${item.stats}</div>`;

    document.getElementById("dbModalRecipeBtn").textContent = "📋 룬 조합 복사";
    databaseCopyText = item.recipe;
    setDbModalImage(item.image || null);
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
    setDbModalImage(item.image || null);
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
    setDbModalImage(item.image || null);
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
    setDbModalImage(item.image || null);
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
    setDbModalImage(item.image || null);
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
    const nickInput = document.getElementById('fbNick');
    if (nickInput && !nickInput.value) {
        nickInput.value = localStorage.getItem("d2_fb_nick") || "";
    }
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
    const nickInput = document.getElementById('fbNick');
    const nickname = (nickInput?.value || "").trim().slice(0, 20);
    if (nickname) localStorage.setItem("d2_fb_nick", nickname);
    
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
                    { title: "👤 닉네임", value: nickname || "익명", short: true },
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
    window.calculateDropOdds = calculateDropOdds;
    window.setDropCalcMf = setDropCalcMf;
}

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
    bindGlobalFunctions();

    try {
        await loadData();
        runewordLinkNeedles = null;
        renderUniqueTable();
        renderSiteMetadata();
        await Promise.all([loadLevelingGuide(), loadRuneList()]);
        await initDropCalc();
    } catch (error) {
        console.error('악군 데이터 초기화 실패:', error);

        if (location.protocol === 'file:') {
            console.warn(
                'JSON 데이터는 file:// 환경에서 fetch할 수 없습니다. ' +
                'VS Code Live Server 또는 GitHub Pages에서 실행하세요.'
            );
        }
    }
}

async function loadPatchNotes() {
    try {
        const response = await fetch('data/patchnotes.json?v=12');
        const patches = await response.json();
        
        const container = document.getElementById('patch-notes-container');
        if (!container) return;

        container.innerHTML = patches.map(patch => {
            const activeClass = patch.isActive ? 'always-gold' : 'always-gray';
            
            const linkButtonHtml = patch.link ? `
                <a href="${patch.link}" target="_blank" rel="noopener noreferrer" class="patch-external-link" onclick="event.stopPropagation()" title="공식 패치 노트 원문 보기">
                    🔗
                </a>
            ` : '';

            return `
                <div class="patch-accordion ${patch.isOpen ? 'open' : ''} ${activeClass} searchable-item">
                    <div class="patch-header" onclick="toggleAccordion(this)">
                        <span class="patch-title-text">${patch.badge} ${patch.version}</span>
                        <div class="patch-header-right">
                            ${linkButtonHtml}
                        </div>
                    </div>
                    <div class="patch-body">
                        ${patch.schedule.length > 0 ? `
                            <h4>📅 시즌 일정</h4>
                            <ul>
                                ${patch.schedule.map(s => `<li>${s}</li>`).join('')}
                            </ul>
                        ` : ''}
                        <h4>🛡️ 주요 변경 사항</h4>
                        <ul>
                            ${patch.changes.map(c => `<li>${c}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('패치 노트를 불러오지 못했습니다:', error);
    }
}

function levelingGuideMatches(guide, filter) {
    if (!guide || !filter) return false;
    const haystack = [
        guide.title,
        guide.intro,
        guide.seasonNote,
        ...(guide.aliases || []),
        ...(guide.classes || []).flatMap(c => [c.name, c.badge, c.text]),
        ...(guide.stages || []).flatMap(s => [s.title, s.goal, ...(s.steps || [])]),
        ...(guide.runewords || []).flatMap(r => [r.name, r.when, r.why]),
        ...(guide.countess || []).flatMap(c => [c.diff, c.runes, c.tip]),
        ...(guide.sockets || []).flatMap(s => [s.diff, s.use]),
        ...(guide.tips || [])
    ].join(' ').toLowerCase();
    return haystack.includes(filter);
}

function levelingRuneLabel(id, name) {
    const item = typeof getRecord === 'function' ? getRecord('runeword', id) : null;
    if (item) {
        return `<span class="item-inline rune" onclick="openRuneModal(${Number(id)})">${name}</span>`;
    }
    return `<span class="rune">${name}</span>`;
}

function escapeRegExp(value) {
    return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

let runewordLinkNeedles = null;

function getRunewordLinkNeedles() {
    if (runewordLinkNeedles) return runewordLinkNeedles;

    const seen = new Map();
    const add = (needle, id) => {
        if (!needle || String(needle).length < 2) return;
        if (!seen.has(needle)) seen.set(needle, id);
    };

    (DATA.runewords || []).forEach(rw => {
        add(rw.name, rw.id);
        (rw.aliases || []).forEach(alias => add(alias, rw.id));
    });

    [
        ['호토', 30019],
        ['오심', 30019],
        ['HOTO', 30019],
        ['CTA', 30006],
        ['서약', 30004],
        ['꺼불', 30030],
        ['에니그마', 30022]
    ].forEach(([needle, id]) => add(needle, id));

    runewordLinkNeedles = [...seen.entries()]
        .sort((a, b) => b[0].length - a[0].length)
        .map(([needle, id]) => ({ needle, id, escaped: escapeRegExp(needle) }));

    return runewordLinkNeedles;
}

function linkRunewordsInText(text) {
    const raw = String(text || '');
    const needles = getRunewordLinkNeedles();
    if (!raw || !needles.length) return raw;

    const pattern = new RegExp(needles.map(n => n.escaped).join('|'), 'g');
    const lookup = Object.fromEntries(needles.map(n => [n.needle, n.id]));

    return raw.replace(pattern, matched => {
        const id = lookup[matched];
        const item = typeof getRecord === 'function' ? getRecord('runeword', id) : null;
        if (!item) return matched;
        return `<span class="item-inline rune" onclick="openRuneModal(${Number(id)})">${matched}</span>`;
    });
}

function runeTierBadge(tier) {
    if (tier === 'high') {
        return '<span class="badge rune-tier-high">고급 룬</span>';
    }
    if (tier === 'mid') {
        return '<span class="badge rune-tier-mid">중급 룬</span>';
    }
    return '<span class="badge rune-tier-low">하급 룬</span>';
}

async function loadRuneList() {
    try {
        const response = await fetch('data/runes.json?v=16');
        const runes = await response.json();
        DATA.runes = runes;
        if (window.DATA) window.DATA.runes = runes;

        const tbody = document.getElementById('runeListTbody');
        if (!tbody) return;

        tbody.innerHTML = runes.map(rune => `
            <tr class="searchable-item">
                <td>${rune.num}번</td>
                <td class="rune">${rune.name} (${rune.eng})</td>
                <td>${runeTierBadge(rune.tier)}</td>
                <td>${rune.upgrade}</td>
                <td>${rune.use}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('룬 번호표를 불러오지 못했습니다:', error);
    }
}

function levelingBuildButtons(entry) {
    const buttons = Array.isArray(entry.buildIds) && entry.buildIds.length
        ? entry.buildIds
        : (entry.buildId ? [{ id: entry.buildId, label: '종결 세팅 보기' }] : []);
    return buttons.map(btn => `
        <button type="button" class="btn-detail" onclick="switchSection(null, 'builds'); openPaperDollModal(${Number(btn.id)})">${btn.label}</button>
    `).join('');
}

function renderLevelingGuide(guide) {
    const root = document.getElementById('levelingRoot');
    if (!root || !guide) return;

    const classCards = (guide.classes || []).map(cls => `
        <div class="leveling-class-card searchable-item">
            <span class="leveling-class-badge">${cls.badge}</span>
            <h3>${cls.name}</h3>
            <p>${linkRunewordsInText(cls.text)}</p>
            ${levelingBuildButtons(cls)}
        </div>
    `).join('');

    const stages = (guide.stages || []).map(stage => `
        <article class="leveling-stage searchable-item" id="leveling-${stage.id}">
            <h3>${stage.title}</h3>
            <p class="leveling-goal">${linkRunewordsInText(stage.goal)}</p>
            <ol>${(stage.steps || []).map(step => `<li>${linkRunewordsInText(step)}</li>`).join('')}</ol>
            ${stage.buildIds ? `<div class="leveling-stage-actions">${levelingBuildButtons(stage)}</div>` : ''}
        </article>
    `).join('');

    const runeRows = (guide.runewords || []).map(rw => `
        <tr class="searchable-item">
            <td>${levelingRuneLabel(rw.id, rw.name)}</td>
            <td>${rw.when}</td>
            <td>${rw.why}</td>
        </tr>
    `).join('');

    const countessRows = (guide.countess || []).map(row => `
        <tr class="searchable-item">
            <td class="highlight">${row.diff}</td>
            <td>${row.runes}</td>
            <td>${linkRunewordsInText(row.tip)}</td>
        </tr>
    `).join('');

    const socketRows = (guide.sockets || []).map(row => `
        <tr class="searchable-item">
            <td class="highlight">${row.diff}</td>
            <td>${linkRunewordsInText(row.use)}</td>
        </tr>
    `).join('');

    const tips = (guide.tips || []).map(tip => `<li class="searchable-item">${linkRunewordsInText(tip)}</li>`).join('');

    root.innerHTML = `
        <div class="leveling-note searchable-item">${guide.intro}</div>
        <div class="leveling-note season searchable-item">${guide.seasonNote}</div>
        <h3 class="leveling-subhead">직업별 시즌 초 운영</h3>
        <div class="leveling-class-grid">${classCards}</div>
        ${stages}
        <h3 class="leveling-subhead">만들 순서 (룬어)</h3>
        <div class="leveling-table-wrap">
            <table>
                <thead><tr><th>룬어</th><th>구간</th><th>왜 만드나</th></tr></thead>
                <tbody>${runeRows}</tbody>
            </table>
        </div>
        <h3 class="leveling-subhead">카운테스 룬 구간</h3>
        <div class="leveling-table-wrap">
            <table>
                <thead><tr><th>난이도</th><th>드랍 룬</th><th>쓰임</th></tr></thead>
                <tbody>${countessRows}</tbody>
            </table>
        </div>
        <h3 class="leveling-subhead">라주크 소켓은 아껴 두세요</h3>
        <div class="leveling-table-wrap">
            <table>
                <thead><tr><th>난이도</th><th>권장 사용</th></tr></thead>
                <tbody>${socketRows}</tbody>
            </table>
        </div>
        <h3 class="leveling-subhead">놓치기 쉬운 점</h3>
        <ul style="margin: 0 0 12px 1.2rem; font-size: 0.9rem; word-break: keep-all;">${tips}</ul>
        <div class="leveling-note">버스는 <span class="item-inline" onclick="switchSection(null, 'bus')">11. 버스 가이드</span>, 퀘스트 보상은 <span class="item-inline" onclick="switchSection(null, 'quest')">10. 영구보상 퀘스트</span>, 용병은 <span class="item-inline" onclick="switchSection(null, 'merc')">8. 용병 세팅</span>을 이어서 보시면 됩니다.</div>
    `;
}

async function loadLevelingGuide() {
    try {
        const response = await fetch('data/leveling.json?v=16');
        const guide = await response.json();
        DATA.leveling = guide;
        if (window.DATA) window.DATA.leveling = guide;
        renderLevelingGuide(guide);
    } catch (error) {
        console.error('육성 가이드를 불러오지 못했습니다:', error);
    }
}

document.addEventListener('DOMContentLoaded', loadPatchNotes);

async function loadRunewords() {
    try {
        const response = await fetch('data/runewords.json?v=16');
        const runewords = await response.json();
        
        const tbody = document.getElementById('runewordsTbody');
        if (!tbody) return;

        tbody.innerHTML = runewords.map(item => {
            const badgeHtml = runewordLadderBadge(item);

            return `
                <tr class="searchable-item">
                    <td class="highlight">
                        <span class="item-inline" onclick="openRuneModal(${item.id})" style="cursor:pointer; display:inline-flex; align-items:center; gap:8px;">
                            ${item.legacyKey} ${badgeHtml}
                        </span>
                    </td>
                    <td class="rune">${item.recipe}</td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('룬어 데이터를 불러오지 못했습니다:', error);
    }
}

async function renderBuildCards() {
    const gridContainer = document.getElementById('buildCardsGrid');
    if (!gridContainer) return;

    try {
        const response = await fetch('data/builds.json?v=16'); 
        const data = await response.json();
        const builds = data.items; 

        gridContainer.innerHTML = '';

        builds.forEach(build => {
            let badgeText = build.badge || build.subtitle || build.title.split(' ')[0]; 
            let titleText = build.subtitle || build.title;
            let descText = build.stats
                || (build.info ? build.info.replace(/<[^>]*>?/gm, '') : '');
            descText = descText.trim();
            if (!descText) descText = '클릭하여 상세 장비 세팅을 확인하세요.';
            else if (descText.length > 72) descText = descText.substring(0, 72) + '...';

            let tagAttr = Array.isArray(build.tags) && build.tags.length
                ? build.tags.join(',')
                : 'farm,magic';

            const card = document.createElement('div');
            card.className = 'card searchable-item';
            card.setAttribute('data-tags', tagAttr);
            card.onclick = () => openPaperDollModal(build.id);

            card.innerHTML = `
                <span class="badge">${badgeText}</span>
                <h3>${titleText}</h3>
                <p>${descText}</p>
                <button class="btn-detail">장비 슬롯 보기</button>
            `;

            gridContainer.appendChild(card);
        });

        // ==========================================
        // ★ 핵심 추가: 카드가 동적으로 다 만들어진 직후에 
        // 기존 검색/필터 함수가 있다면 강제로 한 번 실행해 줌
        // ==========================================
        const searchInput = document.getElementById('searchInput');
        if (searchInput && searchInput.value.trim() !== '' && typeof filterBuilds === 'function') {
            // 만약 검색창에 이미 무언가 적혀있었다면 그에 맞춰 필터 적용
            filterBuilds(); 
        }

    } catch (error) {
        console.error('builds.json 불러오기 실패:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    renderBuildCards();
});

document.addEventListener('DOMContentLoaded', loadRunewords);
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

document.addEventListener('DOMContentLoaded', () => {
    const logo = document.getElementById('sidebarLogo');
    if (logo) {
        logo.addEventListener('click', () => {
            // 1. 네비게이션의 '1. 종결 빌드' 버튼 찾기
            const buildsNavBtn = document.querySelector("button[onclick*=\"switchSection(event, 'builds')\"]");
            
            // 2. 만약 switchSection 함수가 있다면 종결 빌드 섹션으로 전환
            if (typeof switchSection === 'function' && buildsNavBtn) {
                // 가짜 이벤트 객체나 첫 번째 인자로 전달해 switchSection 실행
                switchSection({ target: buildsNavBtn }, 'builds');
            }
            
            // 3. 검색창 초기화 및 전체 빌드 보기 상태로 정렬 (필요시)
            const searchInput = document.getElementById('searchInput');
            if (searchInput) searchInput.value = '';
            
            const allFilterBtn = document.querySelector('.filter-btn');
            if (allFilterBtn && typeof filterBuilds === 'function') {
                filterBuilds({ target: allFilterBtn }, 'all');
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    renderBuildCards();

    // 사이드바 로고 클릭 이벤트
    const logo = document.getElementById('sidebarLogo');
    if (logo) {
        logo.addEventListener('click', () => {
            const buildsNavBtn = document.querySelector("button[onclick*=\"switchSection(event, 'builds')\"]");
            if (typeof switchSection === 'function' && buildsNavBtn) {
                switchSection({ target: buildsNavBtn }, 'builds');
            }
        });
    }
    
    // ==========================================
    // ★ [강제 연결] 페이지 내의 모든 텍스트 입력창을 뒤져서
    // 검색창(`searchInput` 등)인 경우 입력할 때마다 filterContent가 무조건 실행되게 함
    // ==========================================
    const allInputs = document.querySelectorAll('input[type="text"]');
    allInputs.forEach(input => {
        input.addEventListener('input', () => {
            if (typeof filterContent === 'function') {
                filterContent();
            }
        });
    });
});