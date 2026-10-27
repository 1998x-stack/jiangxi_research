"""Acceptance checks for archived evidence and the reproducible workbook."""
from pathlib import Path
import csv
import hashlib

from openpyxl import load_workbook

root = Path(__file__).resolve().parent.parent
def read(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

sources = read(root / "data/sources.csv")
manifest = read(root / "data/source_snapshot_manifest.csv")
facts = read(root / "data/observations_reviewed.csv")
audit = read(root / "outputs/source_number_audit.csv")
assert len(sources) == len(manifest) == 16
assert len(facts) == len(audit) == 142
assert len({r["source_id"] for r in manifest}) == 16
assert sum(bool(r["sha256"]) for r in manifest) == 15
for row in manifest:
    if row["path"]:
        assert hashlib.sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"]
assert sum(r["audit_result"] == "table_cell_match" for r in audit) == 72
assert not any(r["audit_result"] == "MISMATCH" for r in audit)
assert sum(r["audit_result"] == "snapshot_unavailable" for r in audit) == 4
keys = [(r["region_code"], r["year"], r["indicator_id"], r["population_scope"], r["source_id"]) for r in facts]
assert len(keys) == len(set(keys)), "duplicate fact version key"
workbook = load_workbook(root / "outputs/江西县域社会保障_2025可复现审计工作簿.xlsx", read_only=True)
assert workbook["事实142条"].max_row == 143
assert workbook["逐条来源审计"].max_row == 143
assert workbook["行政区100"].max_row == 101
assert workbook["峡江养老金复算"]["G5"].value.startswith("=")
print("PASS: source hashes, 72 government table cells, audit coverage, workbook formulas")
