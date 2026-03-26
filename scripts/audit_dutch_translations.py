import json
import os
import re
from wordfreq import zipf_frequency
import argostranslate.package
import argostranslate.translate

DATA = 'C:/Users/hp/dutch-base/data/words.json'
OUT_DIR = 'C:/Users/hp/dutch-base/data/audits'
os.makedirs(OUT_DIR, exist_ok=True)

WORD_RE = re.compile(r"[a-z]+")


def ensure_argos():
    argostranslate.package.update_package_index()
    packages = argostranslate.package.get_available_packages()
    pkg = next((p for p in packages if p.from_code == 'nl' and p.to_code == 'en'), None)
    if not pkg:
        raise RuntimeError('No nl->en package found')
    installed = argostranslate.package.get_installed_packages()
    if not any(p.from_code == 'nl' and p.to_code == 'en' for p in installed):
        path = pkg.download()
        argostranslate.package.install_from_path(path)


ensure_argos()
translator = argostranslate.translate.get_translation_from_codes('nl', 'en')

with open(DATA, 'r', encoding='utf-8') as f:
    data = json.load(f)

issues = {
    'invalid_english': [],
    'low_english_zipf': [],
    'non_alpha_english': [],
    'mismatch_translation': [],
    'invalid_dutch': [],
}

for item in data:
    lemma = item['lemma']
    eng = (item.get('english') or '').strip().lower()
    if not eng:
        issues['invalid_english'].append({'lemma': lemma, 'english': eng})
        continue

    if not re.fullmatch(r'[a-z ]+', eng):
        issues['non_alpha_english'].append({'lemma': lemma, 'english': eng})

    words = eng.split()
    if any(zipf_frequency(w, 'en') <= 0 for w in words):
        issues['invalid_english'].append({'lemma': lemma, 'english': eng})
    elif any(zipf_frequency(w, 'en') < 2.0 for w in words):
        issues['low_english_zipf'].append({'lemma': lemma, 'english': eng, 'zipf': min(zipf_frequency(w, 'en') for w in words)})

    if zipf_frequency(lemma, 'nl') <= 0:
        issues['invalid_dutch'].append({'lemma': lemma})

    # translation mismatch check
    try:
        tr = translator.translate(lemma).lower()
        tr_words = set(WORD_RE.findall(tr))
        eng_words = set(WORD_RE.findall(eng))
        if tr_words and eng_words and eng_words.isdisjoint(tr_words):
            issues['mismatch_translation'].append({'lemma': lemma, 'english': eng, 'argos': tr})
    except Exception:
        pass

summary = {k: len(v) for k, v in issues.items()}
with open(os.path.join(OUT_DIR, 'audit_translation.json'), 'w', encoding='utf-8') as f:
    json.dump({'summary': summary, 'issues': issues}, f, ensure_ascii=False, indent=2)

print('Audit translation complete:', summary)
