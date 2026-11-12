#!/usr/bin/env python3
"""Generate the PANORAMA Mobilidade LATAM edition for 12 November 2026."""
from pathlib import Path
import csv, json, html, re, collections, unicodedata

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / 'editorial'
DATE = '2026-11-12'
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
SOURCE_CLASS_ES = {'Fonte institucional':'Fuente institucional','Imprensa setorial':'Prensa sectorial','Imprensa jornalística':'Prensa periodística'}

selection = json.loads((E / f'selected-{DATE}.json').read_text(encoding='utf-8'))
CARDS = selection['cards']
GAPS = selection['coverage_gaps']

def norm(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text.lower()) if not unicodedata.combining(c))

with open('/opt/data/panorama_knowledge_base/uitp_associados_fontes_redes_master.csv', newline='', encoding='utf-8-sig') as f:
    members = [
        {'country': r['pais'], 'name': r['nome_curto_alias_validado'] or r['associado_uitp_nome_base']}
        for r in csv.DictReader(f) if r['tipo_fonte'] == 'associado_uitp'
    ]
selection['members'] = [{**m, 'tipo_fonte': 'associado_uitp'} for m in members]
(E / f'selected-{DATE}.json').write_text(json.dumps(selection, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

COUNTRY_NORM = {'paraguai':'paraguay','uruguai':'uruguay','ecuador':'equador'}
CITED = {'metro de medellin':'COL-01'}
counts = collections.Counter(c['country'] for c in CARDS)
sigcounts = collections.Counter(c['signal'] for c in CARDS)
escape = lambda x: html.escape(str(x), quote=True)

def member_row(country, lang):
    country_key = COUNTRY_NORM.get(norm(country), norm(country))
    chips, seen = [], set()
    for member in members:
        if COUNTRY_NORM.get(norm(member['country']), norm(member['country'])) != country_key:
            continue
        key = norm(member['name'])
        if not key or key in seen:
            continue
        seen.add(key)
        target = CITED.get(key)
        if target:
            chips.append(f'<a class="member-chip active" href="#card-{target}">{escape(member["name"])}</a>')
        else:
            chips.append(f'<span class="member-chip">{escape(member["name"])}</span>')
    label = 'Associados UITP:' if lang == 'pt' else 'Asociados UITP:'
    return f'<div class="member-buttons"><span class="member-buttons-label">{label}</span>{"".join(chips)}</div>'

def render_card(card, lang, country_label):
    source_lang = 'PT' if card['country'] == 'Brasil' else 'ES'
    labels = ('Resumo', 'Por que importa') if lang == 'pt' else ('Resumen', 'Por qué importa')
    source_class = card['source_class'] if lang == 'pt' else SOURCE_CLASS_ES[card['source_class']]
    source_date = '/'.join(reversed(card['source_publication_date'].split('-')))
    return f'''<article class="card" id="card-{card['id']}">
<div><span class="badge {card['signal']}">{SIG[lang][card['signal']]}</span></div>
<div class="meta">{country_label} · {source_lang} · {source_class} · {escape(card['theme_'+lang])} · {source_date}</div>
<h3>{escape(card['title_'+lang])}</h3>
<div class="field"><strong>{labels[0]}:</strong> {escape(card['summary_'+lang])}</div>
<div class="field"><strong>{labels[1]}:</strong> {escape(card['impact_'+lang])}</div>
<div class="meta source">{escape(card['source'])}</div>
<a class="btn" href="{escape(card['source_url'])}" target="_blank" rel="noopener">{'Saiba mais' if lang == 'pt' else 'Leer más'}</a>
</article>'''

def executive_summary(lang):
    included = ', '.join(f'{pt if lang == "pt" else es} ({counts[c]})' for c,slug,flag,pt,es in COUNTRIES if counts[c])
    gaps = ', '.join(pt if lang == 'pt' else es for c,slug,flag,pt,es in COUNTRIES if not counts[c])
    if lang == 'pt':
        text = (f'Esta edição reúne <strong>{len(CARDS)} notícias estratégicas em {len(counts)} países</strong>: {included}. '
                f'<strong>Sinaleiros: {sigcounts["op"]} oportunidades/avanços, {sigcounts["watch"]} acompanhamentos, {sigcounts["risk"]} alertas/riscos e {sigcounts["monitor"]} monitoramento.</strong> '
                'A agenda concentra pagamentos abertos em Medellín, estruturação ferroviária na Costa Rica, novos marcos normativos na Guatemala e pressões de governança e segurança no Paraguai e no Peru. '
                f'<strong>Sem notícia estratégica qualificada nesta rodada:</strong> {gaps}.')
        return f'<section class="box"><h2>Resumo executivo</h2><p>{text}</p></section>'
    text = (f'Esta edición reúne <strong>{len(CARDS)} noticias estratégicas en {len(counts)} países</strong>: {included}. '
            f'<strong>Señales: {sigcounts["op"]} oportunidades/avances, {sigcounts["watch"]} seguimientos, {sigcounts["risk"]} alertas/riesgos y {sigcounts["monitor"]} monitoreo.</strong> '
            'La agenda concentra pagos abiertos en Medellín, estructuración ferroviaria en Costa Rica, nuevos hitos normativos en Guatemala y presiones de gobernanza y seguridad en Paraguay y Perú. '
            f'<strong>Sin noticia estratégica calificada en esta ronda:</strong> {gaps}.')
    return f'<section class="box"><h2>Resumen ejecutivo</h2><p>{text}</p></section>'

def build(lang):
    template = (E / f'approved-template-{lang}.html').read_text(encoding='utf-8')
    if lang == 'pt':
        template = template.replace('09/11/2026', '12/11/2026').replace('9 de novembro de 2026', '12 de novembro de 2026').replace('/edicoes/2026-11-08/', '/edicoes/2026-11-11/')
    else:
        template = template.replace('09/11/2026', '12/11/2026').replace('9 de noviembre de 2026', '12 de noviembre de 2026').replace('/edicoes/2026-11-08/es/', '/edicoes/2026-11-11/es/')
    jumps, sections = [], []
    for country, slug, flag, pt, es in COUNTRIES:
        label = pt if lang == 'pt' else es
        cards = [c for c in CARDS if c['country'] == country]
        n = len(cards)
        jumps.append(f'<a class="{"empty-jump" if not n else ""}" href="#{slug}">{flag} {label}</a>')
        if n:
            count_text = (f'{n} ' + (('notícia estratégica validada nesta edição.' if n == 1 else 'notícias estratégicas validadas nesta edição.') if lang == 'pt' else ('noticia estratégica validada en esta edición.' if n == 1 else 'noticias estratégicas validadas en esta edición.')))
        else:
            count_text = 'Sem notícia estratégica qualificada nesta rodada.' if lang == 'pt' else 'Sin noticia estratégica calificada en esta ronda.'
        sections.append(f'<section class="country" id="{slug}"><h2>{flag} {label}</h2><p class="count">{count_text}</p>{member_row(country, lang)}{"".join(render_card(c, lang, label) for c in cards)}</section>')
    jump_label = 'Ir direto para um país' if lang == 'pt' else 'Ir directo a un país'
    jump = f'<section class="box"><h2>{jump_label}</h2><div class="jump">{"".join(jumps)}</div></section>'
    output = template.replace('{{SUMMARY}}', executive_summary(lang)).replace('{{JUMP}}', jump).replace('{{COUNTRIES}}', ''.join(sections))
    assert output.count('<article class="card"') == len(CARDS)
    assert output.count('class="member-buttons"') == 15
    assert 'news.google.' not in output and 'google.com/url' not in output
    ids = set(re.findall(r'\bid="([^"]+)"', output))
    for anchor in re.findall(r'href="#([^"]+)"', output):
        assert anchor in ids, anchor
    for card in CARDS:
        assert card['source_url'] in output
    return output

pt, es = build('pt'), build('es')
for relative, content in [
    (f'edicoes/{DATE}/index.html', pt), (f'edicoes/{DATE}/es/index.html', es),
    ('hoje/index.html', pt), ('hoje/es/index.html', es)
]:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

landing = ROOT / 'index.html'
text = landing.read_text(encoding='utf-8')
text = re.sub(r'A edição de 11 de novembro de 2026 reúne 8 notícias estratégicas em 6 países, com fontes originais e leitura em português e espanhol\.', 'A edição de 12 de novembro de 2026 reúne 9 notícias estratégicas em 8 países, com fontes originais e leitura em português e espanhol.', text)
text = text.replace('Disponível:</strong> 11 de novembro de 2026.', 'Disponível:</strong> 12 de novembro de 2026.')
text = text.replace('edicoes/2026-11-11/', 'edicoes/2026-11-12/').replace('edicoes/2026-11-11/es/', 'edicoes/2026-11-12/es/')
landing.write_text(text, encoding='utf-8')

archive = ROOT / 'arquivos/clippings/index.html'
text = archive.read_text(encoding='utf-8')
text = text.replace('Total arquivado: 100 edições · Atualizado em 11 de novembro de 2026.', 'Total arquivado: 101 edições · Atualizado em 12 de novembro de 2026.')
entry = '<article class="card"><h2>2026-11-12</h2><p>PANORAMA Mobilidade LATAM — 9 notícias estratégicas em 8 países.</p><div class="links"><a href="/edicoes/2026-11-12/">HTML PT</a><a href="/edicoes/2026-11-12/es/">HTML ES</a></div></article>'
text = text.replace('<article class="card"><h2>2026-11-11</h2>', entry + '<article class="card"><h2>2026-11-11</h2>', 1)
archive.write_text(text, encoding='utf-8')

json_index = ROOT / 'arquivos/clippings_index.json'
rows = json.loads(json_index.read_text(encoding='utf-8'))
rows = [row for row in rows if row['date'] != DATE]
rows.insert(0, {'date': DATE, 'pt_html_path': f'edicoes/{DATE}/index.html', 'es_html_path': f'edicoes/{DATE}/es/index.html', 'pt_pdf_path': None, 'es_pdf_path': None, 'pt_html_url': f'https://panoramamobilidade.github.io/edicoes/{DATE}/', 'es_html_url': f'https://panoramamobilidade.github.io/edicoes/{DATE}/es/', 'pt_pdf_url': None, 'es_pdf_url': None, 'cards': len(CARDS), 'countries': len(counts), 'country_counts': dict(counts), 'signal_counts': dict(sigcounts)})
json_index.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

csv_index = ROOT / 'arquivos/clippings_index.csv'
with csv_index.open(newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames
    old_rows = [row for row in reader if row['date'] != DATE]
assert headers is not None
new_row = {key: '' for key in headers}
new_row.update({'date': DATE, 'pt_html': f'https://panoramamobilidade.github.io/edicoes/{DATE}/', 'es_html': f'https://panoramamobilidade.github.io/edicoes/{DATE}/es/', 'cards': str(len(CARDS)), 'countries': str(len(counts)), 'op': str(sigcounts['op']), 'watch': str(sigcounts['watch']), 'risk': str(sigcounts['risk']), 'monitor': str(sigcounts['monitor'])})
with csv_index.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers, lineterminator='\n')
    writer.writeheader(); writer.writerow(new_row); writer.writerows(old_rows)

qa = {'date': DATE, 'cards': len(CARDS), 'countries': len(counts), 'country_counts': dict(counts), 'signal_counts': dict(sigcounts), 'coverage_gaps': GAPS, 'google_news_final_urls': 0, 'local_qa': 'passed', 'pdf': 'not generated'}
(E / f'qa-{DATE}.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(qa, ensure_ascii=False))
