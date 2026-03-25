import json
import os
from wordfreq import zipf_frequency

DATA_PATH = 'C:/Users/hp/dutch-base/data/words.json'
OUT_DIR = 'C:/Users/hp/dutch-base/data/audits'

os.makedirs(OUT_DIR, exist_ok=True)

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

issues = {
    'missing_english': [],
    'too_many_words': [],
    'low_zipf': [],
    'non_alpha': [],
    'duplicate_lemma': [],
    'punctuation': [],
}

seen = set()
level_counts = {}
pos_counts = {}
for item in data:
    lemma = item['lemma']
    if lemma in seen:
        issues['duplicate_lemma'].append(lemma)
    seen.add(lemma)

    if not lemma.isalpha():
        issues['non_alpha'].append(lemma)

    eng = item.get('english','')
    if not eng:
        issues['missing_english'].append(lemma)
    else:
        if len(eng.split()) > 2:
            issues['too_many_words'].append({'lemma': lemma, 'english': eng})
        if any(c in eng for c in ".,;:/\\\\\"'`~!@#$%^&*()[]{}<>?|"):
            issues['punctuation'].append({'lemma': lemma, 'english': eng})

    z = zipf_frequency(lemma, 'nl')
    if z < 2.0:
        issues['low_zipf'].append({'lemma': lemma, 'zipf': z})

    lvl = item.get('level')
    if lvl is not None:
        level_counts[lvl] = level_counts.get(lvl, 0) + 1
    pos = item.get('pos')
    if pos:
        pos_counts[pos] = pos_counts.get(pos, 0) + 1

summary = {k: len(v) for k, v in issues.items()}
summary['level_counts'] = level_counts
summary['pos_counts'] = pos_counts

with open(os.path.join(OUT_DIR, 'audit_summary.json'), 'w', encoding='utf-8') as f:
    json.dump({'summary': summary, 'issues': issues}, f, ensure_ascii=False, indent=2)

print('Audit complete:', summary)
