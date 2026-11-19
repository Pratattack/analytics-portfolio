"""Rebuild both projects from clean inputs and check representative cases independently."""
import csv
from decimal import Decimal as D
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent


def read_output(project, name):
    with (project / "outputs" / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def verify():
    case_names = ("costco-membership-pricing", "ups-network-economics")
    with TemporaryDirectory() as directory:
        clean = Path(directory)
        shutil.copy2(ROOT / "model_tools.py", clean)
        for name in case_names:
            original = ROOT / name
            rebuilt = clean / name
            shutil.copytree(original, rebuilt, ignore=shutil.ignore_patterns("outputs", "__pycache__"))
            (rebuilt / "outputs").mkdir()
            subprocess.run([sys.executable, "-B", str(rebuilt / "analyze.py")], check=True)
            expected = {p.name: p.read_bytes() for p in (original / "outputs").iterdir()}
            actual = {p.name: p.read_bytes() for p in (rebuilt / "outputs").iterdir()}
            assert expected == actual, name

        costco = clean / case_names[0]
        results = read_output(costco, "scenarios.csv")
        assert len(results) == 486
        assert len(read_output(costco, "frontier.csv")) == 81
        case = next(row for row in results if [D(row[key]) for key in (
            "fee_increase_pct", "realization_pct", "basket_exposure_pct",
            "avoidable_sga_pct", "attrition_pct")] == [5, 80, 100, 25, 1])
        repriced_fees = D("5907") * D(".99") * D("1.04")
        scenario_profit = (D("297247") - D("264279")) * D(".99") + repriced_fees - D("27190") * D(".9975")
        assert D(case["operating_delta_usd_m"]) == scenario_profit - D("11685")

        ups = clean / case_names[1]
        results = read_output(ups, "scenarios.csv")
        assert len(results) == 189
        assert len(read_output(ups, "savings_frontier.csv")) == 63
        case = next(row for row in results if [D(row[key]) for key in (
            "revenue_loss_pct", "incremental_contribution_pct",
            "implementation_cost_m", "steady_quarterly_savings_usd_m")] == [2, 35, 150, 100])
        cash_flows = [D(s) - D("104.055") for s in (25, 50, 75, 100, 100, 100, 100, 100)]
        value = D("0")
        for cash in reversed(cash_flows):
            value = (value + cash) / D("1.025")
        assert abs(D(case["illustrative_pre_tax_npv_usd_m"]) - (value - 150)) < D(".000001")
    print("PASS: SQL reconciliations, independent Decimal fixtures and byte-identical clean builds")


if __name__ == "__main__":
    verify()
