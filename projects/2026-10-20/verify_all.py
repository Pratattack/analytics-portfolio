"""Three documented verification stages; browser execution has its own CI result."""
import csv
import hashlib
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from acquire import verify_sources
from insurance_pipeline import build as insurance, triangle_inventory
from reit_pipeline import build as reit
from presentation import report
from sec_sources import BASE, PROJECTS, read


def hashes(folder):
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.iterdir()) if p.is_file() and p.suffix!='.sqlite'}


class Links(HTMLParser):
    def __init__(self):super().__init__();self.paths=[];self.images=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag in ['a','img','script']:
            value=attrs.get('href' if tag=='a' else 'src')
            if value and not value.startswith(('https:','http:','#','data:')):self.paths.append(value)
        if tag=='img':assert attrs.get('alt');self.images+=1


def source_lineage(slug,out):
    source_cache={};count=0
    with (out/'source_lineage.csv').open() as file:
        for row in csv.DictReader(file):
            filename=row['numeric_source_file']
            if filename not in source_cache:source_cache[filename]=read(BASE/slug/'data/raw'/filename)
            source=source_cache[filename]
            target=source
            for part in row['pointer'].strip('/').split('/'):target=target[int(part)] if isinstance(target,list) else target[part]
            assert float(row['value'])==target['value']
            assert row['context_id']==target['context_id'] and row['source_id']==target['source_id']
            assert target['unit_measure']=='iso4217:USD'
            count+=1
    return count


def main():
    sources=verify_sources()
    test=subprocess.run([sys.executable,'-m','unittest','-v','test_finance.py'],cwd=BASE,text=True,capture_output=True)
    (BASE/'test_results.txt').write_text(test.stdout+test.stderr)
    assert test.returncode==0,test.stdout+test.stderr
    builders=[insurance,reit];result={}
    for slug,builder in zip(PROJECTS,builders):
        root=BASE/slug;out=root/'outputs';payload=builder(out);report(payload,out)
        expected=read(root/'data/expected_results.json')
        assert payload['metrics']==expected,'Published measured results changed; review source/method differences'
        traced=source_lineage(slug,out)
        audit=read(root/'source_html_audit.json')
        assert audit['status']=='PASS'
        manifest=read(root/'data/source_manifest.json')
        for item in audit['filings']:
            issuer=next(m for m in manifest if m['ticker']==item['ticker'])
            filing=issuer['annual_filing_2025'] if item['filing_year']==2025 else next(f for f in issuer['history_filings'] if f['year']==item['filing_year'])
            assert item['source_html_sha256']==filing['html_sha256'] and item['status']=='PASS'
        if slug.startswith('insurance'):
            _,cells,_,_=triangle_inventory()
            with (out/'sql_current_balances.csv').open() as file:
                for row in csv.DictReader(file):
                    gid=row['group_id'];independent=sum(value-cells[(g,ay,vy,'paid')] for (g,ay,vy,metric),value in cells.items() if g==gid and vy==2025 and metric=='incurred')
                    assert math.isclose(independent,float(row['reported_comparable_unpaid']),abs_tol=.01)
        else:
            with (out/'sql_maturity_exposure.csv').open() as file:
                for row in csv.DictReader(file):
                    source=next(r for r in payload['inputs'] if r['ticker']==row['ticker'])
                    assert float(row['five_year_principal'])==sum(source['maturities'])
            # Original annual CFO pointers are also re-read, not just the generated historical table.
            for row in payload['history']:
                source=read(root/'data/raw'/row['source_file']);target=source
                for part in row['pointer'].strip('/').split('/'):target=target[int(part)] if isinstance(target,list) else target[part]
                assert target.get('value',target.get('val'))==row['cfo']
        with tempfile.TemporaryDirectory() as temporary:
            paths=[Path(temporary)/'first',Path(temporary)/'second']
            for path in paths:
                module='insurance_pipeline' if slug.startswith('insurance') else 'reit_pipeline'
                code='from pathlib import Path;from '+module+' import build;from presentation import report;import sys;p=Path(sys.argv[1]);report(build(p),p)'
                subprocess.run([sys.executable,'-c',code,str(path)],cwd=BASE,check=True,capture_output=True)
            assert hashes(paths[0])==hashes(paths[1])==hashes(out),'Clean-process output mismatch'
        for page in ['report.html','app.html']:
            parser=Links();parser.feed((out/page).read_text())
            for path in parser.paths:assert (out/path).is_file() and (out/path).stat().st_size>0,path
            if page=='report.html':assert parser.images==1
        ET.parse(out/'decision_evidence.svg')
        evidence=dict(stage_1=dict(status='PASS',pinned_archives=sources,source_lineage_values=traced,
                                  original_html_audit='source_html_audit.json; independently executed against pinned original documents; rerun audit_html.py after acquire --rebuild-inline --download-missing'),
                      stage_2=dict(status='PASS',checks=['14 hand-worked/source/method tests','All accepted factors independently reconciled with NumPy','180 refinancing constraints independently solved with SciPy/HiGHS','All SQL monetary aggregates independently reconciled']),
                      stage_3=dict(status='PASS',checks=['Two fresh Python-process output directories','All non-SQLite artifacts byte-identical across clean runs','Local HTML links, image alt text and SVG XML checked']),
                      browser_acceptance='Separate finance-browser-acceptance job; only its actual result and results.json establish browser PASS',
                      limitations=['No physical-device, client, actuary or lender validation','Economic and financial promotion gates are separate from software checks'],
                      generated_artifact_sha256=hashes(out))
        (root/'verification.json').write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
        result[slug]='PASS'
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
