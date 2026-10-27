"""Offline evidence audit acceptance checks; no network access or fixed observation counts."""
from collections import Counter
from pathlib import Path
import csv
import hashlib

from openpyxl import load_workbook

root = Path(__file__).resolve().parent.parent

def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))

sources = read(root / "data/sources.csv")
manifest = read(root / "data/source_snapshot_manifest.csv")
facts = read(root / "data/observations_reviewed.csv")
audit = read(root / "outputs/source_number_audit.csv")
source_ids = {r["source_id"] for r in sources}
manifest_by_source = {r["source_id"]: r for r in manifest}

assert source_ids, "no registered sources"
assert len(source_ids) == len(sources) == len(manifest_by_source) == len(manifest), "duplicate/missing source IDs"
assert source_ids == set(manifest_by_source), "manifest/source registry mismatch"
assert facts and len(facts) == len(audit), "every observation must have an audit record"

for entry in manifest:
    if entry["path"]:
        filepath = (root / entry["path"]).resolve()
        assert filepath.is_relative_to(root.resolve()), "archived path escapes repository"
        assert filepath.is_file(), "missing archived snapshot"
        actual_hash = hashlib.sha256(filepath.read_bytes()).hexdigest()
        assert actual_hash == entry["sha256"], "archived snapshot hash mismatch"
        assert int(entry["bytes"]) == filepath.stat().st_size, "snapshot size mismatch"
    else:
        assert not entry["sha256"], "hash must not exist without snapshot"

def fact_key(row):
    return (row["region_code"], row["year"], row["indicator_id"],
            row["population_scope"], row["source_id"])

by_fact = {fact_key(r): r for r in facts}
by_audit = {fact_key(r): r for r in audit}
assert len(by_fact) == len(facts), "duplicate fact version"
assert len(by_audit) == len(audit), "duplicate audit version"
assert set(by_fact) == set(by_audit), "not every fact has the same audit coverage"
outcomes = Counter()
for key, checked in by_audit.items():
    fact = by_fact[key]
    sid = fact["source_id"]
    assert sid in source_ids, "orphan fact with unknown source"
    outcome = checked["audit_result"]
    assert outcome in {
        "table_cell_match", "numeric_token_present", "derived_not_literal",
        "snapshot_unavailable", "token_not_found_review_needed", "not_independently_checked",
    }, f"unsupported or failed audit outcome: {outcome}"
    assert checked["registered_value"] == fact["value"], f"audited value drift: {key}"
    assert checked["snapshot_sha256"] == manifest_by_source[sid]["sha256"], "evidence version drift"
    if outcome == "table_cell_match":
        assert sid in {"S05","S06"}, "unexpected table parser without manual review"
        assert checked["source_locator"], "table-cell evidence has no locator"
    if outcome == "snapshot_unavailable":
        assert not manifest_by_source[sid]["path"], "unavailable status on archived source"
    if outcome == "numeric_token_present":
        # Token occurrence only checks transcription; it does NOT validate statistical semantics.
        assert checked["source_locator"], "numeric-token audit must include a locator"
    outcomes[outcome] += 1

eligible_cells = [
    r for r in facts
    if r["source_id"] in {"S05", "S06"}
    and r["indicator_id"] in {"resident_population_year_end", "urbanization_rate"}
]
assert eligible_cells, "the baseline Ganzhou two-year source tables must remain present"
assert all(by_audit[fact_key(r)]["audit_result"] == "table_cell_match" for r in eligible_cells), (
    "some of the official Ganzhou county population cells were not verified"
)
wb = load_workbook(root / "outputs/江西县域社会保障_2025可复现审计工作簿.xlsx", read_only=True)
assert "事实142条" in wb.sheetnames, "workbook sheet name must match current artifact contract"
assert wb["事实142条"].max_row == len(facts) + 1
assert wb["逐条来源审计"].max_row == len(audit) + 1
assert wb["行政区100"].max_row == len(read(root / "data/regions_2025.csv")) + 1
assert wb["峡江养老金复算"]["G5"].value.startswith("=")
print(f"PASS: {len(facts)} facts; {len(sources)} sources; {len(eligible_cells)} exact government table cells; statuses={dict(outcomes)}")
