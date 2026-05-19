# Layer 6: 基础数据层

## 6.1 mootdx 财务快照（37 字段季报数据）

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')

# market: 0=深圳, 1=上海
fin = client.finance(symbol='688017')
# 返回 37 个字段的季报快照:
#   liutongguben(流通股本), zongguben(总股本)
#   eps(每股收益), bvps(每股净资产), roe(净资产收益率%)
#   profit(净利润), income(主营收入)
#   meigujingzichan(每股净资产), meigugongjijin(每股公积金)
#   meiguweifeipeili(每股未分配利润)
#   等 37 个季报财务字段
```

---

## 6.2 mootdx F10（公司文本资料）

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')

# 9 大类文本数据:
categories = [
    "最新提示", "公司概况", "财务分析",
    "股东研究", "股本结构", "资本运作",
    "业内点评", "行业分析", "公司大事",
]
for cat in categories:
    text = client.F10(symbol='688017', name=cat)
    print(f"=== {cat} ===")
    print(text[:200] if text else "(空)")
```

> **优化提示**："股东研究" 中的【4. 股东变化】章节含大量历史十大股东列表，实测 16000+ chars。建议只保留最新一期（-70% token）。

---

## 6.3 东财个股基本面（直连 push2 API）

```python
import requests

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

def eastmoney_stock_info(code: str) -> dict:
    """
    东财个股基本面信息。
    返回: {code, name, industry, total_shares, float_shares, mcap, float_mcap, list_date}
    """
    market_code = 1 if code.startswith("6") else 0
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "fltt": "2", "invt": "2",
        "fields": "f57,f58,f84,f85,f127,f116,f117,f189,f43",
        "secid": f"{market_code}.{code}",
    }
    r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=10)
    d = r.json().get("data", {})
    return {
        "code": d.get("f57", ""),
        "name": d.get("f58", ""),
        "industry": d.get("f127", ""),
        "total_shares": d.get("f84", 0),     # 总股本（股）
        "float_shares": d.get("f85", 0),     # 流通股（股）
        "mcap": d.get("f116", 0),            # 总市值（元）
        "float_mcap": d.get("f117", 0),      # 流通市值（元）
        "list_date": str(d.get("f189", "")), # 上市日期 YYYYMMDD
        "price": d.get("f43", 0),
    }
```

---

## 6.4 新浪财报三表（资产负债表 / 利润表 / 现金流量表）

```python
def sina_financial_report(code: str, report_type: str = "lrb") -> list[dict]:
    """
    新浪财报三表。
    code: 6 位代码
    report_type: "fzb"(资产负债表) / "lrb"(利润表) / "llb"(现金流量表)
    返回: 按报告期排序的财务数据列表
    """
    prefix = "sh" if code.startswith("6") else "sz"
    paper_code = f"{prefix}{code}"
    url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
    params = {
        "paperCode": paper_code,
        "source": report_type,
        "type": "0",
        "page": "1",
        "num": "20",  # 最近 20 期
    }
    r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=15)
    d = r.json()
    result = d.get("result", {}).get("data", {})
    items = result.get(report_type, [])
    return items if isinstance(items, list) else []

# 用法
lrb = sina_financial_report("600519", "lrb")  # 利润表
fzb = sina_financial_report("600519", "fzb")  # 资产负债表
llb = sina_financial_report("600519", "llb")  # 现金流量表
```
