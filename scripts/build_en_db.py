#!/usr/bin/env python3
"""Build data/en/{uniques,runewords,runes}.json from Korean sources."""
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


def translate_stats(text: str) -> str:
    return apply_glossary(text, GLOSSARY + BASE_EXTRA)


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
    (en_dir / "uniques.json").write_text(
        json.dumps(uniques, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (en_dir / "runewords.json").write_text(
        json.dumps(runewords, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (en_dir / "runes.json").write_text(
        json.dumps(runes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {len(uniques)} uniques, {len(runewords)} runewords, {len(runes)} runes")
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
