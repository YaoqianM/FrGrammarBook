#!/usr/bin/env python3
"""THE FRENCH WORLD — build build/book.html + registries + deliverables from src/*.fw.

See docs/PLAN.md §6 for the source format. Run tools/make.sh for the full two-pass build.
"""
import csv
import html
import json
import pathlib
import re
import sys
import unicodedata
from collections import Counter, defaultdict, OrderedDict

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "build"
DELIV = ROOT / "deliverables"
PAGES = OUT / "pages.json"

LEVELS = ["A1", "A2", "B1", "B2", "C1"]

KINDS = OrderedDict([
    # kind: (FR label, ZH label, icon, new page?)
    ("ouverture", ("L'OUVERTURE", "开篇三部曲", "star", True)),
    ("guide", ("MODE D'EMPLOI", "使用指南", "pen", True)),
    ("edito", ("ÉDITO", "编者的话", "pen", False)),
    ("serial", ("FEUILLETON", "连载故事", "book", True)),
    ("histoire", ("HISTOIRES", "故事", "cup", True)),
    ("vie", ("VIE QUOTIDIENNE", "日常生活", "key", True)),
    ("humour", ("HUMOUR & CULTURE", "幽默与文化", "smile", False)),
    ("amour", ("AMOUR & RELATIONS", "爱情与关系", "heart", False)),
    ("phrases", ("BELLES PHRASES", "金句", "spark", False)),
    ("plateau", ("LE PLATEAU", "脱口秀", "mic", True)),
    ("debat", ("LE DÉBAT", "辩论", "scale", True)),
    ("idees", ("IDÉES QUI DÉRANGENT", "颠覆性观点", "bolt", False)),
    ("psycho", ("PSYCHOLOGIE", "心理学", "spiral", False)),
    ("philo", ("PHILOSOPHIE & IDÉES", "哲学与思想", "lamp", False)),
    ("cine", ("CINÉ-PHILO", "电影里的哲学", "film", False)),
    ("science", ("SCIENCE & MONDE MODERNE", "科学与现代世界", "atom", False)),
    ("poesie", ("POÉSIE & LITTÉRATURE", "诗歌与文学", "feather", False)),
    ("expr", ("EXPRESSIONS & CONVERSATION", "地道表达", "bubble", False)),
    ("grammaire", ("GRAMMAIRE", "语法", "gear", False)),
    ("tcf", ("TCF CANADA", "TCF 加拿大", "leaf", True)),
])

NOTE_KINDS = {
    "culture": ("CULTURE", "文化", "gold"),
    "quebec": ("⚜ AU QUÉBEC", "在魁北克", "blue"),
    "slang": ("⚠ ATTENTION, FAMILIER", "俚语警告", "orange"),
    "think": ("PENSER EN FRANÇAIS", "法语思维", "gold"),
    "funny": ("POURQUOI C'EST DRÔLE", "笑点在哪里", "orange"),
    "tip": ("ASTUCE", "窍门", "blue"),
    "warn": ("PIÈGE", "常见错误", "orange"),
    "idea": ("À MÉDITER", "想一想", "gold"),
    "source": ("SOURCE", "出处", "grey"),
    "cn": ("POUR LES SINOPHONES", "写给中文母语者", "gold"),
}

ICONS = {
    "star": '<path d="M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6L12 16.6 6.6 19.5l1.2-6L3.3 9.3l6.1-.7z"/>',
    "pen": '<path d="M4 20l4-1 11-11-3-3L5 16z"/><path d="M14 6l3 3"/>',
    "book": '<path d="M3 5.5C5.5 4.5 8.5 4.5 12 6.5c3.5-2 6.5-2 9-1V19c-2.5-1-5.5-1-9 1-3.5-2-6.5-2-9-1z"/><path d="M12 6.5V20"/>',
    "cup": '<path d="M4 9h12v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z"/><path d="M16 10h1.5a2.5 2.5 0 0 1 0 5H16"/><path d="M8 3.5c-.8 1 .8 2-.1 3M12 3.5c-.8 1 .8 2-.1 3"/>',
    "key": '<circle cx="8" cy="12" r="4"/><path d="M12 12h9M18 12v3M21 12v2"/>',
    "smile": '<circle cx="12" cy="12" r="9"/><path d="M8 14.5c2 2.2 6 2.2 8 0"/><path d="M9 9.5h.01M15 9.5h.01"/>',
    "heart": '<path d="M12 20s-7.5-4.6-7.5-10A4.3 4.3 0 0 1 12 7.2 4.3 4.3 0 0 1 19.5 10c0 5.4-7.5 10-7.5 10z"/>',
    "spark": '<path d="M12 3v5M12 16v5M3 12h5M16 12h5M6 6l3 3M15 15l3 3M18 6l-3 3M9 15l-3 3"/>',
    "mic": '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21M8.5 21h7"/>',
    "scale": '<path d="M12 4v16M7 20h10M5 7h14"/><path d="M5 7l-3 6a3 3 0 0 0 6 0zM19 7l-3 6a3 3 0 0 0 6 0z"/>',
    "bolt": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    "spiral": '<path d="M12 12a1.5 1.5 0 1 1 1.5 1.5A3 3 0 1 1 15 10.5a4.5 4.5 0 1 1-4.5-4.5A6 6 0 1 1 6 12"/>',
    "lamp": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
    "film": '<rect x="3" y="8" width="18" height="12" rx="1.5"/><path d="M3 8l2.5-4.5L21 8M8 5.5l2 3.5M13 4.8l2 3.6"/>',
    "atom": '<ellipse cx="12" cy="12" rx="9.5" ry="3.8"/><ellipse cx="12" cy="12" rx="9.5" ry="3.8" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="9.5" ry="3.8" transform="rotate(120 12 12)"/>',
    "feather": '<path d="M20 4C11 4 6 9 5 19l3-3h5c4-1 7-6 7-12z"/><path d="M5 19L14 10"/>',
    "bubble": '<path d="M4 5h16v10H9l-5 4z"/>',
    "gear": '<path d="M4 18L9.5 5h1L16 18M6.3 13h7.4"/><path d="M17 12.5c0-1.4 1-2.5 2.2-2.5S21.5 11 21.5 12.5V18M21.5 15c-1.2-.8-4.5-.8-4.5 1.3 0 1 .8 1.7 2 1.7 1.3 0 2.5-.8 2.5-2.5"/>',
    "leaf": '<path d="M12 21v-5M12 16l-6 1 1.5-2.5L3 11l2-.5L4 7l3 1.5L8 6l2 3 .5-5L12 2l1.5 2 .5 5 2-3 1 2.5L20 7l-1 3.5 2 .5-4.5 3.5L18 17z"/>',
}


def icon(name, cls="ic"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')


# ───────────────────────── text helpers ─────────────────────────

STRONG = re.compile(r"\*\*(?!\*)(?=\S)(.+?)(?<=[^\s*])\*\*")
EM = re.compile(r"(?<![\*\w])\*(?=[^\s*])(.+?)(?<=[^\s*])\*(?![\*\w])")


def emphasis(text):
    out, in_code = [], False
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            in_code = not in_code
        elif not in_code:
            line = STRONG.sub(r"<strong>\1</strong>", line)
            line = EM.sub(r"<em>\1</em>", line)
        out.append(line)
    return "\n".join(out)


def inline(text):
    """Escape + **bold** / *italic* + ==highlight== for short strings (rows, cells)."""
    t = html.escape(text.strip(), quote=False)
    t = STRONG.sub(r"<strong>\1</strong>", t)
    t = EM.sub(r"<em>\1</em>", t)
    t = re.sub(r"==(.+?)==", r'<mark>\1</mark>', t)
    t = t.replace(" // ", "<br>")
    return t


MD_EXT = ["tables", "sane_lists", "md_in_html", "attr_list"]


def md(text):
    text = expand_examples(text)
    return markdown.markdown(emphasis(text), extensions=MD_EXT)


def expand_examples(text):
    """`= FR || ZH` lines inside Markdown bodies → example rows (raw HTML)."""
    out, buf = [], []

    def flush():
        if buf:
            out.append("\n" + '<div class="exs">' + "".join(buf) + "</div>\n")
            buf.clear()

    for line in text.split("\n"):
        m = re.match(r"^\s*=\s+(.*)$", line)
        if m:
            parts = [p.strip() for p in m.group(1).split(" || ")]
            fr = parts[0]
            zh = parts[1] if len(parts) > 1 else ""
            en = parts[2] if len(parts) > 2 else ""
            cls = "ex"
            if fr.startswith("✗"):
                cls += " bad"
            elif fr.startswith("✓"):
                cls += " good"
            g = f'<span class="z">{inline(zh)}</span>' if zh else ""
            if en:
                g += f'<span class="e">{inline(en)}</span>'
            buf.append(f'<div class="{cls}"><span class="f">{inline(fr)}</span>{g}</div>')
        else:
            flush()
            out.append(line)
    flush()
    return "\n".join(out)


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def norm(word):
    w = word.lower().strip()
    w = re.sub(r"^(le |la |les |l'|un |une |des |se |s'|~)", "", w)
    return w.strip()


def sort_key(word):
    w = norm(word)
    w = unicodedata.normalize("NFD", w)
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", "", w)


# ───────────────────────── data model ─────────────────────────

class Issue:
    def __init__(self, num, level, title, title_zh, tag_fr="", tag_zh=""):
        self.num, self.level, self.title, self.title_zh = num, level, title, title_zh
        self.tag_fr, self.tag_zh = tag_fr, tag_zh
        self.pieces, self.badges = [], []
        self.id = f"i{num}"


class Piece:
    def __init__(self, kind, title, title_zh, level, issue, opts=""):
        if kind not in KINDS:
            sys.exit(f"unknown piece kind: {kind}")
        self.kind, self.title, self.title_zh, self.level = kind, title, title_zh, level
        self.issue, self.opts = issue, opts
        self.deck = None
        self.meta = {}
        self.blocks = []
        self.answers = []
        self.id = None


class Ctx:
    def __init__(self):
        self.issues = []
        self.front = []          # pieces before the first @issue
        self.cast = {}
        self.vocab = []          # dicts
        self.expr = []
        self.grammar = []
        self.errors = []


def parse(ctx):
    files = sorted(SRC.glob("*.fw"))
    issue = None
    piece = None
    for f in files:
        lines = f.read_text(encoding="utf-8").split("\n")
        i = 0
        while i < len(lines):
            raw = lines[i]
            line = raw.rstrip()
            loc = f"{f.name}:{i+1}"
            i += 1
            if line.startswith("%%"):           # comment
                continue
            if not line.strip():
                if piece is not None:
                    piece.blocks.append(("gap",))
                continue
            m = re.match(r"^@(\w+)\s*(.*)$", line)
            if m:
                d, arg = m.group(1), m.group(2).strip()
                block_dirs = {"vocab", "expr", "grammar", "note", "compare", "versions", "poem",
                              "q", "a", "speak", "md", "ex", "dialogue", "rappel"}
                if d in block_dirs:
                    body = []
                    while i < len(lines) and lines[i].strip() != "@end":
                        body.append(lines[i].rstrip())
                        i += 1
                    if i >= len(lines):
                        ctx.errors.append(f"{loc}: @{d} without @end")
                    i += 1
                    if piece is None:
                        ctx.errors.append(f"{loc}: @{d} outside a piece")
                        continue
                    if d == "a":
                        piece.answers.append("\n".join(body))
                    else:
                        piece.blocks.append((d, arg, body, loc))
                    continue
                if d == "issue":
                    p = split_fields(arg)
                    tag = p[4] if len(p) > 4 else ""
                    tf, tz = (tag.split(" || ") + [""])[:2] if tag else ("", "")
                    issue = Issue(p[0], p[1], p[2], p[3], tf, tz)
                    ctx.issues.append(issue)
                    piece = None
                elif d == "cast":
                    for kv in arg.split(","):
                        if "=" in kv:
                            k, v = kv.split("=", 1)
                            ctx.cast[k.strip()] = v.strip()
                elif d == "piece":
                    p = split_fields(arg)
                    while len(p) < 5:
                        p.append("")
                    lvl = p[3] or (issue.level if issue else "A1")
                    piece = Piece(p[0], p[1], p[2], lvl, issue, p[4])
                    (issue.pieces if issue else ctx.front).append(piece)
                elif d == "deck":
                    piece.deck = [x.strip() for x in arg.split(" || ")]
                elif d == "meta":
                    for kv in arg.split(";"):
                        if "=" in kv:
                            k, v = kv.split("=", 1)
                            piece.meta[k.strip()] = [x.strip() for x in v.split(",") if x.strip()]
                elif d == "part":
                    p = split_fields(arg)
                    while len(p) < 3:
                        p.append("")
                    piece.blocks.append(("part", p[0], p[1], p[2]))
                elif d == "quote":
                    p = [x.strip() for x in arg.split(" || ")]
                    while len(p) < 3:
                        p.append("")
                    piece.blocks.append(("quote", p[0], p[1], p[2]))
                elif d == "badge":
                    p = [x.strip() for x in arg.split(" || ")]
                    while len(p) < 3:
                        p.append("")
                    issue.badges.append(p)
                elif d == "break":
                    piece.blocks.append(("break",))
                elif d == "h":
                    p = [x.strip() for x in arg.split(" || ")]
                    piece.blocks.append(("h", p[0], p[1] if len(p) > 1 else ""))
                else:
                    ctx.errors.append(f"{loc}: unknown directive @{d}")
                continue
            if " || " in line:
                if piece is None:
                    ctx.errors.append(f"{loc}: row outside a piece")
                    continue
                parts = [x.strip() for x in line.split(" || ")]
                fr, zh = parts[0], parts[1] if len(parts) > 1 else ""
                if not zh:
                    ctx.errors.append(f"{loc}: missing Chinese: {fr[:50]}")
                sp = None
                ms = re.match(r"^\[([^\]]+)\]\s*(.*)$", fr)
                if ms:
                    sp, fr = ms.group(1), ms.group(2)
                    mz = re.match(r"^\[([^\]]+)\]\s*(.*)$", zh)
                    if mz:
                        zh = mz.group(2)
                piece.blocks.append(("row", fr, zh, sp, loc))
                continue
            if piece is not None:
                piece.blocks.append(("text", line, loc))
            else:
                ctx.errors.append(f"{loc}: stray text: {line[:60]}")


# ───────────────────────── rendering ─────────────────────────

class Renderer:
    def __init__(self, ctx, pages):
        self.ctx, self.pages = ctx, pages
        self.n_marker = 0
        self.vocab_seen = {}     # norm -> vocab dict
        self.dupes = []

    def mark(self, mid):
        return f'<span class="mk">§{mid}§</span>'

    def page(self, mid):
        return self.pages.get(mid, "")

    # ── piece header ──
    def header(self, p):
        fr, zh, ic, _ = KINDS[p.kind]
        lvl = f'<span class="lvl lvl-{p.level[:2]}">{html.escape(p.level)}</span>' if p.level else ""
        deck = ""
        if p.deck:
            deck = (f'<div class="deck"><div class="deck-fr">{inline(p.deck[0])}</div>'
                    + (f'<div class="deck-zh">{inline(p.deck[1])}</div>' if len(p.deck) > 1 else "")
                    + "</div>")
        big = "big" if KINDS[p.kind][3] or "big" in p.opts else "small"
        return (f'<header class="ph {big}"><div class="kicker k-{p.kind}">{icon(ic)}'
                f'<span>{fr}</span><span class="kz">{zh}</span>{lvl}</div>'
                f'<h2 id="{p.id}" class="pt">{inline(p.title)}{self.mark(p.id)}</h2>'
                f'<div class="ptz">{html.escape(p.title_zh)}</div>{deck}</header>')

    # ── blocks ──
    def render_piece(self, p):
        out = [self.header(p)]
        rows_buf = []
        n = 0
        kwforms = self.keyword_patterns(p)
        kwdone = set()
        self.cur_lvl = p.level[:2] if p.level[:2] in LEVELS else (p.issue.level if p.issue else "A1")

        def flush_rows():
            if rows_buf:
                out.append('<div class="bi">' + "".join(rows_buf) + "</div>")
                rows_buf.clear()

        pending_gap = False
        for b in p.blocks:
            t = b[0]
            if t == "gap":
                if rows_buf:
                    pending_gap = True
                continue
            if t == "row":
                n += 1
                _, fr, zh, sp, loc = b
                frh = self.highlight(inline(fr), kwforms, kwdone)
                spk = spz = ""
                if sp:
                    spk = f'<span class="sp">{html.escape(sp)}</span>'
                    spz = f'<span class="sp">{html.escape(self.ctx.cast.get(sp, sp))}</span>'
                gapc = " gap" if pending_gap else ""
                pending_gap = False
                rows_buf.append(f'<div class="r{gapc}"><span class="n">{n}</span>'
                                f'<div class="fr">{spk}{frh}</div><div class="zh">{spz}{inline(zh)}</div></div>')
                continue
            flush_rows()
            pending_gap = False
            if t == "part":
                _, lvl, title, zh = b
                if lvl[:2] in LEVELS:
                    self.cur_lvl = lvl[:2]
                pid = f"{p.id}-pt{len(out)}"
                out.append(f'<div class="part"><span class="lvl lvl-{lvl[:2]}">{html.escape(lvl)}</span>'
                           f'<h3 id="{pid}">{inline(title)}</h3><div class="partz">{html.escape(zh)}</div></div>')
            elif t == "h":
                out.append(f'<div class="subh"><span class="shf">{inline(b[1])}</span>'
                           f'<span class="shz">{inline(b[2])}</span></div>')
            elif t == "break":
                out.append('<div class="pb"></div>')
            elif t == "quote":
                _, fr, zh, src = b
                out.append(f'<blockquote class="pull"><div class="qf">{inline(fr)}</div>'
                           f'<div class="qz">{inline(zh)}</div>'
                           + (f'<div class="qs">— {inline(src)}</div>' if src else "") + "</blockquote>")
            elif t == "text":
                out.append(f'<p class="plain">{inline(b[1])}</p>')
            else:
                _, arg, body, loc = b
                out.append(getattr(self, "b_" + t)(p, arg, body, loc))
        flush_rows()
        if p.answers:
            out.append(f'<div class="see-ans">Corrigé · 答案 → <a href="#ans-{p.id}">p. {self.page("ans-" + p.id)}</a></div>')
        cls = f"piece k-{p.kind}" + (" np" if KINDS[p.kind][3] or "np" in p.opts else "")
        return f'<article class="{cls}">' + "".join(out) + "</article>"

    def keyword_patterns(self, p):
        pats = []
        for b in p.blocks:
            if b[0] != "vocab":
                continue
            for line in b[2]:
                if not line.strip() or line.startswith("%%"):
                    continue
                w = line.split(" | ")[0].strip().lstrip("~")
                pats.append(word_regex(w))
        return [x for x in pats if x]

    def highlight(self, h, pats, done):
        # first occurrence of each vocab item in the piece, outside tags
        for idx, pat in enumerate(pats):
            if idx in done:
                continue
            parts = re.split(r"(<[^>]+>)", h)
            for k, seg in enumerate(parts):
                if seg.startswith("<"):
                    continue
                m = pat.search(seg)
                if m:
                    parts[k] = seg[:m.start()] + f'<span class="kw">{m.group(0)}</span>' + seg[m.end():]
                    h = "".join(parts)
                    done.add(idx)
                    break
        return h

    def b_vocab(self, p, arg, body, loc):
        cards = []
        cnt = 0
        for line in body:
            if not line.strip() or line.startswith("%%"):
                continue
            f = split_fields(line)
            if len(f) < 6:
                self.ctx.errors.append(f"{loc}: vocab needs ≥6 fields: {line[:60]}")
                continue
            while len(f) < 10:
                f.append("")
            word, pos, ipa, zh, en, ex, exzh, col, fam, note = f[:10]
            review = word.startswith("~")
            word = word.lstrip("~")
            key = norm(word) + "|" + pos.split()[0] if pos else norm(word)
            vid = f"v{len(self.ctx.vocab) + 1}"
            pclass = re.split(r"[.\s/]", pos.strip())[0] if pos else ""
            vkey = norm(word) + "|" + pclass
            prev = self.vocab_seen.get(vkey)
            if prev and not review:
                self.dupes.append((word, prev["where"], f"{p.issue.num if p.issue else 0}:{p.title}", loc))
            entry = dict(id=vid, word=word, pos=pos, ipa=ipa, zh=zh, en=en, ex=ex, exzh=exzh, col=col,
                         fam=fam, note=note, level=self.cur_lvl, piece=p, review=review,
                         where=f"N°{p.issue.num if p.issue else 0} {p.title}",
                         topics=p.meta.get("topics", []))
            if not review:
                self.vocab_seen.setdefault(vkey, entry)
                cnt += 1
            self.ctx.vocab.append(entry)
            ipa_h = f'<span class="ipa">/{html.escape(ipa)}/</span>' if ipa else ""
            lines = [f'<div class="vw"><span class="w">{inline(word)}</span> <span class="pos">{html.escape(pos)}</span> {ipa_h}</div>',
                     f'<div class="vm"><span class="vz">{inline(zh)}</span>'
                     + (f' <span class="ve">{inline(en)}</span>' if en else "") + "</div>"]
            if ex:
                lines.append(f'<div class="vx">{inline(ex)}' + (f' <span class="vxz">{inline(exzh)}</span>' if exzh else "") + "</div>")
            extra = []
            if col:
                extra.append(f'<span class="lab">＋</span>{inline(col)}')
            if fam:
                extra.append(f'<span class="lab">⟡</span>{inline(fam)}')
            if extra:
                lines.append('<div class="vc">' + " ".join(extra) + "</div>")
            if note:
                lines.append(f'<div class="vn">{inline(note)}</div>')
            rv = " rv" if review else ""
            cards.append(f'<div class="vcard{rv}" id="{vid}">{self.mark(vid)}' + "".join(lines) + "</div>")
        title = arg or "Vocabulaire"
        return (f'<section class="vocab"><div class="bh">{icon("book")}<span>{inline(title)}</span>'
                f'<span class="kz">词汇</span><span class="cnt">{cnt} mots</span></div>'
                f'<div class="vgrid">' + "".join(cards) + "</div></section>")

    def b_expr(self, p, arg, body, loc):
        rows = []
        for line in body:
            if not line.strip() or line.startswith("%%"):
                continue
            f = split_fields(line)
            while len(f) < 5:
                f.append("")
            ex, zh, reg, use, sample = f[:5]
            sfr, szh = (sample.split(" || ") + [""])[:2] if sample else ("", "")
            eid = f"e{len(self.ctx.expr) + 1}"
            self.ctx.expr.append(dict(id=eid, expr=ex, zh=zh, reg=reg, use=use, ex=sfr, exzh=szh,
                                      level=self.cur_lvl, where=f"N°{p.issue.num if p.issue else 0} {p.title}",
                                      piece=p))
            regc = reg_class(reg)
            rows.append(f'<div class="xr" id="{eid}">{self.mark(eid)}<div class="xh"><span class="xe">{inline(ex)}</span>'
                        f'<span class="reg {regc}">{html.escape(reg)}</span></div>'
                        f'<div class="xz">{inline(zh)}</div>'
                        + (f'<div class="xu">{inline(use)}</div>' if use else "")
                        + (f'<div class="xs"><span class="f">{inline(sfr)}</span> <span class="z">{inline(szh)}</span></div>' if sfr else "")
                        + "</div>")
        title = arg or "Expressions"
        return (f'<section class="expr"><div class="bh">{icon("bubble")}<span>{inline(title)}</span>'
                f'<span class="kz">地道表达</span></div>' + "".join(rows) + "</section>")

    def b_grammar(self, p, arg, body, loc):
        f = split_fields(arg)
        while len(f) < 4:
            f.append("")
        title, zh, lvl, key = f[:4]
        gid = f"g{len(self.ctx.grammar) + 1}"
        self.ctx.grammar.append(dict(id=gid, title=title, zh=zh, level=lvl or p.level[:2], key=key, piece=p,
                                     where=f"N°{p.issue.num if p.issue else 0}"))
        return (f'<section class="gram" id="{gid}">{self.mark(gid)}<div class="gh">{icon("gear")}<span class="gl">GRAMMAIRE · 语法</span>'
                f'<span class="lvl lvl-{(lvl or p.level)[:2]}">{html.escape(lvl or p.level)}</span></div>'
                f'<div class="gt">{inline(title)}</div><div class="gz">{html.escape(zh)}</div>'
                f'<div class="gb">{md(chr(10).join(body))}</div></section>')

    def b_rappel(self, p, arg, body, loc):
        f = split_fields(arg)
        while len(f) < 4:
            f.append("")
        title, zh, lvl, ch = f[:4]
        gid = f"g{len(self.ctx.grammar) + 1}"
        self.ctx.grammar.append(dict(id=gid, title=title, zh=zh, level=(lvl or p.level)[:2], key=ch, piece=p,
                                     where=f"N°{p.issue.num if p.issue else 0}"))
        ref = f'<span class="gref">→ Grammaire, ch. {html.escape(ch)}</span>' if ch else ""
        return (f'<aside class="rappel" id="{gid}">{self.mark(gid)}<div class="rh"><span class="rl">RAPPEL · 语法小贴士</span>{ref}</div>'
                f'<div class="rt">{inline(title)} <span class="rz">{html.escape(zh)}</span></div>'
                f'<div class="rb">{md(chr(10).join(body))}</div></aside>')

    def b_note(self, p, arg, body, loc):
        f = split_fields(arg)
        kind = f[0]
        title = f[1] if len(f) > 1 else ""
        lab, zh, color = NOTE_KINDS.get(kind, ("NOTE", "注", "grey"))
        return (f'<aside class="note c-{color}"><div class="nh"><span>{lab}</span><span class="kz">{zh}</span></div>'
                + (f'<div class="nt">{inline(title)}</div>' if title else "")
                + f'<div class="nb">{md(chr(10).join(body))}</div></aside>')

    def b_compare(self, p, arg, body, loc):
        rows = []
        for line in body:
            if not line.strip():
                continue
            c = [x.strip() for x in line.split(" || ")]
            while len(c) < 3:
                c.append("")
            rows.append(f'<div class="cr"><div class="cf">{inline(c[0])}</div><div class="cz">{inline(c[1])}</div>'
                        f'<div class="cn">{inline(c[2])}</div></div>')
        return (f'<section class="compare"><div class="bh">{icon("scale")}<span>{inline(arg or "Comparez")}</span>'
                f'<span class="kz">比较</span></div>' + "".join(rows) + "</section>")

    def b_versions(self, p, arg, body, loc):
        rows = []
        for line in body:
            if not line.strip():
                continue
            c = [x.strip() for x in line.split(" || ")]
            while len(c) < 4:
                c.append("")
            regc = reg_class(c[0])
            rows.append(f'<div class="vr"><div class="vreg"><span class="reg {regc}">{inline(c[0])}</span></div>'
                        f'<div class="vfr">{inline(c[1])}</div><div class="vzh">{inline(c[2])}</div>'
                        + (f'<div class="vwhen">{inline(c[3])}</div>' if c[3] else "") + "</div>")
        return (f'<section class="versions"><div class="bh">{icon("spark")}<span>{inline(arg or "Cinq façons de le dire")}</span>'
                f'<span class="kz">不同说法</span></div>' + "".join(rows) + "</section>")

    def b_poem(self, p, arg, body, loc):
        f = split_fields(arg)
        title = f[0]
        author = f[1] if len(f) > 1 else ""
        out = []
        stanza = []

        def flush():
            if stanza:
                out.append('<div class="stanza">' + "".join(stanza) + "</div>")
                stanza.clear()

        for line in body:
            if not line.strip():
                flush()
                continue
            c = [x.strip() for x in line.split(" || ")]
            stanza.append(f'<div class="vl"><span class="pf">{inline(c[0])}</span>'
                          f'<span class="pz">{inline(c[1]) if len(c) > 1 else ""}</span></div>')
        flush()
        head = (f'<div class="poem-t">{inline(title)}</div>' if title else "") + \
               (f'<div class="poem-a">{inline(author)}</div>' if author else "")
        return f'<section class="poem">{head}' + "".join(out) + "</section>"

    def b_q(self, p, arg, body, loc):
        return (f'<section class="qbox"><div class="bh">{icon("pen")}<span>{inline(arg or "À vous !")}</span>'
                f'<span class="kz">练习</span></div><div class="qb">{md(chr(10).join(body))}</div></section>')

    def b_ex(self, p, arg, body, loc):
        return self.b_q(p, arg, body, loc)

    def b_speak(self, p, arg, body, loc):
        return (f'<section class="speak"><div class="bh">{icon("mic")}<span>{inline(arg or "Défi oral")}</span>'
                f'<span class="kz">口语挑战</span></div><div class="qb">{md(chr(10).join(body))}</div></section>')

    def b_md(self, p, arg, body, loc):
        return f'<div class="mdb">{md(chr(10).join(body))}</div>'

    def b_dialogue(self, p, arg, body, loc):
        return self.b_md(p, arg, body, loc)


def split_fields(line):
    """Split on single pipes (never on the '||' used for FR || ZH samples)."""
    return [x.strip() for x in re.split(r"(?<!\|)\|(?!\|)", line.strip())]


def word_regex(w):
    w = w.strip()
    if not w or len(w) < 3:
        return None
    w = re.sub(r"\s*\(.*?\)", "", w)
    w = w.split(" / ")[0].split(",")[0].strip()
    base = re.sub(r"^(se |s'|l'|le |la |les |un |une )", "", w)
    if not base:
        return None
    if " " in base:
        alts = [re.escape(base)]
    elif base.endswith("er") and len(base) > 4:
        stem = re.escape(base[:-2])
        alts = [stem + r"(?:e|es|ent|ons|ez|é|ée|és|ées|ait|ais|aient|er|ant|era|erai|erais|erait)"]
    elif base.endswith("ir") and len(base) > 4:
        stem = re.escape(base[:-2])
        alts = [stem + r"(?:ir|is|it|issons|issez|issent|i|ie|is|ies|issait)"]
    elif base.endswith("re") and len(base) > 5:
        stem = re.escape(base[:-2])
        alts = [stem + r"(?:re|s|t|ons|ez|ent|u|ue|us)"]
    else:
        alts = [re.escape(base) + r"(?:s|e|es|x)?"]
    return re.compile(r"(?<![\w])(?:" + "|".join(alts) + r")(?![\w])", re.I)


def reg_class(reg):
    r = reg.lower()
    if any(k in r for k in ("vulg", "grossier", "insulte")):
        return "r-vulg"
    if any(k in r for k in ("fam", "argot", "slang")):
        return "r-fam"
    if any(k in r for k in ("soutenu", "formel", "élégant", "littéraire")):
        return "r-sout"
    if any(k in r for k in ("québ", "qc")):
        return "r-qc"
    return "r-neu"


# ───────────────────────── book assembly ─────────────────────────

def assign_ids(ctx):
    k = 0
    for p in ctx.front:
        k += 1
        p.id = f"p0-{k}"
    for iss in ctx.issues:
        for j, p in enumerate(iss.pieces, 1):
            p.id = f"p{iss.num}-{j}"


def cover_html():
    return (ROOT / "tools" / "cover.html").read_text(encoding="utf-8")


def issue_opener(R, iss, stats):
    items = []
    for p in iss.pieces:
        fr, zh, ic, _ = KINDS[p.kind]
        items.append(f'<a class="ii" href="#{p.id}"><span class="ik">{icon(ic)}{fr}</span>'
                     f'<span class="it">{inline(p.title)}<span class="itz">{html.escape(p.title_zh)}</span></span>'
                     f'<span class="ip">{R.page(p.id)}</span></a>')
    s = stats[iss.num]
    tag = ""
    if iss.tag_fr:
        tag = f'<div class="io-tag">{inline(iss.tag_fr)}</div><div class="io-tagz">{inline(iss.tag_zh)}</div>'
    return (f'<section class="iopen" id="{iss.id}">'
            f'<div class="io-top"><span class="io-mast">THE FRENCH WORLD</span><span class="lvl lvl-{iss.level}">{iss.level}</span></div>'
            f'<div class="io-num">N°{iss.num}</div>'
            f'<h1 class="io-title">{inline(iss.title)}{R.mark(iss.id)}</h1><div class="io-zh">{html.escape(iss.title_zh)}</div>{tag}'
            f'<div class="io-stats"><span><b>{len(iss.pieces)}</b> articles · 篇</span><span><b>{s["new"]}</b> mots nouveaux · 新词</span>'
            f'<span><b>{s["expr"]}</b> expressions · 表达</span><span><b>{s["gram"]}</b> rappels de grammaire · 语法提示</span></div>'
            f'<div class="io-list"><div class="io-lh">DANS CE NUMÉRO · 本期内容</div>' + "".join(items) + "</div></section>")


def issue_tracker(R, iss, stats, target):
    s = stats[iss.num]
    pct = min(100, round(100 * s["cum"] / target))
    rows = "".join(
        f'<div class="tr"><span class="box"></span><span class="tk">{KINDS[p.kind][0]}</span>'
        f'<a href="#{p.id}">{inline(p.title)}</a><span class="tp">{R.page(p.id)}</span></div>'
        for p in iss.pieces)
    badges = "".join(
        f'<div class="badge"><span class="bstar">{icon("star")}</span><div><div class="bn">{inline(b[0])}</div>'
        f'<div class="bz">{inline(b[1])}</div><div class="bc">{inline(b[2])}</div></div><span class="box"></span></div>'
        for b in iss.badges)
    miles = "".join(f'<span class="mile{" on" if s["cum"] >= m else ""}" style="left:{min(100, 100*m/target):.1f}%">{m}</span>'
                    for m in range(500, target + 1, 500))
    tid = f"trk{iss.num}"
    return (f'<section class="tracker" id="{tid}"><div class="kicker">{icon("star")}<span>CARNET DE PROGRÈS</span><span class="kz">进度手册</span>'
            f'<span class="lvl lvl-{iss.level}">N°{iss.num}</span></div>'
            f'<h2 class="pt">Vous avez terminé le N°{iss.num} !{R.mark(tid)}</h2><div class="ptz">你读完了第 {iss.num} 期！</div>'
            f'<div class="counter"><div class="cbig">{s["cum"]:,}'.replace(",", " ") +
            f'</div><div class="clab">mots et expressions rencontrés depuis le début<br><span class="kz">从第一页起你已遇到的单词与表达</span></div>'
            f'<div class="cadd">+{s["new"]} mots · +{s["expr"]} expressions dans ce numéro</div>'
            f'<div class="bar"><div class="fill" style="width:{pct}%"></div>{miles}</div>'
            f'<div class="bar-l"><span>0</span><span>Objectif · 目标 : {target:,} </span></div></div>'.replace(",", " ") +
            f'<div class="trk-cols"><div><div class="th">JOURNAL DE LECTURE · 阅读记录</div>{rows}</div>'
            f'<div><div class="th">BADGES · 成就</div>{badges}</div></div></section>')


def build():
    ctx = Ctx()
    parse(ctx)
    assign_ids(ctx)
    pages = json.loads(PAGES.read_text()) if PAGES.exists() else {}
    R = Renderer(ctx, pages)

    # render pieces first (fills registries)
    front_html = [R.render_piece(p) for p in ctx.front]
    issue_bodies = {}
    stats = {}
    cum = len([v for v in ctx.vocab if not v["review"]]) + len(ctx.expr)   # Ouverture counts too
    for iss in ctx.issues:
        before_v = len([v for v in ctx.vocab if not v["review"]])
        before_e = len(ctx.expr)
        before_g = len(ctx.grammar)
        bodies = [R.render_piece(p) for p in iss.pieces]
        new_v = len([v for v in ctx.vocab if not v["review"]]) - before_v
        new_e = len(ctx.expr) - before_e
        cum += new_v + new_e
        stats[iss.num] = dict(new=new_v, expr=new_e, gram=len(ctx.grammar) - before_g, cum=cum)
        issue_bodies[iss.num] = bodies
    target = 3000

    parts = [cover_html()]
    parts.append(sommaire(R, ctx))
    parts.extend(front_html)
    for iss in ctx.issues:
        parts.append(f'<div class="issue iss-{iss.num}">')
        parts.append(issue_opener(R, iss, stats))
        parts.extend(issue_bodies[iss.num])
        parts.append(issue_tracker(R, iss, stats, target))
        parts.append("</div>")
    parts.append(backmatter(R, ctx))

    css = (ROOT / "tools" / "style.css").read_text(encoding="utf-8")
    css += page_rules(ctx)
    fonts = ["source-serif-4/400.css", "source-serif-4/400-italic.css", "source-serif-4/600.css",
             "source-serif-4/600-italic.css", "source-serif-4/700.css",
             "inter/400.css", "inter/500.css", "inter/600.css", "inter/700.css",
             "playfair-display/400.css", "playfair-display/400-italic.css", "playfair-display/700.css",
             "playfair-display/700-italic.css", "playfair-display/900.css",
             "noto-sans-sc/400.css", "noto-sans-sc/500.css", "noto-sans-sc/700.css",
             "noto-serif-sc/400.css", "noto-serif-sc/600.css", "noto-serif-sc/700.css"]
    links = "".join(f'<link rel="stylesheet" href="../node_modules/@fontsource/{f}">' for f in fonts)
    doc = ('<!doctype html><html lang="fr"><head><meta charset="utf-8">'
           '<title>The French World — Le magazine du français, A1 → B2</title>'
           f'{links}<style>{css}</style></head><body>' + "".join(parts) + "</body></html>")
    OUT.mkdir(exist_ok=True)
    (OUT / "book.html").write_text(doc, encoding="utf-8")

    # leftover emphasis markers
    txt = strip_tags(re.sub(r"<style>.*?</style>", "", doc, flags=re.S))
    for m in re.finditer(r".{0,30}(?<![\w])\*\*?\S.{0,30}", txt):
        ctx.errors.append("emphasis? " + m.group(0).replace("\n", " "))

    exports(ctx, R, stats)
    for d in R.dupes:
        print(f"DUPLICATE vocab: {d[0]!r} first in {d[1]}, again in {d[2]} ({d[3]})")
    for e in ctx.errors:
        print("ERROR", e)
    nrows = sum(1 for iss in ctx.issues for p in iss.pieces for b in p.blocks if b[0] == "row") + \
        sum(1 for p in ctx.front for b in p.blocks if b[0] == "row")
    print(f"issues={len(ctx.issues)} pieces={sum(len(i.pieces) for i in ctx.issues) + len(ctx.front)} rows={nrows} "
          f"vocab={len([v for v in ctx.vocab if not v['review']])} expr={len(ctx.expr)} grammar={len(ctx.grammar)} "
          f"dupes={len(R.dupes)} errors={len(ctx.errors)}")


def page_rules(ctx):
    css = []
    for iss in ctx.issues:
        label = f"N° {iss.num} · {iss.level} · {iss.title} · {iss.title_zh}".replace('"', '\\"')
        css.append(f'.iss-{iss.num} {{ page: iss{iss.num}; }}\n'
                   f'@page iss{iss.num} {{ @top-right {{ content: "{label}"; }} }}\n')
    return "\n".join(css)


def sommaire(R, ctx):
    rows = []
    for p in ctx.front:
        fr = KINDS[p.kind][0]
        rows.append(f'<a class="s-p" href="#{p.id}"><span class="s-k">{fr}</span><span class="s-t">{inline(p.title)}'
                    f' <span class="s-z">{html.escape(p.title_zh)}</span></span><span class="s-d"></span><span class="s-n">{R.page(p.id)}</span></a>')
    cur_level = None
    vol = {"A1": "Volume I · A1 · 入门", "A2": "Volume II · A2 · 基础", "B1": "Volume III · B1 · 进阶",
           "B2": "Volume IV · B2 · 中高级", "C1": "Bonus · Vers le C1 · 冲刺 C1"}
    for iss in ctx.issues:
        if iss.level != cur_level:
            cur_level = iss.level
            rows.append(f'<div class="s-vol">{vol.get(iss.level, iss.level)}</div>')
        rows.append(f'<a class="s-i" href="#{iss.id}"><span class="s-num">N°{iss.num}</span><span class="s-t">{inline(iss.title)}'
                    f' <span class="s-z">{html.escape(iss.title_zh)}</span></span><span class="s-d"></span><span class="s-n">{R.page(iss.id)}</span></a>')
        for p in iss.pieces:
            fr = KINDS[p.kind][0]
            rows.append(f'<a class="s-p" href="#{p.id}"><span class="s-k">{fr}</span><span class="s-t">{inline(p.title)}</span>'
                        f'<span class="s-d"></span><span class="s-n">{R.page(p.id)}</span></a>')
    if not any(i.level in ("B1", "B2", "C1") for i in ctx.issues):
        rows.append('<div class="s-vol">Volume III · B1 · Volume IV · B2 · Vers le C1 · TCF Canada — '
                    'lot 2 · 第二批交付</div>')
    for bid, t in BACK:
        rows.append(f'<a class="s-i s-back" href="#{bid}"><span class="s-num">◆</span><span class="s-t">{t}</span>'
                    f'<span class="s-d"></span><span class="s-n">{R.page(bid)}</span></a>')
    return ('<section class="sommaire"><div class="kicker">' + icon("book") + '<span>SOMMAIRE</span><span class="kz">目录</span></div>'
            '<h1 class="som-h" id="sommaire">Au sommaire' + R.mark("sommaire") + '</h1>'
            '<div class="som">' + "".join(rows) + "</div></section>")


BACK = [("bk-ans", "Corrigés · 练习答案"), ("bk-voc", "Index du vocabulaire · 词汇索引"),
        ("bk-exp", "Glossaire des expressions et de l'argot · 表达与俚语词汇表"),
        ("bk-gram", "Index de grammaire · 语法索引"), ("bk-cont", "Index des contenus · 内容索引")]


def backmatter(R, ctx):
    out = ['<div class="back">']
    # answer key
    out.append(f'<section class="bk" id="bk-ans"><div class="kicker">{icon("pen")}<span>CORRIGÉS</span><span class="kz">练习答案</span></div>'
               f'<h1 class="bk-h">Corrigés{R.mark("bk-ans")}</h1><div class="ans">')
    groups = [("Ouverture", ctx.front)] + [(f"N°{i.num} · {i.title}", i.pieces) for i in ctx.issues]
    for gname, plist in groups:
        items = [p for p in plist if p.answers]
        if not items:
            continue
        out.append(f'<div class="ans-g">{html.escape(gname)}</div>')
        for p in items:
            out.append(f'<div class="ans-p" id="ans-{p.id}">{R.mark("ans-" + p.id)}<a href="#{p.id}">{inline(p.title)} '
                       f'<span class="ans-pg">p. {R.page(p.id)}</span></a>'
                       f'<div class="ans-b">{md(chr(10).join(p.answers))}</div></div>')
    out.append("</div></section>")
    # vocab index
    out.append(f'<section class="bk" id="bk-voc"><div class="kicker">{icon("book")}<span>INDEX DU VOCABULAIRE</span><span class="kz">词汇索引</span></div>'
               f'<h1 class="bk-h">Index du vocabulaire{R.mark("bk-voc")}</h1>'
               f'<p class="bk-intro">Chaque mot renvoie à sa première apparition. · 每个词都链接到它第一次出现的页面。 '
               f'Base complète (IPA, exemples, collocations) : <code>deliverables/vocabulary.xlsx</code></p><div class="vidx">')
    letter = None
    for v in sorted([v for v in ctx.vocab if not v["review"]], key=lambda v: sort_key(v["word"])):
        L = (sort_key(v["word"])[:1] or "#").upper()
        if L != letter:
            letter = L
            out.append(f'<div class="vl-h">{L}</div>')
        out.append(f'<a class="vi" href="#{v["id"]}"><span class="viw">{inline(v["word"])}</span>'
                   f'<span class="vip">{html.escape(v["pos"])}</span> <span class="viz">{inline(v["zh"])}</span>'
                   f'<span class="vil">{v["level"]}</span><span class="vin">{R.page(v["id"])}</span></a>')
    out.append("</div></section>")
    # expressions
    out.append(f'<section class="bk" id="bk-exp"><div class="kicker">{icon("bubble")}<span>EXPRESSIONS & ARGOT</span><span class="kz">表达与俚语</span></div>'
               f'<h1 class="bk-h">Glossaire des expressions{R.mark("bk-exp")}</h1><div class="eidx">')
    for e in sorted(ctx.expr, key=lambda e: sort_key(e["expr"])):
        out.append(f'<a class="ei" href="#{e["id"]}"><span class="eie">{inline(e["expr"])}</span>'
                   f'<span class="reg {reg_class(e["reg"])}">{html.escape(e["reg"])}</span>'
                   f'<span class="eiz">{inline(e["zh"])}</span><span class="vin">{R.page(e["id"])}</span></a>')
    out.append("</div></section>")
    # grammar index
    out.append(f'<section class="bk" id="bk-gram"><div class="kicker">{icon("gear")}<span>INDEX DE GRAMMAIRE</span><span class="kz">语法索引</span></div>'
               f'<h1 class="bk-h">Index de grammaire{R.mark("bk-gram")}</h1><div class="gidx">')
    for lvl in LEVELS:
        gs = [g for g in ctx.grammar if g["level"][:2] == lvl]
        if not gs:
            continue
        out.append(f'<div class="gi-h"><span class="lvl lvl-{lvl}">{lvl}</span></div>')
        for g in gs:
            out.append(f'<a class="gi" href="#{g["id"]}"><span class="git">{inline(g["title"])}</span>'
                       f'<span class="giz">{html.escape(g["zh"])}</span><span class="s-d"></span><span class="vin">{R.page(g["id"])}</span></a>')
    out.append("</div></section>")
    # content index by section
    out.append(f'<section class="bk" id="bk-cont"><div class="kicker">{icon("star")}<span>INDEX DES CONTENUS</span><span class="kz">内容索引</span></div>'
               f'<h1 class="bk-h">Index des contenus{R.mark("bk-cont")}</h1><div class="cidx">')
    allp = list(ctx.front) + [p for i in ctx.issues for p in i.pieces]
    for kind, (fr, zh, ic, _) in KINDS.items():
        ps = [p for p in allp if p.kind == kind]
        if not ps:
            continue
        out.append(f'<div class="ci-h">{icon(ic)}{fr} <span class="kz">{zh}</span></div>')
        for p in ps:
            num = p.issue.num if p.issue else "—"
            out.append(f'<a class="ci" href="#{p.id}"><span class="cin">N°{num}</span><span class="cit">{inline(p.title)}</span>'
                       f'<span class="lvl lvl-{p.level[:2]}">{html.escape(p.level)}</span><span class="vin">{R.page(p.id)}</span></a>')
    out.append("</div></section></div>")
    return "".join(out)


# ───────────────────────── exports & reports ─────────────────────────

def forms_regex(word):
    return word_regex(word)


def exports(ctx, R, stats):
    DELIV.mkdir(exist_ok=True)
    vocab = [v for v in ctx.vocab if not v["review"]]
    allp = list(ctx.front) + [p for i in ctx.issues for p in i.pieces]
    order = {id(p): k for k, p in enumerate(allp)}

    # reappearance counts (approximate form matching in later French rows)
    later_text = []
    for p in allp:
        later_text.append(" ".join(b[1] for b in p.blocks if b[0] == "row"))
    for v in vocab:
        pat = word_regex(v["word"])
        k0 = order[id(v["piece"])]
        cnt = 0
        pieces_hit = 0
        if pat:
            for k in range(k0 + 1, len(allp)):
                c = len(pat.findall(later_text[k]))
                cnt += c
                pieces_hit += 1 if c else 0
        v["reuse"] = cnt
        v["reuse_pieces"] = pieces_hit

    def page_of(x):
        return R.page(x)

    fields = ["word", "pos", "gender", "ipa", "zh", "en", "level", "first_appearance", "page", "example", "example_zh",
              "collocations", "word_family", "note", "topics", "later_occurrences"]
    rows = []
    for v in vocab:
        g = "m" if "n.m" in v["pos"] else ("f" if "n.f" in v["pos"] else "")
        rows.append([v["word"], v["pos"], g, f'/{v["ipa"]}/' if v["ipa"] else "", strip_tags(v["zh"]), v["en"], v["level"],
                     v["where"], page_of(v["id"]), v["ex"], v["exzh"], v["col"], v["fam"], v["note"],
                     ", ".join(v["topics"]), v["reuse"]])
    with open(DELIV / "vocabulary.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(fields)
        w.writerows(rows)
    with open(DELIV / "anki_vocabulary.tsv", "w", encoding="utf-8") as fh:
        fh.write("#separator:tab\n#html:true\n#columns:Front\tBack\tTags\n")
        for v in vocab:
            front = f'{v["word"]} <i>({v["pos"]})</i><br>/{v["ipa"]}/'
            back = f'{v["zh"]}<br><i>{v["en"]}</i><br><br>{v["ex"]}<br>{v["exzh"]}'
            tags = f'FW::{v["level"]} ' + " ".join("FW::" + t.replace(" ", "_") for t in v["topics"])
            fh.write(f"{front}\t{back}\t{tags}\n".replace("\n\t", "\t"))
    erows = [[e["expr"], e["zh"], e["reg"], e["use"], e["ex"], e["exzh"], e["level"], e["where"], page_of(e["id"])]
             for e in ctx.expr]
    with open(DELIV / "expressions.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["expression", "zh", "register", "usage", "example", "example_zh", "level", "first_appearance", "page"])
        w.writerows(erows)
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        wb = Workbook()
        ws = wb.active
        ws.title = "Vocabulary"
        ws.append(fields)
        for r in rows:
            ws.append(r)
        ws2 = wb.create_sheet("Expressions")
        ws2.append(["expression", "zh", "register", "usage", "example", "example_zh", "level", "first_appearance", "page"])
        for r in erows:
            ws2.append(r)
        ws3 = wb.create_sheet("Grammar")
        ws3.append(["level", "topic", "zh", "issue", "piece", "page"])
        for g in ctx.grammar:
            ws3.append([g["level"], g["title"], g["zh"], g["where"], g["piece"].title, page_of(g["id"])])
        ws4 = wb.create_sheet("Content")
        ws4.append(["issue", "section", "title", "zh", "level", "page", "characters", "setting", "themes", "rows"])
        for p in allp:
            ws4.append([p.issue.num if p.issue else "front", KINDS[p.kind][0], p.title, p.title_zh, p.level,
                        page_of(p.id), ", ".join(p.meta.get("characters", [])), ", ".join(p.meta.get("setting", [])),
                        ", ".join(p.meta.get("themes", [])), sum(1 for b in p.blocks if b[0] == "row")])
        for sh in (ws, ws2, ws3, ws4):
            for c in sh[1]:
                c.font = Font(bold=True, color="FFFFFF")
                c.fill = PatternFill("solid", fgColor="333333")
            sh.freeze_panes = "A2"
            for col in sh.columns:
                sh.column_dimensions[col[0].column_letter].width = 22
        wb.save(DELIV / "vocabulary.xlsx")
    except ImportError:
        pass

    # grammar index
    g_md = ["# Grammar index · 语法索引\n"]
    for lvl in LEVELS:
        gs = [g for g in ctx.grammar if g["level"][:2] == lvl]
        if gs:
            g_md.append(f"\n## {lvl}\n\n| Topic | 中文 | Issue | Page |\n|---|---|---|---:|")
            for g in gs:
                g_md.append(f'| {g["title"]} | {g["zh"]} | {g["where"]} | {page_of(g["id"])} |')
    (DELIV / "grammar_index.md").write_text("\n".join(g_md) + "\n", encoding="utf-8")

    # content index
    c_md = ["# Content index · 内容索引\n", "| Issue | Section | Title | 中文 | Level | Page |", "|---|---|---|---|---|---:|"]
    for p in allp:
        c_md.append(f'| {p.issue.num if p.issue else "—"} | {KINDS[p.kind][0]} | {p.title} | {p.title_zh} | {p.level} | {page_of(p.id)} |')
    (DELIV / "content_index.md").write_text("\n".join(c_md) + "\n", encoding="utf-8")

    # answer key
    a_md = ["# Answer key · 练习答案\n"]
    for p in allp:
        if p.answers:
            a_md.append(f'\n## N°{p.issue.num if p.issue else 0} · {p.title} (p. {page_of(p.id)})\n')
            a_md.append("\n".join(p.answers))
    (DELIV / "answer_key.md").write_text("\n".join(a_md) + "\n", encoding="utf-8")

    # TCF vocabulary by topic
    by_topic = defaultdict(list)
    for v in vocab:
        for t in v["topics"]:
            by_topic[t].append(v)
    t_md = ["# TCF Canada vocabulary by topic · 按主题分类的 TCF 词汇\n"]
    for t in sorted(by_topic):
        t_md.append(f"\n## {t} ({len(by_topic[t])})\n\n| Mot | Nature | 中文 | English | Niveau | Page |\n|---|---|---|---|---|---:|")
        for v in sorted(by_topic[t], key=lambda v: sort_key(v["word"])):
            t_md.append(f'| {v["word"]} | {v["pos"]} | {strip_tags(v["zh"])} | {v["en"]} | {v["level"]} | {page_of(v["id"])} |')
    (DELIV / "tcf_vocabulary.md").write_text("\n".join(t_md) + "\n", encoding="utf-8")

    # CEFR coverage
    cov = ["# CEFR coverage report · 欧标覆盖报告\n",
           "| Level | Issues | Pieces | Aligned rows | French words in rows | New vocabulary | Expressions | Grammar topics |",
           "|---|---|---:|---:|---:|---:|---:|---:|"]
    for lvl in LEVELS:
        iss = [i for i in ctx.issues if i.level == lvl]
        if not iss:
            continue
        ps = [p for i in iss for p in i.pieces]
        rws = [b for p in ps for b in p.blocks if b[0] == "row"]
        words = sum(len(re.findall(r"[\wÀ-ÿ'’-]+", b[1])) for b in rws)
        nv = len([v for v in vocab if v["piece"].issue in iss])
        ne = len([e for e in ctx.expr if e["piece"].issue in iss])
        ng = [g for g in ctx.grammar if g["piece"].issue in iss]
        cov.append(f'| {lvl} | {", ".join("N°" + i.num for i in iss)} | {len(ps)} | {len(rws)} | {words} | {nv} | {ne} | {len(ng)} |')
    for lvl in LEVELS:
        gs = [g for g in ctx.grammar if g["level"][:2] == lvl]
        if gs:
            cov.append(f"\n## {lvl} — grammar covered\n")
            cov.extend(f'- {g["title"]} ({g["zh"]}) — {g["where"]}' for g in gs)
    for lvl in LEVELS:
        iss = [i for i in ctx.issues if i.level == lvl]
        if not iss:
            continue
        cnt = Counter(KINDS[p.kind][0] for i in iss for p in i.pieces)
        cov.append(f"\n## {lvl} — sections\n")
        cov.extend(f"- {k}: {n}" for k, n in cnt.most_common())
    (DELIV / "cefr_coverage.md").write_text("\n".join(cov) + "\n", encoding="utf-8")

    # repetition report
    rep = ["# Repetition & vocabulary-tracking report · 重复与词汇追踪报告\n"]
    rep.append(f"- New vocabulary entries: **{len(vocab)}** (review cards: {len([v for v in ctx.vocab if v['review']])})")
    rep.append(f"- Duplicate headwords introduced as *new* twice: **{len(R.dupes)}**")
    for d in R.dupes:
        rep.append(f"  - {d[0]} — first {d[1]}, again {d[2]}")
    reused = [v for v in vocab if v["reuse"] > 0]
    r3 = [v for v in vocab if v["reuse"] >= 3]
    if vocab:
        rep.append(f"- Words that reappear later in the reading texts (approximate form matching): "
                   f"**{len(reused)} / {len(vocab)} ({100*len(reused)//len(vocab)} %)**; three times or more: {len(r3)}")
    titles = Counter(p.title for p in allp)
    dup_titles = [t for t, n in titles.items() if n > 1]
    rep.append(f"- Duplicate piece titles: {len(dup_titles)} {dup_titles if dup_titles else ''}")
    rowtexts = Counter(b[1].strip() for p in allp for b in p.blocks if b[0] == "row" and len(b[1]) > 25)
    dup_rows = [t for t, n in rowtexts.items() if n > 1]
    rep.append(f"- Identical French sentences (>25 chars) appearing twice or more: {len(dup_rows)}")
    for t in dup_rows[:30]:
        rep.append(f"  - {t}")
    rep.append("\n## Characters\n")
    chars = defaultdict(list)
    for p in allp:
        for c in p.meta.get("characters", []):
            chars[c].append(f'N°{p.issue.num if p.issue else 0}')
    for c, lst in sorted(chars.items(), key=lambda x: -len(x[1])):
        rep.append(f"- {c}: {len(lst)} pieces ({', '.join(OrderedDict.fromkeys(lst))})")
    rep.append("\n## Settings & themes\n")
    sets = Counter(s for p in allp for s in p.meta.get("setting", []))
    ths = Counter(s for p in allp for s in p.meta.get("themes", []))
    rep.append("- Settings: " + ", ".join(f"{k} ({n})" for k, n in sets.most_common()))
    rep.append("- Themes: " + ", ".join(f"{k} ({n})" for k, n in ths.most_common()))
    rep.append("\n## Most revisited words\n")
    for v in sorted(vocab, key=lambda v: -v["reuse"])[:40]:
        rep.append(f'- {v["word"]} ({v["level"]}, {v["where"]}): {v["reuse"]} later occurrences in {v["reuse_pieces"]} pieces')
    rep.append("\n## Words not yet revisited (candidates for reuse in later issues)\n")
    rep.append(", ".join(v["word"] for v in vocab if v["reuse"] == 0))
    (DELIV / "repetition_report.md").write_text("\n".join(rep) + "\n", encoding="utf-8")

    # registry for authoring: compact list of headwords
    (OUT / "headwords.txt").write_text("\n".join(sorted({norm(v["word"]) for v in vocab})), encoding="utf-8")
    (OUT / "stats.json").write_text(json.dumps(stats), encoding="utf-8")


if __name__ == "__main__":
    build()
