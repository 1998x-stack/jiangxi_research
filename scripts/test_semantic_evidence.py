"""Acceptance tests for 65 historical number-only records with explicit signoff limits."""
from pathlib import Path
import csv

ROOT=Path(__file__).resolve().parent.parent
def read(path):
    with (ROOT/path).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))
source=read("outputs/source_number_audit.csv")
sem=read("outputs/semantic_evidence_audit.csv")
original=[x for x in source if x["audit_result"]=="numeric_token_present"]
assert len(original)==len(sem), "every legacy number-only item must be dispositioned"
key=lambda r:(r["region_code"],r["year"],r["indicator_id"],r["population_scope"],r["source_id"])
assert {key(x) for x in original}=={key(x) for x in sem}
assert all(row["manual_semantic_signoff"]=="pending" for row in sem), "automation must not sign off as a human reviewer"
assert all(row["source_sha256"] for row in sem)
assert all(row["method_limitation"] for row in sem)
assert all(row["automated_status"] in {
    "anchored_context_candidate", "lexical_candidate_group_not_bound",
    "bounded_numeric_only","no_bounded_numeric_match",
} for row in sem)
assert len({key(row) for row in sem})==len(sem)
print(f"PASS: {len(sem)} numeric-token observations receive contextual audit and remain pending independent semantic signoff")
