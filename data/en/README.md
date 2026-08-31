# English locale sync notes

## Layout
- KO (default): `/data/*.json`
- EN: `/data/en/*.json` for localized files
- Images: shared under `/items/` (KO screenshots OK for now)

## Localized files
- uniques.json, runewords.json, runes.json
- builds.json, leveling.json, dropcalc.json, patchnotes.json

## Regenerate
```bash
python3 scripts/build_en_db.py        # uniques / runewords / runes
python3 scripts/build_en_content.py   # builds / leveling / dropcalc / patchnotes
```

## Workflow
1. Update KO JSON first
2. Re-run generators (or hand-edit `data/en/`)
3. Bump `dataVer` / `?v=` cache query in `js/main.js` + `index.html` / `en/index.html`
4. Add a `meta.json` history line

## Not fully automated
- Long HTML guide tables in `en/index.html` (sections 4–12) — glossary-assisted; polish manually when needed
- Sunders / charms / ubers still share KO JSON (Phase 2+ DB only covered core item DBs)
