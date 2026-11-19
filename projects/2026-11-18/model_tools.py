"""Small offline helpers for the two November 18 decision cases."""
import csv
import json
import sqlite3
from html import escape


def load_inputs(root, numeric_columns):
    with (root / "data/reported.csv").open(newline="") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames
        rows = [
            {key: (int(value) if value else None) if key in numeric_columns else value
             for key, value in row.items()}
            for row in reader
        ]
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE reported (" + ", ".join(columns) + ")")
        db.executemany("INSERT INTO reported VALUES (" + ", ".join("?" for _ in columns) + ")",
                       (list(row.values()) for row in rows))
        query = db.execute((root / "reconcile.sql").read_text())
        names = [column[0] for column in query.description]
        checks = [dict(zip(names, result)) for result in query]
    if not checks or any(value != 0 for row in checks for key, value in row.items()
                         if key.endswith("_residual")):
        raise ValueError("Reported financial statements do not reconcile")
    return rows, json.loads((root / "data/scenarios.json").read_text()), checks


def csv_output(root, filename, rows):
    with (root / "outputs" / filename).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def render_table(headers, rows):
    def cells(values, tag):
        return "".join(f"<{tag}>{escape(str(value))}</{tag}>" for value in values)

    body = "".join(f"<tr>{cells(row, 'td')}</tr>" for row in rows)
    return (f'<div class="table"><table><thead><tr>{cells(headers, "th")}</tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


def report(root, title, intro, sections, source_url):
    body = "".join(f"<section><h2>{escape(heading)}</h2>{content}</section>"
                   for heading, content in sections)
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title>
<style>
  *{{box-sizing:border-box}}body{{margin:0;background:#f2f2ed;color:#172b2e;font:1rem/1.55 system-ui,sans-serif}}
  main{{max-width:62rem;margin:auto;padding:clamp(1.25rem,5vw,4.25rem)}}h1{{font-size:clamp(2.1rem,5.6vw,4.2rem);
  line-height:1.04;letter-spacing:-.035em;margin:.3em 0}}h2{{font-size:1.3rem}}section{{border-top:1px solid #a4ada3;
  margin-top:1.8rem;padding-top:.65rem}}.intro{{font-size:1.15rem;max-width:43rem}}.table{{overflow-x:auto}}
  table{{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}}td,th{{text-align:left;padding:.7rem .5rem;
  border-bottom:1px solid #adb8af}}th{{background:#dfe8df}}a{{color:#005450}}footer{{padding-top:2rem}}
</style></head>
<body><main><h1>{escape(title)}</h1><p class="intro">{escape(intro)}</p>{body}
<footer><a href="{escape(source_url, quote=True)}">Company financial disclosure</a></footer></main></body></html>
"""
    (root / "outputs/report.html").write_text(document)
