"""Build a deterministic 100-county primary-evidence collection queue.

This is an internal research request tracker, not evidence that official
information-disclosure applications have actually been filed or accepted.
"""
from pathlib import Path
import csv

ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/"data"
OUT=ROOT/"outputs"
def read(p):
    with p.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))
regions=read(DATA/"regions_2025.csv")
facts=read(DATA/"observations_reviewed.csv")
funds=read(DATA/"county_social_fund_execution_2025.csv")
policies=read(DATA/"resident_base_pension_policy_2025.csv")
old={(r["region_code"],r["indicator_id"]) for r in facts if r["year"]=="2025"}
fund_regions={r["region_code"] for r in funds if r["statistical_level"]=="县级"}
local_policy={r["region_code"] for r in policies if r["jurisdiction"]=="county_enacted_minimum"}
groups=("enterprise","public","resident")
rows=[]
for r in regions:
    c=r["region_code"]
    have_a=[(c,"pension_"+g+"_annual_paid") in old for g in groups]
    have_p=[(c,"pension_"+g+"_recipients_year_end") in old for g in groups]
    all_a=all(have_a)
    all_p=all(have_p)
    has_fund=c in fund_regions
    has_local=c in local_policy
    priority="P0" if all_a and not all_p else ("P1" if has_fund or has_local or all_a else "P2")
    rows.append({
        "region_code":c, "county":r["county"],"prefecture":r["prefecture"],
        "three_pension_amounts_available":str(all_a).lower(),
        "three_pension_recipients_available":str(all_p).lower(),
        "any_local_fund_execution_public":str(has_fund).lower(),
        "county_specific_base_pension_rule_confirmed":str(has_local).lower(),
        "priority":priority,
        "missing_need":"monthly pension beneficiaries (person-months); annual basic pension paid; retroactive pay by scheme; supplementary annuities separately",
        "secondary_need":"county fiscal supplement split and benefit standard by effective month; fund final account with budget code",
        "target_agencies":"县人社局/社保经办机构、县财政局；必要时通过政府信息公开法定渠道申请已存在的汇总记录",
        "submission_state":"NOT_SUBMITTED",
        "response_state":"NOT_RECEIVED",
        "method_note":"A public report absence does not establish actual data absence. No personal identifiers requested.",
    })
OUT.mkdir(exist_ok=True)
with (OUT/"county_primary_evidence_request_queue_2025.csv").open("w",encoding="utf-8-sig",newline="") as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
assert len(rows)==100 and len({r["region_code"] for r in rows})==100
print(f"Built 100-county research-only acquisition queue. Full 2025 three-fund amounts: {sum(x['three_pension_amounts_available']=='true' for x in rows)}; monthly recipients: {sum(x['three_pension_recipients_available']=='true' for x in rows)}")
