import csv, json, random, math, statistics, sqlite3, html
from pathlib import Path
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
def write_csv(name, rows):
    rows = list(rows)
    with (OUT/name).open("w", newline="") as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def report(title, summary, sections):
    text = f"# {title}\n\nSYNTHETIC PORTFOLIO CASE | USD | 2026-10-17\n\n{summary}\n\n"
    for heading, body in sections:
        text += f"## {heading}\n\n{body}\n\n"
    (OUT/"decision_memo.md").write_text(text)
    blocks = "".join(f"<section><h2>{html.escape(h)}</h2><p>{html.escape(b)}</p></section>" for h,b in sections)
    (OUT/"report.html").write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>body{{font:17px/1.6 system-ui;background:#eef2f6;color:#172c42;margin:0}}main{{max-width:960px;margin:auto;padding:40px 24px}}header,section{{background:white;padding:26px;border-radius:12px;margin:18px 0}}small{{color:#52657a}}h1{{line-height:1.2}}h2{{color:#006b70}}p{{white-space:pre-wrap}}</style><main><header><small>SYNTHETIC PORTFOLIO CASE · 17 OCT 2026 · USD</small><h1>{html.escape(title)}</h1><p>{html.escape(summary)}</p></header>{blocks}<footer>No employer data, endorsement, or actual commercial results.</footer></main></html>')

def npv(balance, spend, apr, pd, lgd, cac, retention=.88, funding=.055, discount=.12, years=3):
    if not(0<=pd<=1 and 0<=lgd<=1 and 0<=retention<=1 and balance>=0 and spend>=0 and cac>=0 and discount>-1): raise ValueError("invalid economics")
    # Static annual performing exposure approximation. Retention includes every exit.
    annual=balance*(apr-funding)-balance*pd*lgd+spend*(.018-.012)-48
    return -cac+sum(annual*retention**(y-1)/(1+discount)**y for y in range(1,years+1))

def experiment(rows):
    groups=[[r["converted"] for r in rows if r["arm"]==a] for a in [0,1]]
    rates=[statistics.mean(g) for g in groups]
    delta=rates[1]-rates[0]
    se=math.sqrt(sum(p*(1-p)/len(g) for p,g in zip(rates,groups)))
    return dict(control_rate=rates[0],treatment_rate=rates[1],absolute_lift=delta,ci_low=delta-1.96*se,ci_high=delta+1.96*se,control_n=len(groups[0]),treatment_n=len(groups[1]))

def main():
    rng=random.Random(61017); rows=[]
    segments={"Prime":(.022,3000,15000,.22,140),"Near-prime":(.065,2200,10500,.25,180),"Revolver":(.10,4200,9000,.27,210)}
    for i in range(12000):
        seg=rng.choices(list(segments),[.5,.3,.2])[0]; arm=rng.randrange(2)
        prob={"Prime":.11,"Near-prime":.09,"Revolver":.07}[seg]+arm*.014
        rows.append(dict(prospect_id=i,segment=seg,arm=arm,converted=int(rng.random()<prob)))
    write_csv("randomized_campaign.csv",rows)
    db=sqlite3.connect(":memory:"); db.execute("create table campaign(prospect_id integer primary key, segment text, arm integer check(arm in (0,1)), converted integer check(converted in (0,1)))")
    db.executemany("insert into campaign values (:prospect_id,:segment,:arm,:converted)",rows)
    cur=db.execute((ROOT/"analysis.sql").read_text()); sql=[dict(zip([c[0] for c in cur.description],r)) for r in cur]
    write_csv("campaign_summary.csv",sql)
    e=experiment(rows)
    economics=[]
    for seg,(pd,balance,spend,apr,cac) in segments.items():
        for arm in [0,1]:
            # Treatment has an incremental $70 acquisition incentive per acquired account.
            g=[r for r in rows if r["segment"]==seg and r["arm"]==arm]
            rate=statistics.mean(r["converted"] for r in g)
            value=npv(balance,spend,apr,pd,.85,cac+70*arm)
            economics.append(dict(segment=seg,arm=arm,prospects=len(g),conversion=rate,account_npv=value,npv_per_prospect=rate*value))
    write_csv("segment_economics.csv",economics)
    sensitivity=[]
    for seg,(pd,balance,spend,apr,cac) in segments.items():
        for loss_mult in [1,1.5,2]:
            for funding in [.04,.055,.075]:
                for retention in [.75,.88,.95]:
                    sensitivity.append(dict(segment=seg,pd_multiplier=loss_mult,funding=funding,retention=retention,account_npv=npv(balance,spend,apr,min(pd*loss_mult,1),.85,cac,retention,funding)))
    write_csv("risk_sensitivity.csv",sensitivity)
    values={a:sum(r["prospects"]*r["npv_per_prospect"] for r in economics if r["arm"]==a)/sum(r["prospects"] for r in economics if r["arm"]==a) for a in [0,1]}
    # Stratified bootstrap holds segment weights fixed for modeled NPV per prospect.
    weights={s:sum(r["segment"]==s for r in rows)/len(rows) for s in segments}
    strata={(s,a):[r["converted"] for r in rows if r["segment"]==s and r["arm"]==a] for s in segments for a in [0,1]}
    # Binomial parametric bootstrap of conversions conditional on observed strata rates.
    boot=[]
    for _ in range(400):
        arms={0:0,1:0}
        for econ in economics:
            s,a=econ["segment"],econ["arm"]; g=strata[s,a]; p=econ["conversion"]
            rate=sum(rng.random()<p for __ in g)/len(g)
            arms[a]+=weights[s]*rate*econ["account_npv"]
        boot.append(arms[1]-arms[0])
    boot.sort(); interval=[boot[9],boot[389]]
    standardized={a:sum(weights[r["segment"]]*r["npv_per_prospect"] for r in economics if r["arm"]==a) for a in [0,1]}
    delta=standardized[1]-standardized[0]
    result=dict(experiment=e,raw_npv_per_prospect=values,standardized_npv_per_prospect=standardized,incremental_npv_per_prospect=delta,conditional_bootstrap_95_interval=interval,bootstrap_draws=400,scenario_count=len(sensitivity))
    (OUT/"metrics.json").write_text(json.dumps(result,indent=2,sort_keys=True))
    report("Credit Card Acquisition: Growth vs Risk-Adjusted Value",f"Synthetic randomized campaign: conversion lift {e['absolute_lift']*100:.2f} percentage points; modeled incremental NPV ${delta:.2f} per prospect after standardizing segment mix.",[
      ("Decision","Do not scale an incentive based on conversion alone. "+("Advance to a measured limited rollout; " if interval[0]>0 else "Retain control pending stronger value evidence; ")+"track realized acquisition cost, vintage loss, spend, attrition and complaints before scaling. This conclusion applies only to the simulation."),
      ("Experiment",f"12,000 randomized prospects. Control {e['control_rate']:.2%}, treatment {e['treatment_rate']:.2%}. Unadjusted approximate 95% lift interval: [{e['ci_low']*100:.2f}, {e['ci_high']*100:.2f}] percentage points. Assignment occurs before conversion; intention-to-treat conversion includes all prospects."),
      ("Economics",f"Three-year acquired-account NPV combines interest, funding, net interchange/rewards, expected loss, servicing and acquisition cost. Treatment adds $70 per acquired account. Standardized modeled value difference ${delta:.2f}/prospect; conditional 95% parametric bootstrap interval [${interval[0]:.2f}, ${interval[1]:.2f}]. Uncertainty covers conversions only, conditional on assumed economics; not full business uncertainty."),
      ("Stress & measurement plan","81 segment scenarios vary PD by 1x/1.5x/2x, funding 4%/5.5%/7.5%, and annual retention 75%/88%/95%. Pre-register a fixed horizon and primary NPV/prospect metric; monitor credit-loss and complaint guardrails. Do not repeatedly peek and stop on significance. No protected characteristics enter the simulation."),
      ("Limitations","All prospects, probabilities and financial parameters are simulated. This is a static exposure approximation, not a lending decision engine or regulatory capital model. PD and LGD are assumptions, not fitted predictions. No revenue recognized on defaulted balances is modeled explicitly. Real rollout requires seasoned vintages, compliance review and credit/finance validation."),
      ("Personal understanding","I can explain why an offer that converts more prospects may still destroy value: additional incentives and expected losses can exceed the extra contribution. Randomization supports a conversion comparison within this simulation, while the profit conclusion remains conditional on the financial assumptions. I would separate observed outcomes from modeled lifetime value in an interview."),
      ("Sources & role alignment","Wells Fargo Business Analyst description supplied by the user: economic models, acquisition, P&L, test plans and post-launch measurement. Context: https://www.federalreserve.gov/Releases/G19/Current/default.htm (reviewed 2026-10-17). No Federal Reserve figures are ingested or used to calibrate assumptions; context only.")])
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()
