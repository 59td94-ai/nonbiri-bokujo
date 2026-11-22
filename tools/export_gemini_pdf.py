#!/usr/bin/env python3
"""Gemini チェック用の小分けファイルを1つの PDF にまとめる（150行ごとに改ページ・番号つき）。"""
import pathlib, html
from playwright.sync_api import sync_playwright
root = pathlib.Path(__file__).resolve().parent.parent
files = sorted((root / "i18n" / "gemini").glob("check_*.txt"))
parts = []
for i, f in enumerate(files):
    txt = f.read_text(encoding="utf-8")
    head, body = txt.split("（", 1)[0], "（" + txt.split("（", 1)[1] if i else txt
    if i == 0:
        intro, rest = txt.split("\n（", 1); rest = "（" + rest
        parts.append(f'<section><pre class="h">{html.escape(intro)}</pre>')
    else:
        rest = txt[txt.index("\n（") + 1:]
        parts.append('<section class="pb">')
    title, *lines = rest.strip().split("\n")
    rows = "".join(f"<tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td><td>{html.escape(c)}</td></tr>"
                   for a, b, c in (l.split("｜", 2) for l in lines if l.count("｜") >= 2))
    parts.append(f"<h2>まとまり {i+1}／{len(files)} {html.escape(title)}</h2><table>{rows}</table></section>")
doc = f"""<!doctype html><meta charset=utf-8><style>
body{{font-family:"Noto Sans CJK JP",sans-serif;font-size:9.5pt;margin:0}}
pre.h{{white-space:pre-wrap;font-family:inherit;background:#f6f3ea;padding:8px;border-radius:6px}}
h2{{font-size:11pt;margin:10px 0 6px}} .pb{{page-break-before:always}}
table{{border-collapse:collapse;width:100%}} td{{border:1px solid #ccc;padding:2px 5px;vertical-align:top}}
td:first-child{{width:3em;text-align:right;color:#666}} td:nth-child(2){{width:46%}}
</style>{''.join(parts)}"""
out = root / "i18n" / "gemini" / "gemini_check_all.pdf"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = b.new_page(); pg.set_content(doc); pg.pdf(path=str(out), format="A4", margin={"top": "12mm", "bottom": "12mm", "left": "10mm", "right": "10mm"})
    b.close()
print(out)
