import argparse
import csv
import json
import os
import re
from collections import defaultdict

from wordfreq import top_n_list, zipf_frequency
import spacy
from transformers import MarianMTModel, MarianTokenizer

TOKEN_RE = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ'\-]+$")

LEVEL_TARGETS = [500, 700, 700, 700, 650, 650, 600]
MIN_ZIPF = 1.8

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

class Translator:
    def __init__(self, model_name='Helsinki-NLP/opus-mt-nl-en'):
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)

    def translate_batch(self, texts):
        batch = self.tokenizer(texts, return_tensors='pt', padding=True, truncation=True)
        gen = self.model.generate(**batch, max_length=64)
        return [t.strip() for t in self.tokenizer.batch_decode(gen, skip_special_tokens=True)]


def normalize_gloss(gloss):
    if not gloss:
        return ''
    gloss = gloss.strip()
    gloss = re.sub(r'\s+', ' ', gloss)
    return gloss.lower()

def single_word_gloss(gloss):
    gloss = normalize_gloss(gloss)
    if not gloss:
        return ''
    # drop leading "to " for verbs
    gloss = re.sub(r'^(to\s+)', '', gloss, flags=re.IGNORECASE)
    # take first segment before punctuation
    gloss = re.split(r'[;,/]', gloss)[0].strip()
    # keep only first word if multiword remains
    gloss = gloss.split()[0] if gloss else ''
    return gloss.lower()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', type=int, default=4500)
    parser.add_argument('--candidates', type=int, default=20000)
    parser.add_argument('--out', default='data/words.json')
    parser.add_argument('--csv', default='data/words_full.csv')
    parser.add_argument('--cache', default='data/translation_cache.json')
    parser.add_argument('--no-translate', action='store_true')
    args = parser.parse_args()

    nlp = spacy.load('nl_core_news_sm', disable=['parser', 'ner'])

    token_list = [t.lower() for t in top_n_list('nl', args.candidates) if TOKEN_RE.match(t)]
    total_tokens = len(token_list)

    lemma_stats = defaultdict(lambda: {'freq': 0.0, 'pos': None, 'tokens': set()})

    for idx, (token, doc) in enumerate(zip(token_list, nlp.pipe(token_list, batch_size=1000))):
        if not doc:
            continue
        t = doc[0]
        if t.pos_ == 'PROPN':
            continue
        pos = POS_MAP.get(t.pos_)
        if not pos:
            continue
        lemma = t.lemma_.lower().strip()
        if not lemma:
            continue
        if not TOKEN_RE.match(lemma):
            continue

        # use zipf frequency for Dutch to prioritize correct spellings
        z = zipf_frequency(lemma, 'nl')
        if z < MIN_ZIPF:
            continue
        lemma_stats[lemma]['freq'] += z
        lemma_stats[lemma]['pos'] = pos
        lemma_stats[lemma]['tokens'].add(token)

    items = []
    for lemma, info in lemma_stats.items():
        items.append({
            'lemma': lemma,
            'pos': info['pos'],
            'freq': info['freq'],
            'tokens': sorted(list(info['tokens'])),
        })

    items.sort(key=lambda x: x['freq'], reverse=True)
    items = items[: args.target]

    levels = []
    idx = 0
    for level, count in enumerate(LEVEL_TARGETS, start=1):
        for _ in range(count):
            if idx >= len(items):
                break
            levels.append(level)
            idx += 1
    while len(levels) < len(items):
        levels.append(7)

    cache = {}
    if os.path.exists(args.cache):
        with open(args.cache, 'r', encoding='utf-8') as f:
            cache = json.load(f)

    translator = None
    if not args.no_translate:
        translator = Translator()

    BATCH = 48
    for i, item in enumerate(items):
        lemma = item['lemma']
        if lemma in cache:
            continue
        if not translator:
            continue

        batch = []
        for j in range(i, min(i + BATCH, len(items))):
            if items[j]['lemma'] in cache:
                continue
            batch.append(items[j]['lemma'])
        if not batch:
            continue

        translated = translator.translate_batch(batch)
        for lemma_text, gloss in zip(batch, translated):
            cache[lemma_text] = single_word_gloss(gloss)
        with open(args.cache, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

    data = []
    for i, item in enumerate(items, start=1):
        lemma = item['lemma']
        gloss = cache.get(lemma, '')
        freq = item['freq']
        tier = 'A' if freq >= 0.9 else 'B' if freq >= 0.8 else 'C' if freq >= 0.7 else 'D'
        register = 'everyday' if freq >= 0.9 else 'mixed' if freq >= 0.8 else 'formal'
        data.append({
            'rank': i,
            'lemma': lemma,
            'english': gloss,
            'pos': item['pos'],
            'level': levels[i-1] if i-1 < len(levels) else 7,
            'freq_score': round(freq, 6),
            'freq_tier': tier,
            'register': register,
            'tokens': item['tokens'],
        })

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(args.csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)

    print(f'Generated {len(data)} entries to {args.out}')


if __name__ == '__main__':
    main()
