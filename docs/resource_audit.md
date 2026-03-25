# Resource Audit — Dutch Core Vocabulary MVP

## Primary corpus sources (open)
- **SoNaR / OpenSoNaR + CGN**: backbone for contemporary written Dutch with broad domain coverage.
- **SUBTLEX-NL**: subtitle frequency for everyday spoken usefulness.

## Lemmatization & morphology
- **spaCy (nl_core_news_sm)**: lemmatizer + POS for Dutch.
- **Stanza**: cross-check pipeline for lemma/POS consistency.

## Cross-check references
- **CELEX (Dutch)**: lemma reference and lexical structure (secondary).

## Notes
- MVP list uses wordfreq for ranked candidates + spaCy lemmatization.
- Next: add SoNaR/SUBTLEX ingestion scripts to replace proxy frequency.
