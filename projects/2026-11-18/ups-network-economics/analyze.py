"""Reconcile UPS profit and estimate the savings hurdle for a network redesign."""
from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from model_tools import csv_output, load_inputs, render_table, report

SOURCE = "https://investors.ups.com/sec-filings/all-sec-filings/content/0001628280-26-067381/exhibit991-earningspressre.htm"
ADJUSTMENTS = ("network", "other_transformation", "impairment", "asset_gain", "divestiture")


def main():
    sources, args, reconciliations = load_inputs(
        ROOT, set(ADJUSTMENTS) | {"year", "revenue", "gaap", "adjusted"})
    csv_output(ROOT, "reconciliation.csv", reconciliations)
    index = {(row["scope"], row["window"], row["year"]): row for row in sources}
    bridge = []
    for scope, window in (("consolidated", "Q3"), ("consolidated", "9M"), ("domestic", "Q3")):
        old, new = (index[scope, window, year] for year in (2025, 2026))
        delta = {name: (new[name] or 0) - (old[name] or 0) for name in ("gaap", *ADJUSTMENTS, "adjusted")}
        assert delta["gaap"] + sum(delta[name] for name in ADJUSTMENTS) == delta["adjusted"]
        bridge.append(dict(scope=scope, window=window, **delta))
    assert [(row["gaap"], row["adjusted"]) for row in bridge] == [(-60, -78), (-1351, -293), (303, 129)]
    csv_output(ROOT, "operating_bridge.csv", bridge)
    latest = index["domestic", "Q3", 2026]
    gain = bridge[2]["adjusted"]
    rate = args["quarterly_discount_rate_pct"] / 100
    ramp = args["savings_ramp"]
    assert len(ramp) == args["quarters"]
    discounts = [(1 + rate) ** (-quarter) for quarter in range(1, len(ramp) + 1)]
    savings_pv = sum(weight * discount for weight, discount in zip(ramp, discounts))
    annuity_pv = sum(discounts)
    thresholds, scenarios = [], []
    for loss, margin, initial in product(args["revenue_loss_pct"],
                                        args["incremental_contribution_pct"],
                                        args["implementation_cost_m"]):
        lost_profit = latest["revenue"] * loss * margin / 10000
        required = (initial + annuity_pv * lost_profit) / savings_pv
        assert abs(sum((required * weight - lost_profit) * discount
                       for weight, discount in zip(ramp, discounts)) - initial) < 1e-8
        base = dict(revenue_loss_pct=loss, incremental_contribution_pct=margin,
                    implementation_cost_m=initial)
        thresholds.append({**base, "quarterly_profit_loss_usd_m": round(lost_profit, 6),
                           "q3_gain_remaining_usd_m": round(gain - lost_profit, 6),
                           "required_quarterly_savings_usd_m": round(required, 6)})
        for savings in args["quarterly_savings_m"]:
            npv = savings * savings_pv - lost_profit * annuity_pv - initial
            scenarios.append({**base, "steady_quarterly_savings_usd_m": savings,
                              "illustrative_pre_tax_npv_usd_m": round(npv, 6)})
    case = args["decision_case"]
    selected = next(row for row in thresholds if all(row[k] == v for k, v in case.items()))
    required = selected["required_quarterly_savings_usd_m"]
    assert selected["quarterly_profit_loss_usd_m"] == 104.055
    assert 140 < required < 170
    csv_output(ROOT, "savings_frontier.csv", thresholds)
    csv_output(ROOT, "scenarios.csv", scenarios)
    report(ROOT, "UPS network redesign savings hurdle",
           f"At 2% domestic revenue leakage and a 35% contribution margin, an illustrative redesign needs about ${required:.0f} million of steady quarterly savings to break even.",
           [
               ("Reported profit bridge",
                render_table(["Scope", "Window", "GAAP change, USD millions",
                              "Adjusted change, USD millions"],
                             [[row["scope"], row["window"], f'{row["gaap"]:+,}', f'{row["adjusted"]:+,}']
                              for row in bridge])
                + "<p>The Q3 domestic comparison improved on both bases while consolidated adjusted operating profit fell. The bridge does not identify savings caused by the network program.</p>"),
               ("Decision thresholds", "<p>At 35% incremental contribution, a 2.48% domestic revenue decline would erase the $129 million year-over-year Q3 adjusted improvement. The investment hurdle instead compares incremental cash flow with holding the latest network unchanged. It assumes $150 million of upfront cash cost and a four-quarter ramp.</p>"
                + render_table(["Revenue loss", "Savings hurdle per quarter"],
                               [[f'{row["revenue_loss_pct"]}%', f'${row["required_quarterly_savings_usd_m"]:.1f}m']
                                for row in thresholds if row["implementation_cost_m"] == 150
                                and row["incremental_contribution_pct"] == 35])),
               ("Stage the decision", "<p>Start with a limited lane pilot, verify service and contribution on affected accounts, and include stranded cost and incremental capex in the cash case. Advance only if measured net savings clear the hurdle under a credible leakage stress. The eight-quarter screen holds the Q3 revenue base flat and excludes taxes, working capital, seasonality and terminal value. The cash cost is an assumption separate from UPS’s reported accounting charges.</p>"),
           ], SOURCE)


if __name__ == "__main__":
    main()
