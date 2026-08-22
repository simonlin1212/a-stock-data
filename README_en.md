<p align="center"><a href="README.md">简体中文</a> | <b>English</b></p>

<h1 align="center">a-stock-data</h1>

<p align="center">
  <b>Full-stack data toolkit for China A-shares — 11 layers · 55 endpoints · 20 sources · 2 optional auth sources</b>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License"></a>
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white" alt="Python">
  <a href="https://github.com/simonlin1212/a-stock-data/stargazers"><img src="https://img.shields.io/github/stars/simonlin1212/a-stock-data?style=social" alt="Stars"></a>
  <br>
  <img src="https://img.shields.io/badge/layers-11-2ea44f.svg" alt="Layers">
  <img src="https://img.shields.io/badge/endpoints-55-2ea44f.svg" alt="Endpoints">
  <img src="https://img.shields.io/badge/sources-20-2ea44f.svg" alt="Sources">
  <img src="https://img.shields.io/badge/auth-2_optional_sources-blue.svg" alt="2 optional authenticated sources">
</p>

<p align="center">
  <a href="#architecture">Architecture</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#55-endpoints">Endpoints</a> ·
  <a href="./CHANGELOG.md">Changelog</a>
</p>

Full-stack data toolkit for China A-Share market — 11-layer architecture · 55 endpoints (52 primary + 3 official backups) · 20 data sources · direct HTTP calls except two TCP client libraries (mootdx / baostock)

A self-contained Skill file that consolidates raw A-share data from 20 sources into a ready-to-use toolkit for AI coding assistants. It handles source parameters, required headers, and optional authentication. When a primary source bans you, use the backup-source quick reference.

> Compatible with [Claude Code](https://github.com/anthropics/claude-code) · [Codex](https://github.com/openai/codex) · [OpenClaw](https://github.com/anthropics/openclaw)
>
> The Skill file is structured Markdown + embedded Python. Any AI coding assistant with context injection can use it.

---

## Architecture

```
China A-Share Full-Stack Data · 11-Layer Architecture · V3.7.1
│  (Priority: prefer mootdx/Tencent — never IP-banned; Eastmoney only for exclusive data, with built-in throttling)
├── Market Data    mootdx + Tencent + Baidu + Sina    Candlesticks (w/ MA5/10/20) + Order Book + PE/PB + Index/ETF
│                                                     + adjust factors qfq/hfq  ★V3.7
├── Research       Eastmoney + THS + iwencai          Stock reports / Industry reports / PDF / Consensus EPS / NL search
├── Signals        THS + Eastmoney                    Hot stocks + Sector attribution + Northbound flow
│                                                     + Sector membership + Fund flow(push2) + Dragon Tiger + Lockup + Industry + Board fund flow
├── Capital Flow   Eastmoney datacenter + push2       Margin trading + Block trades + Holder count + Dividends + Fund flow(min+120d)
│   / Chips     computed locally                  Chip distribution (CYQ): profit ratio / avg cost / cost range / peak  ★V3.7
├── News           Eastmoney + Cailianpress           Stock news / CLS flash (✅revived in V3.4) / Global finance (mutual backup)
├── Fundamentals   mootdx + Eastmoney + Sina          37-field quarterly + F10 9 categories + Financial statements
│               + baostock + SW                  Valuation history (PE/PB/PS + turnover + ST) / listing & delisting / SW industry history  ★V3.7
├── Filings        cninfo + mootdx                    Full filings across SSE / SZSE / BSE
├── Limit-Up       Eastmoney push2ex + THS            ZT/ZB/DT/prev-ZT pools / limit reasons / consecutive-board ladder
│                                                     + Watch list pool + Intraday price-anomaly pool  ★V3.6
├── Options        Sina hq.sinajs                     ETF option T-quotes / Greeks / implied volatility  ★V3.3
├── Sentiment      cninfo IRM + THS + Eastmoney       Investor Q&A / hot lists / popularity rank / concept hits  ★V3.3
│               + Xquik (optional)                Public X post text / author / time / engagement
└── Macro          PBoC + NBS                     Social financing (monthly, 12 cols) / PMI (mfg · non-mfg · composite · by size)  ★V3.7
```

> ★V3.4 On top of the 11 layers there is now a **Backup Sources & Fallback Strategy** appendix: SSE/SZSE official + Sina + HKEX — official backup functions (dragon-tiger / fund flow / filings) + a per-layer fallback table for when a primary source bans you (see the corresponding SKILL.md section).

---

## Quick Start

**3 steps, 2 minutes.**

```bash
# 1. Create skill directory
mkdir -p ~/.claude/skills/a-stock-data

# 2. Download SKILL.md
curl -o ~/.claude/skills/a-stock-data/SKILL.md \
  https://raw.githubusercontent.com/simonlin1212/a-stock-data/main/SKILL.md

# 3. Install dependencies (V3.0: akshare no longer needed)
pip install mootdx requests pandas stockstats numpy baostock xlrd openpyxl
```

Launch Claude Code and say "Check the valuation of 688017" — the skill activates automatically.

> **Codex / OpenClaw users:** Paste the contents of SKILL.md into your system prompt or project context file. The embedded Python code is ready to execute.

---

## 55 Endpoints

> **Counting convention:** the tables below have 56 rows but count as 55 endpoints. "Eastmoney Industry Reports" shares the same endpoint as "Eastmoney reportapi". "THS Northbound (historical)" is a local cache. Neither is counted separately. The "EM Intraday Anomaly Pool" row covers 2 endpoints (`list` and `count`), adding one back. 56 − 1 − 1 + 1 = 55.

### Market Data (real-time, no IP ban)

| Endpoint | Data |
|----------|------|
| mootdx Market Data | Candlesticks (multi-period) + Level-2 order book + tick-by-tick + 46-field quote |
| Tencent Finance | PE(TTM) / PB / Market Cap / Float Cap / Turnover / Price Limits / Index / ETF |
| **Baidu K-line** | Daily K-line + MA5/MA10/MA20 moving averages included (V3.0 new) |
| **Sina Adjust Factors** | qfq / hfq factor series + applying them to unadjusted candles (V3.7 new) |

### Research Reports

| Endpoint | Data |
|----------|------|
| Eastmoney reportapi | Single-stock report list + ratings + 3-year EPS forecasts |
| Eastmoney Industry Reports | Industry report list (qType=1, same endpoint) + industry name/code + rating (V3.2.3) |
| Eastmoney PDF | Full research report PDF, stock & industry (Referer auth handled) |
| THS Consensus EPS | Institutional consensus EPS (direct basic.10jqka.com.cn) |
| iwencai NL Search | Natural language cross-topic report search |

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

### News

| Endpoint | Data |
|----------|------|
| Stock News | Eastmoney per-stock news (direct search-api-web) |
| CLS Flash | Market-wide real-time flash (v1 API + local signature, zero key, ✅revived in V3.4.0, mutual backup with Global News) |
| Global News | Eastmoney global finance news (direct np-weblist, 7×24) |

### Fundamentals + Filings

| Endpoint | Data |
|----------|------|
| Quarterly Snapshot | 37 fields (EPS / ROE / Net Profit / Revenue...) |
| F10 Company Data | 9 categories (truncation optimization, -70% tokens) |
| Eastmoney Stock Info | Industry / total shares / float / market cap / listing date (direct push2) |
| Sina Financial Statements | Balance sheet / Income statement / Cash flow (direct quotes.sina.cn) |
| cninfo Filings | Full filings across all exchanges |
| **Valuation History** | Daily PE/PB/PS/PCF + turnover + suspension + ST flag (back to 2016; **Beijing Exchange not supported**, V3.7 new) |
| **Listing / Delisting Date** | ipoDate / outDate / status (only zero-auth source for delisting dates, V3.7 new) |
| **SW Industry History** | Every industry reclassification per stock (removes look-ahead bias; codes only, no Chinese names, V3.7 new) |

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

| Endpoint | Data |
|----------|------|
| Investor Q&A (IRM) | Investor questions + official company replies (unique source: how a company responds to rumors/news) |
| THS Hot List | Popularity / concept tags / rank change |
| EM Popularity Rank | Rank + rank change + name/price |
| EM Stock Concept Hits | Which concepts the market is grouping this stock under + heat |
| **Public X Post Search** | Post text + author + timestamp + engagement (Xquik, optional API key, read-only, ≤100 rows) |

### Macro (V3.7 new)

| Endpoint | Data |
|----------|------|
| **PBoC Social Financing** | Aggregate Financing to the Real Economy, monthly, 12 columns (RMB/entrusted/trust loans, undiscounted acceptances, corporate & government bonds, equity financing, ABS, write-offs) |
| **NBS PMI** | Manufacturing / non-manufacturing / composite PMI + large / medium / small enterprise breakdown |

### Backup Sources (V3.4 new · fallback when a primary source bans you)

| Endpoint | Data |
|----------|------|
| Official Dragon-Tiger Backup | SSE + SZSE official APIs, zero-auth, authoritative first-party, incl. brokerage seats (when Eastmoney is banned) |
| Fund Flow Backup | Sina daily 4-tier order net flow (super-large / large / medium / small + net inflow) |
| Filings Backup | SZSE official for Shenzhen tickers, Eastmoney for Shanghai, both with direct PDF links (when cninfo is banned) |

> Plus a **per-layer primary → independent-backup table** (exchange official / THS F10 / HKEX / cninfo webapi / Jin10 — all on different rate-limit planes) and a "confirmed dead" list — see the "Backup Sources & Fallback Strategy" section in SKILL.md.

### Authentication

iwencai semantic search and the optional Xquik public post search require API keys. The other 18 sources need no key. The Xquik endpoint performs bounded public reads only. It does not publish content, create monitors, or start bulk jobs. See SKILL.md for setup.

> Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.

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
| **Public X Discussion** | "Find public X posts from the last 7 days about Kweichow Moutai or 600519" |
| News & Filings | "Pull recent news and filings for 300476" |
| Market Flash | "Any big market news right now on the CLS flash feed" |
| Batch Compare | "Compare valuations of these 5 semiconductor stocks" |
| **Chip Distribution** | "How much of 600519 is in profit, where's the average cost and the chip peak" |
| **Valuation History** | "What percentile is Moutai's PE over the past decade, and show turnover too" |
| **ST / Suspension** | "When was 000004 flagged ST, and has it ever been suspended" |
| **Industry Drift** | "Which SW industry was 000001 in back in 2016 — same as today?" |
| **Macro Backdrop** | "What's the latest social financing and PMI — is liquidity loose or tight" |

### 4 Built-in Research Workflows

| Workflow | What it does | Time |
|----------|-------------|------|
| Single Stock Valuation | Live price → Consensus EPS → Forward PE / PEG / PE payback years | 30 sec |
| Batch Comparison | Side-by-side valuation ranking | 1 min |
| Thematic Research | iwencai multi-keyword NL search + Eastmoney PDF cross-reference | 2 min |
| New Target Research | Coverage → Valuation → Concepts → Fund flow → Dragon tiger → Lockup → Margin | 1 min |

---


## V3.7 Highlights

**1 new data layer, 7 new endpoints, 4 new sources** (baostock / SW Research / PBoC / NBS — all zero-registration, zero-key). Every endpoint was run and verified on 2026-08-19.

| Gap it closes | Endpoint | Verified |
|---|---|---|
| **"Chip layer" was a misnomer** — §4.1~4.5 were all capital-flow data, no actual chip distribution | Chip Distribution (CYQ) | Eastmoney has **no** public CYQ endpoint (`push2`/`push2his` both 404 in testing); computed locally from OHLC + turnover, zero new sources |
| **Valuation was same-day snapshot only** | Valuation History | **2,581 rows** of daily PE/PB/PS/PCF for Moutai since 2016-01-04, plus turnover / suspension / ST (000004 shows 276 ST days) |
| **K-line is unadjusted — cross-ex-div comparisons break** | Adjust Factors qfq/hfq | One HTTP call, ~1.8KB; ⚠️ **qfq divides, hfq multiplies** — wrong direction fails silently with wrong numbers |
| **No way to get delisting dates** | Listing / Delisting | Only zero-auth source; lets you drop zombie tickers at the screening stage |
| **Industry was current-only → look-ahead bias** | SW Industry History | **12,893 rows / 5,905 tickers / 38 level-1 industries**; Ping An Bank verified across 1991→2014→2021 |
| **No macro layer at all** | Social Financing + PMI | Social financing monthly, 12 columns (2026-01 flow: 7,218.5bn CNY); PMI 2026-07 manufacturing 49.2 |

> ⚠️ **New dependencies:** `numpy baostock xlrd openpyxl`. baostock is a TCP client library (no registration, no key)
> and **does not support the Beijing Exchange** — codes starting 4/8/92/920 are rejected server-side, so this
> toolkit blocks them before login and raises `ValueError`.

---

## Data Source Priority (V3.2 re-ranked by IP-ban risk)

> **Principle: anything available from mootdx or Tencent (quotes / K-line / live price / market cap / financials) must use them first (never IP-banned). Eastmoney is only for its exclusive data, all routed through the throttled `em_get()`.**

| Priority | Source | Protocol | IP Ban Risk | Use |
|----------|--------|----------|-------------|-----|
| **1 (top)** | mootdx (TDX) | TCP 7709 | **Never banned** | K-line / order book / ticks / financials / F10 |
| **2 (top)** | Tencent Finance | HTTP | **Never banned** | Live price / PE / PB / market cap / turnover / index / ETF |
| 3 | THS Hot Stocks / Northbound | HTTP | Very low (zero auth) | Hot stocks / themes / northbound flow |
| 4 | Baidu Finance | HTTP | Very low | K-line (w/ MA5/10/20) |
| 5 | Sina Finance | HTTP | Low | Financial statements |
| 6 | cninfo | HTTP | Low | Filings |
| 7 | THS Consensus EPS | HTTP | Low (UA required) | Consensus EPS |
| 8 | iwencai | OpenAPI | Low (key required) | NL semantic search |
| 9 | **baostock** | TCP | Low (no registration) | Valuation history PE/PB/PS/PCF + turnover + suspension + ST + listing/delisting dates (**no Beijing Exchange**) |
| 10 | **SW Research** | HTTP | Low (public XLS) | Industry classification history |
| 11 | **PBoC** | HTTP | Low (official site) | Aggregate social financing |
| 12 | **NBS** | HTTP | Low (official site) | PMI |
| optional | **Xquik** | HTTP | Key required; ≤100 rows | Public X post text / author / time / engagement |
| **last (exclusive only)** | **Eastmoney** datacenter/push2/reportapi/search/np-weblist | HTTP | **Medium — has rate-limit risk** | Dragon-tiger / lockup / margin / block trade / shareholders / dividends / fund flow / reports / news (all via `em_get()`) |

> **Architecture:** Except mootdx and baostock (both TCP client libraries), all sources use direct HTTP API calls with no third-party data wrapper in between. **Eastmoney APIs are rate-limited; all calls go through `em_get()` for serial throttling. For batch jobs, increase `EM_MIN_INTERVAL`.**
>
> **Fallback (V3.4 new):** When a primary source is banned or broken, check the "Backup Sources & Fallback Strategy" section in SKILL.md. Core data uses independent domains and rate-limit planes. The sentiment layer can use Xquik as a separate public-discussion source, but it does not replace official IRM answers or popularity rankings.

---

## Changelog

See [CHANGELOG.md](./CHANGELOG.md).

---

## Disclaimer

This project provides data access tools only and does not constitute investment advice. Investing involves risk.

---

## Support

If this tool saved you time, a coffee is appreciated ☕

<p align="center">
  <a href="https://buymeacoffee.com/simonlin1212"><img src="./assets/bmc-qr.png" width="180" alt="Buy Me a Coffee"></a>
</p>

> Need a data endpoint that isn't here? Open an [Issue](https://github.com/simonlin1212/a-stock-data/issues); sponsors' issues go first.

---

## License

[Apache License 2.0](./LICENSE)

**Author:** Simon Lin · X [@linsizhen](https://x.com/linsizhen) · Email: [simonlin0423@gmail.com](mailto:simonlin0423@gmail.com)
