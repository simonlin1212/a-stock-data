# 行情层

使用场景：实时行情、K线、盘口、逐笔、PE/PB、市值、换手率、涨跌停、指数和 ETF。

## 函数

| 需求 | 函数 | 数据源 | 说明 |
|---|---|---|---|
| K线 | `mootdx_bars(code, category=4, offset=10)` | mootdx | 多周期 K线。 |
| 实时报价/盘口 | `mootdx_quotes(codes)` | mootdx | 返回价格、五档、成交量等通达信字段。 |
| 逐笔成交 | `mootdx_transactions(code, date)` | mootdx | 非交易时间可能为空。 |
| PE/PB/市值/涨跌停 | `tencent_quote(codes)` | 腾讯财经 | 支持股票、指数、ETF。 |
| 百度 K线带 MA | `baidu_kline_with_ma(code, start_time="")` | 百度股市通 | 返回 MA5/MA10/MA20。 |

## mootdx category

| category | 周期 |
|---|---|
| 4 | 日线 |
| 5 | 周线 |
| 6 | 月线 |
| 7 | 1 分钟 |
| 8 | 5 分钟 |
| 9 | 15 分钟 |
| 10 | 30 分钟 |
| 11 | 60 分钟 |

mootdx 不提供 PE、PB、市值、换手率、涨跌停价，这些走 `tencent_quote()`。

## 腾讯字段重点

`tencent_quote()` 已解析常用字段：

- `price`
- `last_close`
- `open`
- `change_amt`
- `change_pct`
- `high`
- `low`
- `amount_wan`
- `turnover_pct`
- `pe_ttm`
- `mcap_yi`
- `float_mcap_yi`
- `pb`
- `limit_up`
- `limit_down`
- `vol_ratio`
- `pe_static`

腾讯返回 GBK 编码和 `~` 分隔字段，脚本已处理。

## Caveat

- 交易时间外，逐笔成交可能为空。
- 百度 `ResultCode` 历史上存在 int/string 不稳定，脚本按结果结构容错。
- 指数和 ETF 代码也可交给 `tencent_quote()`，但口径与个股字段不完全一致。
