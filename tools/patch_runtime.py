#!/usr/bin/env python3
"""多言語スクリプトに英語の追加辞書（EN_EXTRA）を読む処理を足す。1回だけ実行する。"""
import pathlib
root = pathlib.Path(__file__).resolve().parent.parent
html = root / "index.html"
s = html.read_text(encoding="utf-8")
if "/*EN_EXTRA_BEGIN*/" in s:
    raise SystemExit("already patched")
OLD = "  function trOne(base){\n    if(lang===\"ja\")return base;"
assert s.count(OLD) == 1
NEW = r'''  /* 2026-11-22：英語の追加辞書（i18n/en.json → tools/build_en.py で埋め込み）。英語のときだけ使う */
  /*EN_EXTRA_BEGIN*/var EN_EXTRA="";/*EN_EXTRA_END*/
  var ENN={},ENT={},ENRX=null,JPX=/[぀-ヿ一-鿿]/;
  (function(){try{if(!EN_EXTRA||typeof DecompressionStream==="undefined")return;
    var bin=atob(EN_EXTRA),u=new Uint8Array(bin.length);for(var i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);
    new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream("gzip"))).text().then(function(tx){
      var d=JSON.parse(tx);ENN=d.nouns||{};ENT=d.text||{};
      var ks=Object.keys(ENN).sort(function(a,b){return b.length-a.length}).map(function(k){return k.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")});
      ENRX=ks.length?new RegExp(ks.join("|"),"g"):null;CACHE={};window.__lsEnReady=true;if(lang==="en")applyAll();
    }).catch(function(){});}catch(e){}})();
  var EMO=/[\u{1F000}-\u{1FAFF}\u{2190}-\u{21FF}\u{2300}-\u{27BF}\u{2B00}-\u{2BFF}\u{1F1E6}-\u{1F1FF}]\u{FE0F}?|\u{200D}|\u{FE0F}/gu;
  function enStrip(x){return x.replace(EMO,"").replace(/[ 　]{2,}/g," ").trim()}
  function enLook1(key,nums){
    var fill=function(x,ns){return x.replace(/\{(\d+)\}/g,function(_,i){return nums[i-1]!=null?nums[i-1]:""}).replace(/\{([A-Za-z])\}/g,function(_,c){var lo=c>="a",v=ns[c.toUpperCase().charCodeAt(0)-65];return v==null?"":lo?v.toLowerCase():v})};
    if(ENT[key])return fill(ENT[key],[]);
    if(ENRX){var ns=[],j=0,key2=key.replace(ENRX,function(m){ns.push(ENN[m]);return "{"+String.fromCharCode(65+(j++))+"}"});
      if(j&&ENT[key2])return fill(ENT[key2],ns);}
    return null;
  }
  function enLook(base){
    if(ENN[base])return ENN[base];
    var nums=[],k=0,key=base.replace(NUM,function(m){nums.push(m);return "{"+(++k)+"}"});
    var r=enLook1(key,nums);if(r)return r;
    var sk=enStrip(key);if(sk&&sk!==key){r=enLook1(sk,nums);
      if(r){var pre=base.match(/^((?:[\u{1F000}-\u{1FAFF}\u{2190}-\u{21FF}\u{2300}-\u{27BF}\u{2B00}-\u{2BFF}]\u{FE0F}?)+[ 　]?)/u);
        if(pre&&r.indexOf(pre[1].trim())!==0)r=pre[1]+r;return r}}
    return null;
  }
  var SEGRX=/(\s*[：:・／\/、。！？!?（）()「」『』【】〔〕\n→＋+×|]\s*|\s+)/;
  var SEGMAP={"：":": ","・":" · ","／":" / ","、":", ","。":". ","！":"! ","？":"? ","（":" (","）":")","「":"“","」":"”","『":"“","』":"”","【":"[","】":"]","〔":"(","〕":")","＋":"+"};
  function enSeg(base){
    var parts=base.split(SEGRX);if(parts.length<2)return null;var out="";
    for(var i=0;i<parts.length;i++){var p=parts[i];if(!p)continue;
      if(i%2===1){var t=p.trim();out+=(t&&SEGMAP[t]!==undefined)?SEGMAP[t]:p;continue}
      if(!JPX.test(p)){out+=p;continue}
      var x=FWD[p]?FWD[p][1]:null;if(!x)x=enLook(p);
      if(!x){var nums=[],k=0,key=p.replace(NUM,function(m){nums.push(m);return "{"+(++k)+"}"}),r=TPL[key];
        if(r&&r[0])x=r[0].replace(/\{(\d+)\}/g,function(_,q){return nums[q-1]!=null?nums[q-1]:""});}
      if(!x||JPX.test(x))return null;out+=x;}
    return out.replace(/ {2,}/g," ").replace(/\( /g,"(").replace(/ \)/g,")").replace(/^ | $/g,"");
  }
  function trOne(base){
    if(lang==="ja")return base;
    if(lang==="en"){var c0=CACHE.en||(CACHE.en={});if(base in c0)return c0[base];
      var e0=enLook(base);if(e0){c0[base]=e0;return e0}}'''
s = s.replace(OLD, NEW, 1)
OLD2 = "    if(!out)out=base;c[base]=out;return out;\n  }"
assert s.count(OLD2) == 1
NEW2 = "    if(!out&&lang===\"en\"&&!trOne._seg){trOne._seg=1;try{out=enSeg(base)}finally{trOne._seg=0}}\n    if(!out){out=base;if(lang===\"en\"&&window.__lsMiss&&JPX.test(base))window.__lsMiss.add(base.replace(NUM,function(){return \"#\"}))}\n    c[base]=out;return out;\n  }"
s = s.replace(OLD2, NEW2, 1)
html.write_text(s, encoding="utf-8")
print("patched")
