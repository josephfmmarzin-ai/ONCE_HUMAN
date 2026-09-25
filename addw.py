import json,sys
p='data/details/weapons.json'; d=json.load(open(p)); new=json.load(sys.stdin)
for k,v in new.items(): v.setdefault('source','oncehumandb.com'); d[k]=v
json.dump(d,open(p,'w'),ensure_ascii=False,indent=1); print(len(d),'armes détaillées')
