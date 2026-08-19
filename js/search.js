/**
 * @file search.js
 * @description 사이트 전역 통합 실시간 검색 및 이벤트 자동 바인딩 모듈
 */

console.log("🔥 search.js 파일 로딩 성공!");

window.findRelatedBuilds = function(keyword) {
    if (!window.DATA || !window.DATA.builds) {
        console.warn("⚠️ window.DATA.builds가 없습니다!");
        return [];
    }
    const results = [];
    const lowerKeyword = keyword.toLowerCase();

    window.DATA.builds.forEach(build => {
        // 타이틀(성기사)이나 서브타이틀(축복받은 망치 햄딘)에 키워드가 포함되어 있는지 정밀 검사
        const titleText = (build.title || "").toLowerCase();
        const subtitleText = (build.subtitle || "").toLowerCase();
        
        let isMatched = titleText.includes(lowerKeyword) || subtitleText.includes(lowerKeyword);

        // 장비나 슬롯 내부 세부 데이터에서도 검색
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

window.filterContent = function() {
    const inputEl = document.getElementById('searchInput');
    if (!inputEl) {
        console.error("❌ [디버깅] 'searchInput' 요소를 찾을 수 없습니다!");
        return;
    }
    
    const filter = inputEl.value.toLowerCase().trim();
    console.log("🔍 [디버깅] 검색어 입력됨:", filter);

    if (!filter) {
        window.clearSearchResultsUI();
        window.filterBuilds(null, 'all');
        return;
    }

    // 1. 메인 화면 카드 검사
    const cards = document.querySelectorAll('#buildCardsGrid .card');
    console.log("📦 [디버깅] 찾은 빌드 카드 개수:", cards.length);

    if (cards.length === 0) {
        console.warn("⚠️ [디버깅] #buildCardsGrid 안에 .card가 하나도 없습니다! 동적 렌더링이 안 끝났거나 아이디가 다를 수 있습니다.");
    }

    let matchedCardCount = 0;
    cards.forEach((card, index) => {
        const text = card.textContent.toLowerCase();
        const show = text.includes(filter);
        card.style.display = show ? 'flex' : 'none';
        if (show) {
            matchedCardCount++;
            console.log(`✨ [디버깅] ${index}번째 카드 매칭 성공!`, card.querySelector('h3')?.textContent);
        }
    });

    console.log("🎯 [디버깅] 최종 매칭된 카드 수:", matchedCardCount);

    // 2. 룬어/유니크 매칭
    const primaryMatches = [];
    if (window.DATA?.runewords) {
        window.DATA.runewords.forEach(rw => {
            if (JSON.stringify(rw).toLowerCase().includes(filter)) {
                primaryMatches.push({ type: 'runeword', title: rw.name || rw.legacyKey, category: '룬어', id: rw.id });
            }
        });
    }
    const relatedBuilds = window.findRelatedBuilds(filter);

    // 3. UI 처리
    if (primaryMatches.length === 0 && relatedBuilds.length === 0 && matchedCardCount > 0) {
        window.clearSearchResultsUI();
    } else {
        renderGlobalSearchResults(filter, primaryMatches, relatedBuilds);
    }
};

function renderGlobalSearchResults(keyword, primaries, builds) {
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
        
        // 1. 룬어 및 유니크 아이템 결과 렌더링 (기존 스크린샷 스타일)
        if (primaries.length > 0) {
            html += `<div style="font-size: 0.75rem; color: var(--gold); margin: 6px 4px 4px; font-weight: bold;">✨ 핵심 정보 (조합 및 스크립트)</div>`;
            primaries.forEach(item => {
                html += `
                <div onclick="open${item.type === 'runeword' ? 'Rune' : 'Unique'}Modal(${item.id}); window.closeGlobalSearch();" 
                     style="background: #1e1e24; border: 1px solid #333; border-radius: 6px; padding: 10px; margin-bottom: 6px; cursor: pointer; transition: 0.2s;"
                     onmouseover="this.style.borderColor='var(--gold)'" onmouseout="this.style.borderColor='#333'">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="color: #f39c12; font-weight: bold;">${item.title}</span>
                        <span style="font-size: 0.7rem; background: #2a2a35; color: #aaa; padding: 2px 6px; border-radius: 4px;">${item.category}</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #ccc;">${item.highlight}</div>
                </div>`;
            });
        }

        // 2. 종결 빌드 결과 렌더링 (아이템 카드와 똑같은 디자인 적용)
        if (builds.length > 0) {
            html += `<div style="font-size: 0.75rem; color: #38bdf8; margin: 10px 4px 4px; font-weight: bold;">🛡️ 추천 종결 빌드</div>`;
            builds.forEach(build => {
                html += `
                <div onclick="switchSection(null, 'builds'); openPaperDollModal(${build.id}); window.closeGlobalSearch();" 
                     style="background: #1e1e24; border: 1px solid #333; border-radius: 6px; padding: 10px; margin-bottom: 6px; cursor: pointer; transition: 0.2s;"
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
}

window.clearSearchResultsUI = () => { const d = document.getElementById('global-search-dropdown'); if (d) d.style.display = 'none'; };
window.closeGlobalSearch = () => { window.clearSearchResultsUI(); const i = document.getElementById('searchInput'); if (i) i.value = ''; };

window.filterBuilds = (evt, tag) => {
    document.querySelectorAll('.filter-tags .filter-btn').forEach(b => b.classList.remove('active'));
    if (evt?.currentTarget) evt.currentTarget.classList.add('active');
    document.querySelectorAll('#buildCardsGrid .card').forEach(c => c.style.display = (tag === 'all' || c.getAttribute('data-tags')?.includes(tag)) ? 'flex' : 'none');
};

// ==========================================
// ★ 검색창 이벤트 강제 연결 (핵심 추가 부분)
// ==========================================
window.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', window.filterContent);
        console.log("✅ [검색 모듈] searchInput에 실시간 이벤트 리스너가 성공적으로 부착되었습니다.");
    } else {
        console.error("❌ [검색 모듈] DOM에 'searchInput'이 존재하지 않습니다!");
    }
});

window.addEventListener('click', (e) => {
    const d = document.getElementById('global-search-dropdown'), s = document.getElementById('searchInput');
    if (d && s && !d.contains(e.target) && !s.contains(e.target)) window.clearSearchResultsUI();
});