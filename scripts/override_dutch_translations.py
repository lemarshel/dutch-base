import json

DATA = 'C:/Users/hp/dutch-base/data/words.json'

OVERRIDES = {
    'julia': 'julia',
    'lyon': 'lyon',
    'andré': 'andre',
    'hendriks': 'hendriks',
    'willems': 'willems',
    'aart': 'aart',
    'jonker': 'jonker',
    'sexdate': 'sex date',
    'syrisch': 'syrian',
    'dragon': 'dragon',
    'kuil': 'pit',
    'geus': 'rebel',
    'webshop': 'online shop',
    'polder': 'polder',
    'kamerlid': 'member',
}

with open(DATA,'r',encoding='utf-8') as f:
    data=json.load(f)

for item in data:
    lemma = item['lemma']
    if lemma in OVERRIDES:
        item['english'] = OVERRIDES[lemma]

with open(DATA,'w',encoding='utf-8') as f:
    json.dump(data,f,ensure_ascii=False,indent=2)

print('Overrides applied')
