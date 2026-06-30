# 东财 IP 封禁实战分析与备用数据源方案

> **案例日期：** 2026-06-30 · **封禁时长：** 全天未恢复 · **影响范围：** push2/push2his 全系列

---

## 一、封禁现象

| 域名 | 用途 | 状态 | 错误表现 |
|------|------|------|----------|
| `push2.eastmoney.com` | 实时行情/股票列表 | **完全封禁** | `RemoteDisconnected: Remote end closed connection without response` |
| `push2his.eastmoney.com` | 历史K线/资金流向 | **完全封禁** | 同上 |
| `82.push2.eastmoney.com` | 负载均衡节点 | **完全封禁** | 同上 |
| `90.push2.eastmoney.com` | 负载均衡节点 | **完全封禁** | 同上 |
| 直接IP `61.129.129.196` | push2 服务器直连 | **完全封禁** | 同上（IP级封禁，非DNS） |
| `datacenter-web.eastmoney.com` | 财务数据/股票列表 | **正常** | — |
| `np-anotice-stock.eastmoney.com` | 公告数据 | **正常** | — |
| `reportapi.eastmoney.com` | 研报数据 | **正常** | — |

**关键特征：** 封禁是 IP 级别的（直连 IP 也被拒），不是 DNS 污染（DNS 正常解析到 `61.129.129.196`）。GitHub、百度等外部网站均正常，确认是东方财富单方面封禁。

---

## 二、封禁原因深度分析

### 2.1 根因：高频并发 + 零限流

用户的选股脚本 `stock_screener.py` 存在以下问题：

```python
# 问题代码示例（原始）
def em_get(url, params=None):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, params=params, headers=headers, timeout=30)  # 无限流、无重试、无Session复用
    return r

# 步骤3：10线程并行获取K线
with ThreadPoolExecutor(max_workers=10) as executor:
    # 对 4758 只股票逐个请求K线，每只2次请求（前复权+原始价）
    # 总请求量 = 4758 × 2 = 9516 次，10并发，零间隔
```

### 2.2 封禁触发的六大因素

| 因素 | 详情 | 严重程度 |
|------|------|----------|
| **① 无请求间隔** | 脚本使用 `requests.get()` 直连，无任何 `time.sleep()` 或限流机制 | 极高 |
| **② 高并发** | `ThreadPoolExecutor(max_workers=10)` 10线程同时请求同一API | 极高 |
| **③ 超大请求量** | 全市场5208只股票，每只需2-3次API调用（列表+K线+复权），单次扫描约15000+请求 | 极高 |
| **④ 三版本重复扫描** | V2/V3/V4三个脚本依次运行，请求量×3，同一IP在1小时内发出45000+请求 | 极高 |
| **⑤ 无Session复用** | 每次请求新建TCP连接，连接数激增触发服务端防护 | 高 |
| **⑥ 无退避重试** | 请求失败时直接抛异常崩溃，未实现指数退避机制 | 中 |

### 2.3 东财风控阈值回顾

根据 SKILL.md 中已文档化的实测阈值：

> - 每秒 > 5 次 → 触发风控
> - 并发 ≥ 10 → 触发风控
> - 1 分钟 ≥ 200 次 → 触发封禁
> - 5 分钟 ≥ 300 次 → 触发封禁

用户的脚本在步骤3中：10线程 × 每线程约0.5秒/请求 = **每秒约20次请求**，远超每秒5次的风控阈值。4758只股票 ÷ 10线程 × 2次请求/只 ≈ 951秒，但前200秒内已发出约4000次请求，远超1分钟200次的封禁阈值。

### 2.4 封禁时间线

```
16:15  V2首次运行 → 获取900只股票后连接被关闭（约第9页时触发风控）
16:17  V3首次运行 → 步骤1即失败（IP已被封禁）
16:18  V4首次运行 → 步骤1即失败（IP已被封禁）
16:27  V2重试 → 仍失败（封禁持续）
18:34  V2再次重试 → 仍失败（封禁持续2小时+）
18:35  测试直接IP访问 → 失败（确认IP级封禁）
18:44  切换备用数据源 → 成功完成全量扫描
```

**结论：** 一旦触发封禁，封禁时长至少数小时（本次全天未恢复），非简单重试可解决。

---

## 三、备用数据源方案（已验证可用）

### 3.1 可用数据源清单

| 数据源 | 域名 | 用途 | 限制 |
|--------|------|------|------|
| **东财 datacenter** | `datacenter-web.eastmoney.com` | 股票列表（含板块/市场） | 无风控，分页500条/页 |
| **腾讯行情** | `qt.gtimg.cn` | 实时行情（价格/涨跌幅/PE/市值） | 批量≤60只/次，GBK编码 |
| **腾讯K线** | `web.ifzq.gtimg.cn` | 日K线（前复权） | 高频后可能限流（非封IP） |
| **新浪K线** | `money.finance.sina.com.cn` | 日K线（不复权，降级方案） | 偶发403，不复权 |
| **新浪行情** | `hq.sinajs.cn` | 实时行情 | 需Referer头，偶发403 |

### 3.2 数据源替换映射

| 原始接口（push2） | 替代方案 | 字段差异 |
|-------------------|----------|----------|
| `push2/clist/get`（股票列表） | `datacenter-web` RPT_LICO_FN_CPD + 腾讯行情批量 | 行业字段来自datacenter的BOARD_NAME |
| `push2his/kline/get`（K线） | 腾讯 `fqkline/get`（前复权）→ 新浪 `getKLineData`（降级） | 腾讯有前复权；新浪不复权 |
| `push2/stock/get`（个股信息） | 腾讯行情 `qt.gtimg.cn` | 腾讯无行业/概念字段 |
| `push2his/fflow/daykline`（资金流） | 无直接替代 | 降级为空（不影响核心筛选） |
| `np-anotice-stock`（公告） | 原接口正常 | 无需替换 |

### 3.3 腾讯行情字段映射（实测校准）

```
v_sh600000="1~浦发银行~600000~8.61~8.73~8.69~684341~..."
              ↑     ↑       ↑      ↑     ↑     ↑      ↑
            市场   名称    代码   现价  昨收  今开   成交量(手)

关键字段索引：
  [3]  当前价格        [4]  昨收价
  [6]  成交量(手)      [32] 涨跌幅(%)
  [39] PE(动态)        [44] 流通市值(亿)
  [45] 总市值(亿)      [47] PB
```

> **注意：** 网上大量教程将字段43标注为PB，实测43=振幅%，46=PB。本映射已实测校准。

---

## 四、防封最佳实践

### 4.1 铁律（不可违反）

1. **所有东财请求必须走 `em_get()` 限流** — 间隔≥1s + 随机抖动 + Session复用
2. **批量任务调大 `EM_MIN_INTERVAL`** — 全市场扫描建议 `EM_MIN_INTERVAL=2.0`
3. **并发≤3** — 东财接口绝不使用10线程，建议3线程或串行
4. **K线优先用 mootdx/腾讯** — 东财push2his仅作为末位降级
5. **三版本分时段运行** — V2/V3/V4不要连续运行，间隔至少30分钟

### 4.2 选股脚本改造建议

```python
# 改造前（危险）
def em_get(url, params=None):
    r = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    return r

# 改造后（安全）
import requests as _rq
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

EM_SESSION = _rq.Session()
EM_SESSION.headers.update({"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"})
_retry = Retry(total=3, backoff_factor=1, status_forcelist=[429,500,502,503,504])
EM_SESSION.mount("https://", HTTPAdapter(max_retries=_retry, pool_connections=1, pool_maxsize=3))
EM_MIN_INTERVAL = 2.0  # 全市场扫描建议2秒
_last_em_time = 0

def em_get(url, params=None):
    global _last_em_time
    import time as _t, random as _r
    elapsed = _t.time() - _last_em_time
    wait = EM_MIN_INTERVAL + _r.uniform(0.1, 0.5) - elapsed
    if wait > 0:
        _t.sleep(wait)
    _last_em_time = _t.time()
    return EM_SESSION.get(url, params=params, timeout=30)
```

### 4.3 多版本扫描的时间规划

| 时间 | 任务 | 说明 |
|------|------|------|
| 15:30 | V2扫描 | 全市场，约15分钟 |
| 15:50 | V3扫描 | 仅主板，约10分钟（与V2间隔20分钟） |
| 16:05 | V4扫描 | 主板VAR7，约10分钟（与V3间隔15分钟） |
| 16:20 | AI投研报告 | 读取V3结果，无push2请求 |
| 16:30 | 资讯雷达 | RSS抓取，无东财请求 |
| 16:40 | V1部署 | 静态HTML，无数据请求 |

---

## 五、备用数据源适配器使用方法

### V3.3.2 优化版（东财优先 + 智能限流 + 并发2）

```python
# 适配器V2: 东财优先, 带智能限流防封, 并发降到2
import data_fallback
import stock_screener

# Monkey-patch: 替换所有东财API依赖 + step3并发降到2
data_fallback.patch_module(stock_screener)

# 正常运行选股脚本
stock_screener.main()
```

适配器V2的核心改进：
- **K线优先东财**：优先用 `push2his`（前复权，数据最准确），通过 `em_get()` 限流
- **封禁自动检测**：连续3次 `RemoteDisconnected` → 标记封禁 → 后续K线自动走腾讯/新浪
- **并发降到2**：`patch_module()` 自动替换 step3，`max_workers=10` → `max_workers=2`
- **三级降级**：东财(限流2s) → 腾讯(前复权) → 新浪(不复权)

### V3.3.1 原始版（纯备用源）

```python
# 适配器V1: 纯备用源, 不使用东财
# 仅当东财确定被封时使用
```

适配器会自动：
- 用 `datacenter-web` + 腾讯行情 替代 `push2/clist/get`
- 用 腾讯K线(前复权) → 新浪K线(降级) 替代 `push2his/kline/get`
- 用 腾讯行情 替代 `push2/stock/get`
- 资金流/公告降级为空（不影响核心选股逻辑）
