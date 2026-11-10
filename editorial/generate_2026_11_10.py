#!/usr/bin/env python3
"""Publish the PANORAMA daily edition for 10 November 2026 from reviewed intake."""
from pathlib import Path
import csv, json, html, re, collections, unicodedata
ROOT = Path(__file__).resolve().parents[1]
E = ROOT / 'editorial'
DATE = '2026-11-10'

COUNTRIES = [
 ('Argentina','argentina','🇦🇷','Argentina','Argentina'), ('Bolivia','bolivia','🇧🇴','Bolívia','Bolivia'),
 ('Brasil','brasil','🇧🇷','Brasil','Brasil'), ('Chile','chile','🇨🇱','Chile','Chile'),
 ('Colombia','colombia','🇨🇴','Colômbia','Colombia'), ('Costa Rica','costa-rica','🇨🇷','Costa Rica','Costa Rica'),
 ('Equador','equador','🇪🇨','Equador','Ecuador'), ('El Salvador','el-salvador','🇸🇻','El Salvador','El Salvador'),
 ('Guatemala','guatemala','🇬🇹','Guatemala','Guatemala'), ('Mexico','mexico','🇲🇽','México','México'),
 ('Panama','panama','🇵🇦','Panamá','Panamá'), ('Paraguay','paraguai','🇵🇾','Paraguai','Paraguay'),
 ('Peru','peru','🇵🇪','Peru','Perú'), ('Uruguay','uruguai','🇺🇾','Uruguai','Uruguay'), ('Venezuela','venezuela','🇻🇪','Venezuela','Venezuela')]
SIG = {'pt': {'op':'🟢 Oportunidade/avanço','watch':'🟡 Acompanhar','risk':'🔴 Alerta/risco','monitor':'🔵 Monitoramento'},
       'es': {'op':'🟢 Oportunidad/avance','watch':'🟡 Seguimiento','risk':'🔴 Alerta/riesgo','monitor':'🔵 Monitoreo'}}

def c(id, country, signal, source, date, url, theme_pt, theme_es, title_pt, title_es, summary_pt, summary_es, impact_pt, impact_es, source_class='Imprensa setorial'):
    return dict(id=id,country=country,signal=signal,source=source,source_publication_date=date,source_url=url,theme_pt=theme_pt,theme_es=theme_es,title_pt=title_pt,title_es=title_es,summary_pt=summary_pt,summary_es=summary_es,impact_pt=impact_pt,impact_es=impact_es,source_class=source_class)

CARDS = [
 c('BRA-01','Brasil','watch','Diário do Transporte','2026-11-09','https://diariodotransporte.com.br/2026/11/09/metro-df-adia-para-25-de-novembro-licitacao-de-novo-sistema-de-controle-de-trens-que-inclui-expansoes-de-ceilandia-e-samambaia/','Sinalização ferroviária / licitação','Señalización ferroviaria / licitación','Metrô-DF remarca para 25 de novembro licitação do sistema CBTC da Linha 1','Metro-DF reprograma para el 25 de noviembre la licitación del sistema CBTC de la Línea 1','O Metrô-DF remarcou para 25 de novembro a sessão de recebimento de propostas para sinalização e controle de trens da Linha 1, após problema técnico informado pela comissão. O escopo inclui CBTC, telecomunicações e integração com a frota existente.','Metro-DF reprogramó para el 25 de noviembre la recepción de propuestas para señalización y control de trenes de la Línea 1, tras un problema técnico informado por la comisión. El alcance incluye CBTC, telecomunicaciones e integración con la flota existente.','É um reagendamento de licitação, não contratação nem implantação do sistema. A concorrência e a compatibilidade com futuras extensões serão os próximos marcos.' ,'Es una reprogramación de licitación, no una contratación ni la implantación del sistema. El concurso y la compatibilidad con futuras extensiones serán los próximos hitos.'),
 c('BRA-02','Brasil','watch','Diário do Transporte','2026-11-09','https://diariodotransporte.com.br/2026/11/09/belo-horizonte-republica-licitacao-para-trabalho-social-na-vila-guarata-ligado-a-implantacao-do-terminal-brt-amazonas/','Infraestrutura BRT / trabalho social','Infraestructura BRT / trabajo social','Belo Horizonte republica licitação de trabalho social ligado ao Terminal BRT Amazonas','Belo Horizonte republica una licitación de trabajo social vinculado a la Terminal BRT Amazonas','A prefeitura republicou pregão para elaborar e implementar o Projeto de Trabalho Social da Vila Guaratã, associado ao Terminal BRT Amazonas. A abertura das propostas está marcada para 18 de novembro.','La alcaldía republicó una licitación para elaborar e implementar el Proyecto de Trabajo Social de Vila Guaratã, asociado a la Terminal BRT Amazonas. La apertura de propuestas está prevista para el 18 de noviembre.','A etapa explicita a dimensão social preparatória de uma intervenção de infraestrutura. Não confirma construção do terminal, reassentamentos ou operação de linhas futuras.','La etapa explicita la dimensión social preparatoria de una intervención de infraestructura. No confirma la construcción de la terminal, reasentamientos ni la operación de rutas futuras.'),
 c('BRA-03','Brasil','watch','Diário do Transporte','2026-11-09','https://diariodotransporte.com.br/2026/11/09/novos-brts-metro-vlt-e-trens-regionais-distrito-federal-marca-audiencia-para-apresentar-plano-de-mobilidade-dos-proximos-dez-anos/','Planejamento de rede / participação pública','Planificación de red / participación pública','Distrito Federal abre audiência pública sobre plano decenal de mobilidade','Distrito Federal abre audiencia pública sobre un plan decenal de movilidad','A Secretaria de Transporte e Mobilidade do DF agendou para 11 de novembro audiência pública sobre o PDTU, com diretrizes para BRT, metrô, VLT e trens regionais no horizonte do plano.','La Secretaría de Transporte y Movilidad del DF programó para el 11 de noviembre una audiencia pública sobre el PDTU, con directrices para BRT, metro, tranvía y trenes regionales en el horizonte del plan.','A audiência abre uma etapa de participação e priorização de rede; não representa contratação, licitação ou implantação imediata das expansões citadas.','La audiencia abre una etapa de participación y priorización de red; no representa contratación, licitación ni implantación inmediata de las expansiones citadas.'),
 c('BRA-04','Brasil','watch','URBS Curitiba','2026-11-10','https://www.urbs.curitiba.pr.gov.br/noticia/urbs-abre-consulta-publica-sobre-revisao-tarifaria-do-transporte-coletivo','Tarifa / regulação / governança','Tarifa / regulación / gobernanza','Curitiba abre consulta sobre revisão tarifária anual de 2027','Curitiba abre consulta sobre la revisión tarifaria anual de 2027','A URBS abriu consulta pública para receber contribuições à revisão tarifária anual aplicável ao transporte coletivo de Curitiba em 2027. A divulgação não fixa valor de tarifa nem delibera reajuste.','URBS abrió una consulta pública para recibir aportes a la revisión tarifaria anual aplicable al transporte colectivo de Curitiba en 2027. La divulgación no fija un valor de tarifa ni decide un reajuste.','O processo antecipa um debate regulatório relevante para custos e usuários. A proposta técnica e a decisão tarifária ainda precisarão ser publicadas.','El proceso anticipa un debate regulatorio relevante para costos y usuarios. La propuesta técnica y la decisión tarifaria aún deberán publicarse.','Fonte institucional'),
 c('CHI-01','Chile','op','Ministério dos Transportes e Telecomunicações (MTT)','2026-11-04','https://mtt.gob.cl/plan-piloto-agentes-antievasion-logra-positivos-resultados-pago-del-pasaje-aumento-254/','Operação / evasão tarifária','Operación / evasión tarifaria','Piloto de agentes antievasão eleva em 25,4% as validações no serviço 107 da Red Movilidad','Piloto de agentes contra la evasión eleva un 25,4% las validaciones en el servicio 107 de Red Movilidad','O MTT informa 78.473 validações adicionais e aumento de 25,4% no serviço 107, com 89 agentes em 936 viagens no primeiro mês do piloto. A autoridade declarou intenção de replicar progressivamente a medida.','El MTT informa 78.473 validaciones adicionales y un aumento del 25,4% en el servicio 107, con 89 agentes en 936 viajes durante el primer mes del piloto. La autoridad declaró su intención de replicar gradualmente la medida.','É resultado de um piloto em um serviço, não redução comprovada da evasão em toda a rede. Replicação, custo e persistência do efeito merecem acompanhamento.','Es el resultado de un piloto en un servicio, no una reducción comprobada de la evasión en toda la red. La replicación, el costo y la persistencia del efecto requieren seguimiento.','Fonte institucional'),
 c('CHI-02','Chile','op','SoyChile','2026-11-07','https://www.soychile.cl/temuco/sociedad/2026/11/07/971880/gore-inversion-transporte-publico-araucania.html','Renovação de frota / eletrificação','Renovación de flota / electrificación','Araucanía apresenta renovação de frota, eletrificação e infraestrutura de transporte público','Araucanía presenta renovación de flota, electrificación e infraestructura de transporte público','O Governo Regional informou investimento de CLP 10.242 milhões em 2026, com renovação de 263 veículos em 22 comunas, recursos para ônibus padrão RED, táxis coletivos e dez projetos de infraestrutura. Entre os táxis coletivos apresentados há 26 elétricos.','El Gobierno Regional informó una inversión de CLP 10.242 millones en 2026, con renovación de 263 vehículos en 22 comunas, recursos para buses estándar RED, taxis colectivos y diez proyectos de infraestructura. Entre los taxis colectivos presentados hay 26 eléctricos.','O pacote combina renovação, acessibilidade e infraestrutura regional. Os 26 elétricos não devem ser estendidos a todos os 263 veículos apresentados.','El paquete combina renovación, accesibilidad e infraestructura regional. Los 26 eléctricos no deben extrapolarse a los 263 vehículos presentados.','Imprensa jornalística'),
 c('COL-01','Colombia','op','Portal Bogotá / Empresa Metro de Bogotá','2026-11-08','https://bogota.gov.co/mi-ciudad/movilidad/2026-11/metro-de-bogota-completa-puente-ferroviario-en-la-nqs','Infraestrutura metroferroviária / obras','Infraestructura metroferroviaria / obras','Linha 1 do Metro de Bogotá completa continuidade estrutural de ponte ferroviária na NQS','Línea 1 del Metro de Bogotá completa la continuidad estructural de un puente ferroviario en la NQS','A concretagem da última aduela completou a continuidade da estrutura de 159 metros na NQS com Calle 8 Sur. O Portal Bogotá situa o avanço global da Linha 1 em 84,68%.','El vaciado de la última dovela completó la continuidad de la estructura de 159 metros en la NQS con Calle 8 Sur. Portal Bogotá sitúa el avance global de la Línea 1 en el 84,68%.','O marco físico reduz incertezas de execução em um ponto crítico da obra. O percentual é o informado pelo poder público e não equivale à entrada em operação.','El hito físico reduce incertidumbres de ejecución en un punto crítico de la obra. El porcentaje es el informado por el poder público y no equivale a la entrada en operación.','Fonte institucional'),
 c('COL-02','Colombia','op','Portal Bogotá / Empresa Metro de Bogotá','2026-11-08','https://bogota.gov.co/mi-ciudad/movilidad/2026-11/linea-1-metro-bogota-11-parques-renovados-en-las-areas-de-influencia','Integração urbana / segurança viária','Integración urbana / seguridad vial','Linha 1 do Metro de Bogotá prevê renovar 11 parques no entorno do corredor','Línea 1 del Metro de Bogotá prevé renovar 11 parques en el entorno del corredor','A fonte informa intervenções de pavimentação, mobiliário urbano, interseções e conexões de pedestres em 11 parques da área de influência, como parte das melhorias de espaço público da Linha 1.','La fuente informa intervenciones de pavimentación, mobiliario urbano, intersecciones y conexiones peatonales en 11 parques del área de influencia, como parte de las mejoras de espacio público de la Línea 1.','A frente conecta a obra principal à acessibilidade e à segurança dos acessos. É uma intervenção planejada no corredor, não uma entrega já concluída dos parques.','El frente conecta la obra principal con la accesibilidad y la seguridad de los accesos. Es una intervención planificada en el corredor, no una entrega ya concluida de los parques.','Fonte institucional'),
 c('MEX-01','Mexico','watch','Chilango','2026-11-04','https://www.chilango.com/noticias/transporte/linea-3-del-metro-tendra-intervencion-profunda-de-indios-verdes-a-la-raza-cierres-nocturnos-y-en-fin-de-semana/','Infraestrutura metroferroviária / modernização','Infraestructura metroferroviaria / modernización','CDMX detalha intervenção profunda na Linha 3 do Metro entre Indios Verdes e La Raza','CDMX detalla una intervención profunda en la Línea 3 del Metro entre Indios Verdes y La Raza','O secretário de Mobilidade descreveu intervenção no trecho afetado por falha geológica, com modernização integral, orçamento superior a MXN 40 bilhões e programação de fechamentos noturnos e de fins de semana. A fonte situa 2027 como período mais intenso.','El secretario de Movilidad describió una intervención en el tramo afectado por una falla geológica, con modernización integral, presupuesto superior a MXN 40 mil millones y programación de cierres nocturnos y de fines de semana. La fuente sitúa 2027 como el período más intenso.','O anúncio torna visível o desafio de resiliência de um trecho crítico da rede. Não se trata de obra já iniciada, orçamento integralmente executado ou calendário definitivo de interrupções.','El anuncio visibiliza el desafío de resiliencia de un tramo crítico de la red. No se trata de una obra ya iniciada, presupuesto plenamente ejecutado ni calendario definitivo de interrupciones.','Imprensa jornalística'),
 c('URU-01','Uruguay','watch','El País Uruguay','2026-11-09','https://www.elpais.com.uy/informacion/servicios/cuando-se-podra-abonar-el-boleto-con-tarjeta-de-credito-y-debito-en-los-omnibus-de-montevideo','Bilhetagem / pagamentos interoperáveis','Recaudo / pagos interoperables','Montevidéu prevê pagamentos a bordo por cartões e e-wallets a partir de junho de 2027','Montevideo prevé pagos a bordo con tarjetas y e-wallets desde junio de 2027','Reportagem atribuída à Intendência de Montevidéu informa cronograma a partir de junho de 2027 para pagamento a bordo com cartões nacionais e internacionais de débito, crédito, pré-pagos e e-wallets. A nota também registra teste da nova versão de Cómo Ir.','Una nota atribuida a la Intendencia de Montevideo informa un cronograma desde junio de 2027 para pagos a bordo con tarjetas nacionales e internacionales de débito, crédito, prepagas y e-wallets. También registra pruebas de una nueva versión de Cómo Ir.','O cronograma aponta uma agenda de interoperabilidade de pagamentos e informação ao usuário. A aceitação não está disponível hoje e a conclusão dependerá da implantação anunciada.','El cronograma apunta a una agenda de interoperabilidad de pagos e información al usuario. La aceptación no está disponible hoy y la conclusión dependerá de la implantación anunciada.','Imprensa jornalística')]

# Members are read from the controlled master, then only evidence-backed citations are green/card-linked.
def norm(x): return ''.join(z for z in unicodedata.normalize('NFKD',x.lower()) if not unicodedata.combining(z))
with open('/opt/data/panorama_knowledge_base/uitp_associados_fontes_redes_master.csv',newline='',encoding='utf-8-sig') as f:
    members=[{'country':r['pais'],'name':r['nome_curto_alias_validado'] or r['associado_uitp_nome_base'],'tipo_fonte':r['tipo_fonte']} for r in csv.DictReader(f) if r['tipo_fonte']=='associado_uitp']
CITED={'metro de bogota':'COL-01','metro cdmx':'MEX-01','intendencia de montevideo':'URU-01'}

selection={'date':DATE,'cards':CARDS,'members':members,'coverage_gaps':['Argentina','Bolivia','Costa Rica','Equador','El Salvador','Guatemala','Panama','Paraguay','Peru','Venezuela'],'intake_records':['2026-11-10-0830-fontes-proprias.md','2026-11-10-0930-imprensa-instituicoes.md','2026-11-10-1015-google-news-lacunas.md']}
(E/f'selected-{DATE}.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n')
counts=collections.Counter(x['country'] for x in CARDS); sigcounts=collections.Counter(x['signal'] for x in CARDS)
escape=lambda x: html.escape(str(x),quote=True)

def member_row(country,lang):
    chips=[]; seen=set()
    country_norm={'paraguai':'paraguay','uruguai':'uruguay','ecuador':'equador'}.get(norm(country),norm(country))
    for m in members:
        mcountry={'paraguai':'paraguay','uruguai':'uruguay','ecuador':'equador'}.get(norm(m['country']),norm(m['country']))
        if mcountry!=country_norm: continue
        key=norm(m['name'])
        if not key or key in seen: continue
        seen.add(key)
        target=CITED.get(key)
        if target: chips.append(f'<a class="member-chip active" href="#card-{target}">{escape(m["name"])}</a>')
        else: chips.append(f'<span class="member-chip">{escape(m["name"])}</span>')
    label='Associados UITP:' if lang=='pt' else 'Asociados UITP:'
    return f'<div class="member-buttons"><span class="member-buttons-label">{label}</span>'+''.join(chips)+'</div>'

def render_card(x,lang,label):
    source_lang='PT' if x['country']=='Brasil' else 'ES'
    fields=('Resumo','Por que importa') if lang=='pt' else ('Resumen','Por qué importa')
    source_class=x['source_class'] if lang=='pt' else {'Fonte institucional':'Fuente institucional','Imprensa setorial':'Prensa sectorial','Imprensa jornalística':'Prensa periodística'}[x['source_class']]
    date='/'.join(reversed(x['source_publication_date'].split('-')))
    return f'''<article class="card" id="card-{x['id']}"><div><span class="badge {x['signal']}">{SIG[lang][x['signal']]}</span></div><div class="meta">{label} · {source_lang} · {source_class} · {escape(x['theme_'+lang])} · {date}</div><h3>{escape(x['title_'+lang])}</h3><div class="field"><strong>{fields[0]}:</strong> {escape(x['summary_'+lang])}</div><div class="field"><strong>{fields[1]}:</strong> {escape(x['impact_'+lang])}</div><div class="meta source">{escape(x['source'])}</div><a class="btn" href="{escape(x['source_url'])}" target="_blank" rel="noopener">{'Saiba mais' if lang=='pt' else 'Leer más'}</a></article>'''

def summary(lang):
    dist=', '.join(f'{pt if lang=="pt" else es} ({counts[c]})' for c,slug,flag,pt,es in COUNTRIES if counts[c])
    gaps=', '.join(pt if lang=='pt' else es for c,slug,flag,pt,es in COUNTRIES if not counts[c])
    if lang=='pt':
        return f'<section class="box"><h2>Resumo executivo</h2><p>Esta edição reúne <strong>10 notícias estratégicas em 5 países</strong>: {dist}. <strong>Sinaleiros: {sigcounts["op"]} oportunidades/avanços e {sigcounts["watch"]} acompanhamentos.</strong> O recorte combina marcos físicos e urbanos do Metro de Bogotá, renovação de frota e controle de evasão no Chile, processos de planejamento e regulação no Brasil, modernização metroferroviária na Cidade do México e interoperabilidade de pagamentos em Montevidéu. <strong>Sem notícia estratégica qualificada nesta rodada:</strong> {gaps}.</p></section>'
    return f'<section class="box"><h2>Resumen ejecutivo</h2><p>Esta edición reúne <strong>10 noticias estratégicas en 5 países</strong>: {dist}. <strong>Señales: {sigcounts["op"]} oportunidades/avances y {sigcounts["watch"]} seguimientos.</strong> El recorte combina hitos físicos y urbanos del Metro de Bogotá, renovación de flota y control de evasión en Chile, procesos de planificación y regulación en Brasil, modernización metroferroviaria en Ciudad de México e interoperabilidad de pagos en Montevideo. <strong>Sin noticia estratégica calificada en esta ronda:</strong> {gaps}.</p></section>'

def edition(lang):
    template=(E/f'approved-template-{lang}.html').read_text()
    if lang=='pt':
        template=template.replace('09/11/2026','10/11/2026').replace('9 de novembro de 2026','10 de novembro de 2026').replace('/edicoes/2026-11-08/','/edicoes/2026-11-09/')
    else:
        template=template.replace('09/11/2026','10/11/2026').replace('9 de noviembre de 2026','10 de noviembre de 2026').replace('/edicoes/2026-11-08/es/','/edicoes/2026-11-09/es/')
    jumps=[]; sections=[]
    for country,slug,flag,pt,es in COUNTRIES:
        label=pt if lang=='pt' else es; items=[x for x in CARDS if x['country']==country]; n=len(items)
        jumps.append(f'<a class="{"empty-jump" if not n else ""}" href="#{slug}">{flag} {label}</a>')
        empty='Sem notícia estratégica qualificada nesta rodada.' if lang=='pt' else 'Sin noticia estratégica calificada en esta ronda.'
        if n: count=f'{n} '+(('notícia estratégica validada nesta edição.' if n==1 else 'notícias estratégicas validadas nesta edição.') if lang=='pt' else ('noticia estratégica validada en esta edición.' if n==1 else 'noticias estratégicas validadas en esta edición.'))
        else: count=empty
        sections.append(f'<section class="country" id="{slug}"><h2>{flag} {label}</h2><p class="count">{count}</p>{member_row(country,lang)}'+''.join(render_card(x,lang,label) for x in items)+'</section>')
    jump=f'<section class="box"><h2>{"Ir direto para um país" if lang=="pt" else "Ir directo a un país"}</h2><div class="jump">'+''.join(jumps)+'</div></section>'
    out=template.replace('{{SUMMARY}}',summary(lang)).replace('{{JUMP}}',jump).replace('{{COUNTRIES}}',''.join(sections))
    assert out.count('<article class="card"')==10
    assert out.count('class="member-buttons"')==15
    assert 'news.google.' not in out and 'google.com/url' not in out
    ids=set(re.findall(r'\bid="([^"]+)"',out))
    for anchor in re.findall(r'href="#([^"]+)"',out): assert anchor in ids,anchor
    for x in CARDS: assert x['source_url'] in out
    return out

pt,es=edition('pt'),edition('es')
for rel,content in [('edicoes/2026-11-10/index.html',pt),('edicoes/2026-11-10/es/index.html',es),('hoje/index.html',pt),('hoje/es/index.html',es)]:
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(content)

# Current landing and archive: targeted content updates only.
landing=ROOT/'index.html'; t=landing.read_text()
t=re.sub(r'A edição de 9 de novembro de 2026 reúne 34 notícias estratégicas em 13 países, com fontes originais e leitura em português e espanhol\.', 'A edição de 10 de novembro de 2026 reúne 10 notícias estratégicas em 5 países, com fontes originais e leitura em português e espanhol.',t)
t=t.replace('Disponível:</strong> 9 de novembro de 2026.','Disponível:</strong> 10 de novembro de 2026.').replace('edicoes/2026-11-09/','edicoes/2026-11-10/').replace('edicoes/2026-11-09/es/','edicoes/2026-11-10/es/')
landing.write_text(t)
archive=ROOT/'arquivos/clippings/index.html'; t=archive.read_text()
t=t.replace('Total arquivado: 98 edições · Atualizado em 9 de novembro de 2026.','Total arquivado: 99 edições · Atualizado em 10 de novembro de 2026.')
entry='<article class="card"><h2>2026-11-10</h2><p>PANORAMA Mobilidade LATAM — 10 notícias estratégicas em 5 países.</p><div class="links"><a href="/edicoes/2026-11-10/">HTML PT</a><a href="/edicoes/2026-11-10/es/">HTML ES</a></div></article>'
t=t.replace('<article class="card"><h2>2026-11-09</h2>',entry+'<article class="card"><h2>2026-11-09</h2>',1)
archive.write_text(t)

# Structured archive indexes.
jp=ROOT/'arquivos/clippings_index.json'; rows=json.loads(jp.read_text())
rows=[x for x in rows if x['date']!=DATE]
rows.insert(0,{'date':DATE,'pt_html_path':'edicoes/2026-11-10/index.html','es_html_path':'edicoes/2026-11-10/es/index.html','pt_pdf_path':None,'es_pdf_path':None,'pt_html_url':'https://panoramamobilidade.github.io/edicoes/2026-11-10/','es_html_url':'https://panoramamobilidade.github.io/edicoes/2026-11-10/es/','pt_pdf_url':None,'es_pdf_url':None,'cards':10,'countries':5,'country_counts':dict(counts),'signal_counts':dict(sigcounts)})
jp.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
cp=ROOT/'arquivos/clippings_index.csv'
with cp.open(newline='',encoding='utf-8') as f: reader=csv.DictReader(f); headers=reader.fieldnames; old=[r for r in reader if r['date']!=DATE]
assert headers is not None
new={h:'' for h in headers}; new.update({'date':DATE,'pt_html':'https://panoramamobilidade.github.io/edicoes/2026-11-10/','es_html':'https://panoramamobilidade.github.io/edicoes/2026-11-10/es/','cards':'10','countries':'5','op':str(sigcounts['op']),'watch':str(sigcounts['watch']),'risk':'0','monitor':'0'})
with cp.open('w',newline='',encoding='utf-8') as f: w=csv.DictWriter(f,fieldnames=headers,lineterminator='\n'); w.writeheader(); w.writerow(new); w.writerows(old)
qa={'date':DATE,'cards':10,'countries':5,'country_counts':dict(counts),'signal_counts':dict(sigcounts),'coverage_gaps':selection['coverage_gaps'],'google_news_final_urls':0,'local_qa':'passed','pdf':'not generated'}
(E/f'qa-{DATE}.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(qa,ensure_ascii=False))
