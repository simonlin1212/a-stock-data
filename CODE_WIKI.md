# a-stock-data · Code Wiki

> A股全栈数据工具包 — 7层架构 · 28个端点 · 13个数据源 · 产业链研报分析自动化流水线

---

## 目录

1. [项目概览](#1-项目概览)
2. [整体架构](#2-整体架构)
3. [目录结构](#3-目录结构)
4. [核心模块详解](#4-核心模块详解)
5. [关键类与函数](#5-关键类与函数)
6. [数据层架构（SKILL.md）](#6-数据层架构skillmd)
7. [依赖关系与调用链](#7-依赖关系与调用链)
8. [配置与环境变量](#8-配置与环境变量)
9. [运行方式](#9-运行方式)
10. [常见问题与踩坑](#10-常见问题与踩坑)
11. [版本历史](#11-版本历史)

---

## 1. 项目概览

### 1.1 项目定位

**a-stock-data** 是一个自包含的A股全栈数据工具包，核心价值：

- 整合13个公开数据源的A股原始数据，封装为AI编程助手直接可用的工具集
- 内置产业链研报自动化分析流水线：下载 → LLM分析 → 估值补全 → HTML可视化看板
- 零第三方数据封装依赖（V3.0彻底移除akshare，全部直连HTTP/TCP底层API）
- 兼容 Claude Code / Codex / OpenClaw 等主流AI编程助手

### 1.2 核心特性

| 特性 | 说明 |
|------|------|
| 7层数据架构 | 行情/研报/信号/资金面/新闻/基础数据/公告 七层覆盖 |
| 28个数据端点 | 全部端点实测通过（2026-05-19 覆盖主板/科创板/ST） |
| 13个数据源 | mootdx/腾讯/东财/同花顺/百度/新浪/财联社/巨潮/iwencai等 |
| 研报自动化 | 按行业批量下载 → LLM结构化分析 → 实时估值补全 → 看板生成 |
| 鉴权友好 | 仅iwencai语义搜索需API Key，其余全部免费无Key |

---

## 2. 整体架构

### 2.1 系统组成

项目分为两大部分：

```
a-stock-data
├── 核心数据层 (SKILL.md)          # 7层28端点 · A股全栈数据获取API
│   └── 可独立作为Skill供AI助手调用
│
└── 产业链分析流水线 (3个Python脚本) # 研报→分析→看板 自动化流水线
    ├── industry_report_downloader.py  # Step1: 按行业批量下载研报PDF
    ├── industry_analyzer.py           # Step2: PDF抽取+LLM分析+估值补全
    └── industry_dashboard.py          # Step3: 多Tab HTML看板渲染
```

### 2.2 七层数据架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     A股全栈数据 · 七层架构                       │
├─────────────────────────────────────────────────────────────────┤
│  ① 行情层   mootdx(TCP) + 腾讯财经(HTTP) + 百度K线(HTTP)        │
│             K线(带MA) + 五档盘口 + PE/PB/市值 + 指数/ETF        │
├─────────────────────────────────────────────────────────────────┤
│  ② 研报层   东财 reportapi/PDF + 同花顺一致预期 + iwencai NL     │
│             研报列表 + PDF下载 + 评级预测 + 语义检索            │
├─────────────────────────────────────────────────────────────────┤
│  ③ 信号层   同花顺热点+北向 + 百度概念板块 + 东财push2资金流    │
│             强势股+题材归因 + 龙虎榜 + 解禁 + 行业对比          │
├─────────────────────────────────────────────────────────────────┤
│  ④ 资金面   东财 datacenter + push2his                          │
│             融资融券 + 大宗交易 + 股东户数 + 分红 + 120日资金流 │
├─────────────────────────────────────────────────────────────────┤
│  ⑤ 新闻层   东财 + 财联社（直连HTTP）                           │
│             个股新闻 + 财联社快讯 + 全球资讯                    │
├─────────────────────────────────────────────────────────────────┤
│  ⑥ 基础数据  mootdx finance/F10 + 东财push2 + 新浪财报          │
│             季报37字段 + F10九大类 + 三表 + 个股信息            │
├─────────────────────────────────────────────────────────────────┤
│  ⑦ 公告层   巨潮 cninfo + mootdx F10                            │
│             沪深北全量公告检索+下载                              │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 产业链分析流水线

```
industry_report_downloader.py
        │
        ▼  ① 行业匹配 → ② 成分股列表 → ③ 研报拉取去重 → ④ PDF批量下载
    研报PDF文件夹
        │
        ▼
industry_analyzer.py
        │
        ▼  ⑤ PDF文本抽取(pdfplumber→pypdf→pdfminer降级)
        │
        ▼  ⑥ LLM Map: 逐篇抽取关键事实
        │
        ▼  ⑦ LLM Reduce: 合成结构化JSON(严格schema)
        │
        ▼  ⑧ tencent_quote补全实时行情(现价/PE/PB/市值)
    analysis dict / analysis.json
        │
        ▼
industry_dashboard.py
        │
        ▼  ⑨ 渲染4-Tab HTML看板(总览/成本/风险/估值)
    analysis.html (自包含,离线可打开)
```

---

## 3. 目录结构

```
/workspace/
├── SKILL.md                          # [核心] A股数据Skill文件(28端点完整实现)
├── industry_report_downloader.py     # 研报批量下载器
├── industry_analyzer.py              # 产业链LLM分析器
├── industry_dashboard.py             # HTML看板渲染器
├── README.md                         # 项目说明文档
├── CHANGELOG.md                      # 版本变更日志
├── LICENSE                           # Apache 2.0许可证
├── assets/                           # 静态资源
│   ├── bmc-sponsor.png
│   └── wechat-sponsor.jpg
└── .github/
    └── FUNDING.yml                   # 赞助配置
```

### 文件职责总览

| 文件 | 职责 | 依赖 | 行数 |
|------|------|------|------|
| [SKILL.md](file:///workspace/SKILL.md) | 核心数据层，7层28端点全部实现 | mootdx/requests/pandas/stockstats | ~1500行 |
| [industry_report_downloader.py](file:///workspace/industry_report_downloader.py) | 按行业批量下载东财研报PDF | requests | ~490行 |
| [industry_analyzer.py](file:///workspace/industry_analyzer.py) | PDF文本抽取+LLM分析+估值补全 | requests/pdfplumber/pypdf/pdfminer | ~490行 |
| [industry_dashboard.py](file:///workspace/industry_dashboard.py) | 多Tab HTML看板渲染（纯标准库） | 仅Python标准库 | ~570行 |

---

## 4. 核心模块详解

### 4.1 industry_report_downloader.py — 研报批量下载器

**模块职责：** 按行业关键词从东方财富网批量下载研报PDF，支持过滤/去重/断点续传。

**工作流程：**
1. 拉取东财全行业列表（~100个行业）
2. 模糊匹配用户指定行业
3. 分页拉取行业成分股（最多500只）
4. 逐股拉取研报列表，按infoCode全局去重
5. 支持日期/评级/关键词过滤
6. 批量下载PDF，断点续传（已存在>1KB则跳过）

**关键API端点：**
- 行业列表/成分股: `https://push2.eastmoney.com/api/qt/clist/get`
- 研报列表: `https://reportapi.eastmoney.com/report/list`
- PDF下载: `https://pdf.dfcfw.com/pdf/H3_{infoCode}_1.pdf`

---

### 4.2 industry_analyzer.py — 产业链LLM分析器

**模块职责：** 读取研报PDF文件夹，通过LLM完成产业链结构化分析，补全实时估值数据。

**Map-Reduce LLM架构：**
- **Map阶段：** 逐篇研报抽取关键事实（成本/BOM/龙头/壁垒/风险/估值线索）
- **Reduce阶段：** 汇总所有事实，合成严格schema的结构化JSON分析结果

**输出JSON Schema：**
```python
{
  "industry": "行业名",
  "generated_at": "生成时间",
  "report_count": "研报数",
  "source_dir": "来源目录",
  "overview": {
    "panorama": "产业全景概述",
    "cost_structure": [{"module", "pct", "note"}],      # 赛道成本构成
    "module_importance": [{"module", "importance", "score", "reason"}],
    "module_leaders": [{"module", "leaders", "note"}],  # 模块龙头
    "leader_replaceability": [{"module", "replaceable", "reason"}],
    "bom": [{"component", "pct", "qty", "suppliers", "note"}],  # BOM表
    "milestones": [{"date", "event"}]                   # 产业里程碑
  },
  "cost_components": [
    {"name", "cost_pct", "process", "companies", "advantages", "barriers"}
  ],
  "substitution_risk": {
    "risks": [{"module", "level", "risk"}],
    "safe_tracks": [{"module", "reason"}]
  },
  "valuation": [
    {"name", "code", "module", "growth", "irreplaceability",
     "price", "pe", "pb", "mcap"}  # price/pe/pb/mcap由程序补全
  ]
}
```

---

### 4.3 industry_dashboard.py — HTML看板渲染器

**模块职责：** 将analysis dict渲染为自包含单文件HTML（内嵌CSS+JS，离线可打开）。

**看板结构（4个Tab）：**

| Tab | 内容 |
|-----|------|
| **总览** | 产业全景 + 成本构成条形图 + 模块重要性 + 模块龙头 + 可替代性 + BOM表 + 里程碑时间线 |
| **成本构成** | 各零部件成本占比汇总 + 逐个零部件卡片（工艺/标的企业/优势/技术壁垒） |
| **替代风险** | 风险清单表格 + 安全赛道列表 |
| **估值全景** | 核心标的估值表（名称/代码/模块/现价/PE/PB/市值/增速/不可替代性） |

**设计特点：**
- 深色主题（类GitHub Dark）
- 响应式布局（桌面2列，移动端1列）
- 纯标准库实现（零外部依赖）
- 风险/重要性等级色标：高(红)/中(黄)/低(绿)

---

## 5. 关键类与函数

### 5.1 industry_report_downloader.py 核心函数

| 函数 | 签名 | 职责 |
|------|------|------|
| [fetch_industry_list()](file:///workspace/industry_report_downloader.py#L60-L84) | `() → list[dict]` | 拉取东财全行业列表（~100个），返回名称/代码/涨跌/领涨股 |
| [match_industry()](file:///workspace/industry_report_downloader.py#L87-L96) | `(keyword, list) → list[dict]` | 模糊匹配行业名，优先精确匹配，其次包含匹配 |
| [fetch_industry_stocks()](file:///workspace/industry_report_downloader.py#L101-L137) | `(bk_code, max_stocks=500) → list[dict]` | 分页拉取行业成分股，自动翻页，返回代码/名称/价格/涨跌幅 |
| [fetch_reports_for_stock()](file:///workspace/industry_report_downloader.py#L142-L184) | `(code, begin_date, end_date, max_pages=3) → list[dict]` | 拉取单只股票研报列表，返回原始record含infoCode/title/org/rating |
| [fetch_reports_for_industry()](file:///workspace/industry_report_downloader.py#L187-L246) | `(stocks, begin, end, rating/keyword/limit) → list[dict]` | 批量拉取行业研报，**按infoCode全局去重**，支持过滤 |
| [sanitize_filename()](file:///workspace/industry_report_downloader.py#L251-L253) | `(s, max_len=80) → str` | 清理文件名非法字符 |
| [download_pdf()](file:///workspace/industry_report_downloader.py#L256-L301) | `(record, target_dir, dry_run) → (status, path)` | 下载单篇PDF，断点续传（>1KB已存在则skip），返回ok/skip/fail/dry |
| [batch_download()](file:///workspace/industry_report_downloader.py#L304-L334) | `(reports, output_dir, delay=0.5, dry_run) → stats` | 批量下载，打印进度，返回ok/skip/fail统计 |
| [main()](file:///workspace/industry_report_downloader.py#L366-L488) | CLI入口 | 解析参数，执行完整下载流水线 |

---

### 5.2 industry_analyzer.py 核心函数

#### PDF文本抽取层

| 函数 | 签名 | 职责 |
|------|------|------|
| [_extract_with_pdfplumber()](file:///workspace/industry_analyzer.py#L70-L78) | `(path, max_pages) → str` | pdfplumber抽取（首选） |
| [_extract_with_pypdf()](file:///workspace/industry_analyzer.py#L81-L89) | `(path, max_pages) → str` | pypdf抽取（备选1） |
| [_extract_with_pdfminer()](file:///workspace/industry_analyzer.py#L92-L94) | `(path, max_pages) → str` | pdfminer抽取（备选2） |
| [extract_pdf_text()](file:///workspace/industry_analyzer.py#L97-L109) | `(path, max_pages=30) → str` | **优雅降级抽取**，按顺序尝试三个库，全部失败返回空串 |
| [load_corpus()](file:///workspace/industry_analyzer.py#L112-L136) | `(folder, max_pages, max_files) → list[dict]` | 读取文件夹全部PDF，抽取文本，返回 `[{file, text}]` |

#### LLM客户端层

| 函数 | 签名 | 职责 |
|------|------|------|
| [llm_chat()](file:///workspace/industry_analyzer.py#L141-L171) | `(messages, temp=0.2, max_tokens=4096, retries=2) → str` | OpenAI兼容接口调用，指数退避重试，返回content文本 |
| [_parse_json_loose()](file:///workspace/industry_analyzer.py#L174-L186) | `(text) → Any` | LLM输出宽松JSON解析，容忍```json代码块包裹，截取{} |

#### LLM Map-Reduce层

| 函数 | 签名 | 职责 |
|------|------|------|
| [map_reports()](file:///workspace/industry_analyzer.py#L203-L226) | `(corpus, max_chars=6000, use_llm) → list[dict]` | **Map阶段：** 逐篇研报抽取关键事实，返回 `[{file, facts}]` |
| [reduce_facts()](file:///workspace/industry_analyzer.py#L267-L280) | `(industry, facts, max_chars=40000) → dict` | **Reduce阶段：** 汇总事实合成结构化JSON，严格遵循schema |
| [empty_skeleton()](file:///workspace/industry_analyzer.py#L283-L295) | `() → dict` | 无LLM/无Key时返回空骨架，保证看板结构完整 |

#### 估值补全层

| 函数 | 签名 | 职责 |
|------|------|------|
| [tencent_quote()](file:///workspace/industry_analyzer.py#L299-L341) | `(codes) → dict[code→quote]` | 腾讯财经批量实时行情，返回name/price/pe_ttm/pb/mcap_yi |
| [enrich_valuation()](file:///workspace/industry_analyzer.py#L344-L365) | `(analysis) → analysis` | 对valuation列表中有效6位代码的标的补全实时price/pe/pb/mcap |

#### 主流水线

| 函数 | 签名 | 职责 |
|------|------|------|
| [analyze()](file:///workspace/industry_analyzer.py#L370-L410) | `(input_dir, industry, use_llm, max_pages...) → dict` | 完整流水线：加载PDF → LLM map → LLM reduce → 估值补全 |
| [main()](file:///workspace/industry_analyzer.py#L434-L490) | CLI入口 | 支持--input/--from-json/--no-llm/--dump-json等模式 |

---

### 5.3 industry_dashboard.py 核心函数

#### 工具函数

| 函数 | 签名 | 职责 |
|------|------|------|
| [esc()](file:///workspace/industry_dashboard.py#L40-L44) | `(v) → str` | HTML转义，None→空字符串 |
| [fmt_num()](file:///workspace/industry_dashboard.py#L47-L57) | `(v, suffix="", digits=2) → str` | 数字格式化，空值返回'—'，支持千分位 |
| [level_class()](file:///workspace/industry_dashboard.py#L60-L69) | `(level) → str` | 风险/重要性等级→CSS class：高→lv-high(红)/中→lv-mid(黄)/低→lv-low(绿) |

#### Tab渲染函数

| 函数 | 签名 | 职责 |
|------|------|------|
| [_render_cost_bars()](file:///workspace/industry_dashboard.py#L74-L92) | `(cost_structure) → str` | 成本构成→水平条形图HTML |
| [_render_overview()](file:///workspace/industry_dashboard.py#L95-L205) | `(ov) → str` | 总览Tab：全景/成本条/重要性/龙头/可替代性/BOM/里程碑 |
| [_render_cost()](file:///workspace/industry_dashboard.py#L208-L241) | `(components) → str` | 成本构成Tab：成本汇总条 + 逐个零部件卡片 |
| [_render_risk()](file:///workspace/industry_dashboard.py#L244-L283) | `(risk) → str` | 替代风险Tab：风险表 + 安全赛道表 |
| [_render_valuation()](file:///workspace/industry_dashboard.py#L286-L314) | `(valuation) → str` | 估值全景Tab：核心标的估值大表 |

#### 主渲染

| 函数 | 签名 | 职责 |
|------|------|------|
| [render_html()](file:///workspace/industry_dashboard.py#L399-L447) | `(analysis) → str` | 组装完整HTML文档（内嵌CSS+JS） |
| [render_dashboard()](file:///workspace/industry_dashboard.py#L450-L456) | `(analysis, output_path) → str` | 渲染并写入HTML文件，返回绝对路径 |
| [demo_analysis()](file:///workspace/industry_dashboard.py#L461-L551) | `() → dict` | 内置人形机器人产业链示例数据，用于预览样式 |
| [main()](file:///workspace/industry_dashboard.py#L556-L574) | CLI入口 | 支持--demo预览，或从JSON文件渲染 |

---

## 6. 数据层架构（SKILL.md）

SKILL.md是项目核心，包含7层28个数据端点的完整Python实现。以下是分层概览：

### 6.1 全局工具函数

| 函数 | 职责 |
|------|------|
| `get_prefix(code)` | 6位代码→市场前缀(sh/sz/bj) |
| `eastmoney_datacenter(report_name, ...)` | 东财数据中心统一查询helper（龙虎榜/解禁/两融/大宗/股东/分红共用） |

### 6.2 Layer 1: 行情层（3端点）

| 端点 | 函数 | 数据源 | 数据内容 |
|------|------|--------|----------|
| mootdx行情 | `client.bars/quotes/transaction` | TCP 7709 | K线(多周期)/46字段实时报价/逐笔成交 |
| 腾讯财经 | `tencent_quote(codes)` | HTTP qt.gtimg.cn | PE(TTM)/PB/市值/换手率/涨跌停/指数/ETF |
| 百度K线 | `baidu_kline_with_ma(code)` | HTTP finance.pae.baidu.com | 日K线**自带MA5/MA10/MA20** |

### 6.3 Layer 2: 研报层（4端点）

| 端点 | 函数 | 数据源 | 数据内容 |
|------|------|--------|----------|
| 东财研报列表 | `eastmoney_reports(code)` | reportapi.eastmoney.com | 研报列表+评级+三年EPS预测 |
| 东财PDF下载 | `download_pdf(record)` | pdf.dfcfw.com | 研报PDF（已处理Referer鉴权） |
| 同花顺一致预期 | `ths_eps_forecast(code)` | basic.10jqka.com.cn | 机构一致预期EPS |
| iwencai NL搜索 | `iwencai_search/query()` | openapi.iwencai.com | 自然语言跨主题检索（需API Key） |

### 6.4 Layer 3: 信号层（9端点）

| 端点 | 函数 | 数据源 | 数据内容 |
|------|------|--------|----------|
| 同花顺热点 | `ths_hot_reason(date)` | zx.10jqka.com.cn | 当日强势股+**题材归因reason tags** |
| 同花顺北向实时 | `hsgt_realtime()` | data.hexin.cn | 沪股通/深股通分钟级流向(262点) |
| 北向历史缓存 | `_save/_load_northbound_*` | 本地CSV | 自缓存日级北向历史 |
| 百度概念板块 | `baidu_concept_blocks(code)` | finance.pae.baidu.com | 行业/概念/地域三维归属 |
| 东财资金流(分钟) | `eastmoney_fund_flow_minute(code)` | push2.eastmoney.com | 主力/大单/中单/小单/超大单分钟净流入 |
| 龙虎榜席位 | `dragon_tiger_board(code,...)` | datacenter-web | 上榜记录+买卖TOP5+机构动向 |
| 全市场龙虎榜 | `daily_dragon_tiger(date)` | datacenter-web | 每日全市场上榜+净买额排名 |
| 限售解禁日历 | `lockup_expiry(code,...)` | datacenter-web | 历史解禁+未来90天待解禁 |
| 行业板块排名 | `industry_comparison(top_n)` | push2.eastmoney.com | 全行业涨跌/上涨下跌家数/领涨股 |

### 6.5 Layer 4: 资金面/筹码层（5端点）

| 端点 | 函数 | RPT报表名 | 数据内容 |
|------|------|-----------|----------|
| 融资融券 | `margin_trading(code)` | RPTA_WEB_RZRQ_GGMX | 融资/融券余额/买入/偿还 |
| 大宗交易 | `block_trade(code)` | RPT_DATA_BLOCKTRADE | 成交价/量+营业部+溢价率 |
| 股东户数 | `holder_num_change(code)` | RPT_HOLDERNUMLATEST | 季度股东数+环比+户均持股 |
| 分红送转 | `dividend_history(code)` | RPT_SHAREBONUS_DET | 每股派息/送股/转增+进度 |
| 资金流120日 | `stock_fund_flow_120d(code)` | push2his | 主力/大单/中单/小单日级净流入 |

### 6.6 Layer 5: 新闻层（3端点）

| 端点 | 函数 | 数据源 | 数据内容 |
|------|------|--------|----------|
| 东财个股新闻 | `eastmoney_stock_news(code)` | search-api-web (JSONP) | 个股相关新闻 |
| 财联社快讯 | `cls_flash()` | cls.cn | 分钟级全市场电报 |
| 东财全球资讯 | `eastmoney_global_news()` | np-weblist (需req_trace UUID) | 7×24全球财经快讯 |

### 6.7 Layer 6: 基础数据层（4端点）

| 端点 | 函数/方法 | 数据源 | 数据内容 |
|------|-----------|--------|----------|
| 季报快照 | `client.finance` | mootdx TCP | 37字段(EPS/ROE/净利润/营收...) |
| F10公司资料 | `client.get_finance_text_category(...)` | mootdx TCP | 9大类文本(截断优化-70%token) |
| 东财个股信息 | `eastmoney_stock_info(code)` | push2 | 行业/总股本/流通股/市值/上市日期 |
| 新浪财报三表 | `sina_financial_statements(code)` | quotes.sina.cn | 资产负债表/利润表/现金流量表 |

---

## 7. 依赖关系与调用链

### 7.1 Python包依赖

```
核心数据层 (SKILL.md 运行时):
├── mootdx >= 0.10      # TCP行情/财务/F10（唯一非HTTP依赖）
├── requests            # 所有HTTP API直连
├── pandas              # 数据处理+HTML表格解析
└── stockstats          # 技术指标计算(RSI/MACD/BOLL等)

研报下载器:
└── requests            # 仅需requests

LLM分析器:
├── requests            # LLM API + 腾讯行情
├── pdfplumber          # PDF文本抽取（首选）
├── pypdf               # PDF抽取备选1
└── pdfminer.six        # PDF抽取备选2

HTML渲染器:
└── (仅Python标准库)    # 零外部依赖！
```

### 7.2 模块调用关系

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI 入口点                              │
├─────────────────────────────────────────────────────────────┤
│  industry_report_downloader.py (main)                       │
│       │                                                     │
│       ├─→ fetch_industry_list()  ──→ 东财push2 API          │
│       ├─→ match_industry()                                  │
│       ├─→ fetch_industry_stocks() ──→ 东财push2 API         │
│       ├─→ fetch_reports_for_industry()                      │
│       │    └─→ fetch_reports_for_stock() ──→ 东财reportapi  │
│       └─→ batch_download()                                  │
│            └─→ download_pdf() ──→ 东财pdf.dfcfw.com         │
│                                                             │
│  industry_analyzer.py (main)                                │
│       │                                                     │
│       ├─→ analyze()                                         │
│       │    ├─→ load_corpus()                                │
│       │    │    └─→ extract_pdf_text()                      │
│       │    │         ├─→ _extract_with_pdfplumber()         │
│       │    │         ├─→ _extract_with_pypdf()              │
│       │    │         └─→ _extract_with_pdfminer()           │
│       │    ├─→ map_reports()  ──→ llm_chat() (OpenAI兼容)  │
│       │    ├─→ reduce_facts() ──→ llm_chat()                │
│       │    └─→ enrich_valuation()                           │
│       │         └─→ tencent_quote() ──→ 腾讯财经API         │
│       └─→ render_dashboard() ──→ industry_dashboard.py      │
│                                                             │
│  industry_dashboard.py (main)                               │
│       └─→ render_dashboard()                                │
│            └─→ render_html()                                │
│                 ├─→ _render_overview()                      │
│                 ├─→ _render_cost()                          │
│                 ├─→ _render_risk()                          │
│                 └─→ _render_valuation()                     │
└─────────────────────────────────────────────────────────────┘
```

### 7.3 数据流向

```
东财/腾讯/同花顺/百度/新浪/财联社/巨潮
    │
    │ HTTP/TCP
    ▼
SKILL.md 28端点函数 (原始数据)
    │
    ├──────────────────────────────────┐
    │                                  │
    ▼                                  ▼
个股查询/估值/题材分析         industry_report_downloader.py
    │                                  │
    │                           PDF文件(本地)
    │                                  │
    │                                  ▼
    │                         industry_analyzer.py
    │                                  │
    │                         analysis dict / JSON
    │                                  │
    └──────────┬───────────────────────┘
               │  (tencent_quote补全估值)
               ▼
         industry_dashboard.py
               │
               ▼
         analysis.html (自包含看板)
```

---

## 8. 配置与环境变量

### 8.1 必需/可选环境变量

| 变量名 | 必需 | 用途 | 默认值 |
|--------|------|------|--------|
| `LLM_API_KEY` | 分析器LLM功能需要 | OpenAI兼容接口Key | `""` (空→跳过LLM用骨架) |
| `LLM_BASE_URL` | 否 | LLM API Base URL | `https://api.openai.com/v1` |
| `LLM_MODEL` | 否 | 模型名称 | `gpt-4o-mini` |
| `IWENCAI_API_KEY` | 仅iwencai搜索需要 | iwencai语义搜索Key | `""` |
| `IWENCAI_BASE_URL` | 否 | iwencai API地址 | `https://openapi.iwencai.com` |

> **说明：** 除iwencai语义搜索和LLM分析功能外，其余所有数据端点均无需任何API Key，完全免费。

### 8.2 本地缓存

北向资金历史数据缓存路径：
```
~/.tradingagents/cache/northbound_daily.csv
```
格式：`date,hgt,sgt` （日期,沪股通净买额亿,深股通净买额亿），每次调用自动积累。

---

## 9. 运行方式

### 9.1 安装依赖

```bash
# 核心数据层依赖
pip install mootdx requests pandas stockstats

# 产业链分析流水线额外依赖
pip install pdfplumber  # 或 pypdf / pdfminer.six（优雅降级，任一即可）
```

### 9.2 SKILL.md 安装（AI助手集成）

```bash
# Claude Code 用户
mkdir -p ~/.claude/skills/a-stock-data
curl -o ~/.claude/skills/a-stock-data/SKILL.md \
  https://raw.githubusercontent.com/simonlin1212/a-stock-data/main/SKILL.md
```

Codex/OpenClaw用户：将SKILL.md内容贴入系统prompt或项目上下文即可。

### 9.3 产业链研报分析流水线

#### Step 1: 列出可用行业
```bash
python industry_report_downloader.py --list-industries
```

#### Step 2: 下载行业研报
```bash
# 下载"半导体"行业最近90天研报
python industry_report_downloader.py --industry 半导体 --days 90

# 下载"新能源汽车"行业，仅"买入"评级，最多50篇
python industry_report_downloader.py --industry 新能源汽车 --rating 买入 --limit 50

# 自定义输出目录
python industry_report_downloader.py --industry 白酒 --output ./reports/baijiu

# Dry run模式：只列出清单不下载
python industry_report_downloader.py --industry 人形机器人 --dry-run
```

#### Step 3: LLM分析 + 生成看板
```bash
# 完整流水线：PDF抽取 → LLM分析 → 估值补全 → HTML看板
export LLM_API_KEY="sk-..."  # 可选，不设则用空骨架
python industry_analyzer.py \
  --input ./reports/半导体 \
  --industry 半导体 \
  -o 半导体看板.html

# 导出中间JSON便于调试/二次渲染
python industry_analyzer.py \
  --input ./reports/半导体 \
  --industry 半导体 \
  --dump-json analysis.json

# 从已有JSON渲染（跳过PDF/LLM，仍补全实时估值）
python industry_analyzer.py --from-json analysis.json -o 看板.html

# 无LLM模式：仅估值层+骨架（无需API Key）
python industry_analyzer.py \
  --input ./reports/半导体 \
  --industry 半导体 \
  --no-llm
```

#### Step 4 (可选): 单独渲染看板样式预览
```bash
python industry_dashboard.py --demo -o demo.html
# 或从JSON渲染
python industry_dashboard.py analysis.json -o analysis.html
```

### 9.4 Python API 调用示例

```python
# 估值补全 + 看板渲染
from industry_analyzer import tencent_quote, enrich_valuation
from industry_dashboard import render_dashboard

# 拉取实时行情
quotes = tencent_quote(["688017", "600519"])
for code, q in quotes.items():
    print(f"{q['name']}: 价{q['price']} PE={q['pe_ttm']} 市值{q['mcap_yi']}亿")

# 渲染看板
analysis = {"industry": "示例", "overview": {}, "cost_components": [], ...}
analysis = enrich_valuation(analysis)
path = render_dashboard(analysis, "output.html")
print(f"看板: {path}")
```

---

## 10. 常见问题与踩坑

### 10.1 数据源已知坑

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 腾讯API字段43不是PB | 网上教程普遍写错 | **43=振幅%，46=PB**（已实测校准） |
| 百度ResultCode类型不稳定 | 有时返回int `0`，有时string `"0"` | 用 `str()` 统一比较 |
| iwencai返回401 | SkillHub 2.0强制X-Claw Headers | 确保携带完整X-Claw-*头 |
| 同花顺热点reason为空 | 盘后数据15:30后才更新；ST股无标注 | 盘后调用，dropna过滤 |
| 北向资金历史只有几天 | V2.1改为本地自缓存模式 | 持续运行自动积累，首次只有当天 |
| 东财全球资讯403 | V3.1新增必填`req_trace` UUID | 必须生成UUID传入 |
| 巨潮公告查不到 | `stock`参数从`code,plate`改为`code,orgId` | 新格式如`600519,gssh0600519` |
| push2资金流单位问题 | 金额单位是**元**（非万元） | 使用时注意 `/1e4` 或 `/1e8` 换算 |
| mootdx海外超时 | TCP直连通达信服务器需国内IP | 走代理或切换其他数据源 |

### 10.2 架构设计原则

1. **零第三方数据封装**：除mootdx(TCP)外全部直连HTTP API，避免akshare等中间层故障点
2. **优雅降级**：PDF抽取三库fallback，无LLM Key时空骨架保证流程不中断
3. **断点续传**：研报PDF已存在(>1KB)自动跳过
4. **全局去重**：行业研报按infoCode去重，避免同一研报被多只成分股重复挂载
5. **自包含输出**：HTML看板内嵌CSS/JS，单文件离线可打开
6. **零依赖渲染**：industry_dashboard.py仅用标准库，任何Python环境可运行

---

## 11. 版本历史

详见 [CHANGELOG.md](file:///workspace/CHANGELOG.md)

| 版本 | 日期 | 关键变更 |
|------|------|----------|
| **v3.1** | 2026-05-19 | 修复4个失效接口（百度PAE→东财push2，大宗交易/机构席位报表更新），东财全球资讯/巨潮公告参数修复，28端点全量实测 |
| **v3.0** | 2026-05-17 | **Breaking Change：彻底移除akshare**，全部直连HTTP；新增资金面/筹码层5端点；七层架构+28端点+13数据源 |
| v2.1 | 2026-05-12 | 新增龙虎榜/解禁/行业对比/百度概念/百度资金流；北向资金自缓存；F10截断-70%token |
| v2.0 | 2026-05-11 | 首次开源；新增信号层（同花顺热点+北向）；六层架构15端点 |
| v1.0 | 2026-04 | 内部版本；五层架构13端点 |

---

## License

[Apache License 2.0](file:///workspace/LICENSE)

**作者：** Simon 林 · 抖音「Simon林」 · 公众号「硅基世纪」

> **Disclaimer：** 本项目仅提供数据获取与分析工具，不构成任何投资建议。股市有风险，投资需谨慎。
