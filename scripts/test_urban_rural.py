"""Independent checks on the Ganzhou 18-county urban/rural derived estimates."""
from pathlib import Path
from decimal import Decimal
import csv
import json

ROOT=Path(__file__).resolve().parent.parent
def load(name):
    with (ROOT/"outputs"/name).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))
base=load("ganzhou_population_2024_2025.csv")
derived=load("ganzhou_urban_rural_derived.csv")
summary=json.loads((ROOT/"outputs/ganzhou_urban_rural_summary.json").read_text(encoding="utf-8"))
assert len(base)==len(derived)==18
assert len({r["region_code"] for r in derived})==18
assert {r["region_code"] for r in base}=={r["region_code"] for r in derived}
by_code={r["region_code"]:r for r in base}
pop_delta=urban_delta=rural_delta=Decimal(0)
for row in derived:
    orig=by_code[row["region_code"]]
    p0,p1=(Decimal(orig[f"pop_{y}"]) for y in ("2024","2025"))
    q0,q1=(Decimal(orig[f"urbanization_{y}"]) for y in ("2024","2025"))
    a,b=(Decimal(row[k]) for k in ("urban_2024_proxy","urban_2025_proxy"))
    c,d=(Decimal(row[k]) for k in ("rural_2024_proxy","rural_2025_proxy"))
    assert a+c==p0 and b+d==p1
    assert a==p0*q0/100 and b==p1*q1/100
    assert Decimal(row["urban_delta_proxy"])==b-a
    assert Decimal(row["rural_delta_proxy"])==d-c
    assert Decimal(row["population_delta"])==p1-p0
    # Rounding-bound validation independent of generator.
    bound=Decimal(row["urban_delta_rounding_bound"])
    assert (b-a)>bound and (d-c)<-bound
    assert row["urban_gain_robust"]=="true" and row["rural_decline_robust"]=="true"
    pop_delta += p1-p0
    urban_delta += b-a
    rural_delta += d-c
assert (pop_delta,urban_delta,rural_delta)==(Decimal("-11000"),Decimal("113552.13"),Decimal("-124552.13"))
assert int(summary["population_delta"]) == int(pop_delta)
assert Decimal(str(summary["urban_delta_proxy"])) == urban_delta
assert Decimal(str(summary["rural_delta_proxy"])) == rural_delta
assert summary["urban_gain_robust_count"]==18
assert summary["rural_decline_robust_count"]==18
print("PASS: 18 counties, per-county identities, rounding robustness, and 2024/25 population totals")
