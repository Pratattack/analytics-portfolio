from pathlib import Path
from lxml import etree
import json,re,csv
ROOT=Path(__file__).resolve().parents[1]

def parse(path):
    root=etree.HTML(path.read_bytes());contexts={}
    for e in root.iter():
        if e.tag.endswith(':context'):
            d={'dimensions':[]}
            for c in e.iter():
                tag=c.tag.split(':')[-1]
                if tag in ['instant','startdate','enddate']:d[tag]=''.join(c.itertext()).strip()
                if tag in ['explicitmember','typedmember']:d['dimensions'].append([c.get('dimension'),''.join(c.itertext()).strip()])
            contexts[e.get('id')]=d
    facts=[]
    for e in root.iter():
        if not e.tag.endswith(':nonfraction'):continue
        text=''.join(e.itertext()).strip();clean=text.replace(',','').replace('$','').replace('(','').replace(')','').replace('\u2212','-')
        if clean in ['—','–','-','']:v=0
        else:
            try:v=float(clean)
            except ValueError:continue
        v*=10**int(e.get('scale','0'))
        if e.get('sign')=='-':v=-abs(v)
        facts.append({'source_id':path.stem,'name':e.get('name'),'context':e.get('contextref'),'unit':e.get('unitref'),'value':v,'display':text,**contexts.get(e.get('contextref'),{})})
    return facts

def main():
    facts=[]
    for p in sorted((ROOT/'data/raw').glob('*.html')):facts.extend(parse(p))
    (ROOT/'data/filing_facts.json').write_text(json.dumps(facts,indent=2)+'\n')
    print('Parsed',len(facts),'numeric filing facts')

if __name__=='__main__':main()
