# The Spanish World · 西班牙语世界

A bilingual **Spanish ⇄ Simplified Chinese** reading magazine that takes a learner from **A1 to B2**, with a bonus "Hacia el C1" issue and a **DELE B2 / SIELE** section. Spanish edition of [*The French World*](../french-world/): Latin American (Mexican) Spanish as the base, with notes for Spain; the story moves from Ciudad de México to Madrid. Dark mode, pages sized for an iPad in portrait.

📘 **The magazine:** [`The_Spanish_World.pdf`](The_Spanish_World.pdf) (564 pages)

## What's inside

| Part | Issues | Level |
|---|---|---|
| Opening | Modo de empleo, 6-month plan, characters, *Un encuentro inesperado* (A1 → A2 → B1 triptych) | — |
| Volume I | N.º 1 Primeras veces · N.º 2 La ciudad · N.º 3 La gente | A1 |
| Volume II | N.º 4 Ayer · N.º 5 En el trabajo · N.º 6 Lejos | A2 |
| Volume III | N.º 7 Elegir · N.º 8 ¿Y si…? · N.º 9 Lo que nos decimos | B1 |
| Volume IV | N.º 10 El tiempo · N.º 11 El poder de las palabras · N.º 12 Lo que importa | B2 |
| Extra | N.º 13 Hacia el C1 (literary tenses, essay, editorial, Cervantes) | C1 |
| DELE · SIELE | format and scoring, reading test with key, listening transcripts, 2 writing + 3 speaking tasks with B2 models, exam-day checklist | B2 |
| Back matter | answer key, vocabulary index, expressions & slang glossary, DELE vocabulary by theme, grammar index, content index | — |

- **189 pieces**: the serial *María & Lucas* (12 episodes + the opening triptych), short stories, everyday life in Mexico City and Madrid, humour, dating and relationships, the talk show *Esta noche con Rafa*, debates, *Ideas incómodas*, psychology, philosophy, film (*Relatos salvajes*, *Campeones*, *Roma*), science, poetry (original poems + public-domain Machado, Bécquer, Sor Juana, Garcilaso, Lorca, Cervantes), expressions, Mexican and Spanish slang.
- **2,153 aligned sentence pairs**, **798 vocabulary entries** (Latin American IPA, Chinese, English, example, collocations, notes on Mexico vs Spain) and **190 expressions** with register labels.
- **53 short « Recuerda » grammar reminders**, word counter, reading log and badges at the end of every issue.

## Deliverables (`deliverables/`, regenerated on every build)

`vocabulary.csv`, `vocabulary.xlsx`, `anki_vocabulary.tsv`, `expressions.csv`, `dele_vocabulary.md`, `grammar_index.md`, `content_index.md`, `answer_key.md`, `cefr_coverage.md`, `repetition_report.md`, `study_guide.md`.

## Build

Same pipeline as the French edition (source format in [`docs/PLAN.md`](docs/PLAN.md)):

```bash
cd spanish-world
npm install
pip install markdown pypdf openpyxl
bash tools/make.sh
```

## Limitations

- No audio: every word has IPA, and an iPad can read any selected sentence aloud.
- The Spanish and Chinese were written for this book and checked carefully, but not reviewed by a human editor. From N.º 4 onwards the vocabulary cards are shorter than in the French edition.
- Exam formats, visas and paperwork change: always check the official sites (Instituto Cervantes, SIELE, Gobierno de España, SAT, IMSS).
