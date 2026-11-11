#!/usr/bin/env python3
"""Publish the PANORAMA daily edition for 11 November 2026 from reviewed internal intake."""
from pathlib import Path
import csv, json, html, re, collections, unicodedata

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / 'editorial'
DATE = '2026-11-11'
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

def c(id, country, signal, source, date, url, theme_pt, theme_es, title_pt, title_es, summary_pt, summary_es, impact_pt, impact_es, source_class):
    return dict(id=id,country=country,signal=signal,source=source,source_publication_date=date,source_url=url,theme_pt=theme_pt,theme_es=theme_es,title_pt=title_pt,title_es=title_es,summary_pt=summary_pt,summary_es=summary_es,impact_pt=impact_pt,impact_es=impact_es,source_class=source_class)

CARDS = [
 c('BRA-01','Brasil','watch','Via Trolebus','2026-11-11','https://viatrolebus.com.br/2026/11/cptm-escolhe-consorcio-para-via-da-linha-10/','Licitação / manutenção metroferroviária','Licitación / mantenimiento metroferroviario','CPTM declara vencedor para manutenção da via da Linha 10–Turquesa','CPTM declara ganador para el mantenimiento de la vía de la Línea 10–Turquesa','A CPTM declarou habilitado e vencedor o Consórcio Manutenção Turquesa na licitação para serviços de engenharia de manutenção preventiva e corretiva da via permanente da Linha 10–Turquesa. Valor, prazo e assinatura ainda não foram divulgados.','CPTM declaró habilitado y ganador al Consorcio Manutenção Turquesa en la licitación de servicios de ingeniería para el mantenimiento preventivo y correctivo de la vía permanente de la Línea 10–Turquesa. Aún no se divulgaron valor, plazo ni firma.','O resultado avança a contratação de manutenção de ativo ferroviário, mas não equivale a contrato assinado ou início dos serviços. Os próximos marcos são a formalização e o cronograma de execução.','El resultado avanza la contratación del mantenimiento de un activo ferroviario, pero no equivale a un contrato firmado ni al inicio de los servicios. Los próximos hitos son la formalización y el cronograma de ejecución.','Imprensa setorial'),
 c('BRA-02','Brasil','op','Technibus','2026-11-10','https://technibus.com.br/2026/11/10/onibus-eletricos-de-sao-jose-sao-apresentados-na-cop31','Eletrificação / modelo contratual','Electrificación / modelo contractual','São José dos Campos atualiza implantação de ônibus elétricos e modelo de operação','São José dos Campos actualiza la implantación de buses eléctricos y su modelo operativo','A reportagem registra 20 dos 400 ônibus previstos em contrato já em circulação e informa a previsão de mais 24 articulados até o fim de novembro e 65 veículos adicionais até o fim de dezembro. O modelo separa frota, operação, recarga e bilhetagem.','La nota registra que 20 de los 400 buses previstos en el contrato ya circulan e informa la previsión de 24 articulados más hasta fines de noviembre y 65 vehículos adicionales hasta fines de diciembre. El modelo separa flota, operación, recarga y recaudo.','A atualização permite acompanhar uma implantação escalonada e a divisão de responsabilidades do contrato. As quantidades previstas não devem ser tratadas como entregas já realizadas.','La actualización permite seguir una implantación escalonada y la división de responsabilidades del contrato. Las cantidades previstas no deben tratarse como entregas ya realizadas.','Imprensa setorial'),
 c('BRA-03','Brasil','watch','Via Trolebus','2026-11-07','https://viatrolebus.com.br/2026/11/metro-testa-cbtc-na-linha-3-contratado-em-2008/','Sinalização / comissionamento CBTC','Señalización / puesta en servicio CBTC','Metrô de São Paulo programa nova etapa de testes do CBTC na Linha 3–Vermelha','Metro de São Paulo programa una nueva etapa de pruebas del CBTC en la Línea 3–Roja','A próxima etapa de marcha branca testa comunicação trem-via, localização, intervalos, aceleração, frenagem e paradas. A expectativa reportada é concluir essa fase no início de 2027, após validações de segurança, desempenho e confiabilidade.','La próxima etapa de marcha blanca prueba comunicación tren-vía, localización, intervalos, aceleración, frenado y paradas. La expectativa reportada es concluir esta fase a inicios de 2027, tras validaciones de seguridad, desempeño y confiabilidad.','É um marco de comissionamento tecnológico, não operação comercial do CBTC nem redução imediata de intervalos. A validação operacional seguirá sendo o ponto decisivo.','Es un hito de puesta en servicio tecnológica, no operación comercial del CBTC ni reducción inmediata de intervalos. La validación operacional seguirá siendo el punto decisivo.','Imprensa setorial'),
 c('CHI-01','Chile','op','Ministério dos Transportes e Telecomunicações (MTT)','2026-11-10','https://mtt.gob.cl/presidente-kast-participa-en-marcha-blanca-del-teleferico-bicentenario-que-conectara-huechuraba-con-el-sector-oriente-de-santiago/','Infraestrutura concedida / comissionamento','Infraestructura concesionada / puesta en servicio','Teleférico Bicentenario inicia marcha branca em Santiago','Teleférico Bicentenario inicia marcha blanca en Santiago','Começou a fase de testes do sistema entre Providencia e Huechuraba, pelo Parque Metropolitano. O MTT informa 3,4 km, três estações, 121 cabines, capacidade de até 3 mil pessoas por hora e por sentido e previsão de operação provisória no primeiro trimestre de 2027, após testes e autorizações.','Comenzó la fase de pruebas del sistema entre Providencia y Huechuraba, por el Parque Metropolitano. El MTT informa 3,4 km, tres estaciones, 121 cabinas, capacidad de hasta 3 mil personas por hora y sentido y previsión de operación provisoria en el primer trimestre de 2027, tras pruebas y autorizaciones.','A marcha branca reduz incerteza sobre a entrega de uma infraestrutura elétrica concedida. Não é abertura ao público nem operação comercial definitiva.','La marcha blanca reduce la incertidumbre sobre la entrega de una infraestructura eléctrica concesionada. No es apertura al público ni operación comercial definitiva.','Fonte institucional'),
 c('COL-01','Colombia','watch','Portal Bogotá / Empresa Metro de Bogotá','2026-11-06','https://bogota.gov.co/mi-ciudad/movilidad/2026-11/tres-grupos-participaran-en-licitacion-de-linea-2-del-metro-de-bogota','Concessão / infraestrutura metroferroviária','Concesión / infraestructura metroferroviaria','Três grupos são pré-qualificados para a concessão da Linha 2 do Metro de Bogotá','Tres grupos son precalificados para la concesión de la Línea 2 del Metro de Bogotá','A Empresa Metro de Bogotá concluiu a avaliação de pré-qualificação: três agrupamentos seguirão para a solicitação de ofertas, sujeita à não objeção da banca multilateral. A licitação é prevista para o primeiro semestre de 2027.','La Empresa Metro de Bogotá concluyó la evaluación de precalificación: tres agrupaciones seguirán a la solicitud de ofertas, sujeta a la no objeción de la banca multilateral. La licitación está prevista para el primer semestre de 2027.','O passo sustenta a estrutura concorrencial e financeira do projeto. Não representa proposta recebida, adjudicação ou início de obras.','El paso sostiene la estructura competitiva y financiera del proyecto. No representa oferta recibida, adjudicación ni inicio de obras.','Fonte institucional'),
 c('COS-01','Costa Rica','watch','ARESEP','2026-11-10','https://aresep.go.cr/noticias/aresep-reafirma-la-legalidad-del-canon-para-los-servicios-especiales-de-transporte-y-mantiene-espacios-de-dialogo-con-el-sector/','Regulação / transporte especial','Regulación / transporte especial','ARESEP prevê iniciar em 2027 a regulação do transporte especial de trabalhadores','ARESEP prevé iniciar en 2027 la regulación del transporte especial de trabajadores','A autoridade reguladora informou que iniciará em 2027 a regulação da modalidade especial de transporte de trabalhadores e, em seguida, das modalidades de estudantes e turismo. A nota registra diálogo com o setor e nova mesa técnica sobre cálculo e implantação.','La autoridad reguladora informó que iniciará en 2027 la regulación de la modalidad especial de transporte de trabajadores y, luego, de estudiantes y turismo. La nota registra diálogo con el sector y una nueva mesa técnica sobre cálculo e implantación.','É um marco regulatório para uma modalidade específica; não é nova tarifa do transporte regular nem regra já vigente para todos os operadores.','Es un hito regulatorio para una modalidad específica; no es una nueva tarifa del transporte regular ni una regla ya vigente para todos los operadores.','Fonte institucional'),
 c('MEX-01','Mexico','watch','Chilango','2026-11-04','https://www.chilango.com/noticias/transporte/semaforos-inteligentes-de-cdmx-asi-funcionaran-flujo-vehicilar-tiempo-de-viaje/','ITS / prioridade ao transporte coletivo','ITS / prioridad al transporte colectivo','CDMX planeja semáforos adaptativos com prioridade ao transporte coletivo','CDMX planea semáforos adaptativos con prioridad al transporte colectivo','O secretário de Mobilidade apresentou projeto de modernização em três fases, previsto para começar em 2027, com semáforos capazes de adaptar ciclos ao fluxo e prever prioridade ao transporte coletivo. A expectativa mencionada é reduzir tempos de viagem entre 10% e 20%.','El secretario de Movilidad presentó un proyecto de modernización en tres fases, previsto para comenzar en 2027, con semáforos capaces de adaptar ciclos al flujo y prever prioridad al transporte colectivo. La expectativa mencionada es reducir los tiempos de viaje entre 10% y 20%.','É planejamento de ITS e prioridade semafórica. A redução de tempo é expectativa, não resultado medido, e não há confirmação de contratação ou implantação concluída.','Es planificación de ITS y prioridad semafórica. La reducción de tiempo es una expectativa, no un resultado medido, y no hay confirmación de contratación ni implantación concluida.','Imprensa jornalística'),
 c('PAN-01','Panama','op','Telemetro','2026-11-09','https://www.telemetro.com/nacionales/mibus-anuncia-nuevas-formas-pago-pasajeros-utilizaran-tarjetas-visa-mastercard-apple-pay-y-google-pay-n6097968/amp','Bilhetagem / pagamentos sem contato','Recaudo / pagos sin contacto','MiBus incorpora cartões bancários e carteiras digitais aos validadores do Metro Bus','MiBus incorpora tarjetas bancarias y billeteras digitales a los validadores del Metro Bus','Os novos validadores passam a aceitar Visa, Mastercard, Apple Pay e Google Pay, além do cartão tradicional. A atualização mantém a exigência de uso do mesmo meio de pagamento em toda a transferência e prevê restrição de novos usos quando houver pagamento pendente.','Los nuevos validadores pasan a aceptar Visa, Mastercard, Apple Pay y Google Pay, además de la tarjeta tradicional. La actualización mantiene la exigencia de usar el mismo medio de pago en toda la transferencia y prevé restricción de nuevos usos cuando haya un pago pendiente.','A medida amplia os meios de pagamento e atualiza a experiência do usuário. Não comprova interoperabilidade tarifária integral com o Metro de Panamá ou outros sistemas.','La medida amplía los medios de pago y actualiza la experiencia del usuario. No demuestra interoperabilidad tarifaria integral con Metro de Panamá u otros sistemas.','Imprensa jornalística')]

def norm(x): return ''.join(z for z in unicodedata.normalize('NFKD',x.lower()) if not unicodedata.combining(z))
with open('/opt/data/panorama_knowledge_base/uitp_associados_fontes_redes_master.csv',newline='',encoding='utf-8-sig') as f:
    members=[{'country':r['pais'],'name':r['nome_curto_alias_validado'] or r['associado_uitp_nome_base'],'tipo_fonte':r['tipo_fonte']} for r in csv.DictReader(f) if r['tipo_fonte']=='associado_uitp']
CITED={'metro de sao paulo':'BRA-03','metro de bogota':'COL-01','aresep':'COS-01','mibus panama':'PAN-01'}
GAPS=['Argentina','Bolivia','Equador','El Salvador','Guatemala','Paraguay','Peru','Uruguay','Venezuela']
selection={'date':DATE,'cards':CARDS,'members':members,'coverage_gaps':GAPS,'intake_records':['2026-11-11-0830-fontes-proprias.md','2026-11-11-0930-imprensa-instituicoes.md','2026-11-11-1015-google-news-lacunas.md']}
(E/f'selected-{DATE}.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n')
counts=collections.Counter(x['country'] for x in CARDS); sigcounts=collections.Counter(x['signal'] for x in CARDS)
escape=lambda x: html.escape(str(x),quote=True)

def member_row(country,lang):
    chips=[]; seen=set(); country_norm={'paraguai':'paraguay','uruguai':'uruguay','ecuador':'equador'}.get(norm(country),norm(country))
    for m in members:
        mcountry={'paraguai':'paraguay','uruguai':'uruguay','ecuador':'equador'}.get(norm(m['country']),norm(m['country']))
        if mcountry!=country_norm: continue
        key=norm(m['name'])
        if not key or key in seen: continue
        seen.add(key); target=CITED.get(key)
        chips.append(f'<a class="member-chip active" href="#card-{target}">{escape(m["name"])}</a>' if target else f'<span class="member-chip">{escape(m["name"])}</span>')
    return f'<div class="member-buttons"><span class="member-buttons-label">{"Associados UITP:" if lang=="pt" else "Asociados UITP:"}</span>'+''.join(chips)+'</div>'

def render_card(x,lang,label):
    source_lang='PT' if x['country']=='Brasil' else 'ES'
    fields=('Resumo','Por que importa') if lang=='pt' else ('Resumen','Por qué importa')
    sc=x['source_class'] if lang=='pt' else {'Fonte institucional':'Fuente institucional','Imprensa setorial':'Prensa sectorial','Imprensa jornalística':'Prensa periodística'}[x['source_class']]
    date='/'.join(reversed(x['source_publication_date'].split('-')))
    return f'''<article class="card" id="card-{x['id']}"><div><span class="badge {x['signal']}">{SIG[lang][x['signal']]}</span></div><div class="meta">{label} · {source_lang} · {sc} · {escape(x['theme_'+lang])} · {date}</div><h3>{escape(x['title_'+lang])}</h3><div class="field"><strong>{fields[0]}:</strong> {escape(x['summary_'+lang])}</div><div class="field"><strong>{fields[1]}:</strong> {escape(x['impact_'+lang])}</div><div class="meta source">{escape(x['source'])}</div><a class="btn" href="{escape(x['source_url'])}" target="_blank" rel="noopener">{'Saiba mais' if lang=='pt' else 'Leer más'}</a></article>'''

def summary(lang):
    dist=', '.join(f'{pt if lang=="pt" else es} ({counts[c]})' for c,slug,flag,pt,es in COUNTRIES if counts[c])
    gaps=', '.join(pt if lang=='pt' else es for c,slug,flag,pt,es in COUNTRIES if not counts[c])
    if lang=='pt':
        p=f'Esta edição reúne <strong>{len(CARDS)} notícias estratégicas em {len(counts)} países</strong>: {dist}. <strong>Sinaleiros: {sigcounts["op"]} oportunidades/avanços e {sigcounts["watch"]} acompanhamentos.</strong> O Brasil concentra três marcos de manutenção, eletrificação e sinalização; a agenda regional combina comissionamento de infraestrutura no Chile, concessão metroferroviária na Colômbia, regulação na Costa Rica, ITS na Cidade do México e pagamentos sem contato no Panamá. <strong>Sem notícia estratégica qualificada nesta rodada:</strong> {gaps}.'
        return f'<section class="box"><h2>Resumo executivo</h2><p>{p}</p></section>'
    p=f'Esta edición reúne <strong>{len(CARDS)} noticias estratégicas en {len(counts)} países</strong>: {dist}. <strong>Señales: {sigcounts["op"]} oportunidades/avances y {sigcounts["watch"]} seguimientos.</strong> Brasil concentra tres hitos de mantenimiento, electrificación y señalización; la agenda regional combina puesta en servicio de infraestructura en Chile, concesión metroferroviaria en Colombia, regulación en Costa Rica, ITS en Ciudad de México y pagos sin contacto en Panamá. <strong>Sin noticia estratégica calificada en esta ronda:</strong> {gaps}.'
    return f'<section class="box"><h2>Resumen ejecutivo</h2><p>{p}</p></section>'

def edition(lang):
    template=(E/f'approved-template-{lang}.html').read_text()
    if lang=='pt': template=template.replace('09/11/2026','11/11/2026').replace('9 de novembro de 2026','11 de novembro de 2026').replace('/edicoes/2026-11-08/','/edicoes/2026-11-10/')
    else: template=template.replace('09/11/2026','11/11/2026').replace('9 de noviembre de 2026','11 de noviembre de 2026').replace('/edicoes/2026-11-08/es/','/edicoes/2026-11-10/es/')
    jumps=[]; sections=[]
    for country,slug,flag,pt,es in COUNTRIES:
        label=pt if lang=='pt' else es; items=[x for x in CARDS if x['country']==country]; n=len(items)
        jumps.append(f'<a class="{"empty-jump" if not n else ""}" href="#{slug}">{flag} {label}</a>')
        empty='Sem notícia estratégica qualificada nesta rodada.' if lang=='pt' else 'Sin noticia estratégica calificada en esta ronda.'
        count=(f'{n} '+(('notícia estratégica validada nesta edição.' if n==1 else 'notícias estratégicas validadas nesta edição.') if lang=='pt' else ('noticia estratégica validada en esta edición.' if n==1 else 'noticias estratégicas validadas en esta edición.'))) if n else empty
        sections.append(f'<section class="country" id="{slug}"><h2>{flag} {label}</h2><p class="count">{count}</p>{member_row(country,lang)}'+''.join(render_card(x,lang,label) for x in items)+'</section>')
    jump=f'<section class="box"><h2>{"Ir direto para um país" if lang=="pt" else "Ir directo a un país"}</h2><div class="jump">'+''.join(jumps)+'</div></section>'
    out=template.replace('{{SUMMARY}}',summary(lang)).replace('{{JUMP}}',jump).replace('{{COUNTRIES}}',''.join(sections))
    assert out.count('<article class="card"')==len(CARDS)
    assert out.count('class="member-buttons"')==15
    assert 'news.google.' not in out and 'google.com/url' not in out
    ids=set(re.findall(r'\bid="([^"]+)"',out))
    for anchor in re.findall(r'href="#([^"]+)"',out): assert anchor in ids,anchor
    for x in CARDS: assert x['source_url'] in out
    return out

pt,es=edition('pt'),edition('es')
for rel,content in [(f'edicoes/{DATE}/index.html',pt),(f'edicoes/{DATE}/es/index.html',es),('hoje/index.html',pt),('hoje/es/index.html',es)]:
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(content)
landing=ROOT/'index.html'; t=landing.read_text()
t=re.sub(r'A edição de 10 de novembro de 2026 reúne 10 notícias estratégicas em 5 países, com fontes originais e leitura em português e espanhol\.', 'A edição de 11 de novembro de 2026 reúne 8 notícias estratégicas em 6 países, com fontes originais e leitura em português e espanhol.',t)
t=t.replace('Disponível:</strong> 10 de novembro de 2026.','Disponível:</strong> 11 de novembro de 2026.').replace('edicoes/2026-11-10/','edicoes/2026-11-11/').replace('edicoes/2026-11-10/es/','edicoes/2026-11-11/es/')
landing.write_text(t)
archive=ROOT/'arquivos/clippings/index.html'; t=archive.read_text()
t=t.replace('Total arquivado: 99 edições · Atualizado em 10 de novembro de 2026.','Total arquivado: 100 edições · Atualizado em 11 de novembro de 2026.')
entry='<article class="card"><h2>2026-11-11</h2><p>PANORAMA Mobilidade LATAM — 8 notícias estratégicas em 6 países.</p><div class="links"><a href="/edicoes/2026-11-11/">HTML PT</a><a href="/edicoes/2026-11-11/es/">HTML ES</a></div></article>'
t=t.replace('<article class="card"><h2>2026-11-10</h2>',entry+'<article class="card"><h2>2026-11-10</h2>',1)
archive.write_text(t)
jp=ROOT/'arquivos/clippings_index.json'; rows=json.loads(jp.read_text()); rows=[x for x in rows if x['date']!=DATE]
rows.insert(0,{'date':DATE,'pt_html_path':f'edicoes/{DATE}/index.html','es_html_path':f'edicoes/{DATE}/es/index.html','pt_pdf_path':None,'es_pdf_path':None,'pt_html_url':f'https://panoramamobilidade.github.io/edicoes/{DATE}/','es_html_url':f'https://panoramamobilidade.github.io/edicoes/{DATE}/es/','pt_pdf_url':None,'es_pdf_url':None,'cards':len(CARDS),'countries':len(counts),'country_counts':dict(counts),'signal_counts':dict(sigcounts)})
jp.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
cp=ROOT/'arquivos/clippings_index.csv'
with cp.open(newline='',encoding='utf-8') as f: reader=csv.DictReader(f); headers=reader.fieldnames; old=[r for r in reader if r['date']!=DATE]
assert headers is not None
new={h:'' for h in headers}; new.update({'date':DATE,'pt_html':f'https://panoramamobilidade.github.io/edicoes/{DATE}/','es_html':f'https://panoramamobilidade.github.io/edicoes/{DATE}/es/','cards':str(len(CARDS)),'countries':str(len(counts)),'op':str(sigcounts['op']),'watch':str(sigcounts['watch']),'risk':'0','monitor':'0'})
with cp.open('w',newline='',encoding='utf-8') as f: w=csv.DictWriter(f,fieldnames=headers,lineterminator='\n'); w.writeheader(); w.writerow(new); w.writerows(old)
qa={'date':DATE,'cards':len(CARDS),'countries':len(counts),'country_counts':dict(counts),'signal_counts':dict(sigcounts),'coverage_gaps':GAPS,'google_news_final_urls':0,'local_qa':'passed','pdf':'not generated'}
(E/f'qa-{DATE}.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(qa,ensure_ascii=False))
