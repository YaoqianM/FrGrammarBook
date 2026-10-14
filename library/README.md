# 法语知识阅读库 · French Knowledge Reading Library

A1–C1，以 B2 为目标，以 TCF Canada 阅读为主线，以加拿大/魁北克生活为主要场景。

这个目录是一个长期出版项目的工作区。读者看到的是 `articles/` 里的文章；`editorial/` 里的东西只给编辑看。

## 目录

| 路径 | 内容 |
|---|---|
| `editorial/charter.md` | 编辑方针（风格、等级、核查规则的浓缩版）。新对话开始时先读它。 |
| `editorial/lexicon-index.md` | 所有讲过的词 → 文章（自动生成，查重用） |
| `editorial/topic-cards-batch-01.md` | 第一批 20 张选题卡 + 编辑审查记录 |
| `editorial/catalogue.md` | 文章目录：ID、标题、等级、文体、目标表达、状态 |
| `editorial/lexicon.md` | 词汇台账：重点讲过什么、在哪讲的、以后能深化什么 |
| `editorial/sources.md` | 事实核查记录：出处、核查日期、【待核查】清单 |
| `articles/` | 正文。文件名 = 文章 ID + 目标词 |

## 当前进度

- 重心（2026-10-14 调整）：**趣味学单词**为主，阅读训练为辅。
- 第一册已出版：`法语单词有意思_第一册.pdf`（47 篇，117 页，含目录、页码、文章编号、词汇索引）。
- 下一步：第二册选题。备选见 `editorial/catalogue.md` 末尾。

## 重新生成 PDF

```bash
npm install                 # 在仓库根目录：Playwright + 字体
pip install markdown pypdf  # pdftotext（poppler-utils）也需要
./library/tools/make.sh     # 两遍渲染填页码，并重新生成目录与词汇总表
```

文章分到哪个部分、按什么顺序，在 `tools/build.py` 的 `PARTS` 里定义。

## 换新对话时

把 `editorial/charter.md`、`catalogue.md`、`lexicon-index.md`、`lexicon.md` 交给新对话即可接着做。不要依赖"记得"——台账里没写的，就当没讲过。
