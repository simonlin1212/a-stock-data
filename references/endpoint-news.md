# 新闻层

使用场景：个股新闻、全市场 7x24 快讯。

## 函数

| 需求 | 函数 | 数据源 | 说明 |
|---|---|---|---|
| 个股新闻 | `eastmoney_stock_news(code, page_size=20)` | 东财 search-api-web | 返回标题、摘要、时间、媒体、URL。 |
| 全市场快讯 | `eastmoney_global_news(page_size=50)` | 东财 np-weblist | 7x24 财经资讯。 |
| 财联社旧入口 | `cls_telegraph(page_size=50)` | 已下线 | 兼容 stub，返回空列表。 |

## V3.2.1 修复点

`eastmoney_stock_news()` 按东财实际结构解析：`result.cmsArticleWebOld` 直接是文章列表，不再按 `{list: [...]}` 嵌套读取。

## 财联社下线

`cls.cn/nodeapi/telegraphList` 等旧 API 已全面 404。用户要求“财联社快讯”时：

1. 说明旧公开接口已下线。
2. 默认改用 `eastmoney_global_news()`。
3. 不把 `cls_telegraph()` 作为有效端点计入 27 个端点。
