import json,re,time
from playwright.sync_api import sync_playwright
JP=re.compile(r'[぀-ヿ一-鿿]')
DUMP_JS=r"""
() => {
 const JP=/[぀-ヿ一-鿿]/; const out=new Set();
 const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT|NodeFilter.SHOW_ELEMENT);
 let n; while((n=w.nextNode())){
  if(n.nodeType===1){ if(/^(SCRIPT|STYLE)$/.test(n.nodeName)) continue;
    for(const a of ['title','aria-label','placeholder','data-lab']){const v=n.getAttribute&&n.getAttribute(a); if(v&&JP.test(v)) out.add('@'+v.trim())}
    continue}
  const p=n.parentNode; if(p&&/^(SCRIPT|STYLE)$/.test(p.nodeName)) continue;
  const t=(n.nodeValue||'').trim(); if(t&&JP.test(t)) out.add(t);
 }
 // pseudo content
 return [...out];
}"""
class G:
    def __init__(s,lang='en',save=None,w=1280,h=720):
        s.p=sync_playwright().start()
        s.b=s.p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
        s.ctx=s.b.new_context(viewport={'width':w,'height':h},has_touch=False)
        init="localStorage.setItem('nonbiriFarm_lang','%s');"%lang
        if save: init+="if(!sessionStorage.getItem('_s')){localStorage.setItem('nonbiriFarmSave',%s);sessionStorage.setItem('_s','1')}"%json.dumps(save)
        s.ctx.add_init_script(init)
        s.pg=s.ctx.new_page(); s.errs=[]
        s.pg.on('pageerror',lambda e:s.errs.append(str(e)))
        s.seen=set()
    def go(s):
        s.pg.goto('http://localhost:8765/index.html'); time.sleep(3)
    def dump(s,tag=''):
        r=s.pg.evaluate(DUMP_JS); new=[x for x in r if x not in s.seen]; s.seen.update(r); return new
    def click_text(s,txt,exact=False,timeout=1500):
        loc=s.pg.get_by_text(txt,exact=exact).first
        try: loc.click(timeout=timeout); time.sleep(0.6); return True
        except Exception as e: return False
    def close(s): s.b.close(); s.p.stop()
CLICK_JS=r"""
(t) => { const els=[...document.querySelectorAll('button,a,div,span,[onclick]')].filter(e=>{const r=e.getBoundingClientRect();
  if(r.width<2||r.height<2) return false; const cs=getComputedStyle(e); if(cs.visibility==='hidden'||cs.display==='none'||+cs.opacity===0) return false;
  return (e.innerText||'').trim()===t || (e.innerText||'').trim().startsWith(t)});
  els.sort((a,b)=>(a.innerText||'').length-(b.innerText||'').length);
  if(!els.length) return false; const e=els[0]; const r=e.getBoundingClientRect(); return [r.x+r.width/2,r.y+r.height/2];
}"""
def vclick(g,t,wait=0.6):
    p=g.pg.evaluate(CLICK_JS,t)
    if not p: return False
    g.pg.mouse.click(p[0],p[1]); time.sleep(wait); return True
G.vclick=vclick
LIST_JS=r"""
(sel) => { const out=[]; const root=sel?document.querySelector(sel):document.body; if(!root) return out;
 for(const e of root.querySelectorAll('button,[onclick],.card,a,[role=button],.lsTab,.tab')){
  const r=e.getBoundingClientRect(); if(r.width<4||r.height<4||r.bottom<0||r.top>innerHeight) continue;
  const cs=getComputedStyle(e); if(cs.visibility==='hidden'||cs.pointerEvents==='none') continue;
  const el=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2); if(!el||!(e===el||e.contains(el))) continue;
  out.push({t:(e.innerText||e.getAttribute('aria-label')||e.title||'').trim().slice(0,60),x:r.x+r.width/2,y:r.y+r.height/2,id:e.id,c:e.className&&e.className.baseVal===undefined?e.className:''});
 } return out;}"""
def clickables(g,sel=None): return g.pg.evaluate(LIST_JS,sel)
G.clickables=clickables
