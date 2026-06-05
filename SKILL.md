---
name: a-stock-data-next
description: A 股全栈数据工具包。用于实时行情、K线、估值、研报、一致预期、题材热点、概念板块、北向资金、资金流、龙虎榜、限售解禁、融资融券、大宗交易、股东户数、分红、新闻、基本面、财报三表和巨潮公告等 A 股数据任务。
origin: custom
version: 4.0.0
---

# A股全栈数据工具包

本 Skill 采用渐进式披露结构：本文件只负责路由、约束和最小操作说明；端点实现放在 `scripts/a_stock_client.py`；字段口径、工作流和故障处理按需读取 `references/`。

## 使用原则

1. 先识别用户任务类型、股票代码、日期范围和输出要求。
2. 只读取最相关的 1-2 个 reference 文件，不要一次加载全部文档。
3. 优先执行 `scripts/a_stock_client.py` 中的函数，不要把完整端点代码复制进上下文。
4. 回答必须说明数据源、数据日期、缺失字段和 caveat。
5. 不要用记忆补当前行情、新闻、公告、资金流、研报或估值输入。

## 数据源优先级

能用通达信或腾讯拿到的数据，优先不用东财：

- 通达信 `mootdx`：K线、五档、逐笔、财务快照、F10。
- 腾讯财经：实时价、PE/PB、市值、换手率、涨跌停、指数、ETF。
- 东财：只用于独有数据，如研报、资金流、龙虎榜、解禁、两融、大宗、股东户数、分红、个股新闻、全球资讯。

所有东财请求必须经 `em_get()` 串行限流。批量任务调大 `EM_MIN_INTERVAL`，不要并发请求东财。

详细规则见 `references/conventions.md`。

## 路由索引

| 用户意图 | 读取文件 |
|---|---|
| 依赖、ticker 归一化、数据源优先级、东财防封 | `references/conventions.md` |
| 实时行情、K线、盘口、逐笔、PE/PB、市值、指数、ETF | `references/endpoint-market.md` |
| 研报列表、PDF、一致预期 EPS、iwencai 语义搜索 | `references/endpoint-research.md` |
| 热点题材、北向、概念、分钟资金流、龙虎榜、解禁、行业轮动 | `references/endpoint-signals.md` |
| 融资融券、大宗交易、股东户数、分红、120 日资金流 | `references/endpoint-capital-chip.md` |
| 个股新闻、全市场 7x24 快讯、财联社下线替代 | `references/endpoint-news.md` |
| 财务快照、F10、东财基本面、新浪财报三表 | `references/endpoint-fundamentals.md` |
| 巨潮公告、F10 公告摘要 | `references/endpoint-announcements.md` |
| 前向 PE、PE 消化时间、PEG | `references/valuation-formulas.md` |
| 单票完整估值、新标的估值判断 | `references/workflows-valuation.md` |
| 多股票批量估值、横向对比、筛选 | `references/workflows-screening.md` |
| 主题研报、产业链调研、题材归因 | `references/workflows-theme-research.md` |
| 401、403、乱码、接口为空、财联社下线、东财防封 | `references/troubleshooting.md` |

## 脚本入口

主要实现位于：

```text
scripts/a_stock_client.py
```

示例：

```bash
python scripts/a_stock_client.py tencent_quote 600519
python scripts/a_stock_client.py full_valuation 688017
```

在 Python 中调用：

```python
from scripts.a_stock_client import tencent_quote, full_valuation

quote = tencent_quote(["600519"])
valuation = full_valuation("688017")
```

环境检查：

```bash
python scripts/validate_env.py
```

iwencai key 配置：

调用 iwencai 前，优先从环境变量读取 `IWENCAI_API_KEY`。若无法获取，向用户说明 iwencai 语义搜索需要 key，可通过 https://www.iwencai.com/skillhub 获取，并设置环境变量后重试。不要从本地验证目录读取 key，也不要把 key 写入受版本管理文件。

迁移完整性 smoke test：

```bash
python scripts/smoke_test_endpoints.py
```

## 有效端点覆盖

当前有效能力为 27 个端点。财联社旧 API 已下线，不计入有效端点；`cls_telegraph()` 仅保留兼容入口，默认返回空列表，使用 `eastmoney_global_news()` 替代。

端点分布：

- 行情层：mootdx 行情、腾讯财经、百度 K线。
- 研报层：东财研报、东财 PDF、同花顺一致预期、iwencai 搜索。
- 信号层：同花顺热点、北向实时、北向历史缓存、东财板块归属、东财分钟资金流、龙虎榜、全市场龙虎榜、限售解禁、行业排名。
- 资金面/筹码层：融资融券、大宗交易、股东户数、分红送转、120 日资金流。
- 新闻层：东财个股新闻、东财全球资讯。
- 基础数据层：mootdx 财务快照、mootdx F10、东财个股基本面、新浪财报三表。
- 公告层：巨潮公告、mootdx F10 公告摘要。

## 输出契约

回答中应包含：

1. 结论或数据表。
2. 数据源和日期。
3. 缺失字段、接口为空、非交易日、无 key、无机构覆盖等说明。
4. 如果包含估值或题材判断，必须区分事实和推断。

如果依赖缺失、网络不可达或接口下线，说明具体缺口，并只基于已取得或用户提供的数据继续。
