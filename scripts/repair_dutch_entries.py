import json
import re
import spacy
from wordfreq import zipf_frequency
from transformers import MarianMTModel, MarianTokenizer

DATA = 'C:/Users/hp/dutch-base/data/words.json'

# Manual overrides for common function words / particles
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
    'zij': 'they',
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
    'duren': 'last',
    'ontstaan': 'arise',
    'ondernemen': 'undertake',
    'bezighouden': 'occupy',
    'aandringen': 'insist',
    'vorderen': 'advance',
    'uiting': 'expression',
    'mop': 'joke',
}

STOPWORDS = {'the','a','an','to','of','in','on','for','and','or','be','is','are','was','were'}

POS_MAP = {
    'NOUN': 'noun',
    'VERB': 'verb',
    'ADJ': 'adjective',
    'ADV': 'adverb',
    'ADP': 'preposition',
    'CCONJ': 'conjunction',
    'SCONJ': 'conjunction',
    'PRON': 'pronoun',
    'DET': 'determiner',
    'NUM': 'numeral',
    'INTJ': 'interjection',
}

WORD_RE = re.compile(r'[a-z]+')

model_name = 'Helsinki-NLP/opus-mt-nl-en'
model = MarianMTModel.from_pretrained(model_name)
tokenizer = MarianTokenizer.from_pretrained(model_name)

nlp = spacy.load('nl_core_news_sm', disable=['parser','ner'])


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


def needs_fix(item):
    eng = item.get('english','')
    if not eng:
        return True
    if not re.fullmatch(r'[a-z ]+', eng):
        return True
    if len(eng.split()) > 2:
        return True
    if eng.strip() == item['lemma'].lower():
        return True
    # too short or low English frequency
    if len(eng.strip()) <= 1:
        return True
    if zipf_frequency(eng.split()[0], 'en') < 2.0:
        return True
    return False

with open(DATA, 'r', encoding='utf-8') as f:
    data = json.load(f)

# retranslate only invalid entries
lemmas_to_fix = [d['lemma'] for d in data if needs_fix(d) and d['lemma'] not in OVERRIDES]

BATCH = 48
for i in range(0, len(lemmas_to_fix), BATCH):
    batch = lemmas_to_fix[i:i+BATCH]
    tokens = tokenizer(batch, return_tensors='pt', padding=True, truncation=True)
    gen = model.generate(**tokens, max_length=64)
    outs = tokenizer.batch_decode(gen, skip_special_tokens=True)
    for lemma, gloss in zip(batch, outs):
        cleaned = sanitize_gloss(gloss)
        for item in data:
            if item['lemma'] == lemma:
                item['english'] = cleaned
                break

# apply overrides and pos corrections
for item in data:
    lemma = item['lemma']
    if lemma in OVERRIDES:
        item['english'] = OVERRIDES[lemma]
    # POS correction via spaCy
    doc = nlp(lemma)
    if doc:
        pos = POS_MAP.get(doc[0].pos_)
        if pos:
            item['pos'] = pos
    # final sanitize
    item['english'] = sanitize_gloss(item.get('english',''))

with open(DATA, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Repair complete')
