"""Line-level paid-loss triangle challenge from original SEC inline-XBRL facts."""
from collections import defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import sqlite3
from statistics import median
from finance_models import chain_ladder
from sec_sources import BASE, read, dump
from source_selection import annual_accession, gaap

SLUG = 'insurance-reserve-capital-review'
PAID = 'us-gaap:ShortdurationInsuranceContractsCumulativePaidClaimsAndAllocatedClaimAdjustmentExpenseNet'
INCURRED = 'us-gaap:ShortdurationInsuranceContractsIncurredClaimsAndAllocatedClaimAdjustmentExpenseNet'


def csv_write(path, rows):
    if not rows: return
    fields = list(rows[0])
    with path.open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fields, lineterminator='\n'); writer.writeheader(); writer.writerows(rows)


def label(dimensions):
    values = [re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', member.split(':')[-1].removesuffix('Member')) for member in dimensions.values()]
    return ' / '.join(values) if values else 'Consolidated aggregate (not additive to component lines)'


def triangle_inventory():
    root = BASE / SLUG
    groups, cells, lineage, duplicates = {}, {}, [], 0
    for issuer in read(root / 'data/source_manifest.json'):
        ticker = issuer['ticker']; raw = read(root / 'data/raw' / f'{ticker}-2025-inline.json.gz')
        for index, fact in enumerate(raw['facts']):
            if fact['concept'] not in [PAID, INCURRED]: continue
            if fact['unit_measure'] != 'iso4217:USD': raise ValueError('Triangle value is not a USD amount')
            dimensions = dict(fact['dimensions'])
            axes = [axis for axis in dimensions if 'accidentyearaxis' in axis.lower()]
            if len(axes) != 1 or fact.get('typed_dimensions'): continue
            member = dimensions.pop(axes[0]); match = re.search(r'accidentyear(20\d{2})member$', member.lower())
            if not match: continue
            ay = int(match.group(1)); instant = fact.get('instant')
            if not instant or not instant.endswith('-12-31'): continue
            vy = int(instant[:4])
            if not 2015 <= ay <= vy <= 2025: continue
            dims = json.dumps(dimensions, sort_keys=True, separators=(',', ':'))
            group = ticker + '-' + hashlib.sha256(dims.encode()).hexdigest()[:10]
            groups[group] = dict(group_id=group, ticker=ticker, line=label(dimensions), dimensions=dims,
                                 aggregate=not dimensions, source_url=raw['source_url'], accession=raw['accession'], filed=raw['filed'])
            metric = 'paid' if fact['concept'] == PAID else 'incurred'
            key = (group, ay, vy, metric)
            if key in cells:
                if cells[key] != fact['value']: raise ValueError('Conflicting duplicate triangle cell: '+str(key))
                duplicates += 1
            cells[key] = fact['value']
            lineage.append(dict(group_id=group, accident_year=ay, valuation_year=vy, metric=metric,
                                value=fact['value'], numeric_source_file=f'{ticker}-2025-inline.json.gz',
                                pointer=f'/facts/{index}', context_id=fact['context_id'], source_id=fact['source_id'],
                                scale=fact['scale'], sign=fact['sign'], displayed=fact['displayed'],
                                source_html_sha256=raw['source_html_sha256']))
    return groups, cells, lineage, duplicates


def complete_triangle(data, cutoff):
    years = sorted({ay for ay, vy in data if vy <= cutoff})
    if not years or years != list(range(years[0], cutoff+1)): raise ValueError('Nonconsecutive accident years')
    for ay in years:
        for vy in range(ay, cutoff+1):
            if (ay, vy) not in data: raise ValueError('Incomplete cumulative paid triangle')


def build(destination=None):
    root = BASE / SLUG; out = destination or root / 'outputs'; out.mkdir(parents=True, exist_ok=True)
    groups, cells, lineage, duplicates = triangle_inventory()
    rows, inventory, factors, predictions, sensitivity = [], [], [], [], []
    for group_id, group in sorted(groups.items()):
        paid = {(ay, vy): value for (g, ay, vy, metric), value in cells.items() if g == group_id and metric == 'paid'}
        incurred = {(ay, vy): value for (g, ay, vy, metric), value in cells.items() if g == group_id and metric == 'incurred'}
        eligible, reason = True, ''
        if group['aggregate']: eligible, reason = False, 'Aggregate overlaps separately disclosed component lines'
        try:
            complete_triangle(paid, 2025)
            fit = chain_ladder(paid, 2025)
        except ValueError as error: eligible, reason = False, str(error)
        current_ays = sorted(ay for ay, vy in paid if vy == 2025)
        reported = None
        if all((ay, 2025) in incurred for ay in current_ays):
            reported = sum(incurred[(ay, 2025)]-paid[(ay, 2025)] for ay in current_ays)
        if reported is None or reported < 0: eligible, reason = False, 'Missing or negative comparable incurred-minus-paid balance'
        inventory.append(dict(**group, accident_years=len(current_ays), paid_cells=len(paid), eligible=eligible, exclusion_reason=reason,
                              reported_unpaid_comparable=reported))
        if eligible:
            fitted_median = chain_ladder(paid, 2025, method='median')
            candidates = []
            for method in ['volume', 'median']:
                for tail in [1.0, 1.05, 1.10]:
                    result = chain_ladder(paid, 2025, method=method, tail=tail)
                    sensitivity.append(dict(group_id=group_id, method=method, tail_factor=tail, unpaid=result['unpaid'],
                                            gap_to_reported=result['unpaid']-reported))
                    candidates.append(result['unpaid'])
            rows.append(dict(group_id=group_id, ticker=group['ticker'], line=group['line'],
                             reported_unpaid=reported, chain_ladder_unpaid=fit['unpaid'],
                             gap=fit['unpaid']-reported, median_method_unpaid=fitted_median['unpaid'],
                             sensitivity_low=min(candidates), sensitivity_high=max(candidates),
                             tail_10pct_increment=chain_ladder(paid, 2025, tail=1.10)['unpaid']-fit['unpaid'],
                             oldest_factor_support=min(fit['support'].values()), accident_years=len(current_ays)))
            for method,model in [('volume',fit),('median',fitted_median)]:
                for age, factor in model['factors'].items():
                    factors.append(dict(group_id=group_id, method=method, development_age=age, factor=factor, support=model['support'][age]))
        # Eligibility is recalculated from each masked diagonal, independent of the 2025 model gate.
        if group['aggregate']: continue
        for cutoff in [2022, 2023, 2024]:
            try:
                complete_triangle(paid, cutoff)
                fitted = chain_ladder(paid, cutoff)
            except ValueError: continue
            max_age = max(fitted['factors'])+1
            for estimate in fitted['estimates']:
                ay = estimate['accident_year']
                if cutoff-ay >= max_age or (ay, cutoff+1) not in paid: continue
                previous = paid.get((ay, cutoff-1), 0)
                current = paid[(ay, cutoff)]; actual = paid[(ay, cutoff+1)]-current
                baseline = current-previous
                prediction = estimate['next_paid']-current
                predictions.append(dict(group_id=group_id, ticker=group['ticker'], accident_year=ay,
                                        masked_cutoff=cutoff, target_valuation_year=cutoff+1, actual_movement=actual,
                                        chain_ladder_movement=prediction, repeat_increment_baseline=baseline,
                                        model_absolute_error=abs(actual-prediction), baseline_absolute_error=abs(actual-baseline)))
    rows.sort(key=lambda r: (-r['tail_10pct_increment'], r['group_id']))
    for rank, row in enumerate(rows, 1): row['tail_sensitivity_review_rank'] = rank
    cell_rows = [dict(group_id=g, accident_year=ay, valuation_year=vy, metric=metric, value=value)
                 for (g, ay, vy, metric), value in sorted(cells.items())]
    for name, data in [('triangle_cells.csv', cell_rows), ('source_lineage.csv', lineage), ('triangle_inventory.csv', inventory),
                       ('reserve_review.csv', rows), ('development_factors.csv', factors), ('masked_diagonal_diagnostic.csv', predictions),
                       ('model_tail_sensitivity.csv', sensitivity)]: csv_write(out / name, data)
    database = out / 'analysis.sqlite'
    if database.exists(): database.unlink()
    with sqlite3.connect(database) as db:
        db.execute('CREATE TABLE cells(group_id TEXT, accident_year INTEGER, valuation_year INTEGER, metric TEXT, value REAL, PRIMARY KEY(group_id,accident_year,valuation_year,metric))')
        db.executemany('INSERT INTO cells VALUES(:group_id,:accident_year,:valuation_year,:metric,:value)', cell_rows)
        sql = (root / 'analysis.sql').read_text()
        db.executescript(sql)
        query = db.execute('SELECT * FROM current_balances ORDER BY group_id')
        sql_rows = [dict(zip([c[0] for c in query.description], values)) for values in query.fetchall()]
        csv_write(out / 'sql_current_balances.csv', sql_rows)
    model_error = sum(r['model_absolute_error'] for r in predictions)
    baseline_error = sum(r['baseline_absolute_error'] for r in predictions)
    denominator = sum(abs(r['actual_movement']) for r in predictions)
    metrics = dict(industry='Property and casualty insurance', issuer_count=len(read(root/'data/source_manifest.json')),
                   numeric_triangle_cells=len(cells), source_lineage_rows=len(lineage), equal_duplicate_facts=duplicates,
                   candidate_triangles=len(groups), eligible_triangles=len(rows), excluded_triangles=len(groups)-len(rows),
                   diagnostic_cells=len(predictions), diagnostic_target_years=[2023, 2024, 2025],
                   model_wape=model_error/denominator, baseline_wape=baseline_error/denominator,
                   absolute_error_difference_usd=baseline_error-model_error,
                   reported_comparable_unpaid=sum(r['reported_unpaid'] for r in rows),
                   model_unpaid=sum(r['chain_ladder_unpaid'] for r in rows),
                   one_tenth_tail_increment=sum(r['tail_10pct_increment'] for r in rows),
                   predictive_promotion=False, financial_decision='Prioritize actuarial diligence; no reserve release or capital-return authorization',
                   timing='2025 filing triangles; historical diagonals masked in a revised current-disclosure cohort, not an as-released backtest',
                   source_cutoff='2026-10-20', assumption='Tail factors and method envelopes are sensitivities, not confidence intervals')
    dump(out / 'metrics.json', metrics)
    payload = dict(kind='insurance', metrics=metrics, rows=rows, inventory=inventory, factors=factors,
                   predictions=predictions, cells=cell_rows, sensitivity=sensitivity)
    dump(out / 'application_data.json', payload)
    return payload


if __name__ == '__main__':
    print(json.dumps(build()['metrics'], indent=2))
