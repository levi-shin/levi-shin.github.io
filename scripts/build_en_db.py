#!/usr/bin/env python3
"""Build data/en/{uniques,runewords,runes,sunders,charms,ubers}.json from Korean sources."""
from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

RW = json.loads((DATA / "runewords.json").read_text(encoding="utf-8"))
UNI = json.loads((DATA / "uniques.json").read_text(encoding="utf-8"))
RUNES = json.loads((DATA / "runes.json").read_text(encoding="utf-8"))
SUNDERS = json.loads((DATA / "sunders.json").read_text(encoding="utf-8"))
CHARMS = json.loads((DATA / "charms.json").read_text(encoding="utf-8"))
UBERS = json.loads((DATA / "ubers.json").read_text(encoding="utf-8"))

SUNDER_NAMES = {
    40001: "Flame Rift (Fire)",
    40002: "Cold Rupture (Cold)",
    40003: "Crack of the Heavens (Lightning)",
    40004: "Rotting Fissure (Poison)",
    40005: "Bone Break (Physical)",
    40006: "Black Cleft (Magic)",
}

CHARM_NAMES = {
    50001: "Annihilus",
    50002: "Hellfire Torch",
}

CHARM_DROP = {
    50001: "Uber Diablo (Diablo Clone) — 100% drop on kill",
    50002: "Uber Tristram Torch quest (defeat Mephisto, Diablo, and Baal)",
}

CHARM_STATS = {
    50001: 'Fixed rolls: <strong>+1 All Skills</strong> / <strong>All Attributes +20</strong> (perfect) / <strong>All Resistances +20</strong> (perfect) / <strong>+10% Experience Gained</strong>',
    50002: 'Fixed rolls: <strong>+3 [Character Class Skills]</strong> / <strong>All Attributes +20</strong> (perfect) / <strong>All Resistances +20</strong> (perfect) / Level 8 <strong>Firestorm</strong> 5% chance on striking',
}

UBER_NAMES = {
    60001: "Madawc (Lightning / Magic)",
    60002: "Talic (Fire / Poison)",
    60003: "Korlic (Cold / Physical)",
}

UBER_SUMMON = "Cube five Barbarian statue pieces → obtain the Key to the Pinnacle of Passage → open the portal"

UBER_STATS = {
    60001: "<strong>Watcher's Thunder (Lightning):</strong> +5~10% Lightning Skills, -5~10% Enemy Lightning Resist, 1% chance to cast Level 25 Cyclone Armor when struck, 15~35% Magic Find, 25~50% Extra Gold, +3~5% Experience<br><br><strong>Guardian's Light (Magic):</strong> +5~10% Magic Skills, -5~10% Enemy Magic Resist, 15~35% Magic Find, 25~50% Extra Gold, +3~5% Experience",
    60002: "<strong>Guardian's Vengeance (Poison):</strong> +5~10% Poison Skills, -5~10% Enemy Poison Resist, 1% chance to cast Level 25 Bone Armor when struck, 15~35% Magic Find, 25~50% Extra Gold, +3~5% Experience<br><br><strong>Protector's Flame (Fire):</strong> +5~10% Fire Skills, -5~10% Enemy Fire Resist, 15~35% Magic Find, 25~50% Extra Gold, +3~5% Experience",
    60003: "<strong>Protector's Frost (Cold):</strong> +5~10% Cold Skills, -5~10% Enemy Cold Resist, 1% chance to cast Level 25 Frozen Armor when struck, 15~35% Magic Find, 25~50% Extra Gold, +3~5% Experience<br><br><strong>Physical charm:</strong> exclusive endgame charm with enhanced physical damage plus Crushing Blow / Deadly Strike",
}

SUNDER_STATS = {
    40001: "Breaks Fire Immunity + Enemy Fire Resist -7% + All Attributes +4 + Mana +66 + Fire Resist -72% + Magic Damage Reduced by 6 + Gold Find +22%",
    40002: "Breaks Cold Immunity + Faster Hit Recovery +20% + Enemy Cold Resist -6% + Mana +74 + Cold Resist -84% + Damage Reduced by 5 + Magic Find +19%",
    40003: "Breaks Lightning Immunity + Faster Hit Recovery +24% + Enemy Lightning Resist -9% + Mana +72 + Lightning Resist -70% + Damage Reduced by 5 + Gold Find +51%",
    40004: "Breaks Poison Immunity + Enemy Poison Resist -6% + All Attributes +5 + Mana +45 + Poison Resist -77% + Magic Damage Reduced by 7 + Gold Find +34%",
    40005: "Breaks Physical Immunity + Enhanced Damage +87% + All Attributes +8 + Life +17 + Damage Reduced by 6 + Physical Damage Taken +20% + Gold Find +25%",
    40006: "Breaks Magic Immunity + Faster Run/Walk +7% + Enemy Magic Resist -6% + Mana +58 + Magic Resist -55% + Damage Reduced by 9 + Magic Find +19%",
}

SUNDER_DROP = "Hell Terror Zone act bosses and champions"

SUNDER_EXTRA = [
    ("잠복하는 화파참", "Dormant Fire Sunder Charm"),
    ("잠복하는 콜파참", "Dormant Cold Sunder Charm"),
    ("잠복하는 번파참", "Dormant Lightning Sunder Charm"),
    ("잠복하는 독파참", "Dormant Poison Sunder Charm"),
    ("잠복하는 물파참", "Dormant Physical Sunder Charm"),
    ("잠복하는 마파참", "Dormant Magic Sunder Charm"),
    ("깊은 세계석 조각", "Deep Worldstone Shard"),
    ("동부 세계석 조각", "Eastern Worldstone Shard"),
    ("남부 세계석 조각", "Southern Worldstone Shard"),
    ("서부 세계석 조각", "Western Worldstone Shard"),
    ("북부 세계석 조각", "Northern Worldstone Shard"),
    ("세계석 조각 3종", "three Worldstone Shard types"),
    ("최상급 루비", "Perfect Ruby"),
    ("최상급 사파이어", "Perfect Sapphire"),
    ("최상급 토파즈", "Perfect Topaz"),
    ("최상급 에메랄드", "Perfect Emerald"),
    ("최상급 자수정", "Perfect Amethyst"),
    ("최상급 다이아몬드", "Perfect Diamond"),
    ("괴물의 화염 면역 파괴", "Breaks Fire Immunity"),
    ("괴물의 냉기 면역 파괴", "Breaks Cold Immunity"),
    ("괴물의 번개 면역 파괴", "Breaks Lightning Immunity"),
    ("괴물의 독 면역 파괴", "Breaks Poison Immunity"),
    ("괴물의 물리 면역 파괴", "Breaks Physical Immunity"),
    ("괴물의 마법 면역 파괴", "Breaks Magic Immunity"),
    ("적의 화염 저항", "Enemy Fire Resist"),
    ("적의 냉기 저항", "Enemy Cold Resist"),
    ("적의 번개 저항", "Enemy Lightning Resist"),
    ("적의 독 저항", "Enemy Poison Resist"),
    ("적 마법 저항", "Enemy Magic Resist"),
    ("모든 능력치", "All Attributes"),
    ("금화", "Gold Find"),
    ("받는 물리 피해", "Physical Damage Taken"),
    ("이속", "Faster Run/Walk"),
    ("타격 회복 속도", "Faster Hit Recovery"),
    ("피해 ", "Damage "),
    ("증가", "Increased"),
    ("감소", "Reduced"),
]

CHARM_EXTRA = [
    ("섬멸의 부적", "Annihilus"),
    ("애니참", "Anni"),
    ("지옥의 횃불", "Hellfire Torch"),
    ("횃불참", "Torch"),
    ("고정 스펙", "Fixed rolls"),
    ("모든 스탯", "All Attributes"),
    ("모든 저항", "All Resistances"),
    ("경험치 획득", "Experience Gained"),
    ("캐릭터 직업 스킬", "Character Class Skills"),
    ("화염 폭풍", "Firestorm"),
    ("타격 시", "On striking"),
    ("확률 발동", "chance to cast"),
    ("우버 디아블로", "Uber Diablo"),
    ("디아블로 클론", "Diablo Clone"),
    ("처치 시 100% 드랍", "100% drop on kill"),
    ("트리스트럼 횃불 퀘스트", "Uber Tristram Torch quest"),
    ("메피스토", "Mephisto"),
    ("디아블로", "Diablo"),
    ("바알", "Baal"),
]

UBER_EXTRA = [
    ("5종류의 바바 동상 큐빙", "Cube five Barbarian statue pieces"),
    ("위압적인 정상의 열쇠", "Key to the Pinnacle of Passage"),
    ("획득 후 포탈 오픈", "then open the portal"),
    ("감시자의 천둥", "Watcher's Thunder"),
    ("수호자의 빛", "Guardian's Light"),
    ("수호자의 역정", "Guardian's Vengeance"),
    ("보호자의 불꽃", "Protector's Flame"),
    ("보호자의 서리", "Protector's Frost"),
    ("물리형 부적", "Physical charm"),
    ("번개 스킬", "Lightning Skills"),
    ("매직 스킬", "Magic Skills"),
    ("독 스킬", "Poison Skills"),
    ("화염 스킬", "Fire Skills"),
    ("냉기 스킬", "Cold Skills"),
    ("적 번개 저항", "Enemy Lightning Resist"),
    ("적 매직 저항", "Enemy Magic Resist"),
    ("적 독 저항", "Enemy Poison Resist"),
    ("적 화염 저항", "Enemy Fire Resist"),
    ("적 냉기 저항", "Enemy Cold Resist"),
    ("피격 시", "When Struck"),
    ("사이클론 아머", "Cyclone Armor"),
    ("본아머", "Bone Armor"),
    ("프로즌 아머", "Frozen Armor"),
    ("골찬", "Extra Gold"),
    ("경험치", "Experience"),
    ("물리 피해 증대", "Enhanced Physical Damage"),
    ("강타/치명타", "Crushing Blow / Deadly Strike"),
    ("전용 종결 부적", "exclusive endgame charm"),
]

ko_to_eng_rw: dict[str, str] = {}
for r in RW:
    ko_to_eng_rw[r["name"]] = r["eng"]
    for a in r.get("aliases") or []:
        if re.search(r"[가-힣]", a):
            ko_to_eng_rw[a] = r["eng"]

ko_to_eng_rune = {r["name"]: r["eng"] for r in RUNES}

GLOSSARY = [
    ("라이프 흡수", "Life Steal"),
    ("마나 훔침", "Mana Steal"),
    ("마나 재생", "Replenish Mana"),
    ("마법 피해 감소", "Magic Damage Reduced"),
    ("물리 피해 감소", "Physical Damage Reduced"),
    ("피해 감소", "Damage Reduced"),
    ("모든 저항", "All Resistances"),
    ("모든 스킬", "All Skills"),
    ("모든 스탯", "All Attributes"),
    ("시전 속도", "Faster Cast Rate"),
    ("타격 회복", "Faster Hit Recovery"),
    ("공격 속도", "Increased Attack Speed"),
    ("달리기·걷기", "Faster Run/Walk"),
    ("달리기/걷기", "Faster Run/Walk"),
    ("명중률", "Attack Rating"),
    ("방어력 상승", "Enhanced Defense"),
    ("방어력", "Defense"),
    ("피해 상승", "Enhanced Damage"),
    ("추가 피해", "Damage"),
    ("최대 마나", "Max Mana"),
    ("최대 스태미나", "Max Stamina"),
    ("최대 피해", "Maximum Damage"),
    ("빛 반경", "Light Radius"),
    ("처치 시 마나", "Mana after each Kill"),
    ("처치 시 생명력", "Life after each Kill"),
    ("개방 상처", "Open Wounds"),
    ("강타", "Crushing Blow"),
    ("치명타", "Deadly Strike"),
    ("적중 시 밀어냄", "Knockback"),
    ("빙결되지 않음", "Cannot Be Frozen"),
    ("파괴 불가", "Indestructible"),
    ("요구치", "Requirements"),
    ("죽은 몬스터 되살아나지 않음", "Slain Monsters Rest in Peace"),
    ("악마에게 주는 피해", "Damage to Demons"),
    ("언데드에게 주는 피해", "Damage to Undead"),
    ("적 번개 저항", "Enemy Lightning Resist"),
    ("적 화염 저항", "Enemy Fire Resist"),
    ("적 냉기 저항", "Enemy Cold Resist"),
    ("적 독 저항", "Enemy Poison Resist"),
    ("번개 기술 피해", "Lightning Skill Damage"),
    ("화염 기술 피해", "Fire Skill Damage"),
    ("냉기 기술 피해", "Cold Skill Damage"),
    ("독 기술 피해", "Poison Skill Damage"),
    ("번개 저항", "Lightning Resist"),
    ("화염 저항", "Fire Resist"),
    ("냉기 저항", "Cold Resist"),
    ("독 저항", "Poison Resist"),
    ("독 피해", "Poison Damage"),
    ("번개 피해", "Lightning Damage"),
    ("화염 피해", "Fire Damage"),
    ("냉기 피해", "Cold Damage"),
    ("마법 흡수", "Magic Absorb"),
    ("원거리 방어", "Defense vs Missile"),
    ("피격 시 반사 피해", "Attacker Takes Damage"),
    ("피격 시", "When Struck"),
    ("레벨당 생명력·마나", "Life and Mana per Level"),
    ("레벨당 생명력", "Life per Level"),
    ("레벨당 마나", "Mana per Level"),
    ("캐릭터 레벨 비례", "based on Character Level"),
    ("캐릭터 레벨", "Character Level"),
    ("전투 명령", "Battle Command"),
    ("전투 지시(BO)", "Battle Orders"),
    ("전투 지시", "Battle Orders"),
    ("전투의 외침", "Battle Cry"),
    ("아마존 스킬", "Amazon Skills"),
    ("투창·창 스킬", "Javelin and Spear Skills"),
    ("화염 스킬", "Fire Skills"),
    ("온기", "Warmth"),
    ("복구 속도 증가", "Replenish Quantity"),
    ("회복 속도", "Replenish Life"),
    ("상점 가격", "Vendor Prices"),
    ("매찬", "Magic Find"),
    ("삥", "Gold Find"),
    ("으뜸", "perfect"),
    ("고정 으뜸", "fixed perfect"),
    ("생명력", "Life"),
    ("활력", "Vitality"),
    ("민첩", "Dexterity"),
    ("덱스", "Dexterity"),
    ("에너지", "Energy"),
    ("마나", "Mana"),
    ("힘·활력", "Strength and Vitality"),
    ("힘·민첩", "Strength and Dexterity"),
    ("힘 ", "Strength "),
    ("힘+", "Strength +"),
    (" / 힘", " / Strength"),
    ("힘", "Strength"),
    ("창", "Spear"),
    ("검", "Sword"),
    ("약화 충전", "charges of Weaken"),
    ("독노바 충전", "charges of Poison Nova"),
    ("레벨 3 ", "Level 3 "),
    ("피해 10% 마나로 전환", "Damage Taken Goes To Mana 10%"),
    ("독·냉·번 저항", "Poison/Cold/Lightning Resist"),
    ("화염·번개·독 저항", "Fire/Lightning/Poison Resist"),
    ("피해 ", "Damage "),
    (" / 피해", " / Damage"),
    ("피해", "Damage"),
    ("추가 ", "extra "),
    ("감속", "Slow"),
    ("블럭확률증가", "Increased Chance of Blocking"),
    ("블럭 확률", "Chance of Blocking"),
    ("야만용사", "Barbarian"),
    ("보스 및", "bosses and"),
    ("보스및", "bosses and"),
    ("보스", "bosses"),
    ("에테 ", "eth "),
    ("아마존", "Amazon"),
    ("활/석궁", "Bow/Crossbow"),
    ("그랜드 매트론 보우", "Grand Matron Bow"),
    ("히드라 보우", "Hydra Bow"),
    ("그레이트 보우", "Great Bow"),
    ("광신(Fanaticism)", "Fanaticism"),
    ("광신", "Fanaticism"),
    ("보너스", "bonus"),
    ("회복", "Replenish"),
    ("투구", "Helm"),
    ("예:", "e.g."),
    ("회 ", " charges "),
    ("강령술사", "Necromancer"),
    ("암살자", "Assassin"),
    ("혼돈 Skills", "Chaos Skills"),
    ("독·뼈 Skills", "Poison & Bone Skills"),
    ("저주", "Curses"),
    ("그림자 단련 Skills", "Shadow Disciplines Skills"),
    ("Chance of Blocking 증가", "Increased Chance of Blocking"),
    ("Mana 획득(마상)", "Damage Taken Goes To Mana"),
    ("최대 Fire Resist", "Maximum Fire Resist"),
    ("최대 Cold Resist", "Maximum Cold Resist"),
    ("최대 Lightning Resist", "Maximum Lightning Resist"),
    ("최대 Poison Resist", "Maximum Poison Resist"),
    ("적 마법 저항", "Enemy Magic Resist"),
    ("적의 매직 저항", "Enemy Magic Resist"),
    ("대상 Slow", "Slows Target"),
    ("냉기 흡수", "Cold Absorb"),
    ("화염 흡수", "Fire Absorb"),
    ("번개 흡수", "Lightning Absorb"),
    ("빙결 시간 반감", "Half Freeze Duration"),
    ("스태미나", "Stamina"),
    ("Life 추출", "Life Drain"),
    ("화염파도", "Fire Wave"),
    ("신캐 Skills", "new-class Skills"),
    ("Level당", "per Level"),
    ("1Level", "Level 1"),
    ("15Level", "Level 15"),
    ("10Level", "Level 10"),
    ("25Level", "Level 25"),
    ("8Level", "Level 8"),
    ("5Level", "Level 5"),
    ("부여", "grants"),
    ("확률", "chance"),
    ("발동", "proc"),
    ("증가", "Increased"),
    ("감소", "Reduced"),
    ("흡수", "Absorb"),
    ("저항", "Resist"),
    ("면역", "Immunity"),
    ("파괴", "breaks"),
]

DROP_GLOSSARY = [
    ("지옥(헬)", "Hell"),
    ("악몽(나이트)", "Nightmare"),
    ("일반(노말)", "Normal"),
    ("일반(Normal)", "Normal"),
    ("카오스 샌크츄어리", "Chaos Sanctuary"),
    ("고대 하수도", "Ancient Tunnels"),
    ("고대하수도", "Ancient Tunnels"),
    ("공포의 영역", "Terror Zones"),
    ("안다리엘", "Andariel"),
    ("메피스토", "Mephisto"),
    ("디아블로", "Diablo"),
    ("바알", "Baal"),
    ("트라빈칼", "Travincal"),
    ("국민 앵벌", "popular farm"),
    ("최고 확률", "best odds"),
    ("극악의 드랍률", "extremely rare"),
    ("에테 으뜸", "eth perfect"),
    ("헬 안다/메피", "Hell Andariel / Mephisto"),
    ("전 지역", "all areas"),
    ("카오스", "Chaos"),
    ("피트", "Pit"),
    ("노말", "Normal"),
    ("사냥터", "farming spots"),
    ("에테", "ethereal"),
    ("안다", "Andariel"),
    ("메피", "Mephisto"),
    (" 등 ", " etc. "),
]

BASE_EXTRA = [
    ("2소켓", "2-socket"),
    ("3소켓", "3-socket"),
    ("4소켓", "4-socket"),
    ("5소켓", "5-socket"),
    ("6소켓", "6-socket"),
    ("크리스탈 소드", "Crystal Sword"),
    ("자이언트 쓰레셔", "Giant Thresher"),
    ("크립틱 액스", "Cryptic Axe"),
    ("콜로서스 불즈", "Colossus Voulge"),
    ("플레일", "Flail"),
    ("메이지 플레이트", "Mage Plate"),
    ("브레스트 플레이트", "Breast Plate"),
    ("더스크 슈라우드", "Dusk Shroud"),
    ("숏 스태프", "Short Staff"),
    ("세크리드 타지", "Sacred Targe"),
    ("라지 실드", "Large Shield"),
    ("서클릿", "Circlet"),
    ("다이어뎀", "Diadem"),
    ("마스크", "Mask"),
    ("모나크", "Monarch"),
    ("폴암", "Polearm"),
    ("쓰레셔", "Thresher"),
    ("올레지", "all-res"),
    ("패캐", "FCR"),
    ("스태프모드", "staffmods"),
    ("파이어볼", "Fireball"),
    ("화염 계열", "Fire tree"),
    ("레벨링", "Leveling"),
    ("종결", "Endgame"),
    ("초반", "early"),
    ("용병", "Mercenary"),
    ("공용", "general"),
    ("성기사", "Paladin"),
    ("원소술사", "Sorceress"),
    ("방패", "Shield"),
    ("무난", "solid"),
    ("가성비", "budget"),
    ("방어:", "Defense:"),
    ("+스킬", "+Skills"),
    ("스킬", "Skills"),
    ("전투 스킬", "Combat Skills"),
    ("선고(Conviction)", "Conviction"),
    ("선고", "Conviction"),
    ("오라", "Aura"),
    ("레벨", "Level"),
]


def apply_glossary(text: str, glossary: list[tuple[str, str]]) -> str:
    out = str(text)
    for ko, en in sorted(glossary, key=lambda x: len(x[0]), reverse=True):
        out = out.replace(ko, en)
    return out


STATS_EXTRA = [
    ("타운 포탈(Town Portal)", "Town Portal"),
    ("Skills grants", "Skills"),
    ("타격 시", "On striking"),
    ("When Struck 번개 반사", "Lightning bolt on striking"),
    ("When Struck", "When Struck"),
    ("번개 반사", "Lightning bolt"),
    ("타격 시 5% chance로", "5% chance on striking to cast"),
    ("죽은 몬스터가 되살아나지 않음", "Slain Monsters Rest in Peace"),
    ("몬스터 Replenish 방지", "Prevent Monster Heal"),
    ("charges of Weaken 18회", "18 charges of Weaken"),
    ("회", " charges"),
    ("신성한 충격(Holy Shock)", "Holy Shock"),
    ("신성한 충격", "Holy Shock"),
    ("악마·언데드 Damage Increased", "Damage to Demons and Undead Increased"),
    ("속죄(Redemption)", "Redemption"),
    ("속죄", "Redemption"),
    ("Enhanced Defense 가변", "variable Enhanced Defense"),
    ("가변", "variable"),
    ("처치 시 화염 폭풍", "Firestorm on kill"),
    ("대상 방어 무시", "Ignore Target's Defense"),
    ("방어(Defiance)", "Defiance"),
    ("적 Life after each Kill", "Enemy Life after each Kill"),
    ("적의 Fire Resist", "Enemy Fire Resist"),
    ("적의 Cold Resist", "Enemy Cold Resist"),
    ("적의 Lightning Resist", "Enemy Lightning Resist"),
    ("적의 Poison Resist", "Enemy Poison Resist"),
    ("new-class Skills", "new-class skills"),
    (" chance proc", " chance to proc"),
    (" chance로", " chance to"),
    ("aura", "Aura"),
    ("Skills 부여", "Skills"),
    ("부여", "grants"),
    ("반사", "reflect"),
    ("폭풍", "storm"),
    ("방어", "Defense"),
    ("악마·언데드", "Demons and Undead"),
    ("악마", "Demons"),
    ("언데드", "Undead"),
]

def _merged_glossary() -> list[tuple[str, str]]:
    merged = GLOSSARY + STATS_EXTRA + BASE_EXTRA
    try:
        import sys

        scripts = Path(__file__).resolve().parent
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from build_en_content import GLOSSARY as CONTENT_GLOSSARY  # noqa: WPS433

        merged = GLOSSARY + STATS_EXTRA + CONTENT_GLOSSARY + BASE_EXTRA
    except Exception:
        pass
    return merged


def translate_stats(text: str) -> str:
    glossary = _merged_glossary()
    out = str(text)
    for _ in range(3):
        out = apply_glossary(out, glossary)
    return out


def translate_drop(text: str) -> str:
    return apply_glossary(text, DROP_GLOSSARY + GLOSSARY)


def translate_base(text: str) -> str:
    m = re.fullmatch(r".+?\(([A-Za-z0-9 '\-/]+)\)\s*", str(text))
    if m:
        return m.group(1).strip()
    return apply_glossary(text, BASE_EXTRA + GLOSSARY)


def recipe_en(recipe: str) -> str:
    parts = []
    for token in re.split(r"\s*\+\s*", recipe):
        m = re.search(r"\(([A-Za-z]+)\)", token)
        parts.append(m.group(1) if m else token.strip())
    return " + ".join(parts)


def map_runeword_token(name: str) -> str:
    name = name.strip()
    if not name:
        return name
    if name in ko_to_eng_rw:
        return ko_to_eng_rw[name]
    extras = {
        "소켓 룬 제거": "socketed rune removal",
        "올저항 소켓": "all-res jewel socket",
        "베르 합성": "Ber crafting",
        "파괴 불가": "Indestructible",
    }
    if name in extras:
        return extras[name]
    for ko, en in sorted(ko_to_eng_rw.items(), key=lambda x: -len(x[0])):
        if ko in name:
            return name.replace(ko, en)
    return name


def translate_use(use: str) -> str:
    parts = []
    for chunk in re.split(r",\s*", use):
        if "·" in chunk:
            parts.append("/".join(map_runeword_token(x) for x in chunk.split("·")))
        else:
            parts.append(map_runeword_token(chunk))
    return ", ".join(parts)


def translate_upgrade(up: str) -> str:
    if "하위 재료 없음" in up:
        return "Starter rune (no upgrade recipe)"
    out = up
    for kr in sorted(RUNES, key=lambda x: -len(x["name"])):
        out = out.replace(f"{kr['name']} 룬", f"{kr['eng']} Rune")
    out = out.replace("개", "")
    out = apply_glossary(
        out,
        [
            ("최하급 토파즈", "Chipped Topaz"),
            ("최하급 자수정", "Chipped Amethyst"),
            ("최하급 사파이어", "Chipped Sapphire"),
            ("최하급 루비", "Chipped Ruby"),
            ("최하급 에메랄드", "Chipped Emerald"),
            ("최하급 다이아몬드", "Chipped Diamond"),
            ("하급 토파즈", "Flawed Topaz"),
            ("하급 자수정", "Flawed Amethyst"),
            ("하급 사파이어", "Flawed Sapphire"),
            ("하급 루비", "Flawed Ruby"),
            ("하급 에메랄드", "Flawed Emerald"),
            ("하급 다이아몬드", "Flawed Diamond"),
            ("상급 토파즈", "Flawless Topaz"),
            ("상급 자수정", "Flawless Amethyst"),
            ("상급 사파이어", "Flawless Sapphire"),
            ("상급 루비", "Flawless Ruby"),
            ("상급 에메랄드", "Flawless Emerald"),
            ("토파즈", "Topaz"),
            ("자수정", "Amethyst"),
            ("사파이어", "Sapphire"),
            ("루비", "Ruby"),
            ("에메랄드", "Emerald"),
            ("다이아몬드", "Diamond"),
        ],
    )
    out = re.sub(r"([A-Za-z]+) Rune\s+(\d+)", r"\2 \1 Rune", out)
    return out


def build_uniques():
    out = []
    for u in UNI:
        item = deepcopy(u)
        item["name"] = u.get("eng") or u["name"]
        item["base"] = translate_base(u.get("base", ""))
        item["drop"] = translate_drop(u.get("drop", ""))
        item["stats"] = translate_stats(u.get("stats", ""))
        out.append(item)
    return out


def build_runewords():
    out = []
    for r in RW:
        item = deepcopy(r)
        item["name"] = r.get("eng") or r["name"]
        item["recipe"] = recipe_en(r.get("recipe", ""))
        item["base"] = translate_base(r.get("base", ""))
        item["base"] = apply_glossary(item["base"], BASE_EXTRA + GLOSSARY)
        item["stats"] = translate_stats(r.get("stats", ""))
        out.append(item)
    return out


def translate_sunder_recipe(recipe: str) -> str:
    out = recipe

    def repl_rune(m: re.Match) -> str:
        return f"{m.group(3)} Rune (#{m.group(1)})"

    out = re.sub(r"(\d+)번\s+([가-힣]+)\(([A-Za-z]+)\)", repl_rune, out)
    for kr in sorted(RUNES, key=lambda x: -len(x["name"])):
        eng = kr["eng"]
        num = kr.get("num", "")
        out = out.replace(f"{num}번 {kr['name']}", f"{eng} Rune (#{num})")
        out = out.replace(f"{kr['name']}({eng})", f"{eng} Rune")
    out = apply_glossary(out, SUNDER_EXTRA + GLOSSARY + BASE_EXTRA)
    return out


def build_sunders():
    out = []
    for s in SUNDERS:
        item = deepcopy(s)
        item["name"] = SUNDER_NAMES.get(s["id"], s["name"])
        item["drop"] = SUNDER_DROP
        item["recipe"] = translate_sunder_recipe(s.get("recipe", ""))
        item["stats"] = SUNDER_STATS.get(s["id"], translate_stats(s.get("stats", "")))
        out.append(item)
    return out


def build_charms():
    out = []
    for c in CHARMS:
        item = deepcopy(c)
        item["name"] = CHARM_NAMES.get(c["id"], c["name"])
        item["drop"] = CHARM_DROP.get(c["id"], apply_glossary(c.get("drop", ""), CHARM_EXTRA + GLOSSARY))
        item["stats"] = CHARM_STATS.get(c["id"], apply_glossary(c.get("stats", ""), CHARM_EXTRA + GLOSSARY))
        out.append(item)
    return out


def build_ubers():
    out = []
    for u in UBERS:
        item = deepcopy(u)
        item["name"] = UBER_NAMES.get(u["id"], u["name"])
        item["summon"] = UBER_SUMMON
        item["stats"] = UBER_STATS.get(u["id"], apply_glossary(u.get("stats", ""), UBER_EXTRA + GLOSSARY))
        out.append(item)
    return out


def build_runes():
    out = []
    for r in RUNES:
        item = deepcopy(r)
        item["name"] = r["eng"]
        item["upgrade"] = translate_upgrade(r["upgrade"])
        item["use"] = translate_use(r["use"])
        out.append(item)
    return out


def hangul_ratio(s: str) -> float:
    return len(re.findall(r"[가-힣]", s)) / max(1, len(s))


def main() -> None:
    en_dir = DATA / "en"
    en_dir.mkdir(parents=True, exist_ok=True)
    uniques = build_uniques()
    runewords = build_runewords()
    runes = build_runes()
    sunders = build_sunders()
    charms = build_charms()
    ubers = build_ubers()
    (en_dir / "uniques.json").write_text(
        json.dumps(uniques, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (en_dir / "runewords.json").write_text(
        json.dumps(runewords, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (en_dir / "runes.json").write_text(
        json.dumps(runes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (en_dir / "sunders.json").write_text(
        json.dumps(sunders, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (en_dir / "charms.json").write_text(
        json.dumps(charms, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (en_dir / "ubers.json").write_text(
        json.dumps(ubers, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"wrote {len(uniques)} uniques, {len(runewords)} runewords, {len(runes)} runes, "
        f"{len(sunders)} sunders, {len(charms)} charms, {len(ubers)} ubers"
    )
    print("unique[0]:", uniques[0]["name"], "|", uniques[0]["drop"][:70])
    print("rw[0]:", runewords[0]["name"], runewords[0]["recipe"])
    print("rune[2]:", runes[2])
    print(
        "hangul leftover avg — uniques:",
        round(sum(hangul_ratio(u["stats"]) for u in uniques) / len(uniques), 3),
        "rw:",
        round(sum(hangul_ratio(u["stats"]) for u in runewords) / len(runewords), 3),
        "runes use:",
        round(sum(hangul_ratio(u["use"]) for u in runes) / len(runes), 3),
    )


if __name__ == "__main__":
    main()
