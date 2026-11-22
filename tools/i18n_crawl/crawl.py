import sys,json,time,re
sys.path.insert(0,'/home/claude/crawl')
from boot import *
BAD=re.compile(r'やり直し|Start over|NEW GAME|はじめから|From the beginning|リセット|削除|Delete|引き継ぎコードを読|⤢|全画面|日本語|简体|繁體|한국어|English|ログアウト')
CLOSE_JS=r"""()=>{let n=0;for(const s of ['#lsModalX','.lsX','.mx','.close','[aria-label="閉じる"]','[aria-label="Close"]']){for(const e of document.querySelectorAll(s)){const r=e.getBoundingClientRect();if(r.width>2&&r.height>2){e.click();n++}}}
 for(const e of document.querySelectorAll('button')){const t=(e.innerText||'').trim();const r=e.getBoundingClientRect();if(r.width>2&&/^(OK|閉じる|とじる|Close|×|✕|いいえ|No|キャンセル|Cancel|もどる|戻る|Back)$/.test(t)){e.click();n++}}return n}"""
def closeall(g):
    for i in range(4):
        n=g.pg.evaluate(CLOSE_JS); g.pg.evaluate(SKIP); g.pg.keyboard.press('Escape')
        if not n: break
        time.sleep(0.4)
def run(tab,depth=2,budget=900,out='out'):
    g=boot('/home/claude/crawl/save1.json')
    found=set(g.dump()); t0=time.time(); clicked=set()
    def go_tab():
        closeall(g); g.pg.evaluate("(id)=>{const e=document.getElementById(id); if(e) e.click()}",tab); time.sleep(0.8)
    def explore(path,d):
        if time.time()-t0>budget: return
        cs=[c for c in g.clickables() if c['x']>215 and c['y']>70 and not BAD.search(c['t'])]
        for c in cs:
            if time.time()-t0>budget: return
            key=tuple(path)+(c['t'],)
            if key in clicked or not c['t']: continue
            clicked.add(key)
            # replay path
            go_tab()
            ok=True
            for pt in path:
                if not g.vclick(pt,0.7): ok=False;break
            if not ok: continue
            if not g.vclick(c['t'],0.9): continue
            new=g.dump(); found.update(new)
            if d<depth: explore(path+[c['t']],d+1)
    go_tab(); found.update(g.dump())
    explore([],1)
    json.dump(sorted(found),open(f'/home/claude/crawl/{out}_{tab}.json','w'),ensure_ascii=False,indent=0)
    print(tab,len(found),'errs',g.errs[:2],'time',int(time.time()-t0)); g.close()
if __name__=='__main__':
    run(sys.argv[1],int(sys.argv[2]) if len(sys.argv)>2 else 2,int(sys.argv[3]) if len(sys.argv)>3 else 900)
