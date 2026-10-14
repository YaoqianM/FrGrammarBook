# IELTS 学术词汇进阶宝典 · IELTS Academic Vocabulary Builder

A five-volume English vocabulary course in Chinese and English, written for junior-high learners in Shenzhen who are working towards IELTS Academic, with Band 9 as a long-term goal.

📘 **The PDFs** are in [`pdf/`](pdf/):

| Volume | File | Level | Units | Entries |
|---|---|---|---|---|
| Ⅰ 基础升级 Foundations Upgrade | `IELTS_Vocab_Vol1_Foundations_Upgrade.pdf` | A2 → B1 | 1–12 | 671 |
| Ⅱ 中级核心 Core Vocabulary | `IELTS_Vocab_Vol2_Core_Vocabulary.pdf` | B1 → B2 | 13–26 | 837 |
| Ⅲ 高级应用 Academic & Topic Vocabulary | `IELTS_Vocab_Vol3_Academic_and_Topic_Vocabulary.pdf` | B2 → C1 | 27–40 | 795 |
| Ⅳ 高分精修 Precision & Band Boosters | `IELTS_Vocab_Vol4_Precision_and_Band_Boosters.pdf` | C1 → C2 | 41–51 | 712 |
| Ⅴ 索引与复习手册 Index & Review Handbook | `IELTS_Vocab_Vol5_Index_and_Review_Handbook.pdf` | all | — | indexes |

**3,015 deduplicated entries** (words, collocations, phrasal verbs and fixed expressions), plus 971 derived forms listed in word families and not counted twice. 482 ★ featured entries carry a short explanation. There are 49 compare boxes for confusable words and 69 tip/IELTS boxes. Every unit ends with an auto-generated Quick Review, and each volume has its own answer key and index.

Volume 5 contains the study roadmap, review methods, topic index, a master A–Z index (entry number + volume/page), the word-family index, a confusable-words quick reference and a collocation summary.

## How it is built

The content is plain text in `data/`, one file per unit (format described at the top of `tools/build.py`). The pipeline is the one from the French grammar book in this repository (Markdown/HTML → headless Chromium → PDF), adapted for structured vocabulary data:

```bash
npm install                 # at the repository root: Playwright + fonts
pip install markdown pypdf pyspellchecker
cd ielts-vocab
python3 tools/build.py check   # duplicates, word-family double counting, format, statistics
python3 tools/qa.py            # spelling, cross-references, example coverage
./tools/make.sh                # builds all five volumes (two passes each for page numbers)
```

The `check` step fails on duplicate headwords and on a derived form that is both a word-family member and a separate entry, so the count stays honest. `data/fam-ok.txt` lists the deliberate exceptions.
