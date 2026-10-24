"""Retain only numerical ledger cells and audited presentation signs from original ARO tables."""

from lxml import html
from pathlib import Path
import json, gzip, re, hashlib, argparse
from config import ROOT, ARO
from inline import parse

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True, type=Path)
    a = ap.parse_args()
    out = []
    for m in json.loads((ROOT / ARO / "data/source_manifest.json").read_text()):
        b = (a.cache / (m["ticker"] + "-" + m["report_end"][:4] + ".htm")).read_bytes()
        assert hashlib.sha256(b).hexdigest() == m["original_html_sha256"]
        tr = html.fromstring(b)
        nodes = list(tr.iter())
        idx = {id(e): i for i, e in enumerate(nodes)}
        fs = {f["element_index"]: f for f in parse(b)}
        tabs = []
        for tab in tr.iter("table"):
            tags = [
                e.get("name", "")
                for e in tab.iter()
                if str(e.tag).lower().endswith(":nonfraction")
            ]
            if "us-gaap:AssetRetirementObligation" in tags and any(
                "LiabilitiesSettled" in t or "LiabilitiesIncurred" in t for t in tags
            ):
                tabs.append(tab)
        if not tabs:
            for e in tr.iter():
                if (
                    e.get("name", "")
                    != "us-gaap:AssetRetirementObligationLiabilitiesSettled"
                ):
                    continue
                for anc in e.iterancestors():
                    tags = [n.get("name", "") for n in anc.iter()]
                    if (
                        "us-gaap:AssetRetirementObligation" in tags
                        and "us-gaap:AssetRetirementObligationLiabilitiesIncurred"
                        in tags
                    ):
                        tabs.append(anc)
                        break
        assert tabs, m["file"]
        tab = min(tabs, key=lambda t: len(list(t.iter())))
        cells = []
        for e in tab.iter():
            if idx[id(e)] not in fs:
                continue
            f = fs[idx[id(e)]]
            if f["dimensions"] or f["unit"].upper() != "ISO4217:USD":
                continue
            td = next((x for x in e.iterancestors() if x.tag == "td"), None)
            if td is None:
                td = next(x for x in e.iterancestors() if x.tag == "div")
            s = "".join(td.text_content().split()).replace("$", "")
            assert re.fullmatch(r"[()−\-–—0-9,.]+", s), (m["file"], s[:120])
            # Presentation sign can differ from taxonomy sign, especially credit-balance FX/revision tags.
            display = (
                -abs(f["value"])
                if s.startswith("(") or s.startswith("-")
                else abs(f["value"])
            )
            cells.append(
                {
                    **f,
                    "display_value": display,
                    "display_negative": s.startswith("(") or s.startswith("-"),
                }
            )
        out.append({**m, "table_numeric_cells": cells})
    p = ROOT / ARO / "data/ledger_sources.json"
    p.write_text(json.dumps(out, separators=(",", ":")) + "\n")
    print(
        len(out),
        "tables",
        sum(len(m["table_numeric_cells"]) for m in out),
        "original numeric ledger cells",
    )
