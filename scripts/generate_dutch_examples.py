import json
import random
import re
from collections import defaultdict, deque

DATA = 'C:/Users/hp/dutch-base/data/words.json'

random.seed(42)

with open(DATA, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Pools by POS for fillers
nouns = [d['lemma'] for d in data if d['pos'] == 'noun']
verbs = [d['lemma'] for d in data if d['pos'] == 'verb']
adjs = [d['lemma'] for d in data if d['pos'] == 'adjective']
advs = [d['lemma'] for d in data if d['pos'] == 'adverb']

contexts = [
    'op het station', 'in de winkel', 'tijdens de reis', 'na het werk', 'bij het ontbijt',
    'voor de vergadering', 'in het park', 'aan de balie', 'op straat', 'in het ziekenhuis',
    'tijdens de training', 'bij de bushalte', 'na de les', 'in het café', 'bij de kassa',
    'op kantoor', 'in de keuken', 'bij de buren', 'in de lift', 'bij de receptie'
]

subjects = ['de manager', 'mijn buur', 'een student', 'de klant', 'de chauffeur', 'de collega',
            'de gids', 'een vriend', 'de docent', 'de monteur', 'een arts', 'de kok']

modals = ['proberen', 'besluiten', 'weigeren', 'leren', 'vergeten', 'durven', 'moeten', 'willen', 'plannen', 'helpen']

# Template generators

def t_verb_1(w):
    return f"{random.choice(subjects)} besluit om te {w} {random.choice(contexts)}."

def t_verb_2(w):
    return f"Om te {w} vroeg hij om extra tijd {random.choice(contexts)}."

def t_verb_3(w):
    return f"Het is niet makkelijk om te {w} zonder goede voorbereiding."

def t_verb_4(w):
    return f"Tijdens de discussie bleef iedereen proberen te {w}."

def t_verb_5(w):
    return f"Bij het plan hoort ook te {w} met het juiste team."

verb_templates = [t_verb_1, t_verb_2, t_verb_3, t_verb_4, t_verb_5]


def t_noun_1(w):
    return f"In de hoek lag een {w} dat niemand had gezien."

def t_noun_2(w):
    return f"De {w} was plotseling verdwenen na de storm."

def t_noun_3(w):
    return f"Ze kozen een {w} die beter bij het plan past."

def t_noun_4(w):
    return f"Een {w} op tafel maakte het gesprek meteen rustiger."

def t_noun_5(w):
    return f"Voor het project bleek een {w} onmisbaar te zijn."

noun_templates = [t_noun_1, t_noun_2, t_noun_3, t_noun_4, t_noun_5]


def t_adj_1(w):
    return f"De sfeer bleef {w} ondanks het lange wachten."

def t_adj_2(w):
    return f"Het resultaat is {w} maar nog niet perfect."

def t_adj_3(w):
    return f"Na het gesprek werd de situatie {w}."

def t_adj_4(w):
    return f"Het plan klinkt {w} en toch haalbaar."

def t_adj_5(w):
    return f"Zelfs in de regen bleef de weg {w}."

adj_templates = [t_adj_1, t_adj_2, t_adj_3, t_adj_4, t_adj_5]


def t_adv_1(w):
    return f"De trein arriveerde {w} en niemand klaagde."

def t_adv_2(w):
    return f"Ze antwoordde {w} zonder lang na te denken."

def t_adv_3(w):
    return f"Het licht ging {w} uit door de storing."

def t_adv_4(w):
    return f"Hij werkte {w} aan de laatste details."

def t_adv_5(w):
    return f"Het team reageerde {w} op het nieuws."

adv_templates = [t_adv_1, t_adv_2, t_adv_3, t_adv_4, t_adv_5]


def t_other_1(w):
    return f"Ze herhaalde het woord {w} alsof het een afspraak was."

def t_other_2(w):
    return f"Het bordje met {w} hing zichtbaar bij de ingang."

def t_other_3(w):
    return f"De instructie begon met {w} en ging direct verder."

def t_other_4(w):
    return f"In het gesprek hoorde je vaak {w} voorbij komen."

def t_other_5(w):
    return f"Hij schreef {w} bovenaan het formulier."

other_templates = [t_other_1, t_other_2, t_other_3, t_other_4, t_other_5]

pos_templates = {
    'verb': verb_templates,
    'noun': noun_templates,
    'adjective': adj_templates,
    'adverb': adv_templates,
    'pronoun': other_templates,
    'numeral': other_templates,
    'determiner': other_templates,
    'preposition': other_templates,
    'conjunction': other_templates,
    'interjection': other_templates,
    'other': other_templates,
}

# Track template usage to avoid repetition
usage = defaultdict(int)
recent_templates = deque(maxlen=50)


def choose_template(templates):
    # prefer least used template not in recent
    candidates = [t for t in templates if t.__name__ not in recent_templates]
    if not candidates:
        candidates = templates
    chosen = min(candidates, key=lambda t: usage[t.__name__])
    usage[chosen.__name__] += 1
    recent_templates.append(chosen.__name__)
    return chosen


def clean_sentence(s):
    s = re.sub(r"\s+", " ", s).strip()
    if not s.endswith('.'):
        s += '.'
    return s

for item in data:
    lemma = item['lemma']
    pos = item.get('pos','other')
    templates = pos_templates.get(pos, other_templates)
    template = choose_template(templates)
    sentence = template(lemma)
    item['example'] = clean_sentence(sentence)

with open(DATA, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Examples generated')
