import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--words', default='data/words.json')
parser.add_argument('--cache', default='data/translation_cache.json')
parser.add_argument('--out', default='data/words.json')
args = parser.parse_args()

with open(args.words, 'r', encoding='utf-8') as f:
    data = json.load(f)

with open(args.cache, 'r', encoding='utf-8') as f:
    cache = json.load(f)

updated = 0
for item in data:
    lemma = item.get('lemma')
    if lemma in cache and cache[lemma]:
        if item.get('english') != cache[lemma]:
            item['english'] = cache[lemma]
            updated += 1

with open(args.out, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Applied cache entries: {updated}')
