#!/usr/bin/env python3
"""Quality checks beyond `build.py check`: English spelling, cross-references, example coverage."""
import collections, re, sys
sys.path.insert(0, "tools")
import build
from spellchecker import SpellChecker

units = build.load_units()
sp = SpellChecker(language="en")
# British spellings and proper nouns used on purpose
ok = set("""
analyse analysed analyses analysing organise organised organisation colour favourite behaviour neighbour neighbours neighbourhood
travelling programme programmes centre centres metre metres litre theatre licence practise practised defence offence
recognise recognised realise realised memorise criticise criticised apologise apologised emphasise emphasised prioritise
modernise globalisation globalise urbanisation urbanised privatise privatised nationalise penalise penalised subsidise
categorise categorised summarise synchronise synchronises scrutinise revolutionise revolutionised minimise maximise
stabilise stabilised pedestrianise rejuvenate commercialise commercialised commercialisation socialise empathise
digitise electrify fibre storey storeys grey cosy fulfil enrol enrolment judgement ageing sceptical sceptic scepticism
labour counselling counsellor jewellery mould plough tyre aluminium honour humour rumour rumours odour flavour
endeavour vapour savoury programme catalogue dialogue monologue cheque kerb
shenzhen guangzhou futian nanshan dongmen hainan huizhou hunan guangdong wutong yunnan tibet guilin leizhou
huangguoshu xian confucius genghis khan einstein darwin fleming curie mozart edison bell dolly crispr doudna charpentier
nike tiktok huawei facebook nasa nhs ipcc iucn wwf fao unesco ielts tcf cefr awl coxhead dweck holt lunstad
cambridge oxford eton yellowstone venice barcelona amazon himalayas maya miami sydney renaissance
covid ok tv wifi gdp cctv ngo ngos vr ar ai ev evs uk us eu un mbps km cv sb sth etc
taikonauts mahjong dim sum karate judo kungfu sushi selfie selfies emoji
""".split())
sp.word_frequency.load_words(ok)

def words(text):
    text = re.sub(r"\*|\(|\)|/|…", " ", text)
    return re.findall(r"[A-Za-z][A-Za-z'’-]*[A-Za-z]|[A-Za-z]", text)

unknown = collections.Counter()
where = {}
for un, u in units.items():
    for e in build.entries_of(u):
        for field in (e.head, e.colloc, e.example, e.also):
            for w in words(field):
                for part in re.split(r"[-'’]", w):
                    lw = part.lower()
                    if len(lw) < 3 or lw in ok:
                        continue
                    if lw not in sp:
                        unknown[lw] += 1
                        where.setdefault(lw, f"U{un} {e.head}")
    for b in u["blocks"]:
        if b[0] == "cmp":
            for row in b[2]:
                for w in words(row[0] + " " + row[2]):
                    lw = w.lower().strip("'’")
                    if len(lw) >= 3 and lw not in ok and lw not in sp:
                        unknown[lw] += 1
                        where.setdefault(lw, f"U{un} cmp")
print("== possibly misspelt words (review) ==")
for w, n in sorted(unknown.items()):
    print(f"{w:22s} {n:3d}  {where[w]}")

# cross references like （U27） or Unit 27 must point to an existing unit that mentions the word
print("== cross-references ==")
bad = 0
for p in sorted(build.DATA.glob("[0-9][0-9]-*.txt")):
    txt = p.read_text(encoding="utf-8")
    for m in re.finditer(r"\*([A-Za-z][^*]{0,40})\*（U(\d+)）", txt):
        word, un = m.group(1), int(m.group(2))
        if un not in units:
            print("missing unit", p.name, m.group(0)); bad += 1; continue
        target = (build.DATA / units[un]["file"]).read_text(encoding="utf-8").lower()
        stem = word.lower().split("/")[0].strip()[:6]
        if stem not in target:
            print("ref?", p.name, m.group(0)); bad += 1
print("bad refs:", bad)

# examples in which the headword could not be found (for information)
miss = 0
for un, u in units.items():
    for e in build.entries_of(u):
        if e.example:
            rx = build.head_regex(e.head)
            if not rx or not rx.search(e.example):
                miss += 1
print("entries whose example does not contain the headword form:", miss)
