"""赣州18个行政县区：2024—2025城乡常住人口结构重建。

输入是由赣州市政府两年县区表核对的 outputs/ganzhou_population_2024_2025.csv。
城镇/乡村人数通过总人口×城镇化率重建，属于派生估算，不是官方直接公布人数。
不包括赣州经开区、蓉江新区两个功能区，故18县区总和不能当作全市数据。
"""
from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "outputs/ganzhou_population_2024_2025.csv"
OUTPUT = ROOT / "outputs/ganzhou_urban_rural_derived.csv"
SUMMARY = ROOT / "outputs/ganzhou_urban_rural_summary.json"
ONE_HUNDRED = Decimal("100")
POP_HALF_STEP = Decimal("50")  # 源表0.01万人=100人，单年四舍五入误差不超过50人
RATE_HALF_STEP = Decimal("0.005")  # 城镇化率保留0.01个百分点

def estimate(pop: Decimal, percent: Decimal) -> tuple[Decimal, Decimal]:
    urban = pop * percent / ONE_HUNDRED
    return urban, pop - urban

def urban_bound(pop: Decimal) -> Decimal:
    """最坏情形人数界：人口和比率均可能独立四舍五入。"""
    return POP_HALF_STEP + (pop + POP_HALF_STEP) * RATE_HALF_STEP / ONE_HUNDRED

def build() -> dict:
    with INPUT.open(encoding="utf-8-sig", newline="") as f:
        records = list(csv.DictReader(f))
    assert len(records) == 18, "expected 18 administrative county-level areas (not the 2 functional zones)"
    assert len({r["region_code"] for r in records}) == len(records), "duplicate county code"
    rows = []
    urban_delta = rural_delta = population_delta = Decimal(0)
    urban_total_2024 = urban_total_2025 = Decimal(0)
    rural_total_2024 = rural_total_2025 = Decimal(0)
    urban_positive = rural_negative = 0
    for r in records:
        p0, p1 = (Decimal(r[f"pop_{y}"]) for y in ("2024", "2025"))
        q0, q1 = (Decimal(r[f"urbanization_{y}"]) for y in ("2024", "2025"))
        assert p0 > 0 and p1 > 0 and 0 <= q0 <= 100 and 0 <= q1 <= 100
        u0, v0 = estimate(p0, q0)
        u1, v1 = estimate(p1, q1)
        dp, du, dv = p1-p0, u1-u0, v1-v0
        assert abs((du + dv)-dp) <= Decimal("0.000001")
        # 县级城镇变化的不确定区间；乡村变化误差亦采用保守合计界。
        conservative_bound = urban_bound(p0) + urban_bound(p1)
        urban_positive += int(du - conservative_bound > 0)
        rural_negative += int(dv + conservative_bound < 0)
        population_delta += dp
        urban_delta += du
        rural_delta += dv
        urban_total_2024 += u0
        urban_total_2025 += u1
        rural_total_2024 += v0
        rural_total_2025 += v1
        rows.append({
            "region_code": r["region_code"], "county": r["county"],
            "urban_2024_proxy": f"{u0:.2f}", "urban_2025_proxy": f"{u1:.2f}",
            "rural_2024_proxy": f"{v0:.2f}", "rural_2025_proxy": f"{v1:.2f}",
            "urban_delta_proxy": f"{du:.2f}", "rural_delta_proxy": f"{dv:.2f}",
            "population_delta": f"{dp:.0f}",
            "urban_delta_rounding_bound": f"{conservative_bound:.2f}",
            "urban_gain_robust": str(du > conservative_bound).lower(),
            "rural_decline_robust": str(dv < -conservative_bound).lower(),
            "sources": "S06_2024;S05_2025",
            "classification": "derived_from_official_table_not_observed_migration",
        })
    OUTPUT.parent.mkdir(exist_ok=True, parents=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    assert abs(urban_delta + rural_delta - population_delta) < Decimal("0.000001")
    summary = {
        "population_scope": "18 administrative counties/districts/county-level cities, excluding 2 functional zones",
        "source_ids": ["S05", "S06"],
        "official_precision_population_people": 100,
        "official_precision_urbanization_percentage_points": 0.01,
        "county_count": 18,
        "population_delta": int(population_delta),
        "urban_population_2024_proxy": float(urban_total_2024),
        "urban_population_2025_proxy": float(urban_total_2025),
        "rural_population_2024_proxy": float(rural_total_2024),
        "rural_population_2025_proxy": float(rural_total_2025),
        "urban_delta_proxy": float(urban_delta),
        "rural_delta_proxy": float(rural_delta),
        "urban_gain_robust_count": urban_positive,
        "rural_decline_robust_count": rural_negative,
        "method": "urban_population=year_end_residents*official_urbanization_rate/100; rural=total-urban",
        "caveat": "Not directly observed urban/rural headcounts or flows; reclassification and rounding possible. No city-wide estimate.",
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return summary

if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
