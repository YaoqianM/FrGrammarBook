#!/usr/bin/env python3
"""Build library/build/reader.html from library/articles/*.md.

Each article starts with an HTML comment holding editorial metadata
(id, level, targets, ...). The comment is stripped from the page; `id`,
`level` and `targets` feed the article header, the table of contents and
the vocabulary index. Page numbers come from build/pages.json, written by
locate.py after a first render (two-pass build, see make.sh).
"""
import html
import json
import pathlib
import re
import unicodedata

import markdown

LIB = pathlib.Path(__file__).resolve().parent.parent
ROOT = LIB.parent
ARTICLES = LIB / "articles"
OUT = LIB / "build"
PAGES = OUT / "pages.json"

TITLE = "法语单词有意思"
SUBTITLE = "Les mots qui ont une histoire"
VOLUME = "第一册 · A1–C1 · 加拿大与魁北克"

PARTS = [
    ("一", "英语帮倒忙", "长得像英语，意思却是另一回事",
     ["A001", "A021", "A036", "A038", "A039", "A023", "A022", "A024",
      "A030", "A035", "A037", "A008", "A033", "A010", "A019"]),
    ("二", "英语是法语的仓库", "拼写规律、词族与词的来历",
     ["A044", "A025", "A028", "A026", "A027", "A045", "A029", "A032",
      "A034", "A042", "A043", "A040", "A017", "A046"]),
    ("三", "小词的大差别", "几个改变整句意思的小词",
     ["A002", "A006", "A004", "A007", "A015", "A009", "A018", "A020"]),
    ("四", "在加拿大生活的词", "魁北克日常、工作、住房与公共生活",
     ["A003", "A031", "A041", "A005", "A047", "A016", "A014", "A011",
      "A013", "A012"]),
]

PREFACE = """
这不是一本词汇书，至少不是那种一页列二十个词、配上翻译和例句的词汇书。

这里的每一篇，都从一个小问题开始：为什么魁北克餐厅写 *Apportez votre vin*，外卖却叫 *pour emporter*？为什么法语的"罢工"叫"河岸"？为什么英语越好，读法语时反而越容易猜错？

问题讲清楚了，词也就记住了。

**怎么读。** 不必按顺序。四个部分各有侧重：第一部分专门对付英语"假朋友"；第二部分利用英语和法语之间的拼写规律和共同来历，一次认识一批词；第三部分讲几个会改变整句意思的小词；第四部分是在加拿大、尤其是魁北克生活时用得上的词。每篇标题旁有参考等级（A1–C1），但等级只是提示，不是门槛。

**关于英语。** 如果你的英语不错，它会是你学法语最好的工具——也会是最常见的陷阱。这本书两方面都讲。

**关于地区差异。** 书中会区分通用法语、魁北克常用说法和法国常用说法。没有哪一种"更正确"，只是用在不同的地方。

**关于事实。** 词源、地区用法、法律和公共服务方面的说法，都尽量依据可靠来源核查过，包括魁北克法语办公室（OQLF）、魁北克住房行政法庭（TAL）等机构的资料，以及主要的历史词典。查不到可靠依据的有趣故事，宁可不写，或者明确说明"证据不足"。法律与公共服务信息以 2026 年 10 月核查时为准，实际办事请以官方最新说明为准。

书末有词汇索引，可以按词查找它在哪一篇里被讲过。
"""

MD_EXT = ["tables", "attr_list", "md_in_html", "sane_lists", "nl2br"]

STRONG = re.compile(r"\*\*(?!\*)(?=\S)(.+?)(?<=[^\s*])\*\*")
EM = re.compile(r"(?<!\*)\*(?=[^\s*])(.+?)(?<=[^\s*])\*(?!\*)")


def emphasis(text):
    """Handle **bold** / *italic* ourselves: Markdown won't close emphasis after
    an apostrophe followed by a letter (**l'**homme), which French needs."""
    out = []
    for line in text.split("\n"):
        line = STRONG.sub(r"<strong>\1</strong>", line)
        line = EM.sub(r"<em>\1</em>", line)
        out.append(line)
    return "\n".join(out)


def md(text):
    return markdown.markdown(emphasis(text), extensions=MD_EXT)


def inline(text):
    return re.sub(r"^<p>(.*)</p>$", r"\1", md(text.strip()), flags=re.S)


def curly(text):
    """Chinese prose uses straight quotes in the sources; print curly ones."""
    out = []
    for line in text.split("\n"):
        if line.lstrip().startswith("<"):
            out.append(line)
            continue
        parts = line.split('"')
        line = parts[0] + "".join(("“" if i % 2 else "”") + seg for i, seg in enumerate(parts[1:], 1))
        out.append(line)
    return "\n".join(out)


def parse(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--(.*?)-->\s*", raw, flags=re.S)
    meta = {}
    for line in m.group(1).strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    body = curly(raw[m.end():])
    title_m = re.match(r"#\s+(.*)\n", body)
    meta["title"] = title_m.group(1).strip()
    body = body[title_m.end():]
    # <details> answers are always shown in print
    body = re.sub(r"<details>\s*<summary>(.*?)</summary>",
                  r'<div class="answers" markdown="1">\n\n**\1**\n', body)
    body = body.replace("</details>", "</div>")
    meta["body"] = body
    return meta


def split_targets(s):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "(（":
            depth += 1
        elif ch in ")）":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return [t for t in out if t and t != "—"]


ARTICLE_PREFIX = re.compile(r"^(le |la |les |l'|un |une |des |se |s'|un/une |être |faire |avoir )", re.I)


def sort_key(term):
    t = term.lower().lstrip("-").replace("*", "")
    for _ in range(2):
        t = ARTICLE_PREFIX.sub("", t)
    t = unicodedata.normalize("NFD", t)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", "", t)


def main():
    pages = json.loads(PAGES.read_text()) if PAGES.exists() else {}
    pg = lambda key: str(pages.get(key, "")) if pages else ""

    arts = {}
    for f in sorted(ARTICLES.glob("A*.md")):
        a = parse(f)
        arts[a["id"]] = a
    placed = [i for p in PARTS for i in p[3]]
    missing = set(arts) - set(placed)
    assert not missing, f"articles not placed in a part: {missing}"
    assert len(placed) == len(set(placed)), "article placed twice"

    toc_rows, body_parts, index = [], [], {}
    n = 0
    for pi, (num, name, sub, ids) in enumerate(PARTS, 1):
        pkey = f"p{pi}"
        toc_rows.append(
            f'<div class="toc-part"><span>第{num}部分　{name}</span><span class="pg">{pg(pkey)}</span></div>')
        body_parts.append(
            f'<section class="part"><div class="part-num">第{num}部分</div>'
            f'<div class="part-title">{name}</div>'
            f'<div class="part-sub">{sub} <span class="mark">§{pkey}§</span></div></section>')
        for aid in ids:
            a = arts[aid]
            n += 1
            key = aid.lower()
            title = inline(a["title"])
            toc_rows.append(
                f'<div class="toc-art"><span class="toc-id">{aid}</span>'
                f'<span class="toc-title">{title}</span><span class="toc-lvl">{html.escape(a["level"])}</span>'
                f'<span class="pg">{pg(key)}</span></div>')
            body_parts.append(
                f'<article class="art" id="{key}">'
                f'<div class="art-head"><span class="art-id">{aid} <span class="mark">§{key}§</span></span>'
                f'<span class="art-lvl">{html.escape(a["level"])}</span></div>'
                f'<h1>{title}</h1>'
                f'{md(a["body"])}</article>')
            for t in split_targets(a.get("targets", "")):
                index.setdefault(t, set()).add(aid)

    # vocabulary index, grouped by initial letter
    entries = sorted(index.items(), key=lambda kv: (sort_key(kv[0]), kv[0]))
    groups, cur = [], None
    for term, ids in entries:
        k = sort_key(term)
        letter = k[:1].upper() if k[:1].isalpha() else "#"
        if letter != cur:
            groups.append(f'<div class="idx-letter">{letter}</div>')
            cur = letter
        refs = ", ".join(
            f'{i}{("·" + pg(i.lower())) if pages else ""}' for i in sorted(ids))
        groups.append(f'<div class="idx-row"><span class="idx-term">{inline(term)}</span>'
                      f'<span class="idx-ref">{refs}</span></div>')

    cover = (
        '<section class="cover"><div class="cover-inner">'
        f'<div class="cover-kicker">{SUBTITLE}</div>'
        f'<div class="cover-title">{TITLE}</div>'
        f'<div class="cover-vol">{VOLUME}</div>'
        '<div class="cover-words">actuellement · dépanneur · enjeu · grève · chaise · '
        'magasiner · avocat · journée · tuque · courriel</div>'
        f'<div class="cover-foot">{len(placed)} 篇 · 法语知识阅读库</div>'
        '</div></section>')
    preface = f'<section class="front"><h1>写在前面<span class="mark">§pre§</span></h1>{md(curly(PREFACE))}</section>'
    toc = f'<section class="toc"><h1>目录</h1>{"".join(toc_rows)}</section>'
    idx = (f'<section class="index"><h1>词汇索引<span class="mark">§idx§</span></h1>'
           f'<p class="idx-note">按词查找讲解它的文章（文章编号 · 页码）。冠词、se、être 等不参与排序。</p>'
           f'<div class="idx-cols">{"".join(groups)}</div></section>')
    toc = toc.replace("</section>",
                      f'<div class="toc-part"><span>词汇索引</span><span class="pg">{pg("idx")}</span></div></section>')

    fonts = ["source-serif-4/400.css", "source-serif-4/400-italic.css", "source-serif-4/600.css",
             "source-serif-4/700.css", "source-serif-4/700-italic.css",
             "inter/400.css", "inter/600.css", "inter/700.css",
             "noto-sans-sc/400.css", "noto-sans-sc/700.css",
             "noto-serif-sc/400.css", "noto-serif-sc/700.css"]
    links = "".join(f'<link rel="stylesheet" href="../../node_modules/@fontsource/{p}">' for p in fonts)
    css = (LIB / "tools" / "style.css").read_text(encoding="utf-8")
    doc = ('<!doctype html><html lang="zh"><head><meta charset="utf-8">'
           f'<title>{TITLE} · {SUBTITLE}</title>{links}<style>{css}</style></head><body>'
           f'{cover}{preface}{toc}{"".join(body_parts)}{idx}</body></html>')

    text_only = re.sub(r"<style[^>]*>.*?</style>", "", doc, flags=re.S)
    text_only = re.sub(r"<[^>]+>", "", text_only)
    for m in re.finditer(r".{0,30}(?<![\w])\*{1,3}[^\s*].{0,30}", text_only):
        print("WARN emphasis:", m.group(0).replace("\n", " "))
    OUT.mkdir(exist_ok=True)
    (OUT / "reader.html").write_text(doc, encoding="utf-8")
    print(f"built {n} articles, {len(index)} index entries")


if __name__ == "__main__":
    main()
