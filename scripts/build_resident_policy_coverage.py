"""Build 2025 county pension *minimum floor* coverage, never impute actual county pensions.

Only Ganzhou's 18 county-level administrative districts have verified city-wide
2025 minimum notices in the current policy dataset. Other 82 units stay missing.
Fiscal fund expenditures are not identical to pensions paid to beneficiaries.
"""
from pathlib import Path
import csv
from decimal import Decimal

ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/"data"
OUT=ROOT/"outputs"

def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

regions=read(DATA/"regions_2025.csv")
policies=read(DATA/"resident_base_pension_policy_2025.csv")
city={p["period_start"]:p for p in policies if p["region_code"]=="360700" and p["jurisdiction"]=="city_minimum"}
assert set(city)=={"2025-01-01","2025-07-01"}
local={(p["region_code"],p["period_start"]):p for p in policies if p["jurisdiction"]=="county_enacted_minimum"}
rows=[]
for region in regions:
    in_city=region["prefecture"]=="赣州市"
    for date,end in [("2025-01-01","2025-06-30"),("2025-07-01","2025-12-31")]:
        reg=region["region_code"]
        floor=city[date] if in_city else None
        specific=local.get((reg,date))
        city_amount=Decimal(floor["monthly_basic_min_yuan"]) if floor else None
        county_amount=Decimal(specific["monthly_basic_min_yuan"]) if specific else None
        assert county_amount is None or city_amount is not None and county_amount >= city_amount
        rows.append({
            "region_code":reg, "county":region["county"],"prefecture":region["prefecture"],
            "period_start":date,"period_end":end,
            "enforceable_city_floor_yuan":str(city_amount) if city_amount is not None else "",
            "verified_county_enacted_floor_yuan":str(county_amount) if county_amount is not None else "",
            "county_additional_payment_yuan":specific["local_add_over_city_yuan"] if specific else "",
            "actual_county_minimum_yuan":str(county_amount) if specific else "",
            "actual_is_verified":str(bool(specific)).lower(),
            "city_floor_source":floor["source_id"] if floor else "",
            "county_policy_source":specific["source_id"] if specific else "",
            "interpretation":"county formally documented" if specific else ("city statutory floor only; local amount UNKNOWN" if floor else "no county- or city-level 2025 policy verified"),
        })
target=OUT/"resident_policy_coverage_100_counties_2025.csv"
target.parent.mkdir(exist_ok=True)
with target.open("w",encoding="utf-8-sig",newline="") as stream:
    writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
print(f"Built {len(rows)} county-half-year rows; {sum(r['actual_is_verified']=='true' for r in rows)} independently documented county policy rows.")
