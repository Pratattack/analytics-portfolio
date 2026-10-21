"""Independent standard-library HTML parser reconciles lxml-extracted values and contexts."""
from html.parser import HTMLParser
import gzip
import hashlib
import json
import math
from sec_sources import BASE, PROJECTS, read


class IndependentFacts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.facts={};self.contexts={};self.context=None;self.field=None;self.buffer=[];self.active=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='xbrli:context':self.context=(attrs['id'],{'dimensions':{}})
        if self.context and tag in ['xbrli:identifier','xbrli:instant','xbrli:startdate','xbrli:enddate','xbrldi:explicitmember']:
            self.field=(tag,attrs.get('dimension'));self.buffer=[]
        if tag=='ix:nonfraction':self.active.append([attrs,[]])
    def handle_data(self,data):
        for active in self.active:active[1].append(data)
        if self.field is not None:self.buffer.append(data)
    def handle_endtag(self,tag):
        if self.field and self.field[0]==tag:
            content=''.join(self.buffer).strip()
            if tag=='xbrldi:explicitmember':self.context[1]['dimensions'][self.field[1]]=content
            else:self.context[1][tag.split(':')[-1]]=content
            self.field=None;self.buffer=[]
        if tag=='xbrli:context' and self.context:
            self.contexts[self.context[0]]=self.context[1];self.context=None
        if tag=='ix:nonfraction' and self.active:
            attrs,chunks=self.active.pop()
            if attrs.get('xsi:nil')=='true':return
            text=''.join(chunks).strip().replace(',','').replace('\u00a0','')
            try:
                if text in ['—','–','-']:value=0.0
                else:value=float(text.strip('()'))*(-1 if text.startswith('(') else 1)
                value*=10.0**int(attrs.get('scale','0'))
                if attrs.get('sign')=='-':value=-abs(value)
                if math.isfinite(value):self.facts[attrs['id']]=(value,attrs['contextref'],attrs.get('name'))
            except (ValueError,KeyError):pass


def audit():
    outputs=[]
    for slug in PROJECTS:
        root=BASE/slug;checks=[]
        for issuer in read(root/'data/source_manifest.json'):
            for year,filing in [(2025,issuer['annual_filing_2025'])]+[(f['year'],f) for f in issuer.get('history_filings',[])]:
                source=root/'data/raw'/filing['file']
                content=gzip.decompress(source.read_bytes());assert hashlib.sha256(content).hexdigest()==filing['html_sha256']
                parser=IndependentFacts();parser.feed(content.decode('utf-8'))
                primary=read(root/'data/raw'/f"{issuer['ticker']}-{year}-inline.json.gz")
                for row in primary['facts']:
                    value,context,concept=parser.facts[row['source_id']]
                    assert math.isclose(value,row['value'],rel_tol=1e-12,abs_tol=1e-6),(issuer['ticker'],row['source_id'])
                    assert context==row['context_id'] and concept==row['concept']
                    independent=parser.contexts[context]
                    for field in ['dimensions','identifier','instant','startdate','enddate']:
                        assert independent.get(field)==row.get(field),(issuer['ticker'],context,field)
                checks.append(dict(ticker=issuer['ticker'],filing_year=year,source_html_sha256=filing['html_sha256'],
                                   independently_reconciled_numeric_values=len(primary['facts']),source_url=filing['url'],status='PASS'))
        evidence=dict(status='PASS',parser='Python HTMLParser independent of production lxml parser',filings=checks)
        (root/'source_html_audit.json').write_text(json.dumps(evidence,indent=2)+'\n');outputs.extend(checks)
    print(json.dumps(dict(status='PASS',filings=len(outputs),numeric_values=sum(r['independently_reconciled_numeric_values'] for r in outputs))))


if __name__=='__main__':audit()
