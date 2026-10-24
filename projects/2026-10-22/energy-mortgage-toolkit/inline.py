"""Inline-XBRL numerical snapshot extraction, retaining dimensions, units and document position."""

from lxml import html
import re
from decimal import Decimal


def parse(b):
    tree = html.fromstring(b)
    ctx = {}
    units = {}
    for e in tree.iter():
        t = str(e.tag).lower()
        if t.endswith(":unit"):
            units[e.get("id")] = "|".join(
                x.text or ""
                for x in e.iter()
                if str(x.tag).lower().endswith(":measure")
            )
        if t.endswith(":context"):
            p = {
                str(x.tag).lower().split(":")[-1]: x.text
                for x in e.iter()
                if str(x.tag).lower().endswith((":startdate", ":enddate", ":instant"))
            }
            dims = {
                x.get("dimension"): x.text
                for x in e.iter()
                if str(x.tag).lower().endswith(":explicitmember")
            }
            ctx[e.get("id")] = {
                "start": p.get("startdate", ""),
                "end": p.get("enddate", p.get("instant", "")),
                "dimensions": dims,
            }
    out = []
    for i, e in enumerate(tree.iter()):
        if not str(e.tag).lower().endswith(":nonfraction"):
            continue
        c = ctx.get(e.get("contextref"))
        s = e.text_content().strip().replace(",", "").replace("−", "-")
        if (
            not c
            or str(e.get("{http://www.w3.org/2001/XMLSchema-instance}nil", "")).lower()
            == "true"
        ):
            continue
        if s in ("—", "–", "-"):
            v = Decimal(0)
        elif not re.fullmatch(r"[-+]?\d+(?:\.\d+)?", s):
            continue
        else:
            v = Decimal(s)
        v *= Decimal(10) ** int(e.get("scale", "0"))
        if e.get("sign") == "-":
            v = -v
        out.append(
            {
                "tag": e.get("name"),
                "context": e.get("contextref"),
                "unit": units.get(e.get("unitref"), ""),
                "value": float(v),
                "element_index": i,
                "decimals": e.get("decimals", "INF"),
                "scale": int(e.get("scale", "0")),
                **c,
            }
        )
    return out
