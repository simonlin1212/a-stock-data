# 通用约定

## 依赖

```bash
pip install -r requirements.txt
```

- `mootdx`：通达信 TCP 行情、财务快照、F10。
- `requests`：所有 HTTP 数据源。
- `pandas`：表格解析和 DataFrame 输出。
- `lxml`：`pandas.read_html()` 解析同花顺一致预期表格。
- `stockstats`：技术指标扩展，当前端点不强制使用。

`iwencai` 语义研报搜索额外需要：

```bash
export IWENCAI_API_KEY="your_key_here"
export IWENCAI_BASE_URL="https://openapi.iwencai.com"
```

读取规则：仅从环境变量 `IWENCAI_API_KEY` 读取。若缺失，调用 iwencai 端点会报错并提示从 https://www.iwencai.com/skillhub 获取 key 后设置环境变量。

不要把 key 写入 README、SKILL.md、references、`local-validation/` 或其他文件。

其他数据源无需 key。

## 代码格式

所有脚本入口在 `scripts/a_stock_client.py`。优先执行脚本函数，不要把完整端点代码读入上下文。

```python
from scripts.a_stock_client import tencent_quote

quote = tencent_quote(["600519"])
```

命令行入口：

```bash
python scripts/a_stock_client.py tencent_quote 600519
python scripts/a_stock_client.py full_valuation 688017
```

## Ticker 归一化

`normalize_code()` 支持：

| 输入 | 输出 |
|---|---|
| `688017` | `688017` |
| `SH688017` / `sh688017` | `688017` |
| `688017.SH` / `688017.sh` | `688017` |
| `SZ000001` | `000001` |
| `BJ832000` | `832000` |

## 市场前缀

`get_prefix()` 规则：

| 代码开头 | 前缀 |
|---|---|
| `6` / `9` | `sh` |
| `8` | `bj` |
| 其他 | `sz` |

## 数据源优先级

原则：行情、K线、实时价、市值、财务快照能从通达信或腾讯拿到的，一律优先使用它们。东财只用于独有数据，并且必须经 `em_get()` 串行限流。

| 优先级 | 数据源 | 用途 | 风险 |
|---|---|---|---|
| 1 | mootdx 通达信 | K线、五档、逐笔、财务快照、F10 | 不封 IP |
| 2 | 腾讯财经 | 实时价、PE/PB、市值、换手率、涨跌停、指数、ETF | 不封 IP |
| 3 | 同花顺热点/北向 | 强势股、题材归因、北向资金 | 极低 |
| 4 | 百度股市通 | 概念板块、K线 | 极低 |
| 5 | 新浪财经 | 财报三表 | 低 |
| 6 | 巨潮 cninfo | 公告全文 | 低 |
| 7 | 同花顺一致预期 | EPS 一致预期 | 低 |
| 8 | iwencai | NL 语义研报搜索 | 需 key |
| 末位 | 东财 datacenter/push2/reportapi/search/np-weblist | 龙虎榜、解禁、两融、大宗、股东户数、分红、资金流、研报、新闻 | 有风控 |

## 东财防封

所有 `eastmoney.com` 请求必须走 `em_get()`。

`em_get()` 内置：

- `EM_SESSION` 会话复用。
- `EM_SESSION.trust_env = False`，东财请求默认不继承系统代理；直连失败后才尝试一次环境代理 fallback。
- `EM_MIN_INTERVAL=1.0` 秒最小间隔。
- 0.1-0.5 秒随机抖动。
- 默认 UA。

批量筛选时把 `EM_MIN_INTERVAL` 调大到 1.5-2 秒。不要并发请求东财接口。

## 输出要求

回答中必须说明：

- 数据源。
- 观察日期或公告/报告日期。
- 缺失字段。
- 接口下线、无 key、无覆盖、非交易日等 caveat。

不要用训练数据补当前市场价格、资金流、公告、新闻、研报。
