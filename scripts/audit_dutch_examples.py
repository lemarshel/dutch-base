import json
import re
from collections import defaultdict

DATA = 'C:/Users/hp/dutch-base/data/words.json'
OUT = 'C:/Users/hp/dutch-base/data/audits/audit_examples.json'

with open(DATA, 'r', encoding='utf-8') as f:
    data = json.load(f)

issues = {
    'missing_example': [],
    'length_out_of_range': [],
    'lemma_missing': [],
    'duplicate_example': [],
}

seen = set()
for item in data:
    lemma = item['lemma']
    ex = (item.get('example') or '').strip()
    if not ex:
        issues['missing_example'].append(lemma)
        continue
    words = re.findall(r"[A-Za-zÀ-ÿ]+", ex)
    if len(words) < 6 or len(words) > 14:
        issues['length_out_of_range'].append({'lemma': lemma, 'example': ex, 'len': len(words)})
    if not re.search(rf'\b{re.escape(lemma)}\b', ex, flags=re.IGNORECASE):
        issues['lemma_missing'].append({'lemma': lemma, 'example': ex})
    key = ex.lower()
    if key in seen:
        issues['duplicate_example'].append({'lemma': lemma, 'example': ex})
    seen.add(key)

summary = {k: len(v) for k, v in issues.items()}
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump({'summary': summary, 'issues': issues}, f, ensure_ascii=False, indent=2)

print('Audit examples complete:', summary)
