#!/usr/bin/env python3
"""英語のとき「1 bags」「Buy 1 bags」などを単数（1 bag）にする。1回だけ実行する（2026-11-24）。
数字は表示のときに入るので en.json では直せない → 訳し終わった文の最後で直す。"""
import pathlib
root = pathlib.Path(__file__).resolve().parent.parent
html = root / "index.html"
s = html.read_text(encoding="utf-8")
if "function enSg(" in s:
    raise SystemExit("already patched")

OLD1 = "  function trOne(base){\n    if(lang===\"ja\")return base;"
assert s.count(OLD1) == 1
NEW1 = r'''  /* 2026-11-24：英語で数が1のときは単数に（1 bags → 1 bag）。前が数字・小数点・カンマ・¥のときは直さない（11 bags・0.1・2,001 など） */
  var ENSG={bags:"bag",plots:"plot",blocks:"block",years:"year",seasons:"season",stems:"stem",times:"time",wins:"win",things:"thing",places:"place",races:"race",buildings:"building",pages:"page",bottles:"bottle",machines:"machine",animals:"animal",guests:"guest",visitors:"visitor",fields:"field",eggs:"egg",workplaces:"workplace",departments:"department",cows:"cow",flowers:"flower",openings:"opening",sections:"section",racehorses:"racehorse",batches:"batch",guides:"guide",cookies:"cookie",employees:"employee",requests:"request",stores:"store",spots:"spot",people:"person",seconds:"second",minutes:"minute",days:"day",hours:"hour",items:"item",seeds:"seed",units:"unit",heads:"head",colonies:"colony"};
  var ENSGRX=new RegExp("(^|[^0-9.,¥$])1 ("+Object.keys(ENSG).join("|")+")(?![A-Za-z])","g");
  function enSg(x){return typeof x==="string"&&x.indexOf("1 ")>=0?x.replace(ENSGRX,function(_,p,w){return p+"1 "+ENSG[w]}):x}
  function trOne(base){
    if(lang==="ja")return base;'''
s = s.replace(OLD1, NEW1, 1)

OLD2 = "var e0=enLook(base);if(e0){c0[base]=e0;return e0}}"
assert s.count(OLD2) == 1
s = s.replace(OLD2, "var e0=enLook(base);if(e0){e0=enSg(e0);c0[base]=e0;return e0}}", 1)

OLD3 = "    c[base]=out;return out;\n  }"
assert s.count(OLD3) == 1
s = s.replace(OLD3, "    if(lang===\"en\")out=enSg(out);\n    c[base]=out;return out;\n  }", 1)
html.write_text(s, encoding="utf-8")
print("patched")
