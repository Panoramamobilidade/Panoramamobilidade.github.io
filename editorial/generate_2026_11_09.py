#!/usr/bin/env python3
"""Rebuild only the approved Nov 9 edition from durable bilingual selection.
No source searches, no older-edition or Notion writes. Run from any directory.
"""
from pathlib import Path
import json,re,html,csv,collections,unicodedata,hashlib
ROOT=Path(__file__).resolve().parents[1]; E=ROOT/'editorial'
DATA=json.loads((E/'selected-2026-11-09.json').read_text()); CARDS=DATA['cards']; DATE=DATA['date']
escape=lambda s:html.escape(str(s),quote=True)
def norm(s):
 return ''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if not unicodedata.combining(c))
# The regional navigation retains the two previously approved empty sections.
COUNTRIES=[('Argentina','argentina','🇦🇷','Argentina','Argentina'),('Bolivia','bolivia','🇧🇴','Bolívia','Bolivia'),('Brasil','brasil','🇧🇷','Brasil','Brasil'),('Chile','chile','🇨🇱','Chile','Chile'),('Colombia','colombia','🇨🇴','Colômbia','Colombia'),('Costa Rica','costa-rica','🇨🇷','Costa Rica','Costa Rica'),('Equador','equador','🇪🇨','Equador','Ecuador'),('El Salvador','el-salvador','🇸🇻','El Salvador','El Salvador'),('Guatemala','guatemala','🇬🇹','Guatemala','Guatemala'),('Mexico','mexico','🇲🇽','México','México'),('Panama','panama','🇵🇦','Panamá','Panamá'),('Paraguay','paraguai','🇵🇾','Paraguai','Paraguay'),('Peru','peru','🇵🇪','Peru','Perú'),('Uruguay','uruguai','🇺🇾','Uruguai','Uruguay'),('Venezuela','venezuela','🇻🇪','Venezuela','Venezuela')]
SIGNALS={'pt':{'op':'🟢 Oportunidade/avanço','watch':'🟡 Acompanhar','risk':'🔴 Alerta/risco','monitor':'🔵 Monitoramento'},'es':{'op':'🟢 Oportunidad/avance','watch':'🟡 Seguimiento','risk':'🔴 Alerta/riesgo','monitor':'🔵 Monitoreo'}}
# Explicit evidence-backed member-to-card associations. All other chips are inert.
CITED={'ualabee':'ARG-01','metro de sao paulo':'BRA-existing-1','companhia do metropolitano de sao paulo':'BRA-existing-1','efe':'CHI-01','efe trenes':'CHI-01','aresep':'COS-01','transporte de pasajeros quito':'EQU-02','atu lima-callao':'PER-01','semov edomex':'MEX-01'}
counts=collections.Counter(c['country'] for c in CARDS); signals=collections.Counter(c['signal'] for c in CARDS)
assert len(CARDS)==34 and len(counts)==13
assert counts=={'Argentina':2,'Bolivia':2,'Brasil':10,'Chile':2,'Colombia':2,'Costa Rica':2,'Equador':2,'Guatemala':2,'Mexico':4,'Panama':1,'Paraguay':2,'Peru':2,'Uruguay':1}
assert len({c['id'] for c in CARDS})==34 and len({c['source_url'] for c in CARDS})==34
assert 'BOL-02' not in {c['id'] for c in CARDS}
# Hash older editions before writing to demonstrate scope preservation.
old={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'edicoes').rglob('*.html') if DATE not in str(p)}

def card(c,lang,label):
 source_lang='PT' if c['country']=='Brasil' else 'ES'
 institutional=c['source'] in ['Prefeitura de Porto Alegre','EFE','Quito Informa','Ministério das Cidades']
 sector=c['source'] in ['Via Trolebus','Diário do Transporte','Technibus','Agência iNFRA','Pasajero7','Autocosmos Colombia']
 source_class=('Fonte institucional' if lang=='pt' else 'Fuente institucional') if institutional else (('Imprensa setorial' if lang=='pt' else 'Prensa sectorial') if sector else ('Imprensa jornalística' if lang=='pt' else 'Prensa periodística'))
 date='/'.join(reversed(c['source_publication_date'].split('-')))
 fields=('Resumo','Por que importa') if lang=='pt' else ('Resumen','Por qué importa')
 return f'''<article class="card" id="card-{escape(c['id'])}"><div><span class="badge {c['signal']}">{SIGNALS[lang][c['signal']]}</span></div><div class="meta">{label} · {source_lang} · {source_class} · {escape(c['theme_'+lang])} · {date}</div><h3>{escape(c['title_'+lang])}</h3><div class="field"><strong>{fields[0]}:</strong> {escape(c['summary_'+lang])}</div><div class="field"><strong>{fields[1]}:</strong> {escape(c['impact_'+lang])}</div><div class="meta source">{escape(c['source'])}</div><a class="btn" href="{escape(c['source_url'])}" target="_blank" rel="noopener">{'Saiba mais' if lang=='pt' else 'Leer más'}</a></article>'''

def member_row(country,lang):
 chips=[]; seen=set()
 for m in DATA['members']:
  mapped_country={'paraguai':'paraguay','uruguai':'uruguay','ecuador':'equador'}.get(norm(m['country']),norm(m['country']))
  if m['tipo_fonte']!='associado_uitp' or mapped_country!=norm(country): continue
  name=m['name']; key=norm(name)
  if key in seen: continue
  seen.add(key); target=CITED.get(key)
  if target: chips.append(f'<a class="member-chip active" href="#card-{target}">{escape(name)}</a>')
  else: chips.append(f'<span class="member-chip">{escape(name)}</span>')
 return '<div class="member-buttons"><span class="member-buttons-label">'+('Associados UITP:' if lang=='pt' else 'Asociados UITP:')+'</span>'+''.join(chips)+'</div>'

def summary(lang):
 dist=', '.join(f'{c[3 if lang=="pt" else 4]} ({counts[c[0]]})' for c in COUNTRIES if counts[c[0]])
 if lang=='pt':
  p=f'Esta edição reúne <strong>34 notícias estratégicas em 13 países</strong>: {dist}. O Brasil concentra dez cards e o México, quatro. <strong>Sinaleiros: {signals["op"]} oportunidades/avanços, {signals["watch"]} acompanhamentos, {signals["risk"]} alertas/riscos e {signals["monitor"]} monitoramentos.</strong> Eletrificação e financiamento se destacam ao lado de bilhetagem digital, integração de redes e segurança. A queda da demanda na província de Santa Fe e as extorsões no Peru reforçam riscos de receita e continuidade operacional. A edição inclui reportagens de 3 a 9 de novembro, com datas e estágios explícitos: propostas não são compras, balanços não são inaugurações e agendas futuras não são lançamentos concluídos. Panamá e Uruguai têm um item cada; os demais onze países com cobertura têm pelo menos dois. El Salvador e Venezuela permanecem sem notícia estratégica qualificada nesta rodada.'
  title='Resumo executivo'
 else:
  p=f'Esta edición reúne <strong>34 noticias estratégicas en 13 países</strong>: {dist}. Brasil concentra diez tarjetas y México, cuatro. <strong>Señales: {signals["op"]} oportunidades/avances, {signals["watch"]} seguimientos, {signals["risk"]} alertas/riesgos y {signals["monitor"]} monitoreos.</strong> La electrificación y el financiamiento destacan junto al recaudo digital, la integración de redes y la seguridad. La caída de la demanda en la provincia de Santa Fe y las extorsiones en Perú refuerzan riesgos de ingresos y continuidad operativa. La edición incluye notas del 3 al 9 de noviembre, con fechas y etapas explícitas: propuestas no son compras, balances no son inauguraciones y agendas futuras no son lanzamientos concluidos. Panamá y Uruguay tienen un artículo cada uno; los otros once países con cobertura tienen al menos dos. El Salvador y Venezuela permanecen sin noticia estratégica calificada en esta ronda.'
  title='Resumen ejecutivo'
 return f'<section class="box"><h2>{title}</h2><p>{p}</p></section>'

for lang in ['pt','es']:
 template=(E/f'approved-template-{lang}.html').read_text()
 assert all(template.count(x)==1 for x in ['{{SUMMARY}}','{{JUMP}}','{{COUNTRIES}}'])
 sections=[]; jumps=[]
 for country,slug,flag,pt,es in COUNTRIES:
  label=pt if lang=='pt' else es; items=[c for c in CARDS if c['country']==country]; n=len(items)
  empty='Sem notícia estratégica qualificada nesta rodada.' if lang=='pt' else 'Sin noticia estratégica calificada en esta ronda.'
  count=(f'{n} '+('notícia estratégica validada nesta edição.' if n==1 else 'notícias estratégicas validadas nesta edição.')) if lang=='pt' else (f'{n} '+('noticia estratégica validada en esta edición.' if n==1 else 'noticias estratégicas validadas en esta edición.'))
  jumps.append(f'<a class="{"empty-jump" if not n else ""}" href="#{slug}">{flag} {label}</a>')
  sections.append(f'<section class="country" id="{slug}"><h2>{flag} {label}</h2><p class="count">{count if n else empty}</p>'+member_row(country,lang)+''.join(card(c,lang,label) for c in items)+'</section>')
 jump='<section class="box"><h2>'+('Ir direto para um país' if lang=='pt' else 'Ir directo a un país')+'</h2><div class="jump">'+''.join(jumps)+'</div></section>'
 out=template.replace('{{SUMMARY}}',summary(lang)).replace('{{JUMP}}',jump).replace('{{COUNTRIES}}',''.join(sections))
 target=ROOT/'edicoes'/DATE/('es/index.html' if lang=='es' else 'index.html'); target.parent.mkdir(parents=True,exist_ok=True); target.write_text(out)
 # Do not replace a newer current edition.
 current=ROOT/'hoje'/('es/index.html' if lang=='es' else 'index.html')
 dates=re.findall(r'20\d\d-\d\d-\d\d',current.read_text()) if current.exists() else []
 if not dates or max(dates)<=DATE: current.write_text(out)
 # Basic content and navigation QA.
 assert out.count('<article class="card"')==34
 ids=set(re.findall(r'\bid="([^"]+)"',out))
 for anchor in re.findall(r'href="#([^"]*)"',out): assert anchor in ids,anchor
 assert 'news.google.' not in out and '<i>' not in out
 assert out.count('class="member-buttons"')==15
 assert len(re.findall(r'<div class="ruler-item">[^<]+</div>',out))==4
 assert all(escape(c['source_url']) in out for c in CARDS)
 print(lang,'34 cards / 13 countries / 15 regional sections / no broken internal links')

# Preserve all historical index rows and update only the matching date.
index_path=ROOT/'arquivos/clippings_index.json'; index=json.loads(index_path.read_text()); target=next(x for x in index if x['date']==DATE)
target.update(cards=34,countries=13,country_counts=dict(counts),signal_counts=dict(signals))
index_path.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'arquivos/clippings_index.csv'
with p.open(newline='') as f: reader=csv.DictReader(f); headers=reader.fieldnames; csvrows=list(reader)
for row in csvrows:
 if row['date']==DATE:
  row.update(cards=34,countries=13,**{s:signals[s] for s in ['op','watch','risk','monitor']})
with p.open('w',newline='') as f:
 assert headers is not None
 writer=csv.DictWriter(f,fieldnames=headers,lineterminator='\n');writer.writeheader();writer.writerows(csvrows)
for name in ['index.html','arquivos/clippings/index.html']:
 p=ROOT/name; text=p.read_text(); text=text.replace('5 notícias estratégicas em 3 países','34 notícias estratégicas em 13 países');p.write_text(text)
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in old.items())
report={'date':DATE,'cards':34,'countries':13,'country_counts':dict(counts),'signal_counts':dict(signals),'older_edition_files_unchanged':len(old),'withheld':['BOL-02'],'pdf':'Not generated: established local PDF converters unavailable.','local_qa':'passed'}
(E/'qa-2026-11-09.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
