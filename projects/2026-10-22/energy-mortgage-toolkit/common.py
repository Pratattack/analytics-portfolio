from pathlib import Path
import csv, json, hashlib


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rounded(value):
    # Published derived results use 12 significant digits, below floating-point/BLAS noise.
    # Pinned source snapshots retain original numeric strings/precision.
    if isinstance(value, float):
        return float(format(value, ".12g"))
    if isinstance(value, dict):
        return {k: rounded(v) for k, v in value.items()}
    if isinstance(value, list):
        return [rounded(v) for v in value]
    return value


def write(p, rows, fields=None):
    p.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or list(dict.fromkeys(k for r in rows for k in r))
    with p.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rounded(rows))


def read(p):
    with p.open() as f:
        return list(csv.DictReader(f))


def dump(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(rounded(obj), indent=2, allow_nan=False) + "\n")
