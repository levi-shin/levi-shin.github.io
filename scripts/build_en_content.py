#!/usr/bin/env python3
"""Build data/en/{builds,leveling,dropcalc,patchnotes}.json from Korean sources."""
from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EN = DATA / "en"

HANGUL = re.compile(r"[가-힣]")
PAREN_EN = re.compile(r"\(([^가-힣()][^()]*)\)\s*$")

# ---------------------------------------------------------------------------
# Lookups from Phase-2 EN DBs
# ---------------------------------------------------------------------------
EN_UNIQUES = {u["id"]: u for u in json.loads((EN / "uniques.json").read_text(encoding="utf-8"))}
EN_RW = {r["id"]: r for r in json.loads((EN / "runewords.json").read_text(encoding="utf-8"))}
KO_RW = json.loads((DATA / "runewords.json").read_text(encoding="utf-8"))
KO_UNI = json.loads((DATA / "uniques.json").read_text(encoding="utf-8"))
KO_RUNES = json.loads((DATA / "runes.json").read_text(encoding="utf-8"))

ko_name_to_en: dict[str, str] = {}
# Short KO tokens that corrupt Korean prose if replaced globally.
SKIP_GLOBAL_NAMES = {
    "힘",  # Strength RW — handled via glossary contexts
    "부",  # Wealth
    "꿈",  # Dream
    "엣지",
    "화이트",
}
for r in KO_RW:
    en = r.get("eng") or EN_RW.get(r["id"], {}).get("name") or r["name"]
    if r["name"] not in SKIP_GLOBAL_NAMES and len(r["name"]) >= 2:
        ko_name_to_en[r["name"]] = en
    for a in r.get("aliases") or []:
        if HANGUL.search(a) and len(a) >= 2 and a not in SKIP_GLOBAL_NAMES:
            ko_name_to_en[a] = en
for u in KO_UNI:
    en = u.get("eng") or EN_UNIQUES.get(u["id"], {}).get("name") or u["name"]
    ko_name_to_en[u["name"]] = en
    bare = re.sub(r"\([^)]*\)", "", u["name"]).strip()
    if bare and bare != u["name"] and len(bare) >= 2:
        ko_name_to_en.setdefault(bare, en)
# Runes: NEVER replace bare 1–2 syllable names (말/로/자/헬 destroy prose).
# Only "X 룬" forms are safe.
for r in KO_RUNES:
    ko_name_to_en[f"{r['name']} 룬"] = f"{r['eng']} Rune"

# ---------------------------------------------------------------------------
# Explicit build identity (minimize Hangul in title/subtitle/badge)
# ---------------------------------------------------------------------------
BUILD_META = {
    70001: {
        "title": "Sorceress",
        "subtitle": "Lightning Sorc (Lightning / Chain Lightning)",
        "badge": "Lightning",
    },
    70002: {
        "title": "Sorceress",
        "subtitle": "Blizzard Sorc (Blizzard)",
        "badge": "Blizzard",
    },
    70003: {
        "title": "Paladin",
        "subtitle": "Blessed Hammer (Hammerdin)",
        "badge": "Hammerdin",
    },
    70004: {
        "title": "Paladin",
        "subtitle": "Smiter (Ubers / Torch)",
        "badge": "Smiter",
    },
    70005: {
        "title": "Necromancer",
        "subtitle": "Summon Necro (Skeleton Army)",
        "badge": "Summon",
    },
    70006: {
        "title": "Necromancer",
        "subtitle": "Bone Nec (Bone Spear)",
        "badge": "Bone",
    },
    70007: {
        "title": "Amazon",
        "subtitle": "Javazon (Lightning Fury)",
        "badge": "Javazon",
    },
    70008: {
        "title": "Amazon",
        "subtitle": "Faith Bowazon (Multiple Shot)",
        "badge": "Bowazon",
    },
    70009: {
        "title": "Barbarian",
        "subtitle": "WW Barb / GF Barb (Whirlwind)",
        "badge": "WW Barb",
    },
    70010: {
        "title": "Barbarian",
        "subtitle": "Berserk Barb",
        "badge": "Berserk",
    },
    70011: {
        "title": "Druid",
        "subtitle": "Wind Druid (Tornado / Hurricane)",
        "badge": "Wind",
    },
    70012: {
        "title": "Druid",
        "subtitle": "Fury Werewolf",
        "badge": "Werewolf",
    },
    70013: {
        "title": "Assassin",
        "subtitle": "Mosaic Sin (Phoenix Strike)",
        "badge": "Mosaic",
    },
    70014: {
        "title": "Assassin",
        "subtitle": "Trapsin (Lightning Sentry)",
        "badge": "Trapsin",
    },
    70015: {
        "title": "Warlock",
        "subtitle": "Resonating Blow (125 FCR)",
        "badge": "Resonating",
    },
    70016: {
        "title": "Warlock",
        "subtitle": "Apocalypse / Fire AoE",
        "badge": "Apocalypse",
    },
    70017: {
        "title": "Sorceress",
        "subtitle": "Nova Sorc (Lightning Nova)",
        "badge": "Nova",
    },
    70018: {
        "title": "Necromancer",
        "subtitle": "Poison Nec (Poison Nova)",
        "badge": "Poison",
    },
}

# Curated English prose (glossary alone produces half-translated sentences).
BUILD_PROSE = {
    70001: {
        "stats": "Strength 156 (Monarch), rest Life · 117% FCR (9-frame)",
        "inventory": "Heaven's Breach (Lightning Sunder), Lightning skillers, Anni, Torch",
        "skills": "Lightning (20), Chain Lightning (20), Lightning Mastery (20), Lightning Bolt (20, synergy)",
        "playstyle": (
            "Buff Battle Command / Battle Orders with CTA, then Teleport in. "
            "Use Chain Lightning on packs; Lightning on lined-up targets or bosses. "
            "Static Field bosses down, then finish with Lightning. "
            "Damage drops hard if you engage before the Infinity merc's Conviction lands — watch merc position."
        ),
    },
    70002: {
        "stats": "Strength 156, rest Life · 105% FCR (9-frame)",
        "inventory": "Cold Rupture (Cold Sunder), Cold skillers, Anni, Torch",
        "skills": "Blizzard (20), Ice Blast (20), Glacial Spike (20), Cold Mastery (20)",
        "playstyle": (
            "Teleport and drop Blizzard from off-screen, then pull monsters into the AoE. "
            "Static Field bosses, then keep Blizzard up. "
            "Blizzard has cast delay — diving the middle before it lands can get you hit; plant your feet first."
        ),
    },
    70003: {
        "stats": "Dexterity to 75% block with Holy Shield up, rest Life · 125% FCR",
        "inventory": "Combat skillers, Anni, Torch, life/res small charms",
        "skills": "Blessed Hammer (20), Concentration (20), Vigor (20), Blessed Aim (20)",
        "playstyle": (
            "Teleport into packs with Concentration on. "
            "Hold still or micro-move so hammers spiral through the pack. "
            "Recheck Holy Shield 75% block and CTA Battle Command / Battle Orders often."
        ),
    },
    70004: {
        "stats": "Holy Shield 75% block, rest Life",
        "inventory": "Anni, Torch, all-res/life small charms, Physical Sunder (optional)",
        "skills": "Smite (20), Holy Shield (20), Fanaticism (20)",
        "playstyle": (
            "Prebuff Fade in town with Treachery, then swap to main gear. "
            "Uber order: Lilith → Duriel → Izual → Tristram, Smite throughout. "
            "Don't stick early — wait for Dracul's Life Tap, then swing. "
            "If the Reaper's Toll merc dies, Decrepify drops; keep the merc alive."
        ),
    },
    70005: {
        "stats": "Strength 156, rest Life",
        "inventory": "Summoning skillers, Anni, Torch",
        "skills": "Raise Skeleton (20), Skeleton Mastery (20), Corpse Explosion (20)",
        "playstyle": (
            "Fill skeletons and mages, then Teleport the army onto packs. "
            "Clear density with Corpse Explosion; let summons handle bosses. "
            "Amplify Damage into Corpse Explosion is the core loop. "
            "Keep Beast (Fanaticism) and merc Infinity (Conviction) up."
        ),
    },
    70006: {
        "stats": "Strength 156, rest Life · 125% FCR",
        "inventory": "Poison & Bone skillers, Anni, Torch, Magic Sunder (optional)",
        "skills": "Bone Spear (20), Bone Spirit (20), Bone Wall (20), Bone Prison (20)",
        "playstyle": (
            "Teleport for angles — Bone Spear on lines, Bone Spirit on spread packs. "
            "Recast Bone Armor when it breaks; Bone Prison scary pulls. "
            "Insight merc covers mana; refresh CTA Battle Orders regularly."
        ),
    },
    70007: {
        "stats": "Block build: Dex to 75% block; Pierce build: gear reqs then Life · 52% IAS",
        "inventory": "Heaven's Breach (Lightning Sunder), Javelin skillers, spare Titan's / Thunderstroke",
        "skills": "Lightning Fury (20), Charged Strike (20), Lightning Strike (20)",
        "playstyle": (
            "Razortail Pierce is mandatory. "
            "Lightning Fury on stacked Cows/Pit; Charged Strike on bosses at melee range. "
            "Valkyrie and Decoy peel aggro; swap spare javelins when Titan's quantity runs out. "
            "Throw Fury from Conviction range with the Infinity merc."
        ),
    },
    70008: {
        "stats": "Bow Dexterity reqs, rest Life (extra Dex for max damage)",
        "inventory": "Bone Break (Physical Sunder), max-damage charms",
        "skills": "Multiple Shot (20), Strafe (20), Guided Arrow (20)",
        "playstyle": (
            "Run Faith (Fanaticism) and Act 2 Pride merc (Concentration), then Multiple Shot packs. "
            "Bosses: Guided Arrow or Strafe. "
            "Without Pierce, arrows stop on the first target — confirm belt Pierce and Physical Sunder."
        ),
    },
    70009: {
        "stats": "Gear Strength cushion; ~3k Life after CTA Battle Orders",
        "inventory": "Gheed's Fortune, GF/MF grand charms",
        "skills": "Whirlwind (20), Sword Mastery (20), Find Item (50%+)",
        "playstyle": (
            "CTA Battle Orders, then Whirlwind through packs on dual Grief. "
            "Clear trash, swap to hork Barb, Find Item corpses. "
            "Horking too early mid-fight is messy — clean up, then swap."
        ),
    },
    70010: {
        "stats": "Reach ~3k Life, then Strength (Berserk is magic damage — no Strength scaling)",
        "inventory": "Life/res small charms; Physical Sunder optional (main skill is magic damage)",
        "skills": "Berserk (20), Howl (20), Sword Mastery (20)",
        "playstyle": (
            "Berserk ignores Physical Immunes as magic damage. "
            "Single-target swing with Howl synergy for bosses/Ubers. "
            "Damage after Reaper's Toll Decrepify; Teleport away from nasty projectiles."
        ),
    },
    70011: {
        "stats": "Monarch Strength 156, rest Life · 99% FCR (10-frame)",
        "inventory": "Elemental skillers, Anni, Torch, Bone Break (Physical Sunder)",
        "skills": "Tornado (20), Twister (20), Hurricane (20)",
        "playstyle": (
            "Hurricane, Cyclone Armor, and Oak Sage up, then Teleport into position. "
            "Pre-drop Tornado on monster pathing lines. "
            "Tornado is Physical — without Sunder, Physical Immune packs barely take damage."
        ),
    },
    70012: {
        "stats": "Weapon Dexterity reqs, rest Life",
        "inventory": "Shape Shifting skillers, max-damage/life small charms",
        "skills": "Werewolf (20), Lycanthropy (20), Fury (20)",
        "playstyle": (
            "Stay Werewolf and chain Fury. "
            "Confirm eth Reaper's Toll Decrepify and Act 1 Faith Fanaticism. "
            "If life steal drops, step back, reproc Dracul's, then re-engage."
        ),
    },
    70013: {
        "stats": "Gear reqs, then rest Life",
        "inventory": "Heaven's Breach (Lightning) or Fire/Physical Sunder, Martial Arts skillers",
        "skills": "Phoenix Strike (20), Fists of Thunder (20), Blades of Ice (20)",
        "playstyle": (
            "Stack Fire/Cold/Lightning charges with Phoenix Strike, release with Dragon Claw or Dragon Tail. "
            "Mosaic dual-wield keeps charges, so finishers can be spammed. "
            "Travel on CTA + Spirit Teleport, then swap back to claws — confirm claws after every swap."
        ),
    },
    70014: {
        "stats": "Monarch Strength 156, rest Life · 102%+ FCR",
        "inventory": "Heaven's Breach (Lightning Sunder), Traps skillers, Anni, Torch",
        "skills": "Lightning Sentry (20), Death Sentry (20), Shock Web (20)",
        "playstyle": (
            "Teleport in, plant five Lightning Sentries; Death Sentry corpses as they appear. "
            "Shadow Master peels, then move to the next pack. "
            "Traps do not follow Teleport — replant inside Infinity Conviction range."
        ),
    },
    70015: {
        "stats": "Gear Strength only; 0 Dex/Energy; rest Life · 125% FCR",
        "inventory": "Life/res small charms, Physical Sunder, Anni, Torch (Warlock skillers lower priority)",
        "skills": "Resonating Blow (20), Mirror Blades (20), Blade Move, Demon Binding, Devour",
        "playstyle": (
            "Resonating Blow scales with FCR, not IAS — hit the 125 breakpoint, then spam. "
            "Eth Insight + Phoenix covers mana and Redemption. "
            "Keep a bound demon in front, Resonating Blow from pack center; Lower Resist bosses first. "
            "Below 125 FCR the build feels much worse — verify the breakpoint."
        ),
    },
    70016: {
        "stats": "Gear Strength reqs, rest Life · 125% FCR (includes Obsession 65)",
        "inventory": "Flame Rift (Fire Sunder), Chaos/Fire skillers, Anni, Torch",
        "skills": "Apocalypse (20), Flame Wave (20), Fire Seal · Lower Resist, Devour",
        "playstyle": (
            "Teleport into pack center, lay Fire Ring / Flame Wave, spam Apocalypse. "
            "Warlocks can wear two-hand Obsession staff and Grimoire together. "
            "Flickering Flame plus Infinity merc cuts Fire resist before damage lands. "
            "Without broken immunes, damage is near zero — respect Sunder and Conviction range."
        ),
    },
    70017: {
        "stats": "Gear Strength reqs; Energy Shield builds invest Energy · 105% FCR (8-frame)",
        "inventory": "Heaven's Breach (Lightning Sunder), Lightning skillers, Anni, Torch",
        "skills": "Nova (20), Lightning Mastery (20), Static Field (20), Telekinesis · Energy Shield",
        "playstyle": (
            "Teleport onto pack center and spam Nova. "
            "Nova only hits around you — casting from range does almost nothing. "
            "Static Field bosses, then stick Nova. "
            "Energy Shield drops at 0 mana — watch the mana pool."
        ),
    },
    70018: {
        "stats": "Monarch Strength 156, rest Life · 75% FCR (main) / 125% (Spirit + FCR Circlet)",
        "inventory": "Rotting Cleavage (Poison Sunder), Poison & Bone skillers, Anni, Torch",
        "skills": "Poison Nova (20), Poison Explosion (20), Lower Resist (20), Corpse Explosion",
        "playstyle": (
            "Lower Resist, soak packs with Poison Nova, Corpse Explosion as bodies drop. "
            "Poison is DoT — you can move to the next pack immediately. "
            "Keep Lower Resist up on bosses while reapplying Poison Nova. "
            "Poison Nova without Lower Resist loses most of its damage — curse first."
        ),
    },
}


def compose_info(prose: dict) -> str:
    return (
        f"<strong>📊 Stats:</strong> {prose['stats']}<br>"
        f"<strong>🎒 Inventory:</strong> {prose['inventory']}<br>"
        f"<strong>⚡ Skills:</strong> {prose['skills']}<br>"
        f"<strong>🎮 Playstyle:</strong> {prose['playstyle']}"
    )


SLOT_MAP = {
    "무기 (Weapon)": "Weapon",
    "투구 (Helm)": "Helm",
    "갑옷 (Armor)": "Armor",
    "방패 (Shield)": "Shield",
    "장갑 / 신발": "Gloves / Boots",
    "벨트 / 장신구": "Belt / Jewelry",
    "스왑 (Weapon Swap)": "Weapon Swap",
    "용병 무기": "Merc Weapon",
    "용병 투구": "Merc Helm",
    "용병 갑옷": "Merc Armor",
}

# ---------------------------------------------------------------------------
# Glossary (longest match first via apply_glossary)
# ---------------------------------------------------------------------------
GLOSSARY: list[tuple[str, str]] = [
    # --- classes / build nicknames ---
    ("원소술사 (Sorceress)", "Sorceress"),
    ("성기사 (Paladin)", "Paladin"),
    ("강령술사 (Necromancer)", "Necromancer"),
    ("야만용사 (Barbarian)", "Barbarian"),
    ("악마술사 (Warlock)", "Warlock"),
    ("악마술사(워록)", "Warlock"),
    ("악마술사", "Warlock"),
    ("암살자 (Assassin)", "Assassin"),
    ("드루이드 (Druid)", "Druid"),
    ("아마존 (Amazon)", "Amazon"),
    ("원소술사", "Sorceress"),
    ("성기사", "Paladin"),
    ("강령술사", "Necromancer"),
    ("야만용사", "Barbarian"),
    ("암살자", "Assassin"),
    ("드루이드", "Druid"),
    ("아마존", "Amazon"),
    ("워록", "Warlock"),
    ("체라소서", "Lightning Sorc"),
    ("극블리소서", "Blizzard Sorc"),
    ("노바소서", "Nova Sorc"),
    ("화염 소서", "Fire Sorc"),
    ("소서면", "Sorc,"),
    ("소서", "Sorc"),
    ("햄딘", "Hammerdin"),
    ("슴딘", "Smiter"),
    ("조독넥", "Summon Necro"),
    ("본넥", "Bone Nec"),
    ("독넥", "Poison Nec"),
    ("자바마", "Javazon"),
    ("활마", "Bowazon"),
    ("왚바바", "WW Barb"),
    ("삥바바", "GF Barb"),
    ("알리바바", "hork Barb"),
    ("버서크 바바", "Berserk Barb"),
    ("바바", "Barb"),
    ("엘리드루", "Wind Druid"),
    ("늑드루", "Werewolf Druid"),
    ("모자이크씬", "Mosaic Sin"),
    ("트랩씬", "Trapsin"),
    ("메아리치는 타격", "Resonating Blow"),
    ("메아리 종결", "Resonating Blow endgame"),
    ("메아리 125패캐", "Resonating Blow 125 FCR"),
    ("메아리는", "Resonating Blow is"),
    ("메아리·종말", "Resonating Blow / Apocalypse"),
    ("메아리", "Resonating Blow"),
    ("종말 종결", "Apocalypse endgame"),
    ("종말(화염)", "Apocalypse (Fire)"),
    ("종말 / 화염 장판", "Apocalypse / Fire AoE"),
    ("아포칼립스", "Apocalypse"),
    ("종말", "Apocalypse"),
    # --- skills ---
    ("연쇄 번개", "Chain Lightning"),
    ("번개 분노", "Lightning Fury"),
    ("번개 파수꾼", "Lightning Sentry"),
    ("번개 일격", "Lightning Strike"),
    ("번개 숙련", "Lightning Mastery"),
    ("번개 줄기", "Lightning Bolt"),
    ("번개 파장", "Lightning Nova"),
    ("번개 스킬참", "Lightning skillers"),
    ("번개 파괴참", "Lightning Sunder Charm"),
    ("번개 주얼", "Lightning facet"),
    ("충전된 일격", "Charged Strike"),
    ("불사조 일격", "Phoenix Strike"),
    ("천둥의 주먹", "Fists of Thunder"),
    ("얼음 칼날", "Blades of Ice"),
    ("용의 발톱", "Dragon Claw"),
    ("용의 꼬리", "Dragon Tail"),
    ("축복받은 망치", "Blessed Hammer"),
    ("신성한 방패", "Holy Shield"),
    ("홀리실드", "Holy Shield"),
    ("신성한 빙결", "Holy Freeze"),
    ("피해 증폭", "Amplify Damage"),
    ("시체 폭발", "Corpse Explosion"),
    ("해골 되살리기", "Raise Skeleton"),
    ("해골 숙련", "Skeleton Mastery"),
    ("뼈 영혼", "Bone Spirit"),
    ("뼈 감옥", "Bone Prison"),
    ("뼈 갑옷", "Bone Armor"),
    ("뼈 창", "Bone Spear"),
    ("뼈 벽", "Bone Wall"),
    ("독 노바", "Poison Nova"),
    ("다발 사격", "Multiple Shot"),
    ("유도 화살", "Guided Arrow"),
    ("아이템 찾기", "Find Item"),
    ("소용돌이", "Whirlwind"),
    ("광전사", "Berserk"),
    ("버서크", "Berserk"),
    ("회오리바람", "Twister"),
    ("회오리 갑옷", "Cyclone Armor"),
    ("참나무 현자", "Oak Sage"),
    ("허리케인", "Hurricane"),
    ("늑대인간", "Werewolf"),
    ("변신술", "Lycanthropy"),
    ("전자기장", "Static Field"),
    ("전투 명령", "Battle Command"),
    ("전투 지시(BO)", "Battle Orders"),
    ("전투 지시", "Battle Orders"),
    ("전투의 외침", "Battle Cry"),
    ("오더스", "Battle Orders"),
    ("CTA 오더", "CTA Battle Orders"),
    ("CTA로", "With CTA,"),
    ("CTA", "CTA"),
    ("성타", "Holy Bolt"),
    ("질주", "Charge"),
    ("강타", "Smite"),
    ("집중", "Concentration"),
    ("원기", "Vigor"),
    ("조준", "Blessed Aim"),
    ("광신(Fanaticism)", "Fanaticism"),
    ("광신", "Fanaticism"),
    ("선고(Conviction)", "Conviction"),
    ("선고", "Conviction"),
    ("위세", "Might"),
    ("명상", "Meditation"),
    ("정화", "Cleansing"),
    ("노화", "Decrepify"),
    ("흐리기", "Fade"),
    ("포효", "Howl"),
    ("배쉬", "Bash"),
    ("분노", "Fury"),
    ("속사", "Strafe"),
    ("돌풍", "Tornado"),
    ("토네이도", "Tornado"),
    ("풍수", "Wind"),
    ("눈보라", "Blizzard"),
    ("얼음살", "Ice Blast"),
    ("빙하의 창", "Glacial Spike"),
    ("냉기 숙련", "Cold Mastery"),
    ("프로즌 오브", "Frozen Orb"),
    ("파이어볼", "Fireball"),
    ("온기", "Warmth"),
    ("텔레포트", "Teleport"),
    ("텔포", "Teleport"),
    ("발키리", "Valkyrie"),
    ("미끼", "Decoy"),
    ("마법사", "Skeleton Mage"),
    ("해골", "Skeleton"),
    ("야수", "Beast"),
    ("무기력 저주", "Lower Resist"),
    ("미소모", "not consumed"),
    ("충전 미", "charges not "),
    ("악마 속박", "Demon Binding"),
    ("소모(", "Devour ("),
    ("소모,", "Devour,"),
    ("소모 ", "Devour "),
    ("소모", "Devour"),
    ("화염파", "Flame Wave"),
    ("화염 고리", "Fire Ring"),
    ("화염 인장", "Fire Seal"),
    ("화염 장판", "Fire AoE"),
    ("그리모어", "Grimoire"),
    ("그리모어(방패 칸)", "Grimoire (shield slot)"),
    ("그리모어(방패)", "Grimoire (shield)"),
    # --- items / charms ---
    ("새로워진 천상의 틈", "The Newly Made Heaven's Breach"),
    ("천상의 틈", "Heaven's Breach"),
    ("새로워진 추위의 파열", "The Newly Made Cold Rupture"),
    ("추위의 파열", "Cold Rupture"),
    ("새로워진 뼈의 분쇄", "The Newly Made Bone Break"),
    ("뼈의 분쇄", "Bone Break"),
    ("깜빡이는 불꽃", "Flickering Flame"),
    ("안다리엘의 두건", "Andariel's Visage"),
    ("요르단(조단)의 반지", "The Stone of Jordan"),
    ("조단 반지", "SOJ"),
    ("요르단", "SOJ"),
    ("조단", "SOJ"),
    ("불카토스의 결혼반지", "Bul-Kathos' Wedding Band"),
    ("마라의 만화경", "Mara's Kaleidoscope"),
    ("거미그물 띠", "Arachnid Mesh"),
    ("배틀 부츠", "War Traveler"),
    ("모래폭풍 여로", "Sandstorm Trek"),
    ("기드의 운", "Gheed's Fortune"),
    ("서슬꼬리", "Razortail"),
    ("대군주의", "Trang-Oul's"),
    ("타이탄", "Titan's Revenge"),
    ("썬더스트로크", "Thunderstroke"),
    ("드라쿨", "Dracul's Grasp"),
    ("라이프 탭", "Life Tap"),
    ("리퍼", "The Reaper's Toll"),
    ("에테 리퍼", "eth Reaper's Toll"),
    ("칠흑서리", "Darkforce Spawn"),
    ("샤코", "Shako"),
    ("감시자의 천둥", "Eschuta's Temper"),
    ("에슈타의 성미", "Eschuta's Temper"),
    ("마수", "Magefist"),
    ("혹", "Find Item"),
    ("천사의 의복", "Angel's Vestments"),
    ("천사 세트", "Angel's set"),
    ("물리 파괴참", "Physical Sunder Charm"),
    ("마법 파괴참", "Magic Sunder Charm"),
    ("냉기 파괴참", "Cold Sunder Charm"),
    ("화염/물리 파괴참", "Fire/Physical Sunder Charm"),
    ("파괴참", "Sunder Charm"),
    ("번개 스킬참", "Lightning skillers"),
    ("냉기 스킬참", "Cold skillers"),
    ("전투 스킬참", "Combat skillers"),
    ("소환 스킬참", "Summoning skillers"),
    ("뼈와 독 스킬참", "Poison & Bone skillers"),
    ("투창 스킬참", "Javelin skillers"),
    ("원소 스킬참", "Elemental skillers"),
    ("변신 스킬참", "Shape Shifting skillers"),
    ("무술 스킬참", "Martial Arts skillers"),
    ("스킬참", "skillers"),
    ("애니참", "Anni"),
    ("횃불참", "Torch"),
    ("횃불", "Torch"),
    ("맥어뎀참", "max damage charms"),
    ("맥어뎀", "max damage"),
    ("스몰참", "small charms"),
    ("그랜드참", "grand charms"),
    ("올레지/생명", "all-res/life"),
    ("올레지", "all-res"),
    ("올인", "all-in"),
    # --- gear slang ---
    ("5/5 번개 주얼작", "5/5 Lightning facet"),
    ("주얼작", "facet socket"),
    ("라깍", "IAS/FHR jewel"),
    ("으뜸 15/20", "perfect 15/20"),
    ("으뜸", "perfect"),
    ("패캐", "FCR"),
    ("패힛", "FHR"),
    ("이속", "FRW"),
    ("공속", "IAS"),
    ("매찬", "Magic Find"),
    ("삥/", "GF/"),
    ("삥", "Gold Find"),
    ("에테 ", "eth "),
    ("에테", "eth"),
    ("아콘 스태프", "Archon Staff"),
    ("아콘 플레이트", "Archon Plate"),
    ("아콘", "Archon Plate"),
    ("더스크/아콘", "Dusk Shroud / Archon Plate"),
    ("더스크", "Dusk Shroud"),
    ("메이지 플레이트", "Mage Plate"),
    ("크리스탈 소드", "Crystal Sword"),
    ("자이언트 쓰레셔", "Giant Thresher"),
    ("크립틱 액스", "Cryptic Axe"),
    ("콜로서스 불즈", "Colossus Voulge"),
    ("쓰레셔/맨캐쳐", "Thresher / Mancatcher"),
    ("쓰레셔", "Thresher"),
    ("맨캐쳐", "Mancatcher"),
    ("숏 스태프", "Short Staff"),
    ("세크리드 타지", "Sacred Targe"),
    ("서클릿", "Circlet"),
    ("다이어뎀", "Diadem"),
    ("모나크", "Monarch"),
    ("플레일", "Flail"),
    ("폴암", "Polearm"),
    ("루닉 탤런", "Runic Talons"),
    ("언어스드 원드", "Unearthed Wand"),
    ("양손 무기", "two-handed weapon"),
    ("양손", "two-hand"),
    ("쌍수", "dual wield"),
    ("클로", "claws"),
    ("스왑", "swap"),
    ("본세팅", "main setup"),
    ("사전버프", "prebuff"),
    ("가성비", "budget"),
    ("종결 빌드", "endgame build"),
    ("종결", "endgame"),
    ("자립", "self-sufficient farming"),
    ("앵벌", "farming"),
    ("육성", "leveling"),
    ("레벨링", "leveling"),
    ("버스", "boosting"),
    ("본캐", "main character"),
    ("첫 캐릭", "starter character"),
    ("래더", "Ladder"),
    ("비레더", "non-Ladder"),
    ("스탠다드", "Standard"),
    ("시즌 초", "season start"),
    ("시즌", "season"),
    # --- places / bosses ---
    ("카오스 샌크츄어리", "Chaos Sanctuary"),
    ("공포의 영역", "Terror Zones"),
    ("테러존", "Terror Zones"),
    ("잊혀진 탑", "Forgotten Tower"),
    ("카우 레벨", "Cow Level"),
    ("카우", "Cows"),
    ("카오스", "Chaos"),
    ("피트", "Pit"),
    ("헬포지", "Hellforge"),
    ("트리스트럼", "Tristram"),
    ("안다리엘", "Andariel"),
    ("메피스토", "Mephisto"),
    ("디아블로", "Diablo"),
    ("바알", "Baal"),
    ("카운테스", "Countess"),
    ("고대인", "Ancients"),
    ("라주크", "Larzuk"),
    ("우버", "Uber"),
    ("릴리스", "Lilith"),
    ("듀리엘", "Duriel"),
    ("이즈얼", "Izual"),
    ("헬 안다", "Hell Andariel"),
    ("헬 메피", "Hell Mephisto"),
    ("헬 바알", "Hell Baal"),
    ("헬 ", "Hell "),
    ("악몽 ", "Nightmare "),
    ("노말 ", "Normal "),
    ("지옥", "Hell"),
    ("악몽", "Nightmare"),
    ("노말", "Normal"),
    # --- auras / merc ---
    ("ACT 2 위세 무한 용병", "Act 2 Might Infinity merc"),
    ("ACT 2 신성한 빙결 통찰 용병", "Act 2 Holy Freeze Insight merc"),
    ("ACT 2 위세 용병 (노화)", "Act 2 Might merc (Decrepify)"),
    ("ACT 2 위세 자존심 용병", "Act 2 Might Pride merc"),
    ("ACT 2 위세 통찰 용병 (자가 무한 기준)", "Act 2 Might Insight merc (self Infinity)"),
    ("ACT 1 신념 용병 (광신 오라)", "Act 1 Faith merc (Fanaticism)"),
    ("ACT 2 ", "Act 2 "),
    ("ACT 1 ", "Act 1 "),
    ("사막 용병", "Desert mercenary"),
    ("2막 사막", "Act 2 Desert"),
    ("2막 용병", "Act 2 merc"),
    ("1막 신념", "Act 1 Faith"),
    ("용병", "merc"),
    ("무한", "Infinity"),
    ("통찰", "Insight"),
    ("인내", "Fortitude"),
    ("수수께끼", "Enigma"),
    ("영혼", "Spirit"),
    ("배신", "Treachery"),
    ("연기", "Smoke"),
    ("잠행", "Stealth"),
    ("학식", "Lore"),
    ("신념", "Faith"),
    ("자존심", "Pride"),
    ("순종", "Obedience"),
    ("치료", "Cure"),
    ("방벽", "Bulwark"),
    ("고뇌", "Grief"),
    ("망명", "Exile"),
    ("화이트", "White"),
    ("꽃잎", "Leaf"),
    ("고대인의 서약", "Ancient's Pledge"),
    ("서약", "Ancient's Pledge"),
    ("오크의 심장", "Heart of the Oak"),
    ("호토", "HOTO"),
    ("콜투암스", "Call to Arms"),
    ("명예의 굴레", "Chains of Honor"),
    ("초승달", "Crescent Moon"),
    ("불사조", "Phoenix"),
    ("모자이크", "Mosaic"),
    ("탈태", "Metamorphosis"),
    ("집착", "Obsession"),
    ("스트렝스", "Strength"),
    ("오라", "aura"),
    # --- stats / UI labels ---
    ("시전 속도", "Faster Cast Rate"),
    ("타격 회복", "Faster Hit Recovery"),
    ("공격 속도", "Increased Attack Speed"),
    ("달리기·걷기", "Faster Run/Walk"),
    ("달리기/걷기", "Faster Run/Walk"),
    ("모든 저항", "All Resistances"),
    ("모든 스킬", "All Skills"),
    ("생명력", "Life"),
    ("활력", "Vitality"),
    ("민첩", "Dexterity"),
    ("에너지", "Energy"),
    ("마나", "Mana"),
    ("명중률", "Attack Rating"),
    ("명중", "Attack Rating"),
    ("방어력", "Defense"),
    ("블럭확률증가", "Increased Chance of Blocking"),
    ("블럭 확률", "Chance of Blocking"),
    ("블럭", "block"),
    ("저항", "resist"),
    ("레지", "res"),
    ("물리 면역", "Physical Immune"),
    ("화염 면역", "Fire Immune"),
    ("물리 감소", "Physical Damage Reduction"),
    ("물리 피해", "Physical Damage"),
    ("물리 딜", "Physical damage"),
    ("마법 피해", "Magic Damage"),
    ("화염 피해", "Fire Damage"),
    ("번개 피해", "Lightning Damage"),
    ("냉기 피해", "Cold Damage"),
    ("독 피해", "Poison Damage"),
    ("흡혈", "life steal"),
    ("관통", "Pierce"),
    ("밀도", "packs"),
    ("잡몹", "trash mobs"),
    ("보스", "boss"),
    ("프레임", "frame"),
    ("스탯", "Stats"),
    ("인벤토리", "Inventory"),
    ("운영법", "Playstyle"),
    ("스킬", "Skills"),
    ("시너지", "synergy"),
    ("요구치", "requirements"),
    ("장비", "gear"),
    ("갑옷", "Armor"),
    ("투구", "Helm"),
    ("방패", "Shield"),
    ("무기", "Weapon"),
    ("장갑", "Gloves"),
    ("신발", "Boots"),
    ("벨트", "Belt"),
    ("장신구", "Jewelry"),
    ("반지", "Ring"),
    ("아뮬", "Amulet"),
    ("주얼", "Jewel"),
    ("룬어", "runeword"),
    ("유니크", "unique"),
    ("큐브", "cube"),
    ("소켓", "socket"),
    ("홈", "sockets"),
    ("베이스", "base"),
    ("템트리", "gear tree"),
    ("템", "gear"),
    ("딜", "damage"),
    ("어그로", "aggro"),
    ("차지", "charges"),
    ("마무리기", "finisher"),
    ("변신", "shapeshift"),
    ("늑대", "Werewolf"),
    ("투창", "Javelin"),
    ("창", "Spear"),
    ("활", "Bow"),
    ("검", "Sword"),
    ("힘 ", "Strength "),
    ("힘+", "Strength +"),
    ("힘", "Strength"),
    ("또는", "or"),
    ("대안", "alt"),
    ("선택", "optional"),
    ("유지", "keep"),
    ("재고용", "rehire"),
    ("고용", "hire"),
    ("추천", "recommended"),
    ("특화", "specialized"),
    ("기준", "setup"),
    ("자가", "self"),
    ("초반", "early"),
    ("초중반", "early-mid"),
    ("중반", "mid"),
    ("이후", "later"),
    ("필수", "required"),
    ("없으면", "if unavailable"),
    ("있으면", "if available"),
    ("됩니다.", "."),
    ("습니다.", "."),
    ("십니다.", "."),
    ("주세요.", "."),
    ("됩니다", ""),
    ("습니다", ""),
    ("십니다", ""),
    ("주세요", ""),
]

# Extra prose polish for leveling/playstyle (applied after glossary)
PROSE_EXTRA: list[tuple[str, str]] = [
    ("페이즈 블레이드", "Phase Blade"),
    ("페이즈블레이드", "Phase Blade"),
    ("그랜드 매이트런 보우", "Grand Matron Bow"),
    ("그랜드 매트론 보우", "Grand Matron Bow"),
    ("참룬작", "Cham Rune socket"),
    ("베르룬작", "Ber Rune socket"),
    ("참룬", "Cham Rune"),
    ("베르룬", "Ber Rune"),
    ("샤엘/옴작", "Shael/Ohm socket"),
    ("옴작", "Ohm socket"),
    ("루비 ", "Ruby "),
    ("파다이", "P-Diamond"),
    ("증뎀", "ED"),
    ("속죄", "Redemption"),
    ("기동 alt", "mobility alt"),
    ("기동:", "mobility:"),
    ("기동 ", "mobility "),
    ("생존:", "survivability:"),
    ("생존 ", "survivability "),
    ("레어/크래프트", "rare/crafted"),
    ("크래프트", "crafted"),
    ("레어", "rare"),
    ("FCR링", "FCR ring"),
    ("링", " ring"),
    ("셉터/도끼", "scepter/axe"),
    ("도끼", "axe"),
    ("셉터", "scepter"),
    ("9레벨", "level 9"),
    ("레벨", "level"),
    ("강령 ", "Necro "),
    ("사이드/", "Scythe / "),
    ("self착용", "self-wield"),
    ("동시 착용 가능", "can equip both"),
    ("전투 중", "in combat"),
    ("요구 최저", "lowest Str req"),
    ("꺼불", "Flickering Flame"),
    ("혼돈/", "Chaos /"),
    ("혼돈 ", "Chaos "),
    ("화염 ", "Fire "),
    ("냉기 ", "Cold "),
    ("독 ", "Poison "),
    ("번개 ", "Lightning "),
    ("물리 ", "Physical "),
    ("마력 보호막", "Energy Shield"),
    ("염력", "Telekinesis"),
    ("거울상 칼날", "Mirror Blades"),
    ("칼날 이동", "Blade Move"),
    ("죽음 파수꾼", "Death Sentry"),
    ("감전 그물", "Shock Web"),
    ("그림자 전령", "Shadow Master"),
    ("덫 스킬참", "Traps skillers"),
    ("기괴 스킬참", "Warlock skillers"),
    ("불길의 균열", "Flame Rift"),
    ("부패의 분열", "Rotting Cleavage"),
    ("화염 파괴참", "Fire Sunder Charm"),
    ("독 파괴참", "Poison Sunder Charm"),
    ("쌍 (", "pair ("),
    ("쌍수", "dual wield"),
    (" 쌍", " dual"),
    ("달성)", "breakpoint)"),
    ("없음", "none"),
    ("착용", "equip"),
    ("세팅", "setup"),
    ("단일", "single"),
    ("시 ", " when "),
    ("일격 ", "Strike "),
    ("업글 권장", "upgrade recommended"),
    ("사용 불가", "N/A"),
    ("듀얼 ", "dual "),
    ("렘룬작", "Lem Rune socket"),
    ("조드룬작", "Zod Rune socket"),
    ("2드루 ", "+2 Druid "),
    ("2어쌔 ", "+2 Assassin "),
    ("무술 ", "Martial Arts "),
    ("범용:", "general:"),
    ("FCR용)", "FCR)"),
    ("패캐용", "FCR"),
    ("텔포 ", "Teleport "),
    ("Warlock은", "Warlock"),
    ("워록은", "Warlock"),
    ("용병이", "merc "),
    ("용병 ", "merc "),
    ("지팡이", "staff"),
    ("이라 ", " so "),
    ("이면 ", " if "),
    ("이때 ", "then "),
    ("merc이", "merc "),
    ("독뼈", "P&B"),
    ("독깍", "enemy Poison Resist"),
    ("(+강령)", "(+Necro)"),
    ("기술 피해", "Skill Damage"),
    ("생존·", "survivability · "),
    ("번개:", "Lightning:"),
    ("처음부터 육성 가이드", "Fresh Ladder Leveling Guide"),
    ("육성 가이드", "Leveling Guide"),
    ("시즌 첫 캐릭으로 가장 편합니다", "is the easiest season starter"),
    ("첫 캐릭 추천", "Best starter"),
    ("자립·버스", "Self-farm / boosting"),
    ("자바 육성", "Javelin leveling"),
    ("소환이 편함", "Easy summons"),
    ("트랩 → 모자이크", "Traps → Mosaic"),
    ("바람 / 늑대", "Wind / Werewolf"),
    ("왚 / 삥", "WW / GF"),
    ("워록 · 양손+방패", "Warlock · 2H + shield"),
    ("1. 노말 (1~40)", "1. Normal (1–40)"),
    ("2. 악몽 (40~60)", "2. Nightmare (40–60)"),
    ("3. 지옥 진입 (60~75)", "3. Entering Hell (60–75)"),
    ("4. 자립 후 종결로", "4. After farming — toward endgame"),
    ("5. 악마술사(워록) 육성", "5. Warlock leveling"),
    ("6. 용병 템 트리 (초반 룬어 기준)", "6. Merc gear tree (early runewords)"),
    ("노말 2막", "Normal Act 2"),
    ("지옥 초입", "Early Hell"),
    ("자립·종결", "Farming / endgame"),
    ("메아리 종결 보기", "View Resonating Blow endgame"),
    ("종말 종결 보기", "View Apocalypse endgame"),
    ("메아리 종결", "Resonating Blow endgame"),
    ("종말 종결", "Apocalypse endgame"),
    ("엘 ~ 랄", "El – Ral"),
    ("엘 ~ 아이오", "El – Io"),
    ("엘 ~ 아이스트", "El – Ist"),
    ("솔~움", "Sol – Um"),
    ("헬~굴", "Hel – Gul"),
    ("말·굴·앰", "Mal · Gul · Amn"),
    ("탈·에드·랄·오르트·탈", "Tal · Eth · Ral · Ort · Tal"),
    ("탈+에드", "Tal + Eth"),
    ("티르+랄", "Tir + Ral"),
    ("랄+오르트+탈", "Ral + Ort + Tal"),
    ("오르트+솔", "Ort + Sol"),
    ("탈+주울+오르트+앰", "Tal + Thul + Ort + Amn"),
    ("랄+티르+탈+솔", "Ral + Tir + Tal + Sol"),
    ("네프+룸", "Nef + Lum"),
    ("샤엘+주울+렘", "Shael + Thul + Lem"),
    ("헬+코+주울+에드+팔", "Hel + Ko + Thul + Eth + Fal"),
    ("베르+말+베르+아이스트", "Ber + Mal + Ber + Ist"),
    ("앰+티르", "Amn + Tir"),
    ("아이오 3개", "3 Io"),
    ("35패캐", "35 FCR"),
    ("75패캐", "75 FCR"),
    ("125패캐", "125 FCR"),
    ("패캐 65", "65 FCR"),
    ("패캐 117%", "117% FCR"),
    ("패캐 105%", "105% FCR"),
    ("패캐 125%", "125% FCR"),
    ("패캐 99%", "99% FCR"),
    ("황금 저항(75)", "capped resists (75)"),
    ("−100", "-100"),
    ("+175", "+175"),
    ("+스킬", "+Skills"),
    ("+3 스킬", "+3 Skills"),
    ("+3 화염", "+3 Fire"),
    ("+3 뼈 창", "+3 Bone Spear"),
    ("+3 불사조 일격", "+3 Phoenix Strike"),
    ("+4 모든 스킬", "+4 to All Skills"),
    ("+1 스킬", "+1 Skills"),
    ("+50", "+50"),
    ("2소켓", "2-socket"),
    ("3소켓", "3-socket"),
    ("4소켓", "4-socket"),
    ("5소켓", "5-socket"),
    ("6소켓", "6-socket"),
    ("악의 소굴", "Den of Evil"),
    ("라다멘트", "Radament"),
    ("라만 에센의 책", "The Book of Skill (Lam Esen)"),
    ("이주알", "Izual"),
    ("말라 저항", "Anya resist"),
    ("아리앗 정상", "Arreat Summit"),
    ("사막 위세(물리)", "Desert Might (Physical)"),
    ("신성한 빙결(안전)", "Holy Freeze (safe)"),
    ("페이퍼돌", "paperdoll"),
    ("영구 보상", "permanent quest rewards"),
    ("공유 창고", "shared stash"),
    ("아이템 찾기 전용", "Find Item only"),
    ("한국 시간", "KST"),
]


def apply_glossary(text: str, glossary: list[tuple[str, str]], passes: int = 3) -> str:
    out = str(text)
    ordered = sorted(glossary, key=lambda x: len(x[0]), reverse=True)
    for _ in range(passes):
        prev = out
        for ko, en in ordered:
            out = out.replace(ko, en)
        if out == prev:
            break
    return out


def prefer_paren_english(text: str) -> str:
    """If string ends with ASCII parenthetical, prefer that English part."""
    s = str(text).strip()
    m = PAREN_EN.search(s)
    if m and HANGUL.search(s[: m.start()]):
        return m.group(1).strip()
    return s


def translate_slot(slot: str) -> str:
    if slot in SLOT_MAP:
        return SLOT_MAP[slot]
    preferred = prefer_paren_english(slot)
    if preferred != slot and not HANGUL.search(preferred):
        return preferred
    return apply_glossary(slot, GLOSSARY + PROSE_EXTRA)


def translate_text(text: str) -> str:
    if not text:
        return text
    out = str(text)
    # replace known item/runeword Korean names first (longest keys)
    for ko, en in sorted(ko_name_to_en.items(), key=lambda x: -len(x[0])):
        if ko and ko in out:
            out = out.replace(ko, en)
    out = apply_glossary(out, PROSE_EXTRA + GLOSSARY)
    # cleanup doubled spaces / empty punct leftovers from polite endings
    out = re.sub(r" {2,}", " ", out)
    out = re.sub(r"\s+\.", ".", out)
    out = re.sub(r"\s+,", ",", out)
    return out.strip() if isinstance(text, str) and text == text.strip() else out


def resolve_link_name(seg: dict) -> str:
    sid = seg.get("id")
    dtype = seg.get("dataType")
    if dtype == "unique" and sid in EN_UNIQUES:
        return EN_UNIQUES[sid]["name"]
    if dtype == "runeword" and sid in EN_RW:
        return EN_RW[sid]["name"]
    # fallback: eng field via KO sources / glossary
    name = seg.get("name", "")
    if sid in EN_UNIQUES:
        return EN_UNIQUES[sid]["name"]
    if sid in EN_RW:
        return EN_RW[sid]["name"]
    if name in ko_name_to_en:
        return ko_name_to_en[name]
    return translate_text(name) or name


def translate_content(content: list) -> list:
    out = []
    for seg in content or []:
        s = deepcopy(seg)
        if s.get("type") == "link" and s.get("id") is not None:
            s["name"] = resolve_link_name(s)
        elif s.get("type") == "text" and "value" in s:
            s["value"] = translate_text(s["value"])
        elif "name" in s and HANGUL.search(str(s.get("name", ""))):
            s["name"] = translate_text(s["name"])
        out.append(s)
    return out


def translate_merc(merc: dict) -> dict:
    m = deepcopy(merc)
    m["title"] = translate_text(merc.get("title", ""))
    gear = []
    for g in merc.get("gear") or []:
        gg = deepcopy(g)
        gg["slot"] = translate_slot(g.get("slot", ""))
        gg["content"] = translate_content(g.get("content") or [])
        gear.append(gg)
    m["gear"] = gear
    return m


def build_builds() -> dict:
    src = json.loads((DATA / "builds.json").read_text(encoding="utf-8"))
    out = deepcopy(src)
    items = []
    for it in src["items"]:
        b = deepcopy(it)
        meta = BUILD_META.get(it["id"], {})
        b["title"] = meta.get("title") or prefer_paren_english(it["title"])
        b["subtitle"] = meta.get("subtitle") or translate_text(it["subtitle"])
        if "badge" in it:
            b["badge"] = meta.get("badge") or translate_text(it["badge"])
        b["tags"] = list(it.get("tags") or [])
        b["legacyKey"] = it.get("legacyKey")
        slots = []
        for sl in it.get("slots") or []:
            slots.append(
                {
                    "slot": translate_slot(sl["slot"]),
                    "content": translate_content(sl.get("content") or []),
                }
            )
        b["slots"] = slots
        b["merc"] = translate_merc(it.get("merc") or {})
        prose = BUILD_PROSE.get(it["id"])
        if prose:
            b["stats"] = prose["stats"]
            b["inventory"] = prose["inventory"]
            b["skills"] = prose["skills"]
            b["playstyle"] = prose["playstyle"]
            b["info"] = compose_info(prose)
        else:
            for field in ("info", "playstyle", "stats", "inventory", "skills"):
                if field in it and isinstance(it[field], str):
                    b[field] = translate_text(it[field])
        items.append(b)
    out["items"] = items
    return out


# ---------------------------------------------------------------------------
# Leveling — curated English (readable community guide tone)
# ---------------------------------------------------------------------------
LEVELING_EN = {
    "title": "Fresh Ladder Leveling Guide",
    "aliases": [
        "leveling",
        "ladder start",
        "starter",
        "Countess",
        "Stealth",
        "Warlock",
        "Resonating Blow",
        "Apocalypse",
        "merc",
        "gear tree",
        "Strength",
    ],
    "intro": (
        "Right after a Ladder launch, endgame gear matters less than which runewords "
        "you craft and where you farm. Follow the order below and you will stay on track "
        "from Normal through Hell self-sufficiency."
    ),
    "seasonNote": (
        "From Ladder Season 15 (August 22, 2026), early/mid uniques and Angel's Vestments "
        "are buffed — equip them as they drop. Physical builds especially benefit from the "
        "Angel set for Attack Rating. Previous-season shared-stash items move to a "
        "'Find Item only' tab, so move what you need into this season's stash yourself."
    ),
    "classes": [
        {
            "name": "Sorceress",
            "badge": "Best starter",
            "text": (
                "Teleport makes Sorceress the easiest season starter. "
                "Put a point in Warmth, clear Normal with Fireball or Frozen Orb, "
                "and take at least 1 Teleport. From Nightmare you can respec to Blizzard "
                "or Chain Lightning. An Insight merc removes most mana stress."
            ),
            "buildId": 70002,
        },
        {
            "name": "Paladin",
            "badge": "Self-farm / boosting",
            "text": (
                "Clear Normal with Holy Bolt and Charge, then move to Blessed Hammer "
                "once you have Spirit and Ancient's Pledge. Shield resists alone keep Hell stable."
            ),
            "buildId": 70003,
        },
        {
            "name": "Amazon",
            "badge": "Javelin leveling",
            "text": (
                "Push Javelin/Spear skills, then dump into Lightning Fury when it unlocks. "
                "Until Titan's Revenge drops, use skill-pointed javelins."
            ),
            "buildId": 70007,
        },
        {
            "name": "Necromancer",
            "badge": "Easy summons",
            "text": (
                "Skeletons plus Corpse Explosion is the safest path. "
                "For Bone Spear, aim for White (+3 Bone Spear Unearthed Wand)."
            ),
            "buildId": 70005,
        },
        {
            "name": "Assassin",
            "badge": "Traps → Mosaic",
            "text": (
                "Level on Lightning Sentry traps early. "
                "Mosaic comes after Mal · Gul · Amn — socket +3 Phoenix Strike Runic Talons dual-wield."
            ),
            "buildId": 70014,
        },
        {
            "name": "Druid",
            "badge": "Wind / Werewolf",
            "text": (
                "Level as Wind (Tornado) or Werewolf shapeshift. "
                "Metamorphosis helms are a Hell+ concern."
            ),
            "buildId": 70011,
        },
        {
            "name": "Barbarian",
            "badge": "WW / GF",
            "text": (
                "Start Bash, transition to Whirlwind. "
                "One point in Find Item early makes later farming smoother."
            ),
            "buildId": 70009,
        },
        {
            "name": "Warlock",
            "badge": "Warlock · 2H + shield",
            "text": (
                "Two-hand weapons and Grimoire (shield slot) can be worn together, "
                "so Insight polearm plus Pledge/Spirit shield levels cleanly. "
                "Early: Demon Binding + Devour into Resonating Blow, or Flame Wave / Fire Ring AoE. "
                "Resonating Blow is FCR (75 → 125), not IAS."
            ),
            "buildId": 70015,
            "buildIds": [
                {"id": 70015, "label": "Resonating Blow endgame"},
                {"id": 70016, "label": "Apocalypse endgame"},
            ],
        },
    ],
    "stages": [
        {
            "id": "normal",
            "title": "1. Normal (1–40)",
            "goal": "Craft Teleport tools, Stealth, and Ancient's Pledge; hit Ancients at 20; kill Baal.",
            "steps": [
                "Always take Den of Evil, Radament, Lam Esen's Tome, Izual, and Anya resists each difficulty. Rewards are summarized in menu 10.",
                "Farm Countess (Forgotten Tower level 5) for Tal · Eth · Ral · Ort · Tal. Normal Countess drops up to Ral.",
                "Make Stealth (Tal + Eth) in a 2-socket armor first — FRW, FCR, and FHR in one piece.",
                "Fire Sorc: Leaf (Tir + Ral) in a +Fire Short Staff; Warmth/Fireball staffmods help.",
                "Ancient's Pledge (Ral + Ort + Tal) in a 3-socket shield removes most resist worry.",
                "Hire an Act 2 Desert merc — Might or Holy Freeze both work. When Amn drops, Strength (Amn + Tir) on a 2-socket polearm. Merc gear by stage is in section 6.",
                "Arreat Summit Ancients require level 20. If short, Cow Level or Countess.",
            ],
        },
        {
            "id": "nightmare",
            "title": "2. Nightmare (40–60)",
            "goal": "Craft Lore, Spirit sword, and Insight; Smoke makes Hell resists much easier.",
            "steps": [
                "Nightmare Countess drops through Io. Sol and Amn here finish Lore, Spirit, and Insight mats.",
                "Lore (Ort + Sol) in a 2-socket helm — Circlet with +Skills is ideal.",
                "Spirit (Tal + Thul + Ort + Amn) wants a 4-socket Crystal Sword. Many Larzuk a Normal white Crystal Sword to 4os — save socket quests.",
                "Insight (Ral + Tir + Tal + Sol) on a 4-socket polearm for the Act 2 merc — Meditation nearly ends mana issues. Rehire same aura in Nightmare Act 2; armor Smoke, helm Lore.",
                "Smoke (Nef + Lum) is +50 all resist — craft before Hell. Nightmare Countess does not drop Lum; cube 3 Io or farm Nightmare Hellforge / Hell Countess. 2-socket Mage Plate is the easy base.",
                "Ancients are level 40. If resists are low, finish Smoke first.",
            ],
        },
        {
            "id": "hell",
            "title": "3. Entering Hell (60–75)",
            "goal": "Approach 75 resists and farm Countess, Andariel, Mephisto, and Cows for self-sufficiency.",
            "steps": [
                "Hell starts at −100 resist. Capped 75 needs +175 from gear — Smoke's +50 shines here.",
                "Ancients are level 60. If short, more Nightmare Cows or Nightmare Baal.",
                "Hell Countess drops through Ist — farm Treachery (Shael + Thul + Lem) mats and higher runes.",
                "Treachery on Mage Plate is a Fade prebuff. On-hit Fade spikes resists and PDR. If you don't use it, give it to the merc.",
                "Spirit Monarch (35 FCR) is the caster shield endgame. Until Strength 156 is comfortable, keep Pledge.",
                "Farm Andariel / Mephisto for Shako, SOJ, Andariel's Visage, and similar. Even without them, runewords alone can clear Cows and Chaos.",
            ],
        },
        {
            "id": "self",
            "title": "4. After farming — toward endgame",
            "goal": "Target HOTO, CTA, and Enigma, then swap into your class endgame build.",
            "steps": [
                "Heart of the Oak (HOTO) on Flail is standard — 40 FCR, all-res, and +3 Skills.",
                "Call to Arms on a 5-socket Crystal Sword for Battle Command / Battle Orders swap.",
                "Enigma prefers Mage Plate (55 Strength). Classes without Teleport change how they play once it drops.",
                "Further gear is in section 1 endgame builds by class. Warlocks should read section 5 first, then Resonating Blow / Apocalypse paperdolls. Merc early tree is section 6; endgame section 8; farms section 12.",
            ],
        },
        {
            "id": "warlock",
            "title": "5. Warlock leveling",
            "goal": (
                "Tank with Binding summons, cover mana/res with Insight + shield, "
                "then self-farm Resonating Blow 125 FCR or Apocalypse Fire."
            ),
            "buildIds": [
                {"id": 70015, "label": "View Resonating Blow endgame"},
                {"id": 70016, "label": "View Apocalypse endgame"},
            ],
            "steps": [
                "Warlocks wear a two-hand weapon and Grimoire (shield slot) together. Insight polearm plus Ancient's Pledge / Spirit / Phoenix on the off-hand is the core plan.",
                "Normal: Demon Binding (tank summon) and Devour (leech/mana) first, then dump Resonating Blow. For Fire, take Flame Wave, Fire Ring, and Fire Seal.",
                "Resonating Blow is FCR, not IAS. Hit 75 FCR first; once farming, aim for 125 (same table as Paladin/Necro). Missing breakpoints feels terrible.",
                "Stealth armor and Pledge shield match other classes. Fire Warlock can Leaf a +Fire Short Staff.",
                "In Nightmare, craft Insight (Ral + Tir + Tal + Sol) on eth Thresher / Cryptic Axe for yourself — Meditation keeps mana up. Pair Lore helm and Spirit shield (or Spirit sword swap).",
                "Bosses: Lower Resist first, then Resonating Blow / Apocalypse. Bound demon in front while you damage from pack center is safest.",
                "In Hell, Smoke for all-res; Enigma unlocks Teleport mobility. Resonating endgame is Insight + Phoenix Monarch; Apocalypse is Obsession Archon Staff + Flickering Flame + Grimoire.",
                "Apocalypse (Fire) does almost nothing to Fire Immunes. Until Sunder and Infinity Conviction, Resonating Blow farms more easily.",
                "If you hold Insight, give the merc Obedience or Infinity. Merc order is section 6.",
            ],
        },
    ],
    "mercTree": {
        "title": "6. Merc gear tree (early runewords)",
        "goal": "Raise an Act 2 Desert merc from Normal; upgrade weapon Strength → Insight → Infinity.",
        "rows": [
            {
                "when": "Normal Act 2",
                "hire": "Desert Might (Physical) or Holy Freeze (safe)",
                "weapon": "Any polearm/spear. When Amn drops: Strength (Amn + Tir) 2-socket polearm",
                "armor": "Spare Stealth, or any armor",
                "helm": "Any helm",
            },
            {
                "when": "Nightmare",
                "hire": "Rehire same aura in Nightmare Act 2 (higher aura level)",
                "weapon": "Insight (Ral + Tir + Tal + Sol) 4-socket polearm. Eth Thresher / Cryptic Axe; budget 4os Colossus Voulge",
                "armor": "Smoke (Nef + Lum) or Stealth",
                "helm": "Lore (Ort + Sol)",
            },
            {
                "when": "Early Hell",
                "hire": "Hell Act 2 rehire optional — keep the aura",
                "weapon": "Keep Insight. If you hold Insight, merc gets Obedience (Hel + Ko + Thul + Eth + Fal)",
                "armor": "Treachery (Shael + Thul + Lem) — Fade",
                "helm": "Keep Lore. Poison-heavy: Cure; dies often: Bulwark",
            },
            {
                "when": "Farming / endgame",
                "hire": "Act 2 Might or Holy Freeze. Bowazon / Werewolf endgame: Act 1 Faith",
                "weapon": "Infinity (Ber + Mal + Ber + Ist) eth Giant Thresher / Cryptic Axe",
                "armor": "Fortitude eth Archon Plate",
                "helm": "Andariel's Visage; until then Lore / Cure / Bulwark",
            },
        ],
        "steps": [
            "Season-start merc default is Act 2 Desert. Might for Physical damage, Holy Freeze for safety. Rehire same aura in Nightmare Act 2 for higher aura level.",
            "Craft your Stealth / Pledge first; spare runes go to the merc. Normal Amn → Strength (Amn + Tir) on 2-socket polearm for leech and Crushing Blow so the merc lives.",
            "As soon as Sol appears in Nightmare, craft Insight. Meditation nearly ends your mana issues. Ideal bases: eth Thresher / Cryptic Axe; otherwise 4os Colossus Voulge first.",
            "Before Hell, Smoke for merc all-res; when Lem drops, Treachery. On-hit Fade spikes resists and PDR. You can Fade-prebuff then hand Treachery to the merc.",
            "Classes that self-wield Insight (Warlock) should move the merc to Obedience, then Infinity when Conviction is needed.",
            "Endgame order: Infinity weapon → Fortitude armor → Andariel's Visage. Class merc endgames are also in menu 8.",
        ],
    },
    "runewords": [
        {"id": 30002, "name": "Stealth", "when": "Early Normal", "why": "FRW · FCR · FHR. Craft this first."},
        {"id": 30003, "name": "Leaf", "when": "Fire Sorc / Warlock Normal", "why": "Socket a +3 Fire Short Staff."},
        {"id": 30004, "name": "Ancient's Pledge", "when": "After Normal Countess", "why": "Shield resists. Paladins love all-res Sacred Targe."},
        {"id": 30037, "name": "Strength", "when": "Late Normal merc", "why": "Amn + Tir. 2-socket polearm. Leech + CB before Insight."},
        {"id": 30005, "name": "Lore", "when": "Nightmare", "why": "+1 Skills helm. Circlet preferred. Also merc helm."},
        {"id": 30007, "name": "Spirit", "when": "Nightmare", "why": "4-socket Crystal Sword. Later 35 FCR Monarch."},
        {"id": 30018, "name": "Insight", "when": "Nightmare merc / Warlock self", "why": "Meditation. Warlock holds the polearm and a shield together."},
        {"id": 30016, "name": "Obedience", "when": "Hell merc budget", "why": "When you hold Insight. Eth Thresher / Cryptic Axe."},
        {"id": 30036, "name": "Smoke", "when": "Late Nightmare – early Hell", "why": "+50 all-res. 2-socket Mage Plate."},
        {"id": 30017, "name": "Treachery", "when": "Early Hell self / merc", "why": "Fade prebuff. Mage Plate. Also merc armor."},
        {"id": 30025, "name": "Cure", "when": "Hell merc helm", "why": "Cleansing aura. Swap over Lore in poison-heavy areas."},
        {"id": 30026, "name": "Bulwark", "when": "Hell merc helm", "why": "Physical DR. Swap over Lore when the merc dies often."},
        {"id": 30020, "name": "Fortitude", "when": "Merc armor endgame", "why": "Eth Archon Plate. After Treachery."},
        {"id": 30008, "name": "Infinity", "when": "Merc weapon endgame", "why": "Eth Giant Thresher / Cryptic Axe. Conviction aura."},
        {"id": 30019, "name": "Heart of the Oak", "when": "After farming", "why": "Flail base. Caster weapon endgame."},
        {"id": 30006, "name": "Call to Arms", "when": "After farming", "why": "5-socket Crystal Sword. Battle Command swap."},
        {"id": 30022, "name": "Enigma", "when": "Mobility endgame", "why": "Mage Plate. Turning point for non-Teleport classes and Warlock."},
        {"id": 30030, "name": "Flickering Flame", "when": "Fire Warlock endgame", "why": "+3 Fire Skills Diadem. Apocalypse helm."},
        {"id": 30040, "name": "Obsession", "when": "Fire Warlock endgame", "why": "+4 All Skills Archon Staff. 65 FCR in one piece."},
    ],
    "countess": [
        {"diff": "Normal", "runes": "El – Ral", "tip": "Farm Stealth, Leaf, and Pledge mats here."},
        {"diff": "Nightmare", "runes": "El – Io", "tip": "Sol / Amn finish Lore, Spirit, Insight. No Lum — cube 3 Io."},
        {"diff": "Hell", "runes": "El – Ist", "tip": "Farm Lem for Treachery and higher runes. Core season-start farm."},
    ],
    "sockets": [
        {"diff": "Normal Larzuk", "use": "4-socket Crystal Sword (Spirit sword)"},
        {"diff": "Nightmare Larzuk", "use": "4-socket Monarch (Spirit shield)"},
        {
            "diff": "Hell Larzuk",
            "use": "3-socket Mage Plate (Enigma) · Fire Warlock may want 6-socket Archon Staff (Obsession)",
        },
    ],
    "tips": [
        "Season first character: Teleport Sorc, then level your main on the second character.",
        "Boosting only and skipping quest rewards permanently costs skills, stats, and resists. Grab menu-10 permanent rewards each difficulty.",
        "Larzuk sockets are once per difficulty. Recommended order: Spirit sword → Spirit Monarch → Enigma.",
        "Nightmare Hellforge drops Sol–Um (Lum/Lem hope). Hell Hellforge is Hel–Gul.",
        "Default merc is Act 2 Desert. Weapons: Strength → Insight → Infinity. Armor: Stealth/Smoke → Treachery → Fortitude.",
        "Warlocks wear two-hand + Grimoire together. Self Insight with Pledge/Spirit/Phoenix in the shield slot.",
        "Resonating Blow is FCR, not IAS. Hit 75 first; endgame 125. Frame tables are in menu 9.",
        "Physical characters miss often without Attack Rating. Season 15 buffed Angel's Vestments (weapon/ring/amulet) — wear them Normal–Nightmare.",
    ],
}


def build_leveling() -> dict:
    # Start from curated EN; keep buildId numbers from source if structure drifts.
    src = json.loads((DATA / "leveling.json").read_text(encoding="utf-8"))
    out = deepcopy(LEVELING_EN)
    # Sync buildIds from KO source so numbers stay authoritative.
    for ko_c, en_c in zip(src.get("classes") or [], out["classes"]):
        if "buildId" in ko_c:
            en_c["buildId"] = ko_c["buildId"]
        if "buildIds" in ko_c:
            en_c["buildIds"] = [
                {
                    "id": x["id"],
                    "label": next(
                        (
                            e["label"]
                            for e in (en_c.get("buildIds") or [])
                            if e.get("id") == x["id"]
                        ),
                        translate_text(x.get("label", "")),
                    ),
                }
                for x in ko_c["buildIds"]
            ]
    for ko_s, en_s in zip(src.get("stages") or [], out["stages"]):
        en_s["id"] = ko_s["id"]
        if "buildIds" in ko_s:
            en_s["buildIds"] = [
                {
                    "id": x["id"],
                    "label": next(
                        (
                            e["label"]
                            for e in (en_s.get("buildIds") or [])
                            if e.get("id") == x["id"]
                        ),
                        translate_text(x.get("label", "")),
                    ),
                }
                for x in ko_s["buildIds"]
            ]
    # Prefer EN runeword names from EN DB by id
    for row in out.get("runewords") or []:
        rid = row.get("id")
        if rid in EN_RW:
            row["name"] = EN_RW[rid]["name"]
    return out


# ---------------------------------------------------------------------------
# Dropcalc
# ---------------------------------------------------------------------------
DROP_FARM = [
    ("헬 안다리엘", "Hell Andariel"),
    ("헬 메피스토", "Hell Mephisto"),
    ("헬 바알", "Hell Baal"),
    ("헬 디아블로", "Hell Diablo"),
    ("악몽 안다리엘", "Nightmare Andariel"),
    ("악몽 메피스토", "Nightmare Mephisto"),
    ("헬 ", "Hell "),
    ("악몽 ", "Nightmare "),
    ("노말 ", "Normal "),
    ("안다리엘", "Andariel"),
    ("메피스토", "Mephisto"),
    ("디아블로", "Diablo"),
    ("바알", "Baal"),
    ("헬", "Hell"),
    ("악몽", "Nightmare"),
    ("노말", "Normal"),
]


def build_dropcalc() -> dict:
    src = json.loads((DATA / "dropcalc.json").read_text(encoding="utf-8"))
    items = []
    for it in src["items"]:
        row = {"id": it["id"], "oneIn0": it["oneIn0"]}
        if it["id"] in EN_UNIQUES:
            row["name"] = EN_UNIQUES[it["id"]]["name"]
        else:
            row["name"] = translate_text(it.get("name", ""))
        farm = it.get("farm", "")
        for ko, en in sorted(DROP_FARM, key=lambda x: -len(x[0])):
            farm = farm.replace(ko, en)
        row["farm"] = farm
        items.append(row)
    return {"items": items}


# ---------------------------------------------------------------------------
# Patch notes — readable English (not glossary gibberish)
# ---------------------------------------------------------------------------
PATCHNOTES_EN = [
    {
        "version": "Patch 3.3 (Ladder Season 15) — Diablo II: Resurrected Ladder Season 15 is live",
        "badge": "🚀",
        "isActive": True,
        "isOpen": True,
        "link": "https://news.blizzard.com/en-us/article/24296140/ii-15",
        "schedule": [
            "Ladder Season 14 ended — Aug 18 (Tue) 3:00 AM KST",
            "Ladder Season 15 patch rollout began — Aug 19 (Wed)",
            "<b>Ladder Season 15 started — Aug 22 9:00 AM KST</b>",
        ],
        "changes": [
            "<b>Non-Ladder (Standard) carryover:</b> Previous Ladder-only items/runewords "
            "(Madness, Ground, Metamorphosis, Hearth, Temper, Cure, Bulwark, and related) "
            "can now be crafted and used in non-Ladder.",
            "<b>Gear and set balance:</b> Several unique items (e.g. Bloodletter, Battle Branch, "
            "Rogues Bow, Snowclash) and set items received option/required-level adjustments.",
            "<b>Terror Zones / drop tuning:</b> Chance for Rare-or-better drops from Herald "
            "tier 3+ has increased.",
            "<b>Systems and bug fixes:</b> Jump into the fray with new Ladder items, Terror Zone "
            "changes, and assorted bug fixes — see the full notes on the Blizzard page.",
        ],
    },
    {
        "version": "Patch 3.2 (Ladder Season 14 — archive)",
        "badge": "📜",
        "isActive": False,
        "isOpen": False,
        "link": "https://news.blizzard.com/en-us/diablo2",
        "schedule": [
            "Ladder Season 14 start: May 22, 2026 (PDT) / May 23 9:00 AM KST",
            "Warlock class balance updates and a major Terror Zone system overhaul",
        ],
        "changes": [
            "<b>Warlock class tuning:</b> Core skill mechanics reworked and damage synergy balance adjusted.",
            "<b>Terror Zones and Herald tiers:</b> Tier 1–3 Heralds now hunt players inside Terror Zones.",
            "<b>Colossal Ancients difficulty:</b> Magic resist and damage mechanics made more threatening.",
        ],
    },
    {
        "version": "Patch 3.1 (Warlock launch and systems pass)",
        "badge": "📜",
        "isActive": False,
        "isOpen": False,
        "link": "https://news.blizzard.com/en-us/diablo2",
        "schedule": [],
        "changes": [
            "<b>New class — Warlock:</b> Dark magic and summon trees plus dedicated Warlock gear.",
            "<b>Hardcore Level 99 race:</b> Hardcore Ladder race to 99 celebrating the Warlock launch.",
            "Graphics rendering optimizations, lobby filter improvements, and many client crash fixes.",
        ],
    },
]


def localize_blizzard_link(url: str) -> str:
    if not url:
        return url
    return (
        url.replace("/ko-kr/", "/en-us/")
        .replace("news.blizzard.com/ko-kr", "news.blizzard.com/en-us")
    )


def build_patchnotes() -> list:
    src = json.loads((DATA / "patchnotes.json").read_text(encoding="utf-8"))
    # Prefer curated EN; fall back to glossary + link rewrite if lengths diverge
    if len(src) == len(PATCHNOTES_EN):
        out = []
        for ko, en in zip(src, PATCHNOTES_EN):
            row = deepcopy(en)
            row["isActive"] = ko.get("isActive", en["isActive"])
            row["isOpen"] = ko.get("isOpen", en["isOpen"])
            row["badge"] = ko.get("badge", en["badge"])
            row["link"] = localize_blizzard_link(ko.get("link") or en["link"])
            out.append(row)
        return out
    # fallback
    out = []
    for ko in src:
        out.append(
            {
                "version": translate_text(ko.get("version", "")),
                "badge": ko.get("badge"),
                "isActive": ko.get("isActive"),
                "isOpen": ko.get("isOpen"),
                "link": localize_blizzard_link(ko.get("link", "")),
                "schedule": [translate_text(s) for s in ko.get("schedule") or []],
                "changes": [translate_text(s) for s in ko.get("changes") or []],
            }
        )
    return out


# ---------------------------------------------------------------------------
def hangul_count(s: str) -> int:
    return len(HANGUL.findall(s or ""))


def hangul_ratio(s: str) -> float:
    return hangul_count(s) / max(1, len(s or ""))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # validate
    json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    EN.mkdir(parents=True, exist_ok=True)

    builds = build_builds()
    leveling = build_leveling()
    dropcalc = build_dropcalc()
    patchnotes = build_patchnotes()

    write_json(EN / "builds.json", builds)
    write_json(EN / "leveling.json", leveling)
    write_json(EN / "dropcalc.json", dropcalc)
    write_json(EN / "patchnotes.json", patchnotes)

    n_builds = len(builds["items"])
    print(f"wrote builds={n_builds}, leveling stages={len(leveling.get('stages', []))}, "
          f"dropcalc={len(dropcalc['items'])}, patchnotes={len(patchnotes)}")

    # title/subtitle hangul check
    leftover = []
    for it in builds["items"]:
        for field in ("title", "subtitle"):
            if hangul_count(it[field]):
                leftover.append((it["id"], field, it[field]))
        for sl in it["slots"]:
            if hangul_count(sl["slot"]):
                leftover.append((it["id"], "slot", sl["slot"]))
    print(f"hangul leftover in title/subtitle/slot: {len(leftover)}")
    for row in leftover[:10]:
        print(" ", row)

    print("\nsample build[0]:", builds["items"][0]["title"], "|", builds["items"][0]["subtitle"])
    print("  weapon link:", builds["items"][0]["slots"][0]["content"][0])
    print("  merc:", builds["items"][0]["merc"]["title"])
    print("  playstyle:", builds["items"][0]["playstyle"][:120], "...")

    print("\nsample leveling title:", leveling["title"])
    print("  class[0]:", leveling["classes"][0]["name"], leveling["classes"][0]["badge"])
    print("  stage[0]:", leveling["stages"][0]["title"], "|", leveling["stages"][0]["goal"][:80])

    print("\nsample dropcalc[0]:", dropcalc["items"][0])
    print("sample patchnotes[0].version:", patchnotes[0]["version"])
    print("sample patchnotes[0].link:", patchnotes[0]["link"])

    # rough hangul leftover ratios
    play_h = sum(hangul_ratio(it["playstyle"]) for it in builds["items"]) / n_builds
    info_h = sum(hangul_ratio(it["info"]) for it in builds["items"]) / n_builds
    print(f"\navg hangul ratio playstyle={play_h:.3f} info={info_h:.3f}")


if __name__ == "__main__":
    main()
