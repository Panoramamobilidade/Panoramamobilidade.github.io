#!/usr/bin/env python3
"""Durable, data-driven recovery edition. Never overwrites past editions."""
from pathlib import Path
import csv,json,html,re,collections,unicodedata
ROOT=Path(__file__).resolve().parents[1]; E=ROOT/'editorial'; DATE='2026-11-13'; BASE='https://panoramamobilidade.github.io'
COUNTRIES=[('Argentina','argentina','🇦🇷','Argentina','Argentina'),('Bolivia','bolivia','🇧🇴','Bolívia','Bolivia'),('Brasil','brasil','🇧🇷','Brasil','Brasil'),('Chile','chile','🇨🇱','Chile','Chile'),('Colombia','colombia','🇨🇴','Colômbia','Colombia'),('Costa Rica','costa-rica','🇨🇷','Costa Rica','Costa Rica'),('Equador','equador','🇪🇨','Equador','Ecuador'),('Guatemala','guatemala','🇬🇹','Guatemala','Guatemala'),('Mexico','mexico','🇲🇽','México','México'),('Panama','panama','🇵🇦','Panamá','Panamá'),('Paraguay','paraguai','🇵🇾','Paraguai','Paraguay'),('Peru','peru','🇵🇪','Peru','Perú'),('Uruguay','uruguai','🇺🇾','Uruguai','Uruguay')]
SIG={'pt':{'op':'🟢 Oportunidade/avanço','watch':'🟡 Acompanhar','risk':'🔴 Alerta/risco','monitor':'🔵 Monitoramento'},'es':{'op':'🟢 Oportunidad/avance','watch':'🟡 Seguimiento','risk':'🔴 Alerta/riesgo','monitor':'🔵 Monitoreo'}}
SOURCE_CLASS_ES={'Fonte institucional':'Fuente institucional','Imprensa setorial':'Prensa sectorial','Imprensa jornalística':'Prensa periodística'}
selection=json.loads((E/f'selected-{DATE}.json').read_text()); CARDS=selection['cards']; counts=collections.Counter(c['country']for c in CARDS); signals=collections.Counter(c['signal']for c in CARDS)
assert set(counts)<=set(c[0]for c in COUNTRIES)
assert len(set(c['id']for c in CARDS))==len(CARDS)==len(set(c['source_url']for c in CARDS))
for c in CARDS:assert '2026-11-06'<=c['source_publication_date']<=DATE and c['source_url'].startswith('https://')
escape=lambda x:html.escape(str(x),quote=True)
def norm(t):return ''.join(c for c in unicodedata.normalize('NFKD',t.lower())if not unicodedata.combining(c))
CN={'paraguai':'paraguay','uruguai':'uruguay','ecuador':'equador'}
with open('/opt/data/panorama_knowledge_base/uitp_associados_fontes_redes_master.csv',encoding='utf-8-sig',newline='')as f:
 members=[{'country':r['pais'],'name':r['nome_curto_alias_validado']or r['associado_uitp_nome_base'],'tipo_fonte':r['tipo_fonte']}for r in csv.DictReader(f)if r['tipo_fonte']=='associado_uitp']
selection['members']=members
(E/f'selected-{DATE}.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n')
CITED={'aresep':'COS-01','cutcsa':'URU-02','subterraneos de buenos aires s.e. (sbase)':'ARG-01','metro de santiago':'CHI-01','metro de bogota':'COL-01','metro de quito':'EQU-02','transporte de pasajeros quito':'EQU-01','municipalidad de guatemala':'GUA-01','metro cdmx':'MEX-03','atu lima-callao':'PER-01','metro de sao paulo':'BRA-02','motiva trilhos':'BRA-06'}
def member_row(country,lang):
 chips=[];seen=set();key=CN.get(norm(country),norm(country))
 for m in members:
  if CN.get(norm(m['country']),norm(m['country']))!=key:continue
  n=norm(m['name'])
  if n in seen:continue
  seen.add(n);target=CITED.get(n)
  chips.append(f'<a class="member-chip active" href="#card-{target}">{escape(m["name"])}</a>'if target else f'<span class="member-chip">{escape(m["name"])}</span>')
 return '<div class="member-buttons"><span class="member-buttons-label">'+('Associados UITP:'if lang=='pt'else'Asociados UITP:')+'</span>'+''.join(chips)+'</div>'
def card(c,lang,label):
 cls=c['source_class']if lang=='pt'else SOURCE_CLASS_ES[c['source_class']];day='/'.join(reversed(c['source_publication_date'].split('-')))
 source=c['source']
 if c['id']=='PER-01':source='Gestión · '+('conteúdo para assinantes'if lang=='pt'else'contenido para suscriptores')
 return f'''<article class="card" id="card-{c['id']}"><div><span class="badge {c['signal']}">{SIG[lang][c['signal']]}</span></div><div class="meta">{label} · {'PT'if c['country']=='Brasil'else'ES'} · {cls} · {escape(c['theme_'+lang])} · {day}</div><h3>{escape(c['title_'+lang])}</h3><div class="field"><strong>{'Resumo'if lang=='pt'else'Resumen'}:</strong> {escape(c['summary_'+lang])}</div><div class="field"><strong>{'Por que importa'if lang=='pt'else'Por qué importa'}:</strong> {escape(c['impact_'+lang])}</div><div class="meta source">{escape(source)}</div><a class="btn" href="{escape(c['source_url'])}" target="_blank" rel="noopener">{'Saiba mais'if lang=='pt'else'Leer más'}</a></article>'''
def summary(lang):
 included=', '.join(f'{pt if lang=="pt"else es} ({counts[c]})'for c,_,_,pt,es in COUNTRIES if counts[c]); short=', '.join(pt if lang=='pt'else es for c,_,_,pt,es in COUNTRIES if counts[c]<2)
 if lang=='pt':
  text=f'Esta edição reúne <strong>{len(CARDS)} notícias estratégicas em {len(counts)} países</strong>: {included}. <strong>Sinaleiros: {signals["op"]} oportunidades/avanços, {signals["watch"]} acompanhamentos, {signals["risk"]} alertas/riscos e {signals["monitor"]} monitoramentos.</strong> Financiamento e renovação de frota no Brasil e regulação, acessibilidade e implantação ferroviária no México concentram a agenda. Pagamentos digitais, qualidade do serviço e governança completam a leitura regional. <strong>{short} têm uma notícia cada; a cobertura de duas por país permanece incompleta.</strong> As datas das fontes estão nos cards; a edição também recupera fatos ainda não publicados nesta seleção dos últimos sete dias.'
 else:
  text=f'Esta edición reúne <strong>{len(CARDS)} noticias estratégicas en {len(counts)} países</strong>: {included}. <strong>Señales: {signals["op"]} oportunidades/avances, {signals["watch"]} seguimientos, {signals["risk"]} alertas/riesgos y {signals["monitor"]} monitoreos.</strong> Financiación y renovación de flota en Brasil y regulación, accesibilidad e implantación ferroviaria en México concentran la agenda. Pagos digitales, calidad del servicio y gobernanza completan la lectura regional. <strong>{short} tienen una noticia cada; la cobertura de dos por país sigue incompleta.</strong> Las fechas de las fuentes figuran en las tarjetas; la edición también recupera hechos aún no publicados en esta selección de los últimos siete días.'
 return f'<section class="box"><h2>{"Resumo executivo"if lang=="pt"else"Resumen ejecutivo"}</h2><p>{text}</p></section>'
def build(lang):
 t=(E/f'approved-template-{lang}.html').read_text();t=t.replace('09/11/2026','13/11/2026').replace('9 de novembro de 2026','13 de novembro de 2026').replace('9 de noviembre de 2026','13 de noviembre de 2026').replace('/edicoes/2026-11-08/','/edicoes/2026-11-12/')
 sections=[];jumps=[]
 for c,slug,flag,pt,es in COUNTRIES:
  label=pt if lang=='pt'else es;items=[x for x in CARDS if x['country']==c];n=len(items);jumps.append(f'<a href="#{slug}">{flag} {label}</a>')
  ct=f'{n} '+(('notícia estratégica validada nesta edição.'if n==1 else'notícias estratégicas validadas nesta edição.')if lang=='pt'else('noticia estratégica validada en esta edición.'if n==1 else'noticias estratégicas validadas en esta edición.'))
  sections.append(f'<section class="country" id="{slug}"><h2>{flag} {label}</h2><p class="count">{ct}</p>{member_row(c,lang)}'+''.join(card(x,lang,label)for x in items)+'</section>')
 jump=f'<section class="box country-jump"><h2 class="jump-title">{"Ir direto para um país"if lang=="pt"else"Ir directo a un país"}</h2><div class="jump jump-buttons">'+''.join(jumps)+'</div></section>'
 t=t.replace('{{SUMMARY}}',summary(lang)).replace('{{JUMP}}',jump).replace('{{COUNTRIES}}',''.join(sections))
 # Preserve all approved styles; ensure the existing mobile jump is scrollable.
 t=t.replace('</style>','@media(max-width:720px){.country-jump .jump-buttons{flex-wrap:nowrap;max-width:100%;overflow-x:auto}.country-jump .jump-buttons a{flex-shrink:0}}</style>')
 assert t.count('<article class="card"')==len(CARDS)and t.count('class="member-buttons"')==len(COUNTRIES)
 assert 'news.google.'not in t and '{{'not in t
 ids=set(re.findall(r'\bid="([^"]+)"',t))
 for target in re.findall(r'href="#([^"]+)"',t):assert target in ids,target
 return t
outputs={'pt':build('pt'),'es':build('es')}
current=(ROOT/'hoje/index.html').read_text();dates=re.findall(r'(\d{2})/(\d{2})/(202\d)',current[:3000]);current_date=max((f'{y}-{m}-{d}'for d,m,y in dates),default='0000-00-00')
assert current_date<=DATE,f'Newer current edition {current_date}; do not roll back'
for lang,text in outputs.items():
 for dest in [ROOT/f'edicoes/{DATE}'/('es/index.html'if lang=='es'else'index.html'),ROOT/'hoje'/('es/index.html'if lang=='es'else'index.html')]:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text)
landing=ROOT/'index.html';t=landing.read_text();t=re.sub(r'A edição de .*? reúne \d+ notícias estratégicas em \d+ países, com fontes originais e leitura em português e espanhol\.',f'A edição de 13 de novembro de 2026 reúne {len(CARDS)} notícias estratégicas em {len(counts)} países, com fontes originais e leitura em português e espanhol.',t);t=re.sub(r'Disponível:</strong>.*?</p>','Disponível:</strong> 13 de novembro de 2026.</p>',t);t=re.sub(r'edicoes/2026-11-\d{2}/',f'edicoes/{DATE}/',t);landing.write_text(t)
idx=ROOT/'arquivos/clippings_index.json';rows=json.loads(idx.read_text());rows=[r for r in rows if r['date']!=DATE]
entry={'date':DATE,'pt_html_path':f'edicoes/{DATE}/index.html','es_html_path':f'edicoes/{DATE}/es/index.html','pt_pdf_path':None,'es_pdf_path':None,'pt_html_url':f'{BASE}/edicoes/{DATE}/','es_html_url':f'{BASE}/edicoes/{DATE}/es/','pt_pdf_url':None,'es_pdf_url':None,'cards':len(CARDS),'countries':len(counts),'country_counts':dict(counts),'signal_counts':dict(signals)}
rows=sorted([entry]+rows,key=lambda x:x['date'],reverse=True);idx.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
csvpath=ROOT/'arquivos/clippings_index.csv'
with csvpath.open(newline='')as f:reader=csv.DictReader(f);headers=reader.fieldnames;old=[r for r in reader if r['date']!=DATE]
assert headers is not None
new={h:''for h in headers};new.update(date=DATE,pt_html=entry['pt_html_url'],es_html=entry['es_html_url'],cards=str(len(CARDS)),countries=str(len(counts)),**{s:str(signals[s])for s in ['op','watch','risk','monitor']})
with csvpath.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=headers,lineterminator='\n');w.writeheader();w.writerows([new]+old)
archive=ROOT/'arquivos/clippings/index.html';t=archive.read_text();t=re.sub(r'Total arquivado: \d+ edições · Atualizado em .*?\.',f'Total arquivado: {len(rows)} edições · Atualizado em 13 de novembro de 2026.',t);t=re.sub(r'<article class="card"><h2>2026-11-13</h2>.*?</article>','',t,flags=re.S);entry_html=f'<article class="card"><h2>{DATE}</h2><p>PANORAMA Mobilidade LATAM — {len(CARDS)} notícias estratégicas em {len(counts)} países.</p><div class="links"><a href="/edicoes/{DATE}/">HTML PT</a><a href="/edicoes/{DATE}/es/">HTML ES</a></div></article>';t=t.replace('<article class="card"><h2>2026-11-12</h2>',entry_html+'<article class="card"><h2>2026-11-12</h2>',1);archive.write_text(t)
qa={'date':DATE,'cards':len(CARDS),'countries':len(counts),'country_counts':dict(counts),'signal_counts':dict(signals),'country_shortfalls':selection['country_shortfalls'],'google_news_final_urls':0,'local_qa':'passed','pdf':'not generated: established WeasyPrint converter missing libpangoft2-1.0-0','public_qa':'not deployed'}
(E/f'qa-{DATE}.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n');print(json.dumps(qa,ensure_ascii=False))
