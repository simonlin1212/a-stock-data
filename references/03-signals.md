# Layer 3: 信号层

> 用到 `eastmoney_datacenter` helper 时请回到 SKILL.md 的 Common Utilities 复制定义。

## 3.1 同花顺热点 — 当日强势股 + 题材归因（独家）

**核心价值**：不只告诉你"哪些走强"，还告诉你"为什么走强" — 同花顺编辑部人工运营的题材标签。

```python
import requests
import pandas as pd
from datetime import date as _date

def ths_hot_reason(date: str = None) -> pd.DataFrame:
    """
    同花顺当日强势股归因。
    date: 'YYYY-MM-DD' 格式，None=今天
    返回 DataFrame，含每只股票的题材标签 (reason)。
    实测: 73ms 拿到 ~125 只 + 完整字段
    """
    if date is None:
        date = _date.today().strftime("%Y-%m-%d")

    url = (
        f"http://zx.10jqka.com.cn/event/api/getharden/"
        f"date/{date}/orderby/date/orderway/desc/charset/GBK/"
    )
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "Chrome/117.0.0.0 Safari/537.36"
        )
    }
    r = requests.get(url, headers=headers, timeout=10)
    data = r.json()
    if data.get("errocode", 0) != 0:
        raise RuntimeError(f"同花顺热点错误: {data.get('errormsg', '')}")

    rows = data.get("data") or []
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    rename_map = {
        "name": "名称", "code": "代码", "reason": "题材归因",
        "close": "收盘价", "zhangdie": "涨跌额", "zhangfu": "涨幅%",
        "huanshou": "换手率%", "chengjiaoe": "成交额",
        "chengjiaoliang": "成交量", "ddejingliang": "大单净量",
        "market": "市场",
    }
    return df.rename(columns=rename_map)

# 用法
df = ths_hot_reason("2026-05-09")
print(f"当日强势股: {len(df)} 只")
print(df[["代码", "名称", "涨幅%", "题材归因"]].head(10))
```

### 同花顺热点字段速查

| 原字段 | 中文 | 说明 |
|---|---|---|
| code | 代码 | 6 位股票代码 |
| name | 名称 | 简称 |
| **reason** | **题材归因** | **核心字段，人工运营 tags，如"算力租赁+Token工厂+AI政务"** |
| zhangfu | 涨幅% | 当日涨幅 |
| huanshou | 换手率% | 当日换手 |
| chengjiaoe | 成交额 | 元 |
| ddejingliang | 大单净量 | 主力净流入指标 |

---

## 3.2 同花顺北向资金 — hsgtApi 实时分钟流向 + 本地自缓存历史

> **已知行业性问题**：eastmoney 全系北向数据自 2024-08 后净买额字段返回 NaN/0，属上游断供。已改为**本地 CSV 自缓存模式** —— 每次拉实时数据后自动写入本地 CSV，历史越跑越丰富。

```python
import requests
import pandas as pd
from pathlib import Path

HSGT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "Chrome/117.0.0.0 Safari/537.36"
    ),
    "Host": "data.hexin.cn",
    "Referer": "https://data.hexin.cn/",
}

def hsgt_realtime() -> pd.DataFrame:
    """
    沪深股通当日实时分钟流向（含集合竞价 09:10–15:00，262 个时间点）。
    返回字段: time, hgt(沪股通累计净买入), sgt(深股通累计净买入)
    单位: 亿元
    """
    url = "https://data.hexin.cn/market/hsgtApi/method/dayChart/"
    r = requests.get(url, headers=HSGT_HEADERS, timeout=10)
    d = r.json()
    times = d.get("time", [])
    hgt = d.get("hgt", [])
    sgt = d.get("sgt", [])
    n = len(times)
    return pd.DataFrame({
        "time": times,
        "hgt_yi": hgt[:n] + [None] * (n - len(hgt)),
        "sgt_yi": sgt[:n] + [None] * (n - len(sgt)),
    })


def _northbound_cache_path() -> Path:
    """北向资金本地 CSV 缓存路径"""
    p = Path.home() / ".tradingagents" / "cache" / "northbound_daily.csv"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _save_northbound_snapshot(date: str, hgt: float, sgt: float):
    """写入/更新当天北向收盘数据到 CSV"""
    path = _northbound_cache_path()
    rows = {}
    if path.exists():
        for line in path.read_text().strip().split("\n")[1:]:
            parts = line.split(",")
            if len(parts) == 3:
                rows[parts[0]] = line
    rows[date] = f"{date},{hgt},{sgt}"
    with open(path, "w") as f:
        f.write("date,hgt,sgt\n")
        for d in sorted(rows.keys()):
            f.write(rows[d] + "\n")


def _load_northbound_history(n: int = 20) -> pd.DataFrame:
    path = _northbound_cache_path()
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    return df.tail(n)


# 用法 1: 实时分钟流向
df = hsgt_realtime()
print(f"分钟点数: {len(df)}")

# 用法 2: 自动缓存今日收盘数据
if not df.empty:
    last = df.dropna().iloc[-1]
    _save_northbound_snapshot("2026-05-17", last["hgt_yi"], last["sgt_yi"])

# 用法 3: 读取历史
hist = _load_northbound_history(20)
print(hist)
```

---

## 3.3 百度股市通 — 概念板块归属

```python
import requests

_BAIDU_PAE_HEADERS = {
    "Host": "finance.pae.baidu.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117.0.0.0",
    "Accept": "application/vnd.finance-web.v1+json",
    "Origin": "https://gushitong.baidu.com",
    "Referer": "https://gushitong.baidu.com/",
}

def baidu_concept_blocks(code: str) -> dict:
    """
    百度股市通概念板块归属。
    返回: {industry: [...], concept: [...], region: [...], concept_tags: [...]}
    """
    url = (
        f"https://finance.pae.baidu.com/api/getrelatedblock"
        f"?code={code}&market=ab&typeCode=all&finClientType=pc"
    )
    r = requests.get(url, headers=_BAIDU_PAE_HEADERS, timeout=10)
    d = r.json()
    if str(d.get("ResultCode", -1)) != "0":
        raise RuntimeError(f"百度PAE错误: {d}")

    result = {"industry": [], "concept": [], "region": [], "concept_tags": []}
    for block in d.get("Result", []):
        block_type = block.get("type", "")
        for item in block.get("list", []):
            entry = {
                "name": item.get("name", ""),
                "change_pct": item.get("increase", ""),
                "desc": item.get("desc", ""),
            }
            if "行业" in block_type:
                result["industry"].append(entry)
            elif "概念" in block_type:
                result["concept"].append(entry)
                result["concept_tags"].append(entry["name"])
            elif "地域" in block_type:
                result["region"].append(entry)
    return result

# 用法
blocks = baidu_concept_blocks("688017")
print("行业:", [b["name"] for b in blocks["industry"]])
print("概念:", blocks["concept_tags"])
print("地域:", [b["name"] for b in blocks["region"]])
```

> **踩坑**：`ResultCode` 返回类型不稳定 — 有时 int `0`，有时 string `"0"`。必须用 `str()` 统一比较。

---

## 3.4 百度股市通 — 个股资金流向（分钟级）

```python
def baidu_fund_flow_realtime(code: str, date: str) -> list[dict]:
    """
    个股资金流向（分钟级）。date: YYYYMMDD 紧凑格式。
    返回: [{time, mainForce, retail, super, large, price}, ...]
    """
    url = (
        f"https://finance.pae.baidu.com/vapi/v1/fundflow"
        f"?code={code}&market=ab&date={date}&finClientType=pc"
    )
    r = requests.get(url, headers=_BAIDU_PAE_HEADERS, timeout=10)
    d = r.json()
    if str(d.get("ResultCode", -1)) != "0":
        return []
    raw = d.get("Result", {}).get("update_data", "")
    if not raw:
        return []
    rows = []
    for segment in raw.split(";"):
        parts = segment.split(",")
        if len(parts) >= 9:
            rows.append({
                "time": parts[0],
                "mainForce": float(parts[2]) if parts[2] else 0,
                "retail": float(parts[3]) if parts[3] else 0,
                "super": float(parts[4]) if parts[4] else 0,
                "large": float(parts[5]) if parts[5] else 0,
                "price": float(parts[8]) if parts[8] else 0,
            })
    return rows


def baidu_fund_flow_history(code: str, days: int = 20) -> list[dict]:
    """
    个股资金流向（日级，最近 N 交易日）。
    返回: [{date, close, change_pct, superNetIn, largeNetIn, mediumNetIn, littleNetIn, mainIn}, ...]
    """
    url = (
        f"https://finance.pae.baidu.com/vapi/v1/fundsortlist"
        f"?code={code}&market=ab&pn=0&rn={days}&finClientType=pc"
    )
    r = requests.get(url, headers=_BAIDU_PAE_HEADERS, timeout=10)
    d = r.json()
    if str(d.get("ResultCode", -1)) != "0":
        return []
    rows = []
    for item in d.get("Result", {}).get("list", []):
        rows.append({
            "date": item.get("showtime", ""),
            "close": item.get("closepx", ""),
            "change_pct": item.get("ratio", ""),
            "superNetIn": item.get("superNetIn", ""),
            "largeNetIn": item.get("largeNetIn", ""),
            "mediumNetIn": item.get("mediumNetIn", ""),
            "littleNetIn": item.get("littleNetIn", ""),
            "mainIn": item.get("extMainIn", ""),
        })
    return rows
```

> **踩坑**：实时数据格式是分号分隔字符串（非 JSON 数组），`date` 参数用紧凑格式 `20260517` 而非 `2026-05-17`。

---

## 3.5 龙虎榜席位 — 个股上榜记录 + 买卖席位 TOP5 + 机构动向

> 依赖 SKILL.md 的 `eastmoney_datacenter()` helper。

```python
from datetime import datetime, timedelta

def dragon_tiger_board(code: str, trade_date: str, look_back: int = 30) -> dict:
    """
    龙虎榜数据聚合。trade_date: YYYY-MM-DD。
    返回: {records: [...], seats: {buy: [...], sell: [...]}, institution: {...}}
    """
    start = datetime.strptime(trade_date, "%Y-%m-%d") - timedelta(days=look_back)
    start_str = start.strftime("%Y-%m-%d")

    # 1. 上榜记录
    records = []
    data = eastmoney_datacenter(
        "RPT_DAILYBILLBOARD_DETAILSNEW",
        filter_str=f"(TRADE_DATE>='{start_str}')(TRADE_DATE<='{trade_date}')(SECURITY_CODE=\"{code}\")",
        page_size=50, sort_columns="TRADE_DATE", sort_types="-1",
    )
    for row in data:
        records.append({
            "date": str(row.get("TRADE_DATE", ""))[:10],
            "reason": row.get("EXPLANATION", ""),
            "net_buy": round((row.get("BILLBOARD_NET_AMT") or 0) / 10000, 1),
            "turnover": round(float(row.get("TURNOVERRATE") or 0), 2),
        })

    # 2. 最近上榜的买卖席位
    seats = {"buy": [], "sell": []}
    if records:
        latest_date = records[0]["date"]
        buy_data = eastmoney_datacenter(
            "RPT_BILLBOARD_DAILYDETAILSBUY",
            filter_str=f"(TRADE_DATE='{latest_date}')(SECURITY_CODE=\"{code}\")",
            page_size=10, sort_columns="BUY", sort_types="-1",
        )
        for row in buy_data[:5]:
            seats["buy"].append({
                "name": row.get("OPERATEDEPT_NAME", ""),
                "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                "net": round((row.get("NET") or 0) / 10000, 1),
            })
        sell_data = eastmoney_datacenter(
            "RPT_BILLBOARD_DAILYDETAILSSELL",
            filter_str=f"(TRADE_DATE='{latest_date}')(SECURITY_CODE=\"{code}\")",
            page_size=10, sort_columns="SELL", sort_types="-1",
        )
        for row in sell_data[:5]:
            seats["sell"].append({
                "name": row.get("OPERATEDEPT_NAME", ""),
                "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                "net": round((row.get("NET") or 0) / 10000, 1),
            })

    # 3. 机构买卖统计
    institution = {}
    inst_data = eastmoney_datacenter(
        "RPT_ORGANIZATION_BUSSINESS",
        filter_str=f"(SECURITY_CODE=\"{code}\")",
        page_size=1, sort_columns="TRADE_DATE", sort_types="-1",
    )
    if inst_data:
        row = inst_data[0]
        institution = {
            "buy_count": row.get("BUY_TIMES", 0),
            "sell_count": row.get("SELL_TIMES", 0),
            "net_amount": round((row.get("NET_BUY_AMT") or 0) / 10000, 1),
        }

    return {"records": records, "seats": seats, "institution": institution}
```

> **ST 股注意**：5% 涨跌停更容易触发龙虎榜（"连续三日偏离值累计达 12%"）；科创板 20% 涨跌停则较少触发。

---

## 3.6 限售解禁日历 — 历史 + 未来 90 天

```python
from datetime import datetime, timedelta

def lockup_expiry(code: str, trade_date: str, forward_days: int = 90) -> dict:
    """限售解禁日历。返回: {history: [...], upcoming: [...]}"""
    history_data = eastmoney_datacenter(
        "RPT_LIFT_STAGE",
        filter_str=f"(SECURITY_CODE=\"{code}\")",
        page_size=15, sort_columns="FREE_DATE", sort_types="-1",
    )
    history = [{
        "date": str(row.get("FREE_DATE", ""))[:10],
        "type": row.get("LIMITED_STOCK_TYPE", ""),
        "shares": row.get("FREE_SHARES_NUM", 0),
        "ratio": row.get("FREE_RATIO", 0),
    } for row in history_data]

    end_date = datetime.strptime(trade_date, "%Y-%m-%d") + timedelta(days=forward_days)
    end_str = end_date.strftime("%Y-%m-%d")
    upcoming_data = eastmoney_datacenter(
        "RPT_LIFT_STAGE",
        filter_str=f"(SECURITY_CODE=\"{code}\")(FREE_DATE>='{trade_date}')(FREE_DATE<='{end_str}')",
        page_size=20, sort_columns="FREE_DATE", sort_types="1",
    )
    upcoming = [{
        "date": str(row.get("FREE_DATE", ""))[:10],
        "type": row.get("LIMITED_STOCK_TYPE", ""),
        "shares": row.get("FREE_SHARES_NUM", 0),
        "ratio": row.get("FREE_RATIO", 0),
    } for row in upcoming_data]
    return {"history": history, "upcoming": upcoming}
```

**限售股类型参考**：首发原股东限售（IPO 后 1-3 年）/ 首发机构配售（战略配售）/ 定增机构配售（6-18 个月）/ 股权激励限售。

---

## 3.7 行业板块排名（V3.0 改用东财）

```python
import requests

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

def industry_comparison(top_n: int = 20) -> dict:
    """全行业涨跌幅排名（东财行业板块，~100 个行业）。"""
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1", "pz": "100", "po": "1", "np": "1",
        "fltt": "2", "invt": "2", "fs": "m:90+t:2",
        "fields": "f2,f3,f4,f12,f13,f14,f104,f105,f128,f136,f140,f141,f207",
    }
    r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=15)
    d = r.json()
    items = d.get("data", {}).get("diff", [])
    if not items:
        return {"top": [], "bottom": [], "total": 0}

    rows = [{
        "rank": i + 1,
        "name": item.get("f14", ""),
        "change_pct": item.get("f3", 0),
        "code": item.get("f12", ""),
        "up_count": item.get("f104", 0),
        "down_count": item.get("f105", 0),
        "leader": item.get("f140", ""),
        "leader_change": item.get("f136", 0),
    } for i, item in enumerate(items)]

    return {"top": rows[:top_n], "bottom": rows[-top_n:], "total": len(rows)}
```

> 同花顺 `stock_board_industry_summary_ths` 接口 2026 年初加了反爬 401（需登录态），换东财即可。

---

## 3.8 全市场龙虎榜

```python
from datetime import datetime

def daily_dragon_tiger(trade_date: str = None, min_net_buy: float = None) -> dict:
    """
    全市场龙虎榜。
    trade_date: YYYY-MM-DD（默认当日）
    min_net_buy: 净买入下限（万元），None 不过滤
    """
    if trade_date is None:
        trade_date = datetime.now().strftime("%Y-%m-%d")

    data = eastmoney_datacenter(
        "RPT_DAILYBILLBOARD_DETAILSNEW",
        filter_str=f"(TRADE_DATE>='{trade_date}')(TRADE_DATE<='{trade_date}')",
        page_size=500, sort_columns="BILLBOARD_NET_AMT", sort_types="-1",
    )
    if not data:
        return {"date": trade_date, "total_records": 0, "stocks": [],
                "note": "无数据（非交易日或盘后未更新）"}

    actual_date = str(data[0].get("TRADE_DATE", ""))[:10] if data else trade_date
    stocks = []
    for row in data:
        net_buy = (row.get("BILLBOARD_NET_AMT") or 0) / 10000
        if min_net_buy is not None and net_buy < min_net_buy:
            continue
        stocks.append({
            "code": row.get("SECURITY_CODE", ""),
            "name": row.get("SECURITY_NAME_ABBR", ""),
            "reason": row.get("EXPLANATION", ""),
            "close": row.get("CLOSE_PRICE") or 0,
            "change_pct": round(float(row.get("CHANGE_RATE") or 0), 2),
            "net_buy_wan": round(net_buy, 1),
            "buy_wan": round((row.get("BILLBOARD_BUY_AMT") or 0) / 10000, 1),
            "sell_wan": round((row.get("BILLBOARD_SELL_AMT") or 0) / 10000, 1),
            "turnover_pct": round(float(row.get("TURNOVERRATE") or 0), 2),
        })
    return {"date": actual_date, "total_records": len(stocks), "stocks": stocks}
```

---

## 3.9 信号层组合用法：题材热度 + 资金验证

```python
# 拉当日强势股 reason
df_hot = ths_hot_reason()

# 词频统计 reason 列里的题材关键词
from collections import Counter
all_tags = []
for r in df_hot["题材归因"].dropna():
    tags = [t.strip() for t in str(r).split("+") if t.strip()]
    all_tags.extend(tags)
cnt = Counter(all_tags)
print("当日 TOP 10 题材热度:")
for tag, n in cnt.most_common(10):
    print(f"  {tag}: {n} 只")

# 同时拉北向当日流向
df_north = hsgt_realtime()
hgt_close = df_north["hgt_yi"].dropna().iloc[-1] if not df_north.empty else 0
sgt_close = df_north["sgt_yi"].dropna().iloc[-1] if not df_north.empty else 0
print(f"北向收盘累计: 沪股通 {hgt_close} 亿 / 深股通 {sgt_close} 亿")

# 行业对比
comp = industry_comparison(10)
print("行业涨幅 TOP 5:")
for r in comp["top"][:5]:
    print(f"  {r['name']}: {r['change_pct']}% 涨{r['up_count']}跌{r['down_count']}")
```
