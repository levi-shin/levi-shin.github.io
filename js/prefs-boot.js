/**
 * Early prefs boot: language redirect before paint (no ?lang= param).
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

    function applyLangRedirect() {
        const prefs = load();
        const saved = prefs.lang;
        if (!saved) return;

        const path = location.pathname;
        if (saved === 'en' && (path === '/' || path === '/index.html')) {
            location.replace('/en/');
            return;
        }
        if (saved === 'ko' && path.startsWith('/en')) {
            location.replace('/');
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
