"""Validate manually curated source observations, without mutating or regenerating them.

The CSV files under data/ are the canonical version-controlled transcriptions.
Earlier versions of this project embedded observations in Python and rewrote the
CSV on every run; that was unsafe for later manual evidence corrections.
Run: python -S scripts/prepare_data.py
"""
from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

def records(name: str) -> list[dict[str, str]]:
    path = DATA / name
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"empty data table: {name}")
    return rows

regions = records("regions_2025.csv")
sources = records("sources.csv")
facts = records("observations_reviewed.csv")
region_codes = {r["region_code"] for r in regions}
source_ids = {r["source_id"] for r in sources}

assert len(regions) == len(region_codes) == 100, "county roster must contain 100 distinct administrative regions"
assert len(sources) == len(source_ids), "duplicate source ID"
assert all(c.isdigit() and len(c) == 6 for c in region_codes)
assert all(r["publisher"] and r["url"] for r in sources), "source without publisher or URL"

seen = set()
for idx, fact in enumerate(facts, 2):
    sid, code, year, indicator = (fact[k] for k in ("source_id", "region_code", "year", "indicator_id"))
    if sid not in source_ids:
        raise ValueError(f"line {idx}: unknown source_id={sid}")
    if code not in region_codes and code != "360000":
        raise ValueError(f"line {idx}: unknown region_code={code}")
    if not year.isdigit() or not (2000 <= int(year) <= 2100):
        raise ValueError(f"line {idx}: invalid observation year")
    if not indicator or not fact["unit"] or not fact["population_scope"]:
        # A blank population_scope is legal for some total-fund indicators;
        # require explicit field presence, not arbitrary nonblank population.
        if not indicator or not fact["unit"]:
            raise ValueError(f"line {idx}: missing indicator or unit")
    try:
        value = Decimal(fact["value"])
    except (InvalidOperation, KeyError) as exc:
        raise ValueError(f"line {idx}: value must be an observed numeric value") from exc
    if not value.is_finite():
        raise ValueError(f"line {idx}: nonfinite data not allowed")
    key = (code, year, indicator, fact["population_scope"], sid)
    if key in seen:
        raise ValueError(f"line {idx}: duplicate observation/version {key}")
    seen.add(key)
    status = fact["verification_status"]
    if not status or status[0] not in "ABC":
        raise ValueError(f"line {idx}: verification grade missing")
print(f"PASS: validated {len(regions)} administrative units, {len(sources)} source records and {len(facts)} curated observations; no files rewritten")
