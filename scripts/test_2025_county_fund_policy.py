"""Separation and arithmetic checks for 2025 county pension fund and policy tables."""
from pathlib import Path
from datetime import date
from decimal import Decimal
import csv

ROOT=Path(__file__).resolve().parent.parent
def read(path):
    with (ROOT/path).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

fund=read("data/county_social_fund_execution_2025.csv")
policy=read("data/resident_base_pension_policy_2025.csv")
coverage=read("outputs/resident_policy_coverage_100_counties_2025.csv")
regions=read("data/regions_2025.csv")

assert len(fund)==16 and len({r["region_code"] for r in fund})==4
assert len(coverage)==len(regions)*2==200
assert sum(r["prefecture"]=="赣州市" for r in coverage)==36
assert sum(r["actual_is_verified"]=="true" for r in coverage)==2
assert sum(bool(r["enforceable_city_floor_yuan"]) for r in coverage)==36
assert sum(not r["enforceable_city_floor_yuan"] and not r["actual_county_minimum_yuan"] for r in coverage)==164

groups={}
for r in fund:
    assert r["indicator"] in {"fund_income","fund_expenditure"}
    assert r["insurance_fund"] in {"机关事业单位基本养老保险","城乡居民基本养老保险"}
    assert r["year"]=="2025" and Decimal(r["value_wanyuan"])>0
    assert r["account_scope"] and r["source_id"] and r["source_url"]
    key=(r["region_code"],r["insurance_fund"],r["indicator"])
    assert key not in groups, f"duplicate budget line: {key}"
    groups[key]=Decimal(r["value_wanyuan"])
assert groups[("360222","城乡居民基本养老保险","fund_expenditure")]==Decimal(12200)
assert groups[("360429","机关事业单位基本养老保险","fund_expenditure")]==Decimal(24488)
assert groups[("360726","城乡居民基本养老保险","fund_expenditure")]==Decimal(14718)
assert groups[("360200","城乡居民基本养老保险","fund_expenditure")]==Decimal(47100)

for r in policy:
    start=date.fromisoformat(r["period_start"]);end=date.fromisoformat(r["period_end"])
    assert start<=end and start.year==end.year==2025
    assert Decimal(r["monthly_basic_min_yuan"])>0
    assert r["source_id"] and r["source_url"] and r["verification_status"]

for r in coverage:
    if r["region_code"]=="360735":
        expected=Decimal(208 if r["period_start"]=="2025-01-01" else 228)
        assert Decimal(r["actual_county_minimum_yuan"])==expected
        assert Decimal(r["county_additional_payment_yuan"])==3
    if r["prefecture"]=="赣州市":
        expected=Decimal(205 if r["period_start"]=="2025-01-01" else 225)
        assert Decimal(r["enforceable_city_floor_yuan"])==expected
        if not r["actual_is_verified"]=="true":
            assert r["actual_county_minimum_yuan"]=="", "Do not mislabel city floor as actual county benefit"
    else:
        assert not r["enforceable_city_floor_yuan"]

assert all(r["statistical_level"]=="地级市" for r in fund if r["region_code"]=="360200")
assert all("企业职工" not in r["insurance_fund"] for r in fund), "County fund reporting scope excludes nationwide-enterprise insurance"
print("PASS: 16 public pension fund observations; 200 policy-coverage cells; no missing values imputed as observed.")
