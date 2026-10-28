"""Отделка «Внешняя / внутренняя панель» входных дверей — по расположению на страницах моделей старого сайта (Tilda).
Значение берём из текста, который стоит прямо под подписью «Внешняя панель» / «Внутренняя панель» на холсте блока.
Раньше панели брались по порядку строк в HTML — у части моделей туда попадали кнопки и заголовки, а у других
внешняя и внутренняя перепутывались. Страницы: catalog-source/sl-html/<id>.html (недостающие — копии web.archive.org).
Запуск: python3 catalog-source/panels.py  (потом python3 prototype-catalog/build.py)"""
import json, os
import re, html, sys
SL=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sl-html')
JUNK=re.compile(r'^(внешняя панель|внутренняя панель|отправить|сиетл)$|вернуться|дверь для дома|дверь с\s+терморазрыв|дверь в квартиру|стоимость|размеры|цена|^от\s*[\d\s]+р|\d+\s*[*x×]\s*\d+|^хаски\b|оставить заявку|запись на', re.I)
def clean(t):
    t=re.sub(r'<br\s*/?>','\n',t); t=re.sub(r'<[^>]+>',' ',t); t=html.unescape(t); t=re.sub(r'[ \t\xa0]+',' ',t)
    return re.sub(r'\s*\n\s*',' ',t).strip()
def records(path):
    t=open(path,encoding='utf-8').read()
    starts=[(m.start(),m.group(0)) for m in re.finditer(r'<div[^>]*\bid="rec\d+"[^>]*>',t)]
    for i,(s,tag) in enumerate(starts):
        smax=re.search(r'data-screen-max="(\d+)',tag)
        if smax and int(smax.group(1))<=980: continue
        e=starts[i+1][0] if i+1<len(starts) else len(t)
        yield t[s:e]
def elems(rec):
    out=[]
    ms=list(re.finditer(r"<div[^>]*class=['\"][^'\"]*\btn-elem\b[^'\"]*['\"][^>]*>",rec))
    for i,m in enumerate(ms):
        tag=m.group(0); g=lambda k:(re.search(r'data-field-%s-value=["\']([^"\']*)'%k,tag) or [0,''])[1]
        if (re.search(r'data-elem-type=["\'](\w+)',tag) or [0,''])[1]!='text': continue
        end=ms[i+1].start() if i+1<len(ms) else len(rec)
        n=lambda v: float(re.match(r'-?\d+(\.\d+)?',v).group(0)) if re.match(r'-?\d+',v or '') else None
        out.append({'x':n(g('left')),'y':n(g('top')),'w':n(g('width')) or 0,'txt':clean(rec[m.end():end])})
    return out
def panels(pid):
    path=os.path.join(SL,pid+'.html')
    if not os.path.exists(path): return {}
    res={}
    for rec in records(path):
        E=[e for e in elems(rec) if e['x'] is not None and e['y'] is not None]
        for lab,key in (('Внешняя панель','outer'),('Внутренняя панель','inner')):
            if key in res: continue
            for L in [e for e in E if e['txt']==lab and 0<=e['x']<=1250]:
                c=[e for e in E if e is not L and e['txt'] and not JUNK.search(e['txt']) and 0<e['y']-L['y']<=70
                   and e['x']<L['x']+L['w'] and e['x']+e['w']>L['x'] and len(e['txt'])<=140]
                if c:
                    res[key]=min(c,key=lambda e:e['y']-L['y'])['txt']; break
        if len(res)==2: break
    return res

if __name__ == '__main__':
    CAT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'prototype-catalog', 'data', 'catalog.json')
    d = json.load(open(CAT, encoding='utf-8'))
    n = 0
    for p in d['products']:
        got = panels(p['id'])
        if got:
            if (p.get('panels') or {}) != got:
                n += 1
            p['panels'] = got
    json.dump(d, open(CAT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('моделей с отделкой:', sum(1 for p in d['products'] if p.get('panels')), '| изменено:', n)
