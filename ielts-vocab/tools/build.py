#!/usr/bin/env python3
"""Build the IELTS vocabulary series (volumes 1–5) from ielts-vocab/data/*.txt.

Usage:  build.py check          validate all data (duplicates, format) and print stats
        build.py html N         write build/volN.html (uses build/volN.pages.json if present)

Data format (one file per unit, data/NN-slug.txt):

    @unit 13
    @title Thinking & Intelligence
    @zh 思考、认知与智力
    @level B1–B2
    @intro 一两句中文引入（Markdown）。

    ## Section heading · 中文

    * word | pos | 中文释义 | collocation; collocation | Example. // Example 2. | S W
      ipa: /…/
      fam: derived (n.) · derived (adj.)
      note: 重点讲解（Markdown，可多行 note:）
      also: more collocations
    - word | pos | 中文释义 | collocation | Example.

    @cmp Optional title
    word | 区别说明 | Example.
    word | 区别说明 | Example.
    note: 补充说明
    @end

    @box tip|warn|ielts|memo|rule Optional title
    Markdown…
    @end

`*` = featured (deep) entry, `-` = normal entry. Fields after 中文释义 are optional.
Tags: S = natural in speaking, W = formal / writing.
"""
import hashlib
import html
import json
import pathlib
import random
import re
import sys
import unicodedata

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "build"
MD_EXT = ["tables", "attr_list", "md_in_html", "sane_lists"]

VOLUMES = {
    1: dict(title="Foundations Upgrade", zh="基础升级", level="A2 → B1", units=range(1, 13),
            colour="#1f6f78", accent="#e0a43a", roman="Ⅰ",
            scope="把熟悉但“用不准”的常用词升级：高频动词搭配、日常话题、常见多义词、基础短语动词和第一批易混词。"),
    2: dict(title="Core Vocabulary", zh="中级核心", level="B1 → B2", units=range(13, 27),
            colour="#1f3a68", accent="#e2574c", roman="Ⅱ",
            scope="IELTS 高频生活与社会话题的核心词汇：思维、教育、心理、沟通、工作、消费、城市、住房、动物、媒体、旅游、法律，以及 B2 短语动词和第一批构词法。"),
    3: dict(title="Academic & Topic Vocabulary", zh="高级应用", level="B2 → C1", units=range(27, 41),
            colour="#4a2f73", accent="#f0b23e", roman="Ⅲ",
            scope="学术阅读与写作的主力词汇：科学研究、科技与 AI、环境能源、医疗、农业、经济、政府、历史、伦理、创新、人口，以及学术动词和抽象名词。"),
    4: dict(title="Precision & Band Boosters", zh="高分精修", level="C1 → C2", units=range(41, 52),
            colour="#7a2430", accent="#d7b56d", roman="Ⅳ",
            scope="让表达更准确、更自然：图表与趋势、比例比较、逻辑连接、论证评价、语气缓和、精确形容词、高级搭配、自然口语、高级易混词、近义词精辨和词根。"),
    5: dict(title="Index & Review Handbook", zh="索引与复习手册", level="全套 · All levels", units=range(0),
            colour="#2b3440", accent="#7fc4b8", roman="Ⅴ",
            scope="全套总索引、主题索引、词族索引、易混词速查、高价值搭配汇总、学习路线和复习方法。"),
}
SERIES = "IELTS Academic Vocabulary Builder"
SERIES_ZH = "IELTS 学术词汇进阶宝典"

TAGS = {"S": ("口语", "tag-s"), "W": ("写作", "tag-w")}
BOXES = {
    "tip": ("💡", "记忆窍门 · Tip"),
    "warn": ("⚠️", "常见错误 · Watch out"),
    "ielts": ("🎯", "IELTS 用法 · Exam use"),
    "memo": ("🧠", "知识小站 · Did you know?"),
    "rule": ("🧩", "构词规律 · Pattern"),
}

# ---------------------------------------------------------------- text helpers

STRONG = re.compile(r"\*\*(?!\*)(?=\S)(.+?)(?<=[^\s*])\*\*")
EM = re.compile(r"(?<![\*\w])\*(?=[^\s*])(.+?)(?<=[^\s*])\*(?![\*\w])")


def emphasis(text):
    text = STRONG.sub(r"<strong>\1</strong>", text)
    return EM.sub(r"<em>\1</em>", text)


def md(text):
    return markdown.markdown(emphasis(text), extensions=MD_EXT)


def md_inline(text):
    out = md(text.strip())
    return re.sub(r"^<p>(.*)</p>$", r"\1", out, flags=re.S)


def esc(s):
    return html.escape(s, quote=False)


def sort_key(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = re.sub(r"^(be|the|a|an|to)\s+", "", s)
    return re.sub(r"[^a-z0-9 ]", "", s).strip()


def head_key(head):
    """Key used for duplicate detection."""
    h = head.lower().replace("’", "'")
    h = re.sub(r"\(.*?\)", "", h)
    h = re.sub(r"\b(sb|sth|sb's|one's|oneself|someone|something)\b", "", h)
    h = re.sub(r"[^a-z' -]", " ", h)
    return re.sub(r"\s+", " ", h).strip()


# ------------------------------------------------------------- inflection

IRREG = {
    "be": "am is are was were been being 's 're 'm", "have": "has had having 's 've 'd",
    "do": "does did done doing", "go": "goes went gone going", "take": "took taken",
    "make": "made", "get": "got gotten", "give": "gave given", "come": "came",
    "see": "saw seen", "bring": "brought", "think": "thought", "find": "found",
    "keep": "kept", "put": "putting", "run": "ran running", "set": "setting",
    "hold": "held", "break": "broke broken", "fall": "fell fallen", "grow": "grew grown",
    "rise": "rose risen", "arise": "arose arisen", "catch": "caught", "buy": "bought",
    "teach": "taught", "seek": "sought", "speak": "spoke spoken", "write": "wrote written",
    "drive": "drove driven", "feel": "felt", "leave": "left", "lose": "lost",
    "mean": "meant", "pay": "paid", "say": "said", "sell": "sold", "tell": "told",
    "understand": "understood", "wear": "wore worn", "win": "won winning",
    "choose": "chose chosen", "begin": "began begun beginning", "draw": "drew drawn",
    "show": "shown", "know": "knew known", "throw": "threw thrown", "blow": "blew blown",
    "fly": "flew flown flies", "forget": "forgot forgotten", "hide": "hid hidden",
    "lead": "led", "lie": "lay lain lying", "ride": "rode ridden", "shake": "shook shaken",
    "steal": "stole stolen", "stick": "stuck", "strike": "struck", "sink": "sank sunk",
    "spend": "spent", "build": "built", "send": "sent", "lend": "lent", "bend": "bent",
    "deal": "dealt", "meet": "met", "fight": "fought", "bear": "bore borne",
    "tear": "tore torn", "stand": "stood", "sit": "sat sitting", "eat": "ate eaten",
    "drink": "drank drunk", "sleep": "slept", "wake": "woke woken", "hear": "heard",
    "read": "reads reading", "cut": "cutting", "let": "letting", "hit": "hitting",
    "shut": "shutting", "spread": "spreads", "cost": "costs", "hurt": "hurts",
    "quit": "quitting", "upset": "upsetting", "overcome": "overcame",
    "undergo": "underwent undergone", "withdraw": "withdrew withdrawn",
    "undertake": "undertook undertaken", "foresee": "foresaw foreseen",
    "overtake": "overtook overtaken", "mistake": "mistook mistaken", "swear": "swore sworn",
    "feed": "fed", "light": "lit", "dig": "dug digging", "freeze": "froze frozen",
    "forgive": "forgave forgiven", "forbid": "forbade forbidden", "shine": "shone",
    "slide": "slid", "spin": "spun spinning", "swing": "swung", "wind": "wound",
    "bind": "bound", "seek out": "sought", "outgrow": "outgrew outgrown",
    "oversee": "oversaw overseen", "uphold": "upheld", "withhold": "withheld",
    "outweigh": "outweighs outweighed", "mislead": "misled", "breed": "bred",
    "flee": "fled", "creep": "crept", "weep": "wept", "sweep": "swept", "leap": "leapt",
    "burn": "burnt", "learn": "learnt", "dream": "dreamt", "spell": "spelt",
    "prove": "proven", "sew": "sewn", "saw": "sawn", "sow": "sown", "swell": "swollen",
    "ring": "rang rung", "sing": "sang sung", "swim": "swam swum swimming",
    "drop": "dropped dropping", "stop": "stopped stopping", "plan": "planned planning",
    "child": "children", "person": "people", "man": "men", "woman": "women",
    "mouse": "mice", "foot": "feet", "tooth": "teeth", "goose": "geese",
}


def token_forms(tok):
    t = tok.lower()
    forms = {t, t + "s", t + "es", t + "ed", t + "d", t + "ing", t + "er", t + "est"}
    if re.search(r"[^aeiou]y$", t):
        forms |= {t[:-1] + x for x in ("ies", "ied", "ier", "iest", "ily")}
    if t.endswith("e"):
        forms |= {t[:-1] + "ing"}
    if t.endswith("ie"):
        forms |= {t[:-2] + "ying"}
    if re.search(r"[^aeiou][aeiou][bdgklmnprt]$", t):
        forms |= {t + t[-1] + x for x in ("ed", "ing", "er", "est")}
    if t.endswith("fe"):
        forms.add(t[:-2] + "ves")
    elif t.endswith("f"):
        forms.add(t[:-1] + "ves")
    for a, b in (("is", "es"), ("on", "a"), ("um", "a"), ("us", "i")):
        if t.endswith(a) and len(t) > 5:
            forms.add(t[: -len(a)] + b)
    if t.endswith("c"):
        forms |= {t + "ked", t + "king"}
    forms |= set(IRREG.get(t, "").split())
    return forms


PLACEHOLDER = {"sb", "sth", "sb's", "one's", "oneself", "someone", "something", "…", "...", "doing"}


def head_regex(head):
    """Regex matching the headword (with inflections) inside an example sentence."""
    h = re.sub(r"\(.*?\)", " ", head)
    h = h.replace("/", " ").replace("’", "'")
    toks = [t for t in h.split() if t]
    while toks and toks[0].lower() in PLACEHOLDER:
        toks.pop(0)
    while toks and toks[-1].lower() in PLACEHOLDER:
        toks.pop()
    if not toks:
        return None
    gap = r"(?:\s+[\w'’,-]+){0,5}?"
    parts, pending_gap = [], False
    for t in toks:
        tl = t.lower()
        if tl in PLACEHOLDER:
            pending_gap = True
            continue
        if not re.match(r"^[\w'-]+$", tl):
            return None
        alts = sorted(token_forms(tl), key=len, reverse=True)
        pat = "(?:" + "|".join(re.escape(a) for a in alts) + ")"
        if parts:
            parts.append((gap if pending_gap else "") + r"\s+")
        parts.append(pat)
        pending_gap = False
    return re.compile(r"(?<![\w-])" + "".join(parts) + r"(?![\w-])", re.I)


# ------------------------------------------------------------------- parsing

class Entry:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def parse_unit(path):
    lines = path.read_text(encoding="utf-8").split("\n")
    unit = dict(file=path.name, blocks=[], intro="", level="")
    i, n = 0, 0
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        i += 1
        if not line.strip() or line.startswith("#!"):
            continue
        m = re.match(r"^@(unit|title|zh|level|intro)\s+(.*)$", line)
        if m:
            k, v = m.group(1), m.group(2).strip()
            unit[k] = int(v) if k == "unit" else v
            continue
        if line.startswith("## "):
            unit["blocks"].append(("h2", line[3:].strip()))
            continue
        m = re.match(r"^@(cmp|box)\s*(\w*)\s*(.*)$", line)
        if m:
            kind = m.group(1)
            body = []
            while i < len(lines) and lines[i].strip() != "@end":
                body.append(lines[i].rstrip())
                i += 1
            i += 1
            if kind == "cmp":
                title = (m.group(2) + " " + m.group(3)).strip()
                rows, notes = [], []
                for b in body:
                    if not b.strip():
                        continue
                    if b.strip().startswith("note:"):
                        notes.append(b.strip()[5:].strip())
                    else:
                        f = [x.strip() for x in b.split("|")]
                        if len(f) < 2:
                            raise SystemExit(f"{path.name}: bad cmp row: {b}")
                        rows.append((f[0], f[1], f[2] if len(f) > 2 else ""))
                unit["blocks"].append(("cmp", title, rows, notes))
            else:
                bk = m.group(2)
                if bk not in BOXES:
                    raise SystemExit(f"{path.name}: unknown box {bk}")
                unit["blocks"].append(("box", bk, m.group(3).strip(), "\n".join(body)))
            continue
        m = re.match(r"^([*-])\s+(.*)$", line)
        if m:
            f = [x.strip() for x in m.group(2).split("|")]
            if len(f) < 3:
                raise SystemExit(f"{path.name}:{i}: entry needs head | pos | zh: {line}")
            while len(f) < 6:
                f.append("")
            n += 1
            f = ["" if x in ("—", "-") else x for x in f]
            e = Entry(head=f[0], pos=f[1], zh=f[2], colloc=f[3], example=f[4],
                      tags=f[5].split(), featured=m.group(1) == "*", ipa="", fam="",
                      notes=[], also="", unit=unit.get("unit"), n=n, line=i)
            while i < len(lines) and re.match(r"^\s+(ipa|fam|note|also):", lines[i]):
                k, v = re.match(r"^\s+(\w+):\s*(.*)$", lines[i]).groups()
                if k == "note":
                    e.notes.append(v)
                else:
                    setattr(e, k, v)
                i += 1
            if sum(len(x) for x in e.notes) >= 50:
                e.featured = True  # an entry with a real explanation is a featured entry
            unit["blocks"].append(("entry", e))
            continue
        if line.startswith("@"):
            raise SystemExit(f"{path.name}:{i}: unknown directive {line}")
        unit["blocks"].append(("p", line))
    return unit


def load_units():
    units = {}
    for p in sorted(DATA.glob("[0-9][0-9]-*.txt")):
        u = parse_unit(p)
        if u.get("unit") in units:
            raise SystemExit(f"duplicate unit number {u['unit']}")
        units[u["unit"]] = u
    return units


def entries_of(u):
    return [b[1] for b in u["blocks"] if b[0] == "entry"]


def vol_of_unit(un):
    for v, cfg in VOLUMES.items():
        if un in cfg["units"]:
            return v
    return None


# -------------------------------------------------------------------- checks

def check(units):
    seen, problems = {}, []
    total = feat = cmp = 0
    for un, u in sorted(units.items()):
        for k in ("title", "zh", "level"):
            if k not in u:
                problems.append(f"U{un}: missing @{k}")
        for b in u["blocks"]:
            if b[0] == "cmp":
                cmp += 1
        for e in entries_of(u):
            total += 1
            feat += e.featured
            k = head_key(e.head)
            if k in seen:
                problems.append(f"DUP '{e.head}' U{un} (line {e.line}) and U{seen[k]}")
            else:
                seen[k] = un
            if not e.pos or not e.zh:
                problems.append(f"U{un}: '{e.head}' missing pos/zh")
            for ex in filter(None, e.example.split("//")):
                ex = ex.strip()
                if not re.search(r"[.!?…”'\"]$", ex):
                    problems.append(f"U{un}: '{e.head}' example lacks final punctuation: {ex}")
                if not ex[0].isupper() and not ex[0] in "‘“'\"":
                    problems.append(f"U{un}: '{e.head}' example not capitalised: {ex}")
            for t in e.tags:
                if t not in TAGS:
                    problems.append(f"U{un}: '{e.head}' bad tag {t}")
            for fld in (e.zh, e.colloc, e.example, " ".join(e.notes)):
                if "  " in fld:
                    problems.append(f"U{un}: '{e.head}' double space")
    return problems, total, feat, cmp


# ----------------------------------------------------------------- rendering

def mark(mid):
    return f'<span class="mark">§{mid}§</span>'


def bold_head(example, rx):
    if not rx:
        return esc(example)
    out, last = [], 0
    for m in rx.finditer(example):
        out.append(esc(example[last:m.start()]))
        out.append("<b>" + esc(m.group(0)) + "</b>")
        last = m.end()
    out.append(esc(example[last:]))
    return "".join(out)


def inline(s):
    """Light Markdown for short fields (keeps * emphasis, escapes HTML)."""
    return emphasis(esc(s))


def render_entry(e):
    rx = head_regex(e.head)
    tags = "".join(f'<span class="tag {TAGS[t][1]}">{TAGS[t][0]}</span>' for t in e.tags)
    ipa = f'<span class="ipa">{esc(e.ipa)}</span>' if e.ipa else ""
    left = (f'<div class="hw-col"><span class="id">{e.unit}.{e.n}</span>'
            f'<span class="hw">{esc(e.head)}</span>{mark(f"e{e.unit}_{e.n}")}'
            f'<span class="pos">{esc(e.pos)}</span>{ipa}{tags}</div>')
    right = [f'<div class="zhdef">{inline(e.zh)}</div>']
    if e.colloc:
        cols = " · ".join(inline(c.strip()) for c in e.colloc.split(";"))
        right.append(f'<div class="col"><span class="k">搭配</span>{cols}</div>')
    if e.also:
        right.append(f'<div class="col"><span class="k">另见</span>{inline(e.also)}</div>')
    for ex in filter(None, (x.strip() for x in e.example.split("//"))):
        right.append(f'<div class="exs">{bold_head(ex, rx)}</div>')
    if e.fam:
        right.append(f'<div class="fam"><span class="k">词族</span>{inline(e.fam)}</div>')
    for nt in e.notes:
        right.append(f'<div class="note">{md_inline(nt)}</div>')
    cls = "entry featured" if e.featured else "entry"
    star = '<div class="star">★ 重点词</div>' if e.featured else ""
    return f'<div class="{cls}">{star}<div class="row">{left}<div class="body-col">{"".join(right)}</div></div></div>'


def render_cmp(title, rows, notes):
    words = [r[0] for r in rows]
    t = title or " vs. ".join(words)
    trs = "".join(
        f'<tr><td class="w">{inline(w)}</td><td>{inline(d)}</td><td class="x">{"<br>".join(inline(y.strip()) for y in x.split("//"))}</td></tr>'
        for w, d, x in rows)
    nts = "".join(f'<p>{md_inline(n)}</p>' for n in notes)
    return (f'<div class="cmp"><div class="cmp-head"><span class="label">⚖️ 易混辨析 · Compare</span>'
            f'<span class="title">{inline(t)}</span></div><table>{trs}</table>{nts}</div>')


def render_box(kind, title, body):
    icon, label = BOXES[kind]
    head = f'<span class="icon">{icon}</span><span class="label">{label}</span>'
    if title:
        head += f'<span class="title">{md_inline(title)}</span>'
    return f'<div class="box {kind}"><div class="box-head">{head}</div><div class="box-body">{md(body)}</div></div>'


def first_sense(zh):
    s = re.split(r"[；;（(]", zh)[0].strip()
    return s or zh


def make_quiz(u):
    """Two automatic review exercises per unit: gap-fill and Chinese→English recall."""
    es = entries_of(u)
    rnd = random.Random(int(hashlib.md5(str(u["unit"]).encode()).hexdigest(), 16))
    gap_cands = []
    for e in es:
        if not e.example or any(p in e.head.lower().split() for p in PLACEHOLDER):
            continue
        rx = head_regex(e.head)
        ex = e.example.split("//")[0].strip()
        m = rx.search(ex) if rx else None
        if m and len(rx.findall(ex)) == 1:
            gap_cands.append((e, ex, m))
    rnd.shuffle(gap_cands)
    gaps = gap_cands[:8]
    gaps.sort(key=lambda g: g[0].n)
    used = {g[0].n for g in gaps}
    rec = [e for e in es if e.n not in used and len(e.head) < 34]
    rnd.shuffle(rec)
    rec = sorted(rec[:8], key=lambda e: e.n)
    return gaps, rec


def hint(head):
    h = re.sub(r"\(.*?\)", "", head).strip()
    words = h.split()
    return " ".join(w[0] + "_" * (len(w) - 1) if w.lower() not in PLACEHOLDER else w for w in words)


def render_quiz(u):
    gaps, rec = make_quiz(u)
    out = ['<div class="quiz"><h2 class="notoc">Quick Review · 快速复习</h2>']
    answers = []
    if gaps:
        bank = sorted({re.sub(r"\(.*?\)", "", g[0].head).strip() for g in gaps}, key=str.lower)
        out.append('<p class="qh">A. 选词填空（注意词形变化）</p>')
        out.append('<div class="bank">' + "".join(f"<span>{esc(b)}</span>" for b in bank) + "</div><ol>")
        ans = []
        for e, ex, m in gaps:
            out.append(f"<li>{esc(ex[:m.start()])}<span class='blank'></span>{esc(ex[m.end():])}</li>")
            ans.append(m.group(0))
        out.append("</ol>")
        answers.append("A. " + " · ".join(f"{k}) {esc(a)}" for k, a in enumerate(ans, 1)))
    if rec:
        start = 1
        out.append('<p class="qh">B. 看中文，写出英文（首字母已给出）</p><ol class="two">')
        for e in rec:
            out.append(f"<li>{inline(first_sense(e.zh))}（{esc(e.pos)}）<span class='hint'>{esc(hint(e.head))}</span></li>")
        out.append("</ol>")
        answers.append("B. " + " · ".join(f"{k}) {esc(e.head)}" for k, e in enumerate(rec, start)))
    out.append("</div>")
    return "".join(out), answers


def render_unit(u, toc, hc):
    es = entries_of(u)
    feat = sum(e.featured for e in es)
    hid = f"h{u['unit']}_0"
    toc.append((1, hid, f"Unit {u['unit']} · {u['title']}", u["zh"]))
    parts = [f'<article class="unit"><div class="unit-top"><span class="unit-no">UNIT {u["unit"]:02d}</span>'
             f'<span class="level">{esc(u["level"])}</span></div>'
             f'<h1 id="{hid}">{esc(u["title"])}{mark(hid)}<small>{esc(u["zh"])}</small></h1>'
             f'<div class="stats">本单元 {len(es)} 个词条 · ★ 重点 {feat} 个</div>']
    if u.get("intro"):
        parts.append(f'<div class="intro">{md_inline(u["intro"])}</div>')
    sec = 0
    for b in u["blocks"]:
        if b[0] == "h2":
            sec += 1
            sid = f"h{u['unit']}_{sec}"
            toc.append((2, sid, b[1], ""))
            parts.append(f'<h2 id="{sid}">{inline(b[1])}{mark(sid)}</h2>')
        elif b[0] == "entry":
            parts.append(render_entry(b[1]))
        elif b[0] == "cmp":
            parts.append(render_cmp(*b[1:]))
        elif b[0] == "box":
            parts.append(render_box(*b[1:]))
        elif b[0] == "p":
            parts.append(f"<p>{md_inline(b[1])}</p>")
    qhtml, answers = render_quiz(u)
    parts.append(qhtml)
    parts.append("</article>")
    return "".join(parts), answers


def fonts_links():
    fonts = ["source-serif-4/400.css", "source-serif-4/400-italic.css", "source-serif-4/600.css",
             "source-serif-4/700.css", "source-serif-4/600-italic.css",
             "inter/400.css", "inter/500.css", "inter/600.css", "inter/700.css", "inter/800.css",
             "noto-sans-sc/400.css", "noto-sans-sc/500.css", "noto-sans-sc/700.css",
             "noto-serif-sc/400.css", "noto-serif-sc/700.css"]
    return "".join(f'<link rel="stylesheet" href="../../node_modules/@fontsource/{p}">' for p in fonts)


def cover(v):
    cfg = VOLUMES[v]
    steps = "".join(
        f'<span class="{"on" if k == v else ""}">{VOLUMES[k]["roman"]} {VOLUMES[k]["zh"]}</span>'
        for k in VOLUMES)
    return f"""<section class="cover" style="--c:{cfg['colour']};--a:{cfg['accent']}">
  <div class="bar"></div>
  <div class="kicker">{SERIES} · Volume {v} of 5</div>
  <div class="ctitle">{esc(cfg['title'])}</div>
  <div class="czh">{SERIES_ZH}<br>第{"一二三四五"[v-1]}册 · {cfg['zh']}</div>
  <div class="clevel">{cfg['level']}</div>
  <div class="cscope">{cfg['scope']}</div>
  <div class="big">{cfg['roman']}</div>
  <div class="path">{steps}</div>
  <div class="foot">For Shenzhen junior-high learners aiming at IELTS Academic · 面向深圳初中生的长期词汇路线<br>
  词汇是主线 · 解释是辅助 · 例句让知识落地</div>
</section>"""


def toc_html(toc, pages, title="目录 · Contents"):
    rows = []
    for level, hid, text, zh in toc:
        p = pages.get(hid, "")
        cls = {0: "toc-part", 1: "toc-ch", 2: "toc-sec"}[level]
        z = f' <span class="tz">{esc(zh)}</span>' if zh else ""
        rows.append(f'<a class="{cls}" href="#{hid}"><span class="t">{inline(text)}{z}</span>'
                    f'<span class="dots"></span><span class="p">{p}</span></a>')
    return f'<article class="toc"><h1 class="plain">{title}</h1>{"".join(rows)}</article>'


def legend_html():
    sample = Entry(head="significant", pos="adj.", zh="重要的；显著的；（数量）相当大的",
                   colloc="a significant increase; play a significant role in",
                   example="There has been a significant rise in online shopping.",
                   tags=["W"], featured=False, ipa="/sɪɡˈnɪfɪkənt/",
                   fam="significance (n.) · significantly (adv.) · insignificant (adj.)",
                   notes=[], also="", unit=0, n=0)
    return render_entry(sample).replace('<span class="mark">§e0_0§</span>', "")


def series_table(units):
    rows = []
    for v, cfg in VOLUMES.items():
        if v == 5:
            rows.append(f"<tr><td>{cfg['roman']}</td><td>{cfg['zh']}<br><small>{cfg['title']}</small></td>"
                        f"<td>—</td><td>—</td><td>{cfg['scope']}</td></tr>")
            continue
        us = [units[k] for k in cfg["units"] if k in units]
        n = sum(len(entries_of(u)) for u in us)
        rows.append(f"<tr><td>{cfg['roman']}</td><td>{cfg['zh']}<br><small>{cfg['title']}</small></td>"
                    f"<td>{cfg['level']}</td><td>Unit {min(cfg['units'])}–{max(cfg['units'])}<br>{n} 词条</td>"
                    f"<td>{cfg['scope']}</td></tr>")
    return ('<table class="series"><thead><tr><th>册</th><th>名称</th><th>难度</th><th>范围</th><th>内容</th></tr></thead>'
            + "".join(rows) + "</table>")


def front_matter(v, units):
    path = DATA / f"vol{v}-intro.md"
    intro = md(path.read_text(encoding="utf-8")) if path.exists() else ""
    total = sum(len(entries_of(u)) for u in units.values())
    return (f'<article class="front"><h1 class="plain">关于本册 · About this volume</h1>{intro}'
            f'<h2 class="notoc">全套结构 · The series</h2><p>全套共 5 册，四册正文共 {total} 个去重词条（派生词放在“词族”中，不重复计数），第 5 册为总索引与复习手册。</p>'
            f'{series_table(units)}'
            f'<h2 class="notoc">怎么读一个词条 · How to read an entry</h2>{legend_html()}'
            '<ul class="legend"><li><b>编号</b>：27.3 = 第 27 单元第 3 个词条。全套编号统一，索引都用这个编号。</li>'
            '<li><b>★ 重点词</b>：多义、易错、搭配关键或能带出一个词族的词，附有简短讲解。其余词条只给最必要的信息。</li>'
            '<li><b>搭配</b>：优先整块记忆的表达。<b>词族</b>：值得一起掌握的派生词（不单独计数）。</li>'
            '<li><span class="tag tag-s">口语</span> 适合自然口语使用；<span class="tag tag-w">写作</span> 偏正式，适合学术写作，日常聊天少用。没有标签的词两种场合都常见。</li>'
            '<li>音标采用英式发音（DJ/IPA 体系），只在读音容易出错或重音会变化时标注。</li>'
            '<li>例句中加粗的部分就是本词条的词或表达。每单元最后有 <b>Quick Review</b>，答案在本册末尾。</li></ul>'
            '</article>')


def volume_index(v, units, pages):
    items = []
    for un in VOLUMES[v]["units"]:
        if un not in units:
            continue
        for e in entries_of(units[un]):
            items.append((sort_key(e.head), e))
    items.sort(key=lambda x: (x[0], x[1].head))
    rows, letter = [], ""
    for k, e in items:
        L = (k[:1] or "#").upper()
        if L != letter:
            letter = L
            rows.append(f'<div class="ix-letter">{L}</div>')
        p = pages.get(f"e{e.unit}_{e.n}", "")
        rows.append(f'<div class="ix"><span class="w">{esc(e.head)}</span><span class="z">{inline(first_sense(e.zh))}</span>'
                    f'<span class="d"></span><span class="r">{e.unit}.{e.n}{" · p" + str(p) if p else ""}</span></div>')
    return "".join(rows)


def build_volume(v, units, pages):
    cfg = VOLUMES[v]
    toc, body, answer_blocks = [], [], []
    hc = [0]
    vunits = {k: units[k] for k in cfg["units"] if k in units}
    for un, u in vunits.items():
        h, ans = render_unit(u, toc, hc)
        body.append(h)
        answer_blocks.append((u, ans))
    # answer key
    toc.append((1, "hak", "Answer Key · 快速复习答案", ""))
    ak = ['<article class="appendix answers"><h1 id="hak">Answer Key' + mark("hak") + '<small>快速复习答案</small></h1>']
    for u, ans in answer_blocks:
        ak.append(f'<div class="ak"><b>Unit {u["unit"]} · {esc(u["title"])}</b><br>' + "<br>".join(ans) + "</div>")
    ak.append("</article>")
    body.append("".join(ak))
    toc.append((1, "hix", "Index · 本册词条索引", ""))
    body.append('<article class="appendix"><h1 id="hix">Index' + mark("hix") +
                '<small>本册词条索引（按字母排序 · 编号 · 页码）</small></h1>'
                f'<div class="index">{volume_index(v, units, pages)}</div></article>')
    return wrap(v, cover(v) + front_matter(v, units) + toc_html(toc, pages) + "".join(body))


def wrap(v, inner):
    css = (ROOT / "tools" / "style.css").read_text(encoding="utf-8")
    cfg = VOLUMES[v]
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f"<title>{SERIES} · Vol. {v} · {cfg['title']}</title>{fonts_links()}"
            f"<style>:root{{--vc:{cfg['colour']};--va:{cfg['accent']};}}{css}</style></head>"
            f"<body>{inner}</body></html>")


# ------------------------------------------------------- volume 5 (handbook)

def handbook(units, pages_by_vol):
    from handbook import build_handbook  # noqa: E402  (kept in a separate file)
    return build_handbook(sys.modules[__name__], units, pages_by_vol)


def main():
    units = load_units()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    problems, total, feat, cmp = check(units)
    if cmd == "check":
        for p in problems:
            print(p)
        for v, cfg in VOLUMES.items():
            us = [units[k] for k in cfg["units"] if k in units]
            print(f"Vol {v}: {len(us)} units, {sum(len(entries_of(u)) for u in us)} entries")
        for un, u in sorted(units.items()):
            es = entries_of(u)
            print(f"  U{un:02d} {u['title'][:40]:40s} {len(es):3d} entries, {sum(e.featured for e in es):2d} featured")
        print(f"TOTAL {total} entries, {feat} featured, {cmp} compare boxes, {len(problems)} problems")
        return
    if problems:
        for p in problems:
            print(p)
        raise SystemExit("fix data problems first")
    v = int(sys.argv[2])
    OUT.mkdir(exist_ok=True)
    pf = OUT / f"vol{v}.pages.json"
    pages = json.loads(pf.read_text()) if pf.exists() else {}
    if v == 5:
        pbv = {}
        for k in range(1, 5):
            f = OUT / f"vol{k}.pages.json"
            pbv[k] = json.loads(f.read_text()) if f.exists() else {}
        pbv[5] = pages
        doc = handbook(units, pbv)
    else:
        doc = build_volume(v, units, pages)
    (OUT / f"vol{v}.html").write_text(doc, encoding="utf-8")
    print(f"wrote build/vol{v}.html")


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    main()
