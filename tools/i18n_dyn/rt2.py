import json,sys,re
from playwright.sync_api import sync_playwright
segs=json.load(open('segs2.json'))
todo=set(json.load(open('todo.json')))
keys=[k for k in segs if k in todo]
def samp(h):
    if 'yen(' in h or 'Yen' in h: return '¥1,200'
    if re.search(r'\.icon\b',h) and '+' not in h: return '🥬'
    if re.search(r'name|label|Name|Label|title|NAME',h): return 'キャベツ'
    return '12'
inst=[]
for k in keys:
    hs=segs[k]['holes']
    inst.append(re.sub(r'\{(\d+)\}',lambda m: samp(hs[int(m.group(1))-1]) if int(m.group(1))-1<len(hs) else '12',k))
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
    pg=b.new_page()
    pg.add_init_script("localStorage.setItem('nonbiriFarm_lang','en')")
    pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(4000)
    res=pg.evaluate("a=>a.map(t=>window.__lsT(t))",inst)
    b.close()
JP=re.compile('[぀-ヿ一-鿿]')
ng=[k for k,r in zip(keys,res) if JP.search(r)]
ok=[(i,r) for k,i,r in zip(keys,inst,res) if not JP.search(r)]
print('checked',len(keys),'still NG',len(ng)); print(ok[:15])
json.dump(ng,open(sys.argv[1] if len(sys.argv)>1 else 'ng_out.json','w'),ensure_ascii=False)
json.dump({k:segs[k]['holes'] for k in ng},open('holes_out.json','w'),ensure_ascii=False)
