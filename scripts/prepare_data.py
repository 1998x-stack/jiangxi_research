"""构建逐条证据表。原始数据来自已核对来源文字及既有工作簿的原始采集表。无网络环境下不假装下载原件。"""
from pathlib import Path
import csv, json
BASE=Path(__file__).resolve().parent.parent
DATA=BASE/'data'
SOURCES=[
('S01','江西省2025年国民经济和社会发展统计公报','江西省统计局、国家统计局江西调查总队','江西省','2025','官方公报刊载','https://epaper.jxxw.com.cn/html/2026-03/27/content_7_88438.htm','A-官方发布渠道','综合、就业、社保章节','2026-03-27','无法下载原始网页文件；已在检索工具核对文字'),
('S02','峡江县2025年国民经济和社会发展统计公报','署名峡江县统计局','峡江县','2025','第三方统计公报转载','https://tjgb.hongheiku.com/xjtjgb/xj2020/73609.html','B-原文转载待官方终核','十、人口就业、人民生活和社会保障','2026-06-07','尚未取得可访问的2025县政府原文；数据为年度快报'),
('S03','峡江县2024年国民经济和社会发展统计公报','署名峡江县统计局','峡江县','2024','第三方转载＋官方搜索摘要','https://tjgb.hongheiku.com/xjtjgb/xj2020/65339.html','B-转载/局部官方确认','十、人口就业、人民生活和社会保障','2025-07-09','县政府2024版本链接 https://m.xiajiang.gov.cn/news-show-52834.html 访问超时'),
('S04','吉安县2025年国民经济和社会发展统计公报','署名吉安县相关统计部门','吉安县','2025','第三方平台公报全文','https://maptable.com/tjgb/2025/%E5%90%89%E5%AE%89%E5%B8%82/%E5%90%89%E5%AE%89%E5%8E%BF/report/ji-an-shi-ji-an-xian-2025-nian-guo-min-jing-ji-he-she-hui-fa-zhan-tong-ji-gong-bao','B-原文转载待官方终核','九、人民生活与社会保障','2026','未找到县政府原始发布全文；只有养老金金额、无分制度待遇领取人数'),
('S05','2025年赣州常住人口总量总体稳定 城镇化率突破60%','赣州市统计局','赣州市及分县','2025','市政府官网原文','https://www.ganzhou.gov.cn/zfxxgk/tjzdtjfx/202605/1b10c9c94cf1443f851d6523be5863d3.shtml','A-政府原始发布','正文与各县常住人口表','2026-05-14','含20个统计片区，县级建制18个；功能区不得混入行政区合计'),
('S06','赣州2024年各县（市、区）常住人口主要指标','赣州市统计局','赣州市及分县','2024','市政府官网原文','https://www.ganzhou.gov.cn/zfxxgk/c100093n1/202503/c7bfdc7911ac4c898c559e58a215509a.shtml','A-政府原始发布','常住人口、性别比、城镇化率表','2025-03-22','人口以万人两位小数发布，增量含舍入误差'),
('S07','石城县2025年国民经济和社会发展统计公报','石城县统计局','石城县','2025','县政府官网原文','https://www.shicheng.gov.cn/scxxxgk/tjgb/202604/adc5c0bf738b43f3b5b80a2693d08ed4.shtml','A-政府原始发布','一、综合；九、人口、人民生活、社会保障','2026-04-21','60岁及以上人数是户籍人口口径；不得除以常住人口'),
('S08','江西省住房公积金2025年年度报告','江西省住房和城乡建设厅','江西省/设区市','2025','省住建厅原始通知及官方内容转载','https://zjt.jiangxi.gov.cn/jxszfhcxjst/wjtz/pc/content/content_2049308288025104384.html','A-主管部门发布/可检索','二、业务运行情况：缴存、提取、贷款','2026-04-30','市级表格来自既有工作簿，须对照官方图片逐行最终核验'),
('S09','江西省2025年全省和省级预算执行情况与2026年预算草案报告','江西省财政厅','江西省全省/省级','2025执行','省人大会议文件（江西日报）','https://jiangxi.jxnews.com.cn/system/2026/02/09/031051192.shtml','A-政府预算报告','2025全省与省级社会保险基金预算执行','2026-02-09','全省与省级分开，不是仅基本养老金'),
('S10','江西省2025年省级决算和2026年上半年预算执行情况报告','江西省人民政府、省人大新闻','江西省省级','2025决算','人大网站公报','https://jxrd.jxnews.com.cn/system/2026/08/11/031215391.shtml','A-人大公报','2025省级社保基金预算决算','2026-08-11','省级决算不得与全省执行混合或加总'),
('S11','江西省2025年平均工资公布','江西省统计局(江西统计)；赣江新区官网转载','江西省','2025','政府网页转载主管部门发布','https://www.jdzzsq.gov.cn/qrsj/qtfdgkxx/gzdt/t1095997.shtml','A-政府系统转载','城镇非私营与私营就业人员工资','2026-06-26','不同单位类型、样本构成；不能当同职业待遇差异'),
('S12','县以上行政区划代码截至2024-12-31','县级区划代码汇编站点','江西省100县级单位','2024','第三方代码汇编','https://www.zxinc.org/gb2260-2024.htm','B-2024代码待2025民政部核','江西省360000段','2024-12-31','未取得2025末民政部名录，不能标注为2025已官方确认'),
('S13','江西省2025调整退休人员基本养老金政策执行','财政部江西监管局','江西省','2025','财政部监管局官网','https://jx.mof.gov.cn/xxgk/tongzhitonggao/202507/t20250728_3968859.htm','A-中央部门官网','相关养老金调整政策','2025-07','调整与各群体待遇水平差异需分别研究'),
('S14','中华人民共和国2025年国民经济和社会发展统计公报','国家统计局','全国','2025','国家统计局官网','https://www.stats.gov.cn/sj/zxfbhjd/202602/t20260228_1962662.html','A-国家统计局原文','一、综合，人口与就业','2026-02-28','全国背景，不可用于替代江西县级指标'),
('S15','江西省2025年公积金年报官方稿转发','江西住建官方稿、凤凰网江西频道','江西省','2025','政府官方内容媒体转载','https://jx.ifeng.com/c/8sk35lBJNwe','B-官方内容转载','缴存、提取、住房贷款','2026-04-30','官网页面访问超时情况下交叉核验总计；不自动背书市级截图转录'),
('S16','江西省行政区划（2025年）','区划地名网','江西省','2025','第三方按年度行政名录','https://xzqh.org/show/china/36/2025.html','B-行政区划二手索引','2025末11市100县级单位','2025','2025数目与既有100县表相符；民政部为最终编码源'),
]
with (DATA/'sources.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['source_id','title','publisher','geography','observation_year','source_type','url','grade','locator','publication_date','caveat']);w.writerows(SOURCES)
F=[]
def add(code,name,level,year,indicator,value,unit,sid,population='',status='',note=''):
 F.append([code,name,level,year,indicator,value,unit,population,sid,status or ('A_政府原文' if sid in ['S05','S06','S07','S09','S10','S14'] else 'B_官方稿或转载'),'未备份原始网页；依据检索核对','',note])
# 连续两年峡江数据：2025县统计局署名转载、2024版本官方搜索摘要+转载。
for year,sid,groups in [
 (2024,'S03', [('enterprise',10779,26955.46,24495,18642.90),('public',2453,15209.48,4977,11378.18),('resident',25995,5975.44,33989,4208.58)]),
 (2025,'S02', [('enterprise',11273,29571.25,23914,20208.14),('public',2508,16218.5,4952,11723.52),('resident',27367,7910.83,31028,5134.06)])]:
 for g,n,a,paid,c in groups:
  add('360823','峡江县','县',year,'pension_'+g+'_recipients_year_end',n,'人',sid,g,'B_转载待官方核','年末人数，非全年平均领取人数')
  add('360823','峡江县','县',year,'pension_'+g+'_annual_paid',a,'万元',sid,g,'B_转载待官方核','2025初步快报，资金发放口径待专项核对')
  add('360823','峡江县','县',year,'pension_'+g+'_active_or_paid',paid,'人',sid,g,'B_转载待官方核','职工在职参保/城乡居民实际缴费不同口径')
  add('360823','峡江县','县',year,'pension_'+g+'_contribution',c,'万元',sid,g,'B_转载待官方核','征缴基金，不等于同一县域待遇支付的全部资金来源')
for y,sid,pop,birth,death,urban,hukou in [
 (2024,'S03',146153,1188,1251,77415,188734),
 (2025,'S02',142688,931,1048,76554,187997)]:
 for k,v,u in [('resident_population_year_end',pop,'人'),('births',birth,'人'),('deaths',death,'人'),('urban_resident_population',urban,'人'),('hukou_population',hukou,'人')]:
  add('360823','峡江县','县',y,k,v,u,sid,'常住人口' if k!='hukou_population' else '户籍','B_转载待官方核')
# 吉安县公开数据仅有金额三项，没有领取人数。
for g,v in [('enterprise',57981),('public',32639),('resident',22880)]:
 add('360821','吉安县','县',2025,'pension_'+g+'_annual_paid',v,'万元','S04',g,'B_转载待官方核','不能用参保人数替代待遇人数')
for k,v in [('new_urban_jobs',6041),('urban_income',46935),('rural_income',21265)]:
 add('360821','吉安县','县',2025,k,v,'人' if k=='new_urban_jobs' else '元','S04','','B_转载待官方核')
# 石城县官方县公报。年龄人口明确户籍口径。
for k,v,u,p in [('resident_population_year_end',280500,'人','常住'),('hukou_population',327427,'人','户籍'),('hukou_age_60plus',61421,'人','户籍'),('new_urban_jobs',1410,'人',''),('urban_income',37550,'元','城镇居民'),('rural_income',19075,'元','农村居民'),('general_public_budget_income',85425,'万元','一般公共预算'),('general_public_budget_expenditure',295697,'万元','一般公共预算'),('gdp',120.7736,'亿元','')]:
 add('360735','石城县','县',2025,k,v,u,'S07',p,'A_政府原文')
# 赣州市官方县级人口统计表沿用既有数据，但精度及区域范围核查通过。
with (DATA/'regions_2025.csv').open(encoding='utf-8-sig',newline='') as f:
 code_by_name={r['county']:r['region_code'] for r in csv.DictReader(f)}
# 2024/25县表来自旧版xlsx，单独复制到此处形成可复核结构。
city_rows = [
('章贡区',71.52,71.80,90.95,91.47),('南康区',83.52,83.82,62.99,64.61),('赣县区',57.59,57.34,57.24,58.48),
('信丰县',67.23,67.24,56.01,57.52),('大余县',26.13,26.07,57.04,58.48),('上犹县',26.69,26.57,51.97,53.44),
('崇义县',17.63,17.57,50.42,51.79),('安远县',34.33,34.22,49.92,51.51),('定南县',20.85,20.97,66.90,68.13),
('全南县',16.81,16.80,58.16,59.53),('宁都县',69.29,69.05,52.58,54.10),('于都县',89.96,89.62,47.38,48.90),
('兴国县',70.98,70.63,48.75,50.35),('会昌县',44.93,45.08,57.81,59.23),('寻乌县',27.97,27.97,54.24,55.69),
('石城县',28.12,28.05,51.76,53.34),('瑞金市',61.06,60.67,53.69,55.13),('龙南市',31.63,31.67,67.78,68.87)
]
for county,p24,p25,u24,u25 in city_rows:
 for yr,sid,pop,urban in [(2024,'S06',p24,u24),(2025,'S05',p25,u25)]:
  add(code_by_name[county],county,'县',yr,'resident_population_year_end',int(round(pop*10000)),'人',sid,'常住','A_政府原文','表内原单位万人，精度0.01万人')
  add(code_by_name[county],county,'县',yr,'urbanization_rate',urban,'%',sid,'常住','A_政府原文','官方县区常住人口城镇化率')
# 江西省宏观数据，省级与县级分层。
for k,v,u in [('resident_population_year_end',44740000,'人'),('urban_resident_population',28990000,'人'),('births',248000,'人'),('deaths',337000,'人'),('new_urban_jobs',485000,'人'),('pension_employee_enrolled',15178000,'人'),('pension_resident_enrolled',19030000,'人'),('gdp',36020,'亿元')]:
 add('360000','江西省','省',2025,k,v,u,'S01','全省','A_官方公报刊载','参保≠领取待遇；GDP不等于财政支出')
add('360000','江西省','省',2024,'resident_population_year_end',45020000,'人','S01','全省','A_官方公报刊载','据2025年末4474万人、同比减少28万人反推（比较基期）')
for k,v in [('provident_contributors',3537700),('provident_annual_deposit',728.52),('provident_annual_withdrawal',503.42),('provident_annual_loans',282.16)]:
 add('360000','江西省','省',2025,k,v,'人' if k=='provident_contributors' else '亿元','S08','全省','A_官方部门发布','公积金并非养老保险，2025年报总体指标')
for k,v in [('urban_nonprivate_avg_wage',99446),('urban_private_avg_wage',57223)]:
 add('360000','江西省','省',2025,k,v,'元','S11','对应城镇就业单位类型','A_政府系统转载','不同统计样本，不等于同岗位劳动者工资差')
for k,v,level,sid in [('social_insurance_budget_executed_income',2735.8,'全省','S09'),('social_insurance_budget_executed_expenditure',2603,'全省','S09'),('social_insurance_budget_executed_balance',132.8,'全省','S09'),('social_insurance_budget_executed_rollover',2610,'全省','S09'),('social_insurance_budget_provincial_final_income',1398.9,'省级','S10'),('social_insurance_budget_provincial_final_expenditure',1372.9,'省级','S10')]:
 add('360000','江西省',level,2025,k,v,'亿元',sid,'社保基金预算','A_人大/财政公开','包含多险种，2025全省执行与省级决算绝不可直接做差')
with (DATA/'observations_reviewed.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['region_code','region_name','level','year','indicator_id','value','unit','population_scope','source_id','verification_status','snapshot_status','page_number','caveat']);w.writerows(F)
print('sources',len(SOURCES),'facts',len(F),'gz counties',len(city_rows))