"""Independent numerical checks: enumeration vs LP, source-table hand ledgers, SQL vs matching."""

import unittest, itertools, math, json, sqlite3, csv
import numpy as np
from aro import bounds
from mortgage import source, eligible, match
from config import ROOT, ARO, MORT
from common import read


def enumerate_vertices(rate, mean, cap):
    # Algebraic two-date solutions; binding-cap solutions use two dates in one group and one in the other.
    values = []

    def add(ts, ws):
        if min(ws) < -1e-9 or sum(w for t, w in zip(ts, ws) if t <= 5) > cap + 1e-9:
            return
        assert (
            abs(sum(ws) - 1) < 1e-8
            and abs(sum(t * w for t, w in zip(ts, ws)) - mean) < 1e-7
        )
        values.append(sum(w * (1 + rate) ** t for t, w in zip(ts, ws)))

    for a in range(1, 31):
        if a == mean:
            add([a], [1.0])
        for b in range(a + 1, 31):
            w = (b - mean) / (b - a)
            add([a, b], [w, 1 - w])
    for group in [list(range(1, 6)), list(range(6, 31))]:
        other = range(6, 31) if group[0] == 1 else range(1, 6)
        s = cap if group[0] == 1 else 1 - cap
        for a, b in itertools.combinations(group, 2):
            for c in other:
                wa = (mean - (1 - s) * c - s * b) / (a - b)
                add([a, b, c], [wa, s - wa, 1 - s])
    return (min(values), max(values)) if values else None


class RetirementTests(unittest.TestCase):
    def test_all_unique_lp_cases_against_extreme_point_enumeration(self):
        for rate, mean, cap in itertools.product(
            [0.03, 0.06, 0.09], [5, 10, 15, 20], [0, 0.25, 0.5]
        ):
            z = bounds(1e9, rate, mean, cap)
            e = enumerate_vertices(rate, mean, cap)
            if e is None:
                self.assertEqual(z["status"], "infeasible assumptions")
            else:
                self.assertAlmostEqual(z["lower"] / 1e9, e[0], places=8)
                self.assertAlmostEqual(z["upper"] / 1e9, e[1], places=8)

    def test_hand_worked_jensen_and_zero_rate(self):
        z = bounds(100, 0.1, 2, 1)
        self.assertAlmostEqual(z["lower"], 121)
        self.assertAlmostEqual(z["upper"], 100 * ((28 / 29) * 1.1 + (1 / 29) * 1.1**30))
        z = bounds(700, 0, 15, 0.5)
        self.assertAlmostEqual(z["lower"], 700)
        self.assertAlmostEqual(z["upper"], 700)
        self.assertEqual(bounds(100, 0.1, 5, 0)["status"], "infeasible assumptions")

    def test_invalid_domain(self):
        for args in [
            (100, 0.21, 15, 0.5),
            (100, 0.05, 31, 0.5),
            (100, float("nan"), 15, 0.5),
            (True, 0.05, 15, 0.5),
            (100, 0.05, 15, -1),
        ]:
            with self.assertRaises(ValueError):
                bounds(*args)

    def test_independent_2025_disclosure_ledgers(self):
        # Original disclosure presentation values, USD millions except MUR USD thousands.
        hand = {
            "COP": (8215, [366, 162, -150, -259, -186, 216], 8364, 1e6),
            "EOG": (1460, [91, -75, 60, 33, 1], 1570, 1e6),
            "DVN": (807, [0, 58, -65, 55, 51], 906, 1e6),
            "FANG": (592, [50, 15, -153, 35, 3], 542, 1e6),
            "APA": (2694, [23, 0, -8, -100, 158, 113], 2880, 1e6),
            "MUR": (1008884, [57730, 20744, -12094, -70829, 8432], 1012867, 1e3),
        }
        for r in read(ROOT / ARO / "outputs/latest.csv"):
            a, flow, b, s = hand[r["ticker"]]
            self.assertEqual(a + sum(flow), b)
            self.assertEqual(float(r["opening"]), a * s)
            self.assertEqual(float(r["closing"]), b * s)
        cop = next(
            r for r in read(ROOT / ARO / "outputs/latest.csv") if r["ticker"] == "COP"
        )
        self.assertEqual(float(cop["explicit_cash_paid"]), 259e6)
        self.assertEqual(float(cop["removed_liability"]), 186e6)

    def test_lineage_reconstructs_every_ledger(self):
        lineage = read(ROOT / ARO / "outputs/source_lineage.csv")
        for r in read(ROOT / ARO / "outputs/panel.csv"):
            rr = [
                v
                for v in lineage
                if v["ticker"] == r["ticker"] and v["year"] == r["year"]
            ]
            opening = sum(
                float(v["presentation_value"]) for v in rr if v["role"] == "opening"
            )
            closing = sum(
                float(v["presentation_value"]) for v in rr if v["role"] == "closing"
            )
            flow = sum(
                float(v["presentation_value"]) for v in rr if v["role"] == "flow"
            )
            self.assertLessEqual(
                abs(opening + flow - closing), float(r["rounding_tolerance"])
            )


class MortgageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = source()
        cls.rows, cls.flow = eligible(cls.raw)

    def test_exclusion_partition(self):
        self.assertEqual(
            sum(v for k, v in self.flow.items() if k.startswith("excluded_"))
            + len(self.rows),
            len(self.raw),
        )
        self.assertEqual(len(set(r["source_row"] for r in self.rows)), len(self.rows))

    def test_hand_weighting_fixture(self):
        # Cell x: lender A 2 loans, B 4; cell y: A 6, B 2. Overlap target weights are 1/2,1/2.
        rs = []
        for lei, amount, vals in [
            ("A", 200000, [1, 3]),
            ("B", 200000, [4, 4, 4, 4]),
            ("A", 300000, [6] * 6),
            ("B", 300000, [8] * 2),
        ]:
            for v in vals:
                rs.append(
                    {
                        "lei": lei,
                        "amount": amount,
                        "ltv": 80,
                        "dti_bin": 1,
                        "county": "48201",
                        "spread": v,
                        "cost_bps": 100,
                    }
                )
        ss, detail, cells = match(rs, ["A", "B"], 2)
        self.assertEqual(len(cells), 2)
        self.assertEqual(ss[0]["matched_spread"], 4)
        self.assertEqual(ss[1]["matched_spread"], 6)
        self.assertEqual(match(rs, ["A", "B"], 3)[0], [])

    def test_sql_independently_reconciles_published_matching(self):
        lenders = read(ROOT / MORT / "outputs/lenders.csv")
        leis = [r["lei"] for r in lenders]
        detail = read(ROOT / MORT / "outputs/common_cells.csv")
        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE r(lei,cell,spread,cost)")
        con.executemany(
            "INSERT INTO r VALUES(?,?,?,?)",
            [(r["lei"], r["cell"], r["spread"], r["cost_bps"]) for r in self.rows],
        )
        con.execute("CREATE TABLE w(cell PRIMARY KEY,weight)")
        weights = {r["cell"]: float(r["target_weight"]) for r in detail}
        con.executemany("INSERT INTO w VALUES(?,?)", weights.items())
        self.assertAlmostEqual(sum(weights.values()), 1)
        q = "WITH means AS (SELECT r.lei,r.cell,AVG(spread) spread,AVG(cost) cost,COUNT(*) n FROM r JOIN w ON r.cell=w.cell GROUP BY r.lei,r.cell) SELECT lei,SUM(weight*spread),SUM(weight*cost),SUM(n) FROM means JOIN w ON means.cell=w.cell GROUP BY lei"
        got = {r[0]: r[1:] for r in con.execute(q)}
        for r in lenders:
            z = got[r["lei"]]
            self.assertAlmostEqual(z[0], float(r["matched_spread"]), places=10)
            self.assertAlmostEqual(z[1], float(r["matched_gross_cost_bps"]), places=8)
            self.assertEqual(z[2], int(r["matched_n"]))
        for r in detail:
            self.assertGreaterEqual(int(r["n"]), 10)

    def test_missing_and_domain_not_zero_imputed(self):
        from mortgage import num, dti

        self.assertIsNone(num(""))
        self.assertIsNone(num("NA"))
        self.assertIsNone(num("Exempt"))
        self.assertIsNone(num("NaN"))
        self.assertIsNone(dti(">60%"))
        self.assertEqual(dti("43"), 2)

    def test_sensitivity_lenders_frozen(self):
        ss = read(ROOT / MORT / "outputs/sensitivity.csv")
        self.assertEqual(len(ss), 30)
        self.assertEqual(len(set(r["lei"] for r in ss)), 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
