"""Normalize EIA reliability schedules with cell-level lineage and no imputation."""
from pathlib import Path
import csv,hashlib,json,math,sqlite3
import openpyxl
ROOT=Path(__file__).resolve().parent
FIELDS=['year','utility_id','utility_name','state','ownership','standard','saidi_all','saidi_normal','saifi_all','saifi_normal','customers','automatic','source_file','source_sheet','source_row']
def number(v):
    if v is None or (isinstance(v,str) and v.strip() in ['', '.', 'NA','N/A']):return None
    try:x=float(v)
    except (TypeError,ValueError):raise ValueError(f'Unexpected numeric value {v!r}')
    if not math.isfinite(x) or x<0:raise ValueError(f'Invalid value {v!r}')
    return x
def write_csv(path,rows,fields=None):
    rows=list(rows)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def extract():
    records=[];sources=[];state_totals=[]
    for path in sorted((ROOT/'data/raw').glob('Reliability_*.xlsx')):
        year=int(path.stem.split('_')[1]);book=openpyxl.load_workbook(path,read_only=True,data_only=True)
        sheet=book['Reliability_States'];rows=list(sheet.values)
        header=next(i for i,r in enumerate(rows) if r[0]=='Data Year')
        assert rows[header][1:5]==('Utility Number','Utility Name','State','Ownership')
        assert rows[0][5]=='IEEE Standard' and rows[0][17]=='Other Standard'
        assert rows[header][14]=='Number of Customers' and rows[header][23]=='Number of Customers'
        for idx,r in enumerate(rows[header+1:],header+2):
            if not isinstance(r[0],(int,float)):continue
            assert int(r[0])==year
            for standard,all_col,normal_col,customer_col,auto_col in [('IEEE',5,8,14,16),('Other',17,20,23,27)]:
                item=dict(year=year,utility_id=int(r[1]),utility_name=str(r[2]).strip(),state=str(r[3]).strip(),ownership=str(r[4]).strip(),standard=standard,saidi_all=number(r[all_col]),saidi_normal=number(r[normal_col]),saifi_all=number(r[all_col+1]),saifi_normal=number(r[normal_col+1]),customers=number(r[customer_col]),automatic=str(r[auto_col] or '').strip(),source_file=path.name,source_sheet=sheet.title,source_row=idx)
                records.append(item)
        if 'State Totals' in book.sheetnames:
            for r in book['State Totals'].values:
                if isinstance(r[0],(int,float)):
                    state_totals.append(dict(year=int(r[0]),state=r[1],ieee_customers=number(r[2]),ieee_saidi_all=number(r[3]),ieee_saidi_normal=number(r[6])))
        sources.append(dict(file=path.name,year=year,header_row=header+1,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size))
        book.close()
    if len(sources)!=6:raise ValueError('Expected all six source workbooks')
    keys=[(r['year'],r['utility_id'],r['state'],r['standard']) for r in records]
    if len(keys)!=len(set(keys)):raise ValueError('Duplicate utility-state-method-year key')
    write_csv(ROOT/'data/panel.csv',records,FIELDS)
    if state_totals:write_csv(ROOT/'data/published_state_totals.csv',state_totals)
    (ROOT/'data/workbook_manifest.json').write_text(json.dumps(sources,indent=2))
    return records
if __name__=='__main__':
    records=extract();print(json.dumps(dict(rows=len(records),years=sorted({r['year'] for r in records}),utility_state_keys=len({(r['utility_id'],r['state']) for r in records}),valid_normal=sum(r['saidi_normal'] is not None and (r['customers'] or 0)>0 for r in records)),indent=2))
