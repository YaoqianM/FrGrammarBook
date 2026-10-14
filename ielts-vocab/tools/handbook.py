"""Volume 5: index & review handbook, generated from the same data as volumes 1–4."""
import re

TOPIC_MAP = [
    ("教育与学习 · Education & learning", [7, 14, 13, 26]),
    ("健康、饮食与生活方式 · Health, food & lifestyle", [5, 6, 31, 32, 15]),
    ("环境、能源与自然 · Environment, energy & nature", [10, 21, 29, 30]),
    ("科学与研究 · Science & research", [27, 21, 31]),
    ("科技、媒体与创新 · Technology, media & innovation", [28, 22, 37]),
    ("工作、金钱与经济 · Work, money & the economy", [17, 18, 33]),
    ("城市、住房与交通 · Cities, housing & transport", [9, 19, 20]),
    ("社会、文化与家庭 · Society, culture & family", [2, 3, 16, 23, 35, 40]),
    ("政府、法律与伦理 · Government, law & ethics", [34, 24, 36]),
    ("旅行与全球化 · Travel & globalisation", [9, 23]),
    ("写作 Task 1：图表与数据 · Charts & data", [41, 42]),
    ("写作 Task 2：论证与表达 · Argument & expression", [43, 44, 45, 46, 47, 38, 39]),
    ("口语 · Speaking", [48, 12, 1, 8, 2, 3]),
    ("阅读：同义替换与猜词 · Reading: paraphrase & guessing", [11, 25, 50, 51, 26, 38]),
    ("准确性：易混词与常见错误 · Accuracy", [49, 1, 7, 12]),
]


def build_handbook(b, units, pages_by_vol):
    toc, body = [], []
    esc, inline, md, mark = b.esc, b.inline, b.md, b.mark

    def ref(e):
        v = b.vol_of_unit(e.unit)
        p = pages_by_vol.get(v, {}).get(f"e{e.unit}_{e.n}", "")
        return f"{e.unit}.{e.n} · {b.VOLUMES[v]['roman']}-{p}" if p else f"{e.unit}.{e.n} · {b.VOLUMES[v]['roman']}"

    def unit_page(un):
        v = b.vol_of_unit(un)
        p = pages_by_vol.get(v, {}).get(f"h{un}_0", "")
        return f"{b.VOLUMES[v]['roman']}-{p}" if p else b.VOLUMES[v]["roman"]

    def section(hid, title, sub, inner, cls="hb"):
        toc.append((1, hid, title, sub))
        body.append(f'<article class="{cls}"><h1 id="{hid}">{esc(title)}{mark(hid)}<small>{esc(sub)}</small></h1>{inner}</article>')

    def read(name):
        return md((b.DATA / name).read_text(encoding="utf-8"))

    all_entries = [e for un in sorted(units) for e in b.entries_of(units[un])]

    # 1–3: prose
    section("hb1", "How to Use This Series", "全套使用说明", read("hb-intro.md"))
    section("hb2", "Study Roadmap", "学习路线", read("hb-roadmap.md"))
    section("hb3", "Review Methods", "复习方法", read("hb-review.md"))

    # 4: topic index
    rows = []
    for v, cfg in b.VOLUMES.items():
        for un in cfg["units"]:
            if un not in units:
                continue
            u = units[un]
            es = b.entries_of(u)
            secs = " · ".join(re.sub(r"^\d+\s*·\s*", "", blk[1]).split(" · ")[0] for blk in u["blocks"] if blk[0] == "h2")
            rows.append(f"<tr><td><b>{un}</b></td><td><b>{esc(u['title'])}</b><br>{esc(u['zh'])}"
                        f"<br><small>{esc(secs)}</small></td><td>{cfg['roman']}</td><td>{esc(u['level'].split(' · ')[0])}</td>"
                        f"<td>{len(es)}</td><td>{sum(e.featured for e in es)}</td><td>{unit_page(un)}</td></tr>")
    topic_rows = "".join(
        f"<tr><td>{esc(t)}</td><td>{' · '.join(f'Unit {un} <small>({unit_page(un)})</small>' for un in uns)}</td></tr>"
        for t, uns in TOPIC_MAP)
    inner = ('<h2 class="notoc">按 IELTS 话题查找 · By IELTS topic</h2>'
             '<table class="topics"><thead><tr><th>话题</th><th>相关单元（册-页）</th></tr></thead>' + topic_rows + "</table>"
             '<h2 class="notoc">全部单元一览 · All units</h2>'
             '<table class="units"><thead><tr><th>单元</th><th>主题与分节</th><th>册</th><th>难度</th><th>词条</th><th>★</th><th>页</th></tr></thead>'
             + "".join(rows) + "</table>")
    section("hb4", "Topic Index", "主题索引", inner)

    # 5: master alphabetical index
    items = sorted(all_entries, key=lambda e: (b.sort_key(e.head), e.head))
    out, letter = [], ""
    for e in items:
        L = (b.sort_key(e.head)[:1] or "#").upper()
        if L != letter:
            letter = L
            out.append(f'<div class="ix-letter">{L}</div>')
        out.append(f'<div class="ix"><span class="w">{esc(e.head)}</span><span class="z">{inline(b.first_sense(e.zh))}</span>'
                   f'<span class="d"></span><span class="r">{ref(e)}</span></div>')
    section("hb5", "Alphabetical Index", f"英文词条总索引（共 {len(all_entries)} 条 · 编号 · 册-页）",
            '<p class="note-s">编号 27.3 = 第 27 单元第 3 个词条；Ⅲ-41 = 第三册第 41 页。以 be / to / a / the 开头的表达按后面的词排序。</p>'
            f'<div class="index">{"".join(out)}</div>', cls="hb appendix")

    # 6: word families
    fams = sorted((e for e in all_entries if e.fam), key=lambda e: b.sort_key(e.head))
    out = [f'<div class="fx"><span class="w">{esc(e.head)}</span> <span class="r">{e.unit}.{e.n}</span>'
           f'<div class="f">→ {inline(e.fam)}</div></div>' for e in fams]
    n_items = sum(len(b.fam_items(e.fam)) for e in fams)
    section("hb6", "Word Family Index", f"重点词族索引（{len(fams)} 个词族 · {n_items} 个派生词）",
            '<p class="note-s">左边是正文中的词条（含编号），箭头后是一起学习的派生词。复习方法：遮住箭头右边，试着说出同一词族的其他词性。</p>'
            f'<div class="index fam-index">{"".join(out)}</div>', cls="hb appendix")

    # 7: confusables
    out = []
    for un in sorted(units):
        for blk in units[un]["blocks"]:
            if blk[0] != "cmp":
                continue
            title, rws, notes = blk[1], blk[2], blk[3]
            t = title or " vs. ".join(r[0] for r in rws)
            trs = "".join(f'<tr><td class="w">{inline(w)}</td><td>{inline(d)}</td></tr>' for w, d, _ in rws)
            out.append(f'<div class="cq"><div class="cq-h"><b>{inline(t)}</b> <span class="r">Unit {un} · {unit_page(un)}</span></div>'
                       f'<table>{trs}</table></div>')
    section("hb7", "Confusable Words Quick Reference", "易混词速查表",
            '<p class="note-s">正文中所有“易混辨析”框的速查版（不含例句；完整例句见对应单元）。另有大量易混点写在 ★ 重点词的讲解中，可通过总索引查找。</p>'
            f'<div class="cq-grid">{"".join(out)}</div>', cls="hb appendix")

    # 8: collocations & expressions
    out = []
    n = 0
    for un in sorted(units):
        es = [e for e in b.entries_of(units[un])
              if " " in e.head.strip() and " vs. " not in e.head and e.pos.startswith("phr")]
        if not es:
            continue
        out.append(f'<div class="ix-letter">Unit {un} · {esc(units[un]["title"])}</div>')
        for e in es:
            n += 1
            out.append(f'<div class="ix"><span class="w">{esc(e.head)}</span><span class="z">{inline(b.first_sense(e.zh))}</span>'
                       f'<span class="d"></span><span class="r">{e.unit}.{e.n}</span></div>')
    section("hb8", "High-value Collocations & Expressions", f"高价值搭配与固定表达汇总（{n} 条）",
            '<p class="note-s">正文中以“整块”形式收录的搭配、短语动词和固定表达，按单元排列。建议复习时遮住中文，用每个表达说一个完整的句子。'
            '此外，每个词条的“搭配”栏还有数千个搭配示例。</p>'
            f'<div class="index">{"".join(out)}</div>', cls="hb appendix")

    section("hb9", "A Final Word", "写在最后", read("hb-closing.md"))

    css = """
    .note-s { font-family: "Noto Sans SC", sans-serif; font-size: 0.8rem; color: var(--muted); }
    .hb table.units td, .hb table.topics td { font-size: 0.76rem; }
    .hb table.units td:nth-child(1) { width: 6%; } .hb table.units td:nth-child(3) { width: 5%; }
    .hb table.units td:nth-child(4) { width: 9%; white-space: nowrap; } .hb table.units td:nth-child(5),
    .hb table.units td:nth-child(6) { width: 5%; } .hb table.units td:nth-child(7) { width: 8%; white-space: nowrap; }
    .hb table.units td small { font-family: "Inter", sans-serif; font-size: 0.68rem; }
    .fam-index .fx { break-inside: avoid; margin-bottom: 3px; line-height: 1.35; }
    .fx .w { font-family: "Inter", sans-serif; font-weight: 700; }
    .fx .r { font-family: "Inter", sans-serif; color: #8a93a3; font-size: 0.9em; }
    .fx .f { font-family: "Inter", "Noto Sans SC", sans-serif; color: #3f485a; padding-left: 10px; }
    .cq-grid { columns: 2; column-gap: 14px; }
    .cq { break-inside: avoid; border: 1px solid #ddd2ef; background: #f8f5fc; border-radius: 6px; padding: 4px 8px; margin-bottom: 7px; font-size: 0.74rem; }
    .cq-h { font-family: "Inter", sans-serif; color: #2a1d48; margin-bottom: 2px; }
    .cq-h .r { color: #8a93a3; font-weight: 400; font-size: 0.9em; }
    .cq table { margin: 0; font-size: 1em; }
    .cq td { padding: 1.5px 3px; border-bottom: 1px solid #ebe4f5; background: none !important; }
    .cq td.w { font-family: "Inter", sans-serif; font-weight: 700; color: #3e2a6b; width: 32%; }
    """
    front = (f'<article class="front"><h1 class="plain">关于本册 · About this volume</h1>'
             f'<p>本册是全套书的总索引与复习手册。全套共 51 个单元、{len(all_entries)} 个去重词条、'
             f'{sum(e.featured for e in all_entries)} 个 ★ 重点词、'
             f'{sum(1 for un in units for blk in units[un]["blocks"] if blk[0] == "cmp")} 组易混辨析。</p>'
             f'{b.series_table(units)}</article>')
    html = b.cover(5) + front + b.toc_html(toc, pages_by_vol.get(5, {})) + "".join(body)
    return b.wrap(5, html).replace("</style>", css + "</style>", 1)
