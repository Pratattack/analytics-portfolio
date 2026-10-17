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

def bridge(base, current):
    # Exact ordered bridge: volume, mix, price, then unit variable cost.
    q0=sum(x["quantity"] for x in base); q1=sum(x["quantity"] for x in current)
    cm0=sum(x["quantity"]*(x["price"]-x["unit_cost"]) for x in base)
    volume=(q1-q0)*cm0/q0
    mix=sum((b["quantity"]-a["quantity"]*q1/q0)*(a["price"]-a["unit_cost"]) for a,b in zip(base,current))
    price=sum(b["quantity"]*(b["price"]-a["price"]) for a,b in zip(base,current))
    cost=sum(-b["quantity"]*(b["unit_cost"]-a["unit_cost"]) for a,b in zip(base,current))
    return {"volume":volume,"mix":mix,"price":price,"cost":cost}

def contract_npv(quantity, price, cost, uplift, elasticity, churn, cost_shock, discount=.10):
    if not (0<=churn<=1 and uplift> -1 and discount> -1 and quantity>=0): raise ValueError("invalid scenario")
    volume=quantity*(1-churn)*(1+uplift)**elasticity
    margin=price*(1+uplift)-cost*(1+cost_shock)
    # Three annual flows; no terminal value, inflation or working capital modeled.
    return sum(volume*margin/(1+discount)**year for year in range(1,4))

def main():
    rng=random.Random(20261017)
    rows=[]
    for c in range(1,31):
        for product,p,cost in [("FCC",4200,2750),("Hydrotreating",9200,6600),("Renewables",11400,8200)]:
            q=rng.randint(8,80); price=round(p*rng.uniform(.86,1.12),2); unit=round(cost*rng.uniform(.94,1.07),2)
            for period,qty,pr,uc in [(0,q,price,unit),(1,round(q*rng.uniform(.78,1.24),2),round(price*rng.uniform(.98,1.07),2),round(unit*rng.uniform(1.01,1.10),2))]:
                rows.append(dict(customer=f"C{c:03}",product=product,period=period,quantity=qty,price=pr,unit_cost=uc,service_cost=round(1200+qty*rng.uniform(10,90),2)))
    write_csv("commercial_data.csv", rows)
    db=sqlite3.connect(":memory:")
    db.executescript((ROOT/"analysis.sql").read_text().split("-- ANALYSIS")[0])
    db.executemany("INSERT INTO commercial VALUES (:customer,:product,:period,:quantity,:price,:unit_cost,:service_cost)",rows)
    query=(ROOT/"analysis.sql").read_text().split("-- ANALYSIS")[1]
    cur=db.execute(query); customers=[dict(zip([x[0] for x in cur.description],r)) for r in cur]
    write_csv("customer_profitability.csv",customers)
    base=[r for r in rows if r["period"]==0]; current=[r for r in rows if r["period"]==1]
    b=bridge(base,current)
    cm=lambda rs:sum(r["quantity"]*(r["price"]-r["unit_cost"]) for r in rs)
    change=cm(current)-cm(base)
    assert abs(sum(b.values())-change)<1e-6
    scenarios=[]
    for uplift in [0,.02,.04,.06,.08]:
        for elasticity in [-.5,-1,-2]:
            for churn in [0,.03,.08]:
                for shock in [0,.05,.10]:
                    v=sum(contract_npv(r["quantity"],r["price"],r["unit_cost"],uplift,elasticity,churn,shock) for r in current)
                    scenarios.append(dict(uplift=uplift,elasticity=elasticity,churn=churn,cost_shock=shock,three_year_variable_contribution_npv=v))
    write_csv("contract_sensitivity.csv",scenarios)
    write_csv("margin_bridge.csv",[dict(driver=k,usd=v) for k,v in b.items()])
    loss=[r for r in customers if r["contribution_after_service"]<0]
    result=dict(base_variable_contribution=cm(base),current_variable_contribution=cm(current),change=change,bridge=b,bridge_residual=sum(b.values())-change,negative_customers=len(loss),scenario_count=len(scenarios))
    (OUT/"metrics.json").write_text(json.dumps(result,indent=2,sort_keys=True))
    report("Catalyst Pricing & Contract Economics",f"Variable contribution changed by ${change:,.0f} across 30 fictional customers. The bridge separates commercial drivers before customer service costs.",[
      ("Decision", "Use contract-level review before a portfolio-wide increase. Test 2%-8% price proposals against demand response, churn and cost inflation; do not interpret a hypothetical optimum as measured willingness to pay."),
      ("Margin bridge", "\n".join(f"{k.title()}: ${v:,.0f}" for k,v in b.items())+f"\nReconciliation residual: ${result['bridge_residual']:.8f}. Order matters: volume, mix, price, cost."),
      ("Customer economics",f"{len(loss)} customers have negative contribution after assigned service costs. Service costs are synthetic customer-product allocations, not audited activity-based costs. Review allocation drivers before contract action. See customer_profitability.csv."),
      ("Contract stress testing",f"{len(scenarios)} scenarios include elasticity -0.5/-1/-2, churn 0%/3%/8%, and unit-cost shocks 0%/5%/10%. Three-year NPV discounts constant annual variable contribution at 10%; excludes service costs, tax, capex and working capital."),
      ("Data & limitations","180 synthetic customer-product-period records; quantities in tonnes, prices and unit costs in USD/tonne. Periods are two illustrative annual snapshots. No causal price elasticity is estimated. Product quality, capacity constraints and negotiation dynamics require real validation."),
      ("Personal understanding","I can explain whether margin changed because we sold more, changed the product/customer mix, realized different prices, or incurred higher costs. Revenue growth alone cannot establish profitable growth. I would reconcile the bridge to finance and question service-cost allocations before recommending customer action."),
      ("Sources & role alignment","Ketjen Commercial Finance Analyst description supplied by the user: pricing, margin, mix, contract economics and repeatable reporting. Context: https://www.ketjen.com/solutions/clean-fuels-technology/hydroprocessing-co-processing/ (reviewed 2026-10-17). This source informs the business setting; all numbers and scenario parameters are invented.")])
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()
