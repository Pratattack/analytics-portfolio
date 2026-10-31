from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
data={'plans':json.loads((ROOT/'data/plans.json').read_text()),'profiles':json.loads((ROOT/'data/scenarios.json').read_text())['profiles'],'sources':json.loads((ROOT/'data/source_manifest.json').read_text())}
selected={p['source_id'] for p in data['plans']}
data['sources']=[s for s in data['sources'] if s['id'] in selected]
html=(ROOT/'app/template.html').read_text().replace('__DATA__',json.dumps(data).replace('</','<\\/')).replace('__MODEL__',(ROOT/'app/model.js').read_text()).replace('__UI__',(ROOT/'app/ui.js').read_text())
assert '__DATA__' not in html and '__MODEL__' not in html and '__UI__' not in html
(ROOT/'app/index.html').write_text(html)
print('Built self-contained app/index.html')
