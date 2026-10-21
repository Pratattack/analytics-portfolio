"""Explicit, deterministic source selection; no matching by human-readable label."""
from datetime import date
import math
import json
from sec_sources import CUTOFF


def annual_accession(document, year):
    candidates = []
    for fact in document['facts']['us-gaap'].get('Assets', {}).get('units', {}).get('USD', []):
        if fact.get('end') != f'{year}-12-31' or fact.get('form') != '10-K' or fact['filed'] > CUTOFF: continue
        gap = (date.fromisoformat(fact['filed'])-date(year, 12, 31)).days
        if 0 <= gap <= 183: candidates.append((fact['filed'], fact['accn']))
    return min(candidates) if candidates else None


def gaap(document, concept, end, start=None, accession=None, latest=False):
    rows = document['facts']['us-gaap'].get(concept, {}).get('units', {}).get('USD', [])
    eligible = [(i, r) for i, r in enumerate(rows) if r.get('end') == end and r.get('start') == start
                and r.get('form') in ['10-K', '10-K/A'] and r['filed'] <= CUTOFF
                and (accession is None or r['accn'] == accession)]
    if not eligible: return None
    if latest:
        last = max(r['filed'] for _, r in eligible)
        eligible = [(i, r) for i, r in eligible if r['filed'] == last]
    values = {r['val'] for _, r in eligible}
    if len(values) != 1: raise ValueError(f'Conflicting source values: {concept} {end}')
    i, r = eligible[0]
    return dict(value=r['val'], concept='us-gaap:'+concept, end=end, start=start,
                accession=r['accn'], filed=r['filed'], pointer=f'/facts/us-gaap/{concept}/units/USD/{i}')


def ix(facts, concepts, end='2025-12-31', start=None, dimensions=None):
    dimensions = dimensions or {}
    for concept in concepts:
        rows = [r for r in facts if r['concept'] == concept and r.get('instant', r.get('enddate')) == end
                and r.get('startdate') == start and r['dimensions'] == dimensions and not r.get('typed_dimensions')]
        if not rows: continue
        if any(r.get('unit_measure') != 'iso4217:USD' for r in rows): raise ValueError('Required financial value has a non-USD unit')
        values = {r['value'] for r in rows}
        if len(values) != 1: raise ValueError(f'Ambiguous inline fact {concept}: {values}')
        return dict(rows[0], duplicate_count=len(rows))
    return None


def required(fact, label):
    if fact is None: raise ValueError('Missing required disclosure: '+label)
    if not math.isfinite(fact['value']): raise ValueError('Nonfinite disclosure: '+label)
    return fact['value']
