import json,sys
p='data/details/weapons.json'; d=json.load(open(p)); new=json.load(sys.stdin)
for k,v in new.items():
    d.setdefault(k,{}); d[k].update(v); d[k].setdefault('source','oncehumandb.com')
json.dump(d,open(p,'w'),ensure_ascii=False,indent=1); print(len(d),'armes détaillées')
