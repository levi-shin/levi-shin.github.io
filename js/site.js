/**
 * 사이트 공통 설정 (언어·절대 경로)
 * /en/ 하위에서도 /data, /items, /css, /js 루트 자산을 쓰도록 합니다.
 */

export const SITE_ORIGIN = 'https://diablo.1125labs.com';

/** Phase 2부터 EN 전용 JSON이 있는 파일 */
const LOCALIZED_DATA_FILES = new Set([
    'uniques.json',
    'runewords.json',
    'runes.json'
]);

function detectLang() {
    if (typeof document === 'undefined') {
        return 'ko';
    }
    const htmlLang = (document.documentElement.lang || '').toLowerCase();
    if (htmlLang.startsWith('en')) return 'en';
    if (htmlLang.startsWith('ko')) return 'ko';
    if (typeof location !== 'undefined' && location.pathname.startsWith('/en')) return 'en';
    return 'ko';
}

export const SITE_LANG = detectLang();
export const SITE_HOME = SITE_LANG === 'en' ? '/en/' : '/';
export const SITE_ALT_HOME = SITE_LANG === 'en' ? '/' : '/en/';

const UI = {
    ko: {
        ladderOnly: '🔥 래더 전용',
        ladderOk: '✨ 비래더가능',
        runeTier: { high: '고급 룬', mid: '중급 룬', low: '하급 룬' },
        runeNum: (n) => `${n}번`,
        runeModal: {
            subtitle: (eng, name) => `룬어 · ${eng || name}`,
            intro: '룬 조합 순서와 추천 종결 베이스, 그리고 으뜸 수치를 확인합니다.',
            ladder: '래더 여부',
            recipe: '룬 조합 순서',
            base: '종결 권장 베이스',
            stats: '으뜸(최상급) 변동 옵션',
            copy: '📋 룬 조합 복사'
        },
        uniqueModal: {
            subtitle: (eng) => `유니크 · ${eng || 'Unique Item'}`,
            intro: '유니크 아이템의 최상급(으뜸) 옵션 정보입니다.',
            base: '아이템 종류 / 베이스',
            drop: '대표 드랍 장소',
            dropEmpty: '정보 없음',
            stats: '으뜸(최상급) 옵션 스펙',
            copy: '📋 아이템 정보 복사'
        }
    },
    en: {
        ladderOnly: '🔥 Ladder only',
        ladderOk: '✨ Non-ladder OK',
        runeTier: { high: 'High', mid: 'Mid', low: 'Low' },
        runeNum: (n) => `#${n}`,
        runeModal: {
            subtitle: (eng, name) => `Runeword · ${eng || name}`,
            intro: 'Rune order, recommended endgame bases, and perfect rolls.',
            ladder: 'Ladder',
            recipe: 'Rune order',
            base: 'Recommended base',
            stats: 'Perfect / variable mods',
            copy: '📋 Copy rune order'
        },
        uniqueModal: {
            subtitle: (eng) => `Unique · ${eng || 'Unique Item'}`,
            intro: 'Perfect-roll unique item details.',
            base: 'Item type / base',
            drop: 'Notable drop sources',
            dropEmpty: 'No data',
            stats: 'Perfect mods',
            copy: '📋 Copy item info'
        }
    }
};

export function t() {
    return UI[SITE_LANG] || UI.ko;
}

/** 루트 기준 자산 경로. 예: assetUrl('data/meta.json?v=19') → '/data/meta.json?v=19' */
export function assetUrl(path) {
    const clean = String(path || '').replace(/^\.\//, '').replace(/^\//, '');
    return `/${clean}`;
}

export function dataUrl(file, ver) {
    const name = String(file || '').replace(/^\.?\/*data\//, '').replace(/^en\//, '');
    const q = ver != null && ver !== '' ? `?v=${ver}` : '';
    if (SITE_LANG === 'en' && LOCALIZED_DATA_FILES.has(name)) {
        return `/data/en/${name}${q}`;
    }
    return `/data/${name}${q}`;
}

export function itemImageUrl(imagePath) {
    if (!imagePath) return '';
    return assetUrl(`items/${imagePath}`);
}

if (typeof window !== 'undefined') {
    window.SITE_LANG = SITE_LANG;
    window.SITE_HOME = SITE_HOME;
    window.SITE_ORIGIN = SITE_ORIGIN;
}
