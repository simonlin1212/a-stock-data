# 研报层

使用场景：个股研报、研报 PDF、机构评级、三年 EPS 预测、一致预期 EPS、自然语言主题研报检索。

## 函数

| 需求 | 函数 | 数据源 | 说明 |
|---|---|---|---|
| 研报列表 | `eastmoney_reports(code, max_pages=5)` | 东财 reportapi | 返回研报列表、评级、EPS 预测字段。 |
| PDF 下载 | `download_pdf(record, target_dir="./reports")` | 东财 PDF | 从研报 record 下载 PDF。 |
| 一致预期 EPS | `ths_eps_forecast(code)` | 同花顺 | 直连 `basic.10jqka.com.cn`。 |
| iwencai 搜索 | `iwencai_search(query, channel="report", size=50)` | iwencai OpenAPI | 需要环境变量 `IWENCAI_API_KEY`。 |
| iwencai 查询 | `iwencai_query(query, page=1, limit=50)` | iwencai OpenAPI | 兼容查询入口。 |
| 研报去重 | `dedup_articles(articles)` | 本地 | 按标题/链接去重。 |

## 研报字段

东财 record 常见字段：

- `infoCode`：PDF 下载所需。
- `title`：研报标题。
- `orgSName`：机构。
- `publishDate`：发布日期。
- `emRatingName`：评级。
- `predictNextTwoYearEps` 等 EPS 预测字段。

PDF 下载需要东财 Referer，脚本已处理。

## 一致预期 Caveat

- 同花顺一致预期为空通常表示机构覆盖不足或页面结构变化。
- 预测机构数少于 3 时，不应把一致预期作为强结论。

## iwencai Caveat

- 只有 iwencai 需要 key。
- 401 通常是 `IWENCAI_API_KEY` 缺失、过期或 X-Claw 配置不可用。无 key 时可从 https://www.iwencai.com/skillhub 获取，并设置环境变量 `IWENCAI_API_KEY`。
- 无 key 时可退回东财个股研报和主题关键词检索，但自然语言跨主题能力会下降。
