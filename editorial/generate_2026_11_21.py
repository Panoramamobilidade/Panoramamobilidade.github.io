#!/usr/bin/env python3
"""Generate the 21 Nov 2026 edition from durable, bilingual editorial data."""
from pathlib import Path
import csv, json, html, re, collections, unicodedata

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / 'editorial'
DATE = '2026-11-21'
BASE = 'https://panoramamobilidade.github.io'
COUNTRIES = [
    ('Argentina', 'argentina', '🇦🇷', 'Argentina', 'Argentina'),
    ('Bolivia', 'bolivia', '🇧🇴', 'Bolívia', 'Bolivia'),
    ('Brasil', 'brasil', '🇧🇷', 'Brasil', 'Brasil'),
    ('Chile', 'chile', '🇨🇱', 'Chile', 'Chile'),
    ('Colombia', 'colombia', '🇨🇴', 'Colômbia', 'Colombia'),
    ('Costa Rica', 'costa-rica', '🇨🇷', 'Costa Rica', 'Costa Rica'),
    ('Equador', 'equador', '🇪🇨', 'Equador', 'Ecuador'),
    ('Guatemala', 'guatemala', '🇬🇹', 'Guatemala', 'Guatemala'),
    ('Mexico', 'mexico', '🇲🇽', 'México', 'México'),
    ('Panama', 'panama', '🇵🇦', 'Panamá', 'Panamá'),
    ('Paraguay', 'paraguai', '🇵🇾', 'Paraguai', 'Paraguay'),
    ('Peru', 'peru', '🇵🇪', 'Peru', 'Perú'),
    ('Uruguay', 'uruguai', '🇺🇾', 'Uruguai', 'Uruguay'),
]
SIG = {
    'pt': {'op': '🟢 Oportunidade/avanço', 'watch': '🟡 Acompanhar', 'risk': '🔴 Alerta/risco', 'monitor': '🔵 Monitoramento'},
    'es': {'op': '🟢 Oportunidad/avance', 'watch': '🟡 Seguimiento', 'risk': '🔴 Alerta/riesgo', 'monitor': '🔵 Monitoreo'},
}
SOURCE_CLASS_ES = {'Fonte institucional': 'Fuente institucional', 'Imprensa setorial': 'Prensa sectorial', 'Imprensa jornalística': 'Prensa periodística'}

selection = json.loads((E / f'selected-{DATE}.json').read_text())
CARDS = selection['cards']
counts = collections.Counter(c['country'] for c in CARDS)
signals = collections.Counter(c['signal'] for c in CARDS)
assert set(counts) <= {c[0] for c in COUNTRIES}
assert len(CARDS) == len({c['id'] for c in CARDS}) == len({c['source_url'] for c in CARDS})
for c in CARDS:
    assert '2026-11-09' <= c['source_publication_date'] <= DATE
    assert c['source_url'].startswith('https://')

with open('/opt/data/panorama_knowledge_base/uitp_associados_fontes_redes_master.csv', encoding='utf-8-sig', newline='') as f:
    members = [
        {'country': r['pais'], 'name': r['nome_curto_alias_validado'] or r['associado_uitp_nome_base']}
        for r in csv.DictReader(f) if r['tipo_fonte'] == 'associado_uitp'
    ]
selection['members'] = members
(E / f'selected-{DATE}.json').write_text(json.dumps(selection, ensure_ascii=False, indent=2) + '\n')

CITED = {
    'transmilenio': 'COL-01',
    'aresep': 'CRI-01',
    'atu lima-callao': 'PER-01',
}
COUNTRY_NORMALIZATION = {'paraguai': 'paraguay', 'uruguai': 'uruguay', 'ecuador': 'equador'}
def norm(text):
    return ''.join(ch for ch in unicodedata.normalize('NFKD', text.lower()) if not unicodedata.combining(ch))
def country_key(text):
    value = norm(text)
    return COUNTRY_NORMALIZATION.get(value, value)
def esc(value):
    return html.escape(str(value), quote=True)

def member_row(country, lang):
    chips, seen = [], set()
    for member in members:
        if country_key(member['country']) != country_key(country):
            continue
        name_key = norm(member['name'])
        if name_key in seen:
            continue
        seen.add(name_key)
        card_id = CITED.get(name_key)
        if card_id:
            chips.append(f'<a class="member-chip active" href="#card-{card_id}">{esc(member["name"])}</a>')
        else:
            chips.append(f'<span class="member-chip">{esc(member["name"])}</span>')
    label = 'Associados UITP:' if lang == 'pt' else 'Asociados UITP:'
    return f'<div class="member-buttons"><span class="member-buttons-label">{label}</span>{"".join(chips)}</div>'

def card(c, lang, country_label):
    source_class = c['source_class'] if lang == 'pt' else SOURCE_CLASS_ES[c['source_class']]
    pub_date = '/'.join(reversed(c['source_publication_date'].split('-')))
    source_lang = 'PT' if c['country'] == 'Brasil' else 'ES'
    return f'''<article class="card" id="card-{c['id']}">
<div><span class="badge {c['signal']}">{SIG[lang][c['signal']]}</span></div>
<div class="meta">{country_label} · {source_lang} · {source_class} · {esc(c['theme_' + lang])} · {pub_date}</div>
<h3>{esc(c['title_' + lang])}</h3>
<div class="field"><strong>{'Resumo' if lang == 'pt' else 'Resumen'}:</strong> {esc(c['summary_' + lang])}</div>
<div class="field"><strong>{'Por que importa' if lang == 'pt' else 'Por qué importa'}:</strong> {esc(c['impact_' + lang])}</div>
<div class="meta source">{esc(c['source'])}</div>
<a class="btn" href="{esc(c['source_url'])}" target="_blank" rel="noopener">{'Saiba mais' if lang == 'pt' else 'Leer más'}</a>
</article>'''

def summary(lang):
    included = ', '.join(f'{pt if lang == "pt" else es} ({counts[c]})' for c, _, _, pt, es in COUNTRIES if counts[c])
    gaps = ', '.join(pt if lang == 'pt' else es for c, _, _, pt, es in COUNTRIES if not counts[c])
    if lang == 'pt':
        text = (f'Esta edição reúne <strong>{len(CARDS)} notícias estratégicas em {len(counts)} países</strong>: {included}. '
                f'<strong>Sinaleiros: {signals["op"]} oportunidades/avanços, {signals["watch"]} acompanhamentos, '
                f'{signals["risk"]} alertas/riscos e {signals["monitor"]} monitoramentos.</strong> '
                'A agenda concentra contratos e transição energética de ônibus no Brasil, fiscalização baseada em dados na Argentina, continuidade operacional no Chile, indicadores de uso na Colômbia e articulação entre infraestrutura, território e regulação em outros mercados. '
                f'<strong>{gaps} não tiveram notícia estratégica qualificada nesta rodada.</strong> '
                'As datas das fontes estão nos cards; a edição recupera fatos relevantes ainda não publicados na seleção dos últimos sete dias.')
        title = 'Resumo executivo'
    else:
        text = (f'Esta edición reúne <strong>{len(CARDS)} noticias estratégicas en {len(counts)} países</strong>: {included}. '
                f'<strong>Señales: {signals["op"]} oportunidades/avances, {signals["watch"]} seguimientos, '
                f'{signals["risk"]} alertas/riesgos y {signals["monitor"]} monitoreos.</strong> '
                'La agenda se concentra en contratos y transición energética de autobuses en Brasil, fiscalización basada en datos en Argentina, continuidad operacional en Chile, indicadores de uso en Colombia y articulación entre infraestructura, territorio y regulación en otros mercados. '
                f'<strong>{gaps} no tuvieron una noticia estratégica calificada en esta ronda.</strong> '
                'Las fechas de las fuentes figuran en las tarjetas; la edición recupera hechos relevantes aún no publicados en la selección de los últimos siete días.')
        title = 'Resumen ejecutivo'
    return f'<section class="box"><h2>{title}</h2><p>{text}</p></section>'

def build(lang):
    page = (E / f'approved-template-{lang}.html').read_text()
    page = page.replace('09/11/2026', '21/11/2026')
    page = page.replace('9 de novembro de 2026', '21 de novembro de 2026')
    page = page.replace('9 de noviembre de 2026', '21 de noviembre de 2026')
    page = page.replace('/edicoes/2026-11-08/', '/edicoes/2026-11-20/')
    sections, jumps = [], []
    for country, slug, flag, pt, es in COUNTRIES:
        label = pt if lang == 'pt' else es
        items = [c for c in CARDS if c['country'] == country]
        count = len(items)
        jump_class = ' empty-jump' if not count else ''
        jumps.append(f'<a class="{jump_class.strip()}" href="#{slug}">{flag} {label}</a>')
        if count:
            noun = ('notícia estratégica validada nesta edição.' if count == 1 else 'notícias estratégicas validadas nesta edição.') if lang == 'pt' else ('noticia estratégica validada en esta edición.' if count == 1 else 'noticias estratégicas validadas en esta edición.')
            count_text = f'{count} {noun}'
        else:
            count_text = 'Sem notícia estratégica qualificada nesta rodada.' if lang == 'pt' else 'Sin noticia estratégica calificada en esta ronda.'
        sections.append(f'<section class="country" id="{slug}"><h2>{flag} {label}</h2><p class="count">{count_text}</p>{member_row(country, lang)}{"".join(card(item, lang, label) for item in items)}</section>')
    jump_title = 'Ir direto para um país' if lang == 'pt' else 'Ir directo a un país'
    jump = f'<section class="box country-jump"><h2 class="jump-title">{jump_title}</h2><div class="jump jump-buttons">{"".join(jumps)}</div></section>'
    page = page.replace('{{SUMMARY}}', summary(lang)).replace('{{JUMP}}', jump).replace('{{COUNTRIES}}', ''.join(sections))
    page = page.replace('</style>', '.country-jump .jump-buttons a.empty-jump{color:#87928f;background:#f6f8f7;border-color:#e2e8e5;font-weight:650}@media(max-width:720px){.country-jump .jump-buttons{flex-wrap:nowrap;max-width:100%;overflow-x:auto}.country-jump .jump-buttons a{flex-shrink:0}}</style>')
    assert page.count('<article class="card"') == len(CARDS)
    assert page.count('class="member-buttons"') == len(COUNTRIES)
    assert 'news.google.' not in page and '{{' not in page
    ids = set(re.findall(r'\bid="([^"]+)"', page))
    for target in re.findall(r'href="#([^"]+)"', page):
        assert target in ids, target
    return page

outputs = {'pt': build('pt'), 'es': build('es')}
current = (ROOT / 'hoje/index.html').read_text()
found_dates = re.findall(r'(\d{2})/(\d{2})/(202\d)', current[:3000])
current_date = max((f'{y}-{m}-{d}' for d, m, y in found_dates), default='0000-00-00')
assert current_date <= DATE, f'Newer current edition {current_date}; do not roll back'
for lang, text in outputs.items():
    destinations = [ROOT / f'edicoes/{DATE}' / ('es/index.html' if lang == 'es' else 'index.html'), ROOT / 'hoje' / ('es/index.html' if lang == 'es' else 'index.html')]
    for destination in destinations:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text)

landing = ROOT / 'index.html'
landing_text = landing.read_text()
landing_text = re.sub(r'A edição de .*? reúne \d+ notícias estratégicas em \d+ países, com fontes originais e leitura em português e espanhol\.', f'A edição de 21 de novembro de 2026 reúne {len(CARDS)} notícias estratégicas em {len(counts)} países, com fontes originais e leitura em português e espanhol.', landing_text)
landing_text = re.sub(r'Disponível:</strong>.*?</p>', 'Disponível:</strong> 21 de novembro de 2026.</p>', landing_text)
landing_text = re.sub(r'edicoes/2026-11-\d{2}/', f'edicoes/{DATE}/', landing_text)
landing.write_text(landing_text)

index_path = ROOT / 'arquivos/clippings_index.json'
rows = [row for row in json.loads(index_path.read_text()) if row['date'] != DATE]
entry = {
    'date': DATE,
    'pt_html_path': f'edicoes/{DATE}/index.html',
    'es_html_path': f'edicoes/{DATE}/es/index.html',
    'pt_pdf_path': None, 'es_pdf_path': None,
    'pt_html_url': f'{BASE}/edicoes/{DATE}/',
    'es_html_url': f'{BASE}/edicoes/{DATE}/es/',
    'pt_pdf_url': None, 'es_pdf_url': None,
    'cards': len(CARDS), 'countries': len(counts),
    'country_counts': dict(counts), 'signal_counts': dict(signals),
}
rows = sorted([entry] + rows, key=lambda row: row['date'], reverse=True)
index_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')

csv_path = ROOT / 'arquivos/clippings_index.csv'
with csv_path.open(newline='') as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames
    old_rows = [row for row in reader if row['date'] != DATE]
assert headers is not None
new_row = {header: '' for header in headers}
new_row.update(date=DATE, pt_html=entry['pt_html_url'], es_html=entry['es_html_url'], cards=str(len(CARDS)), countries=str(len(counts)), **{signal: str(signals[signal]) for signal in ['op', 'watch', 'risk', 'monitor']})
with csv_path.open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=headers, lineterminator='\n')
    writer.writeheader()
    writer.writerows([new_row] + old_rows)

archive = ROOT / 'arquivos/clippings/index.html'
archive_text = archive.read_text()
archive_text = re.sub(r'Total arquivado: \d+ edições · Atualizado em .*?\.', f'Total arquivado: {len(rows)} edições · Atualizado em 21 de novembro de 2026.', archive_text)
archive_text = re.sub(r'<article class="card"><h2>2026-11-21</h2>.*?</article>', '', archive_text, flags=re.S)
archive_entry = f'<article class="card"><h2>{DATE}</h2><p>PANORAMA Mobilidade LATAM — {len(CARDS)} notícias estratégicas em {len(counts)} países.</p><div class="links"><a href="/edicoes/{DATE}/">HTML PT</a><a href="/edicoes/{DATE}/es/">HTML ES</a></div></article>'
archive_text = archive_text.replace('<article class="card"><h2>2026-11-20</h2>', archive_entry + '<article class="card"><h2>2026-11-20</h2>', 1)
archive.write_text(archive_text)

qa = {
    'date': DATE, 'cards': len(CARDS), 'countries': len(counts),
    'country_counts': dict(counts), 'signal_counts': dict(signals),
    'country_shortfalls': selection['country_shortfalls'],
    'google_news_final_urls': 0, 'local_qa': 'passed',
    'pdf': 'not generated: established WeasyPrint converter missing libpangoft2-1.0-0',
    'public_qa': 'not deployed',
}
(E / f'qa-{DATE}.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(qa, ensure_ascii=False))
