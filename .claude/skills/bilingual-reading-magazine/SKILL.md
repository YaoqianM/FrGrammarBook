---
name: bilingual-reading-magazine
description: Build a long bilingual graded-reading magazine as one PDF — target language (French, Spanish, or any other) on the left, the learner's language (usually Simplified Chinese) on the same row on the right — taking a learner from A1 to B2/C1 through a serial love story, short stories, humour, talk-show parodies, debates, philosophy, practical life abroad, poems, vocabulary cards with IPA, short grammar reminders, progress badges and an exam section (TCF, DELE, SIELE…), plus vocabulary spreadsheet, Anki deck and indexes. Use this skill whenever someone asks for a bilingual reader, graded reader, language-learning magazine, "learn X by reading" PDF, a side-by-side translation book for an iPad, or wants an existing edition (e.g. The French World / The Spanish World in this repo) adapted to another language, level, reader or exam — even if they only say "make the same book for my friend who learns Italian".
---

# Bilingual reading magazine (A1 → B2/C1, one PDF)

This skill captures how *The French World* (`french-world/`) and *The Spanish World* (`spanish-world/`) were made in this repository, and the directions the user set along the way. Both editions are complete working examples: read their `docs/PLAN.md` and a source file (`src/*.fw`) before writing anything new.

## What the user wants (directions set in past sessions)

These came from the user's own answers and corrections. Treat them as defaults unless the user changes them.

- **Ask first, build second.** Before a 500-page job the user asked for about 20 questions up front. Use `references/interview.md`. For an adaptation of an existing edition, 4–5 questions are enough (variety of the language, settings, what to do with culture-specific content, delivery).
- **Reading first, grammar light.** The user explicitly downgraded grammar to *short reminders only*: 2–4 lines + one example from the text, optionally pointing to a chapter of a separate grammar book. Do not write grammar lessons.
- **"Like TikTok": variety and visible progress.** Many short, different pieces per issue; the rhythm changes constantly. Each issue ends with a word counter, a reading log and five badges tied to concrete actions.
- **Heavy vocabulary.** Vocabulary cards with IPA, the learner's language, a few English glosses, an example with translation, collocations, word family and a usage note (false friends, regional variants, register).
- **Real adult life.** Dating, jealousy, breakups, cheating, swearing (each with register and when not to use it), immigration paperwork, money, work. Romance is realistic and characters may behave badly and grow, but keep sex implied rather than explicit, and never teach manipulation (the talk-show "seduction coach" exists to be mocked).
- **Practical for immigration and exams.** Life in the destination country (renting, bank, doctor, taxes, driving licence, integration) and a separate exam section at the end (format, scores, practice tests with answer key, writing and speaking models, exam-day checklist).
- **One dark PDF for an iPad in portrait** (160 × 230 mm), delivered in batches if the user wants (they chose A1+A2 first, then the rest), or all at once.
- **Budget matters.** When the user mentions money or says "don't overdo it, just translate", switch to compact mode (below) and say what is being trimmed.

## Workflow

1. **Interview** (`references/interview.md`). Record every decision in `<edition>/docs/PLAN.md`: reader, levels, issue list, cast, serial episode beats, section kinds, note kinds, registers, topic list, grammar plan, exam. This file is what keeps a 15-file project consistent across context compactions.
2. **Set up the edition folder** from `assets/pipeline/` (a copy of the Spanish edition's tools; `french-world/tools/` is the French one) (copy into `<edition>/tools/`, plus `package.json`, `.gitignore` from `gitignore`), run `npm install` (Chromium is preinstalled; set `CHROMIUM_PATH` if needed). Localize the labels in `build.py` (see "Localizing the pipeline").
3. **Write the source** one issue at a time in the `.fw` format (`references/fw-format.md`). Start with the front matter (how to read, six-month plan, characters, the opening triptych A1→A2→B1 of the same scene).
4. **Build after every issue**: `python3 tools/build.py` must report `errors=0 dupes=0`. Fix before moving on. Check `build/headwords.txt` before adding vocabulary.
5. **Commit and push after each issue or volume**, so nothing is lost if the session ends.
6. **Final build**: `bash tools/make.sh` (two passes: layout, then page numbers). Run the QA checklist below.
7. **Deliver**: README for the edition, `deliverables/study_guide.md`, a line in the root README, commit, push, send the PDF with the file-sending tool, and summarize in the user's language what is in it and what was trimmed.

## Shape of an issue

About 12–16 pieces, ~150 aligned rows, mixing: editorial · serial episode · story · 1–2 everyday-life guides · humour/culture · love & relationships · "beautiful phrases" (one idea in 5–6 registers) · talk show · debate (two characters, two sides) · "ideas that disturb" (with an "and if it were false?" counter-note) · psychology (with a sources note) · philosophy (with one short attributed quote) · film & philosophy · science · poem · expressions/slang. Then five `@badge` lines. Levels: three issues per CEFR level A1–B2, then a C1 bonus issue, then the exam section, then back matter (generated).

The serial carries the book: one episode per issue, the same café scene at the start and at the end (a dropped phone, a red scarf, a book with a phone number), a misunderstanding, a job offer abroad, a breakup chosen by the heroine for her own life, letters across the distance, a reunion in the new city. Recurring characters appear in other sections (the flatmate, the comedian friend hosting the talk show, the colleague who is also learning the language — the reader's mirror).

## Adapting an edition to another language

Keep the structure, the serial plot, the Chinese column style and the layout; replace everything that is specific to the source culture with its real equivalent. The French→Spanish mapping in `references/adaptation-map.md` is the worked example: cities, names, food, slang, jokes, public-domain poems, films, paperwork, exam, the regional-variant note kind, and the grammar points that only exist in one language. Decide the base variety with the user (e.g. Mexican Spanish with notes for Spain) and keep IPA consistent with it.

## Accuracy and rights

- Facts, studies and statistics get a `@note source` with authors, journal and year; laws, visas, taxes and exam formats get a "rules change, check the official site" warning.
- Poems in full only when in the public domain; modern authors only as one short attributed quote. Translated quotes are marked "traducción libre / traduction libre"; do not invent quotations or present a paraphrase as a quote.
- Real-world numbers you are unsure of: say less rather than guess (a vague true sentence beats a precise wrong one).

## Compact mode (when budget is tight)

- Read the source edition without its vocabulary/expression blocks and without the Chinese column (an `awk` + Python filter), then write one `.fw` file per issue in a single write.
- 3–7 vocabulary cards per piece instead of 10–15; keep every row, rappel, question/answer and badge.
- Two tool calls per issue (read, write) plus one build/commit every two issues.
- Tell the user honestly what was trimmed (in the README too).

## Localizing the pipeline

In `build.py`: `KINDS` (section labels), `NOTE_KINDS` (note boxes, including the regional variant), `reg_class` keywords (register chips), `norm()` and `word_regex()` (article stripping and verb endings for highlighting), `TCF_TOPICS` (topic list used by `@meta topics=`), `iss_label` (issue numbering style), all opener/tracker/sommaire/back-matter strings, `html lang`, title. In `style.css`: the `@page` header strings. Replace `cover.html`. In `make.sh`: the output file name. Grep for the previous language's strings afterwards.

## QA checklist

- `build.py` summary: `errors=0 dupes=0`; counts of pieces, rows, vocab, expressions, grammar look right.
- `make.sh` reports as many located markers as there are `§…§` markers in `build/book.html`, and `build/book.html` has no empty page numbers (`<span class="s-n"></span>`, `ip`, `vin`, `tp`).
- Visual check: render a contact sheet of a few pages (cover, contents, an issue opener, a serial page, a vocabulary page, the tracker, an index) with `pdftoppm -r 40` and look at it.
- Spot-check Chinese column completeness (the build errors on missing translations) and the answer key.

## Pitfalls already solved (do not rediscover them)

- Field splitting uses single `|` only (`split_fields`), so `||` inside a sample sentence is safe; avoid `" | "` inside a field.
- Vocabulary duplicates are keyed on headword + part-of-speech class; reuse a word on purpose with `~word` (review card). A placeholder line `word | ~ | …` is ignored — delete it rather than leave it.
- Page markers can be clipped by the text extractor (long titles near the margin); `locate.py` falls back on the PDF's named destinations.
- Piece headers must not split from their first part (`break-inside: avoid`, `.ph + .part`).
- IPA: phonemic, stress mark before the stressed syllable, syllable dots, one variety; no allophones mixed in.
- Use the regional note kind sparingly and consistently (`⚑ EN ESPAÑA`, `⚜ AU QUÉBEC`).
