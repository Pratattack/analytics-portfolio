"""Consolidated retail-property debt schedules and a constrained cash-flow reverse stress."""
import json
import math
from pathlib import Path
import sqlite3
from finance_models import cash_path, required_rollover
from insurance_pipeline import csv_write
from sec_sources import BASE, read, dump
from source_selection import ix, required, annual_accession, gaap

SLUG = 'retail-reit-refinancing-review'
PREFIX = 'us-gaap:LongTermDebtMaturitiesRepaymentsOfPrincipal'
SUFFIXES = ['InNextTwelveMonths', 'InYearTwo', 'InYearThree', 'InYearFour', 'InYearFive', 'AfterYearFive']


def records():
    root = BASE / SLUG
    result, lineage, maturity_rows, bridges, history, coverage = [], [], [], [], [], []
    for issuer in read(root / 'data/source_manifest.json'):
        ticker = issuer['ticker']; raw = read(root/'data/raw'/f'{ticker}-2025-inline.json.gz'); facts = raw['facts']
        scope = {'dei:LegalEntityAxis': 'skt:TangerPropertiesLimitedPartnershipMember'} if ticker == 'SKT' else {}
        debt_scope = {'us-gaap:LongtermDebtTypeAxis': 'us-gaap:UnsecuredDebtMember'} if ticker == 'KIM' else scope
        row = dict(ticker=ticker, entity=issuer['entity_name'], financial_scope='Operating partnership' if ticker=='SKT' else 'Consolidated parent',
                   source_url=raw['source_url'], accession=raw['accession'], filed=raw['filed'])
        def get(field, concepts, start=None, dimensions=None, end='2025-12-31'):
            selected = ix(facts, concepts, end=end, start=start, dimensions=scope if dimensions is None else dimensions)
            value = required(selected, ticker+' '+field)
            lineage.append(dict(ticker=ticker, field=field, value=value, concept=selected['concept'], context_id=selected['context_id'],
                                dimensions=json.dumps(selected['dimensions'], sort_keys=True), source_id=selected['source_id'],
                                numeric_source_file=f'{ticker}-2025-inline.json.gz', pointer='/facts/'+str(facts.index({k:v for k,v in selected.items() if k!='duplicate_count'})),
                                source_url=raw['source_url'], accession=raw['accession'], filed=raw['filed']))
            return value
        row['cfo'] = get('cfo', ['us-gaap:NetCashProvidedByUsedInOperatingActivities'], start='2025-01-01')
        if ticker == 'REG':
            gross_cash = get('cash_including_restricted', ['us-gaap:CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents'])
            restricted = get('restricted_cash', ['us-gaap:RestrictedCashAndCashEquivalents'])
            row['cash'] = gross_cash-restricted
        else: row['cash'] = get('cash', ['us-gaap:CashAndCashEquivalentsAtCarryingValue'])
        if ticker == 'KIM': row['distributions'] = get('distributions', ['us-gaap:PaymentsOfOrdinaryDividends'], start='2025-01-01')
        elif ticker == 'REG':
            row['distributions'] = sum(get(field, [concept], start='2025-01-01') for field,concept in [
                ('common_dividends','us-gaap:PaymentsOfDividendsCommonStock'),
                ('preferred_dividends','us-gaap:PaymentsOfDividendsPreferredStockAndPreferenceStock'),
                ('minority_distributions','us-gaap:PaymentsOfDividendsMinorityInterest')])
        elif ticker == 'FRT':
            row['distributions'] = get('common_preferred_dividends', ['frt:DividendsPaidToCommonAndPreferredShareholders'], start='2025-01-01') + get('minority_distributions_redemptions', ['frt:Paymentsofdividendsandredemptionsminorityinterest'], start='2025-01-01')
        elif ticker == 'BRX': row['distributions'] = get('distributions', ['us-gaap:PaymentsOfCapitalDistribution'], start='2025-01-01')
        elif ticker == 'SKT': row['distributions'] = get('distributions', ['us-gaap:PaymentsOfDividends'], start='2025-01-01')
        elif ticker == 'SPG': row['distributions'] = get('common_preferred_dividends', ['spg:PaymentsOfOrdinaryDividendsCommonStockAndPreferredStock'], start='2025-01-01') + get('minority_distributions', ['us-gaap:PaymentsOfDividendsMinorityInterest'], start='2025-01-01')
        maturities=[]
        for offset,suffix in enumerate(SUFFIXES):
            value = get('maturity_'+str(offset+1), [PREFIX+suffix], dimensions=debt_scope)
            maturities.append(value)
            maturity_rows.append(dict(ticker=ticker, maturity_bucket=2026+offset if offset<5 else 'After 2030',
                                      ordinal=offset+1, principal=value, scope=json.dumps(debt_scope,sort_keys=True)))
        row['maturities'] = maturities[:5]; row['after_2030'] = maturities[5]
        debt_concepts = ['us-gaap:NotesPayable'] if ticker=='KIM' else ['us-gaap:DebtAndCapitalLeaseObligations'] if ticker=='FRT' else ['us-gaap:LongTermDebt']
        row['book_debt'] = get('book_debt', debt_concepts)
        row['principal_total'] = sum(maturities)
        row['principal_book_difference'] = row['principal_total']-row['book_debt']
        bridges.append(dict(ticker=ticker, scheduled_face_principal=row['principal_total'], book_debt=row['book_debt'],
                            face_minus_book=row['principal_book_difference'], difference_share=row['principal_book_difference']/row['principal_total'],
                            assessment='Principal / carrying-value basis retained; not treated as cash repayment',
                            note='KIM excludes unconsolidated JV mortgages; SKT uses operating-partnership financials; borrowing fees/discounts are not principal'))
        if abs(row['principal_book_difference'])/row['principal_total'] > .02:
            raise ValueError(ticker+' debt-scope bridge exceeds 2% review tolerance; do not silently use this schedule')
        if min(row['cash'], row['distributions'], *maturities) < 0: raise ValueError('Negative source cash/distributions/maturity')
        # Historical CFO is context for shock severity, never used to fit a cash forecast.
        document=read(root/'data/raw'/f'{ticker}.json.gz')
        extra=[read(root/'data/raw'/f"{ticker}-{f['year']}-inline.json.gz") for f in issuer.get('history_filings',[])]
        for year in range(2019,2026):
            end,start=f'{year}-12-31',f'{year}-01-01'
            source=None;value=None
            if ticker!='SKT':
                anchor=annual_accession(document,year)
                selected=gaap(document,'NetCashProvidedByUsedInOperatingActivities',end,start,accession=anchor[1]) if anchor else None
                if selected:
                    value=selected['value'];source=dict(filed=selected['filed'],accession=selected['accession'],pointer=selected['pointer'],source_file=f'{ticker}.json.gz',source_id='')
            if source is None:
                for candidate in sorted([raw]+extra,key=lambda r:r['filed']):
                    selected=ix(candidate['facts'],['us-gaap:NetCashProvidedByUsedInOperatingActivities'],end=end,start=start,dimensions=scope)
                    if selected:
                        value=selected['value'];source=dict(filed=candidate['filed'],accession=candidate['accession'],pointer='/facts/'+str(candidate['facts'].index({k:v for k,v in selected.items() if k!='duplicate_count'})),source_file=next(f'{ticker}-{f["year"]}-inline.json.gz' for f in issuer.get('history_filings',[]) if f['accn']==candidate['accession']) if candidate is not raw else f'{ticker}-2025-inline.json.gz',source_id=selected['source_id']);break
            if source:
                history.append(dict(ticker=ticker,year=year,cfo=value,scope=row['financial_scope'],**source))
            else:coverage.append(dict(ticker=ticker,year=year,field='cfo',reason='No CFO value in the specified annual/entity source context'))
        result.append(row)
    return result,lineage,maturity_rows,bridges,history,coverage


def build(destination=None):
    root=BASE/SLUG;out=destination or root/'outputs';out.mkdir(parents=True,exist_ok=True)
    inputs,lineage,maturities,bridges,history,coverage=records()
    scenarios, paths, decisions, frontiers, recovery=[],[],[],[],[]
    for row in inputs:
        baseline=cash_path(row)
        grid=[]
        for decline in [0,.1,.2,.3,.4]:
            for spread in [0,200,400]:
                solution=required_rollover(row,cfo_decline=decline,spread_bps=spread)
                item=dict(ticker=row['ticker'],cfo_decline=decline,spread_bps=spread,**solution)
                scenarios.append(item);grid.append(item)
                for period in cash_path(row,cfo_decline=decline,spread_bps=spread):
                    paths.append(dict(ticker=row['ticker'],cfo_decline=decline,spread_bps=spread,**period))
        feasible=all(r['feasible'] for r in grid)
        reverse=cash_path(row,spread_bps=200)
        max_decline=min((p['closing_cash']-p['cash_floor'])/((i+1)*row['cfo']) for i,p in enumerate(reverse))
        decisions.append(dict(ticker=row['ticker'],financial_scope=row['financial_scope'],annual_cfo=row['cfo'],annual_distributions=row['distributions'],cash=row['cash'],
                              next_12m_maturities=row['maturities'][0],five_year_maturities=sum(row['maturities']),
                              baseline_fully_rolled_minimum_cash=min(p['closing_cash'] for p in baseline),
                              baseline_cash_floor=row['cfo']*.1,baseline_feasible=all(p['shortfall']<=1e-6 for p in baseline),
                              one_year_cash_to_maturity=(row['cash']+.9*row['cfo']-row['distributions'])/row['maturities'][0] if row['maturities'][0] else None,
                              robust_common_rollover=max(r['minimum_rollover'] for r in grid) if feasible else None,
                              robust_feasible_without_new_liquidity=feasible,
                              maximum_scenario_liquidity_shortfall=max(r['required_liquidity'] for r in grid),
                              maximum_cfo_decline_at_200bps=max_decline,
                              decision='Validate committed liquidity / distributions / investment timing before authorizing deleveraging' if not feasible else 'Conditional deleveraging envelope; verify actual credit terms before adoption'))
        for rollover in [0,.25,.5,.75,1]:
            for spread in [0,200,400]:
                for period in cash_path(row,rollover=rollover,cfo_decline=.2,spread_bps=spread):
                    frontiers.append(dict(ticker=row['ticker'],rollover=rollover,spread_bps=spread,**period))
        for decline in [.2,.4]:
            for spread in [200,400]:
                for duration in [2,5]:
                    recovery.append(dict(ticker=row['ticker'],cfo_decline=decline,spread_bps=spread,recovery_after=duration,
                                         **required_rollover(row,cfo_decline=decline,spread_bps=spread,recovery_after=duration)))
    for name,rows in [('source_lineage.csv',lineage),('debt_maturities.csv',maturities),('debt_basis_bridge.csv',bridges),
                      ('comparative_cfo.csv',history),('disclosure_coverage.csv',coverage),('scenario_solutions.csv',scenarios),
                      ('cash_waterfalls.csv',paths),('financing_review.csv',decisions),('rollover_frontier.csv',frontiers),('recovery_sensitivity.csv',recovery)]:
        csv_write(out/name,rows)
    database=out/'analysis.sqlite'
    if database.exists():database.unlink()
    with sqlite3.connect(database) as db:
        db.execute('CREATE TABLE maturity(ticker TEXT, ordinal INTEGER, principal REAL, PRIMARY KEY(ticker,ordinal))')
        db.executemany('INSERT INTO maturity VALUES(:ticker,:ordinal,:principal)',maturities)
        db.executescript((root/'analysis.sql').read_text())
        q=db.execute('SELECT * FROM maturity_exposure ORDER BY ticker');names=[r[0] for r in q.description]
        csv_write(out/'sql_maturity_exposure.csv',[dict(zip(names,r)) for r in q.fetchall()])
    changes=[]
    for ticker in sorted({r['ticker'] for r in history}):
        annual={r['year']:r['cfo'] for r in history if r['ticker']==ticker}
        for year in sorted(annual):
            if year-1 in annual and annual[year-1]>0:changes.append(dict(ticker=ticker,year=year,cfo_change=annual[year]/annual[year-1]-1))
    csv_write(out/'historical_cfo_changes.csv',changes)
    metrics=dict(industry='Listed retail-property REITs',issuers=len(inputs),source_maturity_buckets=len(maturities),
                 source_lineage_facts=len(lineage),comparative_cfo_observations=len(history),
                 disclosed_face_principal=sum(r['principal_total'] for r in inputs),five_year_maturities=sum(sum(r['maturities']) for r in inputs),
                 next_twelve_month_maturities=sum(r['maturities'][0] for r in inputs),baseline_feasible_issuers=sum(r['baseline_feasible'] for r in decisions),
                 historical_cfo_changes=len(changes),worst_observed_annual_cfo_change=min(r['cfo_change'] for r in changes),
                 historical_declines_beyond_30pct=sum(r['cfo_change']<-.3 for r in changes),
                 scenario_count=len(scenarios),infeasible_scenarios=sum(not r['feasible'] for r in scenarios),
                 robust_feasible_issuers=sum(r['robust_feasible_without_new_liquidity'] for r in decisions),
                 sum_issuer_worst_case_new_liquidity=sum(r['maximum_scenario_liquidity_shortfall'] for r in decisions),
                 source_cutoff='2026-10-20',statement_date='2025-12-31',information_set='Common audited annual base filed February 2026; not current October treasury positions',
                 initial_grid_scenarios=sum(r['cfo_decline']<=.3 for r in scenarios),empirical_severity_challenge_scenarios=sum(r['cfo_decline']==.4 for r in scenarios),
                 two_year_shock_40pct_400bps_feasible=sum(r['feasible'] for r in recovery if r['recovery_after']==2 and r['cfo_decline']==.4 and r['spread_bps']==400),
                 assumptions='CFO declines 0/10/20/30/40%; 40% is an added historical-severity challenge, not a fitted probability. Incremental spreads 0/200/400bp; assumed capex 10% of base CFO, 1% issuance fee, cash floor 10% of base CFO; distributions held fixed',
                 decision='Size a conditional funding envelope; no credit commitment or investment recommendation')
    dump(out/'metrics.json',metrics)
    payload=dict(kind='reit',metrics=metrics,inputs=inputs,rows=decisions,scenarios=scenarios,paths=paths,bridges=bridges,history=history,recovery=recovery)
    dump(out/'application_data.json',payload)
    return payload


if __name__=='__main__':
    print(json.dumps(build()['metrics'],indent=2))
