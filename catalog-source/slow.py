import json,re,html,sys,time,urllib.request,urllib.error
S=sys.argv[1]; D=sys.argv[2]
exec(open(S+'/rescrape.py').read().split("todo=")[0].split("def parse",1)[0])  # imports
src=open(S+'/rescrape.py').read(); exec("def parse"+src.split("def parse",1)[1].split("todo=")[0])
d=json.load(open(D)); res=json.load(open(S+'/scraped.json'))
todo=[p for p in d['products'] if not res[p['id']]['ok']]
print('todo',len(todo),'— жду 20 мин, пока Tilda снимет блокировку',flush=True)
time.sleep(1200)
i=0; bans=0
while i < len(todo):
    p=todo[i]
    try:
        s=urllib.request.urlopen(urllib.request.Request(p['oldUrl'],headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read().decode('utf-8','ignore')
        res[p['id']]=parse(s); i+=1
        json.dump(res,open(S+'/scraped.json','w'),ensure_ascii=False)
        if i%10==0: print(i,'/',len(todo),flush=True)
        time.sleep(12)
    except urllib.error.HTTPError as e:
        if e.code==404: res[p['id']]={'ok':True,'teh':[],'outer':None,'inner':None,'prices':[],'missing':True}; i+=1; continue
        bans+=1; print('blocked',e.code,'at',i,'— пауза 15 мин',flush=True)
        if bans>8: break
        time.sleep(900)
    except Exception as e:
        print('err',e,flush=True); time.sleep(60)
print('done', sum(v['ok'] for v in res.values()), flush=True)
