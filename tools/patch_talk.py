#!/usr/bin/env python3
"""会話シーン（1文字ずつ表示）で、英語のときは訳した文を1文字ずつ出すようにする。1回だけ実行する。
日本語・中国語・韓国語のときは今までどおり。"""
import pathlib
root = pathlib.Path(__file__).resolve().parent.parent
html = root / "index.html"
s = html.read_text(encoding="utf-8")
OLD = 'function lsLine(t){var p=window.__lsProfileGet?window.__lsProfileGet():{name:"牧場主",farm:"のんびり牧場"};return String(t).replace('
NEW = 'function lsLine(t){var p=window.__lsProfileGet?window.__lsProfileGet():{name:"牧場主",farm:"のんびり牧場"};var s0=String(t);try{if(window.__lsLang&&window.__lsLang()==="en"&&window.__lsT)s0=window.__lsT(s0)}catch(e){} /* 2026-11-22：英語は訳した文をタイプする */return s0.replace('
assert s.count(OLD) == 1, s.count(OLD)
s = s.replace(OLD, NEW, 1)
OLD2 = '/* 2026-11-22：英語は訳した文をタイプする */return s0.replace(/\\{name\\}/g,p.name).replace(/\\{farm\\}/g,p.farm)}'
NEW2 = '/* 2026-11-22：英語は訳した文をタイプする */var nm=p.name,fm=p.farm;try{if(window.__lsLang&&window.__lsLang()==="en"){if(nm==="牧場主")nm="Farm owner";if(fm==="のんびり牧場")fm="Nonbiri Farm"}}catch(e){}return s0.replace(/\\{name\\}/g,nm).replace(/\\{farm\\}/g,fm)}'
assert s.count(OLD2) == 1
s = s.replace(OLD2, NEW2, 1)
html.write_text(s, encoding="utf-8")
print("patched")
