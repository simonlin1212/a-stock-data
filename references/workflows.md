# 完整调研流程

四个常用工作流，按需照搬。所有函数定义在对应 `references/0X-*.md`。

## 流程 A：单票完整估值（30 秒）

```python
import urllib.request
import math
import pandas as pd

def full_valuation(code: str) -> dict:
    """单票完整估值分析"""
    # 1. 腾讯实时行情
    prefix = "sh" if code.startswith(("6","9")) else ("bj" if code.startswith("8") else "sz")
    url = f"https://qt.gtimg.cn/q={prefix}{code}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    resp = urllib.request.urlopen(req, timeout=10)
    data = resp.read().decode("gbk")
    vals = data.split('"')[1].split("~")
    price = float(vals[3])
    mcap = float(vals[44])
    pe_ttm = float(vals[39]) if vals[39] else 0
    pb = float(vals[46]) if vals[46] else 0

    # 2. 机构一致预期（直连同花顺）— 复用 references/02-research.md 的 ths_eps_forecast
    df = ths_eps_forecast(code)
    eps_cur = eps_next = None
    analyst_count = 0
    if not df.empty and len(df.columns) >= 3:
        try:
            for i, row in df.iterrows():
                if i == 0:
                    eps_cur = float(row.iloc[2]) if pd.notna(row.iloc[2]) else None
                    analyst_count = int(row.iloc[1]) if pd.notna(row.iloc[1]) else 0
                elif i == 1:
                    eps_next = float(row.iloc[2]) if pd.notna(row.iloc[2]) else None
        except (ValueError, IndexError):
            pass

    # 3. 估值指标
    pe_fwd = price / eps_cur if eps_cur else float("inf")
    cagr = (eps_next / eps_cur - 1) if (eps_cur and eps_next) else 0
    peg = pe_fwd / (cagr * 100) if cagr > 0 else float("inf")
    digest = (
        math.log(pe_fwd / 30) / math.log(1 + cagr)
        if pe_fwd > 30 and cagr > 0 else 0
    )

    return {
        "name": vals[1],
        "price": price,
        "mcap_yi": mcap,
        "pe_ttm": pe_ttm,
        "pb": pb,
        "eps_cur": eps_cur,
        "eps_next": eps_next,
        "pe_fwd": round(pe_fwd, 1) if eps_cur else None,
        "cagr_pct": round(cagr * 100, 0) if cagr else None,
        "peg": round(peg, 2) if peg != float("inf") else None,
        "digest_years": round(digest, 1),
        "analyst_count": analyst_count,
    }

# 用法
result = full_valuation("688017")
print(result)
```

---

## 流程 B：批量估值对比

```python
stocks = ["688017", "300308", "300476", "002463"]
for code in stocks:
    try:
        r = full_valuation(code)
        print(f"{r['name']}({code}): PE_fwd={r['pe_fwd']}x PEG={r['peg']} 消化={r['digest_years']}年 覆盖={r['analyst_count']}家")
    except Exception as e:
        print(f"{code}: 失败 - {e}")
```

---

## 流程 C：主题研报批量检索

```python
# Step 1: iwencai 多 query 语义搜索
queries = [
    "人形机器人产业链深度 2026",
    "人形机器人减速器 丝杠",
    "特斯拉 Optimus 国产供应链",
]
seen_uids = set()
all_articles = []
for q in queries:
    arts = iwencai_search(q, channel="report", size=50)
    for a in arts:
        uid = a.get("uid", "")
        if uid not in seen_uids:
            seen_uids.add(uid)
            all_articles.append(a)
print(f"共 {len(all_articles)} 篇去重后研报")

# Step 2: 东财补充同标的研报 + PDF
for a in all_articles[:10]:
    stocks = a.get("stock_infos") or []
    for s in stocks:
        stock_code = s.get("code", "")
        if stock_code:
            em = eastmoney_reports(stock_code, max_pages=1)
            print(f"  {stock_code}: 东财 {len(em)} 篇")
```

---

## 流程 D：新标的快速调研（V3.0 增强版）

```python
code = "688017"

# 1. 有无机构覆盖？
forecast = ths_eps_forecast(code)
print(f"机构覆盖: {'有' if not forecast.empty else '无'}")

# 2. 实时估值
quotes = tencent_quote([code])
q = quotes[code]
print(f"PE={q['pe_ttm']} PB={q['pb']} 市值={q['mcap_yi']}亿")

# 3. PE 消化 → 用 full_valuation()
# 4. PEG 校验

# 5. 概念板块归属
blocks = baidu_concept_blocks(code)
print(f"概念: {', '.join(blocks['concept_tags'][:10])}")

# 6. 资金流向（百度分钟级）
flow = baidu_fund_flow_history(code)
if flow:
    recent = flow[0]
    print(f"最近主力净流入: {recent['mainIn']}万")

# 7. 资金流向（东财 120 日）
flow_120 = stock_fund_flow_120d(code)
if flow_120:
    total = sum(d["main_net"] for d in flow_120[-20:])
    print(f"近 20 日主力累计净流入: {total/1e8:.2f}亿")

# 8. 龙虎榜
dtb = dragon_tiger_board(code, "2026-05-17")
print(f"近 30 日上龙虎榜: {len(dtb['records'])} 次")

# 9. 解禁预警
lockup = lockup_expiry(code, "2026-05-17")
print(f"未来 90 天待解禁: {len(lockup['upcoming'])} 批")

# 10. 融资融券
margin = margin_trading(code, page_size=5)
if margin:
    print(f"最新融资余额: {margin[0]['rzye']/1e8:.2f}亿")

# 11. 股东户数
holders = holder_num_change(code)
if holders:
    print(f"最新股东数: {holders[0]['holder_num']} 环比{holders[0]['change_ratio']}%")
```
