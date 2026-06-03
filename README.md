# a-stock-data

A 股全栈数据工具包：7 层架构、27 个有效端点、零第三方数据封装依赖。

V4.0 起项目从“单文件内嵌全部代码”改造为“渐进式披露 Skill 包”：

- `SKILL.md`：轻量路由器，只负责触发、路由和约束。
- `scripts/a_stock_client.py`：所有端点实现和命令行入口。
- `references/`：按需读取的端点说明、字段口径、估值公式、工作流和 FAQ。
- `agents/openai.yaml`：Codex UI 元数据。

这样可以保留原有完整能力，同时避免任何 A 股问题都一次性加载 2000 行端点代码。

## 快速开始

完整安装整个 Skill 目录：

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/simonlin1212/a-stock-data ~/.claude/skills/a-stock-data
cd ~/.claude/skills/a-stock-data
pip install mootdx requests pandas lxml stockstats
```

Codex 用户也应把整个 `a-stock-data/` 目录放入可用 Skill 目录，而不是只复制 `SKILL.md`。

环境检查：

```bash
python scripts/validate_env.py
```

迁移完整性检查：

```bash
python scripts/smoke_test_endpoints.py
```

执行端点：

```bash
python scripts/a_stock_client.py tencent_quote 600519
python scripts/a_stock_client.py full_valuation 688017
```

## 架构

```text
A 股全栈数据
├── 行情层      mootdx + 腾讯财经 + 百度K线
├── 研报层      东财 reportapi + 东财 PDF + 同花顺 + iwencai
├── 信号层      同花顺热点/北向 + 百度概念 + 东财资金流/龙虎榜/解禁/行业
├── 资金筹码层  东财 datacenter + push2his
├── 新闻层      东财个股新闻 + 东财全球资讯
├── 基础数据层  mootdx + 东财 + 新浪
└── 公告层      巨潮 cninfo + mootdx F10
```

数据源优先级：

1. 能用通达信 `mootdx` 或腾讯财经拿到的，优先不用东财。
2. 东财只用于独有数据。
3. 所有东财请求统一经 `em_get()` 串行限流，批量任务调大 `EM_MIN_INTERVAL`。

## 27 个有效端点

### 行情层

| 端点 | 函数 | 数据 |
|---|---|---|
| mootdx 行情 | `mootdx_bars` / `mootdx_quotes` / `mootdx_transactions` | K线、五档盘口、逐笔成交、实时报价 |
| 腾讯财经 | `tencent_quote` | PE/PB、市值、换手率、涨跌停、指数、ETF |
| 百度K线 | `baidu_kline_with_ma` | 日 K线、MA5、MA10、MA20 |

### 研报层

| 端点 | 函数 | 数据 |
|---|---|---|
| 东财研报 | `eastmoney_reports` | 研报列表、评级、EPS 预测 |
| 东财 PDF | `download_pdf` | 完整研报 PDF |
| 同花顺一致预期 | `ths_eps_forecast` | 机构一致预期 EPS |
| iwencai 搜索 | `iwencai_search` / `iwencai_query` | 自然语言主题研报检索 |

### 信号层

| 端点 | 函数 | 数据 |
|---|---|---|
| 同花顺热点 | `ths_hot_reason` | 当日强势股、题材归因 |
| 北向实时 | `hsgt_realtime` | 沪股通/深股通分钟流向 |
| 北向历史 | `_load_northbound_history` | 本地自缓存历史 |
| 百度概念 | `baidu_concept_blocks` | 行业、概念、地域归属 |
| 分钟资金流 | `eastmoney_fund_flow_minute` | 主力/超大单/大单/中单/小单分钟净流入 |
| 龙虎榜席位 | `dragon_tiger_board` | 上榜记录、买卖席位、机构动向 |
| 全市场龙虎榜 | `daily_dragon_tiger` | 每日全市场上榜股票和净买额 |
| 限售解禁 | `lockup_expiry` | 历史解禁和未来 90 天预警 |
| 行业排名 | `industry_comparison` | 行业涨跌、上涨下跌家数、领涨股 |

### 资金面 / 筹码层

| 端点 | 函数 | 数据 |
|---|---|---|
| 融资融券 | `margin_trading` | 融资余额、买入、偿还、融券余额 |
| 大宗交易 | `block_trade` | 成交价、量、买卖方、溢价率 |
| 股东户数 | `holder_num_change` | 股东数、环比变化、户均持股 |
| 分红送转 | `dividend_history` | 派息、送股、转增、进度 |
| 120 日资金流 | `stock_fund_flow_120d` | 主力/大单/中单/小单日级净流入 |

### 新闻层

| 端点 | 函数 | 数据 |
|---|---|---|
| 个股新闻 | `eastmoney_stock_news` | 东财个股新闻 |
| 全球资讯 | `eastmoney_global_news` | 东财 7x24 财经资讯 |

财联社旧公开接口已下线，`cls_telegraph()` 仅保留兼容入口，默认返回空列表，不计入有效端点。

### 基础数据和公告

| 端点 | 函数 | 数据 |
|---|---|---|
| 季报快照 | `mootdx_finance` | 37 字段财务快照 |
| F10 公司资料 | `mootdx_f10` / `mootdx_f10_section` | 9 大类公司文本 |
| 东财个股信息 | `eastmoney_stock_info` | 行业、股本、市值、上市日期 |
| 新浪财报三表 | `sina_financial_report` | 利润表、资产负债表、现金流量表 |
| 巨潮公告 | `cninfo_announcements` | 沪深北公告全文检索 |

## 估值和工作流

估值函数：

- `forward_pe(price, eps_forecast)`
- `pe_digestion(current_pe, cagr, target_pe=30)`
- `calc_peg(pe, cagr)`
- `full_valuation(code)`

工作流说明：

- `references/workflows-valuation.md`：单票估值和新标的快速判断。
- `references/workflows-screening.md`：批量估值和横向对比。
- `references/workflows-theme-research.md`：主题研报、产业链调研、题材归因。

## 目录说明

```text
a-stock-data/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
│   ├── a_stock_client.py
│   ├── validate_env.py
│   └── smoke_test_endpoints.py
├── references/
│   ├── conventions.md
│   ├── endpoint-market.md
│   ├── endpoint-research.md
│   ├── endpoint-signals.md
│   ├── endpoint-capital-chip.md
│   ├── endpoint-news.md
│   ├── endpoint-fundamentals.md
│   ├── endpoint-announcements.md
│   ├── valuation-formulas.md
│   ├── workflows-valuation.md
│   ├── workflows-screening.md
│   ├── workflows-theme-research.md
│   └── troubleshooting.md
└── assets/
```

## 注意事项

- 只有 iwencai 需要 `IWENCAI_API_KEY`。
- 东财接口有风控，批量任务不要并发。
- 财联社旧接口已下线，用东财全球资讯替代。
- 回答当前行情、资金流、新闻、公告时必须实时取数，不要使用模型记忆。

---

# English

Full-stack data toolkit for China A-share market: 7-layer architecture, 27 active endpoints, and zero third-party data wrapper dependency.

Since V4.0, this project uses a progressive-disclosure Skill package instead of a monolithic Markdown file:

- `SKILL.md`: lightweight router for activation, routing, source priority, and output contract.
- `scripts/a_stock_client.py`: executable endpoint implementations and CLI entry point.
- `references/`: on-demand endpoint notes, field definitions, valuation formulas, workflows, and FAQ.
- `agents/openai.yaml`: Codex UI metadata.

This keeps all original capabilities while avoiding loading thousands of lines of endpoint code for every A-share request.

## Quick Start

Install the whole Skill directory:

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/simonlin1212/a-stock-data ~/.claude/skills/a-stock-data
cd ~/.claude/skills/a-stock-data
pip install mootdx requests pandas lxml stockstats
```

Codex users should also install the full `a-stock-data/` directory instead of copying only `SKILL.md`.

Environment check:

```bash
python scripts/validate_env.py
```

Migration smoke test:

```bash
python scripts/smoke_test_endpoints.py
```

Run endpoints:

```bash
python scripts/a_stock_client.py tencent_quote 600519
python scripts/a_stock_client.py full_valuation 688017
```

## Architecture

```text
A-share full-stack data
├── Market          mootdx + Tencent Finance + Baidu K-line
├── Research        Eastmoney reportapi + Eastmoney PDF + THS + iwencai
├── Signals         THS hot/northbound + Baidu concepts + Eastmoney flow/DTB/lockup/industry
├── Capital/Chips   Eastmoney datacenter + push2his
├── News            Eastmoney stock news + Eastmoney global news
├── Fundamentals    mootdx + Eastmoney + Sina
└── Announcements   cninfo + mootdx F10
```

Source priority:

1. Prefer `mootdx` or Tencent whenever they cover the requested data.
2. Use Eastmoney only for its exclusive data.
3. Route all Eastmoney requests through `em_get()` with serial throttling. Increase `EM_MIN_INTERVAL` for batch jobs.

## 27 Active Endpoints

### Market

| Endpoint | Function | Data |
|---|---|---|
| mootdx market data | `mootdx_bars` / `mootdx_quotes` / `mootdx_transactions` | K-lines, order book, transactions, quotes |
| Tencent Finance | `tencent_quote` | PE/PB, market cap, turnover, limit prices, indices, ETFs |
| Baidu K-line | `baidu_kline_with_ma` | Daily K-line, MA5, MA10, MA20 |

### Research

| Endpoint | Function | Data |
|---|---|---|
| Eastmoney reports | `eastmoney_reports` | Report list, ratings, EPS forecasts |
| Eastmoney PDF | `download_pdf` | Full research report PDF |
| THS consensus EPS | `ths_eps_forecast` | Institutional consensus EPS |
| iwencai search | `iwencai_search` / `iwencai_query` | Natural-language thematic report search |

### Signals

| Endpoint | Function | Data |
|---|---|---|
| THS hot reasons | `ths_hot_reason` | Strong stocks and theme attribution |
| Northbound realtime | `hsgt_realtime` | Shanghai/Shenzhen Connect minute-level flow |
| Northbound cache | `_load_northbound_history` | Locally cached history |
| Baidu concepts | `baidu_concept_blocks` | Industry, concept, and region tags |
| Minute fund flow | `eastmoney_fund_flow_minute` | Main, super-large, large, mid, small order flow |
| Dragon-Tiger Board | `dragon_tiger_board` | Records, buy/sell brokerages, institutional activity |
| Daily Dragon-Tiger Board | `daily_dragon_tiger` | Full-market daily list and net buy ranking |
| Lockup expiry | `lockup_expiry` | Historical and upcoming lockup releases |
| Industry ranking | `industry_comparison` | Industry change, up/down counts, leaders |

### Capital / Chips

| Endpoint | Function | Data |
|---|---|---|
| Margin trading | `margin_trading` | Margin balance, buy, repay, short balance |
| Block trades | `block_trade` | Price, volume, buyer/seller, premium |
| Shareholder count | `holder_num_change` | Holder count, QoQ change, average shares |
| Dividends | `dividend_history` | Cash dividend, bonus shares, transfer shares |
| 120-day fund flow | `stock_fund_flow_120d` | Daily main/large/mid/small order net inflow |

### News

| Endpoint | Function | Data |
|---|---|---|
| Stock news | `eastmoney_stock_news` | Eastmoney stock news |
| Global news | `eastmoney_global_news` | Eastmoney 7x24 financial news |

The old Cailianpress public API is offline. `cls_telegraph()` is kept only as a compatibility stub and returns an empty list; it is not counted as an active endpoint.

### Fundamentals and Announcements

| Endpoint | Function | Data |
|---|---|---|
| Quarterly snapshot | `mootdx_finance` | 37-field financial snapshot |
| F10 company data | `mootdx_f10` / `mootdx_f10_section` | 9 categories of company text |
| Eastmoney stock info | `eastmoney_stock_info` | Industry, shares, market cap, listing date |
| Sina financial statements | `sina_financial_report` | Income statement, balance sheet, cash flow |
| cninfo announcements | `cninfo_announcements` | Full announcements across Shanghai, Shenzhen, Beijing |

## Valuation and Workflows

Valuation helpers:

- `forward_pe(price, eps_forecast)`
- `pe_digestion(current_pe, cagr, target_pe=30)`
- `calc_peg(pe, cagr)`
- `full_valuation(code)`

Workflow references:

- `references/workflows-valuation.md`: single-stock valuation and quick target research.
- `references/workflows-screening.md`: batch valuation and side-by-side comparison.
- `references/workflows-theme-research.md`: thematic research, supply-chain research, and theme attribution.

## Notes

- Only iwencai requires `IWENCAI_API_KEY`.
- Eastmoney has rate limits. Do not run batch jobs concurrently.
- The old Cailianpress API is offline; use Eastmoney global news instead.
- Always retrieve current quotes, flow, news, announcements, and reports live. Do not answer current market data from model memory.
