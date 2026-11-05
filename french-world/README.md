# The French World · 法语世界

A bilingual **French ⇄ Simplified Chinese** reading magazine that takes a learner from **A1 to B2**, with a bonus "Vers le C1" issue and a TCF Canada section. Dark mode, pages sized for an iPad in portrait.

📘 **The magazine:** [`The_French_World.pdf`](The_French_World.pdf) (≈ 710 pages)

## What's inside

| Part | Issues | Level |
|---|---|---|
| Opening | Mode d'emploi, 6-month plan, characters, *Une rencontre inattendue* (A1 → A2 → B1 triptych) | — |
| Volume I | N°1 Premières fois · N°2 La ville · N°3 Les gens | A1 |
| Volume II | N°4 Hier · N°5 Au travail · N°6 Ailleurs | A2 |
| Volume III | N°7 Choisir · N°8 Et si… ? · N°9 Ce qu'on se dit | B1 |
| Volume IV | N°10 Le temps · N°11 Le pouvoir des mots · N°12 Ce qui compte | B2 |
| Bonus | N°13 Vers le C1 (passé simple, essay, editorial, Proust) | C1 |
| TCF Canada | format & NCLC table, reading test with key, listening transcripts, 3 writing + 3 speaking tasks with B2 models, exam-day checklist | B1–B2 |
| Back matter | answer key, vocabulary index, expressions & slang glossary, TCF vocabulary by theme, grammar index, content index | — |

- **191 pieces**: serial *Marie & Lucas* (Paris → Montréal, 12 episodes + the opening triptych), short stories, everyday life in Paris and Montréal, humour, dating and relationships, the talk show *Le Plateau* (8 episodes), debates, *Idées qui dérangent* (each with a counter-argument), psychology, philosophy, ciné-philo, science, poetry (original poems + public-domain Verlaine, Hugo, Baudelaire, La Fontaine, Ronsard, Rimbaud, Proust), *Belles phrases*, expressions and slang.
- **2,231 aligned sentence pairs**: every French sentence has its Chinese translation on the same row.
- **1,717 vocabulary entries** (gender, IPA, Chinese, English, example, collocations, word family, notes) and **283 expressions** with register labels (neutre, familier, vulgaire, soutenu, québec).
- **Grammar**: 53 short « Rappel » reminders, each pointing to a chapter of [`../French_Grammar_TCF_Canada_B2.pdf`](../French_Grammar_TCF_Canada_B2.pdf).
- **Progress**: word counter, reading log and badges at the end of every issue.
- **Navigation**: clickable table of contents, per-issue contents, PDF bookmarks, linked indexes.

## Deliverables (`deliverables/`, regenerated on every build)

- `vocabulary.csv`, `vocabulary.xlsx`: unified vocabulary database (sheets: Vocabulary, Expressions, Grammar, Content)
- `anki_vocabulary.tsv`: flashcards for Anki, tagged by level and TCF topic
- `expressions.csv`: expressions, idioms and slang with register
- `tcf_vocabulary.md`: full vocabulary grouped by TCF topic
- `grammar_index.md`, `content_index.md`, `answer_key.md`
- `cefr_coverage.md`, `repetition_report.md`: coverage per level, duplicate checks, and how often words reappear later
- `study_guide.md`

## Source and build

Content is written in a small text format (`src/*.fw`, described in [`docs/PLAN.md`](docs/PLAN.md) §6).
The build parses it, checks for missing translations and duplicate vocabulary, then renders HTML → PDF with headless Chromium (CSS paged media).

```bash
cd french-world
npm install
pip install markdown pypdf openpyxl
bash tools/make.sh      # two passes (page numbers), writes The_French_World.pdf + deliverables/
```

Set `CHROMIUM_PATH` if Chromium is not at `/opt/pw-browsers/chromium-1243/chrome-linux64/chrome`. A full build takes about 7 minutes.

## Limitations

- No audio. Every vocabulary entry has IPA, and the guide explains how to have an iPad read any selected sentence aloud.
- Tick boxes for the reading log and badges are drawn, not interactive form fields.
- French and Chinese were written for this book and checked carefully, but have not been reviewed by a human editor.
- Facts, studies and quotations are attributed in « Source » notes; immigration and exam rules change, so always check the official sites.
