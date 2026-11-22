import sys,re; sys.path.insert(0,'/home/claude/work'); from merge import *
def parse(block):
    out={}
    for line in block.strip().split('\n'):
        line=line.strip()
        if not line or line.startswith('##'): continue
        k,v=line.split(' ||| ')
        k=k.replace('\\u3000','\u3000').replace('\\n','\n'); v=v.replace('\\n','\n')
        n=[0]
        def r(m): n[0]+=1; return '{%d}'%n[0]
        k=re.sub('#',r,k)
        # sanity: placeholders count
        ph=set(re.findall(r'\{\d+\}',v)); kh=set(re.findall(r'\{\d+\}',k))
        if not ph<=kh: print('PH MISMATCH',k,v)
        out[k]=v
    return out
