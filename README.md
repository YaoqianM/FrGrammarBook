# La grammaire française, clairement — A1 → B2 (TCF Canada)

A ~220-page French grammar book in **French, English and Chinese** (法·英·中三语对照), written for a Chinese speaker who knows some English and wants to go from A1 to a solid **B2 / NCLC 7** on the **TCF Canada**.

📘 **The book:** [`French_Grammar_TCF_Canada_B2.pdf`](French_Grammar_TCF_Canada_B2.pdf)

## Contents

- **Part 1 · Foundations (A1–A2):** être/avoir, nouns, articles, adjectives, present tense, negation, questions, possessives, prepositions
- **Part 2 · Tenses (A2–B1):** passé composé, imparfait, future tenses, plus-que-parfait, *depuis / il y a / pendant*
- **Part 3 · Pronouns & sentences (B1):** COD/COI, *y/en*, relative pronouns, comparison, adverbs & indefinites
- **Part 4 · Moods (B1–B2):** imperative, conditional, *si* clauses, subjunctive, gérondif
- **Part 5 · B2 toolbox:** passive & causative, reported speech, connectors, register & style, 50 common errors
- **Part 6 · TCF Canada:** exam format and scores, listening/reading strategy, writing and speaking templates with model answers
- **Appendices:** verb tables, numbers/dates/false friends, a 12-month study plan, answer key

## Rebuilding the PDF

The source is Markdown in `src/`. To rebuild:

```bash
npm install          # Playwright + fonts
pip install markdown pypdf
./tools/make.sh      # builds French_Grammar_TCF_Canada_B2.pdf (two passes for TOC page numbers)
```

Set `CHROMIUM_PATH` if Chromium isn't at `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`.
