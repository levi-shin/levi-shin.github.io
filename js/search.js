/**
 * @file search.js
 * @description 사이트 전역 통합 실시간 검색 및 우선순위(핵심 결과 + 연관 사용처) 매칭 모듈
 * @author LEVI SHIN (악군 패키지 백과사전 프로젝트)
 */

// 빌드 데이터 내에 특정 아이템/룬어가 사용되는지 역으로 추적하여 연관 사용처를 찾는 함수
function findRelatedBuilds(keyword) {
    if (!window.DATA || !window.DATA.builds) return [];
    const results = [];
    const lowerKeyword = keyword.toLowerCase();

    window.DATA.builds.forEach(build => {
        let isMatched = false;
        
        const checkSegments = (segments) => {
            if (!Array.isArray(segments)) return;
            segments.forEach(seg => {
                const name = (seg.name || seg.target || seg.value || "").toLowerCase();
                if (name.includes(lowerKeyword)) {
                    isMatched = true;
                }
            });
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
}

// 🌟 핵심 실시간 통합 검색 함수
export function filterContent() {
    const inputEl = document.getElementById('searchInput');
    if (!inputEl) return;
    
    const filter = inputEl.value.toLowerCase().trim();
    
    if (!filter) {
        clearSearchResultsUI();
        return;
    }

    if (!window.DATA || (!window.DATA.runewords && !window.DATA.uniques)) {
        return;
    }

    const primaryMatches = [];

    // 1. 룬어 검색 (legacyKey, name, recipe, base 등 포괄적 매칭)
    if (Array.isArray(window.DATA.runewords)) {
        window.DATA.runewords.forEach(rw => {
            const legacyKey = String(rw.legacyKey || "").toLowerCase();
            const name = String(rw.name || "").toLowerCase();
            const recipe = String(rw.recipe || "").toLowerCase();
            const base = String(rw.base || "").toLowerCase();
            
            if (legacyKey.includes(filter) || name.includes(filter) || recipe.includes(filter) || base.includes(filter)) {
                primaryMatches.push({
                    type: 'runeword',
                    title: rw.legacyKey || rw.name,
                    category: '룬어 조합식',
                    highlight: `조합: ${rw.recipe || '-'}`,
                    subInfo: `베이스: ${rw.base || '-'}`,
                    id: rw.id
                });
            }
        });
    }

    // 2. 유니크 아이템 검색 ('요르단' 등 완벽 대응)
    if (Array.isArray(window.DATA.uniques)) {
        window.DATA.uniques.forEach(uni => {
            const name = String(uni.name || "").toLowerCase();
            const eng = String(uni.eng || "").toLowerCase();
            const legacyKey = String(uni.legacyKey || "").toLowerCase();
            const drop = String(uni.drop || "").toLowerCase();
            
            if (name.includes(filter) || eng.includes(filter) || legacyKey.includes(filter) || drop.includes(filter)) {
                primaryMatches.push({
                    type: 'unique',
                    title: uni.name || uni.legacyKey,
                    category: '유니크 아이템',
                    highlight: `베이스: ${uni.base || '-'}`,
                    subInfo: `드랍: ${uni.drop || '정보 없음'}`,
                    id: uni.id
                });
            }
        });
    }

    // 3. 연관 사용처 수집 (종결 빌드 탐색)
    const relatedBuilds = findRelatedBuilds(filter);

    // 4. 통합 검색 결과 UI 렌더링
    renderGlobalSearchResults(filter, primaryMatches, relatedBuilds);
}

// 통합 검색 결과를 시각적으로 그려주는 헬퍼 함수
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
            const clickAction = item.type === 'runeword' ? `openRuneModal(${item.id})` : `openUniqueModal(${item.id})`;
            html += `
                <div onclick="${clickAction}; closeGlobalSearch();" style="padding: 8px; border-radius: 6px; cursor: pointer; background: rgba(255,255,255,0.03); margin-bottom: 4px; transition: background 0.2s;" onmouseover="this.style.background='rgba(196,154,69,0.15)'" onmouseout="this.style.background='rgba(255,255,255,0.03)'">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: var(--gold, #dfb15b); font-weight: bold;">${item.title}</span>
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

export function filterBuilds(evt, tag) {
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

// 🌟 HTML의 onkeyup="filterContent()"가 이 함수를 확실히 찾을 수 있도록 전역 객체에 등록합니다.
window.filterContent = filterContent;
window.filterBuilds = filterBuilds;