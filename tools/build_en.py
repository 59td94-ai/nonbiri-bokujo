#!/usr/bin/env python3
"""i18n/en.json を index.html の多言語スクリプトに埋め込む（何度実行してもよい）。
en.json:
  "nouns": 名前（作物・製品・施設・キャラなど）。文の中に出てきたら差しかえ用の {A}{B}… になる。
  "text" : 文。キーの数字は {1}{2}…。
build のとき、text の文に nouns の名前が入っていて、英訳にもその名前の英語が入っていれば、
名前を {A}… に置きかえた「ひな形」も自動で作る（別の作物名でも同じ文が訳される）。
英語を選んだときだけ使う。日本語・中国語・韓国語の表示は変わらない。"""
import json, gzip, base64, re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
html = root / "index.html"
data = json.loads((root / "i18n" / "en.json").read_text(encoding="utf-8"))
nouns = data.get("nouns", {}); text = dict(data.get("text", {}))
# ストーリーの題名（titles）から、題名入りの表示をまとめて作る
CH = {"みのり": "Minori", "こはく": "Kohaku", "ひなた": "Hinata", "あかり": "Akari", "つばき": "Tsubaki", "しずく": "Shizuku"}
for jp, en in data.get("titles", {}).items():
    text.setdefault(f"「{jp}」 💗がたまりました", f"“{en}” 💗 is full")
    text.setdefault(f"「{jp}」", f"“{en}”")
    for cj, ce in CH.items():
        for pre in ("", "📖 "):
            text.setdefault(f"{pre}{cj}のストーリー\u3000第{{1}}話「{jp}」", f"{pre}{ce}'s story, Ep. {{1}} “{en}”")
        for cj2, ce2 in CH.items():
            if cj2 != cj: text.setdefault(f"{cj}と{cj2}「{jp}」", f"{ce} & {ce2}: “{en}”")
for cj, ce in CH.items():
    for sp in (" ", "\u3000"):
        for pre in ("", "📖 "):
            text.setdefault(f"{pre}{cj}のストーリー{sp}第{{1}}話", f"{pre}{ce}'s story, Ep. {{1}}")
    for cj2, ce2 in CH.items():
        if cj2 != cj: text.setdefault(f"{cj}と{cj2}", f"{ce} & {ce2}")
keys = sorted(nouns, key=len, reverse=True)
NRX = re.compile("|".join(re.escape(k) for k in keys)) if keys else None
gen = {}
if NRX:
    for k, v in text.items():
        found = []
        def rep(m):
            found.append(m.group(0)); return "{" + chr(65 + len(found) - 1) + "}"
        k2 = NRX.sub(rep, k)
        if not found or k2 in text: continue
        v2, ok = v, True
        for i, jp in enumerate(found):
            en = nouns[jp]; ph = chr(65 + i)
            m = re.search(r"(?<![A-Za-z])" + re.escape(en) + r"(?![A-Za-z])", v2, re.I)
            if not m: ok = False; break
            hit = m.group(0)
            tag = "{" + (ph.lower() if hit == hit.lower() and en != en.lower() else ph) + "}"
            v2 = v2[:m.start()] + tag + v2[m.end():]
        if ok:
            if k2 in gen and gen[k2] != v2: gen[k2] = None
            elif k2 not in gen: gen[k2] = v2
for k2, v2 in gen.items():
    if v2: text.setdefault(k2, v2)
# 絵文字を外した形でも引けるようにする（作物ごとに絵文字が変わる文のため）。runtime の enStrip と同じ処理
EMO = re.compile("[\U0001F000-\U0001FAFF\u2190-\u21FF\u2300-\u27BF\u2B00-\u2BFF\U0001F1E6-\U0001F1FF]\uFE0F?|\u200D|\uFE0F")
def strip(x): return re.sub("[ \u3000]{2,}", " ", EMO.sub("", x)).strip()
for k, v in list(text.items()):
    sk = strip(k)
    if sk and sk != k and sk not in text: text[sk] = strip(v) if strip(v) else v
out = {"nouns": nouns, "text": text}
s = html.read_text(encoding="utf-8")
payload = base64.b64encode(gzip.compress(json.dumps(out, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), 9)).decode()
A, B = "/*EN_EXTRA_BEGIN*/", "/*EN_EXTRA_END*/"
if A not in s: raise SystemExit("marker not found: run tools/patch_runtime.py first")
s = re.sub(re.escape(A) + r".*?" + re.escape(B), lambda m: A + 'var EN_EXTRA="' + payload + '";' + B, s, count=1, flags=re.S)
html.write_text(s, encoding="utf-8")
print("nouns", len(nouns), "text", len(data.get("text", {})), "+templates", sum(1 for v in gen.values() if v), "bytes", len(payload))
