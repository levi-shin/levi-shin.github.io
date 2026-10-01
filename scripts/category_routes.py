#!/usr/bin/env python3
"""Category URL routes shared by the static page builder."""

from __future__ import annotations

# sectionId (DOM) → URL slug (no leading/trailing slash)
SECTION_SLUGS: dict[str, str] = {
    "builds": "builds",
    "uniques": "unique",
    "runes": "runewords",
    "cubing": "cube",
    "runelist": "runes",
    "merc": "mercenary",
    "frame": "frames",
    "leveling": "leveling",
    "dropcalc": "magic-find",
    "ladder": "patches",
    # extra content sections (real nav items, crawlable links)
    "charms": "sunder",
    "uber": "uber",
    "quest": "quests",
    "bus": "bus",
    "farming": "farming",
}

# pages to generate (slug → section + SEO). Order matches sitemap priority.
# `sets` omitted — no dedicated sets section in the app.
CATEGORIES: list[dict] = [
    {
        "slug": "builds",
        "section": "builds",
        "ko": {
            "title": "디아블로2 레저렉션 종결 빌드 | 1125 Labs",
            "description": "디아블로2 레저렉션 직업별 종결 빌드와 페이퍼돌 세팅을 빠르게 확인합니다.",
            "h1": "디아블로2 레저렉션 종결 빌드",
        },
        "en": {
            "title": "D2R Endgame Builds | 1125 Labs",
            "description": "Diablo II Resurrected endgame builds and paperdoll gear setups.",
            "h1": "Diablo II Resurrected Endgame Builds",
        },
    },
    {
        "slug": "unique",
        "section": "uniques",
        "ko": {
            "title": "디아블로2 레저렉션 유니크 아이템 | 1125 Labs",
            "description": "디아블로2 레저렉션 주요 유니크 아이템과 드랍·사용 팁을 빠르게 확인합니다.",
            "h1": "디아블로2 레저렉션 유니크 아이템",
        },
        "en": {
            "title": "D2R Unique Items | 1125 Labs",
            "description": "Key Diablo II Resurrected unique items, drops, and tips.",
            "h1": "Diablo II Resurrected Unique Items",
        },
    },
    {
        "slug": "runewords",
        "section": "runes",
        "ko": {
            "title": "디아블로2 레저렉션 룬워드 검색 | 1125 Labs",
            "description": "디아블로2 레저렉션 룬워드와 필요한 룬, 장비 조건을 빠르게 검색합니다.",
            "h1": "디아블로2 레저렉션 룬워드",
        },
        "en": {
            "title": "D2R Runewords | 1125 Labs",
            "description": "Search Diablo II Resurrected runewords, rune recipes, and base requirements.",
            "h1": "Diablo II Resurrected Runewords",
        },
    },
    {
        "slug": "cube",
        "section": "cubing",
        "ko": {
            "title": "디아블로2 레저렉션 큐빙·크래프트 | 1125 Labs",
            "description": "디아블로2 레저렉션 호라드릭 큐브 조합과 크래프트 정보를 확인합니다.",
            "h1": "디아블로2 레저렉션 큐빙·크래프트",
        },
        "en": {
            "title": "D2R Cubing & Crafting | 1125 Labs",
            "description": "Diablo II Resurrected Horadric Cube recipes and crafting info.",
            "h1": "Diablo II Resurrected Cubing & Crafting",
        },
    },
    {
        "slug": "runes",
        "section": "runelist",
        "ko": {
            "title": "디아블로2 레저렉션 룬 번호표 | 1125 Labs",
            "description": "디아블로2 레저렉션 1~33번 룬 목록과 등급 정보를 확인합니다.",
            "h1": "디아블로2 레저렉션 룬 번호표",
        },
        "en": {
            "title": "D2R Rune List | 1125 Labs",
            "description": "Diablo II Resurrected rune list (#1–33) and tiers.",
            "h1": "Diablo II Resurrected Rune List",
        },
    },
    {
        "slug": "mercenary",
        "section": "merc",
        "ko": {
            "title": "디아블로2 레저렉션 용병 세팅 | 1125 Labs",
            "description": "디아블로2 레저렉션 용병 장비와 추천 세팅을 확인합니다.",
            "h1": "디아블로2 레저렉션 용병 세팅",
        },
        "en": {
            "title": "D2R Mercenary Setups | 1125 Labs",
            "description": "Diablo II Resurrected mercenary gear and recommended setups.",
            "h1": "Diablo II Resurrected Mercenary Setups",
        },
    },
    {
        "slug": "frames",
        "section": "frame",
        "ko": {
            "title": "디아블로2 레저렉션 프레임 정보 | 1125 Labs",
            "description": "직업별 패캐, 패힛 등 디아블로2 레저렉션 프레임 정보를 빠르게 확인합니다.",
            "h1": "디아블로2 레저렉션 프레임 정보",
        },
        "en": {
            "title": "D2R Breakpoints / Frames | 1125 Labs",
            "description": "Diablo II Resurrected FCR, FHR and other breakpoint frames by class.",
            "h1": "Diablo II Resurrected Breakpoints",
        },
    },
    {
        "slug": "leveling",
        "section": "leveling",
        "ko": {
            "title": "디아블로2 레저렉션 육성 가이드 | 1125 Labs",
            "description": "디아블로2 레저렉션 시즌 초 육성 순서와 초반 룬어·용병 가이드입니다.",
            "h1": "디아블로2 레저렉션 육성 가이드",
        },
        "en": {
            "title": "D2R Leveling Guide | 1125 Labs",
            "description": "Diablo II Resurrected ladder start leveling path and early runewords.",
            "h1": "Diablo II Resurrected Leveling Guide",
        },
    },
    {
        "slug": "magic-find",
        "section": "dropcalc",
        "ko": {
            "title": "디아블로2 레저렉션 매찬 계산기 | 1125 Labs",
            "description": "매직 파인드(매찬) 수치에 따른 유니크 드랍 확률을 계산합니다.",
            "h1": "디아블로2 레저렉션 매찬 계산기",
        },
        "en": {
            "title": "D2R Magic Find Calculator | 1125 Labs",
            "description": "Calculate unique drop odds by Magic Find in Diablo II Resurrected.",
            "h1": "Diablo II Resurrected Magic Find Calculator",
        },
    },
    {
        "slug": "patches",
        "section": "ladder",
        "ko": {
            "title": "디아블로2 레저렉션 패치·래더 소식 | 1125 Labs",
            "description": "디아블로2 레저렉션 패치 노트와 래더 시즌 소식을 확인합니다.",
            "h1": "디아블로2 레저렉션 패치·래더 소식",
        },
        "en": {
            "title": "D2R Patches & Ladder | 1125 Labs",
            "description": "Diablo II Resurrected patch notes and ladder season updates.",
            "h1": "Diablo II Resurrected Patches & Ladder",
        },
    },
    {
        "slug": "sunder",
        "section": "charms",
        "ko": {
            "title": "디아블로2 레저렉션 신 파괴참 | 1125 Labs",
            "description": "디아블로2 레저렉션 신 파괴 참(선더 참) 정보를 확인합니다.",
            "h1": "디아블로2 레저렉션 신 파괴참",
        },
        "en": {
            "title": "D2R Sunder Charms | 1125 Labs",
            "description": "Diablo II Resurrected Sunder charm information.",
            "h1": "Diablo II Resurrected Sunder Charms",
        },
    },
    {
        "slug": "uber",
        "section": "uber",
        "ko": {
            "title": "디아블로2 레저렉션 우버·횃불 | 1125 Labs",
            "description": "디아블로2 레저렉션 우버 트리스람·횃불·관련 주얼 정보를 확인합니다.",
            "h1": "디아블로2 레저렉션 우버·횃불",
        },
        "en": {
            "title": "D2R Uber & Torch | 1125 Labs",
            "description": "Diablo II Resurrected Uber Tristram, Torch, and related jewels.",
            "h1": "Diablo II Resurrected Uber & Torch",
        },
    },
    {
        "slug": "quests",
        "section": "quest",
        "ko": {
            "title": "디아블로2 레저렉션 영구보상 퀘스트 | 1125 Labs",
            "description": "디아블로2 레저렉션 영구 보상이 있는 퀘스트를 정리합니다.",
            "h1": "디아블로2 레저렉션 영구보상 퀘스트",
        },
        "en": {
            "title": "D2R Permanent Quests | 1125 Labs",
            "description": "Diablo II Resurrected quests with permanent rewards.",
            "h1": "Diablo II Resurrected Permanent Quests",
        },
    },
    {
        "slug": "bus",
        "section": "bus",
        "ko": {
            "title": "디아블로2 레저렉션 버스 가이드 | 1125 Labs",
            "description": "디아블로2 레저렉션 버스 이용·진행 가이드입니다.",
            "h1": "디아블로2 레저렉션 버스 가이드",
        },
        "en": {
            "title": "D2R Bus Guide | 1125 Labs",
            "description": "Diablo II Resurrected bus leveling guide.",
            "h1": "Diablo II Resurrected Bus Guide",
        },
    },
    {
        "slug": "farming",
        "section": "farming",
        "ko": {
            "title": "디아블로2 레저렉션 TC85 사냥터 | 1125 Labs",
            "description": "디아블로2 레저렉션 TC85 주요 사냥터와 파밍 포인트를 정리합니다.",
            "h1": "디아블로2 레저렉션 TC85 사냥터",
        },
        "en": {
            "title": "D2R TC85 Farming | 1125 Labs",
            "description": "Diablo II Resurrected TC85 farming zones and tips.",
            "h1": "Diablo II Resurrected TC85 Farming",
        },
    },
]


def path_for(slug: str, lang: str) -> str:
    if lang == "en":
        return f"/en/{slug}/"
    return f"/{slug}/"


def home_for(lang: str) -> str:
    return "/en/" if lang == "en" else "/"
