# Layer 4: 资金面 / 筹码层（V3.0 新增）

> 依赖 SKILL.md 的 `eastmoney_datacenter()` helper。

## 4.1 融资融券明细

```python
def margin_trading(code: str, page_size: int = 30) -> list[dict]:
    """
    融资融券明细（日级）。
    返回: [{date, rzye(融资余额), rzmre(融资买入), rqye(融券余额), ...}]
    """
    data = eastmoney_datacenter(
        "RPTA_WEB_RZRQ_GGMX",
        filter_str=f'(SCODE="{code}")',
        page_size=page_size,
        sort_columns="DATE", sort_types="-1",
    )
    return [{
        "date": str(row.get("DATE", ""))[:10],
        "rzye": row.get("RZYE", 0),       # 融资余额（元）
        "rzmre": row.get("RZMRE", 0),     # 融资买入额
        "rzche": row.get("RZCHE", 0),     # 融资偿还额
        "rqye": row.get("RQYE", 0),       # 融券余额（元）
        "rqmcl": row.get("RQMCL", 0),     # 融券卖出量
        "rqchl": row.get("RQCHL", 0),     # 融券偿还量
        "rzrqye": row.get("RZRQYE", 0),   # 融资融券余额合计
    } for row in data]

# 用法
data = margin_trading("600519")
for d in data[:5]:
    print(f"{d['date']}: 融资余额={d['rzye']/1e8:.2f}亿 融券余额={d['rqye']/1e8:.2f}亿")
```

---

## 4.2 大宗交易

```python
def block_trade(code: str, page_size: int = 20) -> list[dict]:
    """
    大宗交易记录。
    返回: [{date, price, vol, amount, buyer, seller, premium_pct}]
    """
    data = eastmoney_datacenter(
        "RPT_DATA_OCCURTRADE",
        filter_str=f'(SECURITY_CODE="{code}")',
        page_size=page_size,
        sort_columns="TRADE_DATE", sort_types="-1",
    )
    rows = []
    for row in data:
        close = row.get("CLOSE_PRICE") or 0
        deal_price = row.get("DEAL_PRICE") or 0
        premium = ((deal_price / close - 1) * 100) if close else 0
        rows.append({
            "date": str(row.get("TRADE_DATE", ""))[:10],
            "price": deal_price,
            "close": close,
            "premium_pct": round(premium, 2),
            "vol": row.get("DEAL_VOL", 0),
            "amount": row.get("DEAL_AMT", 0),
            "buyer": row.get("BUYER_NAME", ""),
            "seller": row.get("SELLER_NAME", ""),
        })
    return rows
```

---

## 4.3 股东户数变化

```python
def holder_num_change(code: str, page_size: int = 10) -> list[dict]:
    """
    股东户数变化（季度级）。
    返回: [{date, holder_num, change_num, change_ratio, avg_shares}]
    股东户数持续减少 = 筹码集中 = 主力吸筹信号
    """
    data = eastmoney_datacenter(
        "RPT_HOLDERNUMLATEST",
        filter_str=f'(SECURITY_CODE="{code}")',
        page_size=page_size,
        sort_columns="END_DATE", sort_types="-1",
    )
    return [{
        "date": str(row.get("END_DATE", ""))[:10],
        "holder_num": row.get("HOLDER_NUM", 0),
        "change_num": row.get("HOLDER_NUM_CHANGE", 0),
        "change_ratio": row.get("HOLDER_NUM_RATIO", 0),  # 环比 %
        "avg_shares": row.get("AVG_FREE_SHARES", 0),     # 户均持股
    } for row in data]
```

---

## 4.4 分红送转历史

```python
def dividend_history(code: str, page_size: int = 20) -> list[dict]:
    """
    分红送转历史。
    返回: [{date, bonus_rmb(每股派息), transfer_ratio(转增比例), bonus_ratio(送股比例)}]
    """
    data = eastmoney_datacenter(
        "RPT_SHAREBONUS_DET",
        filter_str=f'(SECURITY_CODE="{code}")',
        page_size=page_size,
        sort_columns="EX_DIVIDEND_DATE", sort_types="-1",
    )
    return [{
        "date": str(row.get("EX_DIVIDEND_DATE", ""))[:10],
        "bonus_rmb": row.get("PRETAX_BONUS_RMB", 0),    # 每股派息（税前）
        "transfer_ratio": row.get("TRANSFER_RATIO", 0),  # 每 10 股转增
        "bonus_ratio": row.get("BONUS_RATIO", 0),        # 每 10 股送股
        "plan": row.get("ASSIGN_PROGRESS", ""),           # 进度
    } for row in data]
```

---

## 4.5 个股资金流（120 日，日级）

```python
import requests

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

def stock_fund_flow_120d(code: str) -> list[dict]:
    """
    个股资金流（日级，最近 120 个交易日）。
    返回: [{date, main_net(主力净流入), small_net, mid_net, large_net, super_net}]
    单位: 元
    """
    market_code = 1 if code.startswith("6") else 0
    url = "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
    params = {
        "secid": f"{market_code}.{code}",
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65",
        "lmt": "120",
    }
    r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=15)
    d = r.json()
    klines = d.get("data", {}).get("klines", [])
    rows = []
    for line in klines:
        parts = line.split(",")
        if len(parts) >= 7:
            rows.append({
                "date": parts[0],
                "main_net": float(parts[1]) if parts[1] != "-" else 0,
                "small_net": float(parts[2]) if parts[2] != "-" else 0,
                "mid_net": float(parts[3]) if parts[3] != "-" else 0,
                "large_net": float(parts[4]) if parts[4] != "-" else 0,
                "super_net": float(parts[5]) if parts[5] != "-" else 0,
            })
    return rows

# 用法
data = stock_fund_flow_120d("600519")
for d in data[-5:]:
    print(f"{d['date']}: 主力净流入={d['main_net']/1e4:.0f}万 超大单={d['super_net']/1e4:.0f}万")

# 统计近 20 日主力净流入
recent_20 = data[-20:]
total_main = sum(d["main_net"] for d in recent_20)
print(f"近 20 日主力累计净流入: {total_main/1e8:.2f}亿")
```
