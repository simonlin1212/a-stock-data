# a-stock-data

A 股全栈数据工具包 — 10 层架构 · 44 个端点（41 主端点 + 3 官方备胎）· 15 个数据源 · 零第三方数据封装依赖

一个自包含的 Skill 文件，把分散在 15 个数据源里的 A 股原始数据整合成 AI 编程助手直接能用的工具集。你不用再背 mootdx 的 K 线参数、东财的 PDF Referer 头、iwencai 的 X-Claw 鉴权——全部封装好了。主源被封还有「备用源速查」可降级。

> **V3.5.0 板块资金流向（2026-07-23 · #37）：** 补上此前缺失的**板块级资金流**——新增 `board_fund_flow()`，覆盖行业/概念/地域三类板块 × 今日/5日/10日三周期，主力净流入额/净占比 + 超大/大/中/小单四档明细 + 领涨股。与行业板块排名**同源同接口**（东财 push2 `clist`），此前只请求了价格/涨跌家数，本版补请求 `f62/f184/f66...` 资金流字段即覆盖，走 `em_get` 限流防封。端点 43 → 44。
>
> **V3.4.1 前缀路由 + mootdx 验活修复（2026-07-23 · #40 #41 #43）：** ① **腾讯行情前缀路由**——`5` 开头沪 ETF（`510300`）、沪深指数（`000300`/`000016`）此前误判为 `sz` 返空，`000016` 更被拼成 `sz000016`（*ST康佳A）**静默返回错票**；`get_prefix()` 与 `tencent_quote()` 同步修为 `5x→sh` + 沪指数白名单 + 显式前缀透传；② **`tdx_client()` 真实取数验活**——`_probe` 仅 TCP 握手是假阳性（坏服务器握手通却回 2 字节空 body → 静默空表/崩溃），新增 `_validate()` 每台候选须真实拉一根 K 线成功才用，全败才明确报错；③ **备用源补腾讯 m5 分钟 K 线**——同花顺备胎无 5 分钟，mootdx 一挂即断源（附换手率基点字段坑）。端点/源/层数不变，纯质量修复。
>
> **V3.4.0 接口质量 + 备用源韧性（2026-07-11）：** ① **财联社快讯复活**（#14 收口）——官方 v1 API + 本地签名（`md5(sha1(排序query))`，零 key），V3.2 移除的全市场电报能力恢复，与东财 7×24 互备；② **新增「备用源速查 & 降级策略」**——十层主源→独立备胎速查表 + 3 个官方备胎函数（沪深交易所官方龙虎榜 / 新浪资金流 / 深交所官方+东财公告），东财被封时不同风控面即时降级；③ **两个实测坐实的 bug 修复**——解禁接口东财改列名致 type/shares 恒空（改新列名 + 增 able_shares）、行业排名缺 `fid=f3` 致 top/bottom 非按涨幅排序；④ **深股通标注**——北向盘中披露收紧后 sgt 分钟序列不可靠，权威北向指向 HKEX 官方；⑤ **端点路由速查总表**——60+ 函数首次一页总览，agent 可按需局部读取。端点 40→43，数据源 13→15。
>
> **V3.3.0 新增三层（2026-06-28）：** ① **打板层**（#23 / #15）——东财涨停 / 炸板 / 跌停 / 昨日涨停四池 + 同花顺涨停揭秘（涨停原因题材 / 封板成功率）+ 打板情绪速算（炸板率 / 连板梯队）；② **ETF 期权层**（#13）——50ETF / 300ETF 等期权 T型报价 + 希腊字母 + 隐含波动率（新浪源，免本地算 BSM）；③ **舆情互动层**——互动易问答（公司如何回应投资者）+ 同花顺热榜 + 东财人气榜 + 个股概念命中。另显式补充 ETF 支持说明。端点 28→40，层数 7→10。
>
> **V3.2.5 修复（2026-06-28 · #31 / #28）：** ① **分钟 K 线参数 Bug（CRITICAL）**——`bars()` 参数名误写 `category`（实为 `frequency`），被 `**kwargs` 静默吞掉、永远退化成日线，分钟/周/月线全取不到 → 改正参数名 + 按源码重写频率值表 + 补 1分钟/5分钟示例；② **复权口径**——mootdx `bars` 返回**不复权**原始价，补跨除权日须自行复权的警示；③ **`full_valuation` EPS 取错列**——旧 `iloc[2]` 取的是同花顺「最小值」而非「均值＝机构一致预期EPS」，致 PE_fwd/PEG 系统性偏差 → 改按列名取；④ `em_get()` 加连接级自动重试。
>
> **V3.2.4 修复（2026-06-20 · #26）：** **mootdx 0.11.x 全新安装 BESTIP 空串崩溃**——干净环境裸调 `Quotes.factory()` 抛 `ValueError: not enough values to unpack`（老用户 config 已填 IP 不触发，故易漏测）。新增 `tdx_client()` helper（TCP 探测可用服务器 + 三级 fallback）统一替换 4 处 mootdx 调用，对 0.10/0.11 通用、不锁版本（锁 0.10.12 反而在部分 Python 下 import 崩）。
>
> **V3.2.3 新增（2026-06-20）：** **行业研报**——研报层补上东财行业研报端点 `eastmoney_industry_reports()`，与个股研报同端点（仅 `qType=1`），支持全行业拉取或按东财行业码精确过滤，PDF 复用现有 `download_pdf()`。端点数 27 → 28。
>
> **V3.2.2 修复（2026-06-03）：** ① **概念板块归属（#18）**——百度 PAE `getrelatedblock` 失效（`ResultCode 10003`）→ 改用东财 `slist` 一次拿全个股所属板块（行业/概念/地域 + BK码 + 涨跌幅 + 龙头股）；② **巨潮公告 orgId（#19）**——硬编码 `gssx0{code}` 导致大量 601xxx 股票查不到公告 → 改为动态查官方映射表 `szse_stock.json`（6198 只股）；③ 修复综合示例对已删函数 `baidu_fund_flow_history` 的调用；④ §4.5/§5.1 加大陆住宅 IP 间歇风控说明。
>
> **V3.2（2026-05-30）：** ① **数据源优先级 + 东财防封**——优先用通达信(mootdx)/腾讯（不封 IP），东财仅用于其独有数据，并新增统一节流入口 `em_get()`，所有东财接口内置串行限流（间隔≥1s+随机抖动）+ 会话复用，AI 抄代码即自带防封；② **财联社快讯下线（#14）**——`cls.cn` 旧 API 全面 404，改用东财全球资讯。
>
> **V3.1 修复（2026-05-19）：** 替换 4 个失效接口（百度 PAE 资金流→东财 push2、大宗交易/机构席位报表名更新）+ 修复东财全球资讯和巨潮公告参数变更。
>
> **V3.0 Breaking Change：** 彻底移除 akshare 依赖，所有数据源改为直连 HTTP API。新增资金面/筹码层。

> 兼容 [Claude Code](https://github.com/anthropics/claude-code) · [Codex](https://github.com/openai/codex) · [OpenClaw](https://github.com/anthropics/openclaw)
>
> Skill 文件本质是结构化 Markdown + 内嵌 Python，任何支持上下文注入的 AI 编程助手都能用。

---

## 架构

```
A 股全栈数据 · 十层架构 · V3.5.0
│  （优先级：mootdx/腾讯 不封IP 优先用；东财仅用于独有数据，已内置限流防封）
├── 行情层    mootdx + 腾讯财经 + 百度K线   K线(带MA5/10/20) + 五档盘口 + PE/PB/市值 + 指数/ETF
├── 研报层    东财 reportapi + 同花顺 + iwencai  个股研报 / 行业研报 / PDF下载 / 一致预期 / NL搜索
├── 信号层    同花顺 + 东财                  强势股 + 题材归因 + 北向资金 + 板块归属
│                                           + 资金流向(push2) + 龙虎榜 + 全市场龙虎榜 + 解禁 + 行业对比 + 板块资金流
├── 资金面    东财 datacenter + push2        融资融券 + 大宗交易 + 股东户数 + 分红送转 + 资金流(分钟+120日)
├── 新闻层    东财 + 财联社                  个股新闻 / 财联社电报(✅V3.4复活) / 全球资讯（互备）
├── 基础数据  mootdx + 东财 + 新浪           季报37字段 / F10九大类 / 财报三表
├── 公告层    巨潮 cninfo + mootdx           沪深北全量公告
├── 打板层    东财 push2ex + 同花顺          涨停池 / 炸板 / 跌停 / 昨涨停 / 涨停原因题材 / 连板梯队  ★V3.3
├── 期权层    新浪 hq.sinajs                ETF期权 T型报价 / 希腊字母 / 隐含波动率 IV  ★V3.3
└── 舆情互动  巨潮互动易 + 同花顺 + 东财     互动易问答 / 同花顺热榜 / 东财人气榜 / 概念命中  ★V3.3
```

> ★V3.4 十层之外另附**备用源速查 & 降级策略**：沪深交易所官方 + 新浪 + HKEX——龙虎榜/资金流/公告官方备胎函数 + 各层降级速查表，主源被封时用（见 SKILL.md 对应章节）。

---

## 快速开始

**3 步，2 分钟。**

```bash
# 1. 创建 skill 目录
mkdir -p ~/.claude/skills/a-stock-data

# 2. 把 SKILL.md 放进去
curl -o ~/.claude/skills/a-stock-data/SKILL.md \
  https://raw.githubusercontent.com/simonlin1212/a-stock-data/main/SKILL.md

# 3. 安装依赖（V3.0 不再需要 akshare）
pip install mootdx requests pandas stockstats
```

启动 Claude Code，说一句「帮我看看 688017 的估值」，自动激活。

> **Codex / OpenClaw 用户：** 把 SKILL.md 的内容贴入你的系统 prompt 或项目上下文文件即可，内嵌的 Python 代码可直接执行。

---

## 44 个端点能力清单

> **计数口径：** 下方清单共 46 行，按端点计 44 个——「东财 行业研报」与「东财 reportapi」为**同一端点**（仅 `qType` 参数不同），「同花顺北向（历史）」为本地自缓存（非独立端点），两行不重复计数。

### 行情层（实时，不封 IP）

| 端点 | 数据 |
|------|------|
| mootdx 行情 | K线(多周期) + 五档盘口 + 逐笔成交 + 实时报价 46 字段 |
| 腾讯财经 | PE(TTM) / PB / 总市值 / 流通市值 / 换手率 / 涨跌停价 / 指数 / ETF |
| **百度K线** | 日K线 + MA5/MA10/MA20 均价直接返回（V3.0 新增） |

### 研报层

| 端点 | 数据 |
|------|------|
| 东财 reportapi | 个股研报列表 + 评级 + 三年 EPS 预测 |
| 东财 行业研报 | 行业研报列表（qType=1，同端点）+ 行业名/行业码 + 评级（V3.2.3 新增） |
| 东财 PDF 下载 | 完整研报 PDF（个股/行业通用，已处理 Referer 鉴权） |
| 同花顺一致预期 | 机构一致预期 EPS（直连 basic.10jqka.com.cn） |
| iwencai NL 搜索 | 自然语言跨主题研报检索 |

### 信号层

| 端点 | 数据 |
|------|------|
| 同花顺热点 | 当日强势股 + 题材归因 reason tags（编辑部人工标注） |
| 同花顺北向（实时） | 沪股通分钟级流向（深股通近期上游披露收紧仅供参考，权威北向见 HKEX 备胎） |
| 同花顺北向（历史） | 本地自缓存日级历史 |
| 东财板块归属 | 个股所属全部板块（行业/概念/地域混合）+ BK码 + 当日涨跌幅 + 龙头股（V3.2.2 替换百度 PAE，一次请求拿全）|
| **东财资金流向** | 主力 / 大单 / 中单 / 小单 / 超大单分钟级净流入（V3.1 替换百度 PAE） |
| 龙虎榜席位 | 上榜记录 + 买卖席位 TOP5 + 机构动向 |
| 全市场龙虎榜 | 每日全市场上榜股票 + 净买额排名 + 上榜原因 |
| 限售解禁日历 | 历史解禁 + 未来 90 天待解禁预警 |
| **行业板块排名** | 东财行业涨跌/上涨下跌家数（V3.0 替换同花顺，零鉴权） |
| **板块资金流向** | 行业/概念/地域 × 今日/5日/10日 主力净流入额/净占比 + 超大/大/中/小单四档 + 领涨股（V3.5 新增，与行业排名同源）|

### 资金面 / 筹码层（V3.0 新增）

| 端点 | 数据 |
|------|------|
| **融资融券明细** | 日级融资余额/买入/偿还 + 融券余额/卖出/偿还 |
| **大宗交易** | 成交价/量 + 买卖方营业部 + 溢价率 |
| **股东户数变化** | 季度股东数 + 环比变化 + 户均持股（筹码集中度） |
| **分红送转历史** | 每股派息/送股/转增 + 进度状态 |
| **个股资金流120日** | 主力/大单/中单/小单日级净流入 |

### 新闻层

| 端点 | 数据 |
|------|------|
| 个股新闻 | 东财个股新闻流（直连 search-api-web） |
| 财联社电报 | 全市场实时快讯（v1 API + 本地签名零 key，✅V3.4.0 复活，与全球资讯互备） |
| 全球资讯 | 东财全球财经资讯（直连 np-weblist，7×24） |

### 基础数据 + 公告

| 端点 | 数据 |
|------|------|
| 季报快照 | 37 字段（EPS / ROE / 净利润 / 主营收入...） |
| F10 公司资料 | 9 大类文本（截断优化，-70% token） |
| 东财个股信息 | 行业/总股本/流通股/市值/上市日期（直连 push2） |
| 新浪财报三表 | 资产负债表/利润表/现金流量表（直连 quotes.sina.cn） |
| 巨潮公告 | 沪深北交所全量公告 |

### 打板层（V3.3 新增）

| 端点 | 数据 |
|------|------|
| 东财涨停池 | 连板数 / 几天几板 / 封板资金 / 炸板次数 / 首末封板时间 / 所属行业 |
| 东财炸板池 | 曾涨停后开板 + 振幅 / 涨速 |
| 东财跌停池 | 封单资金 / 连续跌停天数 / 开板次数 / 板上成交额 |
| 东财昨日涨停池 | 昨涨停今表现（自算晋级率 / 赚钱效应） |
| 同花顺涨停揭秘 | 涨停原因题材 / 封板成功率 / 一字·换手·T字板 / 封单额 |

### ETF 期权层（V3.3 新增）

| 端点 | 数据 |
|------|------|
| 期权合约清单 | 50ETF / 300ETF / 科创50ETF / 500ETF 各月份认购认沽合约 |
| T型报价 | 买卖五档 / 持仓量 / 行权价 / 最新价 / 成交量额 |
| 希腊字母 + IV | Delta / Gamma / Theta / Vega / 隐含波动率 / 理论价值（交易所预算，免本地算 BSM） |

### 舆情互动层（V3.3 新增）

| 端点 | 数据 |
|------|------|
| 互动易问答 | 投资者提问 + 公司官方回复（AI 问答独家信源：公司如何回应某传闻/利好） |
| 同花顺热榜 | 人气值 / 概念标签 / 排名变化 |
| 东财人气榜 | 排名 + 排名变化 + 名称价格 |
| 东财个股概念命中 | 这只票当下被市场归到哪些概念在炒 + 热度值 |

### 备用源（V3.4 新增 · 主源被封时降级）

| 端点 | 数据 |
|------|------|
| 官方龙虎榜备胎 | 上交所 + 深交所官方接口，零鉴权权威一手，含营业部席位（东财被封时用） |
| 资金流备胎 | 新浪日度四档单净额（超大/大/中/小单 + 净流入） |
| 公告备胎 | 深市走深交所官方、沪市走东财，均带 PDF 直链（巨潮被封时用） |

> 另附**十层主源 → 独立备胎速查表**（交易所官方 / 同花顺 F10 / HKEX / 巨潮 webapi / 金十等，全部不同风控面）与「已死透别用」名单，见 SKILL.md「备用源速查 & 降级策略」章节。

### 鉴权要求

除 iwencai 外，其余所有数据源**完全免费无 Key**。仅 iwencai 语义搜索需要 API Key（[申请地址](https://www.iwencai.com/skillhub)）。

---

## 使用示例

跟你的 AI 助手说这些话就能激活：

| 场景 | 说什么 |
|------|--------|
| 个股估值 | 「帮我估一下 688017，给我 PE / PEG / 消化时间」 |
| 题材归因 | 「今天哪些股票走强，主要是什么题材」 |
| 研报检索 | 「人形机器人产业链最近的研报，特别是丝杠和减速器」 |
| 北向资金 | 「今天北向资金流入流出怎么样」 |
| 概念板块 | 「688017 属于哪些概念板块」 |
| 资金流向 | 「000858 今天主力资金流入还是流出」 |
| 龙虎榜 | 「002475 最近上过龙虎榜吗，哪些营业部在买」 |
| 全市场龙虎榜 | 「今天龙虎榜哪些票净买入最多」 |
| 解禁预警 | 「这只股票未来 3 个月有没有限售解禁」 |
| 行业轮动 | 「今天哪些行业涨幅最大」 |
| **板块资金流** | 「今天主力资金在流入哪些行业/概念板块，近 5 日趋势呢」 |
| 融资融券 | 「600519 最近的融资余额变化趋势」 |
| 大宗交易 | 「这只票最近有没有大宗交易，溢价还是折价」 |
| 股东户数 | 「000858 股东户数在增加还是减少，筹码集中吗」 |
| 分红送转 | 「茅台历年分红派息多少」 |
| **ETF 行情** | 「510050 上证50ETF 现在什么价、今天涨跌多少」 |
| **涨停打板** | 「今天涨停多少家、最高几连板、炸板率多少」 |
| **涨停归因** | 「今天涨停的票都是什么题材，哪些是几天几板」 |
| **ETF 期权** | 「50ETF 平值期权的隐含波动率和 Delta 是多少」 |
| **互动易** | 「比亚迪最近投资者都在问什么，公司怎么回应的」 |
| **市场热度** | 「今天哪些票最热门，被归到什么概念在炒」 |
| 新闻公告 | 「拉一下 300476 最近的新闻和公告」 |
| **市场快讯** | 「用财联社电报看看现在市场上有什么大新闻」 |
| 批量对比 | 「帮我对比这 5 只半导体股的估值」 |

### 内置 4 套调研流程

| 流程 | 做什么 | 耗时 |
|------|--------|------|
| 单票估值 | 实时价 → 一致预期 EPS → 前向 PE / PEG / PE 消化年数 | 30 秒 |
| 批量对比 | 多只股票横向估值排列 | 1 分钟 |
| 主题研报 | iwencai 多关键词 NL 搜索 + 东财 PDF 交叉补充 | 2 分钟 |
| 新标的调研 | 机构覆盖 → 估值 → 概念板块 → 资金流向 → 龙虎榜 → 解禁 → 两融 | 1 分钟 |

---

## V3.4.0 亮点

| 变化 | 说明 |
|------|------|
| **财联社快讯复活（#14 收口）** | 2026-05 死的是旧 `nodeapi` 系接口；官方新版 `v1/roll/get_roll_list` 一直可用，只是强制 `sign` 校验——sign 纯本地可算（`md5(sha1(按 key 字典序拼接的 query 串))`），零 key。全市场电报能力恢复，与东财 7×24 互为独立备份（不同源、不同风控面） |
| **备用源速查 & 降级策略（新增章节）** | 十层主源→独立备胎速查表（交易所官方 / 新浪 / 同花顺 F10 / HKEX / 巨潮 webapi / 金十，全部不同域名不同风控面）+「已死透别用」名单。东财 IP 级风控成片失联时即时降级 |
| **3 个官方备胎函数** | `dragon_tiger_backup()`（沪深交易所官方龙虎榜，零鉴权权威一手，含营业部席位）、`fund_flow_backup()`（新浪日度四档单净额）、`announcements_backup()`（深市深交所官方 / 沪市东财，均带 PDF 直链）。全部 2026-07-11 真实数据实测 |
| **解禁接口字段修复** | 东财 `RPT_LIFT_STAGE` 改列名致 `type`/`shares` 恒空 → 改 `FREE_SHARES_TYPE`/`FREE_SHARES`，新增 `able_shares`（实际可流通股数，更贴近真实抛压） |
| **行业排名排序修复** | clist 请求缺排序字段，top/bottom 切片并非按涨幅排序 → 补 `fid=f3`，现按涨跌幅真实降序 |
| **深股通标注** | 北向盘中披露收紧后 sgt 分钟序列不可靠（hgt 可用），权威北向用 HKEX 官方日统计（备胎表内） |
| **端点路由速查总表** | § → 函数 → 用途 → 源，60+ 内嵌函数首次一页总览；agent 可按表定位章节局部读取，不必通读全文 |
| **端点 40 → 43，数据源 13 → 15** | 新增沪深交易所官方两个一手信源；FAQ 新增东财被封三步处理 / 财联社复活 / mootdx 库烂尾说明 |

> 历史版本亮点见 [CHANGELOG.md](./CHANGELOG.md)。

---

## 数据源优先级（V3.2 重排，按封 IP 风险）

> **原则：行情/K线/实时价/市值/财务能从 mootdx 或腾讯拿到的，一律优先用它们（不封 IP）。东财只用于它独有、别处拿不到的数据，且全部走 `em_get()` 内置限流。**

| 优先级 | 数据源 | 协议 | 封 IP 风险 | 用途 |
|--------|--------|------|-----------|------|
| **1（首选）** | mootdx（通达信） | TCP 7709 | **不封 IP** | K线/五档/逐笔/财务快照/F10 |
| **2（首选）** | 腾讯财经 | HTTP | **不封 IP** | 实时价/PE/PB/市值/换手率/涨跌停/指数/ETF |
| 3 | 同花顺热点/北向 | HTTP | 极低（零鉴权） | 强势股/题材归因/北向资金 |
| 4 | 百度股市通 | HTTP | 极低 | K线（带 MA5/10/20）|
| 5 | 新浪财经 | HTTP | 低 | 财报三表 |
| 6 | 巨潮 cninfo | HTTP | 低 | 公告全文 |
| 7 | 同花顺一致预期 | HTTP | 低（需 UA） | EPS 一致预期 |
| 8 | iwencai | OpenAPI | 低（需 Key） | NL 语义搜索 |
| **末位（仅独有数据）** | **东财** datacenter/push2/reportapi/search/np-weblist | HTTP | **中 — 有风控会封 IP** | 龙虎榜/解禁/两融/大宗/股东户数/分红/资金流/研报/个股新闻/全球资讯（已统一走 `em_get()` 限流） |

> **架构原则：** 除 mootdx（TCP 二进制协议）外，全部直连 HTTP API，零第三方数据封装依赖。**东财系接口有访问频率风控，所有调用统一经 `em_get()` 串行限流防封；批量任务请调大 `EM_MIN_INTERVAL`。**
>
> **降级原则（V3.4 新增）：** 任一主源被封/失效时，查 SKILL.md「备用源速查 & 降级策略」——每类数据都备有一条**不同域名、不同风控面**的独立备胎（沪深交易所官方 / 新浪 / 同花顺 / HKEX），东财被封时它们不受牵连。

---

## FAQ

**Q: SKILL.md 这么大，agent 每次加载很费 token？**
单文件自包含是本项目的**有意产品决策**——拷一个文件就能用、离线可携、便于分发，这个形态会长期保持，不做目录化拆分（相关讨论见 #21 / #22 / #29）。两个降耗建议：① v3.3.1 起 description 已收窄触发范围，无需取数的 A 股话题不会再误加载整个文件；② token 敏感的用户可以不把它装成自动触发 skill，改为放进项目目录、需要取数时让 agent 按需读取——文件按十层组织、章节标题清晰，v3.4.0 起顶部还有「端点路由速查」总表（§→函数→用途→源），agent 按表定位后只读对应层，通常只花几 K token。

**Q: 东财接口 403 / 连接重置，是被封了怎么办？**
东财系接口（datacenter/push2/push2ex/reportapi/search/np-weblist）共用同一套风控，IP 被封会成片失联。三步：① 停止请求等 30-60 分钟（IP 级临时封通常自动解除），或换网络（手机热点）立刻恢复；② 长批任务确认全部走 `em_get()` 并调大 `EM_MIN_INTERVAL`；③ 数据不能等 → 用 SKILL.md「备用源速查 & 降级策略」的独立备胎（交易所官方/新浪/同花顺，不同风控面）。

**Q: 财联社快讯不是 V3.2 标注下线了吗？**
已复活（V3.4.0）。2026-05 死的是旧 `nodeapi` 系接口；官方新版 `v1/roll/get_roll_list` 一直可用，只是强制 `sign` 校验——sign 纯本地可算（`md5(sha1(按 key 字典序拼接的 query 串))`），零 key。与东财 7×24 全球资讯互为独立备份。

**Q: mootdx 库听说停更了，还能用吗？**
库确实烂尾（最后 commit 2024-07，BESTIP bug 无官方修复），但**通达信 TCP 协议本身照常运行**——烂尾的是封装库，不是数据源。内置的 `tdx_client()` 已绕开 BESTIP bug，继续用没问题；若未来装不上，社区活跃替代是 easy_tdx（同协议）。

**Q: `pip install mootdx` 把 httpx 降到 0.25.2，和 MCP（要 httpx≥0.27.1）冲突？（#30）**
mootdx 上游锁了 `httpx<0.26`，与 MCP 等工具的 `httpx≥0.27` 硬冲突，skill 层改不动它的依赖声明。但**可以绕过**——关键点：**mootdx 取行情走的是 TCP 二进制协议（通达信 7709 端口），运行时根本不经过 httpx**，`httpx<0.26` 只是它声明的一个用不到的保守上限。两个务实解法：
> 1. **`--no-deps` 升 httpx（推荐）**：装完 mootdx 后 `pip install --no-deps "httpx>=0.27.1"`，既满足 MCP，mootdx 也照常工作。pip 会留一条 incompatible 警告，但不影响运行（实测 mootdx 0.11.7 在 httpx 0.28.1 下取数正常）。
> 2. **独立 venv 隔离**：把跑 mootdx 的部分和跑 MCP 的主环境分到不同 venv，彻底互不干扰。

**Q: mootdx 和腾讯有什么区别？**
互补。mootdx = 交易层（价格 + 盘口 + K 线），腾讯 = 估值层（PE / PB / 市值 / 换手率 / 涨跌停价）。两者都不封 IP。

**Q: 在海外服务器跑，mootdx 超时？**
mootdx 走 TCP 直连通达信行情服务器，需国内 IP 才稳定。海外环境建议走代理或切换到 yfinance。

**Q: 腾讯 API 字段 43 是 PB 吗？**
不是。43 = 振幅%，46 = PB。网上大量教程写错了，这里是实测校准结果。

**Q: V3.0 为什么移除 akshare？**
akshare 本质是对东财/同花顺/新浪等公开 API 的封装，中间层增加了故障点（版本兼容 bug、pandas 3.0 ArrowInvalid 等）。V3.0 直连底层 HTTP API，零中间依赖，更稳定可控。

**Q: 行业板块为什么从同花顺换成东财？**
同花顺 `stock_board_industry_summary_ths` 接口 2026 年初加了反爬 401。东财 push2 行业板块（`m:90+t:2`）是完美替代，零鉴权且字段更丰富。

**Q: iwencai 返回 401？**
检查：(1) API Key 有效性 (2) 是否携带了 X-Claw-* Headers。SkillHub 2.0 后强制要求。

**Q: 同花顺热点 reason 字段为空？**
盘后数据还没更新，15:30 之后再调。个别 ST 股没有人工标注，`dropna` 过滤即可。

**Q: 百度股市通 ResultCode 不稳定？**
已知坑——有时返回 int `0`，有时返回 string `"0"`。代码里用 `str()` 统一比较即可。

**Q: 东财资金流/个股新闻偶尔返回空或 HTTP 000？（#18）**
部分**大陆住宅宽带 IP** 会被东财 push2/search-api 连接级间歇风控（表现 `HTTP 000` 连接被拒、或新闻只返回 `passportWeb` 无文章）。**这不是代码问题**——同一代码在其他网络/时段实测正常。对策：隔几分钟重试、换网络环境（手机热点）、调大 `EM_MIN_INTERVAL` 降频。日级资金流也可用 mootdx 量价数据务实替代。

**Q: 北向资金历史只有几天？**
V2.1 改为本地自缓存。每次调用自动积累，越跑越丰富。首次运行只有当天数据。

**Q: 不用 Claude Code，能用吗？**
能。SKILL.md 本质是 Markdown + 内嵌 Python 代码。Codex、OpenClaw 或任何 AI 编程助手都能读取。你也可以直接把 Python 代码段复制出来在自己的脚本里跑。

---

## 更新日志

见 [CHANGELOG.md](./CHANGELOG.md)。

---

## Donate

如果这个工具帮到了你的投研工作流，欢迎请作者喝杯咖啡 ☕

<p align="center">
  <img src="./assets/wechat-sponsor.jpg" width="240" alt="微信赞赏码">
</p>
<p align="center">
  <a href="https://ifdian.net/a/simonlin">爱发电</a> ·
  <a href="https://buymeacoffee.com/simonlin1212">Buy Me a Coffee</a>
</p>

> 想要什么数据端点？欢迎开 [Issue](https://github.com/simonlin1212/a-stock-data/issues) 提需求，赞助者的 Issue 优先处理。

---

## Disclaimer

本项目仅提供数据获取工具，不构成任何投资建议。股市有风险，投资需谨慎。

---

## License

[Apache License 2.0](./LICENSE) — 自由使用，注明出处即可。

**作者：** Simon 林 · 抖音「Simon林」 · 公众号「硅基世纪」

---

<details>
<summary><b>🇬🇧 English</b></summary>

# a-stock-data

Full-stack data toolkit for China A-Share market — 10-layer architecture · 44 endpoints (41 primary + 3 official backups) · 15 data sources · zero third-party data wrapper dependencies

A self-contained Skill file that consolidates raw A-share data from 15 sources into a ready-to-use toolkit for AI coding assistants. No need to memorize mootdx candlestick parameters, Eastmoney PDF Referer headers, or iwencai X-Claw authentication — it's all handled. And when a primary source bans you, there's a backup-source quick reference to fall back on.

> **V3.5.0 — board-level fund flow (2026-07-23 · #37):** Fills the previously-missing **sector fund flow** gap — new `board_fund_flow()` covering industry / concept / region boards × today / 5-day / 10-day, with main net inflow amount & ratio + super-large/large/medium/small tiers + leading stock. Same endpoint as the industry ranking (Eastmoney push2 `clist`) — it previously only requested price/advance-decline fields; this version adds the `f62/f184/f66...` fund-flow fields. Throttled via `em_get`. Endpoints 43 → 44.
>
> **V3.4.1 — prefix routing + mootdx validation fixes (2026-07-23 · #40 #41 #43):** ① **Tencent quote prefix routing** — 5-prefixed Shanghai ETFs (`510300`) and SH/SZ indices (`000300`/`000016`) were mis-routed to `sz` (empty), and `000016` was built as `sz000016` (*ST Konka A) **silently returning the wrong stock's data**; `get_prefix()` and `tencent_quote()` both fixed to `5x→sh` + SH-index whitelist + explicit `sh/sz/bj` prefix passthrough. ② **`tdx_client()` real-fetch validation** — `_probe` only did a TCP handshake (false positive: a broken server can handshake yet return a 2-byte empty body → silent empty DataFrame / crash); added `_validate()` requiring each candidate to actually fetch one K-line before use, with an explicit error only when all fail. ③ **Backup source adds Tencent m5 minute K-line** — the Tonghuashun backup has no 5-min bars, so mootdx going down left no 5-min source (field pitfall documented: the 7th field is turnover-rate basis points, not amount). Endpoint/source/layer counts unchanged — quality-only patch.
>
> **V3.4.0 — endpoint quality + backup-source resilience (2026-07-11):** ① **Cailianpress flash revived** (#14 closed) — official v1 API + locally-computed signature (`md5(sha1(sorted query))`, zero key); the market-wide flash removed in V3.2 is back, an independent backup to Eastmoney 7×24. ② **New "backup sources & fallback" section** — a per-layer primary→backup table + 3 official backup functions (SSE/SZSE official dragon-tiger, Sina fund flow, SZSE-official + Eastmoney announcements) on different rate-limit planes, for instant fallback when Eastmoney bans your IP. ③ **Two verified bug fixes** — lockup-expiry columns renamed upstream leaving `type`/`shares` empty (new column names + `able_shares`), and industry ranking missing `fid=f3` so top/bottom weren't sorted by change. ④ **Shenzhen Connect caveat** — sgt minute series unreliable after the disclosure tightening; authoritative northbound now points to HKEX official. ⑤ **Endpoint routing table** — first one-page overview of 60+ functions for partial reads. Endpoints 40→43, data sources 13→15.
>
> **V3.3.0 — three new layers (2026-06-28):** ① **Limit-Up layer** (#23/#15) — Eastmoney limit-up/break/limit-down/prev-day pools + THS limit-up insight (reasons/seal rate) + sentiment quick-calc (break rate/board ladder); ② **ETF Options layer** (#13) — 50ETF/300ETF option T-quotes + Greeks + implied vol (Sina, no local BSM); ③ **Sentiment layer** — investor Q&A (how companies respond to investors) + THS hot list + EM popularity rank. Plus an explicit ETF-support note. Endpoints 28→40, layers 7→10.
>
> **V3.2.5 Fix (2026-06-28 · #31 / #28):** ① **Minute K-line parameter bug (CRITICAL)** — `bars()` used a non-existent param name `category` (the real one is `frequency`); it got silently swallowed by `**kwargs`, so `frequency` always defaulted to 9 (daily) and minute/weekly/monthly requests silently degraded to daily with no error. Fixed the param name, rewrote the frequency table from mootdx source, added 1-min/5-min examples. ② **Adjustment** — mootdx `bars` returns **unadjusted** raw prices; added a warning to adjust manually across ex-dividend dates. ③ **`full_valuation` read the wrong EPS column** — old `iloc[2]` picked the THS "min" column instead of "mean = consensus EPS", biasing PE_fwd/PEG → now picks by column name. ④ `em_get()` now has connection-level retry.
>
> **V3.2.4 Fix (2026-06-20 · #26):** **mootdx 0.11.x fresh-install BESTIP crash** — on a clean machine a bare `Quotes.factory()` throws `ValueError: not enough values to unpack` (existing users whose config already holds IPs never hit it, so it was easy to miss). Added a `tdx_client()` helper (TCP-probes a built-in server list + 3-level fallback) and routed all 4 mootdx calls through it; works on 0.10/0.11 with no version pin (pinning 0.10.12 actually crashes on import under some Pythons).
>
> **V3.2.3 New (2026-06-20):** **Industry reports** — added the Eastmoney industry-report endpoint `eastmoney_industry_reports()` to the research layer. Same endpoint as single-stock reports (only `qType=1`); pull all industries or filter by an Eastmoney industry code, PDF download reuses the existing `download_pdf()`. Endpoints 27 → 28.
>
> **V3.2.2 Fix (2026-06-03):** ① **Sector/concept membership (#18)** — Baidu PAE `getrelatedblock` is dead (`ResultCode 10003`) → switched to Eastmoney `slist`, fetching all of a stock's sectors (industry/concept/region + BK code + change% + leading stock) in one request. ② **cninfo filing orgId (#19)** — hardcoded `gssx0{code}` made many 601xxx tickers return zero filings → now resolves the real orgId dynamically from the official map `szse_stock.json` (6198 stocks). ③ Fixed a crash in the combined example calling the removed `baidu_fund_flow_history`. ④ Added notes on intermittent Eastmoney throttling for some mainland residential IPs.
>
> **V3.2 (2026-05-30):** ① **Data-source priority + Eastmoney anti-ban** — prefer mootdx (TDX) / Tencent (never IP-banned); use Eastmoney only for its exclusive data, all routed through a new throttled `em_get()` (serial rate-limit ≥1s + jitter + session reuse) so copied code is ban-safe by default. ② **Cailianpress (cls.cn) deprecated (#14)** — old API returns 404, replaced by Eastmoney global news.
>
> **V3.1 Fix (2026-05-19):** Replaced 4 broken endpoints (Baidu PAE fund flow → Eastmoney push2, block trade/institution report name updates) + fixed Eastmoney global news and cninfo filing parameter changes.
>
> **V3.0 Breaking Change:** Completely removed akshare dependency. All data sources now use direct HTTP API calls. Added capital flow / ownership layer.

> Compatible with [Claude Code](https://github.com/anthropics/claude-code) · [Codex](https://github.com/openai/codex) · [OpenClaw](https://github.com/anthropics/openclaw)
>
> The Skill file is structured Markdown + embedded Python. Any AI coding assistant with context injection can use it.

---

## Architecture

```
China A-Share Full-Stack Data · 10-Layer Architecture · V3.5.0
│  (Priority: prefer mootdx/Tencent — never IP-banned; Eastmoney only for exclusive data, with built-in throttling)
├── Market Data    mootdx + Tencent + Baidu K-line   Candlesticks (w/ MA5/10/20) + Order Book + PE/PB + Index/ETF
├── Research       Eastmoney + THS + iwencai          Stock reports / Industry reports / PDF / Consensus EPS / NL search
├── Signals        THS + Eastmoney                    Hot stocks + Sector attribution + Northbound flow
│                                                     + Sector membership + Fund flow(push2) + Dragon Tiger + Lockup + Industry + Board fund flow
├── Capital Flow   Eastmoney datacenter + push2       Margin trading + Block trades + Holder count + Dividends + Fund flow(min+120d)
├── News           Eastmoney + Cailianpress           Stock news / CLS flash (✅revived in V3.4) / Global finance (mutual backup)
├── Fundamentals   mootdx + Eastmoney + Sina          37-field quarterly + F10 9 categories + Financial statements
├── Filings        cninfo + mootdx                    Full filings across SSE / SZSE / BSE
├── Limit-Up       Eastmoney push2ex + THS            ZT/ZB/DT/prev-ZT pools / limit reasons / consecutive-board ladder  ★V3.3
├── Options        Sina hq.sinajs                     ETF option T-quotes / Greeks / implied volatility  ★V3.3
└── Sentiment      cninfo IRM + THS + Eastmoney       Investor Q&A / hot lists / popularity rank / concept hits  ★V3.3
```

> ★V3.4 On top of the 10 layers there is now a **Backup Sources & Fallback Strategy** appendix: SSE/SZSE official + Sina + HKEX — official backup functions (dragon-tiger / fund flow / filings) + a per-layer fallback table for when a primary source bans you (see the corresponding SKILL.md section).

---

## Quick Start

**3 steps, 2 minutes.**

```bash
# 1. Create skill directory
mkdir -p ~/.claude/skills/a-stock-data

# 2. Download SKILL.md
curl -o ~/.claude/skills/a-stock-data/SKILL.md \
  https://raw.githubusercontent.com/simonlin1212/a-stock-data/main/SKILL.md

# 3. Install dependencies (V3.0: akshare no longer needed)
pip install mootdx requests pandas stockstats
```

Launch Claude Code and say "Check the valuation of 688017" — the skill activates automatically.

> **Codex / OpenClaw users:** Paste the contents of SKILL.md into your system prompt or project context file. The embedded Python code is ready to execute.

---

## 44 Endpoints

> **Counting convention:** the tables below have 46 rows but count as 44 endpoints — "Eastmoney Industry Reports" shares **the same endpoint** as "Eastmoney reportapi" (only the `qType` parameter differs), and "THS Northbound (historical)" is a local self-built cache (not a separate endpoint); neither is double-counted.

### Market Data (real-time, no IP ban)

| Endpoint | Data |
|----------|------|
| mootdx Market Data | Candlesticks (multi-period) + Level-2 order book + tick-by-tick + 46-field quote |
| Tencent Finance | PE(TTM) / PB / Market Cap / Float Cap / Turnover / Price Limits / Index / ETF |
| **Baidu K-line** | Daily K-line + MA5/MA10/MA20 moving averages included (V3.0 new) |

### Research Reports

| Endpoint | Data |
|----------|------|
| Eastmoney reportapi | Single-stock report list + ratings + 3-year EPS forecasts |
| Eastmoney Industry Reports | Industry report list (qType=1, same endpoint) + industry name/code + rating (V3.2.3) |
| Eastmoney PDF | Full research report PDF, stock & industry (Referer auth handled) |
| THS Consensus EPS | Institutional consensus EPS (direct basic.10jqka.com.cn) |
| iwencai NL Search | Natural language cross-topic report search |

### Signals

| Endpoint | Data |
|----------|------|
| THS Hot Stocks | Today's strong stocks + sector attribution tags (editorial annotations) |
| THS Northbound (real-time) | Shanghai Connect minute-level flow (Shenzhen Connect unreliable since upstream disclosure tightening — see HKEX backup for authoritative data) |
| THS Northbound (historical) | Local self-cached daily history |
| Eastmoney Sector Membership | All sectors a stock belongs to (industry/concept/region mixed) + BK code + daily change + leading stock (V3.2.2, replaced Baidu PAE, one request) |
| **Eastmoney Fund Flow** | Main / Large / Medium / Small / Super-large order minute-level net inflow (V3.1, replaced Baidu PAE) |
| Dragon Tiger Board | Appearance records + Top 5 buy/sell brokerages + institutional activity |
| Daily Dragon Tiger (Full Market) | All stocks on daily board + net buy ranking + appearance reasons |
| Lockup Expiry Calendar | Historical releases + 90-day upcoming expiry alerts |
| **Industry Ranking** | Eastmoney industry change/up/down counts (V3.0, replaced THS 401) |
| **Board Fund Flow** | Industry/concept/region × today/5d/10d main net inflow & ratio + super-large/large/medium/small tiers + leading stock (V3.5, same endpoint as Industry Ranking) |

### Capital Flow / Ownership (V3.0 New)

| Endpoint | Data |
|----------|------|
| **Margin Trading** | Daily margin balance / buy / repay + short selling balance |
| **Block Trades** | Deal price/volume + buyer/seller brokerages + premium rate |
| **Shareholder Count** | Quarterly holder count + QoQ change + avg shares per holder |
| **Dividend History** | Per-share cash dividend / bonus shares / transfer shares |
| **120-Day Fund Flow** | Main / large / medium / small order daily net inflow |

### News

| Endpoint | Data |
|----------|------|
| Stock News | Eastmoney per-stock news (direct search-api-web) |
| CLS Flash | Market-wide real-time flash (v1 API + local signature, zero key, ✅revived in V3.4.0, mutual backup with Global News) |
| Global News | Eastmoney global finance news (direct np-weblist, 7×24) |

### Fundamentals + Filings

| Endpoint | Data |
|----------|------|
| Quarterly Snapshot | 37 fields (EPS / ROE / Net Profit / Revenue...) |
| F10 Company Data | 9 categories (truncation optimization, -70% tokens) |
| Eastmoney Stock Info | Industry / total shares / float / market cap / listing date (direct push2) |
| Sina Financial Statements | Balance sheet / Income statement / Cash flow (direct quotes.sina.cn) |
| cninfo Filings | Full filings across all exchanges |

### Limit-Up / Limit-Down (V3.3 new)

| Endpoint | Data |
|----------|------|
| EM Limit-Up Pool | Consecutive boards / N-day-M-board / seal fund / break count / seal time / industry |
| EM Break-Board Pool | Opened after limit-up + amplitude / speed |
| EM Limit-Down Pool | Seal fund / consecutive limit-down / open count / board turnover |
| EM Prev-Day Limit-Up Pool | Yesterday's limit-up performance today (promotion rate / profit effect) |
| THS Limit-Up Insight | Limit reason themes / seal success rate / board type / seal amount |

### ETF Options (V3.3 new)

| Endpoint | Data |
|----------|------|
| Option Contract List | 50ETF / 300ETF / STAR50 ETF / 500ETF call & put contracts by month |
| T-Quote | Bid/ask 5 levels / open interest / strike / last / volume |
| Greeks + IV | Delta / Gamma / Theta / Vega / implied vol / theoretical value (exchange-computed, no local BSM) |

### Sentiment & Interaction (V3.3 new)

| Endpoint | Data |
|----------|------|
| Investor Q&A (IRM) | Investor questions + official company replies (unique source: how a company responds to rumors/news) |
| THS Hot List | Popularity / concept tags / rank change |
| EM Popularity Rank | Rank + rank change + name/price |
| EM Stock Concept Hits | Which concepts the market is grouping this stock under + heat |

### Backup Sources (V3.4 new · fallback when a primary source bans you)

| Endpoint | Data |
|----------|------|
| Official Dragon-Tiger Backup | SSE + SZSE official APIs, zero-auth, authoritative first-party, incl. brokerage seats (when Eastmoney is banned) |
| Fund Flow Backup | Sina daily 4-tier order net flow (super-large / large / medium / small + net inflow) |
| Filings Backup | SZSE official for Shenzhen tickers, Eastmoney for Shanghai, both with direct PDF links (when cninfo is banned) |

> Plus a **per-layer primary → independent-backup table** (exchange official / THS F10 / HKEX / cninfo webapi / Jin10 — all on different rate-limit planes) and a "confirmed dead" list — see the "Backup Sources & Fallback Strategy" section in SKILL.md.

### Authentication

All data sources except iwencai are **completely free, no API key needed**. Only iwencai semantic search requires an API key ([apply here](https://www.iwencai.com/skillhub)).

---

## Usage Examples

Just tell your AI assistant:

| Scenario | Prompt |
|----------|--------|
| Valuation | "Estimate 688017 — give me PE / PEG / payback period" |
| Sector Attribution | "Which stocks are strong today and what sectors are driving them" |
| Research Reports | "Latest reports on humanoid robot supply chain, especially ball screws and reducers" |
| Northbound Flow | "How's northbound capital flow looking today" |
| Concept Blocks | "What concept sectors does 688017 belong to" |
| Fund Flow | "Is institutional money flowing into or out of 000858 today" |
| Dragon Tiger Board | "Has 002475 appeared on the dragon tiger board recently, which brokerages are buying" |
| Daily Dragon Tiger | "Which stocks had the highest net buy on today's dragon tiger board" |
| Lockup Expiry | "Any lockup expiries coming up in the next 3 months for this stock" |
| Industry Rotation | "Which industries are up the most today, where is money flowing" |
| Margin Trading | "What's the recent trend in margin balance for 600519" |
| Block Trades | "Any recent block trades for this stock, premium or discount" |
| Shareholder Count | "Is 000858 shareholder count increasing or decreasing" |
| Dividends | "How much has Moutai paid in dividends over the years" |
| ETF Quote | "What's the price of 510050 (SSE 50 ETF) and today's change" |
| Limit-Up Sentiment | "How many stocks hit limit-up today, highest consecutive boards, break rate" |
| Limit-Up Themes | "What themes drove today's limit-ups, which are multi-day boards" |
| ETF Options | "What's the implied vol and Delta of the at-the-money 50ETF option" |
| Investor Q&A | "What are investors asking BYD recently and how did the company respond" |
| Market Heat | "Which stocks are hottest today and what concepts are they grouped under" |
| News & Filings | "Pull recent news and filings for 300476" |
| Market Flash | "Any big market news right now on the CLS flash feed" |
| Batch Compare | "Compare valuations of these 5 semiconductor stocks" |

### 4 Built-in Research Workflows

| Workflow | What it does | Time |
|----------|-------------|------|
| Single Stock Valuation | Live price → Consensus EPS → Forward PE / PEG / PE payback years | 30 sec |
| Batch Comparison | Side-by-side valuation ranking | 1 min |
| Thematic Research | iwencai multi-keyword NL search + Eastmoney PDF cross-reference | 2 min |
| New Target Research | Coverage → Valuation → Concepts → Fund flow → Dragon tiger → Lockup → Margin | 1 min |

---

## V3.4.0 Highlights

| Change | Description |
|--------|-------------|
| **Cailianpress flash revived (#14 closed)** | What died in 2026-05 was the old `nodeapi` family; the official `v1/roll/get_roll_list` has been up all along, merely enforcing a `sign` — computable locally (`md5(sha1(query string sorted by key))`), zero key. Market-wide flash restored, an independent backup to Eastmoney 7×24 (different source, different rate-limit plane) |
| **Backup-source quick reference & fallback strategy (new section)** | Per-layer primary → independent-backup table (exchange official / Sina / THS F10 / HKEX / cninfo webapi / Jin10 — all on different domains and rate-limit planes) + a "confirmed dead" list. Instant fallback when an Eastmoney IP-level ban takes out a whole batch |
| **3 official backup functions** | `dragon_tiger_backup()` (SSE + SZSE official dragon-tiger board, zero-auth, authoritative, incl. brokerage seats), `fund_flow_backup()` (Sina daily 4-tier order net flow), `announcements_backup()` (SZSE official for Shenzhen tickers / Eastmoney for Shanghai, both with direct PDF links). All verified against live data on 2026-07-11 |
| **Lockup-expiry field fix** | Eastmoney renamed columns in `RPT_LIFT_STAGE`, leaving `type`/`shares` permanently empty → switched to `FREE_SHARES_TYPE`/`FREE_SHARES`, added `able_shares` (actually tradable shares — closer to real selling pressure) |
| **Industry ranking sort fix** | The clist request lacked a sort field, so top/bottom slices weren't actually ordered by change → added `fid=f3`, now truly sorted descending |
| **Shenzhen Connect caveat** | Since the 2024-08 intraday-disclosure tightening, the sgt minute series is unreliable (hgt still fine); use HKEX official daily stats for authoritative northbound data (in the backup table) |
| **Endpoint routing table** | § → function → purpose → source: the first one-page overview of 60+ embedded functions, letting agents jump to a section instead of reading the whole file |
| **Endpoints 40 → 43, data sources 13 → 15** | Added SSE & SZSE official as first-party sources; FAQ adds an Eastmoney-ban playbook / CLS revival / mootdx-abandoned notes |

> Earlier version highlights: see [CHANGELOG.md](./CHANGELOG.md).

---

## Data Source Priority (V3.2 re-ranked by IP-ban risk)

> **Principle: anything available from mootdx or Tencent (quotes / K-line / live price / market cap / financials) must use them first (never IP-banned). Eastmoney is only for its exclusive data, all routed through the throttled `em_get()`.**

| Priority | Source | Protocol | IP Ban Risk | Use |
|----------|--------|----------|-------------|-----|
| **1 (top)** | mootdx (TDX) | TCP 7709 | **Never banned** | K-line / order book / ticks / financials / F10 |
| **2 (top)** | Tencent Finance | HTTP | **Never banned** | Live price / PE / PB / market cap / turnover / index / ETF |
| 3 | THS Hot Stocks / Northbound | HTTP | Very low (zero auth) | Hot stocks / themes / northbound flow |
| 4 | Baidu Finance | HTTP | Very low | K-line (w/ MA5/10/20) |
| 5 | Sina Finance | HTTP | Low | Financial statements |
| 6 | cninfo | HTTP | Low | Filings |
| 7 | THS Consensus EPS | HTTP | Low (UA required) | Consensus EPS |
| 8 | iwencai | OpenAPI | Low (key required) | NL semantic search |
| **last (exclusive only)** | **Eastmoney** datacenter/push2/reportapi/search/np-weblist | HTTP | **Medium — has rate-limit risk** | Dragon-tiger / lockup / margin / block trade / shareholders / dividends / fund flow / reports / news (all via `em_get()`) |

> **Architecture:** Except mootdx (TCP binary protocol), all sources use direct HTTP API calls, zero third-party data wrapper dependencies. **Eastmoney APIs are rate-limited; all calls go through `em_get()` for serial throttling. For batch jobs, increase `EM_MIN_INTERVAL`.**
>
> **Fallback (V3.4 new):** When any primary source is banned or broken, check the "Backup Sources & Fallback Strategy" section in SKILL.md — every data category has an independent backup on a **different domain and rate-limit plane** (SSE/SZSE official / Sina / THS / HKEX), unaffected when Eastmoney bans you.

---

## Disclaimer

This project provides data access tools only and does not constitute investment advice. Investing involves risk.

---

## License

[Apache License 2.0](./LICENSE)

**Author:** Simon Lin · TikTok [@simonlin121212](https://www.tiktok.com/@simonlin121212) · Douyin "Simon林" · WeChat Official Account "硅基世纪"

</details>

