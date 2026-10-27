"""江西省县域社会保障研究：可复现的描述分析与测试（仅Python标准库，图形可选matplotlib）。
运行: python scripts/prepare_data.py && python scripts/reproduce.py && python scripts/test_research.py
不进行因果回归；不足样本不做县级养老金全省推断。
"""
from pathlib import Path
import csv, json, math, statistics, collections
BASE=Path(__file__).resolve().parent.parent
DATA=BASE/'data'; OUT=BASE/'outputs'; FIG=BASE/'figures'
OUT.mkdir(exist_ok=True);FIG.mkdir(exist_ok=True)
def read(name):
 with (DATA/name).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
obs=read('observations_reviewed.csv')
counties=read('regions_2025.csv')
sources=read('sources.csv')
idx=collections.defaultdict(list)
for r in obs:
 try:r['value']=float(r['value'])
 except (TypeError,ValueError):r['value']=None
 idx[(r['region_code'],int(r['year']),r['indicator_id'])].append(r)

def get(code,year,indicator):
 arr=idx[(code,year,indicator)]
 if not arr:return None
 arr=sorted(arr,key=lambda r:(not r['verification_status'].startswith('A'),r['source_id']))
 return arr[0]['value']

def ratio(a,b):return a/b if (a is not None and b) else None

def county_pension(year,code='360823'):
 arr=[]
 for g,cn in [('enterprise','企业职工'),('public','机关事业'),('resident','城乡居民')]:
  n=get(code,year,'pension_'+g+'_recipients_year_end')
  a=get(code,year,'pension_'+g+'_annual_paid')
  paid=get(code,year,'pension_'+g+'_active_or_paid')
  contribution=get(code,year,'pension_'+g+'_contribution')
  arr.append(dict(group=g,name=cn,recipients_year_end=n,annual_paid_wanyuan=a,monthly_proxy_yuan=ratio(a*10000,n*12) if a is not None else None,active_paid=paid,contribution_wanyuan=contribution))
 tna=sum(r['recipients_year_end'] for r in arr); taa=sum(r['annual_paid_wanyuan'] for r in arr)
 for r in arr:
  r['people_share']=r['recipients_year_end']/tna
  r['paid_share']=r['annual_paid_wanyuan']/taa
  r['payer_to_receiver_proxy']=ratio(r['active_paid'],r['recipients_year_end'])
 return {'year':year,'total_people_year_end':tna,'total_paid_wanyuan':taa,'groups':arr}

p24=county_pension(2024);p25=county_pension(2025)
assert abs(p25['total_paid_wanyuan']-53700.58)<1e-5
assert abs(p24['total_paid_wanyuan']-48140.38)<1e-5
# 解析政策：总额增长分解 ΔA = ΔN×均值(A/N)+ Δ(A/N)×均值(N)，精确恒等式。
decom=[]
for r0,r1 in zip(p24['groups'],p25['groups']):
 n0,n1=r0['recipients_year_end'],r1['recipients_year_end']
 a0,a1=r0['annual_paid_wanyuan'],r1['annual_paid_wanyuan']
 b0,b1=a0/n0,a1/n1
 qty=(n1-n0)*(b0+b1)/2
 intensity=(b1-b0)*(n0+n1)/2
 assert abs((a1-a0)-(qty+intensity))<1e-7
 decom.append(dict(group=r1['group'],annual_paid_growth_wanyuan=a1-a0,year_end_number_component_wanyuan=qty,amount_per_year_end_person_component_wanyuan=intensity,method='对称精确恒等分解（并非因果贡献，年末人数代理）'))
# 省县人口拆分。
pop24=get('360823',2024,'resident_population_year_end');pop25=get('360823',2025,'resident_population_year_end')
births=get('360823',2025,'births');deaths=get('360823',2025,'deaths')
netchange=pop25-pop24; natural=births-deaths; residual=netchange-natural
# 18县区两年官方表，检验相加并逐一计算。
pops=[]
for r in counties:
 if r['prefecture']!='赣州市':continue
 code=r['region_code'];name=r['county']
 a,b=get(code,2024,'resident_population_year_end'),get(code,2025,'resident_population_year_end')
 u0,u1=get(code,2024,'urbanization_rate'),get(code,2025,'urbanization_rate')
 if a is None or b is None:continue
 pops.append(dict(region_code=code,county=name,pop_2024=a,pop_2025=b,delta_people=b-a,change_rate=(b-a)/a,urbanization_2024=u0,urbanization_2025=u1,urbanization_delta_pp=u1-u0))
assert len(pops)==18
# 注意官方赣州总人口还包括统计功能区，避免18区合计误当市计。
prov=dict(pop_2025=get('360000',2025,'resident_population_year_end'),pop_2024=get('360000',2024,'resident_population_year_end'))
prov['delta']=prov['pop_2025']-prov['pop_2024'];prov['natural_change']=get('360000',2025,'births')-get('360000',2025,'deaths');prov['unexplained_residual']=prov['delta']-prov['natural_change']
# 吉安县完整金额、不含完整待遇人数。
jian={}
for grp in ('enterprise','public','resident'):
 jian[grp]=get('360821',2025,'pension_'+grp+'_annual_paid')
jian_sum=sum(jian.values())
jian_shares={k:v/jian_sum for k,v in jian.items()}
# 公积金各市旧版表为待逐图复核证据层；全省指标可由官方原文核。
cpf=read('prior_provident_2025_cities.csv')
cpfs=[]
for r in cpf:
 if r['地级市']=='江西省合计':continue
 n=float(r['实缴人数_万人']);amount=float(r['缴存额_亿元'])
 cpfs.append(dict(city=r['地级市'],contributors_10000=n,deposit_yi=amount,monthly_per_payer_proxy_yuan=round(amount*1e8/(n*1e4*12),1),status='B_分市图片转录待逐行终核'))
cpfs.sort(key=lambda r:-r['monthly_per_payer_proxy_yuan'])
# 证据质量检查。
core_counties_complete=sum(all(get(c['region_code'],2025,'pension_'+g+'_annual_paid') is not None and get(c['region_code'],2025,'pension_'+g+'_recipients_year_end') is not None for g in ('enterprise','public','resident')) for c in counties)
amounts_counties_complete=sum(all(get(c['region_code'],2025,'pension_'+g+'_annual_paid') is not None for g in ('enterprise','public','resident')) for c in counties)
coverage=dict(counties_total=len(counties),pension_amounts_2025_counties=amounts_counties_complete,pension_amounts_and_people_2025_counties=core_counties_complete,ganzhou_counties_two_years=len(pops),government_origin_observations=sum(r['verification_status'].startswith('A') for r in obs),source_secondary_observations=sum(r['verification_status'].startswith('B') for r in obs),observations_total=len(obs))
# 来源冲突：同指标/区域/年不同来源产生的数值差异。
conflicts=[]
for key,arr in idx.items():
 if len(arr)>1 and len({r['value'] for r in arr})>1:
  conflicts.append({'key':key,'entries':[(r['source_id'],r['value']) for r in arr]})
result=dict(meta={'base_year':2025,'methodology':'描述性研究，核查截至2026-10-27；不推断未公开县的养老金','warning':'县级2025养老金数据源属转载 B，尚未获官方原始版本；不形成全省养老金占比估计'},coverage=coverage,xiajiang_2024=p24,xiajiang_2025=p25,xiajiang_decomposition=decom,xiajiang_population=dict(year_end_pop_2024=pop24,year_end_pop_2025=pop25,change=netchange,births=births,deaths=deaths,natural_change=natural,unexplained_residual=residual),jian_an_shares=jian_shares,ganzhou_18_counties=pops,ganzhou_18_change_summary=dict(gain_count=sum(p['delta_people']>0 for p in pops),decline_count=sum(p['delta_people']<0 for p in pops),unchanged_count=sum(p['delta_people']==0 for p in pops),sum_2024=sum(p['pop_2024'] for p in pops),sum_2025=sum(p['pop_2025'] for p in pops),sum_delta=sum(p['delta_people'] for p in pops)),jiangxi_population=prov,jiangxi_wages=dict(nonprivate=get('360000',2025,'urban_nonprivate_avg_wage'),private=get('360000',2025,'urban_private_avg_wage')),provident_city_unverified=cpfs,source_conflicts=conflicts)
with (OUT/'analysis_results.json').open('w',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
with (OUT/'ganzhou_population_2024_2025.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(pops[0]));w.writeheader();w.writerows(pops)
# 简要机器报告：不把中间层证据误表示为官方已核。
with (OUT/'validation_summary.txt').open('w',encoding='utf-8') as f:
 for k,v in coverage.items():f.write(f'{k}: {v}\n')
 f.write(f'2025峡江机关事业金额占比: {p25["groups"][1]["paid_share"]:.8%}\n')
 f.write(f'2025峡江人口变动余项: {residual:.0f}\n')
 f.write(f'不同来源相同观察项数据冲突个数: {len(conflicts)}\n')
try:
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib import font_manager
 font_manager.fontManager.addfont('/usr/share/fonts/truetype/arphic-gbsn00lp/gbsn00lp.ttf')
 plt.rcParams['font.family']=[font_manager.FontProperties(fname='/usr/share/fonts/truetype/arphic-gbsn00lp/gbsn00lp.ttf').get_name()]
 plt.rcParams['axes.unicode_minus']=False
 fig,ax=plt.subplots(figsize=(9.0,4.2))
 cats=[r['name'] for r in p24['groups']]
 ys=[r['paid_share']*100 for r in p24['groups']];ys1=[r['paid_share']*100 for r in p25['groups']]
 x=range(3);ax.bar([i-.19 for i in x],ys,width=.36,label='2024');ax.bar([i+.19 for i in x],ys1,width=.36,label='2025')
 ax.set_xticks(list(x),cats);ax.set_ylabel('三类养老金发放金额占比（%）');ax.set_ylim(0,65);ax.legend(frameon=False);ax.grid(axis='y',alpha=.15)
 fig.tight_layout();fig.savefig(FIG/'峡江养老金金额占比_两年对比.png',dpi=190);plt.close(fig)
 fig,ax=plt.subplots(figsize=(9,5))
 sortedp=sorted(pops,key=lambda q:q['delta_people'])
 ax.barh([v['county'] for v in sortedp],[v['delta_people'] for v in sortedp])
 ax.set_xlabel('2025年相对2024年常住人口变化（人，精度约百人）');ax.grid(axis='x',alpha=.14)
 fig.tight_layout();fig.savefig(FIG/'赣州18县人口增减.png',dpi=190);plt.close(fig)
except ImportError:
 print('matplotlib 不可用，仅提供机器可读结果')
print('研究样本质量：',coverage)
print('峡江2025机关养老金份额:',round(p25['groups'][1]['paid_share']*100,3))
print('省2025人口变化残差:',prov)
print('赣州18县汇总:',result['ganzhou_18_change_summary'])
print('跨来源冲突:',conflicts)