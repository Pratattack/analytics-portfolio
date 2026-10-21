"""Verify bundled numeric SEC snapshots; optionally rebuild them from pinned original filings."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import urllib.request
from sec_sources import BASE, PROJECTS, read, inline_facts


def verify_sources():
    count=0
    for slug in PROJECTS:
        root=BASE/slug
        for name,expected in read(root/'data/pinned_archives.json').items():
            path=root/'data/raw'/name
            assert path.exists(), f'Missing pinned source {path}; restore the repository data'
            raw=path.read_bytes();data=gzip.decompress(raw)
            assert hashlib.sha256(raw).hexdigest()==expected['archive_sha256'],f'Archive changed: {name}'
            assert hashlib.sha256(data).hexdigest()==expected['content_sha256'],f'Numeric source changed: {name}'
            value=json.loads(data)
            if expected['kind'] in ['companyfacts','submissions']:
                assert int(value['cik'])==expected['cik'],'Wrong issuer identity'
            elif expected['kind']=='inline':
                assert value['source_html_sha256']==expected['source_html_sha256']
                assert value['filed']<='2026-10-20'
                assert len({r['source_id'] for r in value['facts']})==len(value['facts']),'Duplicate inline numeric IDs'
            count+=1
    return count


def rebuild_inline(download_missing=False):
    for slug in PROJECTS:
        root=BASE/slug
        for issuer in read(root/'data/source_manifest.json'):
            for year,filing in [(2025,issuer['annual_filing_2025'])]+[(f['year'],f) for f in issuer.get('history_filings',[])]:
                source=root/'data/raw'/filing['file']
                if not source.exists():
                    if not download_missing: raise FileNotFoundError(str(source)+'; use --download-missing to fetch the original public filing')
                    req=urllib.request.Request(filing['url'],headers={'User-Agent':'Prathamesh Singh independent portfolio research github.com/Pratattack'})
                    content=urllib.request.urlopen(req,timeout=90).read()
                    assert hashlib.sha256(content).hexdigest()==filing['html_sha256'],'Original filing bytes changed; stop and review, do not repin'
                    source.write_bytes(gzip.compress(content,mtime=0))
                content=gzip.decompress(source.read_bytes())
                assert hashlib.sha256(content).hexdigest()==filing['html_sha256']
                value=inline_facts(content)
                value.update(source_url=filing['url'],source_html_sha256=filing['html_sha256'],accession=filing['accn'],filed=filing['filed'])
                destination=root/'data/raw'/f"{issuer['ticker']}-{year}-inline.json.gz"
                if destination.exists():
                    assert value==read(destination),'Parsed observations differ from the frozen numeric source; stop and review'
                else:
                    pin=read(root/'data/pinned_archives.json')[destination.name]
                    numeric_data=json.dumps(value,ensure_ascii=True,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
                    assert hashlib.sha256(numeric_data).hexdigest()==pin['content_sha256'],'Rebuilt numeric observations differ from the pinned source'
                    archive=gzip.compress(numeric_data,mtime=0)
                    assert hashlib.sha256(archive).hexdigest()==pin['archive_sha256'],'Archive encoding differs; restore the bundled exact snapshot'
                    destination.write_bytes(archive)
                print(issuer['ticker'],year,'original filing and all parsed numeric facts reconcile',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--rebuild-inline',action='store_true')
    parser.add_argument('--download-missing',action='store_true')
    args=parser.parse_args()
    if args.download_missing:
        for slug in PROJECTS:
            root=BASE/slug
            for name,pin in read(root/'data/pinned_archives.json').items():
                target=root/'data/raw'/name
                if target.exists() or pin['kind']=='inline':continue
                request=urllib.request.Request(pin['source_url'],headers={'User-Agent':'Prathamesh Singh independent portfolio research github.com/Pratattack'})
                data=urllib.request.urlopen(request,timeout=90).read()
                assert hashlib.sha256(data).hexdigest()==pin['content_sha256'],'Live API vintage changed; retain the bundled snapshot instead of silently replacing it'
                archive=gzip.compress(data,mtime=0)
                assert hashlib.sha256(archive).hexdigest()==pin['archive_sha256'],'Archive encoding differs; use the bundled exact snapshot'
                target.write_bytes(archive)
    if args.rebuild_inline:rebuild_inline(args.download_missing)
    print(verify_sources(),'pinned numeric archives verified')
