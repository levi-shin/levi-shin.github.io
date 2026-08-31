#!/usr/bin/env python3
"""Rewrite en/index.html guide sections (4–12) and modal chrome to English."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EN_HTML = ROOT / "en" / "index.html"

SECTIONS: dict[str, str] = {}

SECTIONS["builds"] = """
        <h2 class="section-title">🛡️ 1. Endgame Build Guides</h2>
        <div class="item-click-hint">💡 Use the filters above or click a card to open the <b>in-game paperdoll</b> endgame setup. New season? Start with <span class="item-inline" onclick="event.stopPropagation(); switchSection(null, 'leveling')">14. Leveling Guide</span>.</div>
        
        <div class="filter-tags">
            <button class="filter-btn active" onclick="filterBuilds(event, 'all')">All</button>
            <button class="filter-btn" onclick="filterBuilds(event, 'magic')">⚡ Caster / Elemental</button>
            <button class="filter-btn" onclick="filterBuilds(event, 'physical')">⚔️ Physical</button>
            <button class="filter-btn" onclick="filterBuilds(event, 'summon')">💀 Summon</button>
            <button class="filter-btn" onclick="filterBuilds(event, 'farm')">🌾 Farming / Cows</button>
            <button class="filter-btn" onclick="filterBuilds(event, 'boss')">🔥 Torch / Uber</button>
        </div>

        <div class="grid-cards" id="buildCardsGrid">
            
        </div>
"""

SECTIONS["charms"] = """
        <h2 class="section-title">🔮 4. Sunder Charm Upgrades & New Sunder Recipes</h2>
        <div class="item-click-hint">✨ Click a Sunder Charm name for <b>drop zones</b>, cube recipes, and full stats.</div>
        <table>
            <thead><tr><th>Sunder Charm (type)</th><th>Summary</th></tr></thead>
            <tbody>
                <tr class="searchable-item"><td class="unique"><span class="item-inline" onclick="openSunderModal(40001)">Flame Rift (Fire Sunder)</span></td><td>Breaks Fire Immunity + Enemy Fire Resist -7% + All Attributes +4</td></tr>
                <tr class="searchable-item"><td class="unique"><span class="item-inline" onclick="openSunderModal(40002)">Cold Rupture (Cold Sunder)</span></td><td>Breaks Cold Immunity + FHR +20% + Enemy Cold Resist -6%</td></tr>
                <tr class="searchable-item"><td class="unique"><span class="item-inline" onclick="openSunderModal(40003)">Crack of the Heavens (Lightning Sunder)</span></td><td>Breaks Lightning Immunity + FHR +24% + Enemy Lightning Resist -9%</td></tr>
                <tr class="searchable-item"><td class="unique"><span class="item-inline" onclick="openSunderModal(40004)">Rotting Fissure (Poison Sunder)</span></td><td>Breaks Poison Immunity + Enemy Poison Resist -6% + All Attributes +5</td></tr>
                <tr class="searchable-item"><td class="unique"><span class="item-inline" onclick="openSunderModal(40005)">Bone Break (Physical Sunder)</span></td><td>Breaks Physical Immunity + Enhanced Damage +87% + All Attributes +8</td></tr>
                <tr class="searchable-item"><td class="unique"><span class="item-inline" onclick="openSunderModal(40006)">Black Cleft (Magic Sunder)</span></td><td>Breaks Magic Immunity + Faster Run/Walk +7% + Enemy Magic Resist -6%</td></tr>
            </tbody>
        </table>
"""

SECTIONS["uber"] = """
        <h2 class="section-title">💀 5. Uber Events, Torch Quest & Organ Drops</h2>
        <h3 style="color: var(--gold); margin-top: 10px; margin-bottom: 10px;">🛡️ Endgame charms (Anni / Torch)</h3>
        <div class="item-click-hint">🟠 Click a charm name for stats and how to obtain it.</div>
        <table>
            <thead><tr><th>Event / Torch</th><th>Summon & steps</th><th>Key drops</th></tr></thead>
            <tbody>
                <tr class="searchable-item"><td class="highlight"><span class="item-inline" onclick="openCharmModal(50001)">Uber Diablo (Annihilus)</span></td><td>Spawns when a <b>Stone of Jordan (Jordan ring sale)</b> event triggers on the server</td><td><span class="unique">Annihilus</span> (+1 All Skills, All Attributes +20, All Res +20)</td></tr>
                <tr class="searchable-item"><td class="highlight"><span class="item-inline" onclick="openCharmModal(50002)">Torch quest (Hellfire Torch)</span></td><td><b>Terror / Hate / Destruction key set</b> cubed → <b>three organs</b> → Uber Tristram</td><td><span class="unique">Hellfire Torch</span> (+3 class skills, All Attributes +20, All Res +20)</td></tr>
            </tbody>
        </table>

        <h3 style="color: var(--gold); margin-top: 25px; margin-bottom: 10px;">⚔️ Uber Barbarian brothers — summon & jewel drops</h3>
        <div class="item-click-hint">🔥 Click a brother's name for summon steps and exclusive jewel rolls.</div>
        <table>
            <thead><tr><th>Target (Uber Tristram organs)</th><th>Affinity</th><th>Exclusive jewel / charm types</th></tr></thead>
            <tbody>
                <tr class="searchable-item"><td class="highlight"><span class="item-inline" onclick="openUberModal(60001)">Madawc</span></td><td>⚡ Lightning / ✨ Magic</td><td>Watcher's Thunder (Lightning), Guardian's Light (Magic) jewels</td></tr>
                <tr class="searchable-item"><td class="highlight"><span class="item-inline" onclick="openUberModal(60002)">Talic</span></td><td>🔥 Fire / ☠️ Poison</td><td>Guardian's Vengeance (Poison), Protector's Flame (Fire) jewels</td></tr>
                <tr class="searchable-item"><td class="highlight"><span class="item-inline" onclick="openUberModal(60003)">Korlic</span></td><td>❄️ Cold / ⚔️ Physical</td><td>Protector's Frost (Cold) jewel and exclusive physical endgame charm</td></tr>
            </tbody>
        </table>
"""

SECTIONS["cubing"] = """
        <h2 class="section-title">🧪 6. Horadric Cube, Skill Charm Rerolls & Crafting</h2>
        <table>
            <thead><tr><th>Purpose / type</th><th>Recipe (materials)</th><th>Endgame target (perfect rolls)</th></tr></thead>
            <tbody>
                <tr class="searchable-item"><td class="highlight">Socket weapon (random)</td><td>Normal weapon + <span class="rune">Ral + Amn + Perfect Amethyst</span></td><td>Random 1–max sockets depending on base</td></tr>
                <tr class="searchable-item"><td class="highlight">Socket armor (random)</td><td>Normal armor + <span class="rune">Tal + Thul + Perfect Topaz</span></td><td>Random 1–max sockets depending on base</td></tr>
                <tr class="searchable-item"><td class="highlight">Socket helm (random)</td><td>Normal helm + <span class="rune">Ral + Thul + Perfect Sapphire</span></td><td>Random 1–max sockets depending on base</td></tr>
                <tr class="searchable-item"><td class="highlight">Socket shield (random)</td><td>Normal shield + <span class="rune">Tal + Amn + Perfect Ruby</span></td><td>Random 1–max sockets depending on base</td></tr>
                <tr class="searchable-item"><td class="highlight">Reroll skill charm (life)</td><td>iLvl 91+ Grand Charm (Baal / Diablo / Nihlathak drop) + <span class="rune">3 Perfect gems</span></td><td>+1 [class skills] / <span class="highlight">+45 Life</span> (gamble / reroll GCs)</td></tr>
                <tr class="searchable-item"><td class="highlight">Reroll rare item</td><td>Rare item + <span class="rune">6 Perfect Skulls</span></td><td>Full reroll (rare circlets / amulets)</td></tr>
                <tr class="searchable-item"><td class="highlight">FCR amulet craft</td><td>Magic amulet + <span class="rune">Ral Rune + Perfect Amethyst + jewel</span></td><td><span class="highlight">+2 Skills / 20% FCR</span> / Life / Mana / All Res</td></tr>
                <tr class="searchable-item"><td class="highlight">Crushing Blow gloves craft</td><td>Magic leather gloves + <span class="rune">Nef Rune + Perfect Ruby + jewel</span></td><td><span class="highlight">+2 Skills / 20% IAS / 10% CB</span> / leech / Dex / Life</td></tr>
                <tr class="searchable-item"><td class="highlight">Remove socketed runes/jewels</td><td>Socketed item + <span class="rune">Hel Rune + Town Portal scroll</span></td><td>Keeps item; destroys socketed runes/jewels only</td></tr>
            </tbody>
        </table>
"""

SECTIONS["runelist"] = """
        <h2 class="section-title">🔢 7. Rune Numbers, Tiers & Upgrade Recipes</h2>
        <div class="item-click-hint">💡 Runes #1 El through #33 Zod. Upgrade recipes show materials to <b>craft that rune</b>.</div>
        <div class="leveling-table-wrap">
        <table>
            <thead><tr><th>#</th><th>Rune</th><th>Tier</th><th>Upgrade recipe</th><th>Used in</th></tr></thead>
            <tbody id="runeListTbody">
            </tbody>
        </table>
        </div>
"""

SECTIONS["merc"] = """
        <h2 class="section-title">🗡️ 8. Mercenary Endgame Setups</h2>
        <div class="item-click-hint">💡 Click each gear slot for perfect rolls and details.</div>
        
        <div class="grid-cards" style="grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));">
            
            <div class="card searchable-item" style="background: #141418; border: 1px solid var(--card-border); padding: 16px;">
                <h3 style="color: var(--gold); font-size: 1.05rem; margin-bottom: 4px; border-bottom: 1px solid var(--card-border); padding-bottom: 8px;">Act 2 Desert Merc (standard)</h3>
                <p style="font-size: 0.8rem; color: #a1a1aa; margin-bottom: 12px;">Aura: Might or Holy Freeze</p>
                <div style="display: grid; grid-template-columns: 1fr; gap: 8px;">
                    <div class="paperdoll-slot" onclick="openRuneModal(30008)" style="cursor:pointer;">
                        <div class="slot-title">Weapon</div>
                        <div class="slot-item rune"><span class="item-inline">Infinity</span> or <span class="item-inline" onclick="event.stopPropagation(); openRuneModal(30018)">Insight</span></div>
                    </div>
                    <div class="paperdoll-slot" onclick="openRuneModal(30020)" style="cursor:pointer;">
                        <div class="slot-title">Armor</div>
                        <div class="slot-item rune"><span class="item-inline">Eth Fortitude</span></div>
                    </div>
                    <div class="paperdoll-slot" onclick="openUniqueModal(20007)" style="cursor:pointer;">
                        <div class="slot-title">Helm</div>
                        <div class="slot-item unique"><span class="item-inline">Eth Andariel's Visage</span></div>
                    </div>
                </div>
            </div>

            <div class="card searchable-item" style="background: #141418; border: 1px solid var(--card-border); padding: 16px;">
                <h3 style="color: var(--gold); font-size: 1.05rem; margin-bottom: 4px; border-bottom: 1px solid var(--card-border); padding-bottom: 8px;">Act 1 Rogue (ranged support)</h3>
                <p style="font-size: 0.8rem; color: #a1a1aa; margin-bottom: 12px;">Aura: Fanaticism (Faith bow setup)</p>
                <div style="display: grid; grid-template-columns: 1fr; gap: 8px;">
                    <div class="paperdoll-slot" onclick="openRuneModal(30009)" style="cursor:pointer;">
                        <div class="slot-title">Weapon</div>
                        <div class="slot-item rune"><span class="item-inline">Faith</span></div>
                    </div>
                    <div class="paperdoll-slot" onclick="openRuneModal(30020)" style="cursor:pointer;">
                        <div class="slot-title">Armor</div>
                        <div class="slot-item rune"><span class="item-inline">Fortitude</span> or <span class="item-inline" onclick="event.stopPropagation(); openRuneModal(30017)">Treachery</span></div>
                    </div>
                    <div class="paperdoll-slot" onclick="openUniqueModal(20007)" style="cursor:pointer;">
                        <div class="slot-title">Helm</div>
                        <div class="slot-item unique"><span class="item-inline">Andariel's Visage</span></div>
                    </div>
                </div>
            </div>

            <div class="card searchable-item" style="background: #141418; border: 1px solid var(--card-border); padding: 16px;">
                <h3 style="color: var(--gold); font-size: 1.05rem; margin-bottom: 4px; border-bottom: 1px solid var(--card-border); padding-bottom: 8px;">Act 3 Iron Wolf / caster merc</h3>
                <p style="font-size: 0.8rem; color: #a1a1aa; margin-bottom: 12px;">Type: Fire or Lightning caster</p>
                <div style="display: grid; grid-template-columns: 1fr; gap: 8px;">
                    <div class="paperdoll-slot" onclick="openRuneModal(30007)" style="cursor:pointer;">
                        <div class="slot-title">Weapon & shield</div>
                        <div class="slot-item rune"><span class="item-inline">Spirit sword</span> + Monarch shield</div>
                    </div>
                    <div class="paperdoll-slot" onclick="openRuneModal(30020)" style="cursor:pointer;">
                        <div class="slot-title">Armor</div>
                        <div class="slot-item rune"><span class="item-inline">Fortitude</span> or <span class="item-inline" onclick="event.stopPropagation(); openRuneModal(30011)">Duress</span></div>
                    </div>
                    <div class="paperdoll-slot" onclick="openUniqueModal(20005)" style="cursor:pointer;">
                        <div class="slot-title">Helm</div>
                        <div class="slot-item unique"><span class="item-inline">Harlequin Crest (Shako)</span></div>
                    </div>
                </div>
            </div>

            <div class="card searchable-item" style="background: #141418; border: 1px solid var(--card-border); padding: 16px;">
                <h3 style="color: var(--gold); font-size: 1.05rem; margin-bottom: 4px; border-bottom: 1px solid var(--card-border); padding-bottom: 8px;">Act 5 Barb merc (melee)</h3>
                <p style="font-size: 0.8rem; color: #a1a1aa; margin-bottom: 12px;">Role: front-line tank and burst damage</p>
                <div style="display: grid; grid-template-columns: 1fr; gap: 8px;">
                    <div class="paperdoll-slot" onclick="openRuneModal(30013)" style="cursor:pointer;">
                        <div class="slot-title">Weapon</div>
                        <div class="slot-item rune">Dual <span class="item-inline">Grief</span> or Lawbringer</div>
                    </div>
                    <div class="paperdoll-slot" onclick="openRuneModal(30020)" style="cursor:pointer;">
                        <div class="slot-title">Armor</div>
                        <div class="slot-item rune"><span class="item-inline">Eth Fortitude</span></div>
                    </div>
                    <div class="paperdoll-slot" onclick="openUniqueModal(20016)" style="cursor:pointer;">
                        <div class="slot-title">Helm</div>
                        <div class="slot-item unique"><span class="item-inline">Arreat's Face</span> or <span class="item-inline" onclick="event.stopPropagation(); openUniqueModal(20033)">Guillaume's Face</span></div>
                    </div>
                </div>
            </div>

        </div>
"""

SECTIONS["frame"] = """
        <h2 class="section-title">⚡ 9. FCR / FHR / IAS Breakpoint Tables</h2>
        <table>
            <thead><tr><th>Type</th><th>Class</th><th>Target frame</th><th>Required %</th></tr></thead>
            <tbody>
                <tr class="searchable-item"><td class="highlight">FCR</td><td>Sorceress</td><td>8 frame / 7 frame</td><td>105% / <span class="highlight">200%</span></td></tr>
                <tr class="searchable-item"><td class="highlight">FCR</td><td>Paladin / Necro / Warlock</td><td>10 frame / 9 frame</td><td>75% / <span class="highlight">125%</span></td></tr>
                <tr class="searchable-item"><td class="highlight">FHR</td><td>All classes</td><td>6 frame / 5 frame</td><td>42% / <span class="highlight">86%</span> (86% comfort zone)</td></tr>
                <tr class="searchable-item"><td class="highlight">IAS</td><td>WW Barb (6-hit Whirlwind)</td><td>Weapon base speed</td><td>Phase Grief needs <span class="highlight">30%+ IAS</span></td></tr>
                <tr class="searchable-item"><td class="highlight">IAS</td><td>Javazon (Lightning Fury frames)</td><td>9 frame / 8 frame</td><td>52% / <span class="highlight">89%</span></td></tr>
            </tbody>
        </table>
"""

SECTIONS["quest"] = """
        <h2 class="section-title">📜 10. Permanent Quest Rewards by Difficulty</h2>
        <div style="margin-bottom: 15px; font-size: 0.95rem; background: var(--card-bg); padding: 12px; border-left: 3px solid var(--gold); border-radius: 4px;">
            <span class="highlight">💡 Required quest checkpoints:</span> Clear these on Normal, Nightmare, and Hell to earn permanent skill points, stats, all-resist bonuses, socket rewards, and Personalize. Each reward applies once per difficulty (up to 3 times per character).
        </div>
        <table>
            <thead><tr><th>Act / quest</th><th>Where & how</th><th>Permanent reward</th></tr></thead>
            <tbody>
                <tr class="searchable-item">
                    <td><b>Act 1 Quest 1</b><br>(Den of Evil)</td>
                    <td>Clear all monsters in the Den of Evil outside Rogue Encampment (Akara reward)</td>
                    <td><b>+1 skill point</b>, one free stat/skill reset from Akara</td>
                </tr>
                <tr class="searchable-item">
                    <td><b>Act 2 Quest 1</b><br>(Radament's Lair)</td>
                    <td>Kill Radament in Sewers Level 3 (Lut Gholein)</td>
                    <td><b>+1 skill point</b>, skill books (+1 each) and vendor discount</td>
                </tr>
                <tr class="searchable-item">
                    <td><b>Act 3 Quest 4</b><br>(Lam Esen's Tome)</td>
                    <td>Find the tome in the Ruined Temple (Kurast Bazaar area — Ormus reward)</td>
                    <td><b>+5 stat points</b> (permanent)</td>
                </tr>
                <tr class="searchable-item">
                    <td><b>Act 4 Quest 1</b><br>(The Fallen Angel)</td>
                    <td>Outer Steppes → Plains of Despair, kill <b>Izual</b> (Tyrael reward)</td>
                    <td><b>+2 skill points</b> (permanent)</td>
                </tr>
                <tr class="searchable-item">
                    <td><b>Act 5 Quest 1</b><br>(Rescue on Mount Arreat)</td>
                    <td>Free Barbarian warriors in cages around Frigid Highlands (Larzuk reward)</td>
                    <td><b>Rune & armor rewards:</b> Ral, Ort, Tal runes and crafting support</td>
                </tr>
                <tr class="searchable-item">
                    <td><b>Act 5 Quest 2</b><br>(Rite of Passage — Personalize)</td>
                    <td>Defeat the three Ancients, then Baal's minions and Baal (Larzuk reward)</td>
                    <td><b>Personalize:</b> engrave your character name on gear (+ small defense/durability buff)</td>
                </tr>
                <tr class="searchable-item">
                    <td><b>Act 5 Quest 3</b><br>(Prisoners of Ice)</td>
                    <td>Rescue <b>Anya</b> on Frozen River, then kill Nihlathak (Anya / Larzuk reward)</td>
                    <td><b>All Resist +10%</b> (Anya — stacks to +30% across difficulties) and Larzuk <b>socket reward</b></td>
                </tr>
            </tbody>
        </table>
"""

SECTIONS["bus"] = """
        <h2 class="section-title">🚌 11. Acts 1–5 Quests, Waypoints & Rush Guide</h2>
        <div style="margin-bottom: 15px; font-size: 0.95rem; background: var(--card-bg); padding: 12px; border-left: 3px solid var(--magic-blue); border-radius: 4px;">
            <span class="highlight">⏱️ Rush ETA per difficulty (Acts 1–5):</span> 
            With solid gear and a Teleport rusher, clearing one full difficulty usually takes <b>about 20–30 minutes</b> (Act 2 staff skip / Tele Sorc rusher; Act 3 organ quest is mandatory). <br>
            <span class="highlight">🚌 Level bump trick:</span> Under-level characters (20 / 40 / 60 for Ancients) can piggyback Baal quest completion via a bumper character.
        </div>
        <table>
            <thead><tr><th>Act / ETA</th><th>Required quests (must complete)</th><th>Rusher & passenger tips / waypoints</th></tr></thead>
            <tbody>
                <tr class="searchable-item">
                    <td><b>Act 1</b><br><span style="font-size: 0.75rem; color: var(--gold);">~3–5 min</span></td>
                    <td><ul><li><b>Quest 6 (Andariel):</b> Kill Andariel in Catacombs Level 4</li></ul></td>
                    <td><b>[Rusher]</b> Rush Catacombs 4, open portal before the kill.<br><b>[Passenger]</b> Take portal, talk to <b>Warriv</b> to enter Act 2.</td>
                </tr>
                <tr class="searchable-item">
                    <td><b>Act 2</b><br><span style="font-size: 0.75rem; color: var(--gold);">~5–7 min</span></td>
                    <td>
                        <ul>
                            <li><b>Quest 2 (Horadric Staff):</b> Combine cube, staff, amulet
                                <ul class="sub-list">
                                    <li>- Cube: <b>Dry Hills WP</b> → <b>Hall of the Dead Level 3</b></li>
                                    <li>- Staff: <b>Far Oasis WP</b> → <b>Maggot Lair Level 3</b></li>
                                    <li>- Amulet: <b>Lost City WP</b> → <b>Claw Viper Temple Level 2</b></li>
                                </ul>
                            </li>
                            <li><b>Quest 4 (Arcane Sanctuary):</b> <b>Arcane Sanctuary WP</b>, kill <b>Summoner</b></li>
                            <li><b>Quest 6 (Duriel):</b> Kill <b>Duriel</b> in Tal Rasha's Tomb</li>
                        </ul>
                    </td>
                    <td><b>[Tip]</b> Bring a mule with the staff or pre-make it to skip the staff quest entirely.<br><b>[Passenger]</b> After Summoner, go to Canyon; after Duriel die, portal to town and talk <b>Tyrael → Jerhyn → Meshif</b> for Act 3.</td>
                </tr>
                <tr class="searchable-item">
                    <td><b>Act 3</b><br><span style="font-size: 0.75rem; color: var(--gold);">~5 min</span></td>
                    <td>
                        <ul>
                            <li><b>Quest 3 (Khalim's Will):</b> Eye, Brain, Heart, Flail → enter Durance of Hate
                                <ul class="sub-list">
                                    <li>- Eye: <b>Spider Forest WP</b> → <b>Spider Cavern</b></li>
                                    <li>- Brain: <b>Flayer Jungle WP</b> → <b>Flayer Dungeon Level 3</b></li>
                                    <li>- Heart: <b>Kurast Bazaar WP</b> → <b>Kurast Sewers Level 1</b></li>
                                    <li>- Flail: <b>Travincal WP</b> → kill <b>High Council</b></li>
                                </ul>
                            </li>
                            <li><b>Quest 5 (Temple):</b> Kill <b>Council</b> in Travincal</li>
                            <li><b>Quest 6 (Mephisto):</b> Durance Level 3 — kill <b>Mephisto</b></li>
                        </ul>
                    </td>
                    <td><b>[Tip]</b> Act 3 requires full Khalim quest before Mephisto. Cube all four parts, then enter Durance.<br><b>[Passenger]</b> After Council kill, talk to <b>Cain</b>. After Mephisto, enter the <b>red Hell gate</b> to Act 4.</td>
                </tr>
                <tr class="searchable-item">
                    <td><b>Act 4</b><br><span style="font-size: 0.75rem; color: var(--gold);">~3 min</span></td>
                    <td><ul><li><b>Quest 3 (Terror's End):</b> Chaos Sanctuary — break 5 seals, kill <b>Diablo</b></li></ul></td>
                    <td><b>[Rusher]</b> Teleport to all five seals, kill Diablo.<br><b>[Passenger]</b> Wait in town; after Diablo, talk to <b>Tyrael</b> for Harrogath (Act 5).</td>
                </tr>
                <tr class="searchable-item">
                    <td><b>Act 5</b><br><span style="font-size: 0.75rem; color: var(--gold);">~5–8 min</span></td>
                    <td>
                        <ul>
                            <li><b>Quest 5 (Rite of Passage):</b> Summon & kill <b>three Ancients</b> on Arreat Summit (lvl req: 20 / 40 / 60)</li>
                            <li><b>Quest 6 (Eve of Destruction):</b> Worldstone Keep — kill <b>Baal</b></li>
                        </ul>
                    </td>
                    <td><b>[Rusher]</b> Clear Ancients, take WSK Level 2 waypoint to Throne, finish wave 5 + Baal.<br><b>[Passenger]</b> Enter if level OK; otherwise wait in town and use a <b>bumper</b> for Baal quest credit.</td>
                </tr>
            </tbody>
        </table>
"""

SECTIONS["farming"] = """
        <h2 class="section-title">🎯 12. TC85 Farms, Terror Zones & Herald Tiers</h2>
        <div style="margin-bottom: 15px; font-size: 0.95rem; background: var(--card-bg); padding: 12px; border-left: 3px solid var(--gold); border-radius: 4px;">
            <span class="highlight">⚠️ Hell default resist penalty:</span> All resistances start at <b>-100%</b>, so you need <b>+175% total</b> from gear to cap at 75%.<br><br>
            <span class="highlight">🌀 Terror Zones & Herald tiers:</span> 
            Every 30 minutes a random zone becomes a Terror Zone with boosted monster levels and <b>Herald</b> packs. Higher Herald tiers mean better rare drops and Sunder Charm odds.<br><br>
            • <b>Tier 1:</b> Small elite-led packs — magic/rare items and low materials.<br>
            • <b>Tier 2:</b> Champion / unique mixes — better gear and Dormant Sunder Charm rates.<br>
            • <b>Tier 3+:</b> Top-tier Heralds and regional bosses — Worldstone Shards, statue pieces, best endgame farming targets.
        </div>
        <table>
            <thead><tr><th>Act</th><th>Static TC85 zones</th><th>Terror Zone notes & Herald tiers</th></tr></thead>
            <tbody>
                <tr class="searchable-item"><td>Act 1</td><td class="highlight">The Pit (Levels 1–2), Burial Grounds / Mausoleum</td><td>Early MF spots; Pit / Catacombs TZ with Tier 1–2 Heralds and strong XP</td></tr>
                <tr class="searchable-item"><td>Act 2</td><td class="highlight">Ancient Tunnels, Tal Rasha's Tomb</td><td>Few cold-immune mobs — great for Blizzard Sorc; Tombs TZ with Tier 2–3 Heralds</td></tr>
                <tr class="searchable-item"><td>Act 3</td><td class="highlight">Kurast Sewers / temples, Travincal</td><td>Council runs for runes/jewelry; strong Tier 2 Herald hunting</td></tr>
                <tr class="searchable-item"><td>Act 4</td><td class="highlight">Chaos Sanctuary</td><td>Fixed layout, dense packs — top efficiency for farming and XP</td></tr>
                <tr class="searchable-item"><td>Act 5</td><td class="highlight">Worldstone Keep, Throne of Destruction, Baal room</td><td>Best uniques/runes and <b>Tier 3+ Heralds / regional bosses</b> — endgame destination</td></tr>
            </tbody>
        </table>
"""

SECTIONS["ladder"] = """
        <h2 class="section-title">🔥 13. D2R Patch Notes Archive</h2>
        <p style="font-size: 0.9rem; color: #a1a1aa; margin-bottom: 15px;">Browse detailed patch history. For a fresh season start, see <span class="item-inline" onclick="switchSection(null, 'leveling')">14. Leveling Guide</span>.</p>
        <div id="patch-notes-container">
        </div>
"""

SECTIONS["leveling"] = """
        <h2 class="section-title">🌱 14. Leveling Guide from Scratch</h2>
        <div class="item-click-hint">💡 Click runeword names for recipes and bases. Endgame buttons on class cards open section 1 paperdolls.</div>
        <div id="levelingRoot"></div>
"""

SECTIONS["dropcalc"] = """
        <h2 class="section-title">🎯 15. Magic Find Drop Calculator</h2>
        <div class="item-click-hint">
            Enter your Magic Find to see unique drop odds.
            Higher MF helps, but returns diminish as MF climbs.
            Each item uses its best baseline farm (per kill).
        </div>

        <form id="dropcalcForm" class="dropcalc-form" onsubmit="calculateDropOdds(event)">
            <label class="dropcalc-field">
                <span>My MF (%)</span>
                <input type="number" id="dropcalcMf" name="mf" min="0" max="2000" step="1" value="250" inputmode="numeric" required>
            </label>
            <label class="dropcalc-field dropcalc-field-grow">
                <span>Item filter</span>
                <input type="text" id="dropcalcItemFilter" name="item" placeholder="e.g. Shako, Griffon, SoJ">
            </label>
            <button type="submit" class="dropcalc-submit">Calculate</button>
        </form>

        <div class="dropcalc-presets" aria-label="MF presets">
            <span>Presets:</span>
            <button type="button" class="filter-btn" onclick="setDropCalcMf(0)">0</button>
            <button type="button" class="filter-btn" onclick="setDropCalcMf(150)">150</button>
            <button type="button" class="filter-btn" onclick="setDropCalcMf(250)">250</button>
            <button type="button" class="filter-btn" onclick="setDropCalcMf(350)">350</button>
            <button type="button" class="filter-btn" onclick="setDropCalcMf(500)">500</button>
        </div>

        <div id="dropcalcResults" class="dropcalc-results" hidden></div>
"""

SECTIONS["feedback"] = """
        <h2 class="section-title">📩 16. Feedback & Reports</h2>
        <div style="background: var(--card-bg); border: 1px solid var(--card-border); padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.4);">
            <h3 style="color: var(--gold); font-size: 1.2rem; margin-bottom: 8px;">💡 Missing or incorrect info?</h3>
            <p style="font-size: 0.9rem; color: var(--text-color); margin-bottom: 18px; word-break: keep-all;">
                Report missing unique mods, runeword recipes, or patch notes that need a fix.<br>
                Help us build a more accurate encyclopedia together!
            </p>
            <button onclick="openFeedbackModal()" style="background: linear-gradient(135deg, var(--gold) 0%, var(--gold-light) 100%); color: #0b0b0e; font-weight: bold; border: none; padding: 12px 28px; font-size: 0.95rem; border-radius: 30px; cursor: pointer; box-shadow: 0 4px 15px rgba(223, 177, 91, 0.3); transition: transform 0.2s ease;">
                ✍️ Send feedback
            </button>
        </div>
"""

MODAL_REPLACEMENTS = [
    ('id="dbModalTitle" class="item-modal-title">아이템 상세', 'id="dbModalTitle" class="item-modal-title">Item details'),
    ('aria-label="닫기"', 'aria-label="Close"'),
    ('<h4 id="dbModalSubtitle">상세 정보</h4>', '<h4 id="dbModalSubtitle">Details</h4>'),
    ('copyDatabaseValue()">📋 정보 복사', 'copyDatabaseValue()">📋 Copy info'),
    ('id="itemModalTitle" class="item-modal-title">아이템 상세', 'id="itemModalTitle" class="item-modal-title">Item details'),
    ('aria-label="수수께끼 아이템 이미지"', 'aria-label="Enigma item image"'),
    ('alt="수수께끼"', 'alt="Enigma"'),
    ('<h4 id="itemModalSubtitle">수수께끼 · Enigma</h4>', '<h4 id="itemModalSubtitle">Enigma</h4>'),
    ('<p id="itemModalIntro">3Sockets 갑옷에 자 + 아이드 + 베르 순서로 넣어 만드는 대표적인 종결 룬어입니다.</p>',
     '<p id="itemModalIntro">Classic endgame runeword: Jah + Ith + Ber in a 3-socket armor.</p>'),
    ('copyItemRecipe()">📋 룬 조합 순서 복사', 'copyItemRecipe()">📋 Copy rune order'),
    ('<div id="pdModalTitle" class="item-modal-title">직업 종결 빌드 가이드</div>',
     '<div id="pdModalTitle" class="item-modal-title">Endgame build guide</div>'),
    ('<p style="margin-bottom: 15px; color: #a1a1aa; font-size: 0.85rem;">💡 아래 인벤토리 장비 슬롯을 참고하여 종결 스펙을 세팅하세요.</p>',
     '<p style="margin-bottom: 15px; color: #a1a1aa; font-size: 0.85rem;">💡 Use the inventory slots below as an endgame gear checklist.</p>'),
    ('copyPaperDollValue();">\n                📋 빌드 내용 복사하기',
     'copyPaperDollValue();">\n                📋 Copy build'),
    ('aria-label="모바일 본문 중간 광고"', 'aria-label="Mobile in-content ad"'),
    ('aria-label="우측 광고"', 'aria-label="Right sidebar ad"'),
    ('console.log("🔍 Global search listener가 정상 부착되었습니다.");',
     'console.log("🔍 Global search listener attached.");'),
]


def replace_section(html: str, section_id: str, new_body: str) -> str:
    pattern = rf'(<section id="{re.escape(section_id)}"[^>]*>)(.*?)(</section>)'
    if not re.search(pattern, html, flags=re.DOTALL):
        raise SystemExit(f"section not found: {section_id}")
    return re.sub(
        pattern,
        lambda m: m.group(1) + new_body + m.group(3),
        html,
        count=1,
        flags=re.DOTALL,
    )


def main() -> None:
    html = EN_HTML.read_text(encoding="utf-8")
    for sid, body in SECTIONS.items():
        html = replace_section(html, sid, body)
    for old, new in MODAL_REPLACEMENTS:
        html = html.replace(old, new)
    EN_HTML.write_text(html, encoding="utf-8")
    hangul = len(re.findall(r"[가-힣]", html))
    print(f"updated {EN_HTML} — hangul chars remaining: {hangul}")


if __name__ == "__main__":
    main()
