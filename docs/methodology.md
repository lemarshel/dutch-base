# Methodology — Dutch 4,500 Lemma MVP

## Overview
MVP builds a lemma-based list using:
- wordfreq for candidate ranking (proxy frequency)
- spaCy for lemmatization and POS
- rule-based cleanup for inflected variants

## Canonical forms
- Verbs: infinitive lemma (e.g., gaan)
- Nouns: singular lemma (e.g., huis)
- Adjectives: base form (e.g., groot)
- Separable verbs: full infinitive lemma (e.g., opstaan)

## Candidate generation
1. Pull top 20k Dutch tokens from wordfreq.
2. Filter alphabetic tokens.
3. Lemmatize with spaCy.
4. Aggregate per-lemma frequency with rank-based weights.

## Deduplication rules
- Conjugation/plural forms collapse to base lemma.
- Article-attached and inflectional variants removed.
- Proper nouns removed.

## Ranking
- Sort by aggregated rank-weighted frequency.
- Trim to **4,500** lemmas.
- Assign levels with target distribution: 500 / 700 / 700 / 700 / 650 / 650 / 600.

## Output schema
Each entry includes:
- `rank`, `lemma`, `english`, `pos`, `level`, `freq_score`, `freq_tier`, `register`, `tokens`

## Known gaps (next)
- Replace rank proxy with real corpora (SoNaR + SUBTLEX).
- Add RU translations.
- Add examples + audio.
