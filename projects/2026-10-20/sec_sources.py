"""SEC numeric source extraction with explicit periods, entities, dimensions and scale."""
from decimal import Decimal, InvalidOperation
import gzip
import hashlib
import json
from pathlib import Path
import re
import urllib.request
from lxml import html

BASE = Path(__file__).resolve().parent
CUTOFF = '2026-10-20'
PROJECTS = ['insurance-reserve-capital-review', 'retail-reit-refinancing-review']


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    path.write_bytes(gzip.compress(text, mtime=0) if path.suffix == '.gz' else text + b'\n')


def read(path):
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes())


def numeric(text, scale=0, sign=None):
    text = text.replace('\u00a0', '').replace(',', '').strip()
    if text in ['—', '–', '-']: return 0.0
    if not text: raise ValueError('Blank numeric fact')
    if text.startswith('(') and text.endswith(')'): text = '-' + text[1:-1]
    try: value = Decimal(text) * Decimal(10) ** int(scale or 0)
    except (InvalidOperation, ValueError) as error: raise ValueError('Unparseable numeric fact') from error
    if sign == '-': value = -abs(value)
    if not value.is_finite(): raise ValueError('Nonfinite numeric fact')
    return float(value)


def inline_facts(data):
    root = html.fromstring(data)
    contexts = {}
    units = {}
    for node in root.iter():
        if str(node.tag).lower() == 'xbrli:unit':
            units[node.get('id')] = ','.join((child.text or '').strip() for child in node.iterdescendants() if str(child.tag).lower() == 'xbrli:measure')
    for node in root.iter():
        if str(node.tag).lower() != 'xbrli:context': continue
        context = {'dimensions': {}}
        for child in node.iterdescendants():
            tag = str(child.tag).lower()
            if tag in ['xbrli:identifier', 'xbrli:instant', 'xbrli:startdate', 'xbrli:enddate']:
                context[tag.split(':')[-1]] = (child.text or '').strip()
            if tag == 'xbrldi:explicitmember': context['dimensions'][child.get('dimension')] = (child.text or '').strip()
            if tag == 'xbrldi:typedmember': context['typed_dimensions'] = True
        contexts[node.get('id')] = context
    facts, rejected = [], []
    for position, node in enumerate(root.iter()):
        if str(node.tag).lower() != 'ix:nonfraction': continue
        context = contexts.get(node.get('contextref'))
        if context is None: raise ValueError('Inline fact has unknown context')
        text = ''.join(node.itertext()).strip()
        try:
            if node.get('xsi:nil') == 'true': raise ValueError('Explicit nil numeric fact')
            value = numeric(text, node.get('scale'), node.get('sign'))
        except ValueError as error:
            rejected.append({'concept': node.get('name'), 'context_id': node.get('contextref'), 'reason': str(error)})
            continue
        facts.append(dict(concept=node.get('name'), context_id=node.get('contextref'), source_id=node.get('id'),
                          position=position, unit=node.get('unitref'), unit_measure=units.get(node.get('unitref')), scale=node.get('scale'), sign=node.get('sign'),
                          displayed=text, value=value, **context))
    return {'facts': facts, 'rejected_numeric': rejected, 'contexts': len(contexts)}


def acquire_inline():
    for slug in PROJECTS:
        root = BASE / slug
        manifest = read(root / 'data/source_manifest.json')
        for issuer in manifest:
            filing = issuer['annual_filing_2025']
            path = root / 'data/raw' / filing['file']
            if not path.exists():
                request = urllib.request.Request(filing['url'], headers={'User-Agent': 'Prathamesh Singh independent portfolio research github.com/Pratattack'})
                data = urllib.request.urlopen(request, timeout=90).read()
                assert hashlib.sha256(data).hexdigest() == filing['html_sha256'], 'Official filing bytes changed; review source'
                path.write_bytes(gzip.compress(data, mtime=0))
            data = gzip.decompress(path.read_bytes())
            assert hashlib.sha256(data).hexdigest() == filing['html_sha256']
            extracted = inline_facts(data)
            extracted.update(source_url=filing['url'], source_html_sha256=filing['html_sha256'], accession=filing['accn'], filed=filing['filed'])
            destination = root / 'data/raw' / f"{issuer['ticker']}-2025-inline.json.gz"
            dump(destination, extracted)
            print(slug, issuer['ticker'], len(extracted['facts']), 'numeric facts', flush=True)


if __name__ == '__main__':
    acquire_inline()
