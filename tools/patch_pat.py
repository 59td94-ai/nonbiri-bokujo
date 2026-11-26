#!/usr/bin/env python3
"""2026-11-25：英語のとき、名前や数字をつなげて作る文を「ひな形」で訳す（en.json の pat）。1回だけ実行する。
・ひな形の {1}{2}… にはどんな文字列が入ってもよい。入った部分に日本語があれば、その部分も訳す（訳せなければそのひな形は使わない）
・先頭の絵文字は外して試し、あとで戻す
・「・」などで区切って訳す処理（enSeg）からも使う
・会話の「（タップで戻す）」は CSS の文字なので、英語のときだけ CSS で置きかえる"""
import pathlib
FN = '  var ENP=[];\n  function enPat(base){\n    if(!ENP.length||!JPX.test(base)||enPat._d>6)return null;\n    enPat._d=(enPat._d||0)+1;\n    try{for(var i=0;i<ENP.length;i++){var p=ENP[i];if(base.indexOf(p[0])<0)continue;var m=base.match(p[1]);if(!m)continue;var ok=true;\n      var r=p[2].replace(/\\{(\\d+)\\}/g,function(_,q){var g=m[+q];if(g==null)return "";if(!JPX.test(g))return g;var t=g.trim(),x=trOne(t);if(JPX.test(x)){ok=false;return g}return g.replace(t,x)});\n      if(ok)return r.replace(/([A-Za-z])\\((?!e?s\\))/g,"$1 (")}\n      var pre=base.match(/^((?:[\\u{1F000}-\\u{1FAFF}\\u{2190}-\\u{21FF}\\u{2300}-\\u{27BF}\\u{2B00}-\\u{2BFF}]\\u{FE0F}?|[ \u3000・])+)/u);\n      if(pre&&pre[1].length<base.length){var r2=enPat(base.slice(pre[1].length));if(r2)return pre[1]+r2}\n    }finally{enPat._d--}\n    return null;\n  }\n'
root = pathlib.Path(__file__).resolve().parent.parent
html = root / "index.html"
s = html.read_text(encoding="utf-8")
if "function enPat(" in s:
    raise SystemExit("already patched")
A = "ENN=d.nouns||{};ENT=d.text||{};"
assert s.count(A) == 1
s = s.replace(A, A + "ENP=(d.pat||[]).map(function(x){return [x[0],new RegExp(x[1]),x[2]]});", 1)
B = "  function enLook(base){"
assert s.count(B) == 1
s = s.replace(B, FN + B, 1)
C = "var e0=enLook(base);"
assert s.count(C) == 1
s = s.replace(C, "var e0=enLook(base)||enPat(base);", 1)
D = "var x=FWD[p]?FWD[p][1]:null;if(!x)x=enLook(p);"
assert s.count(D) == 1
s = s.replace(D, D + "if(!x)x=enPat(p);", 1)
E = '#lsTalkScene.nowin .tl button:after{content:"（タップで戻す）";font-weight:normal;margin-left:4px}'
assert s.count(E) == 1
s = s.replace(E, E + 'html[data-ls-lang="en"] #lsTalkScene.nowin .tl button:after{content:"(tap to bring back)"}', 1)
F = 'if(lang==="en"&&window.__lsMiss&&JPX.test(base))'
assert s.count(F) == 1
s = s.replace(F, 'if(lang==="en"&&window.__lsMiss&&!enPat._d&&JPX.test(base))', 1)  # ひな形の中で試した部分は訳もれとして記録しない
html.write_text(s, encoding="utf-8")
print("patched")
