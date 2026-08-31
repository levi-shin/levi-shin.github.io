/**
 * 사이트 공통 설정 (언어·절대 경로)
 * /en/ 하위에서도 /data, /items, /css, /js 루트 자산을 쓰도록 합니다.
 */

export const SITE_ORIGIN = 'https://diablo.1125labs.com';

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

/** 루트 기준 자산 경로. 예: assetUrl('data/meta.json?v=19') → '/data/meta.json?v=19' */
export function assetUrl(path) {
    const clean = String(path || '').replace(/^\.\//, '').replace(/^\//, '');
    return `/${clean}`;
}

export function dataUrl(file, ver) {
    const name = String(file || '').replace(/^\.?\/*data\//, '');
    const q = ver != null && ver !== '' ? `?v=${ver}` : '';
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
