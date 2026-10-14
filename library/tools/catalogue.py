#!/usr/bin/env python3
"""Regenerate editorial/catalogue.md and editorial/lexicon-index.md from article metadata."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from build import ARTICLES, LIB, PARTS, parse, split_targets, sort_key

arts = {a["id"]: a for a in map(parse, sorted(ARTICLES.glob("A*.md")))}
part_of = {aid: f"{num}·{name}" for num, name, _, ids in PARTS for aid in ids}

rows = ["# 文章目录", "", "由 `tools/catalogue.py` 根据各文章头部元数据生成，勿手改；改文章元数据后重新运行。", "",
        "| ID | 标题 | 等级 | 分册部分 | 文体 | 目标词/表达 | 加拿大 | 来源 |", "|---|---|---|---|---|---|---|---|"]
for aid in sorted(arts):
    a = arts[aid]
    cell = lambda k: a.get(k, "").replace("|", "/")
    rows.append(f"| {aid} | {cell('title')} | {cell('level')} | {part_of.get(aid, '—')} | {cell('genre')} | "
                f"{cell('targets')} | {cell('canada')} | {cell('sources')} |")
rows += ["", "## 备选库（未分配 ID）", "",
         "- *soixante-dix / septante / huitante*（A1 小短文）",
         "- *savoir / connaître*（等待合适的场景）",
         "- *pourtant / cependant / toutefois / néanmoins*（接在 A009 之后）",
         "- 魁北克房屋 *3 ½ / 4 ½*、*le 1er juillet* 搬家日（可并入住房词汇篇）",
         "- *piastre / piasse*、*un trente sous*（需先核查）"]
(LIB / "editorial" / "catalogue.md").write_text("\n".join(rows) + "\n", encoding="utf-8")

index = {}
for aid, a in arts.items():
    for t in split_targets(a.get("targets", "")):
        index.setdefault(t, set()).add(aid)
lines = ["# 词汇总表（自动生成）", "",
         "所有文章 `targets` 字段的汇总：词 → 讲解它的文章。写新文章前先在这里查重；"
         "讲解细节与可深化方向见 `lexicon.md`。", "", "| 词/表达 | 文章 |", "|---|---|"]
for t, ids in sorted(index.items(), key=lambda kv: (sort_key(kv[0]), kv[0])):
    lines.append(f"| {t} | {', '.join(sorted(ids))} |")
(LIB / "editorial" / "lexicon-index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"{len(arts)} articles, {len(index)} terms")
