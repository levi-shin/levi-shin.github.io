#!/usr/bin/env python3
"""Build static category pages from index.html / en/index.html."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from category_routes import CATEGORIES, SECTION_SLUGS, home_for, path_for  # noqa: E402

ORIGIN = "https://diablo.1125labs.com"


def replace_meta(html: str, *, title: str, description: str, canonical: str, alt_ko: str, alt_en: str) -> str:
    html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, count=1, flags=re.S)
    html = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{description}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<meta property="og:title" content="[^"]*">',
        f'<meta property="og:title" content="{title}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<meta property="og:description" content="[^"]*">',
        f'<meta property="og:description" content="{description}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<meta property="og:url" content="[^"]*">',
        f'<meta property="og:url" content="{canonical}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<meta name="twitter:title" content="[^"]*">',
        f'<meta name="twitter:title" content="{title}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<meta name="twitter:description" content="[^"]*">',
        f'<meta name="twitter:description" content="{description}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{canonical}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<link rel="alternate" hreflang="ko" href="[^"]*">',
        f'<link rel="alternate" hreflang="ko" href="{alt_ko}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<link rel="alternate" hreflang="en" href="[^"]*">',
        f'<link rel="alternate" hreflang="en" href="{alt_en}">',
        html,
        count=1,
    )
    html = re.sub(
        r'<link rel="alternate" hreflang="x-default" href="[^"]*">',
        f'<link rel="alternate" hreflang="x-default" href="{alt_ko}">',
        html,
        count=1,
    )
    return html


def set_active_section(html: str, section: str) -> str:
    # clear active on sections
    html = re.sub(
        r'(<section\s+id="[^"]+"\s+class="content-section)(?:\s+active)?(")',
        r'\1\2',
        html,
    )
    html = re.sub(
        rf'(<section\s+id="{re.escape(section)}"\s+class="content-section)(")',
        r'\1 active\2',
        html,
        count=1,
    )
    # nav active: clear then set on matching data-section
    html = re.sub(r'(class="nav-btn)(?:\s+active)?(")', r'\1\2', html)
    html = re.sub(
        rf'(<a class="nav-btn" data-section="{re.escape(section)}")',
        rf'<a class="nav-btn active" data-section="{section}"',
        html,
        count=1,
    )
    return html


def set_h1(html: str, h1: str) -> str:
    return re.sub(
        r"(<header class=\"desktop-only\">\s*<h1>)(.*?)(</h1>)",
        rf"\1{h1}\3",
        html,
        count=1,
        flags=re.S,
    )


def set_lang_switcher(html: str, lang: str, slug: str) -> str:
    ko_href = path_for(slug, "ko")
    en_href = path_for(slug, "en")
    if lang == "ko":
        html = re.sub(
            r'<a href="[^"]*" class="active" lang="ko"[^>]*>한국어</a>',
            f'<a href="{ko_href}" class="active" lang="ko" hreflang="ko" onclick="window.__d2SaveLang && __d2SaveLang(\'ko\')">한국어</a>',
            html,
            count=1,
        )
        html = re.sub(
            r'<a href="[^"]*" lang="en"[^>]*>English</a>',
            f'<a href="{en_href}" lang="en" hreflang="en" onclick="window.__d2SaveLang && __d2SaveLang(\'en\')">English</a>',
            html,
            count=1,
        )
    else:
        html = re.sub(
            r'<a href="[^"]*" lang="ko"[^>]*>한국어</a>',
            f'<a href="{ko_href}" lang="ko" hreflang="ko" onclick="window.__d2SaveLang && __d2SaveLang(\'ko\')">한국어</a>',
            html,
            count=1,
        )
        html = re.sub(
            r'<a href="[^"]*" class="active" lang="en"[^>]*>English</a>',
            f'<a href="{en_href}" class="active" lang="en" hreflang="en" onclick="window.__d2SaveLang && __d2SaveLang(\'en\')">English</a>',
            html,
            count=1,
        )
    return html


def inject_body_attr(html: str, section: str) -> str:
    if re.search(r"<body[^>]*data-section=", html):
        return re.sub(r'<body([^>]*)data-section="[^"]*"', rf'<body\1data-section="{section}"', html, count=1)
    return html.replace("<body>", f'<body data-section="{section}">', 1)


def build_one(src: Path, out_dir: Path, cat: dict, lang: str) -> None:
    seo = cat[lang]
    slug = cat["slug"]
    section = cat["section"]
    canonical = ORIGIN + path_for(slug, lang)
    alt_ko = ORIGIN + path_for(slug, "ko")
    alt_en = ORIGIN + path_for(slug, "en")

    html = src.read_text(encoding="utf-8")
    html = replace_meta(
        html,
        title=seo["title"],
        description=seo["description"],
        canonical=canonical,
        alt_ko=alt_ko,
        alt_en=alt_en,
    )
    html = set_h1(html, seo["h1"])
    html = set_active_section(html, section)
    html = set_lang_switcher(html, lang, slug)
    html = inject_body_attr(html, section)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"wrote {out_path.relative_to(ROOT)}")


def write_routes_js() -> None:
    lines = [
        "/** Auto-generated by scripts/build_category_pages.py — do not edit by hand. */",
        "export const SECTION_SLUGS = {",
    ]
    for section, slug in SECTION_SLUGS.items():
        lines.append(f"    {section}: '{slug}',")
    lines += [
        "};",
        "",
        "export const SLUG_SECTIONS = Object.fromEntries(",
        "    Object.entries(SECTION_SLUGS).map(([section, slug]) => [slug, section])",
        ");",
        "",
        "export function sectionPath(sectionId, lang = (typeof window !== 'undefined' && window.SITE_LANG) || 'ko') {",
        "    const slug = SECTION_SLUGS[sectionId];",
        "    if (!slug) return lang === 'en' ? '/en/' : '/';",
        "    return lang === 'en' ? `/en/${slug}/` : `/${slug}/`;",
        "}",
        "",
        "export function sectionFromPath(pathname = typeof location !== 'undefined' ? location.pathname : '/') {",
        "    const p = String(pathname || '/').replace(/\\/index\\.html$/i, '/');",
        "    const m = p.match(/^\\/(en\\/)?([^/]+)\\/?$/);",
        "    if (!m || !m[2]) return null;",
        "    return SLUG_SECTIONS[m[2]] || null;",
        "}",
        "",
    ]
    out = ROOT / "js" / "routes.js"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")


def write_sitemap() -> None:
    today = "2026-10-01"
    chunks = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]

    def add_url(loc: str, ko: str, en: str, priority: str) -> None:
        chunks.append("  <url>")
        chunks.append(f"    <loc>{ORIGIN}{loc}</loc>")
        chunks.append(f"    <lastmod>{today}</lastmod>")
        chunks.append("    <changefreq>weekly</changefreq>")
        chunks.append(f"    <priority>{priority}</priority>")
        chunks.append(f'    <xhtml:link rel="alternate" hreflang="ko" href="{ORIGIN}{ko}"/>')
        chunks.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{ORIGIN}{en}"/>')
        chunks.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{ORIGIN}{ko}"/>')
        chunks.append("  </url>")

    add_url("/", "/", "/en/", "1.0")
    add_url("/en/", "/", "/en/", "0.9")
    for cat in CATEGORIES:
        ko = path_for(cat["slug"], "ko")
        en = path_for(cat["slug"], "en")
        add_url(ko, ko, en, "0.8")
        add_url(en, ko, en, "0.7")

    chunks.append("</urlset>")
    out = ROOT / "sitemap.xml"
    out.write_text("\n".join(chunks) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")


def main() -> None:
    write_routes_js()
    ko_src = ROOT / "index.html"
    en_src = ROOT / "en" / "index.html"
    for cat in CATEGORIES:
        build_one(ko_src, ROOT / cat["slug"], cat, "ko")
        build_one(en_src, ROOT / "en" / cat["slug"], cat, "en")
    write_sitemap()
    print(f"done: {len(CATEGORIES)} categories × ko/en")


if __name__ == "__main__":
    main()
