import sys,json,time; sys.path.insert(0,'/home/claude/crawl')
from boot import *
def shots(lang,prefix):
    g=boot('/home/claude/crawl/save1.json',lang=lang)
    g.pg.evaluate("()=>{window.__lsMiss=new Set()}")
    out={}
    for tab in ['tabHome','tabCrops','tabPoultry','tabMaterial','tabFactory','tabMall','tabShop','tabOffice']:
        g.pg.evaluate("(id)=>{const e=document.getElementById(id); if(e) e.click()}",tab); time.sleep(1.2)
        g.pg.screenshot(path=f'/home/claude/crawl/{prefix}_{tab}.png')
        out[tab]=g.pg.evaluate("()=>document.body.innerText")
    print(lang,'errs',g.errs[:3]); g.close(); return out
if __name__=='__main__':
    o=shots(sys.argv[1],sys.argv[2]); json.dump(o,open(f'/home/claude/crawl/{sys.argv[2]}.json','w'),ensure_ascii=False)
