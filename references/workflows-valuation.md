# 单票估值工作流

使用场景：用户要求“帮我估一下某只 A 股”“给我 PE/PEG/消化时间”“新标的快速判断估值”。

## 输入

- 必需：6 位股票代码或可归一化代码。
- 可选：目标 PE、用户指定 EPS、用户指定 CAGR。

## 推荐步骤

1. `tencent_quote([code])` 获取实时价、PE(TTM)、PB、市值、涨跌幅。
2. `ths_eps_forecast(code)` 获取一致预期 EPS。
3. `forward_pe()` 计算前向 PE。
4. 用最近两年 EPS 预测计算 CAGR。
5. `pe_digestion()` 计算消化到目标 PE 的年数。
6. `calc_peg()` 计算 PEG。
7. `eastmoney_concept_blocks(code)` 获取行业/概念/地域混合板块归属。
8. `eastmoney_fund_flow_minute(code)` 和 `stock_fund_flow_120d(code)` 检查资金方向。
9. `dragon_tiger_board(code, trade_date)` 检查席位异动。
10. `lockup_expiry(code, trade_date)` 检查未来解禁。
11. `margin_trading(code)` 和 `holder_num_change(code)` 补充杠杆资金和筹码变化。

也可直接调用 `full_valuation(code)` 获得基础估值结果，再按需要补充信号层和筹码层。

## 输出格式

1. 估值摘要：价格、PE(TTM)、PB、前向 PE、PEG、消化年数。
2. EPS 依据：来源、年份、机构数。
3. 行业/概念：主要板块。
4. 资金和事件：资金流、龙虎榜、解禁、两融、股东户数。
5. Caveat：缺失数据、机构覆盖不足、非交易日、接口返回空。

## 缺失数据处理

- 一致预期为空：只给 PE(TTM) 和框架，不强算前向 PE。
- 机构数少于 3：标注低置信度。
- 资金流为空：说明可能是非交易日、盘前或接口延迟。
