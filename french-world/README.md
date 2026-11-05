# The French World · 法语世界

A bilingual **French ⇄ Simplified Chinese** reading magazine that takes a learner from **A1 to B2** (plus a "Vers le C1" bonus issue), built for reading on an iPad in dark mode.

📘 **The magazine:** [`The_French_World.pdf`](The_French_World.pdf)

**Status:** Batch 1 is published: the Ouverture plus Volumes I–II, **A1 and A2, N°1 to N°6**. Batch 2 (B1, B2, Vers le C1, the TCF Canada section) comes next.

## What's inside (batch 1)

| | |
|---|---|
| Issues | N°1 Premières fois · N°2 La ville · N°3 Les gens (A1) · N°4 Hier · N°5 Au travail · N°6 Ailleurs (A2) |
| Pieces | 85: serial *Marie & Lucas* (6 episodes + the Ouverture triptych), stories, everyday life (Paris and Montréal), humour, dating and relationships, talk show *Le Plateau*, debates, *Idées qui dérangent*, psychology, philosophy, science, poetry, expressions and slang |
| Reading | 1,081 French ⇄ Chinese sentence pairs, each on one aligned row |
| Vocabulary | 800 entries (gender, IPA, Chinese, English, example, collocations, word family, notes) + 169 expressions with register labels |
| Grammar | short « Rappel » reminders pointing to chapters of [`../French_Grammar_TCF_Canada_B2.pdf`](../French_Grammar_TCF_Canada_B2.pdf) |
| Progress | word counter, reading log and badges at the end of each issue |
| Navigation | clickable table of contents, per-issue contents, PDF bookmarks, linked vocabulary / expression / grammar / content indexes, answer key |

## Deliverables (`deliverables/`, regenerated on every build)

- `vocabulary.csv`, `vocabulary.xlsx` — unified vocabulary database (sheets: Vocabulary, Expressions, Grammar, Content)
- `anki_vocabulary.tsv` — flashcards for Anki, tagged by level and TCF topic
- `expressions.csv` — expressions, idioms and slang with register
- `tcf_vocabulary.md` — vocabulary grouped by TCF topic
- `grammar_index.md`, `content_index.md`, `answer_key.md`
- `cefr_coverage.md`, `repetition_report.md` — coverage per level; duplicate checks and how often words reappear
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

Set `CHROMIUM_PATH` if Chromium is not at `/opt/pw-browsers/chromium-1243/chrome-linux64/chrome`.
