"""把结构化分析结果编译为研究报告 Markdown 和可打印 PDF，证据只按原始来源ID引用。"""
from pathlib import Path
import json,csv,html
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outputs';DATA=ROOT/'data';FIG=ROOT/'figures'
x=json.loads((OUT/'analysis_results.json').read_text(encoding='utf-8'))
p=x['xiajiang_2025'];pold=x['xiajiang_2024'];d=x['xiajiang_decomposition'];cp=x['coverage'];gz=x['ganzhou_18_change_summary']
prof=x['jiangxi_population']; dem=x['xiajiang_population']; city=x['provident_city_unverified']
share=lambda z:f'{z*100:.2f}%'
with (DATA/'sources.csv').open(encoding='utf-8-sig',newline='') as f:src=list(csv.DictReader(f))
refs='\n'.join(f"- [{r['source_id']}] {r['title']}｜{r['publisher']}｜{r['url']}。证据等级：{r['grade']}；注意：{r['caveat']}" for r in src)
funding=2735.8-2603
report=f'''# 江西省县域社会分层与社会保障结构：人口变迁、劳动市场与制度分配的实证研究（阶段性研究报告）

**研究日期：2026-10-27**  
**核心年份：2025；对照年份：2024**  
**研究范围：江西省11个设区市与100个县级行政区建档；严格实证样本按指标各不相同。**

> **研究状态说明：这是已经完成数据复算和部分政府资料原文核验的阶段性实证成果，不是100个县全部指标齐全的终稿。** 2025年三类养老金金额齐全的县仅有2个，金额和领取人数同时齐全的县仅1个；2025峡江县养老金2025原文目前仅能核实署名统计局的全文转载（证据等级B），必须由官方原始版本进行最终复核。原始网站文件没有在本地下载成功，因此不能宣称原始网页快照或哈希已存档。

## 摘要

研究结合既有100县Excel数据库、可核查的省级统计公报及财政报告、赣州两年分县人口官方资料、石城县官方统计公报、峡江和吉安县统计公报转录数据，对江西省县域社会保障分层进行探索性分析。构建了包含**{cp['observations_total']}条标准化观察值、{len(src)}项证据来源、100个区县编码映射、18个县的两年人口比较**的严格审查分析层。观察值中{cp['government_origin_observations']}条登记为政府或主管部门可核查发布渠道、{cp['source_secondary_observations']}条依赖转载/待官方终核，证据状态不等于本地文件快照备份成功。

主要发现有三项：（一）2025年峡江县机关事业退休人数约占三类领取人数{share(p['groups'][1]['people_share'])}，年度发放金额约占{share(p['groups'][1]['paid_share'])}；差距在人数结构与估算人均待遇层面同时存在，但不能据此推断全省水平。[S02]（二）赣州18个县级行政区中有{gz['decline_count']}个2025年常住人口较2024年下降、{gz['gain_count']}个上升、{gz['unchanged_count']}个持平，而18个地区城镇化率均增加；人口总量与城镇化变化并非同一现象。[S05][S06]（三）峡江县和江西全省的常住人口变化均明显超出自然人口增减量，存在值得用迁移与统计修订资料继续解释的残差。[S01][S02][S03] 这些结论均为描述性事实、结构恒等式或待解释问题，不包含经过可靠识别的因果结论。

**关键词：**社会分层；基本养老保险；人口迁移；住房公积金；县域社会学；江西省；财政统筹

## 一、研究问题、理论框架与资料边界

研究围绕五类问题：①企业职工、机关事业单位与城乡居民之间的基本养老待遇差距；②县域人口变动与老龄化；③就业结构、工资与公积金制度覆盖；④社会保险统筹和财政预算口径；⑤上述机制如何在生命历程中累积为经济保障差异。

理论上，把社会分层与生命历程、劳动市场分割、福利制度路径依赖、县域人口迁移联系起来：职业和劳动契约影响参保资格及缴费连续性；退休年份和制度过渡影响计发规则；城乡和县域结构影响人口构成；跨地区统筹改变缴费地与给付地的会计联系。但以上均只是竞争性研究框架，尚未被个体微观数据单独识别。

数据层级严格分离：省级参保人数≠县级待遇领取人数；住房公积金市级缴存数据≠县级缴存人数；县级财政“社保就业支出”≠社保基金待遇发放。为防止生态谬误，县级平均待遇不能用于推断同等工资、年限、职业条件下个体的养老金差距。

## 二、县域养老金：支付份额、人数份额与人均待遇

| 2025年峡江县养老群体 | 年末领取人数（人） | 全年发放（万元） | 人数占比 | 发放额占比 | 估算月均（元） |
|---|---:|---:|---:|---:|---:|
'''
for v in p['groups']:
 report+=f"|{v['name']}|{int(v['recipients_year_end']):,}|{v['annual_paid_wanyuan']:,.2f}|{share(v['people_share'])}|{share(v['paid_share'])}|{v['monthly_proxy_yuan']:,.0f}|\n"
report+=f'''|**三组总计**|**{int(p['total_people_year_end']):,}**|**{p['total_paid_wanyuan']:,.2f}**|**100%**|**100%**|—|

来源：[S02]署名峡江县统计局的2025年度公报转载，待官方原文终核。所谓“估算月均”是年度发放额/年末领取人数/12，而不是精确实际月均待遇；如有年度中途增加退休人员、死亡退出、补发等，将产生统计偏差。不得把上述数值标为真实领取者个人月养老金。

2025年机关事业单位与企业的估算月均差距为**{p['groups'][1]['monthly_proxy_yuan']/p['groups'][0]['monthly_proxy_yuan']:.2f}倍**，与城乡居民约为**{p['groups'][1]['monthly_proxy_yuan']/p['groups'][2]['monthly_proxy_yuan']:.2f}倍**。这不是“公职人员拿走全省30%养老金”的证据，因为这里只是一个县的三类合计，且没有职业构成、缴费年限和补充年金明细。[S02]

### 2024—2025年变化

2024年峡江三类养老待遇发放金额合计{pold['total_paid_wanyuan']:,.2f}万元，2025年为{p['total_paid_wanyuan']:,.2f}万元，同比增长{(p['total_paid_wanyuan']/pold['total_paid_wanyuan']-1)*100:.2f}%。机关事业发放金额份额由{share(pold['groups'][1]['paid_share'])}降至{share(p['groups'][1]['paid_share'])}（下降{(pold['groups'][1]['paid_share']-p['groups'][1]['paid_share'])*100:.2f}个百分点）；城乡居民发放额份额由{share(pold['groups'][2]['paid_share'])}升至{share(p['groups'][2]['paid_share'])}。[S02][S03]

使用对称精确分解式：令年度发放总额 A=N×b，其中 N 为公报报告的年末领取人数，b=A/N 为年度人均代理量，则：

**ΔA = (N₁−N₀)×(b₀+b₁)/2 + (b₁−b₀)×(N₀+N₁)/2。**

本分解为数学恒等式，前项描述年末人数的算术关联，后项描述金额/年末人数代理的算术关联，**不能直接解释为人数增加或制度调整引起的因果影响**。

| 群体 | 发放额增加（万元） | 人数分量（万元） | 人均金额代理分量（万元） |
|---|---:|---:|---:|
'''
for a in d:
 cn={'enterprise':'企业职工','public':'机关事业','resident':'城乡居民'}[a['group']]
 report+=f"|{cn}|{a['annual_paid_growth_wanyuan']:,.2f}|{a['year_end_number_component_wanyuan']:,.2f}|{a['amount_per_year_end_person_component_wanyuan']:,.2f}|\n"
report+='''
## 三、人口变动与城镇化：关键是把人口存量与迁移机制分开

'''
report+=f'''2025年峡江县常住人口由{int(dem['year_end_pop_2024']):,}人下降到{int(dem['year_end_pop_2025']):,}人，减少{abs(int(dem['change'])):,}人；全年出生{int(dem['births']):,}人、死亡{int(dem['deaths']):,}人，自然减少{abs(int(dem['natural_change'])):,}人。两项差额为**{int(dem['unexplained_residual']):,}人**。在不掌握县际/省际迁移登记、人口调查修正、区划边界变动的情况下，不能声称该残差全是净迁出。[S02][S03]

江西全省2025年末常住人口4474万人，较上年减少28万人，全年出生24.8万人、死亡33.7万人；在公布精度下，自然减少约8.9万人，剩余**约19.1万人**的变动需由迁移及统计调整共同解释，不能直接宣称江西“净流出19.1万人”。[S01]

赣州市统计局发布了2024/2025年分县区官方人口表。对应18个县级建制，{gz['decline_count']}个减少、{gz['gain_count']}个增加、{gz['unchanged_count']}个大致持平，合计从{gz['sum_2024']/10000:.2f}万人变为{gz['sum_2025']/10000:.2f}万人（减少{abs(gz['sum_delta'])/10000:.2f}万人）。**18个行政县区两年城镇化率均上升**。赣州市官方统计还单列赣州经济技术开发区、蓉江新区两个功能区，因此不能把18县小计直接当赣州市总量，也不能把功能区当第19、第20个县级行政区。[S05][S06]

石城县政府2025年公报披露，年末户籍人口327,427人、常住人口约280,500人，60岁及以上61,421人**对应户籍人口**，比例约18.76%。这既不等于常住人口老龄化率，也不能把户籍人口与常住人口之差直接认定为净流出人数。[S07]

## 四、就业收入与公积金：正式就业的累积优势是一项待检验机制

江西省2025年城镇非私营单位就业人员年平均工资99,446元，城镇私营单位57,223元，相差42,223元，均值比例约{99446/57223:.2f}。两者涉及不同单位组成、行业和岗位分布，不能简单归结为“同岗位所有制工资溢价”。在控制学历、行业、岗位、工龄、地区前，这只是群体平均工资差。[S11]

省住建厅2025年公积金年报显示：实缴人数353.77万人，年度缴存728.52亿元，提取503.42亿元，发放个人住房贷款282.16亿元。**缴存额/实缴人数/12≈{728.52*1e8/(353.77*1e4*12):,.0f}元/月**，属于含单位与个人缴存的“缴存额与年度实缴人头之比”，未控制全年实缴月份，不能直接当作人均工资或个人当月缴存金额。市级明细目前保留先前工作簿转录值，尚未逐行完成官方图片独立核查，因此不把城市排名作为本报告核心实证结论。[S08][S15]

更深层的社会学命题是：稳定劳动关系可能影响养老缴费连续性和公积金制度进入机会，退休时形成长期资产与现金流差异。这需要个体工资、就业年限、缴费历史或可公开的分群体经办统计数据，当前县级截面无法独立判断其贡献率。

## 五、社会保险基金与公共财政：必须进行会计边界划分

2025年江西**全省**社会保险基金预算执行收入2735.8亿元、支出2603.0亿元，当年收支结余132.8亿元；它并非仅养老保险，更不等于三类基本养老金发放金额。[S09]

另据江西人大对2025年**省级**决算的报告，省级社会保险基金预算决算收入1398.9亿元、支出1372.9亿元。后者既是省级预算层级，又是决算而非全省执行，不能用“全省减省级”直接推算市县养老基金缺口。[S10]

同理，峡江县2025年三类养老金发放合计约5.37亿元，而县一般公共预算社会保障和就业支出约4.25亿元。两者属于不同会计体系和科目集合，绝对不能相减推算“养老金赤字”。[S02]

国务院2015年发布的国发〔2015〕2号规定，机关事业单位养老保险改革自2014年10月1日起实施，并规定新老衔接、视同缴费年限和过渡性养老金等机制。制度演变提供了待遇差异的一种理论解释，但没有个人退休年代、工龄和缴费基数，就不能定量估计这一机制解释的比例。[制度文献P01]

## 六、三条可以成立的结论，以及至少三条尚未成立的解释

**已获描述性支持的结论**：

1. 峡江县2025年三类养老金年度发放总额并非按年末领取人数同比例分配；机关事业养老金在人均月待遇代理值上明显高于其他两类。[S02]
2. 赣州18县区两年人口存量分化与城镇化率普遍提高同时发生，不能将城镇化率提升等同于县域人口增加。[S05][S06]
3. 全省社保基金预算、省级决算与县级一般公共预算存在不可忽略的制度和统计边界；原始科目名称本身即可确定不能混算。[S09][S10]

**未获独立验证、不能作为结论的解释**：

1. “机关事业单位拿走江西全省40%—60%的养老金”：公开完整县级样本远不足以推断，且省级基金有不同汇总口径。
2. “峡江县人口变动差额全部是外出务工人口”：没有分年龄迁移调查和统计修订明细。
3. “不同群体养老金差异主要因为机关身份，而不是缴费与历史制度”：缺乏可比微观数据与因果识别。
4. “江西各县住房公积金缴存水平能从11市年报推算”：市级数据不得按人口比例伪装成县级真实值。

## 七、研究设计、证据质量与独立复核

研究输出采用region_code+year+indicator_id+population_scope+source_id作为分析原始事实层可追溯键；如出现多来源相同变量，保留多条原始记录并进行一致性测试。统计原始文件快照暂未成功备份，当前“来源可定位”不等于“电子档案完整”；来源目录中已说明。

严格审查集包含**{cp['observations_total']}条**标准化记录；其中政府/主管部门原文或公开渠道标记为A级**{cp['government_origin_observations']}条**，转载等B级**{cp['source_secondary_observations']}条**。截至当前，2025养老金三类发放金额齐全县仅**{cp['pension_amounts_2025_counties']}/{cp['counties_total']}**；三类人数与金额齐全仅**{cp['pension_amounts_and_people_2025_counties']}/{cp['counties_total']}**。数据缺失具有潜在选择偏差，因此不能将样本县经验简单推广。

独立测试已经覆盖100县编码唯一、11地级市数量、养老金人数和金额份额加总、月待遇代理值公式、2024—25结构分解残差、赣州18县对照和人口自然变动残差。测试能证明程序与录入值的算术一致性，**不能替代对源政府原件的人工核验**。原始快照为零，存在不可接受的学术档案完备性缺口；研究终稿必须补齐快照、页码和SHA-256。

## 八、下一阶段优先补证路线（按对结论影响排序）

1. **优先获取峡江与吉安2025年统计公报政府原始文件**，争取月度养老金发放人月数，核查基本养老金是否包含年金、死亡抚恤或补发。
2. **通过各设区市社保经办机关/财政决算获取三类基本养老保险人数与基金分项**。优先同口径覆盖多个县的完整组团，而不是无差别抓取几千条异口径数据。
3. **获取2025年民政部行政区划代码终版**，和2024基准匹配，明确功能区的统计边界。
4. **获取县域迁移和人口年龄结构表**，至少区分常住、户籍、16—59岁人口及净迁移测算中的统计修订。
5. **逐图验证2025公积金年报的11市数字、职业/单位类别缴存结构**，有县级原始资料时才构建县级公积金模型。
6. 在有足够多年且同口径的真实观察后再决定是否使用面板回归、空间计量、反事实模型或定性访谈；缺乏数据条件时拒绝因果宣称。

## 九、政策含义与研究结论

江西省的社会分层研究需要把“制度进入机会—工资和就业轨迹—养老缴费记录—退休待遇—财政与统筹安排”看作一个连续的生命历程，而不是一张简单的养老金领取比例饼图。当前数据已足以证明不同县与不同养老制度之间存在结构性差异、人口与城镇化变动不能被简单归类，并且部分广泛流传的财政推算法在会计上不成立。但它**不足以判断差距中多少来自制度身份、多少来自工龄工资，或给出全省养老金制度分配比例**。可靠的否定性发现与无法验证的边界，同样是研究成果。

## 附录A：数据源目录

{refs}

## 附录B：补充制度资料

- [P01] 国务院《关于机关事业单位工作人员养老保险制度改革的决定》（国发〔2015〕2号；自2014年10月1日起实施）：https://www.mohrss.gov.cn/SYrlzyhshbzb/shehuibaozhang/zcwj/yanglao/201505/t20150528_162022.html
- [P02] 民政部《行政区划代码管理办法》（2025年9月1日起施行）：https://www.moj.gov.cn/pub/sfbgw/flfggz/flfggzbmgz/202512/t20251204_528920.html

## 附录C：软件与复现

按下列顺序运行（见随附ZIP中的`README.md`）：

1. `python scripts/prepare_data.py`
2. `python scripts/reproduce.py`
3. `python scripts/test_research.py`
4. 使用已准备的数据与上一版基础数据库，运行`build_workbook.py`生成严格核验版Excel。

所有输出包含抽样边界、来源状态和公式。更多原始数据纳入前需保留旧版本和变更日志。
'''
(OUT/'江西省县域社会结构与社会保障制度实证研究_报告.md').write_text(report,encoding='utf-8')
# PDF 采用经验证的 CID 中文字体；所有核心数字从结果JSON计算
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether,Image
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER,TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
FONT='STSong-Light'; navy=colors.HexColor('#16324F'); muted=colors.HexColor('#4A6075'); pale=colors.HexColor('#F1F5F9');teal=colors.HexColor('#1A7F79')
style={
 'title':ParagraphStyle('cht',fontName=FONT,fontSize=17,leading=25,textColor=navy,spaceAfter=18),
 'subtitle':ParagraphStyle('chsub',fontName=FONT,fontSize=10,leading=16,textColor=muted,spaceAfter=16),
 'heading':ParagraphStyle('chhead',fontName=FONT,fontSize=12,leading=20,textColor=navy,spaceBefore=18,spaceAfter=7,keepWithNext=True),
 'body':ParagraphStyle('chbody',fontName=FONT,fontSize=9.6,leading=17,spaceAfter=9,wordWrap='CJK'),
 'small':ParagraphStyle('chsmall',fontName=FONT,fontSize=8,leading=13,textColor=muted,spaceAfter=7,wordWrap='CJK'),
 'table':ParagraphStyle('chtable',fontName=FONT,fontSize=8.2,leading=13,wordWrap='CJK'),
 'table_header':ParagraphStyle('chtableh',fontName=FONT,fontSize=8.2,leading=13,wordWrap='CJK',textColor=colors.whitesmoke),
 }
P=lambda text,st='body':Paragraph(html.escape(str(text)).replace('\n','<br/>'),style[st])
flow=[]
flow+=[P('江西省县域社会分层与社会保障结构','title'),P('人口变迁、劳动市场与制度分配的实证研究｜2025年阶段性报告｜2026-10-27','subtitle')]
flow+=[P('证据边界：100县级单位已建档，不等于100县各项数据完整。养老金三类金额与人数齐全的仅峡江县（2025原始公报仍待官网终核）；本地原始网页快照暂缺。','small')]
flow+=[P('研究摘要','heading'),P('本报告继承既有江西县域Excel，重新建立来源分级和计算复现链。当前严谨证据层有142条结构化事实、16条来源记录；18个赣州县级行政区具有2024—2025年政府原文人口对照。报告给出养老金分配的可复核算术结果、人口变化残差以及财政预算口径审查；不把少数县案例推成全省结论。')]
flow+=[P('一、数据范围与样本完整性','heading')]
def tbl(head,rows,ws=None):
 contents=[[P(q,'table_header') for q in head]]+[[P(c,'table') for c in row] for row in rows]
 t=Table(contents,colWidths=ws,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),navy),('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,pale]),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),1,teal)]))
 # header style text can't inherit color inside Paragraph; replace first row with modified.
 return t
flow.append(tbl(['核验指标','当前进度','研究判读'],[['行政区名单','100/100','代码按2024版本映射，2025终版待核'],['县级养老金三类金额完整','2/100','峡江、吉安均为公报转载'],['县级金额加领取人数完整','1/100','峡江可计算代理月均'],['赣州人口两年可比','18个县级单位','两年政府原文；功能区单列'],['标准化观测','142条','102条A、40条B；未存源文件快照']],[145,110,250]))
flow.extend([P('二、养老金分配与待遇差距','heading'),P('峡江县2025年三类基本养老保险公布数据如下。按年度发放金额除以年末领取人数所计算的“估算月均”，不是经办部门真实月均养老金。数据仅有署名统计局的转载全文，需县政府原文终核。[S02]')])
pdata=[]
for g in p['groups']:
 pdata.append([g['name'],f"{int(g['recipients_year_end']):,}",f"{g['annual_paid_wanyuan']:,.1f}",share(g['people_share']),share(g['paid_share']),f"{g['monthly_proxy_yuan']:,.0f}"])
flow.append(tbl(['群体','年末人','发放万元','人数比','发放比','月均代理'],pdata,[88,69,93,75,75,105]))
flow.append(P(f"机关事业单位占年末三组领取人数{share(p['groups'][1]['people_share'])}，占年度金额{share(p['groups'][1]['paid_share'])}。其月均估算约为企业{p['groups'][1]['monthly_proxy_yuan']/p['groups'][0]['monthly_proxy_yuan']:.2f}倍、城乡居民{p['groups'][1]['monthly_proxy_yuan']/p['groups'][2]['monthly_proxy_yuan']:.2f}倍。可说明本县三组结构不同，却不能据此估算全省养老金份额。"))
if (FIG/'峡江养老金金额占比_两年对比.png').exists():flow.append(Image(str(FIG/'峡江养老金金额占比_两年对比.png'),width=460,height=215))
flow.extend([P('三、两年变化的精确结构分解','heading'),P(f"峡江三组养老金年度发放从2024年的{pold['total_paid_wanyuan']:,.2f}万元增加至2025年的{p['total_paid_wanyuan']:,.2f}万元，同比约{(p['total_paid_wanyuan']/pold['total_paid_wanyuan']-1)*100:.2f}%。将年度发放额记为A，年末人数记为N，代理均值b=A/N，使用对称分解恒等式：ΔA=ΔN×(b₀+b₁)/2+Δb×(N₀+N₁)/2。下表每一行的两个分量之和严格等于发放额增量，但分量不是政策因果效应。[S02][S03]")])
flow.append(tbl(['群体','增量万元','人数代理分量','人均代理分量'],[[{'enterprise':'企业','public':'机关事业','resident':'城乡居民'}[q['group']],f"{q['annual_paid_growth_wanyuan']:,.1f}",f"{q['year_end_number_component_wanyuan']:,.1f}",f"{q['amount_per_year_end_person_component_wanyuan']:,.1f}"] for q in d],[95,90,158,160]))
flow.extend([P('四、人口与城镇化：两类变量不可混淆','heading'),P(f"峡江2025常住人口减少{abs(dem['change']):,.0f}人，出生与死亡自然差额为{dem['natural_change']:,.0f}人，变动残差{dem['unexplained_residual']:,.0f}人。江西全省减少28万人，出生-死亡约为-8.9万人，未解释余项约-19.1万人。余项可能包含迁移和统计调整，不等于证实的净迁出量。[S01][S02][S03]"),P(f"赣州18个县级建制中2025年人口增加{gz['gain_count']}个、减少{gz['decline_count']}个、持平{gz['unchanged_count']}个；与此同时18县城镇化率均有所提高。不能将县域城镇化率提高推断为总人口增加或人口不外流。[S05][S06]")])
if (FIG/'赣州18县人口增减.png').exists():flow.append(Image(str(FIG/'赣州18县人口增减.png'),width=470,height=270))
flow.extend([P('五、劳动收入与住房保障','heading'),P('江西2025年城镇非私营单位年平均工资99,446元，城镇私营单位57,223元。群体均值差异为42,223元，但行业、职业、教育水平、工龄等混杂因素未控制，不能估计“同岗位工资溢价”。[S11]'),P('2025公积金年度实缴人数353.77万人、缴存总额728.52亿元、提取503.42亿元，缴存/实缴人头/12≈1,716元。其分子包括个人和单位缴存；分母并非全年人月数，不能当个人月工资。[S08]')])
flow.extend([P('六、财政账本与制度史','heading'),P('江西2025年全省社保基金预算执行收入2735.8亿元、支出2603.0亿元；省级2025决算收入1398.9亿元、支出1372.9亿元。二者存在预算层级与执行/决算阶段差异；社保基金又含养老以外险种，不能简单相减计算县级养老金缺口。[S09][S10]'),P('机关事业单位养老保险制度改革依国务院国发〔2015〕2号，自2014年10月1日实施，新老衔接、视同缴费年限、过渡性养老金和职业年金需要分别处理。因此，同一退休年度下的养老金差距不等于制度身份的净因果效应。[P01]')])
flow.extend([P('七、结论与竞争性解释','heading'),P('结论A：养老金总额占比同时由领取人数和估算人均金额共同决定，县级差距存在，但不能推全省。竞争性解释：退休年代、缴费工资、行业人员构成与补发等。'),P('结论B：人口总量变化与城镇化率变化可以方向不同，必须借助分年龄迁移和统计修订识别机制。竞争性解释：城镇化统计变化、人口迁移、城乡人口重分类。'),P('结论C：公积金、养老保险及一般公共财政分别属于不同制度账本；若要讨论财政负担，必须使用同险种分项基金决算及财政补贴明细。')])
flow.extend([P('八、质量审计与待补证据','heading'),P('本研究代码测试通过：100县代码无重复、11市范围、2024/2025养老金加总、代理月均、结构分解闭合、18县政府表对照、人口残差。测试证明算术一致性，不证明未经官方原件核验的转载真伪。'),P('核心限制：（1）2025三类养老金县样本2/100，完整人数仅1县；（2）2025峡江/吉安依赖公报转载；（3）省级市级公积金明细未逐行二次核；（4）原件文件快照与SHA-256尚缺；（5）不足以进行县域因果分析。')])
flow.extend([P('九、后续优先级','heading'),P('1）补齐峡江、吉安县政府官方公报和养老金人月数；2）核对11市公积金原年报附表；3）获取县级同险种基金决算与统筹调剂细目；4）补2025年末民政部行政代码；5）使用年龄、职业和缴费期数据进行真正的可比群体研究。')])
flow.append(P('主要证据与资料索引','heading'))
for source in src:
 label=f"[{source['source_id']}] {source['title']}｜{source['publisher']}。证据等级：{source['grade']}。网址：{source['url']}"
 flow.append(P(label,'small'))
flow.append(P('[P01] 国务院国发〔2015〕2号：https://www.mohrss.gov.cn/SYrlzyhshbzb/shehuibaozhang/zcwj/yanglao/201505/t20150528_162022.html','small'))
flow.append(P('[P02] 民政部《行政区划代码管理办法》：https://www.moj.gov.cn/pub/sfbgw/flfggz/flfggzbmgz/202512/t20251204_528920.html','small'))
pdfpath=OUT/'江西省县域社会分层与社会保障制度_2025实证研究报告.pdf'
def page(canvas,doc):
 canvas.saveState();canvas.setFillColor(muted);canvas.setFont(FONT,8)
 canvas.drawString(42,26,'江西省县域社会分层与保障结构 | 2025阶段性实证研究')
 canvas.drawRightString(A4[0]-43,26,f'{doc.page}')
 canvas.restoreState()
doc=SimpleDocTemplate(str(pdfpath),pagesize=A4,leftMargin=44,rightMargin=44,topMargin=48,bottomMargin=49,author='江西社会保障实证研究',title='江西省县域社会分层与社会保障结构2025研究报告')
doc.build(flow,onFirstPage=page,onLaterPages=page)
print('Markdown',OUT/'江西省县域社会结构与社会保障制度实证研究_报告.md')
print('PDF',pdfpath)