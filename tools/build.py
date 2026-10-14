#!/usr/bin/env python3
"""Build build/book.html from src/*.md.

Custom block syntax (on top of normal Markdown):

    :::ex                      example block, one example per line:
    FR sentence || English || 中文
    :::

    :::rule Optional title     coloured boxes whose body is Markdown.
    ...                        types: rule tip warn memo cn real check
    :::

    :::answers                 answers to the chapter's exercises; removed
    ...                        from the chapter and collected into the
    :::                        answer key at the end of the book.

    @part Title || Subtitle    full-page part divider.
"""
import html
import json
import pathlib
import re

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "build"
PAGES = OUT / "pages.json"

MD_EXT = ["tables", "attr_list", "md_in_html", "sane_lists", "fenced_code"]

BOX_LABELS = {
    "rule": ("📌", "Règle · Rule · 规则"),
    "tip": ("💡", "Astuce · Tip · 窍门"),
    "warn": ("⚠️", "Piège · Trap · 常见错误"),
    "memo": ("🧠", "Mémo · Memory hook · 记忆法"),
    "cn": ("🀄", "Pour les sinophones · 中文母语者注意"),
    "real": ("🗣️", "Dans la vraie vie · Real life · 真实用法"),
    "check": ("✍️", "Exercices · Quick check · 练习"),
}


STRONG = re.compile(r"\*\*(?!\*)(?=\S)(.+?)(?<=[^\s*])\*\*")
EM = re.compile(r"(?<!\*)\*(?=[^\s*])(.+?)(?<=[^\s*])\*(?!\*)")


def emphasis(text):
    """Convert **bold** / *italic* ourselves: Markdown refuses to close emphasis
    after an apostrophe followed by a letter (**l'**homme), which French needs
    constantly."""
    out, in_code = [], False
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            in_code = not in_code
        elif not in_code:
            line = STRONG.sub(r"<strong>\1</strong>", line)
            line = EM.sub(r"<em>\1</em>", line)
        out.append(line)
    return "\n".join(out)


def md(text):
    return markdown.markdown(emphasis(text), extensions=MD_EXT)


def md_inline(text):
    out = md(text.strip())
    return re.sub(r"^<p>(.*)</p>$", r"\1", out, flags=re.S)


def render_examples(lines):
    rows = []
    for line in lines:
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split("||")]
        fr = parts[0]
        en = parts[1] if len(parts) > 1 else ""
        zh = parts[2] if len(parts) > 2 else ""
        cls = "ex"
        if fr.startswith("✗"):
            cls += " bad"
        elif fr.startswith("✓"):
            cls += " good"
        gloss = []
        if en:
            gloss.append(f'<span class="en">{md_inline(en)}</span>')
        if zh:
            gloss.append(f'<span class="zh">{md_inline(zh)}</span>')
        rows.append(
            f'<div class="{cls}"><div class="fr">{md_inline(fr)}</div>'
            f'<div class="gloss">{" ".join(gloss)}</div></div>'
        )
    return '<div class="examples">' + "".join(rows) + "</div>"


def render_box(kind, title, body):
    icon, label = BOX_LABELS[kind]
    head = f'<span class="icon">{icon}</span><span class="label">{label}</span>'
    if title:
        head += f'<span class="title">{md_inline(title)}</span>'
    return (
        f'<div class="box {kind}"><div class="box-head">{head}</div>'
        f'<div class="box-body">{md(body)}</div></div>'
    )


def preprocess(text, answers):
    """Turn custom blocks into raw HTML; stash answers."""
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^:::(\w+)\s*(.*)$", line)
        if m and m.group(1) != "":
            kind, title = m.group(1), m.group(2).strip()
            j = i + 1
            body = []
            while j < len(lines) and lines[j].strip() != ":::":
                body.append(lines[j])
                j += 1
            if kind == "ex":
                out.append("\n" + render_examples(body) + "\n")
            elif kind == "answers":
                answers.append("\n".join(body))
            else:
                out.append("\n" + render_box(kind, title, "\n".join(body)) + "\n")
            i = j + 1
            continue
        m = re.match(r"^@part\s+(.*)$", line)
        if m:
            parts = [p.strip() for p in m.group(1).split("||")]
            sub = "".join(f'<div class="part-sub">{html.escape(p)}</div>' for p in parts[1:])
            out.append(
                f'\n<section class="part"><div class="part-title">{html.escape(parts[0])}</div>{sub}</section>\n'
            )
            i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def slug(n):
    return f"s{n}"


def main():
    pages = json.loads(PAGES.read_text()) if PAGES.exists() else {}
    files = sorted(SRC.glob("*.md"))
    chapters_html = []
    toc = []  # (level, id, text)
    answer_sections = []
    counter = 0

    for f in files:
        answers = []
        body = md(preprocess(f.read_text(encoding="utf-8"), answers))

        def tag(m):
            nonlocal counter
            counter += 1
            hid = slug(counter)
            if m.group("part") is not None:
                inner = m.group("part")
                text = re.sub(r"<[^>]+>", "", inner)
                toc.append((0, hid, text))
                return f'<section class="part" id="{hid}"><div class="part-title">{inner}<span class="mark">§{hid}§</span></div>'
            level, attrs, inner = m.group("lvl"), m.group("attrs"), m.group("inner")
            if 'class="notoc"' not in attrs:
                text = re.sub(r"<small>.*?</small>", "", inner, flags=re.S)
                text = re.sub(r"<[^>]+>", "", text).strip()
                toc.append((int(level), hid, text))
            return f'<h{level} id="{hid}"{attrs}>{inner}<span class="mark">§{hid}§</span></h{level}>'

        body = re.sub(
            r'<section class="part"><div class="part-title">(?P<part>.*?)</div>'
            r'|<h(?P<lvl>[12])(?P<attrs>[^>]*)>(?P<inner>.*?)</h(?P=lvl)>',
            tag, body, flags=re.S)
        cls = "frontmatter" if f.name.startswith("00") else "chapter"
        chapters_html.append(f'<article class="{cls}">{body}</article>')
        if answers:
            first_h1 = re.search(r"^#\s+(.*)$", f.read_text(encoding="utf-8"), re.M)
            title = first_h1.group(1) if first_h1 else f.stem
            title = re.sub(r"\s*<small>.*?</small>", "", title)
            lines = [ln for a in answers for ln in a.split("\n") if ln.strip()]
            answer_sections.append(f"### {title}\n\n" + "\n\n".join(lines))

    # answer key
    if answer_sections:
        counter += 1
        hid = slug(counter)
        toc.append((1, hid, "Corrigés des exercices · Answer key · 练习答案"))
        ak = md("\n\n".join(answer_sections))
        chapters_html.append(
            f'<article class="chapter answers"><h1 id="{hid}">Corrigés des exercices<span class="mark">§{hid}§</span>'
            f'<br><small>Answer key · 练习答案</small></h1>{ak}</article>'
        )

    # table of contents
    toc_rows = []
    for level, hid, text in toc:
        page = pages.get(hid, "")
        cls = {0: "toc-part", 1: "toc-ch", 2: "toc-sec"}[level]
        if level == 2:
            continue  # sections are in the PDF bookmarks; keep the printed TOC short
        toc_rows.append(
            f'<a class="{cls}" href="#{hid}"><span class="t">{text}</span>'
            f'<span class="dots"></span><span class="p">{page}</span></a>'
        )
    toc_html = '<article class="toc"><h1 class="notoc-h">Table des matières<br><small>Contents · 目录</small></h1>' + "".join(toc_rows) + "</article>"

    cover = (ROOT / "tools" / "cover.html").read_text(encoding="utf-8")
    css = (ROOT / "tools" / "style.css").read_text(encoding="utf-8")
    fonts = [
        "source-serif-4/400.css", "source-serif-4/400-italic.css", "source-serif-4/600.css",
        "source-serif-4/700.css", "source-serif-4/600-italic.css",
        "inter/400.css", "inter/600.css", "inter/700.css", "inter/800.css",
        "noto-sans-sc/400.css", "noto-sans-sc/700.css",
        "noto-serif-sc/400.css", "noto-serif-sc/700.css",
    ]
    links = "".join(f'<link rel="stylesheet" href="../node_modules/@fontsource/{p}">' for p in fonts)
    # the front matter (file 00) goes before the TOC; everything else after
    front = [c for c in chapters_html if c.startswith('<article class="frontmatter"')]
    rest = [c for c in chapters_html if not c.startswith('<article class="frontmatter"')]
    doc = (
        '<!doctype html><html lang="fr"><head><meta charset="utf-8">'
        "<title>Grammaire française pour le TCF Canada (B2)</title>"
        f"{links}<style>{css}</style></head><body>"
        f"{cover}{toc_html}{''.join(front)}{''.join(rest)}</body></html>"
    )
    # drop header rows that are entirely empty (tables written with "| | |" headers)
    doc = re.sub(r"<thead>\s*<tr>(?:\s*<th[^>]*>\s*</th>)+\s*</tr>\s*</thead>", "", doc)
    # warn about Markdown emphasis that failed to render
    text_only = re.sub(r"<(pre|style)[^>]*>.*?</\1>", "", doc, flags=re.S)
    text_only = re.sub(r"<[^>]+>", "", text_only)
    for m in re.finditer(r".{0,40}\*\*?[^\s*].{0,40}", text_only):
        print("WARN emphasis:", m.group(0).replace("\n", " "))
    OUT.mkdir(exist_ok=True)
    (OUT / "book.html").write_text(doc, encoding="utf-8")
    (OUT / "toc.json").write_text(json.dumps(toc, ensure_ascii=False), encoding="utf-8")
    print(f"built {len(files)} files, {len(toc)} toc entries")


if __name__ == "__main__":
    main()
