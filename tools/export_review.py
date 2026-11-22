#!/usr/bin/env python3
"""Gemini などでのチェック用に、日本語と英語を並べた表（CSV）を書き出す。"""
import json, csv, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
d = json.loads((root / "i18n" / "en.json").read_text(encoding="utf-8"))
out = root / "i18n" / "en_review.csv"
with out.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["種類", "日本語", "English"])
    for k, v in d.get("nouns", {}).items(): w.writerow(["名前", k, v])
    for k, v in d.get("text", {}).items(): w.writerow(["文", k.replace("\n", "\\n"), v.replace("\n", "\\n")])
print(out, sum(len(x) for x in d.values()), "rows")
