"""Build a Costco membership fee retention frontier from reported FY2026 accounts."""
from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from model_tools import csv_output, load_inputs, render_table, report

SOURCE = "https://investor.costco.com/news/news-details/2026/Costco-Wholesale-Corporation-Reports-Fourth-Quarter-and-Fiscal-Year-2026-Operating-Results/"


def operating_delta(row, hike, attrition, realization, exposure, avoidable):
    effective_hike = hike * realization / 10000
    lost = attrition / 100
    merchandise_contribution = (row["net_sales"] - row["merchandise_cost"]
                                - row["sg_and_a"] * avoidable / 100)
    fee_delta = row["fees"] * ((1 - lost) * (1 + effective_hike) - 1)
    return fee_delta - lost * exposure / 100 * merchandise_contribution


def break_even(row, hike, realization, exposure, avoidable):
    effective_hike = hike * realization / 10000
    contribution = row["net_sales"] - row["merchandise_cost"] - row["sg_and_a"] * avoidable / 100
    return 100 * row["fees"] * effective_hike / (
        row["fees"] * (1 + effective_hike) + contribution * exposure / 100)


def main():
    rows, args, checks = load_inputs(ROOT, {"net_sales", "fees", "revenue", "merchandise_cost",
                                           "sg_and_a", "operating_income"})
    previous, latest = sorted(rows, key=lambda row: row["period"])
    bridge = {
        "merchandise_gross_profit": (latest["net_sales"] - latest["merchandise_cost"]
                                     - previous["net_sales"] + previous["merchandise_cost"]),
        "membership_fee_revenue": latest["fees"] - previous["fees"],
        "sg_and_a": previous["sg_and_a"] - latest["sg_and_a"],
    }
    change = latest["operating_income"] - previous["operating_income"]
    assert sum(bridge.values()) == change == 1302
    assert bridge["membership_fee_revenue"] == 584
    csv_output(ROOT, "reconciliation.csv", checks)
    csv_output(ROOT, "operating_bridge.csv", [{"driver": k, "change_usd_m": v}
                                               for k, v in bridge.items()])
    frontier, scenarios = [], []
    for hike, realization, exposure, avoidable in product(
            args["fee_increase_pct"], args["realization_pct"],
            args["basket_exposure_pct"], args["avoidable_sga_pct"]):
        threshold = break_even(latest, hike, realization, exposure, avoidable)
        assert abs(operating_delta(latest, hike, threshold, realization, exposure, avoidable)) < 1e-8
        base = dict(fee_increase_pct=hike, realization_pct=realization,
                    basket_exposure_pct=exposure, avoidable_sga_pct=avoidable)
        frontier.append({**base, "break_even_attrition_pct": round(threshold, 6)})
        for attrition in args["attrition_pct"]:
            delta = operating_delta(latest, hike, attrition, realization, exposure, avoidable)
            scenarios.append({**base, "attrition_pct": attrition, "operating_delta_usd_m": round(delta, 6)})
    case = args["decision_case"]
    selected = next(row for row in frontier if all(row[k] == v for k, v in case.items()))
    threshold = selected["break_even_attrition_pct"]
    assert 0.7 < threshold < 0.8
    csv_output(ROOT, "frontier.csv", frontier)
    csv_output(ROOT, "scenarios.csv", scenarios)
    comparison = [[f"{k}%", f"{break_even(latest, k, 80, 100, 25):.2f}%"]
                  for k in args["fee_increase_pct"]]
    report(ROOT, "Costco membership pricing and retention",
           f"A modeled 5% fee increase breaks even at {threshold:.2f}% attrition in the reference scenario.",
           [
               ("Reported operating income bridge",
                render_table(["Driver", "FY2026 vs FY2025, USD millions"],
                             [(k.replace("_", " "), f"{v:+,}") for k, v in bridge.items()]
                             + [("Operating income change", f"{change:+,}")])
                + "<p>Membership fee revenue contributed $584 million to the accounting bridge. Membership-level profit and the historical effect of a price change are unobserved.</p>"),
               ("Price test decision", "<p>Use a controlled pilot and measure paid renewal and merchandise contribution together. The table assumes 80% fee realization, 100% basket exposure and 25% avoidable SG&amp;A.</p>"
                + render_table(["Nominal fee increase", "Break-even attrition"], comparison)),
               ("What the scenario varies", "<p>The grid varies realized price, attrition, basket exposure and expense flexibility. Churn applies to fees and to a range of merchandise contribution exposure. Inputs are stress assumptions. Public disclosures lack the cohort data needed to estimate price elasticity.</p>"),
           ], SOURCE)


if __name__ == "__main__":
    main()
