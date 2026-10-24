"""Three recorded gates; actual browser acceptance is separately executable and CI required."""

import json, subprocess, sys, tempfile, shutil, hashlib
from pathlib import Path
from config import ROOT, ARO, MORT

HERE = Path(__file__).resolve().parent


def run(script, root=HERE):
    subprocess.run([sys.executable, str(root / script)], check=True)


def fingerprints(root):
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for slug in [ARO, MORT]
        for p in sorted((root / slug / "outputs").glob("*"))
        if p.is_file()
    }


if __name__ == "__main__":
    before = fingerprints(ROOT)
    for script in ["aro.py", "mortgage.py", "presentation.py"]:
        run(script)
    after = fingerprints(ROOT)
    assert (
        before == after
    ), "Committed output drift: inspect and intentionally regenerate outputs"
    audit = json.loads((HERE / "source_audit.json").read_text())
    assert (
        audit["status"] == "PASS"
        and audit["original_sec_filings"] == 17
        and audit["hmda_rows_compared_to_full_original"] == 123445
    )
    run("test_research.py")
    with tempfile.TemporaryDirectory(prefix="finance-reproduce-") as tmp:
        dest = Path(tmp) / "projects/2026-10-22"
        dest.mkdir(parents=True)
        tool = dest / HERE.name
        shutil.copytree(
            HERE,
            tool,
            ignore=shutil.ignore_patterns(
                "__pycache__", "browser_evidence", "verification.json"
            ),
        )
        for slug in [ARO, MORT]:
            shutil.copytree(ROOT / slug / "data", dest / slug / "data")
        for script in ["aro.py", "mortgage.py", "presentation.py"]:
            run(script, tool)
        assert fingerprints(dest) == after, "Clean no-output rebuild differs"
    record = {
        "status": "PASS",
        "stage_1": {
            "input_methodology": "Pinned archive/member hashes; original HTML audit record; geography, year, row identity and independent aggregate reconciliation; SEC filing cutoff, units, dimensional scope, displayed signs, declared rounding and full-ledger closure."
        },
        "stage_2": {
            "independent_reconciliation": "Hand-worked six latest ledgers, every ledger lineage, analytical Jensen fixture, independent extreme-point enumeration vs every unique LP case, hand-weighting fixture, independently loaded SQL matched totals and count partition."
        },
        "stage_3": {
            "clean_reproduction": "Independent empty-output temporary directory rebuilt all files byte-identically. A fresh pinned environment is exercised in CI.",
            "deterministic_outputs": len(after),
            "browser": "Required separately: browser_test.cjs executes actual engines/desktop/mobile, captures screenshots, invalid/blank/missing/infeasible/empty/recovery/keyboard states and financial reconciliations. See browser_evidence/results.json and commit-specific release; this script alone does not assert browser acceptance.",
        },
        "output_sha256": after,
    }
    (HERE / "verification.json").write_text(json.dumps(record, indent=2) + "\n")
    print(
        "PASS: all three analytical/reproduction stages;",
        len(after),
        "byte-identical outputs. Browser gate separate.",
    )
