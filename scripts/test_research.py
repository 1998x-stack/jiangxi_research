"""重要数据验收测试；与分析代码独立的恒等式复算，不将来源真实性等同于计算正确。"""
from pathlib import Path
import csv, json, math
root=Path(__file__).resolve().parent.parent
x=json.loads((root/'outputs'/'analysis_results.json').read_text(encoding='utf-8'))
with (root/'data'/'regions_2025.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
assert len(rows)==100
assert len({r['region_code'] for r in rows})==100
assert len({r['county'] for r in rows})==100
assert len({r['prefecture'] for r in rows})==11
assert all(r['region_code'].startswith('36') for r in rows)
for year in ['2024','2025']:
 p=x[f'xiajiang_{year}'];groups=p['groups']
 assert len(groups)==3
 assert abs(sum(v['paid_share'] for v in groups)-1)<1e-12
 assert abs(sum(v['people_share'] for v in groups)-1)<1e-12
 assert abs(sum(v['annual_paid_wanyuan'] for v in groups)-p['total_paid_wanyuan'])<1e-8
 assert abs(sum(v['recipients_year_end'] for v in groups)-p['total_people_year_end'])<1e-8
 for v in groups:
  assert math.isclose(v['monthly_proxy_yuan'],v['annual_paid_wanyuan']*10000/(v['recipients_year_end']*12),rel_tol=1e-12)
for d in x['xiajiang_decomposition']:
 assert abs(d['annual_paid_growth_wanyuan'] - d['year_end_number_component_wanyuan']-d['amount_per_year_end_person_component_wanyuan'])<1e-6
assert abs(sum(x['jian_an_shares'].values())-1)<1e-12
assert len(x['ganzhou_18_counties'])==18
assert x['coverage']['pension_amounts_2025_counties']==2
assert x['coverage']['pension_amounts_and_people_2025_counties']==1
assert x['xiajiang_population']['unexplained_residual']==-3348
assert x['jiangxi_population']['unexplained_residual']==-191000
assert x['jiangxi_wages']['nonprivate']==99446
assert x['jiangxi_wages']['private']==57223
print('PASS: 100区县、11市、养老金计算与分解、样本覆盖、人口残差、工资指标')