from lib import *
SKIP="()=>{for(const s of document.querySelectorAll('#lsOpening .sk, .sk')){const r=s.getBoundingClientRect(); if(r.width) s.click()}}"
def boot(save=None,lang='en',extra=None,w=1280,h=720):
    g=G(lang=lang,w=w,h=h)
    sv=open(save).read() if save else None
    js="if(!sessionStorage.getItem('_s')){"
    if sv: js+="localStorage.setItem('nonbiriFarmSave',%s);"%json.dumps(sv)
    js+="localStorage.removeItem('nonbiriFarm_opening');"
    for k,v in (extra or {}).items(): js+="localStorage.setItem(%s,%s);"%(json.dumps(k),json.dumps(v))
    js+="sessionStorage.setItem('_s','1')}"
    g.ctx.add_init_script(js)
    g.go()
    g.pg.mouse.click(640,360); time.sleep(1.2)
    for i in range(8):
        g.pg.evaluate(SKIP); time.sleep(0.5)
        if g.pg.evaluate(CLICK_JS,'LOAD GAME'): break
        g.pg.mouse.click(640,360); time.sleep(0.6)
    g.vclick('LOAD GAME',2)
    for i in range(30):
        g.pg.evaluate(SKIP)
        if g.pg.locator('#lsNameCard input').count() and g.pg.locator('#lsNameCard input').first.is_visible():
            ins=g.pg.locator('#lsNameCard input'); ins.nth(0).fill('Hana'); ins.nth(1).fill('Sunny'); g.pg.locator('#lsNameCard button').last.click(); time.sleep(1)
        vis=g.pg.evaluate("()=>{const t=document.querySelector('#lsTalk,.lsTalk');return !!(t&&t.offsetParent)}")
        if not vis and i>3: break
        g.pg.mouse.click(640,640); time.sleep(0.35)
    return g
