# 信号层

使用场景：题材归因、强势股、北向资金、概念板块、资金流、龙虎榜、限售解禁、行业轮动。

## 函数

| 需求 | 函数 | 数据源 | 说明 |
|---|---|---|---|
| 当日强势股/题材 | `ths_hot_reason(date=None)` | 同花顺热点 | 返回强势股和 reason tags。 |
| 北向实时 | `hsgt_realtime()` | 同花顺北向 | 沪股通/深股通分钟级累计净买入。 |
| 北向缓存路径 | `_northbound_cache_path()` | 本地 | 历史缓存 CSV。 |
| 保存北向快照 | `_save_northbound_snapshot(date, hgt, sgt)` | 本地 | 收盘后积累历史。 |
| 读取北向历史 | `_load_northbound_history(n=20)` | 本地 | 只包含本地已缓存日期。 |
| 板块归属 | `eastmoney_concept_blocks(code)` / `baidu_concept_blocks(code)` | 东财 slist | 行业/概念/地域混合板块归属；旧百度函数名保留兼容。 |
| 分钟资金流 | `eastmoney_fund_flow_minute(code)` | 东财 push2 | 主力/超大单/大单/中单/小单分钟净流入。 |
| 龙虎榜席位 | `dragon_tiger_board(code, trade_date, look_back=30)` | 东财 datacenter | 上榜记录、买卖席位、机构动向。 |
| 限售解禁 | `lockup_expiry(code, trade_date, forward_days=90)` | 东财 datacenter | 历史解禁和未来解禁。 |
| 行业排名 | `industry_comparison(top_n=20)` | 东财 push2 | 行业涨跌、上涨/下跌家数、领涨股。 |
| 全市场龙虎榜 | `daily_dragon_tiger(trade_date=None, min_net_buy=None)` | 东财 datacenter | 每日全市场上榜股票和净买额。 |

## 组合使用

题材热度 + 资金验证：

1. `ths_hot_reason()` 找强势股和题材词。
2. `eastmoney_fund_flow_minute()` 看个股当日资金方向。
3. `stock_fund_flow_120d()` 看日级资金持续性。
4. `industry_comparison()` 验证行业层面的同步性。
5. `dragon_tiger_board()` 判断是否有席位或机构异动。

## Caveat

- 北向历史是本地自缓存，不代表全历史。
- 东财资金流替代了已下线的百度 PAE 资金流。
- 龙虎榜、解禁、行业数据都属于东财独有数据，必须经 `em_get()` 限流。
- 非交易日或盘后未更新时，全市场龙虎榜可能返回空。
