# 主题和产业链调研工作流

使用场景：主题研报、产业链调研、题材归因、热点强度验证。

## 主题研报

1. 有 iwencai key 时，用 `iwencai_search(query, channel="report", size=50)` 多关键词检索。
2. 用 `dedup_articles()` 去重。
3. 对核心标的用 `eastmoney_reports(code)` 补充个股研报。
4. 需要 PDF 时用 `download_pdf(record)`。
5. 输出研报标题、机构、日期、标的、核心观点和 PDF 链接。

## 题材归因

1. `ths_hot_reason()` 获取强势股和题材 reason。
2. 对 reason 做词频或主题聚类。
3. 用 `industry_comparison()` 检查行业涨跌同步性。
4. 对重点标的用 `baidu_concept_blocks(code)` 验证概念归属。
5. 用 `eastmoney_fund_flow_minute(code)` 验证当日资金方向。

## 新标的快速调研

按顺序执行：

1. `eastmoney_reports(code)`：是否有机构覆盖。
2. `tencent_quote([code])`：实时估值。
3. `ths_eps_forecast(code)`：一致预期。
4. `baidu_concept_blocks(code)`：行业/概念。
5. `eastmoney_fund_flow_minute(code)`：当日资金。
6. `stock_fund_flow_120d(code)`：资金持续性。
7. `dragon_tiger_board(code, today)`：席位。
8. `lockup_expiry(code, today)`：解禁。
9. `margin_trading(code)`：融资融券。
10. `holder_num_change(code)`：筹码集中度。

## 输出要求

- 主题结论必须区分“数据事实”和“推断”。
- 研报和公告必须给出日期。
- 不要把题材 reason 直接当成基本面结论。
