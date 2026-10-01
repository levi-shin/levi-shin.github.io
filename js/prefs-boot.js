/**
 * Early prefs boot: language redirect before paint (no ?lang= param).
 * Preserves category URL slugs when switching / ↔ /en/.
 */
(function () {
    const KEY = 'd2_prefs';
    const BOOKMARK_KEY = 'd2_bookmark_dismissed';

    function load() {
        try {
            return JSON.parse(localStorage.getItem(KEY) || '{}');
        } catch {
            return {};
        }
    }

    function save(prefs) {
        try {
            localStorage.setItem(KEY, JSON.stringify(prefs));
        } catch {
            /* ignore quota / private mode */
        }
    }

    function detectLangFromPath() {
        return location.pathname.startsWith('/en') ? 'en' : 'ko';
    }

    function normalizePath(pathname) {
        let p = String(pathname || '/');
        p = p.replace(/\/index\.html$/i, '/');
        if (p.length > 1 && !p.endsWith('/')) p += '/';
        return p;
    }

    function toEnPath(path) {
        const p = normalizePath(path);
        if (p === '/') return '/en/';
        if (p.startsWith('/en/')) return p;
        return '/en' + p;
    }

    function toKoPath(path) {
        const p = normalizePath(path);
        if (p === '/en/' || p === '/en') return '/';
        if (p.startsWith('/en/')) {
            const rest = p.slice(3) || '/';
            return rest.startsWith('/') ? rest : '/' + rest;
        }
        return p;
    }

    function applyLangRedirect() {
        const prefs = load();
        const saved = prefs.lang;
        if (!saved) return;

        const path = location.pathname;
        const isEn = path === '/en' || path.startsWith('/en/');

        if (saved === 'en' && !isEn) {
            location.replace(toEnPath(path));
            return;
        }
        if (saved === 'ko' && isEn) {
            location.replace(toKoPath(path));
        }
    }

    window.__d2SaveLang = function (lang) {
        const prefs = load();
        prefs.lang = lang === 'en' ? 'en' : 'ko';
        save(prefs);
    };

    window.__d2SeedLangIfMissing = function () {
        const prefs = load();
        if (!prefs.lang) {
            prefs.lang = detectLangFromPath();
            save(prefs);
        }
    };

    window.D2_PREFS_KEYS = { PREFS: KEY, BOOKMARK: BOOKMARK_KEY };
    applyLangRedirect();
})();
