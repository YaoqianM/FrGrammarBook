# The `.fw` source format

One file per issue (or per half-issue), in `src/`, sorted by name: `00-front.fw`, `01a.fw`, `01b.fw` … `14-exam.fw`. Directives start with `@`; block directives end with a line `@end`. `%%` starts a comment line. A blank line inside a piece = a small gap between rows.

## Structure

```
@issue 4 | A2 | Hier | 昨天 | Tagline in target language || 中文标语
@cast Marie=玛丽, Lucas=卢卡斯, Le serveur=服务员      (speaker name → Chinese label; can repeat anywhere)
@piece serial | Title | 中文标题 | A2 [| big|np]        (kind | title | zh title | level | options)
@deck One-line hook in target language || 中文导语
@meta characters=Marie, Lucas; setting=café, Paris; themes=…; topics=travail, logement
@part B1 | Subtitle | 中文                             (new page + level chip; used for the triptych)
@h Subheading || 小标题
Target-language sentence. || 中文翻译。                (one numbered aligned row)
[Marie] Dialogue line. || 台词。                       (row with speaker; speaker must be in @cast)
@quote Quotation || 译文 || Author, Work (year)
@break                                                  (page break)
@badge Name || 中文 || concrete action that earns it   (issue-level, 5 per issue)
```

Non-numeric issues are allowed (`@issue TCF | TCF | …`, `@issue DELE | DELE | …`); add a level chip class for that label in `style.css` and a volume label in `sommaire()`.

`topics=` must use the edition's topic list (`TCF_TOPICS` in `build.py`): it feeds the "exam vocabulary by theme" index and the Anki tags.

## Piece kinds

`ouverture guide edito serial histoire vie humour amour phrases plateau debat idees psycho philo cine science poesie expr grammaire tcf` — labels are localized in `KINDS`. Kinds marked "new page" in `KINDS` start on a fresh page.

## Blocks (end each with `@end`)

```
@vocab [optional title]
word | pos | ipa | 中文 | english | Example. | 例句。 | collocations · … | word family | note
~word | pos | …        (review card: allowed duplicate, not counted as new)
@end
```
- pos style per edition: French `n.m.`, `v. pron.`; Spanish `s. m.`, `v. prnl.`, `loc. v.`, `adj.`, `adv.`, `interj.`
- IPA without slashes (the build adds them). Fields 8–10 may be empty but keep the pipes.
- Duplicate check = normalized headword + first token of pos. Check `build/headwords.txt` first.

```
@expr [title]
expression | 中文 | register | usage note | Example sentence. || 例句。
@end
```
Register words drive the chip colour (`reg_class`): neutral, colloquial/familier, vulgar, formal/soutenu, regional (Québec / España / México…).

```
@rappel Title | 中文 | Level | chapter-or-empty
2–4 lines of markdown.
= Example from the text. || 例句。
@end

@note kind | Title          (kinds: culture, <regional>, slang, think, funny, tip, warn, idea, source, cn)
Markdown paragraph(s) in the target language, then a Chinese paragraph.
@end

@compare Title
A || 中文 || comment
@end

@versions Title             (one idea in several registers)
REGISTER || Sentence || 中文 || when to use it
@end

@poem Title | Author, Book (year)
Verse || 译文
(blank line = new stanza)
@end

@q Title                    (questions; markdown)
1. …
@end
@a                          (answers → collected in the answer key, with a "see answers p. N" link)
1. …
@end

@speak Title                (speaking challenge; markdown)
@md                         (free markdown: tables, lists)
```

Inline: `**bold**`, `*italic*`, `==highlight==`, ` // ` = line break inside a row.

## Generated output

`build/book.html` → `build/book.pdf` (Chromium, CSS paged media) → `<Edition>.pdf`; `build/pages.json` (page of every marker), `build/headwords.txt`; `deliverables/`: `vocabulary.csv/.xlsx`, `anki_vocabulary.tsv`, `expressions.csv`, `<exam>_vocabulary.md`, `grammar_index.md`, `content_index.md`, `answer_key.md`, `cefr_coverage.md`, `repetition_report.md`. Write `deliverables/study_guide.md` by hand.
