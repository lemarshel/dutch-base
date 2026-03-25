# Build Notes — Dutch MVP

## How to rebuild
```bash
python scripts/build_dutch_list.py --target 4500 --candidates 20000 --no-translate
```

## Translation
The build script supports Marian MT (`Helsinki-NLP/opus-mt-nl-en`).
Run without `--no-translate` to populate `english` fields.

## Files
- `data/words.json` — app data
- `data/words_full.csv` — full export with metadata
- `data/translation_cache.json` — translation cache (optional)
