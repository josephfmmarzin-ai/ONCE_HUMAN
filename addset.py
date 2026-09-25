import json,sys
sp='data/details/sets.json'; ap='data/details/armor.json'
S=json.load(open(sp)); A=json.load(open(ap)); new=json.load(sys.stdin)
for name,v in new.items():
    S[name]={"bonus":[{"pieces":(e[0] if isinstance(e,list) else i+1),"effect":(e[1] if isinstance(e,list) else e)} for i,e in enumerate(v["bonus"])],"rarity":v.get("rarity",""),"source":"oncehumandb.com"}
    for slug,pr in v.get("pr",{}).items():
        A.setdefault(slug,{}); A[slug]["set"]=name; A[slug]["pollution"]=pr; A[slug].setdefault("source","oncehumandb.com")
json.dump(S,open(sp,'w'),ensure_ascii=False,indent=1); json.dump(A,open(ap,'w'),ensure_ascii=False,indent=1)
print(len(S),'sets |',len(A),'pièces')
