/**
 * Site preferences: section, build filter, bookmark banner.
 */

const PREFS_KEY = 'd2_prefs';
const BOOKMARK_KEY = 'd2_bookmark_dismissed';

function loadPrefs() {
    try {
        return JSON.parse(localStorage.getItem(PREFS_KEY) || '{}');
    } catch {
        return {};
    }
}

function savePrefs(prefs) {
    try {
        localStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
    } catch {
        /* ignore */
    }
}

export function saveSection(sectionId) {
    if (!sectionId) return;
    const prefs = loadPrefs();
    prefs.section = sectionId;
    savePrefs(prefs);
}

export function saveBuildFilter(tag) {
    if (!tag) return;
    const prefs = loadPrefs();
    prefs.buildFilter = tag;
    savePrefs(prefs);
}

export function getSavedSection() {
    return loadPrefs().section || 'builds';
}

export function getSavedBuildFilter() {
    return loadPrefs().buildFilter || 'all';
}

export function initBookmarkBanner() {
    if (localStorage.getItem(BOOKMARK_KEY) === '1') return;

    const sidebar = document.querySelector('.left-sidebar');
    if (!sidebar) return;

    const lang = (document.documentElement.lang || 'ko').startsWith('en') ? 'en' : 'ko';
    const isMac = /Mac|iPhone|iPad|iPod/.test(navigator.platform || navigator.userAgent);
    const shortcut = isMac ? '⌘+D' : 'Ctrl+D';

    const text =
        lang === 'en'
            ? `⭐ Press ${shortcut} to bookmark — keep this on a second monitor while farming.`
            : `⭐ ${shortcut}로 즐겨찾기하고 사냥할 때 보조 모니터에 띄워두세요.`;

    const banner = document.createElement('div');
    banner.className = 'bookmark-banner';
    banner.setAttribute('role', 'note');
    banner.innerHTML = `
        <p class="bookmark-banner-text">${text}</p>
        <button type="button" class="bookmark-banner-dismiss" aria-label="${lang === 'en' ? 'Dismiss' : '닫기'}">×</button>
    `;

    const nav = sidebar.querySelector('.nav-menu');
    if (nav) {
        sidebar.insertBefore(banner, nav);
    } else {
        sidebar.appendChild(banner);
    }

    banner.querySelector('.bookmark-banner-dismiss')?.addEventListener('click', () => {
        localStorage.setItem(BOOKMARK_KEY, '1');
        banner.remove();
    });
}

export function restoreSectionAndFilter() {
    const sectionId = getSavedSection();
    const buildFilter = getSavedBuildFilter();

    if (sectionId && sectionId !== 'builds') {
        const navBtn = document.querySelector(
            `.nav-menu button[onclick*="'${sectionId}'"], .nav-menu button[onclick*='"${sectionId}"']`
        );
        if (typeof window.switchSection === 'function' && navBtn) {
            window.switchSection({ currentTarget: navBtn, target: navBtn }, sectionId);
        }
    }

    if (buildFilter && buildFilter !== 'all') {
        applyBuildFilter(buildFilter);
    }
}

export function restoreBuildFilterAfterCards() {
    const buildFilter = getSavedBuildFilter();
    if (buildFilter && buildFilter !== 'all') {
        applyBuildFilter(buildFilter);
    }
}

function applyBuildFilter(tag) {
    if (typeof window.filterBuilds !== 'function') return;
    const filterBtn = document.querySelector(
        `.filter-tags .filter-btn[onclick*="'${tag}'"], .filter-tags .filter-btn[onclick*='"${tag}"']`
    );
    if (filterBtn) {
        window.filterBuilds({ currentTarget: filterBtn, target: filterBtn }, tag);
    }
}

export function wireLangSwitcher() {
    document.querySelectorAll('.lang-switcher a[href="/"]').forEach((a) => {
        a.addEventListener('click', () => window.__d2SaveLang?.('ko'));
    });
    document.querySelectorAll('.lang-switcher a[href="/en/"]').forEach((a) => {
        a.addEventListener('click', () => window.__d2SaveLang?.('en'));
    });
    window.__d2SeedLangIfMissing?.();
}
