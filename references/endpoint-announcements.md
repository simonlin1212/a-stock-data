# 公告层

使用场景：公告全文检索、公告摘要。

## 函数

| 需求 | 函数 | 数据源 | 说明 |
|---|---|---|---|
| 巨潮公告 | `cninfo_announcements(code, page_size=30)` | 巨潮 cninfo | 沪深北交所公告全文检索，动态解析真实 orgId。 |
| 时间转换 | `_cninfo_ts_to_date(ts)` | 本地 | 将巨潮毫秒时间戳转日期。 |
| F10 公告摘要 | `mootdx_f10_section(code, name)` | mootdx | 适合快速查看最新提示。 |

## 巨潮参数

`stock` 参数使用 `{code},{orgId}`。V3.2.2 后脚本会优先拉取巨潮官方 `szse_stock.json` 映射表获取真实 `orgId`，解决部分 601xxx、688xxx 股票按硬编码规则查不到公告的问题；映射表不可用时再回退旧格式。

- 上海：`600519,gssh0600519`
- 深圳：`000001,gssz0000001`
- 北交：`832000,gsbj0832000`

旧格式仅作为 fallback 使用。

## Caveat

- 巨潮适合公告全文检索。
- mootdx F10 适合公告摘要和快速提示。
- 巨潮公告标题中的 HTML/格式字符需要在输出时清理。
