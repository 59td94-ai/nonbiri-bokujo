import json,glob,re,sys
en=json.load(open('/home/claude/nonbiri-bokujo/i18n/en.json'))
T=en['text']; N=en['nouns']
def norm(x):
    n=[0]
    def r(m): n[0]+=1; return '{%d}'%n[0]
    return re.sub('#',r,x)
m=set()
for f in glob.glob(sys.argv[1] if len(sys.argv)>1 else '/home/claude/crawl/mk_*.json'):
    try: m|=set(json.load(open(f))['miss'])
    except Exception: pass
todo=[x for x in m if norm(x) not in T and x not in N]
# drop typewriter partials: if x is a proper prefix of another miss
allm=sorted(m)
pref=set()
for x in todo:
    for y in allm:
        if y!=x and y.startswith(x): pref.add(x); break
todo=[x for x in todo if x not in pref]
todo.sort(key=len)
json.dump(todo,open('/home/claude/work/pending.json','w'),ensure_ascii=False,indent=0)
print(len(m),'pending',len(todo),'partials',len(pref))
