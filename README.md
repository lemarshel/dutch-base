# Dutch Base (MVP)

A lemma-based Dutch 4,500-core-word list with a lightweight UI.

## Quick start
Open `index.html` in a browser. The app loads `data/words.json` and provides:
- Search by Dutch / English
- POS filters
- Level filters

## Build
```bash
python scripts/build_dutch_list.py --target 4500 --candidates 20000 --no-translate
```

## Docs
- `docs/resource_audit.md`
- `docs/methodology.md`
- `docs/build_notes.md`
