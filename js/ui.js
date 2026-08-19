/**
 * @file ui.js
 * @description 섹션 탭 전환 및 아코디언 토글 등 기본 화면 UI 인터랙션 제어 모듈
 * @author LEVI SHIN (악군 패키지 백과사전 프로젝트)
 */

export function switchSection(evt, sectionId) {
    document.querySelectorAll('.content-section').forEach(sec => sec.classList.remove('active'));
    document.querySelectorAll('.nav-menu button').forEach(btn => btn.classList.remove('active'));
    document.getElementById(sectionId)?.classList.add('active');
    if (evt && evt.currentTarget) evt.currentTarget.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

export function toggleAccordion(headerEl) { 
    headerEl.parentElement.classList.toggle('open'); 
}

// 예시: 카드 렌더링 함수 내부
const ladderBadge = item.isLadder 
    ? '<span class="badge ladder">래더 전용</span>' 
    : '<span class="badge standard">비래더 가능</span>';

// HTML 구조에 ${ladderBadge} 삽입
cardElement.innerHTML = `
    <h3>${item.legacyKey}</h3>
    ${ladderBadge}
    <p class="recipe">${item.recipe}</p>
    <p class="base">${item.base}</p>
    <p class="stats">${item.stats}</p>
`;