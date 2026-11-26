import json,re
d=json.load(open('all.json'))
JP=re.compile('[぀-ヿ一-鿿]')
segs={}
for e in d:
    s='';hs=[]
    for x in e['parts']:
        if 's' in x: s+=x['s']
        else:
            if s.endswith('\x00'): hs[-1]+='+'+x['h']
            else: s+='\x00'; hs.append(x['h'])
    # split by tags keeping hole indices
    hi=0;cur='';curh=[];pieces=[]
    i=0
    toks=re.split(r'(<[^>]*>)',s)
    for t in toks:
        if t.startswith('<') and t.endswith('>'):
            hi+=t.count('\x00'); pieces.append((cur,curh)); cur='';curh=[]; continue
        for ch in t:
            if ch=='\x00': curh.append(hs[hi]); hi+=1
            cur+=ch
    pieces.append((cur,curh))
    for pc,ph in pieces:
        lead=len(pc)-len(pc.lstrip()); t=pc.strip()
        if not JP.search(t.replace('\x00','')): continue
        if '<' in t or '>' in t: continue
        n=[0];
        def rep(_): n[0]+=1; return '{%d}'%n[0]
        key=re.sub('\x00',rep,t)
        hh=ph[:]  # holes in order (strip doesn't remove holes)
        if key not in segs: segs[key]={'ctx':e['ctx'],'holes':hh}
json.dump(segs,open('segs2.json','w'),ensure_ascii=False)
print(len(segs))
