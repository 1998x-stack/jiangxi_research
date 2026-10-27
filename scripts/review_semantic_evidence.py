"""Second-stage contextual evidence audit for numeric-token hits.

All 65 historical "numeric_token_present" cases are re-examined with the local
snapshot SHA-256, a bounded numeric token, indicator-specific lexical context,
and (for pensions) nearest insurance-system scope marker. This is an AUTOMATED
candidate check, NOT a human semantic signoff or government original for B sources.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter
from bs4 import BeautifulSoup
import csv
import hashlib
import re
import unicodedata

ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/"data"
OUT=ROOT/"outputs"

def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))
audit=read(OUT/"source_number_audit.csv")
facts=read(DATA/"observations_reviewed.csv")
manifest={r["source_id"]:r for r in read(DATA/"source_snapshot_manifest.csv")}
key=lambda r:(r["region_code"],r["year"],r["indicator_id"],r["population_scope"],r["source_id"])
facts_by_key={key(r):r for r in facts}
assert len(facts_by_key)==len(facts)
LEXICAL={
    "births":["出生","出生人口"],"deaths":["死亡","死亡人口"],
    "gdp":["生产总值","GDP"],"new_urban_jobs":["新增城镇就业","城镇新增就业"],
    "resident_population_year_end":["常住人口"],"urban_resident_population":["城镇常住人口","城镇人口"],
    "hukou_population":["户籍人口"],"hukou_age_60plus":["60岁及以上","60周岁及以上"],
    "urban_income":["城镇居民","可支配收入"],"rural_income":["农村居民","可支配收入"],
    "general_public_budget_income":["一般公共预算收入"],
    "general_public_budget_expenditure":["一般公共预算支出"],
    "urban_nonprivate_avg_wage":["非私营单位","平均工资"],
    "urban_private_avg_wage":["私营单位","平均工资"],
    "pension_employee_enrolled":["职工基本养老保险","参加"],
    "pension_resident_enrolled":["城乡居民基本养老保险","参保"],
}
PENSION_CUES={
    "recipients_year_end":["退休人数","离退休人员","待遇领取人数","领取待遇人数"],
    "annual_paid":["发放养老金","共发放养老金","发放待遇","养老金待遇"],
    "active_or_paid":["在职参保人数","在职参保","已缴费人数","实际缴费"],
    "contribution":["征缴基金","征缴","保险费收入"],
}
GROUP_CUES={
    "enterprise":["城镇企业职工","企业职工养老","企业退休"],
    "public":["机关事业单位养老","机关事业单位退休","机关事业"],
    "resident":["城乡居民养老","城乡居民基本养老"],
}

def lexical(ind):
    if ind.startswith("social_insurance_"):
        return ["社会保险基金","社保基金"]
    if ind.startswith("pension_"):
        return PENSION_CUES.get(ind.rsplit("_",2)[-1], [])
    return LEXICAL.get(ind, [])

def normalize(txt):
    txt=unicodedata.normalize("NFKC",txt)
    return re.sub(r"[\s,，\u00a0]+","",txt)

def boundaries_for_num(token):
    return re.compile(r"(?<![\d.])"+re.escape(token)+r"(?![\d.])")

pages={}
for sid,r in manifest.items():
    if not r["path"]:
        continue
    b=(ROOT/r["path"]).read_bytes()
    assert hashlib.sha256(b).hexdigest()==r["sha256"]
    soup=BeautifulSoup(b,"html.parser")
    for tag in soup(["script","style","noscript"]):
        tag.decompose()
    pages[sid]=normalize(soup.get_text(" ",strip=True))

out=[]
for record in audit:
    if record["audit_result"]!="numeric_token_present":
        continue
    f=facts_by_key[key(record)]
    sid=f["source_id"]
    text=pages.get(sid,"")
    token=normalize(record["source_value_or_token"])
    regex=boundaries_for_num(token) if token else None
    matches=list(regex.finditer(text)) if regex else []
    ind=f["indicator_id"]
    kind=lexical(ind)
    candidate=None
    best_score=-1
    for m in matches:
        before=text[max(0,m.start()-170):m.start()]
        after=text[m.end():m.end()+65]
        near=before[-80:]+after[:30]
        near_cue=next((cue for cue in kind if normalize(cue) in near), "")
        broad_cue=next((cue for cue in kind if normalize(cue) in before[-170:]+after[:65]),"")
        group=""
        if ind.startswith("pension_"):
            group_name=ind.split("_")[1]
            markers=[]
            for g,options in GROUP_CUES.items():
                for cue in options:
                    pos=before.rfind(normalize(cue))
                    if pos>=0:
                        markers.append((pos,g,cue))
            if markers:
                _,found_g,group=sorted(markers)[-1]
                if found_g!=group_name:
                    group=""
        score=3*bool(near_cue)+bool(broad_cue)+bool(group)
        if score>best_score:
            best_score=score
            candidate=(m, near_cue or broad_cue, group)
    label="no_bounded_numeric_match"
    cue=""
    group=""
    position=""
    if candidate:
        match,cue,group=candidate
        position=str(match.start())
        if cue:
            if ind.startswith("pension_") and not group:
                label="lexical_candidate_group_not_bound"
            else:
                label="anchored_context_candidate"
        else:
            label="bounded_numeric_only"
    out.append({
        "region_code":f["region_code"],"year":f["year"],
        "indicator_id":ind,"population_scope":f["population_scope"],
        "source_id":sid,"registered_value":f["value"],"unit":f["unit"],
        "source_numeric_token":token,
        "bounded_occurrences":str(len(matches)),
        "nearest_context_cue":cue,"nearest_system_cue":group,
        "snapshot_character_offset":position,
        "automated_status":label,
        "manual_semantic_signoff":"pending",
        "original_publisher_check":"pending_if_B_source" if f["verification_status"].startswith("B") else "publisher_recorded_not_manually_verified",
        "source_sha256":manifest[sid]["sha256"],
        "method_limitation":"keyword and local text proximity only; cannot establish original semantics or units independently",
    })
assert len(out)==sum(r["audit_result"]=="numeric_token_present" for r in audit)
target=OUT/"semantic_evidence_audit.csv"
with target.open("w",encoding="utf-8-sig",newline="") as stream:
    w=csv.DictWriter(stream,fieldnames=list(out[0]),lineterminator="\n")
    w.writeheader()
    w.writerows(out)
print("SECOND-STAGE CONTEXT AUDIT:",len(out),"prior numeric-only rows:",dict(Counter(x["automated_status"] for x in out)))
