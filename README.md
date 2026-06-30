# a-stock-data

A 股全栈数据工具包 — 10 层架构 · 40 个端点 · 13 个数据源 · 零第三方数据封装依赖

一个自包含的 Skill 文件，把分散在 13 个数据源里的 A 股原始数据整合成 AI 编程助手直接能用的工具集。你不用再背 mootdx 的 K 线参数、东财的 PDF Referer 头、iwencai 的 X-Claw 鉴权——全部封装好了。

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
A 股全栈数据 · 十层架构 · V3.3.0
│  （优先级：mootdx/腾讯 不封IP 优先用；东财仅用于独有数据，已内置限流防封）
├── 行情层    mootdx + 腾讯财经 + 百度K线   K线(带MA5/10/20) + 五档盘口 + PE/PB/市值 + 指数/ETF
├── 研报层    东财 reportapi + 同花顺 + iwencai  个股研报 / 行业研报 / PDF下载 / 一致预期 / NL搜索
├── 信号层    同花顺 + 东财                  强势股 + 题材归因 + 北向资金 + 板块归属
│                                           + 资金流向(push2) + 龙虎榜 + 全市场龙虎榜 + 解禁 + 行业对比
├── 资金面    东财 datacenter + push2        融资融券 + 大宗交易 + 股东户数 + 分红送转 + 资金流(分钟+120日)
├── 新闻层    东财（直连HTTP）              个股新闻 / 全球资讯（财联社快讯已下线）
├── 基础数据  mootdx + 东财 + 新浪           季报37字段 / F10九大类 / 财报三表
├── 公告层    巨潮 cninfo + mootdx           沪深北全量公告
├── 打板层    东财 push2ex + 同花顺          涨停池 / 炸板 / 跌停 / 昨涨停 / 涨停原因题材 / 连板梯队  ★V3.3
├── 期权层    新浪 hq.sinajs                ETF期权 T型报价 / 希腊字母 / 隐含波动率 IV  ★V3.3
└── 舆情互动  巨潮互动易 + 同花顺 + 东财     互动易问答 / 同花顺热榜 / 东财人气榜 / 概念命中  ★V3.3
```

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

## 40 个端点能力清单

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
| 同花顺北向（实时） | 沪股通 / 深股通分钟级流向（262 个时间点） |
| 同花顺北向（历史） | 本地自缓存日级历史 |
| 东财板块归属 | 个股所属全部板块（行业/概念/地域混合）+ BK码 + 当日涨跌幅 + 龙头股（V3.2.2 替换百度 PAE，一次请求拿全）|
| **东财资金流向** | 主力 / 大单 / 中单 / 小单 / 超大单分钟级净流入（V3.1 替换百度 PAE） |
| 龙虎榜席位 | 上榜记录 + 买卖席位 TOP5 + 机构动向 |
| 全市场龙虎榜 | 每日全市场上榜股票 + 净买额排名 + 上榜原因 |
| 限售解禁日历 | 历史解禁 + 未来 90 天待解禁预警 |
| **行业板块排名** | 东财行业涨跌/上涨下跌家数（V3.0 替换同花顺，零鉴权） |

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
| ~~财联社快讯~~ | ⚠️ 已下线（cls.cn 迁 Next.js，旧 API 404，#14）→ 用全球资讯替代 |
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
| 行业轮动 | 「今天哪些行业涨幅最大，资金在流入哪些板块」 |
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
| 批量对比 | 「帮我对比这 5 只半导体股的估值」 |

### 内置 4 套调研流程

| 流程 | 做什么 | 耗时 |
|------|--------|------|
| 单票估值 | 实时价 → 一致预期 EPS → 前向 PE / PEG / PE 消化年数 | 30 秒 |
| 批量对比 | 多只股票横向估值排列 | 1 分钟 |
| 主题研报 | iwencai 多关键词 NL 搜索 + 东财 PDF 交叉补充 | 2 分钟 |
| 新标的调研 | 机构覆盖 → 估值 → 概念板块 → 资金流向 → 龙虎榜 → 解禁 → 两融 | 1 分钟 |

---

## V3.3.0 亮点

| 变化 | 说明 |
|------|------|
| **打板层（新增一层 · #23 / #15）** | 东财涨停板四池（涨停 / 炸板 / 跌停 / 昨日涨停，走 `push2ex` 与现有 push2 同源限流）+ 同花顺涨停揭秘（涨停原因题材 / 封板成功率 / 板型）+ 打板情绪速算（炸板率 / 连板梯队）。连板梯队、晋级率、题材归因一站到位 |
| **ETF 期权层（新增一层 · #13）** | 50ETF / 300ETF / 科创50ETF / 500ETF 期权 T型报价 + 希腊字母（Delta / Gamma / Theta / Vega）+ 隐含波动率。新浪源，**交易所预算好、不用本地算 BSM** |
| **舆情互动层（新增一层）** | 互动易问答（投资者提问 + 公司回复，AI 能答"公司如何回应某传闻 / 利好"，别处拿不到）+ 同花顺热榜 + 东财人气榜 + 个股概念命中 |
| **ETF 支持显式说明** | ETF 行情 / K线一直支持（腾讯 + mootdx，代码直接当股票查），本版在使用示例表显式补上 ETF 例子，避免被看漏 |
| **端点 28 → 40，层数 7 → 10** | 三个新层全部免登录、零鉴权；东财源走现有 `em_get` 限流防封 |

## V3.2.5 亮点

| 变化 | 说明 |
|------|------|
| **分钟 K 线参数 Bug（#31，CRITICAL）** | `client.bars()` 旧代码用了不存在的参数名 `category=`，被 mootdx `**kwargs` 静默吞掉 → `frequency` 永远默认 9（日线），任何分钟/周/月线请求都静默退化成日线还不报错。改正为 `frequency=`，按 mootdx 0.11.7 源码重写频率值表（旧表 7-11 整段错），补 1分钟（`8`）/ 5分钟（`0`）示例 |
| **复权口径说明（#28）** | mootdx `bars` 返回**不复权**原始价（签名无 `adjust` 参数）→ 补警示：跨除权除息日做估值/回测须自行复权，或改用带前复权的腾讯日 K |
| **`full_valuation` EPS 取错列修复** | 旧代码 `row.iloc[2]` 取的是同花顺表「最小值」列，而非文档声明的「均值＝机构一致预期EPS」（列序 年度/预测机构数/最小值/均值/最大值）→ 致 PE_forward/PEG 系统性偏低。改按列名 `均值`/`预测机构数` 取，抗列序漂移；解析失败由静默 `except: pass` 改 `[WARN]` |
| **`em_get()` 连接级重试** | 挂载 `HTTPAdapter + urllib3.Retry`（total=3 指数退避，429/5xx 重试，403 不重试、靠降频应对），住宅 IP 偶发瞬态错误更稳 |
| **download_pdf 文件名加固** | `org` 机构简称与 `title` 一致做路径字符清洗 + 截断，防机构名含 `/` 拼坏保存路径 |

## V3.2.4 亮点

| 变化 | 说明 |
|------|------|
| **mootdx 0.11.x 兼容（#26 / PR #7）** | 全新安装裸调 `Quotes.factory()` 因 `BESTIP.HQ` 空串抛 `ValueError` → 新增 `tdx_client()` helper：TCP 探测内置可用服务器列表，用显式 `server=(ip,port)` 绕过 BESTIP，三级 fallback（bestip 测速→裸 factory→明确报错）防 IP 老化/换网。4 处 mootdx 调用统一改走它 |
| **不锁 mootdx 版本（决策）** | 锁 `0.10.12` 在干净 Python 3.9 下 `import` 即崩（numpy/pandas 二进制不兼容），比 0.11.x 更糟 → 依赖保持 `>=0.10`，靠 helper 而非锁版本解决兼容 |

## V3.2.3 亮点

| 变化 | 说明 |
|------|------|
| **行业研报端点（新增）** | 研报层补上东财行业研报 `eastmoney_industry_reports()`，与个股研报同端点（仅 `qType=1`），`industry_code="*"` 拉全行业、传东财行业码（如 `1238`=IT服务Ⅱ）精确过滤，PDF 复用 `download_pdf()`，走 `em_get` 限流。端点数 27 → 28 |
| **概念板块归属换源（#18）** | 百度 PAE `getrelatedblock` 失效（`ResultCode 10003`）→ 改用东财 `slist`，一次请求拿全个股所属板块（行业/概念/地域 + BK码 + 涨跌幅 + 龙头股），零鉴权走 `em_get` 限流 |
| **巨潮公告 orgId 动态化（#19）** | 硬编码 `gssx0{code}` 导致大量 601xxx 股票（平安/工行/中石油等）查不到公告 → 动态查官方映射表 `szse_stock.json`（6198 只股，模块级缓存），硬编码降为 fallback |
| **修复综合示例隐藏崩溃** | 示例仍调用 v3.1 已删除的 `baidu_fund_flow_history` → 改为 `eastmoney_fund_flow_minute` |
| **大陆住宅 IP 风控说明** | §4.5 资金流 / §5.1 新闻 加 ⚠️：部分大陆住宅 IP 会被东财间歇风控（`HTTP 000`/空），非代码问题，重试或换网络即可 |
| **数据源优先级原则**（V3.2 起） | 明确「能用通达信(mootdx)/腾讯就别用东财」——前两者 TCP/HTTP 实测不封 IP，可放心高频；东财仅用于其独有数据 |
| **东财统一限流防封** | 新增节流入口 `em_get()`，所有东财端点（datacenter/push2/reportapi/search/np-weblist）改用它，内置串行限流（间隔≥1s+随机抖动）+ 会话复用，批量抄代码即自带防封 |
| **东财风控阈值文档化** | SKILL 新增「数据源优先级 & 东财防封」章节，列出触发封禁的阈值（每秒>5/并发≥10/1分≥200/5分≥300）与防封铁律 |
| **财联社快讯下线（#14）** | `cls.cn` 旧 API 全面 404，标注弃用，改用东财全球资讯 |

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

> **V3.3.1 备用方案：** 当 push2/push2his 被封时，可用 `tools/data_fallback.py` 适配器切换到 datacenter-web + 腾讯行情 + 腾讯K线 + 新浪K线降级。详见 [`docs/anti-ban-case-study.md`](./docs/anti-ban-case-study.md)。

---

## FAQ

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

**Q: 东财 push2/push2his 被封了怎么办？（V3.3.1 实战）**
2026-06-30 实测案例：选股脚本 10 线程并发 + 零限流，1 小时内发出 45000+ 请求，触发东财 **IP 级封禁**（push2/push2his 全系列 `RemoteDisconnected`，持续 20+ 小时）。对策：使用 `tools/data_fallback.py` 适配器一键切换到备用数据源（datacenter-web + 腾讯行情 + 腾讯K线 + 新浪K线降级），详见 [`docs/anti-ban-case-study.md`](./docs/anti-ban-case-study.md)。**预防：** 所有东财请求走 `em_get()` 限流、并发≤3、批量任务 `EM_MIN_INTERVAL≥2s`、多版本脚本分时段运行。

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

Full-stack data toolkit for China A-Share market — 10-layer architecture · 40 endpoints · 13 data sources · zero third-party data wrapper dependencies

A self-contained Skill file that consolidates raw A-share data from 13 sources into a ready-to-use toolkit for AI coding assistants. No need to memorize mootdx candlestick parameters, Eastmoney PDF Referer headers, or iwencai X-Claw authentication — it's all handled.

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
China A-Share Full-Stack Data · 10-Layer Architecture · V3.3.0
│  (Priority: prefer mootdx/Tencent — never IP-banned; Eastmoney only for exclusive data, with built-in throttling)
├── Market Data    mootdx + Tencent + Baidu K-line   Candlesticks (w/ MA5/10/20) + Order Book + PE/PB + Index/ETF
├── Research       Eastmoney + THS + iwencai          Stock reports / Industry reports / PDF / Consensus EPS / NL search
├── Signals        THS + Eastmoney                    Hot stocks + Sector attribution + Northbound flow
│                                                     + Sector membership + Fund flow(push2) + Dragon Tiger + Lockup + Industry
├── Capital Flow   Eastmoney datacenter + push2       Margin trading + Block trades + Holder count + Dividends + Fund flow(min+120d)
├── News           Eastmoney (direct HTTP)            Stock news / Global finance (CLS flash deprecated)
├── Fundamentals   mootdx + Eastmoney + Sina          37-field quarterly + F10 9 categories + Financial statements
├── Filings        cninfo + mootdx                    Full filings across SSE / SZSE / BSE
├── Limit-Up       Eastmoney push2ex + THS            ZT/ZB/DT/prev-ZT pools / limit reasons / consecutive-board ladder  ★V3.3
├── Options        Sina hq.sinajs                     ETF option T-quotes / Greeks / implied volatility  ★V3.3
└── Sentiment      cninfo IRM + THS + Eastmoney       Investor Q&A / hot lists / popularity rank / concept hits  ★V3.3
```

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

## 28 Endpoints

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
| THS Northbound (real-time) | Shanghai/Shenzhen Connect minute-level flow (262 data points) |
| THS Northbound (historical) | Local self-cached daily history |
| Eastmoney Sector Membership | All sectors a stock belongs to (industry/concept/region mixed) + BK code + daily change + leading stock (V3.2.2, replaced Baidu PAE, one request) |
| **Eastmoney Fund Flow** | Main / Large / Medium / Small / Super-large order minute-level net inflow (V3.1, replaced Baidu PAE) |
| Dragon Tiger Board | Appearance records + Top 5 buy/sell brokerages + institutional activity |
| Daily Dragon Tiger (Full Market) | All stocks on daily board + net buy ranking + appearance reasons |
| Lockup Expiry Calendar | Historical releases + 90-day upcoming expiry alerts |
| **Industry Ranking** | Eastmoney industry change/up/down counts (V3.0, replaced THS 401) |

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
| ~~CLS Flash~~ | ⚠️ Deprecated (cls.cn migrated to Next.js, old API 404, #14) → use Global News |
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
| Batch Compare | "Compare valuations of these 5 semiconductor stocks" |

### 4 Built-in Research Workflows

| Workflow | What it does | Time |
|----------|-------------|------|
| Single Stock Valuation | Live price → Consensus EPS → Forward PE / PEG / PE payback years | 30 sec |
| Batch Comparison | Side-by-side valuation ranking | 1 min |
| Thematic Research | iwencai multi-keyword NL search + Eastmoney PDF cross-reference | 2 min |
| New Target Research | Coverage → Valuation → Concepts → Fund flow → Dragon tiger → Lockup → Margin | 1 min |

---

## V3.3.0 Highlights

| Change | Description |
|--------|-------------|
| **Limit-Up Layer (new · #23 / #15)** | Eastmoney's four limit-board pools (limit-up / break / limit-down / prev-day, via `push2ex`, same throttle as push2) + THS limit-up insight (limit reasons / seal success rate / board type) + sentiment quick-calc (break rate / consecutive-board ladder) |
| **ETF Options Layer (new · #13)** | 50ETF / 300ETF / STAR50 / 500ETF option T-quotes + Greeks (Delta/Gamma/Theta/Vega) + implied volatility. Sina source, **exchange-computed, no local BSM** |
| **Sentiment Layer (new)** | Investor Q&A (questions + company replies — answers "how does a company respond to a rumor/news", unavailable elsewhere) + THS hot list + EM popularity rank + concept hits |
| **Explicit ETF note** | ETF quotes/K-line were always supported (Tencent + mootdx, query by code like a stock); this version adds explicit ETF examples so it's not overlooked |
| **Endpoints 28 → 40, layers 7 → 10** | All three new layers are login-free, zero-auth; Eastmoney sources use the existing `em_get` throttle |

## V3.2.5 Highlights

| Change | Description |
|--------|-------------|
| **Minute K-line parameter bug (#31, CRITICAL)** | `client.bars()` used a non-existent param `category=`, silently swallowed by mootdx `**kwargs` → `frequency` always defaulted to 9 (daily), so every minute/weekly/monthly request silently degraded to daily with no error. Fixed to `frequency=`, rewrote the frequency table from mootdx 0.11.7 source (old `7-11` rows were all wrong), added 1-min (`8`) / 5-min (`0`) examples |
| **Adjustment note (#28)** | mootdx `bars` returns **unadjusted** raw prices (no `adjust` param) → added warning: adjust manually across ex-dividend dates or use Tencent forward-adjusted daily K |
| **`full_valuation` wrong EPS column fix** | Old `row.iloc[2]` read the THS "min" column instead of the documented "mean = consensus EPS" (column order: year/analyst count/min/mean/max), biasing PE_forward/PEG low. Now picks by column name, resilient to column reordering; silent `except: pass` → `[WARN]` |
| **`em_get()` connection-level retry** | Mounts `HTTPAdapter + urllib3.Retry` (total=3 exponential backoff, retry on 429/5xx, no retry on 403 — handled by throttling), steadier against transient errors on residential IPs |
| **download_pdf filename hardening** | `org` (institution short name) now sanitized + truncated like `title`, preventing `/` in names from breaking the save path |

## V3.2.4 Highlights

| Change | Description |
|--------|-------------|
| **mootdx 0.11.x compat (#26 / PR #7)** | A bare `Quotes.factory()` crashes on a fresh install (`BESTIP.HQ` empty string → `ValueError`) → added a `tdx_client()` helper that TCP-probes a built-in server list and passes an explicit `server=(ip,port)` to bypass BESTIP, with a 3-level fallback (bestip probe → bare factory → explicit error) against IP aging. All 4 mootdx calls now route through it |
| **No mootdx version pin (decision)** | Pinning `0.10.12` crashes on `import` under a clean Python 3.9 (numpy/pandas ABI mismatch) — worse than 0.11.x → dependency stays `>=0.10`, compat handled by the helper, not a pin |

## V3.2.3 Highlights

| Change | Description |
|--------|-------------|
| **Industry-report endpoint (new)** | Added Eastmoney industry reports `eastmoney_industry_reports()` to the research layer; same endpoint as single-stock reports (only `qType=1`); `industry_code="*"` pulls all industries, pass an Eastmoney industry code (e.g. `1238`=IT Services Ⅱ) to filter, PDF reuses `download_pdf()`, throttled via `em_get`. Endpoints 27 → 28 |
| **Sector membership re-sourced (#18)** | Baidu PAE `getrelatedblock` is dead (`ResultCode 10003`) → switched to Eastmoney `slist`; one request returns all of a stock's sectors (industry/concept/region + BK code + change% + leading stock), no auth, throttled via `em_get` |
| **cninfo orgId resolved dynamically (#19)** | Hardcoded `gssx0{code}` made many 601xxx tickers (Ping An / ICBC / PetroChina, etc.) return zero filings → now resolves the real orgId from the official map `szse_stock.json` (6198 stocks, module-level cache), hardcode kept as fallback |
| **Fixed hidden crash in combined example** | Example still called the v3.1-removed `baidu_fund_flow_history` → switched to `eastmoney_fund_flow_minute` |
| **Mainland residential IP throttling note** | §4.5 fund flow / §5.1 news: some mainland residential IPs hit intermittent Eastmoney throttling (`HTTP 000` / empty) — not a code bug, retry or switch network |
| **Data-source priority principle** (since V3.2) | Prefer mootdx (TDX) / Tencent — both never IP-banned in practice, safe for high-frequency use. Use Eastmoney only for its exclusive data |
| **Unified Eastmoney throttling** | New `em_get()` entry point; all Eastmoney endpoints (datacenter/push2/reportapi/search/np-weblist) route through it with built-in serial rate-limit (≥1s + jitter) + session reuse — copied code is ban-safe by default |
| **Eastmoney rate-limit documented** | New "Data-source priority & Eastmoney anti-ban" section lists ban thresholds (>5/s, ≥10 concurrent, ≥200/min, ≥300/5min) and anti-ban rules |
| **Cailianpress deprecated (#14)** | cls.cn old API returns 404 — marked deprecated, replaced by Eastmoney global news |

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

> **V3.3.1 Fallback:** When push2/push2his is IP-banned, use `tools/data_fallback.py` adapter to switch to datacenter-web + Tencent quotes + Tencent K-line + Sina K-line (degraded). See [`docs/anti-ban-case-study.md`](./docs/anti-ban-case-study.md).

---

## Disclaimer

This project provides data access tools only and does not constitute investment advice. Investing involves risk.

---

## License

[Apache License 2.0](./LICENSE)

**Author:** Simon Lin · TikTok [@simonlin121212](https://www.tiktok.com/@simonlin121212) · Douyin "Simon林" · WeChat Official Account "硅基世纪"

</details>

