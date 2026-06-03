# 基础数据层

使用场景：财务快照、F10、个股基本面、财报三表。

## 函数

| 需求 | 函数 | 数据源 | 说明 |
|---|---|---|---|
| 季报快照 | `mootdx_finance(code)` | mootdx | 37 字段，包括 EPS、ROE、净利润、收入等。 |
| F10 | `mootdx_f10(code, name=None)` | mootdx | 公司资料、股东研究、最新提示等。 |
| F10 栏目 | `mootdx_f10_section(code, name)` | mootdx | 读取指定栏目。 |
| 个股基本面 | `eastmoney_stock_info(code)` | 东财 push2 | 行业、股本、市值、上市日期。 |
| 财报三表 | `sina_financial_report(code, report_type="lrb", num=8)` | 新浪 | 利润表、资产负债表、现金流量表。 |

## 新浪三表

`report_type`：

| 值 | 报表 |
|---|---|
| `lrb` | 利润表 |
| `fzb` | 资产负债表 |
| `llb` | 现金流量表 |

V3.2.1 修复点：新浪实际结构是 `result.data.report_list`，按报告期为键；每期对象的 `data` 字段才是行项列表。脚本已按这个结构解析。

## F10 Caveat

F10 文本可能很长。做摘要时只读取用户需要的栏目，不要把全部 F10 文本放入上下文。
