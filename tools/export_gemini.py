#!/usr/bin/env python3
"""Gemini に手で貼って渡すための小分けファイルを作る（1ファイル約150行）。
番号は en.json の並び順（nouns→text）。チェック済みの範囲は --start で飛ばせる。"""
import json, pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent
d = json.loads((root / "i18n" / "en.json").read_text(encoding="utf-8"))
rows = [("名前", k, v) for k, v in d["nouns"].items()] + [("文", k, v) for k, v in d["text"].items()]
start = int(sys.argv[sys.argv.index("--start") + 1]) if "--start" in sys.argv else 1
size = 150
outdir = root / "i18n" / "gemini"; outdir.mkdir(exist_ok=True)
HEAD = """以下は、のんびりした牧場経営ゲーム「のんびり牧場」の日本語→英語の対訳です。
先にお渡しした説明資料（gemini_brief.pdf）のキャラクター表・用語集にそって見てください。
英語として不自然な表現・誤訳・意味のずれがある行だけ、番号と直した英語を書いてください。問題のない行は書かなくてかまいません。

決まりごと：
・{1} {2} などの記号は数字が入る場所です。そのまま残してください（順番は入れかえてよい）
・絵文字・¥・Lv. もそのまま残してください
・画面がせまいので、短く分かりやすい英語にしてください
・キャラの名前（Minori, Kohaku, Hinata, Akari, Tsubaki, Shizuku）は変えないでください

返事の形：
番号｜元の日本語｜今の英訳｜直した英訳｜理由（ひとこと）

"""
files = []
for i in range(start - 1, len(rows), size):
    chunk = rows[i:i + size]
    a, b = i + 1, i + len(chunk)
    lines = [HEAD + f"（{a}〜{b}行目）\n"]
    for n, (kind, jp, en) in enumerate(chunk, a):
        lines.append(f"{n}｜{jp.replace(chr(10), ' / ')}｜{en.replace(chr(10), ' / ')}")
    p = outdir / f"check_{a:04d}-{b:04d}.txt"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    files.append(p)
print("\n".join(str(f) for f in files))
