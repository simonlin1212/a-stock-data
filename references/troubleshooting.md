# FAQ 和故障处理

## mootdx 和腾讯有什么区别？

mootdx 提供 K线、五档盘口、逐笔成交、财务快照、F10。腾讯提供实时价、PE/PB、市值、换手率、涨跌停、指数和 ETF。能用 mootdx/腾讯时优先用它们。

## 为什么移除 akshare？

akshare 是公开 API 的封装层，会增加版本兼容和中间层故障点。当前架构直连底层 HTTP API，仅保留 mootdx 作为 TCP 行情依赖。

## iwencai 返回 401

检查环境变量 `IWENCAI_API_KEY`、`IWENCAI_BASE_URL` 和 X-Claw 权限。无 key 时可从 https://www.iwencai.com/skillhub 获取，并设置环境变量；仍不提供 key 时只能使用东财研报和其他公开源。

## 同花顺一致预期为空

可能是机构覆盖不足、页面结构变化或网络问题。机构数少于 3 时也要降低置信度。

## 东财 PDF 403

通常是 Referer 或下载链接字段缺失。使用 `download_pdf(record)`，不要手写裸下载请求。

## 腾讯乱码

腾讯行情接口返回 GBK 编码。`tencent_quote()` 已处理。

## 腾讯字段 43 是 PB 吗？

不是。常用口径：`f39` 为 PE(TTM)，`f44` 总市值，`f45` 流通市值，`f46` PB，`f47/f48` 涨跌停价。

## 哪些数据源需要 key？

只有 iwencai 需要。mootdx、腾讯、东财、同花顺、百度、巨潮、新浪无需 key。

## 北向历史为什么只有最近几天？

北向历史为本地自缓存，每次调用后逐步积累，不是全历史接口。

## 行业板块为什么从同花顺换成东财？

同花顺行业接口出现 401 反爬，V3.0 起切换为东财 push2 行业板块。

## 海外服务器 mootdx 超时

mootdx 走通达信 TCP 7709，海外服务器可能连接质量差。可优先用腾讯和 HTTP 源。

## 财联社快讯为什么为空？

财联社旧公开 API 已于 2026-05 下线。`cls_telegraph()` 只保留兼容入口，默认返回空；使用 `eastmoney_global_news()` 替代。

## 东财封 IP 或请求失败

所有东财请求必须经 `em_get()`。批量任务调大 `EM_MIN_INTERVAL`，不要并发请求，不要 1 分钟内高频刷同一源。

## V3.2.1 修复了什么？

- 东财个股新闻：`result.cmsArticleWebOld` 直接是文章列表。
- 新浪财报三表：实际结构为 `result.data.report_list`，每期对象的 `data` 字段才是行项列表。
