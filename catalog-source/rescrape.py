import json,re,html,sys,time,urllib.request
S=sys.argv[1]; D=sys.argv[2]
d=json.load(open(D)); res=json.load(open(S+'/scraped.json'))
def parse(s):
    teh=sorted(set(re.findall(r'https://steelline\.store/(teh[a-z0-9_-]*)',s)))
    t=re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>',' ',s)
    t=html.unescape(re.sub(r'<br\s*/?>','\n',t)); t=re.sub(r'<[^>]+>','\n',t); t=re.sub(r'[ \t ]+',' ',t)
    lines=[l.strip() for l in t.split('\n') if l.strip()]
    outer=inner=None
    if 'Внешняя панель' in lines:
        i=lines.index('Внешняя панель'); outer,inner=lines[i-2],lines[i-1]
    prices=re.findall(r'Стоимость в серии ([0-9А-ЯA-Za-z]+)\s*\n?\s*от ([0-9 ]+)р',t)
    return {'ok':True,'teh':teh,'outer':outer,'inner':inner,'prices':[(a,int(b.replace(' ',''))) for a,b in prices]}
todo=[p for p in d['products'] if not res[p['id']]['ok']]
print('todo',len(todo),flush=True)
for n,p in enumerate(todo):
    for attempt in range(4):
        try:
            s=urllib.request.urlopen(urllib.request.Request(p['oldUrl'],headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36','Accept-Language':'ru-RU,ru;q=0.9'}),timeout=30).read().decode('utf-8','ignore')
            res[p['id']]=parse(s); break
        except Exception as e:
            print(p['id'], 'ошибка', e, flush=True); time.sleep(60*(attempt+1))
    json.dump(res,open(S+'/scraped.json','w'),ensure_ascii=False)
    if n%20==0: print(n, sum(v['ok'] for v in res.values()), flush=True)
    time.sleep(5)
print('done', sum(v['ok'] for v in res.values()), flush=True)
