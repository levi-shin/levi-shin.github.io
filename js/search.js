/**
 * @file search.js
 * @description 사이드바 실시간 검색/필터링 및 빌드 태그 필터 기능 제어 모듈
 * @author LEVI SHIN (악군 패키지 백과사전 프로젝트)
 */

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

export function filterContent() {
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
