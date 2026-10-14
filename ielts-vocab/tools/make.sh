#!/usr/bin/env bash
# Build all five volumes. Two passes each: the second fills TOC/index page numbers.
# Volume 5 (handbook) is built last because its indexes cite pages in volumes 1–4.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/build.py check | tail -1
names=("" "IELTS_Vocab_Vol1_Foundations_Upgrade" "IELTS_Vocab_Vol2_Core_Vocabulary"
       "IELTS_Vocab_Vol3_Academic_and_Topic_Vocabulary" "IELTS_Vocab_Vol4_Precision_and_Band_Boosters"
       "IELTS_Vocab_Vol5_Index_and_Review_Handbook")
labels=("" "Vol. 1 · Foundations Upgrade 基础升级" "Vol. 2 · Core Vocabulary 中级核心"
        "Vol. 3 · Academic & Topic Vocabulary 高级应用" "Vol. 4 · Precision & Band Boosters 高分精修"
        "Vol. 5 · Index & Review Handbook 索引与复习手册")
for v in ${VOLS:-1 2 3 4 5}; do
  rm -f "build/vol$v.pages.json"
  python3 tools/build.py html "$v" && node tools/render.mjs "$v" "${labels[$v]}" && python3 tools/locate.py "$v"
  python3 tools/build.py html "$v" && node tools/render.mjs "$v" "${labels[$v]}" && python3 tools/locate.py "$v"
  cp "build/vol$v.pdf" "pdf/${names[$v]}.pdf"
done
