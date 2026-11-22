import json,sys
p='/home/claude/nonbiri-bokujo/i18n/en.json'
d=json.load(open(p,encoding='utf-8'))
def add(section,items):
    d.setdefault(section,{})
    for k,v in items.items():
        d[section][k]=v
def save():
    for sec in d: d[sec]=dict(sorted(d[sec].items()))
    json.dump(d,open(p,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print({k:len(v) for k,v in d.items()})
