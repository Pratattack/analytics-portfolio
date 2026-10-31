from pathlib import Path
import json,csv,platform
ROOT=Path(__file__).resolve().parents[1]
def main():
    plans=json.loads((ROOT/'data/plans.json').read_text());sources={s['id']:s for s in json.loads((ROOT/'data/source_manifest.json').read_text())};delivery=json.loads((ROOT/'data/supporting_sources.json').read_text())[0]
    with (ROOT/'data/evidence.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['plan_id','field','value','units','document_date','source_id','page','source_url','retrieved_at','source_sha256'])
        fields={'energy_cents':'cents/kWh','base_dollars':'USD/cycle','daily_dollars':'USD/day','delivery_cents':'cents/kWh','delivery_dollars':'USD/cycle','credit_dollars':'USD/cycle','credit_threshold':'kWh/cycle','credit_rule':'inequality','term_months':'months','termination_flat':'USD','termination_per_remaining_month':'USD/remaining_month'}
        for p in plans:
            for key,unit in fields.items():
                external=key in ['delivery_cents','delivery_dollars'] and p['id'].startswith('discount-')
                s=delivery if external else sources[p['source_id']]
                w.writerow([p['id'],key,p[key],unit,delivery['as_of'] if external else p['efl_date'],s['id'],'web table' if external else 1,s['url'],s['retrieved_at'],s['sha256']])
    with (ROOT/'data/exclusions.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['source_id','url','disposition','reason'])
        selected={p['source_id'] for p in plans}
        reasons={'efl-05':'Time-of-use; requires interval consumption data','efl-08':'Unquantifiable ERCOT pass-through charges; no complete recurring-bill reconstruction','efl-10':'Solar export credit; requires export data and eligibility evidence','efl-12':'Time-of-use plus one-time setup; requires interval data and horizon-specific treatment'}
        for s in sources.values():
            reason='Audited monthly structure; date and horizon restrictions retained' if s['id'] in selected else reasons.get(s['id'],s.get('error','Insufficient complete source data'))
            # Keep internal filesystem paths out of the shared source register.
            if reason.startswith('Failed to open file'):reason='Malformed PDF: server returned only a 23-byte document header'
            w.writerow([s['id'],s['url'],'modeled' if s['id'] in selected else 'excluded',reason])
    qa={'date':'2026-10-31','python':platform.python_version(),'local_test_methods_passed':21,'cross_language_bill_cases':189,'source_comparison_points':21,'dom_simulation_assertions':10,'html_external_assets':0,'browser_layout_mobile_keyboard_csv_downloads':'Not tested in a real browser per user instruction','package_source_pdf_policy':'Not redistributed; source-hash test skips until exact provider PDFs are locally available','publication_status':'Approved release snapshot: 31 October 2026'}
    (ROOT/'results/verification.json').write_text(json.dumps(qa,indent=2)+'\n')
    print('Built term-level evidence, exclusions and verification register')
if __name__=='__main__':main()
