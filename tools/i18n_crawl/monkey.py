import sys,json,time,re,random
sys.path.insert(0,'/home/claude/crawl')
from boot import *
from crawl import BAD,closeall
def run(seed,budget,save,out):
    random.seed(seed)
    g=boot(save,extra={})
    g.pg.evaluate("()=>{window.__lsMiss=new Set()}")
    # re-apply so existing nodes get logged
    g.pg.evaluate("()=>{if(window.__lsSetLang)window.__lsSetLang('en')}")
    t0=time.time(); n=0; found=set()
    while time.time()-t0<budget:
        cs=[c for c in g.clickables() if not BAD.search(c['t']) and c['id'] not in ('settingsBtn',)]
        if not cs: g.pg.keyboard.press('Escape'); time.sleep(0.3); continue
        # prefer tabs sometimes
        if random.random()<0.12:
            tabs=[c for c in cs if c['id'].startswith('tab')]
            c=random.choice(tabs) if tabs else random.choice(cs)
        else: c=random.choice(cs)
        g.pg.mouse.click(c['x'],c['y']); time.sleep(0.35); n+=1
        for _ in range(2): g.pg.evaluate(SKIP)
        if g.pg.locator('#lsNameCard input').count() and g.pg.locator('#lsNameCard input').first.is_visible():
            ins=g.pg.locator('#lsNameCard input'); ins.nth(0).fill('Hana'); ins.nth(1).fill('Sunny'); g.pg.locator('#lsNameCard button').last.click()
        if n%25==0:
            found.update(g.dump())
            m=g.pg.evaluate("()=>[...(window.__lsMiss||[])]"); json.dump({'miss':sorted(m),'dom':sorted(found)},open(out,'w'),ensure_ascii=False,indent=0)
    m=g.pg.evaluate("()=>[...(window.__lsMiss||[])]"); found.update(g.dump())
    json.dump({'miss':sorted(m),'dom':sorted(found)},open(out,'w'),ensure_ascii=False,indent=0)
    print(out,'clicks',n,'miss',len(m),'dom',len(found),'errs',g.errs[:3]); g.close()
if __name__=='__main__':
    run(int(sys.argv[1]),int(sys.argv[2]),sys.argv[3],sys.argv[4])
