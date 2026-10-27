"""Independently re-read selected high-value numbers from archived source HTML.

Exact table-cell comparisons are stronger than loose text searches. For prose
pages, an exact numeric token only checks transcription, not statistical scope.
"""
from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"

def records(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))

manifest = {r["source_id"]: r for r in records(DATA / "source_snapshot_manifest.csv")}
observations = records(DATA / "observations_reviewed.csv")
pages = {}
for sid, row in manifest.items():
    if not row["path"]:
        continue
    path = ROOT / row["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"], sid
    pages[sid] = BeautifulSoup(path.read_bytes(), "html.parser")

def compact(value):
    return re.sub(r"[\s,，\u2002\u3000\xa0]+", "", str(value))

def equivalent(a, b):
    try:
        return abs(float(compact(a)) - float(compact(b))) < 1e-8
    except ValueError:
        return False

table_rows = {}
for sid in ("S05", "S06"):
    found = {}
    for tr in pages[sid].find_all("tr"):
        cells = [compact(x.get_text(" ", strip=True)) for x in tr.find_all(["td", "th"]) ]
        if len(cells) == 4:
            found[cells[0]] = cells
    table_rows[sid] = found

audit = []
for row in observations:
    sid = row["source_id"]
    outcome = "not_independently_checked"
    locator = ""
    observed_source_value = ""
    if sid not in pages:
        outcome = "snapshot_unavailable"
    elif sid in table_rows and row["indicator_id"] in {"resident_population_year_end", "urbanization_rate"}:
        cells = table_rows[sid].get(row["region_name"])
        if cells:
            column = 1 if row["indicator_id"] == "resident_population_year_end" else 3
            observed_source_value = cells[column]
            expected = float(row["value"]) / 10000 if column == 1 else float(row["value"])
            outcome = "table_cell_match" if equivalent(observed_source_value, expected) else "MISMATCH"
            locator = f"HTML table / {row['region_name']} / column {column + 1}"
    elif sid in {"S02", "S03", "S04", "S07", "S01", "S09", "S10", "S11"}:
        # Only check direct source numbers. Derived quantities need a separate formula audit.
        if sid == "S01" and row["year"] == "2024":
            outcome = "derived_not_literal"
        else:
            numeric = float(row["value"])
            candidate_values = [row["value"]]
            if row["unit"] == "人" and abs(numeric) >= 10000:
                candidate_values += [f"{numeric / 10000:g}", f"{numeric / 10000:.2f}"]
            if sid == "S07" and row["indicator_id"] == "gdp":
                candidate_values.append(str(round(numeric * 10000)))
            if sid == "S01" and row["unit"] == "人":
                candidate_values += [f"{numeric / 10000:g}", f"{numeric / 1000000:g}"]
            text = compact(pages[sid].get_text(" ", strip=True))
            for candidate in candidate_values:
                token = compact(candidate).rstrip("0").rstrip(".") if "." in str(candidate) else compact(candidate)
                if token and token in text:
                    outcome = "numeric_token_present"
                    observed_source_value = candidate
                    locator = f"HTML text / character {text.find(token)}"
                    break
            else:
                outcome = "token_not_found_review_needed"
    audit.append({
        "region_code": row["region_code"], "year": row["year"],
        "indicator_id": row["indicator_id"], "population_scope": row["population_scope"],
        "source_id": sid, "registered_value": row["value"],
        "source_value_or_token": observed_source_value, "audit_result": outcome,
        "source_locator": locator, "snapshot_sha256": manifest[sid]["sha256"],
    })

path = OUT / "source_number_audit.csv"
with path.open("w", encoding="utf-8-sig", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(audit[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(audit)
from collections import Counter
counts = Counter(r["audit_result"] for r in audit)
print(dict(counts))
if counts["MISMATCH"]:
    for row in audit:
        if row["audit_result"] == "MISMATCH":
            print("MISMATCH", row)
    raise SystemExit(1)
