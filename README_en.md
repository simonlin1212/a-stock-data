<p align="center"><a href="README.md">简体中文</a> | <b>English</b></p>

<h1 align="center">a-stock-data</h1>

<p align="center">
  <b>Full-stack data toolkit for China A-shares — 15 layers · 87 endpoints · 34 sources · zero-auth (except iwencai)</b>
</p>

<p align="center">
  Quotes &amp; K-lines · Research · Market Signals · Capital Flow &amp; Chips · News · Fundamentals · Filings · Limit-Up ·
  ETF Options · Sentiment · Macro &amp; Rates · Index &amp; Calendar · Futures &amp; Commodities · Event-Driven · Convertible Bonds
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License"></a>
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white" alt="Python">
  <a href="https://github.com/simonlin1212/a-stock-data/stargazers"><img src="https://img.shields.io/github/stars/simonlin1212/a-stock-data?style=social" alt="Stars"></a>
  <br>
  <img src="https://img.shields.io/badge/layers-15-2ea44f.svg" alt="Layers">
  <img src="https://img.shields.io/badge/endpoints-87-2ea44f.svg" alt="Endpoints">
  <img src="https://img.shields.io/badge/sources-34-2ea44f.svg" alt="Sources">
  <img src="https://img.shields.io/badge/auth-zero-success.svg" alt="Zero Auth">
</p>

<p align="center">
  <a href="#data-coverage-15-categories">Coverage</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#87-endpoints">Endpoints</a> ·
  <a href="./CHANGELOG.md">Changelog</a>
</p>

Full-stack data toolkit for China A-Share market — 15-layer architecture · 87 capability endpoints (82 primary + 5 backups) · 34 data sources · direct HTTP calls except two TCP client libraries (mootdx / baostock)

A self-contained Skill file that consolidates raw A-share and related market data from 34 sources into a ready-to-use toolkit for AI coding assistants. No need to memorize Tencent K-line paging parameters, the binary layout of TDX end-of-day packages, Eastmoney PDF Referer headers, or iwencai X-Claw authentication — it's all handled. And when a primary source bans you, there's a backup-source quick reference to fall back on.

> Compatible with [Claude Code](https://github.com/anthropics/claude-code) · [Codex](https://github.com/openai/codex) · [OpenClaw](https://github.com/anthropics/openclaw)
>
> The Skill file is structured Markdown + embedded Python. Any AI coding assistant with context injection can use it.

> **V3.10.1 (2026-10-07 · #57):** corrects the §1.2 Tencent K-line volume unit: **STAR Market (688 / 689) is in shares**, everything else is in lots. The docs said lots throughout, so STAR volumes converted per the old docs came out 100× too large. Also adds the rules for reconciling share-level volume with the TDX end-of-day package and Baostock. §1.4 ticks now use a pooled, auto-retrying session (one call ~70 s → ~25 s) and add `frame.attrs["complete"]`, which from 15:31 on checks for missing after-hours fixed-price trades; §13.7 futures daily K-lines retry too. Entry count, source count and returned data are unchanged.
>
> **V3.10.0 (2026-09-22):** after the TDX public servers stopped serving K-lines, order books and ticks (#52), the quote layer now lists the working sources first (Tencent → Tencent K-lines → TDX end-of-day package → Tencent ticks) and moves mootdx to the end as an archive. New: §1.4 `tencent_ticks()` — Tencent intraday ticks for the latest trading day, one snapshot about every 3 seconds (replaces mootdx ticks) — and §13.7 `futures_kline()` — Sina futures daily K-lines, continuous or single contract, **now covering DCE**. Layer 1 is renumbered; the old→new mapping is in the CHANGELOG.
>
> **V3.9.0 (2026-09-20):** three new layers — futures & commodities, event-driven, convertible bonds — plus Tencent K-lines, the TDX official end-of-day package, Sina research reports, ETF shares, yield curves and more in the existing layers: 25 new entries in total. The broken TDX public-server K-line commands (#52) are now routed over HTTP. See the [CHANGELOG](./CHANGELOG.md) (Chinese).

---

## Data Coverage (15 categories)

<table>
<thead>
<tr><th nowrap>#</th><th nowrap>Category</th><th>Data</th><th>Main sources</th></tr>
</thead>
<tbody>
<tr><td nowrap>1</td><td nowrap>Quotes / K-lines</td><td>Live price, PE/PB/market cap/turnover, daily/weekly/monthly forward- and back-adjusted and 1–60-minute K-lines, full-market daily bars for a trading day (with turnover value), adjust factors, index / ETF</td><td>Tencent, TDX official site, Baidu, Sina</td></tr>
<tr><td nowrap>2</td><td nowrap>Research</td><td>Stock / industry reports and PDFs, ratings, 3-year EPS forecasts, consensus EPS, natural-language search, report lists</td><td>Eastmoney, Sina, THS, iwencai</td></tr>
<tr><td nowrap>3</td><td nowrap>Market signals</td><td>Hot stocks and themes, northbound flow, sector membership, fund flow, dragon-tiger board, lockup expiries, industry ranking, board fund flow</td><td>THS, Eastmoney</td></tr>
<tr><td nowrap>4</td><td nowrap>Capital flow / chips</td><td>Margin trading, block trades, shareholder count, dividends, 120-day fund flow, chip distribution, ETF shares</td><td>Eastmoney, SSE, SZSE, computed locally</td></tr>
<tr><td nowrap>5</td><td nowrap>News</td><td>Stock news, CLS flash, 7×24 live news, CCTV evening news transcripts</td><td>Eastmoney, CLS, Wallstreetcn, CCTV</td></tr>
<tr><td nowrap>6</td><td nowrap>Fundamentals</td><td>Quarterly snapshot, F10, financial statements, valuation history, listing/delisting dates, SW industry history, ST list</td><td>TDX (mootdx), Sina, baostock, SW, Eastmoney</td></tr>
<tr><td nowrap>7</td><td nowrap>Filings</td><td>Full filings across SSE / SZSE / BSE</td><td>cninfo</td></tr>
<tr><td nowrap>8</td><td nowrap>Limit-up</td><td>Limit-up / break / limit-down / previous-day pools, limit-up reasons, watch list, intraday anomalies</td><td>Eastmoney, THS</td></tr>
<tr><td nowrap>9</td><td nowrap>ETF options</td><td>T-quotes, Greeks, implied volatility</td><td>Sina</td></tr>
<tr><td nowrap>10</td><td nowrap>Sentiment</td><td>cninfo IRM (Shenzhen), SSE e-Interaction (Shanghai), THS hot list, Eastmoney popularity rank, concept hits</td><td>cninfo, SSE e-Interaction, THS, Eastmoney</td></tr>
<tr><td nowrap>11</td><td nowrap>Macro &amp; rates</td><td>Social financing, PMI, government and credit yield curves, repo fixing rates, LPR, global macro calendar</td><td>PBoC, NBS, ChinaBond, China Money (CFETS), Eastmoney, Wallstreetcn</td></tr>
<tr><td nowrap>12</td><td nowrap>Index &amp; calendar</td><td>CSI / CNI constituents and weights, CSI PE and dividend yield, SZSE trading calendar</td><td>CSI, CNI, SZSE</td></tr>
<tr><td nowrap>13</td><td nowrap>Futures &amp; commodities</td><td>Futures daily quotes, commodity and index options, member position rankings, real-time futures, FTSE China A50, SGE spot</td><td>SHFE, INE, CZCE, CFFEX, GFEX, Sina, SGE</td></tr>
<tr><td nowrap>14</td><td nowrap>Event-driven</td><td>Earnings previews, institutional surveys, shareholder buying/selling, buybacks, share pledges, IPO calendar</td><td>Eastmoney</td></tr>
<tr><td nowrap>15</td><td nowrap>Convertible bonds</td><td>Terms, conversion price, conversion value, premium, listing / delisting status</td><td>Eastmoney</td></tr>
</tbody>
</table>

Plus 5 backups: official dragon-tiger, Sina fund flow, filings, official SSE/SZSE margin data, and BSE current quotes — used when a primary source is blocked.

---

## Architecture

```
China A-Share Full-Stack Data · 15-Layer Architecture · V3.10.1
│  (Priority: Tencent / exchanges and official bodies first — no IP bans; mootdx quote commands return empty since 2026-09,
│   so it is only used for financials and F10; Eastmoney only for exclusive data, with built-in throttling)
├── Market Data    Tencent + TDX site + Baidu + Sina   Live price / PE / PB / market cap + Index/ETF + K-lines (w/ MA5/10/20)
│                                                     + adjust factors qfq/hfq  ★V3.7
│                                                     + adjusted daily/weekly/monthly & 1–60-min K-lines + full-market daily bars  ★V3.9
│                                                     + intraday ticks, ~3 s snapshots (SSE/SZSE stocks + ETFs)  ★V3.10
├── Research       Eastmoney + THS + iwencai + Sina   Stock reports / Industry reports / PDF / Consensus EPS / NL search
│                                                     + Sina report list (second source)  ★V3.9
├── Signals        THS + Eastmoney                    Hot stocks + Sector attribution + Northbound flow
│                                                     + Sector membership + Fund flow(push2) + Dragon Tiger + Lockup + Industry + Board fund flow
├── Capital Flow   Eastmoney datacenter + push2       Margin trading + Block trades + Holder count + Dividends + Fund flow(min+120d)
│   / Chips        computed locally + SSE + SZSE      Chip distribution (CYQ)  ★V3.7 + ETF shares  ★V3.9
├── News           Eastmoney + CLS + Wallstreetcn + CCTV   Stock news / CLS flash / Global news / 7×24 live / CCTV evening news  ★V3.9
├── Fundamentals   mootdx + Eastmoney + Sina          37-field quarterly + F10 latest notes + Financial statements
│               + baostock + SW                  Valuation history (PE/PB/PS + turnover + ST) / listing & delisting / SW industry history  ★V3.7
│                                                     + ST list  ★V3.9
├── Filings        cninfo + mootdx                    Full filings across SSE / SZSE / BSE
├── Limit-Up       Eastmoney push2ex + THS            ZT/ZB/DT/prev-ZT pools / limit reasons / consecutive-board ladder
│                                                     + Watch list pool + Intraday price-anomaly pool  ★V3.6
├── Options        Sina hq.sinajs                     ETF option T-quotes / Greeks / implied volatility  ★V3.3
├── Sentiment      cninfo IRM + SSE e-Interaction + THS + Eastmoney   Shenzhen Q&A / Shanghai Q&A ★V3.9 / hot lists / popularity / concept hits
├── Macro & Rates  PBoC + NBS + ChinaBond + CFETS + Eastmoney + Wallstreetcn
│                                                     Social financing / PMI / yield curves / repo fixing / LPR / macro calendar  ★V3.9
├── Index/Calendar CSI + CNI + SZSE               Constituents / weights / PE & dividend yields / official trading calendar
├── Futures        SHFE + INE + CZCE + CFFEX + GFEX + Sina + SGE
│                                                     Futures daily / commodity & index options / position rank / real-time / A50 / SGE gold  ★V3.9
│                                                     + futures daily K-lines (continuous + contracts, incl. DCE)  ★V3.10
├── Event-Driven   Eastmoney datacenter               Earnings previews / surveys / holder trades / buybacks / pledges / IPO calendar  ★V3.9
└── Convertibles   Eastmoney datacenter               Terms / conversion value / premium / listing status  ★V3.9
```

> The 15 layers include a **Backup Sources & Fallback Strategy** appendix: dragon-tiger, fund flow and filings, plus official SSE/SZSE margin data and BSE current quotes with five-level books. See SKILL.md for coverage and source dates.

---

## Quick Start

**3 steps, 2 minutes.**

```bash
# 1. Create skill directory
mkdir -p ~/.claude/skills/a-stock-data

# 2. Download SKILL.md
curl -o ~/.claude/skills/a-stock-data/SKILL.md \
  https://raw.githubusercontent.com/simonlin1212/a-stock-data/main/SKILL.md

# 3. Install dependencies (V3.0: akshare no longer needed; V3.9 adds none)
pip install mootdx requests pandas stockstats numpy baostock xlrd openpyxl
```

Launch Claude Code and say "Check the valuation of 688017" — the skill activates automatically.

> **Codex / OpenClaw users:** Paste the contents of SKILL.md into your system prompt or project context file. The embedded Python code is ready to execute.

---

## 87 Endpoints

There are 82 primary entries and 5 backups. Counts refer to capability entries: CSI/CNI or SSE/SZSE routes within one function count once; helpers and research candidates are excluded.

> **Counting convention:** the tables below have 88 rows but count as 87 capability endpoints — "Eastmoney Industry Reports" shares **the same endpoint** as "Eastmoney reportapi" (only the `qType` parameter differs) and "THS Northbound (historical)" is a local self-built cache (not a separate endpoint), so neither is counted; the single "EM Intraday Anomaly Pool" row covers **two** endpoints (`list` / `count`), adding one back. 88 − 1 − 1 + 1 = 87. The ticker helper `to_joinquant()` is not counted.

### Market Data (real-time, no IP ban)

<table>
<thead>
<tr><th nowrap>Endpoint</th><th>Data</th></tr>
</thead>
<tbody>
<tr><td nowrap>Tencent Finance</td><td>PE(TTM) / PB / Market Cap / Float Cap / Turnover / Price Limits / Index / ETF</td></tr>
<tr><td nowrap><strong>Tencent K-lines</strong></td><td>SSE/SZSE daily/weekly/monthly forward- and back-adjusted + 1/5/15/30/60-minute bars, rotating across three Tencent hosts; no BSE (V3.9 new)</td></tr>
<tr><td nowrap><strong>TDX End-of-Day Package</strong></td><td>Every SSE/SZSE/BSE security's daily bar for one trading day, incl. turnover value; one 2–3 MB zip; 2022-01-04 and 2023-01-03 tested available, 2021-01-04 gone, not every day verified; packages before 2022-05-06 have no BSE files (V3.9 new)</td></tr>
<tr><td nowrap><strong>Tencent Ticks</strong></td><td>All ticks of the latest trading day (~3-second snapshots, not Level-2 trade-by-trade): time / price / volume / value / buy-sell side, SSE/SZSE stocks + ETFs, no BSE; after the close the total is checked against the day's turnover (V3.10 new, replaces mootdx ticks)</td></tr>
<tr><td nowrap><strong>Baidu K-line</strong></td><td>Daily K-line + MA5/MA10/MA20 moving averages included (V3.0 new)</td></tr>
<tr><td nowrap><strong>Sina Adjust Factors</strong></td><td>qfq / hfq factor series + applying them to unadjusted candles (V3.7 new)</td></tr>
<tr><td nowrap>mootdx Market Data (archive)</td><td>Candlesticks (multi-period) + order book + ticks + 46-field quote (⚠️ TDX public servers return empty since 2026-09, see FAQ #52; use Tencent K-lines / the end-of-day package for bars and Tencent Ticks for trades)</td></tr>
</tbody>
</table>

### Research Reports

| Endpoint | Data |
|----------|------|
| Eastmoney reportapi | Single-stock report list + ratings + 3-year EPS forecasts |
| Eastmoney Industry Reports | Industry report list (qType=1, same endpoint) + industry name/code + rating (V3.2.3) |
| Eastmoney PDF | Full research report PDF, stock & industry (Referer auth handled) |
| THS Consensus EPS | Institutional consensus EPS (direct basic.10jqka.com.cn) |
| iwencai NL Search | Natural language cross-topic report search |
| **Sina Report List** | Title / type / broker / analysts / date — a second source besides Eastmoney; no ratings or targets (V3.9 new, #53) |

### Signals

| Endpoint | Data |
|----------|------|
| THS Hot Stocks | Today's strong stocks + sector attribution tags (editorial annotations) |
| THS Northbound (real-time) | Shanghai Connect minute-level flow (Shenzhen Connect unreliable since upstream disclosure tightening — see HKEX backup for authoritative data) |
| THS Northbound (historical) | Local self-cached daily history |
| Eastmoney Sector Membership | All sectors a stock belongs to (industry/concept/region mixed) + BK code + daily change + leading stock (V3.2.2, replaced Baidu PAE, one request) |
| **Eastmoney Fund Flow** | Main / Large / Medium / Small / Super-large order minute-level net inflow (V3.1, replaced Baidu PAE) |
| Dragon Tiger Board | Appearance records + Top 5 buy/sell brokerages + institutional activity |
| Daily Dragon Tiger (Full Market) | All stocks on daily board + net buy ranking + appearance reasons |
| Lockup Expiry Calendar | Historical releases + 90-day upcoming expiry alerts |
| **Industry Ranking** | Eastmoney industry change/up/down counts (V3.0, replaced THS 401) |
| **Board Fund Flow** | Industry/concept/region × today/5d/10d main net inflow & ratio + super-large/large/medium/small tiers + leading stock (V3.5, same endpoint as Industry Ranking) |

### Capital Flow / Ownership (V3.0 New)

| Endpoint | Data |
|----------|------|
| **Margin Trading** | Daily margin balance / buy / repay + short selling balance |
| **Block Trades** | Deal price/volume + buyer/seller brokerages + premium rate |
| **Shareholder Count** | Quarterly holder count + QoQ change + avg shares per holder |
| **Dividend History** | Per-share cash dividend / bonus shares / transfer shares |
| **120-Day Fund Flow** | Main / large / medium / small order daily net inflow |
| **Chip Distribution (CYQ)** | Profit ratio / average cost / 90-70 cost range & concentration / chip peak (computed locally, V3.7 new) |
| **ETF Shares** | SSE daily archive (2022-01-04 still available in testing) / SZSE current snapshot, in 10k units (V3.9 new) |

### News

<table>
<thead>
<tr><th nowrap>Endpoint</th><th>Data</th></tr>
</thead>
<tbody>
<tr><td nowrap>Stock News</td><td>Eastmoney per-stock news (direct search-api-web)</td></tr>
<tr><td nowrap>CLS Flash</td><td>Market-wide real-time flash (v1 API + local signature, zero key, ✅revived in V3.4.0, mutual backup with Global News)</td></tr>
<tr><td nowrap>Global News</td><td>Eastmoney global finance news (direct np-weblist, 7×24)</td></tr>
<tr><td nowrap><strong>Wallstreetcn Live</strong></td><td>7×24 live news by channel, with a paging cursor (V3.9 new)</td></tr>
<tr><td nowrap><strong>CCTV Evening News</strong></td><td>Xinwen Lianbo item titles + transcripts (cctv.com, updated after about 20:00 Beijing time; V3.9 new)</td></tr>
</tbody>
</table>

### Fundamentals + Filings

| Endpoint | Data |
|----------|------|
| Quarterly Snapshot | 37 fields (EPS / ROE / Net Profit / Revenue...) |
| F10 Text | "Latest notes" (filings / news / block trades / margin / risk alerts digest); since 2026-09 the server only returns this category |
| Eastmoney Stock Info | Industry / total shares / float / market cap / listing date (direct push2) |
| Sina Financial Statements | Balance sheet / Income statement / Cash flow (direct quotes.sina.cn) |
| cninfo Filings | Full filings across all exchanges |
| **Valuation History** | Daily PE/PB/PS/PCF + turnover + suspension + ST flag (back to 2016; **Beijing Exchange not supported**, V3.7 new) |
| **Listing / Delisting Date** | ipoDate / outDate / status (only zero-auth source for delisting dates, V3.7 new) |
| **SW Industry History** | Every industry reclassification per stock (removes look-ahead bias; codes only, no Chinese names, V3.7 new) |
| **ST List** | Today's SSE/SZSE/BSE ST and *ST stocks with price; falls back to baostock (SSE/SZSE only, no price) when Eastmoney is unreachable (V3.9 new) |

### Limit-Up / Limit-Down (V3.3 new)

| Endpoint | Data |
|----------|------|
| EM Limit-Up Pool | Consecutive boards / N-day-M-board / seal fund / break count / seal time / industry |
| EM Break-Board Pool | Opened after limit-up + amplitude / speed |
| EM Limit-Down Pool | Seal fund / consecutive limit-down / open count / board turnover |
| EM Prev-Day Limit-Up Pool | Yesterday's limit-up performance today (promotion rate / profit effect) |
| THS Limit-Up Insight | Limit reason themes / seal success rate / board type / seal amount |
| EM Watch List Pool | Exchange risk-warning / watch list + validity window (new in V3.6) |
| EM Intraday Anomaly Pool | Severe price-anomaly detail + per-stock aggregated counts + all 12 anomaly rules decoded (new in V3.6) |

### ETF Options (V3.3 new)

| Endpoint | Data |
|----------|------|
| Option Contract List | 50ETF / 300ETF / STAR50 ETF / 500ETF call & put contracts by month |
| T-Quote | Bid/ask 5 levels / open interest / strike / last / volume |
| Greeks + IV | Delta / Gamma / Theta / Vega / implied vol / theoretical value (exchange-computed, no local BSM) |

### Sentiment & Interaction (V3.3 new)

<table>
<thead>
<tr><th nowrap>Endpoint</th><th>Data</th></tr>
</thead>
<tbody>
<tr><td nowrap>Investor Q&amp;A (IRM)</td><td>Investor questions + official company replies (cninfo, Shenzhen-listed companies; unique source: how a company responds to rumors/news)</td></tr>
<tr><td nowrap><strong>SSE e-Interaction</strong></td><td>Investor questions + replies for Shanghai-listed companies, which cninfo IRM does not cover (V3.9 new)</td></tr>
<tr><td nowrap>THS Hot List</td><td>Popularity / concept tags / rank change</td></tr>
<tr><td nowrap>EM Popularity Rank</td><td>Rank + rank change + name/price</td></tr>
<tr><td nowrap>EM Stock Concept Hits</td><td>Which concepts the market is grouping this stock under + heat</td></tr>
</tbody>
</table>

### Macro & Rates (V3.7 new, extended in V3.9)

<table>
<thead>
<tr><th nowrap>Endpoint</th><th>Data</th></tr>
</thead>
<tbody>
<tr><td nowrap><strong>PBoC Social Financing</strong></td><td>Aggregate Financing to the Real Economy, monthly, 12 columns (RMB/entrusted/trust loans, undiscounted acceptances, corporate &amp; government bonds, equity financing, ABS, write-offs)</td></tr>
<tr><td nowrap><strong>NBS PMI</strong></td><td>Manufacturing / non-manufacturing / composite PMI + large / medium / small enterprise breakdown</td></tr>
<tr><td nowrap><strong>ChinaBond Yield Curves</strong></td><td>Government / commercial bank AAA / short-term note AAA, 3 months to 30 years (V3.9 new)</td></tr>
<tr><td nowrap><strong>Repo Fixing Rates</strong></td><td>FR001 / FR007 / FR014 and the matching FDR tenors (China Money; FR about 3 years, FDR about 1 year of history; V3.9 new)</td></tr>
<tr><td nowrap><strong>LPR</strong></td><td>1-year / 5-year full history (incl. the daily quotes of the 2013–2019 regime; V3.9 new)</td></tr>
<tr><td nowrap><strong>Global Macro Calendar</strong></td><td>Actual / forecast / previous / revised values and importance (Wallstreetcn; V3.9 new)</td></tr>
</tbody>
</table>

### Index Data and Trading Calendar

| Endpoint | Data |
|----------|------|
| Index Constituents | Latest CSI constituents and latest published CNI month-end constituents; actual source dates, no historical membership backfill |
| Index Weights | Latest published CSI/CNI weights in percentage points; dates may differ from constituents |
| Index Valuation | CSI PE and dividend yields under two share-capital conventions; recent file, no PB or full-history guarantee |
| Official Trading Calendar | Complete SZSE calendar month; missing days, unpublished months and unknown flags raise errors |

### Futures & Commodities (V3.9 new, #49)

<table>
<thead>
<tr><th nowrap>Endpoint</th><th>Data</th></tr>
</thead>
<tbody>
<tr><td nowrap><strong>Futures Daily</strong></td><td>Official closing data from SHFE / INE / CZCE / CFFEX / GFEX: OHLC, settlement, volume, open interest and its change, turnover</td></tr>
<tr><td nowrap><strong>Options Daily</strong></td><td>Commodity and index options: strike, settlement, volume and open interest, Delta, implied volatility (per series on SHFE / INE, per contract on CZCE / GFEX; CFFEX publishes neither Delta nor IV)</td></tr>
<tr><td nowrap><strong>Member Position Rank</strong></td><td>Top 20 members by volume / long / short positions and their changes (SHFE, INE, CZCE, CFFEX)</td></tr>
<tr><td nowrap><strong>Real-Time Futures</strong></td><td>Sina real-time price and best bid/ask across all six futures exchanges (use this for DCE contracts); price limits for CFFEX contracts only</td></tr>
<tr><td nowrap><strong>Futures Daily K-lines</strong></td><td>Sina daily bars for a continuous series (<code>RB0</code> / <code>M0</code>, back to 2005) or a single contract (those expiring from about 2022), all six exchanges incl. DCE; prices match the official daily data, settlement prices are incomplete (V3.10 new)</td></tr>
<tr><td nowrap><strong>FTSE China A50</strong></td><td>FTSE China A50 continuous futures quote</td></tr>
<tr><td nowrap><strong>SGE Spot</strong></td><td>Shanghai Gold Exchange Au99.99 / Au(T+D) / Ag(T+D) / Pt99.95 and more, daily bars</td></tr>
</tbody>
</table>

> DCE's website uses a JavaScript challenge (plain HTTP gets 412), so its official daily quotes are not integrated; use Futures Daily K-lines for DCE history and Real-Time Futures for live prices.

### Event-Driven (V3.9 new)

| Endpoint | Data |
|----------|------|
| **Earnings Previews** | Preview type, expected amount and change ranges, prior-year figure, reasons |
| **Institutional Surveys** | Survey summary (number of institutions, method, venue) or per-institution detail |
| **Shareholder Trades** | Holder, direction, shares and percentage changed, holdings afterwards, average price, channel |
| **Share Buybacks** | Price cap, planned share and amount ranges, shares and amount bought so far, progress |
| **Share Pledges** | CSDC weekly pledge ratio, pledged shares and value, number of pledges (SSE/SZSE only) |
| **IPO Calendar** | Subscription / lottery / payment / listing dates, issue price and PE, winning rate, first-day performance |

### Convertible Bonds (V3.9 new)

<table>
<thead>
<tr><th nowrap>Endpoint</th><th>Data</th></tr>
</thead>
<tbody>
<tr><td nowrap><strong>Convertible Bonds</strong></td><td>Underlying stock, rating, issue size, conversion price, conversion value, premium, listing / maturity / delisting dates and status</td></tr>
</tbody>
</table>

### Backup Sources (fallback when a primary source fails)

| Endpoint | Data |
|----------|------|
| Official Dragon-Tiger Backup | SSE + SZSE official APIs, zero-auth, authoritative first-party, incl. brokerage seats (when Eastmoney is banned) |
| Fund Flow Backup | Sina daily 4-tier order net flow (super-large / large / medium / small + net inflow) |
| Filings Backup | SZSE official for Shenzhen tickers, Eastmoney for Shanghai, both with direct PDF links (when cninfo is banned) |
| Official Margin Backup | Query SSE/SZSE separately; CNY amounts and share/unit quantities; missing SSE short balance remains null |
| BSE Quote Backup | Board-wide or single-symbol OHLC, volume, amount and five-level snapshot; validates session date; no historical backfill or verified intraday latency |

> Plus a **per-layer primary → independent-backup table** (exchange official / THS F10 / HKEX / cninfo webapi / Jin10 — all on different rate-limit planes) and a "confirmed dead" list — see the "Backup Sources & Fallback Strategy" section in SKILL.md. From V3.9 the primary K-line source is Tencent, full-market daily bars can come from the TDX package, and report lists can come from Sina.

### Authentication

All integrated sources except iwencai require no user registration or API key. CSI, CNI and BSE (V3.8) and the 12 sources added in V3.9 (TDX official site, Wallstreetcn, CCTV, SSE e-Interaction, ChinaBond, China Money, the five futures exchanges, SGE) need no user credentials; BSE establishes an anonymous site cookie. Only iwencai semantic search requires an API key ([apply here](https://www.iwencai.com/skillhub)). Optional research candidates are excluded from these capabilities.

---

## Usage Examples

Just tell your AI assistant:

| Scenario | Prompt |
|----------|--------|
| Valuation | "Estimate 688017 — give me PE / PEG / payback period" |
| Sector Attribution | "Which stocks are strong today and what sectors are driving them" |
| Research Reports | "Latest reports on humanoid robot supply chain, especially ball screws and reducers" |
| Northbound Flow | "How's northbound capital flow looking today" |
| Concept Blocks | "What concept sectors does 688017 belong to" |
| Fund Flow | "Is institutional money flowing into or out of 000858 today" |
| Dragon Tiger Board | "Has 002475 appeared on the dragon tiger board recently, which brokerages are buying" |
| Daily Dragon Tiger | "Which stocks had the highest net buy on today's dragon tiger board" |
| Lockup Expiry | "Any lockup expiries coming up in the next 3 months for this stock" |
| Industry Rotation | "Which industries are up the most today, where is money flowing" |
| Margin Trading | "What's the recent trend in margin balance for 600519" |
| Block Trades | "Any recent block trades for this stock, premium or discount" |
| Shareholder Count | "Is 000858 shareholder count increasing or decreasing" |
| Dividends | "How much has Moutai paid in dividends over the years" |
| ETF Quote | "What's the price of 510050 (SSE 50 ETF) and today's change" |
| Limit-Up Sentiment | "How many stocks hit limit-up today, highest consecutive boards, break rate" |
| Limit-Up Themes | "What themes drove today's limit-ups, which are multi-day boards" |
| Watch List Pool | "Which stocks are on the exchange watch list right now, and until when" |
| Intraday Anomalies | "Which stocks had severe price anomalies today, and which rule did they trigger" |
| Anomaly × Watch List | "Of today's anomaly stocks, which are already on the watch list" |
| ETF Options | "What's the implied vol and Delta of the at-the-money 50ETF option" |
| Investor Q&A | "What are investors asking BYD recently and how did the company respond" |
| Market Heat | "Which stocks are hottest today and what concepts are they grouped under" |
| News & Filings | "Pull recent news and filings for 300476" |
| Market Flash | "Any big market news right now on the CLS flash feed" |
| Batch Compare | "Compare valuations of these 5 semiconductor stocks" |
| **Chip Distribution** | "How much of 600519 is in profit, where's the average cost and the chip peak" |
| **Valuation History** | "What percentile is Moutai's PE over the past decade, and show turnover too" |
| **ST / Suspension** | "When was 000004 flagged ST, and has it ever been suspended" |
| **Industry Drift** | "Which SW industry was 000001 in back in 2016 — same as today?" |
| **Macro Backdrop** | "What's the latest social financing and PMI — is liquidity loose or tight" |
| Index Constituents | "List the latest CSI 300 constituents and their source date" |
| Index Weights | "Show the latest published ChiNext weights, preserving their actual date" |
| Index Valuation | "Show recent CSI 300 PE and dividend yields, with both conventions separately" |
| Trading Calendar | "Which days in September 2026 are open, according to SZSE?" |
| Margin Backup | "Eastmoney is unavailable; fetch SSE and SZSE margin data separately for 2026-09-03" |
| BSE Backup | "Fetch the current official BSE snapshot for 920021 and verify its session date" |
| **Adjusted K-lines** | "Forward-adjusted daily bars for 600519 since 2025, plus the latest 96 five-minute bars for 300750" |
| **Full-Market Daily** | "Close and turnover value for every SSE/SZSE/BSE security on 2026-09-18, top 20 by turnover" |
| **Second Report Source** | "Eastmoney is down — use Sina to list recent reports on 600519" |
| **ETF Shares** | "Has 510300's share count grown or shrunk over the past six months" |
| **7×24 Live News** | "Latest 50 items from the Wallstreetcn A-share channel" |
| **CCTV Evening News** | "Which industries did tonight's Xinwen Lianbo mention" |
| **ST List** | "How many ST and *ST stocks are there now, and how many on the BSE" |
| **Shanghai Q&A** | "What has SPD Bank replied on SSE e-Interaction recently" |
| **Yield Curves** | "How has the 10-year government bond yield moved this year, and what's the spread to AAA short-term notes" |
| **Money-Market Rates** | "FR007 over the past month, and when did the LPR last change" |
| **Macro Calendar** | "Which major macro releases are due next week; how did last week's releases compare with forecasts" |
| **Futures Daily** | "Yesterday's settlement prices and open interest for SHFE rebar and copper contracts" |
| **Commodity Options** | "Delta and implied volatility for yesterday's SHFE copper options" |
| **Position Rank** | "Top 20 members' long/short position changes in IF2610" |
| **Commodities** | "Where's soybean meal trading now, and the A50 futures and SGE gold" |
| **Earnings Previews** | "Which Q3 earnings previews show the biggest expected increase" |
| **Institutional Surveys** | "Which institutions have surveyed 688062 recently" |
| **Holder Trades / Buybacks** | "Which shareholders are selling this month, and which companies are buying back shares" |
| **Share Pledges** | "Which companies have the highest pledge ratios" |
| **IPO Calendar** | "Which IPOs can I subscribe to this week, and at what issue PE" |
| **Convertible Bonds** | "Which convertible bonds have the lowest conversion premium right now" |
| **JoinQuant Tickers** | "Convert these tickers to JoinQuant format" |

### 4 Built-in Research Workflows

<table>
<thead>
<tr><th nowrap>Workflow</th><th>What it does</th><th nowrap>Time</th></tr>
</thead>
<tbody>
<tr><td nowrap>Single Stock Valuation</td><td>Live price → Consensus EPS → Forward PE / PEG / PE payback years</td><td nowrap>30 sec</td></tr>
<tr><td nowrap>Batch Comparison</td><td>Side-by-side valuation ranking</td><td nowrap>1 min</td></tr>
<tr><td nowrap>Thematic Research</td><td>iwencai multi-keyword NL search + Eastmoney PDF cross-reference</td><td nowrap>2 min</td></tr>
<tr><td nowrap>New Target Research</td><td>Coverage → Valuation → Concepts → Fund flow → Dragon tiger → Lockup → Margin</td><td nowrap>1 min</td></tr>
</tbody>
</table>

---


## Data Source Priority (V3.9 re-ranked by IP-ban risk)

> **Principle: if Tencent or an exchange / official body has it, don't use Eastmoney.** Quotes, K-lines, live prices, market cap and financial statements available from Tencent, official sources or Sina must come from them. mootdx quote commands return empty since 2026-09 (#52), so mootdx is only used for financial snapshots and F10. Eastmoney is only for its exclusive data, all routed through the throttled `em_get()`.

<table>
<thead>
<tr><th nowrap>Priority</th><th>Source</th><th nowrap>Protocol</th><th>IP Ban Risk</th><th>Use</th></tr>
</thead>
<tbody>
<tr><td nowrap><strong>1 (top)</strong></td><td>Tencent Finance</td><td nowrap>HTTP</td><td><strong>Never banned</strong> (one K-line host rate-limits after ~600 calls; three hosts rotate)</td><td>Live price / PE / PB / market cap / turnover / price limits / index / ETF / daily-weekly-monthly and minute K-lines</td></tr>
<tr><td nowrap><strong>2</strong></td><td>Exchanges / official bodies</td><td nowrap>HTTP</td><td>Very low (avoid bursts)</td><td>TDX package, SSE / SZSE / BSE, five futures exchanges, SGE, ChinaBond, China Money, CSI / CNI, PBoC, NBS</td></tr>
<tr><td nowrap><strong>3</strong></td><td>Sina / cninfo / THS / Baidu / CLS / Wallstreetcn / CCTV / SW</td><td nowrap>HTTP</td><td>Low</td><td>Financial statements, adjust factors, report lists, real-time futures, filings, consensus EPS, hot stocks and northbound, K-lines with MAs, live news, evening news, industry history</td></tr>
<tr><td nowrap><strong>4</strong></td><td>mootdx (TDX)</td><td nowrap>TCP 7709</td><td>Never banned</td><td>Financial snapshots and F10 &quot;latest notes&quot; work; <strong>K-lines / order book / ticks return empty since 2026-09 (#52)</strong>; ticks now come from Tencent §1.4</td></tr>
<tr><td nowrap><strong>4</strong></td><td>baostock</td><td nowrap>TCP</td><td>Low (no registration)</td><td>Valuation history PE/PB/PS/PCF + turnover + suspension + ST + listing/delisting dates (<strong>no Beijing Exchange</strong>)</td></tr>
<tr><td nowrap>Key required</td><td>iwencai</td><td nowrap>OpenAPI</td><td>Low</td><td>NL semantic report search (the only source that needs a key)</td></tr>
<tr><td nowrap><strong>last (exclusive only)</strong></td><td><strong>Eastmoney</strong> datacenter / push2 / reportapi / search / np-weblist</td><td nowrap>HTTP</td><td><strong>Medium — has rate-limit risk</strong></td><td>Dragon-tiger / lockup / margin / block trades / shareholders / dividends / fund flow / report PDFs / news / ST list / LPR / event-driven / convertibles (all via <code>em_get()</code>)</td></tr>
</tbody>
</table>

<details>
<summary><b>All 34 sources</b></summary>

| # | Source | Main use |
|---|--------|----------|
| 1 | Tencent Finance | Live valuation, index / ETF, daily-weekly-monthly and minute K-lines |
| 2 | mootdx (TDX TCP) | Financial snapshots, F10 (quote commands broken, #52) |
| 3 | Eastmoney datacenter | Dragon-tiger, lockups, margin, block trades, shareholders, dividends, event-driven, convertibles, LPR |
| 4 | Eastmoney push2 / push2his | Industry boards, fund flow, stock info, ST list |
| 5 | iwencai | Natural-language report search (key required) |
| 6 | Eastmoney reportapi / PDF | Report lists, ratings, PDFs |
| 7 | THS hot stocks | Hot stocks and themes, limit-up insight, hot list |
| 8 | THS hsgtApi | Northbound flow |
| 9 | Baidu Finance | K-lines with moving averages |
| 10 | Sina Finance | Financial statements, adjust factors, ETF options, report lists, real-time futures, A50 |
| 11 | THS basic | Consensus EPS |
| 12 | CLS (Cailianpress) | Flash news |
| 13 | cninfo | Filings, IRM Q&A |
| 14 | SSE official | Dragon-tiger, order book, margin, ETF shares |
| 15 | SZSE official | Dragon-tiger, filings, order book, margin, trading calendar, ETF shares |
| 16 | baostock | Valuation history, listing/delisting dates, ST-list fallback |
| 17 | SW Research | Industry classification history |
| 18 | PBoC | Social financing |
| 19 | NBS | PMI |
| 20 | CSI | Constituents, weights, PE and dividend yield |
| 21 | CNI | Constituents, weights |
| 22 | BSE official | Current quotes and order book |
| 23 | TDX official end-of-day package | Full-market SSE/SZSE/BSE daily bars for a trading day (with turnover value) |
| 24 | Wallstreetcn | 7×24 live news, global macro calendar |
| 25 | CCTV | Xinwen Lianbo items and transcripts |
| 26 | SSE e-Interaction | Shanghai investor Q&A |
| 27 | ChinaBond | Government and credit yield curves |
| 28 | China Money (CFETS) | Repo fixing rates FR / FDR |
| 29 | SHFE | Futures / options daily, position rank |
| 30 | INE | Crude oil / international copper futures and options, position rank |
| 31 | CZCE | Futures / options daily, position rank |
| 32 | CFFEX | Index / bond futures, index options, position rank |
| 33 | GFEX | Industrial silicon / lithium carbonate futures and options daily |
| 34 | SGE | Gold / silver / platinum spot daily |

</details>

> **Architecture:** Except mootdx and baostock (both TCP client libraries), all sources use direct HTTP API calls with no third-party data wrapper in between. **Eastmoney APIs are rate-limited; all calls go through `em_get()` for serial throttling. For batch jobs, increase `EM_MIN_INTERVAL`.**
>
> **Fallback:** When a primary source fails, check the "Backup Sources & Fallback Strategy" section in SKILL.md. Some core data types have independent backups on **different domains with separate rate limits**. Not every capability has a backup; always verify dates and completeness after fetching.

---

## FAQ

**Why are index weights not dated today? Can they be used for historical backtests?**
Constituents and weights may be published on different dates. The CNI endpoint returns a month-end snapshot; `date` is the source date. Current membership is not historical membership. This release does not integrate adjustment history or substitute zero for missing index PB.

**How do I run the two new backups?**
Execute the full Layer 12 code block in SKILL.md, then the official margin/BSE backup block. Query margin data separately for `SH` and `SZ`; BSE requires the expected session date. Date mismatches, incomplete pagination and unpublished data raise errors.

**mootdx returns no K-lines / `tdx_client()` says no server can return data (#52)**
Tested on 2026-09-20 on each of the 10 built-in servers: all accept TCP connections and return financials and ex-rights data, F10 only returns the "latest notes" category, and K-lines, order books and ticks come back with 0 rows. This is a server-side change; switching mootdx versions does not help. Alternatives:
> - SSE/SZSE daily / weekly / monthly K-lines (adjusted) and 1–60-minute bars → §1.2 `tencent_kline()`
> - Full-market SSE/SZSE/BSE daily bars for one trading day (with turnover value; the only daily-bar route for BSE) → §1.3 `tdx_daily_package()`
> - Live price and order book → §1.1 Tencent, or the official exchange books in the backup table
> - Intraday ticks → §1.4 `tencent_ticks()` (latest trading day only, no BSE)
> - Financial snapshots / F10 "latest notes" → `tdx_client(check='finance')`, which still works; the other 8 F10 categories (company profile, shareholders, etc.) are no longer returned — see SKILL.md §6.2 for replacements
>
> In K-line mode `tdx_client()` probes servers first, so a full failure takes about a minute to raise.

**Are easy_tdx (PR #54) and the official THS API included?**
No. easy_tdx is another client for the same TDX protocol, not a new data source, and #52 is solved over HTTP, so PR #54 is not merged; this project only integrates sources it can query directly. The THS service requires a user key; auction integration needs Python 3.10+ compatibility work. See the [v3.8.0](docs/source-integration-v3.8.0.md) and [v3.9.0](docs/source-integration-v3.9.0.md) integration records (Chinese). V3.9 adds no installation dependencies.

**Can I backtest with it? Does it work with JoinQuant? (#55)**
This skill fetches data; it **has no backtesting engine**. Feed the data into your own framework or JoinQuant.
> - Tickers: `norm_ticker()` / `get_prefix()` accept JoinQuant codes `600519.XSHG` / `000001.XSHE`; `to_joinquant()` converts any supported form to JoinQuant codes. JoinQuant's public docs list no BSE suffix, so BSE codes raise an error instead of being guessed.
> - Adjustment: JoinQuant `get_price` defaults to forward adjustment (`fq='pre'`). Compare against §1.2 `tencent_kline(adjust='qfq')`, or apply the §1.6 adjust factors yourself.
> - Look-ahead bias: use §6.5 for historical valuation and §6.7 for historical industry membership; §12 index constituents are current snapshots only.

**Is Eastmoney the only research-report source? (#53)**
No. §2.4 `sina_research_reports()` is a second source that pages by stock or across the market and keeps working when Eastmoney blocks you. It has title, type, broker, analysts and date but no ratings or price targets; use Eastmoney reports or THS consensus for those.

**Are commodity futures and options covered? What about DCE? (#49)**
Yes, see Futures & Commodities. Official futures and options daily data come from SHFE, INE, CZCE, CFFEX and GFEX; member position rankings cover the first four (not GFEX). Sina real-time futures, FTSE China A50 and SGE spot are included too. **DCE's website blocks scripted access, so its official daily quotes are not integrated**; for DCE contracts such as soybean meal and iron ore use V3.10's `futures_kline('M0')` (Sina, continuous or single contract) for history and Sina real-time futures for live prices.

**Why are cninfo IRM answers empty for Shanghai-listed companies?**
cninfo IRM only covers Shenzhen-listed companies; Shanghai tickers return 0 rows. Use §10.3 `sse_e_interaction()` (SSE e-Interaction) for Shanghai. Some companies genuinely have no replies in the last month, so an empty table can be correct.

## Verification

`python3 -m unittest discover -s tests -v` extracts the shipped code directly from SKILL.md and checks dates, fields, symbol routing, units, pagination and error propagation without network access (173 offline tests as of V3.10.1).

Live tests are opt-in; the date must be a trading day the sources have already published:

```bash
# V3.10's tick and futures K-line entries, plus the §1.2 K-line volume-unit check (downloads one TDX end-of-day package)
ASTOCK_LIVE_V310=1 python3 -m unittest tests.test_v310_sources -v
# the 25 entries added in V3.9 (31 live calls)
ASTOCK_LIVE_V39=2026-09-18 python3 -m unittest tests.test_v39_sources -v
# the V3.8 official margin and BSE backups
ASTOCK_LIVE_TRADE_DATE=2026-09-04 ASTOCK_LIVE_MARGIN_DATE=2026-09-03 python3 -m unittest tests.test_official_data -v
```

Per-entry row counts and data boundaries are in the [v3.9.0 integration record](docs/source-integration-v3.9.0.md); V3.8 is in [v3.8.0](docs/source-integration-v3.8.0.md) (both Chinese).

## Changelog

See [CHANGELOG.md](./CHANGELOG.md).

---

## Disclaimer

This project provides data access tools only and does not constitute investment advice. Investing involves risk.

---

## License

[Apache License 2.0](./LICENSE)

**Author:** Simon Lin · X [@linsizhen](https://x.com/linsizhen) · Email: [simonlin0423@gmail.com](mailto:simonlin0423@gmail.com)
