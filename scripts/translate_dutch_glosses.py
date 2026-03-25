import json
import re
from transformers import MarianMTModel, MarianTokenizer

DATA = 'C:/Users/hp/dutch-base/data/words.json'
CACHE = 'C:/Users/hp/dutch-base/data/translation_cache.json'

with open(DATA, 'r', encoding='utf-8') as f:
    data = json.load(f)

try:
    with open(CACHE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
except FileNotFoundError:
    cache = {}

model_name = 'Helsinki-NLP/opus-mt-nl-en'
model = MarianMTModel.from_pretrained(model_name)
tokenizer = MarianTokenizer.from_pretrained(model_name)


def normalize_gloss(gloss: str) -> str:
    gloss = gloss.strip()
    gloss = re.sub(r'\s+', ' ', gloss)
    return gloss


def single_word_gloss(gloss: str) -> str:
    gloss = normalize_gloss(gloss)
    if not gloss:
        return ''
    gloss = re.sub(r'^(to\s+)', '', gloss, flags=re.IGNORECASE)
    gloss = re.split(r'[;,/]', gloss)[0].strip()
    gloss = gloss.split()[0] if gloss else ''
    return gloss

BATCH = 64

lemmas = [d['lemma'] for d in data if d['lemma'] not in cache]

for i in range(0, len(lemmas), BATCH):
    batch = lemmas[i:i+BATCH]
    if not batch:
        continue
    tokens = tokenizer(batch, return_tensors='pt', padding=True, truncation=True)
    gen = model.generate(**tokens, max_length=64)
    outs = tokenizer.batch_decode(gen, skip_special_tokens=True)
    for lemma, gloss in zip(batch, outs):
        cache[lemma] = single_word_gloss(gloss)
    if i % (BATCH*10) == 0:
        with open(CACHE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

with open(CACHE, 'w', encoding='utf-8') as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

# apply to data
updated = 0
for item in data:
    lemma = item['lemma']
    if lemma in cache and cache[lemma]:
        item['english'] = cache[lemma]
        updated += 1

with open(DATA, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Updated', updated, 'entries')
