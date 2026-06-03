# 批量筛选和横向对比

使用场景：用户要求比较多只股票估值、行业内筛选、批量查看资金或筹码。

## 输入

- 2 只以上股票代码。
- 可选：行业、主题、估值指标、排序字段。

## 推荐步骤

1. 用 `normalize_code()` 清洗代码。
2. 用 `tencent_quote(codes)` 批量获取实时价、PE、PB、市值、换手率。
3. 对每只股票尝试 `ths_eps_forecast(code)` 获取一致预期。
4. 计算前向 PE、PEG 和消化年数。
5. 必要时补充：
   - `stock_fund_flow_120d(code)`：资金持续性。
   - `margin_trading(code)`：两融趋势。
   - `holder_num_change(code)`：筹码集中度。
   - `lockup_expiry(code, today)`：解禁风险。

## 输出格式

用表格输出：

| 代码 | 名称 | 现价 | 市值 | PE(TTM) | PB | 前向 PE | PEG | 消化年数 | 机构数 | Caveat |
|---|---|---|---|---|---|---|---|---|---|---|

## 批量调用规则

- 腾讯可以批量拉取。
- 东财端点必须串行，必要时调大 `EM_MIN_INTERVAL`。
- iwencai 不适合作为每只股票循环高频调用。
