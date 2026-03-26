import json
import re
from wordfreq import zipf_frequency
import argostranslate.package
import argostranslate.translate

DATA = 'C:/Users/hp/dutch-base/data/words.json'

OVERRIDES = {
    'er': 'there',
    'te': 'to',
    'op': 'on',
    'aan': 'on',
    'de': 'the',
    'het': 'the',
    'een': 'a',
    'en': 'and',
    'of': 'or',
    'maar': 'but',
    'niet': 'not',
    'wel': 'well',
    'in': 'in',
    'uit': 'out',
    'voor': 'for',
    'van': 'of',
    'met': 'with',
    'naar': 'to',
    'tot': 'until',
    'bij': 'at',
    'als': 'if',
    'dat': 'that',
    'dit': 'this',
    'die': 'that',
    'ik': 'i',
    'jij': 'you',
    'je': 'you',
    'hij': 'he',
    'zij': 'she',
    'we': 'we',
    'wij': 'we',
    'jullie': 'you',
    'ze': 'they',
    'elf': 'eleven',
    'twaalf': 'twelve',
    'dertien': 'thirteen',
    'veertien': 'fourteen',
    'vijftien': 'fifteen',
    'zestien': 'sixteen',
    'zeventien': 'seventeen',
    'achttien': 'eighteen',
    'negentien': 'nineteen',
    'twintig': 'twenty',
    'dertig': 'thirty',
    'veertig': 'forty',
    'vijftig': 'fifty',
    'zestig': 'sixty',
    'zeventig': 'seventy',
    'tachtig': 'eighty',
    'negentig': 'ninety',
    'honderd': 'hundred',
}

WORD_RE = re.compile(r'[a-z]+')
STOPWORDS = {'the','a','an','to','of','in','on','for','and','or','be','is','are','was','were'}


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


def sanitize_gloss(text):
    text = text.lower()
    words = WORD_RE.findall(text)
    if not words:
        return ''
    filtered = [w for w in words if w not in STOPWORDS]
    if not filtered:
        filtered = words[:1]
    out = []
    for w in filtered:
        if w not in out:
            out.append(w)
        if len(out) == 2:
            break
    return ' '.join(out)


def needs_fix(lemma, eng, argos_gloss):
    if not eng:
        return True
    if not re.fullmatch(r'[a-z ]+', eng):
        return True
    words = eng.split()
    if any(zipf_frequency(w, 'en') <= 0 for w in words):
        return True
    # mismatch with argos (no overlap)
    arg_words = set(WORD_RE.findall(argos_gloss))
    eng_words = set(WORD_RE.findall(eng))
    if arg_words and eng_words and eng_words.isdisjoint(arg_words):
        return True
    return False


ensure_argos()
translator = argostranslate.translate.get_translation_from_codes('nl', 'en')

with open(DATA, 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    lemma = item['lemma']
    if lemma in OVERRIDES:
        item['english'] = OVERRIDES[lemma]
        continue
    eng = (item.get('english') or '').lower().strip()
    argos_raw = translator.translate(lemma)
    argos_clean = sanitize_gloss(argos_raw)
    if needs_fix(lemma, eng, argos_raw):
        item['english'] = argos_clean
    else:
        # normalize any existing
        item['english'] = sanitize_gloss(eng)

with open(DATA, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Translation fix complete')
