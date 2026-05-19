# a-stock-data

A 股全栈数据工具包 — 7 层架构 · 28 个端点 · 13 个数据源 · 零第三方数据封装依赖

一个自包含的 Skill 文件，把分散在 13 个数据源里的 A 股原始数据整合成 AI 编程助手直接能用的工具集。你不用再背 mootdx 的 K 线参数、东财的 PDF Referer 头、iwencai 的 X-Claw 鉴权、百度 PAE 的 Header 拼接——全部封装好了。

> **V3.0 Breaking Change：** 彻底移除 akshare 依赖，所有数据源改为直连 HTTP API。新增资金面/筹码层（融资融券 + 大宗交易 + 股东户数 + 分红送转 + 个股资金流120日）。

> 兼容 [Claude Code](https://github.com/anthropics/claude-code) · [Codex](https://github.com/openai/codex) · [OpenClaw](https://github.com/anthropics/openclaw)
>
> Skill 文件本质是结构化 Markdown + 内嵌 Python，任何支持上下文注入的 AI 编程助手都能用。

---

## 架构

```
A 股全栈数据 · 七层架构 · V3.0
│
├── 行情层    mootdx + 腾讯财经 + 百度K线   K线(带MA5/10/20) + 五档盘口 + PE/PB/市值 + 指数/ETF
├── 研报层    东财 reportapi + 同花顺 + iwencai  研报列表 / PDF下载 / 一致预期 / NL搜索
├── 信号层    同花顺 + 百度股市通 + 东财DC   强势股 + 题材归因 + 北向资金 + 概念板块
│                                           + 资金流向 + 龙虎榜 + 全市场龙虎榜 + 解禁 + 行业对比
├── 资金面    东财 datacenter + push2his     融资融券 + 大宗交易 + 股东户数 + 分红送转 + 资金流120日
├── 新闻层    东财 + 财联社（直连HTTP）      个股新闻 / 财联社快讯 / 全球资讯
├── 基础数据  mootdx + 东财 + 新浪           季报37字段 / F10九大类 / 财报三表
└── 公告层    巨潮 cninfo + mootdx           沪深北全量公告
```

---

## 快速开始

**2 步，1 分钟。**

```bash
# 1. 一键安装（拉取 SKILL.md + references/，自动放到 ~/.claude/skills/a-stock-data/）
curl -fsSL https://raw.githubusercontent.com/simonlin1212/a-stock-data/main/install.sh | bash

# 2. 安装依赖（V3.0 不再需要 akshare）
pip install mootdx requests pandas stockstats
```

启动 Claude Code，说一句「帮我看看 688017 的估值」，自动激活。

> **自定义安装路径**：`INSTALL_DIR=/path/to/skill curl ... | bash`

> **Codex / OpenClaw 用户：** 把 SKILL.md 内容贴入系统 prompt 或项目上下文，需要某层完整代码时再读对应的 `references/0X-*.md`，内嵌 Python 代码可直接执行。

---

## 28 个端点能力清单

### 行情层（实时，不封 IP）

| 端点 | 数据 |
|------|------|
| mootdx 行情 | K线(多周期) + 五档盘口 + 逐笔成交 + 实时报价 46 字段 |
| 腾讯财经 | PE(TTM) / PB / 总市值 / 流通市值 / 换手率 / 涨跌停价 / 指数 / ETF |
| **百度K线** | 日K线 + MA5/MA10/MA20 均价直接返回（V3.0 新增） |

### 研报层

| 端点 | 数据 |
|------|------|
| 东财 reportapi | 研报列表 + 评级 + 三年 EPS 预测 |
| 东财 PDF 下载 | 完整研报 PDF（已处理 Referer 鉴权） |
| 同花顺一致预期 | 机构一致预期 EPS（直连 basic.10jqka.com.cn） |
| iwencai NL 搜索 | 自然语言跨主题研报检索 |

### 信号层

| 端点 | 数据 |
|------|------|
| 同花顺热点 | 当日强势股 + 题材归因 reason tags（编辑部人工标注） |
| 同花顺北向（实时） | 沪股通 / 深股通分钟级流向（262 个时间点） |
| 同花顺北向（历史） | 本地自缓存日级历史 |
| 百度概念板块 | 行业 / 概念 / 地域三维归属 + 当日涨跌幅 |
| 百度资金流向 | 主力 / 散户 / 超大单分钟级 + 20 日历史 |
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
| 财联社快讯 | 分钟级电报（直连 cls.cn） |
| 全球资讯 | 东财全球财经资讯（直连 np-weblist） |

### 基础数据 + 公告

| 端点 | 数据 |
|------|------|
| 季报快照 | 37 字段（EPS / ROE / 净利润 / 主营收入...） |
| F10 公司资料 | 9 大类文本（截断优化，-70% token） |
| 东财个股信息 | 行业/总股本/流通股/市值/上市日期（直连 push2） |
| 新浪财报三表 | 资产负债表/利润表/现金流量表（直连 quotes.sina.cn） |
| 巨潮公告 | 沪深北交所全量公告 |

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

## V3.0 亮点

| 变化 | 说明 |
|------|------|
| **移除 akshare** | 13 个 akshare 调用全部替换为直连 HTTP API，零中间依赖 |
| **资金面/筹码层** | 新增融资融券、大宗交易、股东户数、分红送转、个股资金流120日 |
| **百度K线带MA** | 返回时直接含 MA5/10/20 均价，无需自行计算 |
| **行业板块切东财** | 同花顺加了反爬401，换东财 push2 零鉴权替代 |
| **指数/ETF行情** | 腾讯 API 扩展支持上证指数、沪深300、创业板指、ETF |
| **统一 helper** | `eastmoney_datacenter()` 函数复用 6 类 datacenter 查询 |
| **28 端点** | 从 20 增至 28，数据源从 8 增至 13 |

---

## 数据源优先级

| 优先级 | 数据源 | 协议 | 封 IP 风险 |
|--------|--------|------|-----------|
| 1 | mootdx | TCP (7709) | 极低 |
| 2 | 腾讯财经 | HTTP | 低 |
| 3 | 东财 datacenter | HTTP | 低 |
| 4 | 东财 push2/push2his | HTTP | 低 |
| 5 | iwencai | OpenAPI | 低（需 Key） |
| 6 | 东财 reportapi/PDF | HTTP | 低 |
| 7 | 同花顺热点 | HTTP | 极低（零鉴权） |
| 8 | 同花顺北向 | HTTP | 极低（零鉴权） |
| 9 | 百度股市通 | HTTP | 极低（零鉴权） |
| 10 | 新浪财经 | HTTP | 低 |
| 11 | 同花顺一致预期 | HTTP | 低（需UA） |
| 12 | 财联社 | HTTP | 低 |
| 13 | 巨潮 cninfo | HTTP | 低 |

> **V3.0 架构原则：** 除 mootdx（TCP 二进制协议）外，全部直连 HTTP API，零第三方数据封装依赖。

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

Full-stack data toolkit for China A-Share market — 7-layer architecture · 28 endpoints · 13 data sources · zero third-party data wrapper dependencies

A self-contained Skill file that consolidates raw A-share data from 13 sources into a ready-to-use toolkit for AI coding assistants. No need to memorize mootdx candlestick parameters, Eastmoney PDF Referer headers, iwencai X-Claw authentication, or Baidu PAE header assembly — it's all handled.

> **V3.0 Breaking Change:** Completely removed akshare dependency. All data sources now use direct HTTP API calls. Added capital flow / ownership layer (margin trading + block trades + shareholder count + dividends + 120-day fund flow).

> Compatible with [Claude Code](https://github.com/anthropics/claude-code) · [Codex](https://github.com/openai/codex) · [OpenClaw](https://github.com/anthropics/openclaw)
>
> The Skill file is structured Markdown + embedded Python. Any AI coding assistant with context injection can use it.

---

## Architecture

```
China A-Share Full-Stack Data · 7-Layer Architecture · V3.0
│
├── Market Data    mootdx + Tencent + Baidu K-line   Candlesticks (w/ MA5/10/20) + Order Book + PE/PB + Index/ETF
├── Research       Eastmoney + THS + iwencai          Report list / PDF / Consensus EPS / NL search
├── Signals        THS + Baidu + Eastmoney DC         Hot stocks + Sector attribution + Northbound flow
│                                                     + Concept blocks + Fund flow + Dragon Tiger + Lockup + Industry
├── Capital Flow   Eastmoney datacenter + push2his    Margin trading + Block trades + Holder count + Dividends + 120d flow
├── News           Eastmoney + CLS (direct HTTP)      Stock news / CLS flash / Global finance
├── Fundamentals   mootdx + Eastmoney + Sina          37-field quarterly + F10 9 categories + Financial statements
└── Filings        cninfo + mootdx                    Full filings across SSE / SZSE / BSE
```

---

## Quick Start

**2 steps, 1 minute.**

```bash
# 1. One-line install (fetches SKILL.md + references/ into ~/.claude/skills/a-stock-data/)
curl -fsSL https://raw.githubusercontent.com/simonlin1212/a-stock-data/main/install.sh | bash

# 2. Install dependencies (V3.0: akshare no longer needed)
pip install mootdx requests pandas stockstats
```

Launch Claude Code and say "Check the valuation of 688017" — the skill activates automatically.

> **Custom install path:** `INSTALL_DIR=/path/to/skill curl ... | bash`

> **Codex / OpenClaw users:** Paste the contents of SKILL.md into your system prompt or project context. Read `references/0X-*.md` on demand for the layer you need; the embedded Python code is ready to execute.

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
| Eastmoney reportapi | Report list + ratings + 3-year EPS forecasts |
| Eastmoney PDF | Full research report PDF (Referer auth handled) |
| THS Consensus EPS | Institutional consensus EPS (direct basic.10jqka.com.cn) |
| iwencai NL Search | Natural language cross-topic report search |

### Signals

| Endpoint | Data |
|----------|------|
| THS Hot Stocks | Today's strong stocks + sector attribution tags (editorial annotations) |
| THS Northbound (real-time) | Shanghai/Shenzhen Connect minute-level flow (262 data points) |
| THS Northbound (historical) | Local self-cached daily history |
| Baidu Concept Blocks | Industry / Concept / Region classification + daily change |
| Baidu Fund Flow | Institutional / Retail / Super-large order minute-level + 20-day history |
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
| CLS Flash | Minute-level telegrams (direct cls.cn) |
| Global News | Eastmoney global finance news (direct np-weblist) |

### Fundamentals + Filings

| Endpoint | Data |
|----------|------|
| Quarterly Snapshot | 37 fields (EPS / ROE / Net Profit / Revenue...) |
| F10 Company Data | 9 categories (truncation optimization, -70% tokens) |
| Eastmoney Stock Info | Industry / total shares / float / market cap / listing date (direct push2) |
| Sina Financial Statements | Balance sheet / Income statement / Cash flow (direct quotes.sina.cn) |
| cninfo Filings | Full filings across all exchanges |

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

## V3.0 Highlights

| Change | Description |
|--------|-------------|
| **Removed akshare** | All 13 akshare calls replaced with direct HTTP API calls, zero middleware |
| **Capital Flow Layer** | New: margin trading, block trades, shareholder count, dividends, 120-day fund flow |
| **Baidu K-line w/ MA** | Returns MA5/10/20 moving averages directly, no manual calculation |
| **Industry → Eastmoney** | THS added anti-scraping 401, replaced with Eastmoney push2 (zero auth) |
| **Index/ETF Quotes** | Tencent API extended for SSE Composite, CSI 300, ChiNext, ETFs |
| **Unified Helper** | `eastmoney_datacenter()` function shared across 6 datacenter queries |
| **28 Endpoints** | Up from 20, data sources up from 8 to 13 |

---

## Data Source Priority

| Priority | Source | Protocol | IP Ban Risk |
|----------|--------|----------|-------------|
| 1 | mootdx | TCP (7709) | Very low |
| 2 | Tencent Finance | HTTP | Low |
| 3 | Eastmoney datacenter | HTTP | Low |
| 4 | Eastmoney push2/push2his | HTTP | Low |
| 5 | iwencai | OpenAPI | Low (key required) |
| 6 | Eastmoney reportapi/PDF | HTTP | Low |
| 7 | THS Hot Stocks | HTTP | Very low (zero auth) |
| 8 | THS Northbound | HTTP | Very low (zero auth) |
| 9 | Baidu Finance | HTTP | Very low (zero auth) |
| 10 | Sina Finance | HTTP | Low |
| 11 | THS Consensus EPS | HTTP | Low (UA required) |
| 12 | CLS (Cailian Press) | HTTP | Low |
| 13 | cninfo | HTTP | Low |

> **V3.0 Architecture:** Except mootdx (TCP binary protocol), all sources use direct HTTP API calls. Zero third-party data wrapper dependencies.

---

## Disclaimer

This project provides data access tools only and does not constitute investment advice. Investing involves risk.

---

## License

[Apache License 2.0](./LICENSE)

**Author:** Simon Lin · TikTok [@simonlin121212](https://www.tiktok.com/@simonlin121212) · Douyin "Simon林" · WeChat Official Account "硅基世纪"

</details>

