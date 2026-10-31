/* DOM simulation only. Does not verify browser layout, accessibility or downloads. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=require('node:path').resolve(__dirname,'..');
const data={plans:JSON.parse(fs.readFileSync(root+'/data/plans.json')),profiles:JSON.parse(fs.readFileSync(root+'/data/scenarios.json')).profiles,sources:JSON.parse(fs.readFileSync(root+'/data/source_manifest.json'))};
const elements=new Map();
class Element{
 constructor(id){this.id=id;this.value='';this.checked=false;this.attrs={};this.events={};this.children=[];this._html='';this.textContent='';}
 set innerHTML(s){this._html=s;if(this.id==='profile-inputs'){this.children=[...s.matchAll(/id="(cycle-\d+)"[^>]+value="([^"]+)"/g)].map(m=>{const e=new Element(m[1]);e.value=m[2];elements.set(e.id,e);return e;});}}
 get innerHTML(){return this._html;}
 querySelectorAll(){return this.children;}
 setAttribute(k,v){this.attrs[k]=v;}removeAttribute(k){delete this.attrs[k];}
 addEventListener(k,f){this.events[k]=f;}
 appendChild(){}remove(){}click(){}
}
const ids=['dataset','usage','usage-slider','basis','basis-note','october','prepaid','monthly-status','ranking','curve','profile','profile-inputs','scenario-status','scenario-ranking','sources','export-monthly','export-scenario'];
for(const id of ids)elements.set(id,new Element(id));
elements.get('dataset').textContent=JSON.stringify(data);elements.get('usage').value='1000';elements.get('basis').value='normalized';elements.get('october').checked=true;elements.get('profile').value='steady';
const context=vm.createContext({document:{getElementById:id=>elements.get(id),createElement:()=>new Element('download'),body:new Element('body')},console,Blob,URL,setTimeout});
vm.runInContext(fs.readFileSync(root+'/app/model.js','utf8'),context);vm.runInContext(fs.readFileSync(root+'/app/ui.js','utf8'),context);
const run=s=>vm.runInContext(s,context);
assert.equal(run('monthlyRows.length'),4);
assert.equal(run('monthlyRows[0].provider'),'Frontier Utilities');
assert.ok(elements.get('curve').innerHTML.includes('polyline'));
elements.get('usage').value='999';elements.get('usage').events.input();assert.equal(run('monthlyRows[0].plan'),'Discount Basic 36 Wind');
elements.get('october').checked=false;elements.get('prepaid').checked=true;elements.get('prepaid').events.change();assert.equal(run('monthlyRows.length'),7);
assert.equal(run('scenarioRows.length'),5);assert.ok(!elements.get('scenario-ranking').innerHTML.includes('GoodEnergy 9'));
elements.get('profile').value='seasonal';elements.get('profile').events.change();assert.ok(elements.get('scenario-status').textContent.includes('12,000'));
assert.equal(run('scenarioRows.find(x=>x.plan==="Bill Credit Bundle 12").credit_cycles'),6);
elements.get('cycle-0').value='0';elements.get('cycle-0').events.input();assert.equal(run('scenarioRows.length'),0);assert.ok(elements.get('cycle-0').attrs['aria-invalid']);
elements.get('usage').value='NaN';elements.get('usage').events.input();assert.equal(run('monthlyRows.length'),0);assert.equal(elements.get('ranking').innerHTML,'');
console.log('10 UI behavior assertions passed in a DOM simulation. Real browser testing remains unverified.');
