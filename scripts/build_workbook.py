"""在上一版Excel之上附加严格证据层、公式与审查表。仅使用artifact_tool编辑XLSX。
执行依赖 data/上一版基础数据库.xlsx 和 prepare_data、reproduce 输出。
"""
from pathlib import Path
import csv,json
from artifact_tool import Blob,SpreadsheetFile
BASE=Path(__file__).resolve().parent.parent
DATA=BASE/'data';OUT=BASE/'outputs'
def rows(name):
 with (DATA/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
w=SpreadsheetFile.import_xlsx(Blob.load(str(DATA/'上一版基础数据库.xlsx')))
result=json.loads((OUT/'analysis_results.json').read_text(encoding='utf-8'))
regions=rows('regions_2025.csv'); sources=rows('sources.csv');facts=rows('observations_reviewed.csv')
navy='#16324F'; blue='#235789'; grey='#F0F4F7';white='#FFFFFF'; green='#087E65'
def new_sheet(name,headers,body,widths=None):
 s=w.worksheets.add(name)
 n=len(headers)
 if n:
  s.get_range_by_indexes(0,0,1,n).values=[headers]
  r=s.get_range_by_indexes(0,0,1,n)
  r.format={'fill':navy,'font':{'bold':True,'color':white},'row_height':29,'vertical_alignment':'center','wrap_text':True}
  s.freeze_panes.freeze_rows(1)
 if body:
  # Excel requires None instead of absent values; bulk write.
  s.get_range_by_indexes(1,0,len(body),n).values=[list(b)[:n]+[None]*max(0,n-len(b)) for b in body]
 if widths:
  for j,wd in enumerate(widths):s.get_range_by_indexes(0,j,max(2,len(body)+1),1).format.column_width=wd
 else:
  s.get_range_by_indexes(0,0,max(2,len(body)+1),n).format.column_width=18
 return s
# 首页，聚焦成熟证据覆盖而非所有旧版的未验证汇总。
cover=result['coverage'];p24=result['xiajiang_2024'];p25=result['xiajiang_2025'];xi=result['xiajiang_population']
home=[
 ('研究基准','2025年','对照2024，历史数据按可获得性补充','2026-10-27'),
 ('区县建档',100,'11设区市；2025末代码待民政部原表最终核验','S12/S16'),
 ('2025养老金金额三类齐全县数',2,'峡江县、吉安县；二者均为转载全文','S02/S04'),
 ('2025养老金金额和领取人数齐全县数',1,'仅峡江县，属B级，尚未取得官网原件','S02'),
 ('赣州两年人口可比县数',18,'政府官网原始发布，不含两个功能区','S05/S06'),
 ('严格分析事实条数',cover['observations_total'],'102条来自可核对政府/主管部门发布；40条B级', 'observations_reviewed.csv'),
 ('峡江机关养老金金额占比2025',p25['groups'][1]['paid_share'],'仅为峡江县三类金额占比，禁止推全省','S02'),
 ('峡江机关退休人数占比2025',p25['groups'][1]['people_share'],'年末人数占比，与年度支出分母不等','S02'),
 ('峡江人口变动残差',xi['unexplained_residual'],'不等于已确认净迁出；可能含统计口径调整','S02/S03'),
 ('江西全省2025人口变化',result['jiangxi_population']['delta'],'常住人口较2024年变化','S01'),
 ('核心事实等级说明','A=政府原始发布; B=转载/待终核','未经确认的旧版2025县指标保留在旧工作表，不自动升级','sources.csv'),
 ('源网页本地快照','尚未保存','研究环境无法下载源HTML/PDF；有URL及定位位置','sources.csv'),
 ('可信结论范围','描述性与结构恒等分解','不能宣称全省养老金份额或因果机制','研究报告'),
]
s=new_sheet('研究入口_新', ['审查主题','结论/数值','解释及约束','来源'],home,[29,31,78,28])
s.get_range('B8:B9').set_number_format('0.00%')
# source inventory
sourceheaders=['source_id','报告/文件名','发布单位','统计地域','研究年份','证据形式','来源URL','等级','原文定位','发布日期','缺口与警告']
new_sheet('来源索引_新',sourceheaders,[[q[h] for h in ['source_id','title','publisher','geography','observation_year','source_type','url','grade','locator','publication_date','caveat']] for q in sources],[13,42,26,20,13,24,38,24,35,16,55])
# regions
new_sheet('县区编码100', ['区划代码','省','地级市','县级区','行政类型','代码参照源','代码基期','2025官方核验情况'],[[r[k] for k in ['region_code','province','prefecture','county','type','code_reference','code_reference_year','verified_for_2025']] for r in regions],[15,13,16,18,13,36,17,38])
# full observations
obshead=['行政代码','地域','层级','年份','指标ID','原始值','单位','群体范围','来源ID','核验状态','原文快照','页码','口径备注']
new_sheet('证据事实142条',obshead,[[o[k] if k!='value' else (float(o[k]) if o[k] else None) for k in ['region_code','region_name','level','year','indicator_id','value','unit','population_scope','source_id','verification_status','snapshot_status','page_number','caveat']] for o in facts],[15,15,10,11,38,18,12,20,13,26,35,12,58])
# Xiajiang longitudinal shares all formula sourced from raw values, not fixed outputs
rawrows=[]
for y,p in [(2024,p24),(2025,p25)]:
 for gr in p['groups']:
  rawrows.append([y,gr['name'],gr['recipients_year_end'],gr['annual_paid_wanyuan'],gr['active_paid'],gr['contribution_wanyuan'],None,None,None,None,None,'S03' if y==2024 else 'S02','B_转载待官方终核'])
s=new_sheet('峡江养老金_复算', ['年','群体','年末领取人数(人)','年度待遇金额(万元)','在职参保或实际缴费','征缴基金(万元)','估算月待遇(元)','人数占比','金额占比','缴费者与领取者比值(混合口径)','各组年发放合计','来源','证据状态'],rawrows,[10,17,21,21,25,20,20,16,16,36,19,13,29])
for i in range(2,8):
 st=2 if i<=4 else 5;end=st+2
 s.get_range(f'G{i}').formulas=[[f'=IFERROR(D{i}*10000/C{i}/12,"")']]
 s.get_range(f'H{i}').formulas=[[f'=IFERROR(C{i}/SUM(C${st}:C${end}),"")']]
 s.get_range(f'I{i}').formulas=[[f'=IFERROR(D{i}/SUM(D${st}:D${end}),"")']]
 s.get_range(f'J{i}').formulas=[[f'=IFERROR(E{i}/C{i},"")']]
 s.get_range(f'K{i}').formulas=[[f'=SUM(D${st}:D${end})']]
s.get_range('H2:I7').set_number_format('0.00%')
s.get_range('G2:G7').set_number_format('#,##0.0')
# Exact noncausal decomposition via formula direct from raw rows
raw=[]
for i,grp in enumerate(('企业职工','机关事业','城乡居民')):
 old=i+2;new=i+5
 raw.append([grp,None,None,None,None,None,None,None,'基于年末人数的对称分解，不代表因果贡献'])
s2=new_sheet('峡江金额变化分解',['群体','2024发放万元','2025发放万元','总变化万元','人数结构分量万元','人均发放代理变化分量万元','检验误差','同比','说明'],raw,[20,19,19,17,26,30,16,15,61])
for i in range(2,5):
 r24=i;r25=i+3
 for col,formula in [('B',f"='峡江养老金_复算'!D{r24}"),('C',f"='峡江养老金_复算'!D{r25}"),('D',f'=C{i}-B{i}'),('E',f"=('峡江养老金_复算'!C{r25}-'峡江养老金_复算'!C{r24})*(B{i}/'峡江养老金_复算'!C{r24}+C{i}/'峡江养老金_复算'!C{r25})/2"),('F',f"=(C{i}/'峡江养老金_复算'!C{r25}-B{i}/'峡江养老金_复算'!C{r24})*('峡江养老金_复算'!C{r24}+'峡江养老金_复算'!C{r25})/2"),('G',f'=D{i}-E{i}-F{i}'),('H',f'=IFERROR(D{i}/B{i},"")')]:
  s2.get_range(f'{col}{i}').formulas=[[formula]]
s2.get_range('H2:H4').set_number_format('0.0%')
# population with official sources
poprows=[]
for r in result['ganzhou_18_counties']:
 poprows.append([r['region_code'],r['county'],r['pop_2024'],r['pop_2025'],None,None,r['urbanization_2024'],r['urbanization_2025'],None,'S06','S05','A_两年官方原文'])
ps=new_sheet('赣州18县_政府原文',['代码','县区','2024年末常住人口','2025年末常住人口','人数变化','同比','2024城镇化率%','2025城镇化率%','百分点变化','2024来源','2025来源','核验情况'],poprows,[15,18,24,24,19,14,20,20,17,17,17,27])
for i in range(2,20):
 ps.get_range(f'E{i}').formulas=[[f'=D{i}-C{i}']]
 ps.get_range(f'F{i}').formulas=[[f'=IFERROR(E{i}/C{i},"")']]
 ps.get_range(f'I{i}').formulas=[[f'=H{i}-G{i}']]
ps.get_range('F2:F19').set_number_format('0.00%')
# population residual arithmetic
rows2=[('峡江县',2024,146153,None,None,None,'B_转载'),('峡江县',2025,142688,931,1048,None,'B_转载'),('江西省',2024,45020000,None,None,None,'A_据官方2025数据反推'),('江西省',2025,44740000,248000,337000,None,'A_官方刊载')]
re=new_sheet('人口变动核对',['地区','年份','年末常住人口人','当年出生人数','当年死亡人数','自然变动人数','对上年人口变化','未解释残差(不等于净迁移)','来源证据'],[[n,y,p,b,d,None,None,None,note] for n,y,p,b,d,_,note in rows2],[16,13,24,20,20,21,23,32,34])
for i in (3,5):
 re.get_range(f'F{i}').formulas=[[f'=D{i}-E{i}']]
 re.get_range(f'G{i}').formulas=[[f'=C{i}-C{i-1}']]
 re.get_range(f'H{i}').formulas=[[f'=G{i}-F{i}']]
# Finances budget prevent misuse
budget=[('江西全省','2025执行','社保基金收入',2735.8,'亿元','S09','含养老医保工伤等险种'),('江西全省','2025执行','社保基金支出',2603,'亿元','S09','非养老金独立支出'),('江西省级','2025决算','社保基金收入',1398.9,'亿元','S10','省级决算与全省执行不是同层级'),('江西省级','2025决算','社保基金支出',1372.9,'亿元','S10','不得直接与全省执行数据相减'),('峡江县','2025县统计公报','三类养老金金额加总',53700.58,'万元','S02','不可对比一般公共预算功能科目'),('峡江县','2025县统计公报','一般公共预算社会保障和就业支出',42516,'万元','S02','包括不同社保就业开支，不是同个基金账'),('吉安县','2025县统计公报','三类养老金金额加总',113500,'万元','S04','数据转载；包含不同群体'),('吉安县','2025县统计公报','一般公共预算社会保障和就业支出',78400,'万元','S04','一般公共预算科目')]
new_sheet('财政基金_不可混算',['范围','期间/状态','财务指标','数值','单位','证据ID','比较禁忌'],budget,[18,20,44,19,15,15,75])
quality=[
 ('县区行政名录',100,100,'完整名录/代码取2024版', '需逐项与民政部2025年终码表复核','范围完整但编码未获2025年末官方最终复核'),
 ('三类养老金额完整',2,100,'2025：峡江县、吉安县','2县均来自官方稿转载、无可下载官方网页','只做案例不代表江西全省'),
 ('三类养老金领取人数与金额完整',1,100,'2025：峡江县','2025年转载待官方终核','估算人均使用年末人数'),
 ('赣州人口两年可比',18,18,'县级行政区18；不包含经开/蓉江功能区','2024/25两个政府网页可核','城市数据不等于仅18行政区加总'),
 ('全省公积金缴存量',1,1,'省住建厅年报','全省数据可从官方稿核','不能按人口下推县级'),
 ('分市公积金表',11,11,'沿用上一版图片转录','当前尚未逐行官方图片人工复核','不得据此宣称已完成独立交叉复核'),
 ('原网页快照',0,16,'已保存直接URL与定位文字','源文件下载失败，哈希不可用','本地仅保存结构化记录'),
 ('因果分析可行性',0,5,'目前只具备描述性县区少量观察','不存在识别设计与个体数据','不得进行政策因果归因')]
new_sheet('数据质量与缺口',['指标','已核实/可用样本','分母/规划数','范围说明','阻断因素','处理原则'],quality,[37,20,19,48,55,58])
hyp=[
('H1','职业与制度历史影响人均养老金','同县内三类待遇均值存在差异','峡江2024—25', '可观察差距', '无法控制缴费年限、工资、补充年金','收集分退休年份缴费年限/年金数据','待验证'),
('H2','养老金金额占比由人数与待遇共同决定','A_g/ΣA = N_g×(A_g/N_g)/Σ[N×(A/N)]','峡江和吉安','结构恒等式','年末N不等于全年平均N','养老金经办月度领取人月数','恒等成立但机制未识别'),
('H3','人口变动残差部分来自迁移','年末变动-自然变动具有显著绝对值','峡江、省宏观','计算残差','人口统计修订与统计范围变化','公安迁移登记/抽样迁移调查','非已证实净迁移'),
('H4','县域公积金覆盖关联正规就业结构','不同市人均缴存存在差异','11市旧版汇编','探索性', '没有县级正式就业人数/缴存工资','市公积金中心按职业性质披露','研究假说'),
('H5','县财政社保预算额不等于同级养老金成本','基金预算与一般公共预算概念不同','江西财政决算','预算制度规定','不能估计县级养老金赤字','同险种决算与统筹调剂台账','规则明确')]
new_sheet('制度假说证伪路径',['假说','命题','可观测预测/公式','当前证据','证据性质','竞争解释或限制','新增证据','判定'],hyp,[12,37,66,23,24,57,46,26])
# one-page README
notes=[
 ('01','从【研究入口_新】开始阅读，新工作表是严谨证据层；原19张表保留作工作草稿，不等于全部官方终核。'),
 ('02','【证据事实142条】是规范化观察值，包含来源ID和来源核验状态；【来源索引_新】记录16份材料。'),
 ('03','【峡江养老金_复算】含计算公式；按年度发放额除以年末人数只能估算“月均金额代理”，非真实平均月养老金。'),
 ('04','【峡江金额变化分解】恒等式仅描述变化的算术贡献，不代表由人群变化因果导致的待遇改变。'),
 ('05','【县区编码100】代码基期2024，尚待2025年末民政部官方逐项核验。'),
 ('06','本项目研究文件还包含Python脚本、单元测试、CSV及报告；详见打包ZIP的README。'),
 ('07','源网址核验完成但原始快照/哈希尚缺；不能宣称已经备份政府源页面。'),
 ('08','2025年公积金官方表格的各市数字继承旧工作簿，尚未对原始图片逐行复查。')]
new_sheet('阅读与研究限制',['步骤','解释'],notes,[11,112])
# optional visual chart; do not cover table.
try:
 ch=s.charts.add('ColumnClustered',s.get_range('A1:D7'))
 ch.title_text='峡江三类养老金两年原始数据'
 ch.set_position('O2','W19')
except Exception as e: print('Chart skipped:',str(e)[:160])
OUTPATH=OUT/'江西省县域社会保障实证研究_2025严格核验版.xlsx'
SpreadsheetFile.export_xlsx(w).save(str(OUTPATH))
print('SAVED',OUTPATH)
for area in ('研究入口_新!A1:D6','峡江养老金_复算!A1:M7','数据质量与缺口!A1:F5'):
 try:
  print('inspect',area,w.inspect({'kind':'table','range':area,'include':'values,formulas','table_max_rows':8,'table_max_cols':13}).ndjson[:1400])
 except Exception as e: print('inspect failed',e)