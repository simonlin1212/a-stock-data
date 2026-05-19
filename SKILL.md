---
name: a-stock-data
description: 当用户询问 A 股个股或行业的数据时使用。覆盖场景：A 股个股估值（PE/PEG/一致预期）、实时行情与五档盘口、券商研报检索、龙虎榜与机构席位、北向资金、概念板块归属、个股资金流向、融资融券、大宗交易、股东户数变化、分红送转、限售解禁日历、行业横向对比、产业链调研、巨潮公告全文、批量横向筛选。不要用于港股、美股、加密、期货、境外 ETF、宏观经济。
origin: custom
version: 3.0
---

> 项目主页：https://github.com/simonlin1212/a-stock-data — 更新、反馈、支持作者
>
> 作者：Simon 林 · 抖音「Simon林」· 公众号「硅基世纪」

# A 股全栈数据工具包 V3.0

七层数据架构 · 28 端点 · 13 数据源 · 全部直连 HTTP API（仅 mootdx 走 TCP）· 零第三方数据封装依赖。

**安装方式**：将本仓库放置为 `~/.claude/skills/a-stock-data/`，Claude Code 会自动识别并在 A 股相关对话中激活。

## 七层数据架构与函数索引

```
Layer 1 行情     mootdx + 腾讯 + 百度K线                          → references/01-quotes.md
Layer 2 研报     东财 + 同花顺一致预期 + iwencai                  → references/02-research.md
Layer 3 信号     热点 + 北向 + 概念 + 资金流 + 龙虎 + 解禁 + 行业  → references/03-signals.md
Layer 4 资金面   融资融券 + 大宗 + 股东户数 + 分红 + 120日资金流   → references/04-capital.md
Layer 5 新闻     东财个股 + 财联社 + 东财全球                     → references/05-news.md
Layer 6 基础数据 mootdx 财务/F10 + 东财 + 新浪三表                → references/06-fundamentals.md
Layer 7 公告     巨潮 cninfo + mootdx F10                         → references/07-filings.md

调研流程  A 单票估值 / B 批量对比 / C 主题研报 / D 新标的速览       → references/workflows.md
故障排查  数据源优先级 + 13 个常见踩坑                             → references/faq.md
```

## When to Activate

激活：用户问 **A 股个股 / 概念 / 行业**（估值 / 行情 / 研报 / 龙虎榜 / 北向 / 资金流 / 融资融券 / 解禁 / 分红 / 公告等）。

**不要用**：港股 / 美股 / 加密 / 期货 / 境外 ETF / 宏观经济。

关键词（任一命中即激活）：估值、一致预期、市盈率、PEG、市值、研报、产业链、行业研究、K 线、盘口、公告、新闻、强势股、题材、热点、概念归因、北向资金、沪股通、深股通、概念板块、资金流向、主力、龙虎榜、席位、营业部、净买入、解禁、限售、行业对比、行业轮动、融资融券、两融、大宗交易、股东户数、筹码集中、分红、派息、送股、指数、ETF。

---

## Prerequisites

```bash
pip install mootdx requests pandas stockstats
```

| 依赖 | 用途 |
|------|------|
| mootdx >= 0.10 | TCP 行情 + 财务快照 + F10（唯一非 HTTP 依赖）|
| requests | 所有 HTTP API 直连 |
| pandas | 数据处理 + HTML 表格解析 |
| stockstats | 技术指标（RSI/MACD/BOLL，可选）|

### iwencai API Key（仅 NL 语义搜索研报需要）

```bash
export IWENCAI_API_KEY="your_key_here"
export IWENCAI_BASE_URL="https://openapi.iwencai.com"
# 申请：https://www.iwencai.com/skillhub
```

其他 12 个数据源全部免费、无需 key。

---

## Common Utilities（所有 Layer 共用，请直接复用）

### 市场前缀规则

```python
def get_prefix(code: str) -> str:
    """6 位代码 → 市场前缀 (sh/sz/bj)"""
    if code.startswith(("6", "9")):
        return "sh"
    elif code.startswith("8"):
        return "bj"
    else:
        return "sz"
```

### 东财数据中心统一查询（Layer 3 / 4 共用 helper）

```python
import requests

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
DATACENTER_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"

def eastmoney_datacenter(report_name: str, columns: str = "ALL",
                          filter_str: str = "", page_size: int = 50,
                          sort_columns: str = "", sort_types: str = "-1") -> list[dict]:
    """东财数据中心统一查询 — 龙虎榜/解禁/融资融券/大宗/股东户数/分红 共用。"""
    params = {
        "reportName": report_name, "columns": columns,
        "filter": filter_str, "pageNumber": "1", "pageSize": str(page_size),
        "sortColumns": sort_columns, "sortTypes": sort_types,
        "source": "WEB", "client": "WEB",
    }
    r = requests.get(DATACENTER_URL, params=params, headers={"User-Agent": UA}, timeout=15)
    d = r.json()
    if d.get("result") and d["result"].get("data"):
        return d["result"]["data"]
    return []
```

---

## 估值计算公式

```python
import math

def forward_pe(price: float, eps_forecast: float) -> float:
    """前向 PE = 当前股价 / 未来年度一致预期 EPS"""
    return float("inf") if eps_forecast <= 0 else price / eps_forecast


def pe_digestion(current_pe: float, cagr: float, target_pe: float = 30) -> float:
    """当前 PE 消化到目标 PE 需要多少年。target_pe 默认 30x（A 股成长股锚点）。"""
    if current_pe <= target_pe:
        return 0.0
    if cagr <= 0:
        return float("inf")
    return math.log(current_pe / target_pe) / math.log(1 + cagr)


def calc_peg(pe: float, cagr: float) -> float:
    """PEG = 前向 PE / (CAGR × 100)。<1 便宜 / 1-1.5 合理 / >1.5 贵。"""
    return float("inf") if cagr <= 0 else pe / (cagr * 100)
```

## 投资框架速查

```
壁垒 → 增速 → PE 消化 → PEG 校验

1. 有壁垒吗？(tech_moat / capacity_moat) → 没有则排除
2. 增速多少？(CAGR > 30% 才有意义)
3. PE 多久消化到 30x？(< 2 年合理, > 4 年太贵)
4. PEG 多少？(< 1 便宜, 1-1.5 合理, > 1.5 贵)

30x PE 锚点：A 股成长股的合理估值重力线，所有行业统一用 30x。
期权定价例外：PEG > 3 但壁垒极深时，本质是看涨期权，不适用 PEG 框架。
```

---

## 调用方式

需要某层完整代码时，**Read 对应的 `references/0X-*.md`**——里面是可直接复制的函数实现。

举例：
- 用户问"查 688017 估值" → 读 `references/01-quotes.md` 拿 `tencent_quote()` + `references/02-research.md` 拿 `ths_eps_forecast()`，跑流程 A
- 用户问"昨天龙虎榜净买最多的" → 读 `references/03-signals.md` 拿 `daily_dragon_tiger()`
- 调研整套流程 → 读 `references/workflows.md`

不需要预先把所有 references 全读进 context，**按当前任务挑选**。
