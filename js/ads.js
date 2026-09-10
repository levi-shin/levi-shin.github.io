/**
 * AdSense gating: only show/fill ads when publisher content is ready
 * and the active section is not a low-content / form-only screen.
 */

let contentReady = false;
let adsPushed = false;

function activeSectionId() {
    return document.querySelector('.content-section.active')?.id || 'builds';
}

/** Sections that are mostly UI / forms — no Google ads while active */
const NO_ADS_SECTIONS = new Set(['feedback']);

export function syncAdsForSection(sectionId) {
    const id = sectionId || activeSectionId();
    const allow = contentReady && !NO_ADS_SECTIONS.has(id);

    document.querySelectorAll('.site-ad').forEach((el) => {
        el.classList.toggle('is-hidden', !allow);
        el.setAttribute('aria-hidden', allow ? 'false' : 'true');
    });

    if (allow && !adsPushed) {
        adsPushed = true;
        document.querySelectorAll('.site-ad ins.adsbygoogle').forEach(() => {
            try {
                (window.adsbygoogle = window.adsbygoogle || []).push({});
            } catch {
                /* ignore */
            }
        });
    }
}

/**
 * Call after main encyclopedia content has rendered (e.g. build cards).
 */
export function markPublisherContentReady() {
    const grid = document.getElementById('buildCardsGrid');
    if (!grid || grid.children.length === 0) return false;
    contentReady = true;
    syncAdsForSection(activeSectionId());
    return true;
}
