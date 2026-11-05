# La grammaire française, clairement — A1 → B2 (TCF Canada)

A ~220-page French grammar book in **French, English and Chinese** (法·英·中三语对照), written for a Chinese speaker who knows some English and wants to go from A1 to a solid **B2 / NCLC 7** on the **TCF Canada**.

📘 **The book:** [`French_Grammar_TCF_Canada_B2.pdf`](French_Grammar_TCF_Canada_B2.pdf)

## 📰 New: *The French World* — a bilingual reading magazine (A1 → B2)

A dark-mode French ⇄ Chinese reading magazine for iPad, with a serial love story, stories, humour, talk-show parodies, debates, philosophy, practical life in Paris and Montréal, and 1,700+ vocabulary cards. The complete magazine (A1 → B2 + C1 bonus + TCF section, ≈ 710 pages): **[`french-world/The_French_World.pdf`](french-world/The_French_World.pdf)** · details in [`french-world/README.md`](french-world/README.md).

## 📰 *The Spanish World* — the same magazine for Spanish (A1 → B2)

Spanish ⇄ Chinese edition: Mexican Spanish with notes for Spain, a serial from Ciudad de México to Madrid, Mexican and Spanish slang, public-domain Spanish poetry and a DELE B2 / SIELE section (564 pages): **[`spanish-world/The_Spanish_World.pdf`](spanish-world/The_Spanish_World.pdf)** · details in [`spanish-world/README.md`](spanish-world/README.md).

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
