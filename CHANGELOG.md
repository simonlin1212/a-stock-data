# Changelog

## v4.1.0 — V3.2.2 同步修复、项目更名

### 项目命名
- 重构后项目名改为 `a-stock-data-next`。
- README 明确说明本项目基于原项目 [simonlin1212/a-stock-data](https://github.com/simonlin1212/a-stock-data) 重构而来。

### 依赖
- 新增 `requirements.txt`，显式列出实际运行依赖：`requests`、`pandas`、`lxml`、`mootdx`、`stockstats`。

### V3.2.2 同步修复
- 同步原项目 V3.2.2 的有效修复：百度 PAE `getrelatedblock` 概念归属接口已失效，新增 `eastmoney_concept_blocks()` 改用东财 `slist`；`baidu_concept_blocks()` 保留为兼容 wrapper。
- 同步原项目 V3.2.2 的有效修复：`cninfo_announcements()` 改为优先读取巨潮官方 `szse_stock.json` 映射表动态解析真实 `orgId`，失败时再回退硬编码规则。
- 新增通用 `HTTP_SESSION` 和 `CNINFO_SESSION`，默认不继承系统代理，避免失效本地代理导致腾讯、百度、同花顺、iwencai、新浪和巨潮请求失败；`urllib` 默认 opener 也禁用环境代理。
- `industry_comparison()` 增加 `82.push2.eastmoney.com` 与 HTTP 备用地址；当前网络下东财 `clist` 仍可能被远端断开，验证报告中标记为 WARN。

### iwencai 配置
- `scripts/a_stock_client.py` 调用 iwencai 时仅从环境变量读取 `IWENCAI_API_KEY`；如果缺失，会提示用户可从 https://www.iwencai.com/skillhub 获取 key 并设置环境变量。
- `SKILL.md`、`README.md` 和 references 同步说明 iwencai key 的环境变量配置方式，删除从 `local-validation` 读取 key 的逻辑和说明。
- `scripts/validate_env.py` 仅检查环境变量 `IWENCAI_API_KEY`。

### 验证
- `scripts/validate_env.py` 在 `a-stock-data-verify` 环境中通过，Python 3.12.13，`requests`、`pandas`、`lxml`、`mootdx`、`stockstats` 均 OK。
- `scripts/smoke_test_endpoints.py --network` 最终结果为 `OK=28, WARN=1`；唯一 WARN 为东财 `clist` 行业排名接口在当前网络下被远端断开。

## v4.0.0 — 渐进式披露重构

### 架构调整
- 将原本约 2000 行的单文件 `SKILL.md` 改造为渐进式披露 Skill 包：
  - `SKILL.md` 只保留中文路由、数据源优先级、脚本入口和输出契约。
  - `scripts/a_stock_client.py` 承载全部端点实现，并保留 V3.2.1 的公开函数名。
  - `references/` 按端点层、估值公式、工作流和 FAQ 分层存储说明。
  - 新增 `agents/openai.yaml` 作为 Codex UI 元数据。
- 新增 `scripts/validate_env.py` 环境检查脚本。
- 新增 `scripts/smoke_test_endpoints.py` 迁移完整性 smoke test。
- `scripts/smoke_test_endpoints.py` 扩展为全量网络 best-effort 验证，覆盖行情、研报、信号、资金筹码、新闻、基本面、公告、mootdx 和 iwencai。

### 依赖
- 新增显式依赖 `lxml`，用于 `ths_eps_forecast()` 通过 `pandas.read_html()` 解析同花顺一致预期表格。

### 修复
- 修复 `dragon_tiger_board()` 在无上榜记录时 `buy_data` / `sell_data` 未初始化导致的异常。
- `baidu_concept_blocks()` 遇到百度 PAE 业务错误时改为返回空结构并附带 `error` 字段，不再直接抛异常中断工作流。
- `em_get()` 增加 3 次串行重试，默认直连东财，失败后再尝试一次环境代理 fallback，提高 push2 / push2his 在不同网络环境下的稳定性。
- `eastmoney_stock_info()` 增加腾讯行情 fallback；当东财 push2 基本面接口不可达时，仍返回名称、价格、市值等基础字段，并附带 `fallback` 和 `error`。
- `eastmoney_fund_flow_minute()` 和 `stock_fund_flow_120d()` 增加 HTTP 备用地址，降低 HTTPS push2 / push2his 瞬态断连影响。

### 兼容性
- 所有 V3.2.1 有效端点保留，端点数仍为 27。
- 财联社旧 API 仍标记为下线，`cls_telegraph()` 仅作为兼容 stub 保留，默认返回空列表。
- 继续保留东财 `em_get()` 串行限流、防封和会话复用策略。
- 安装方式从“只复制 `SKILL.md`”变为“安装完整 `a-stock-data/` Skill 目录”。

## v3.2.1 — 2026-05-30

### 修复（预先存在的解析 Bug，非 v3.2 引入）
- **§5.1 东财个股新闻 `eastmoney_stock_news`**：东财实际返回里 `result.cmsArticleWebOld` **直接就是文章列表**（非 `{list:[...]}` 嵌套），旧写法 `.get("cmsArticleWebOld", {}).get("list", [])` 对 list 调用 `.get` 触发 `AttributeError` / 返回空 → 改为遍历 `d.get("result", {}).get("cmsArticleWebOld", []) or []`。
- **§6.4 新浪财报三表 `sina_financial_report`**：新浪实际结构是 `result.data.report_list`（按报告期如 `'20260331'` 为键的 dict，每期对象的 `data` 字段才是行项列表 `[{item_title, item_value, item_tongbi}]`），旧写法取 `result.data.{report_type}` **永久返回空** → 改为遍历 `report_list` 期次（倒序），每期从 `data` 按 `item_title` 提取，返回「按报告期记录列表」（`{"报告期": ..., "<科目>": <值>, "<科目>_同比": <同比>}`）。新增 `num` 参数（默认 8 期）。

### 测试
- 两函数用真实公开 API（茅台 600519，零 key）实测：个股新闻返回 20 条、字段（date/title/content/mediaName/url）齐全；财报三表 lrb/fzb/llb 各返回 8 期、净利润+同比可取。
- 验证方式：exec SKILL.md 代码块本身（含 `em_get` 助手）直连真实 API 断言非空。

### 说明
- 端点数（27）、数据源数不变；修复来自姊妹项目 astock-peg 移植时实测发现并验证的正确修法。

## v3.2 — 2026-05-30

### 新增（数据源优先级 + 东财防封）
- **数据源优先级原则**：新增「数据源优先级 & 东财防封」章节，明确「能用通达信(mootdx)/腾讯（不封 IP）就别用东财，东财仅用于其独有数据」
- **统一节流入口 `em_get()`**：所有东财端点（datacenter / push2 / push2his / reportapi / search-api / np-weblist 共 9 处调用）改用 `em_get()`，内置：
  - 串行限流（`EM_MIN_INTERVAL=1.0s` 最小间隔 + 0.1~0.5s 随机抖动）
  - 复用 `EM_SESSION`（Keep-Alive）+ 默认 UA
  - 批量任务调大 `EM_MIN_INTERVAL` 即进一步降速
- **东财风控阈值文档化**：列出触发封禁的实测阈值（每秒>5 / 并发≥10 / 1分≥200 / 5分≥300）与 5 条防封铁律

### 修复（失效接口）
- **财联社快讯下线（#14）**：`cls.cn/nodeapi/telegraphList` 等旧接口全面 404（网站迁 Next.js + 新 API 需签名）→ §5.2 标注弃用，全市场快讯改用 §5.3 东财全球资讯（np-weblist）

### 变更
- 端点数 28 → 27（财联社快讯下线）
- README 数据源优先级表重排：mootdx/腾讯置顶（标注「不封 IP」），东财降至末位（标注「中—有风控会封 IP」）
- 用真实东财 API（datacenter 股东户数 + np-weblist 全球资讯）实测 `em_get` 功能与限流间隔（间隔 ≥1s 通过）

## v3.1 — 2026-05-19

### 修复（失效接口替换）
- **百度 PAE 资金流** `fundflow` + `fundsortlist` 已下线（返回 null）→ 替换为东财 push2 分钟级资金流 `eastmoney_fund_flow_minute()`
- **大宗交易** `RPT_DATA_OCCURTRADE` 报表配置已下线 → 替换为 `RPT_DATA_BLOCKTRADE`（字段兼容）
- **龙虎榜机构买卖** `RPT_ORGANIZATION_BUSSINESS` 报表配置已下线 → 改用 BUY/SELL 席位明细筛选 `OPERATEDEPT_CODE="0"`
- **东财全球资讯** 新增必填参数 `req_trace`（UUID），否则返回 403
- **巨潮公告** `stock` 参数格式变更：旧 `"{code},{plate}"` → 新 `"{code},{orgId}"`（如 `600519,gssh0600519`），`column` 改为空字符串

### 优化
- 信号层资金流数据源从百度切换到东财 push2，与 Layer 4 资金面统一为东财体系
- 数据源优先级表更新：百度股市通降级为概念板块+K线，资金流功能归入东财 push2

### 测试
- 28 端点全量实测（2026-05-19），所有端点均通过贵州茅台 600519 验证
- push2 系列 5 个端点在阿里云服务器直连验证通过（本地 Clash 代理可能干扰）

---

## v3.0 — 2026-05-17

### Breaking Changes
- **彻底移除 akshare 依赖**：所有 13 个 akshare 调用替换为直连 HTTP API（东财/新浪/同花顺/财联社源头接口）
- `pip install` 不再需要 `akshare`，依赖缩减为 `mootdx requests pandas stockstats`
- 行业板块数据源从同花顺（401 反爬）切换至东财 push2（`m:90+t:2`，零鉴权）

### 新增（资金面/筹码层 — Layer 4）
- **融资融券明细** `margin_trading()` — 日级融资余额/买入/偿还 + 融券余额/卖出/偿还
- **大宗交易** `block_trade()` — 成交价/量 + 买卖方营业部 + 溢价率
- **股东户数变化** `holder_num_change()` — 季度股东数 + 环比变化 + 户均持股
- **分红送转历史** `dividend_history()` — 每股派息/送股/转增 + 进度状态
- **个股资金流120日** `stock_fund_flow_120d()` — 主力/大单/中单/小单日级净流入

### 新增（行情层）
- **百度K线（带MA5/10/20）** `baidu_kline()` — 返回时直接含均价，无需自行计算
- **指数/ETF 实时行情** — 腾讯 API 扩展支持指数代码和 ETF 代码

### 优化
- 架构从六层升级为**七层**，端点从 20 个增至 **28 个**
- 数据源从 8 个增至 **13 个**（东财 datacenter/push2his/search-api/np-weblist + 新浪 + 财联社 独立计数）
- 新增 `eastmoney_datacenter()` 统一 helper — 龙虎榜/解禁/融资融券/大宗/股东/分红共用
- FAQ 新增 5 条常见问题（akshare 移除原因、行业板块切换、海外部署等）

### 测试
- 28 端点全量实测（2026-05-17），覆盖主板/中小板/科创板/ST
- 所有新增 Tier 1 端点均通过贵州茅台 600519 验证

---

## v2.1 — 2026-05-12

### 新增
- **龙虎榜席位**：`get_dragon_tiger_board` — 上榜记录 + 买卖席位 TOP5 + 机构动向（akshare 三函数聚合）
- **限售解禁日历**：`get_lockup_expiry` — 历史解禁记录 + 未来 90 天待解禁事件
- **行业横向对比**：`get_industry_comparison` — 同花顺 90 行业涨跌幅排名 + 成交额 + 净流入 + 领涨股
- **百度股市通概念板块**：`get_concept_blocks` — 行业/概念/地域三维板块归属 + 当日涨跌幅
- **百度股市通资金流向**：`get_fund_flow` — 主力/散户/超大单/大单分钟级流向 + 20 日历史
- 架构端点从 15 个增至 **20 个**，数据源从 7 个增至 **8 个**

### 优化
- **北向资金自缓存**：eastmoney 全系北向数据 2024-08 起断供，改为本地 CSV 自缓存模式（每次调用自动积累）
- **F10 股东研究截断**：【4.股东变化】只保留最新一期，19969→5906 chars（**-70% token 消耗**）
- **百度 PAE ResultCode 修复**：返回类型 int/string 不稳定，统一 `str()` 比较

### 测试
- 17 接口全量实测，覆盖主板/中小板/科创板/ST 四类股票
- 50 OK / 1 预期 WARN（ST 无机构覆盖）/ 0 FAIL

---

## v2.0 — 2026-05-11

首次开源发布。

### 新增
- **信号层**：同花顺热点（当日强势股 + 题材归因 reason tags）
- **信号层**：同花顺北向资金（hsgtApi 实时分钟 + 历史日级）
- 架构从五层升级为**六层**，端点从 13 个增至 **15 个**

### 包含
- 行情层：mootdx K 线 + 盘口 + 逐笔 / 腾讯财经 PE·PB·市值
- 研报层：东财 reportapi + PDF / akshare 一致预期 / iwencai NL 搜索
- 新闻层：个股新闻 / 财联社快讯 / 全球资讯
- 基础数据：季报 37 字段 / F10 九大类 / 个股基本面
- 公告层：巨潮全量公告 / F10 最新提示
- 4 套调研流程：单票估值 / 批量对比 / 主题研报 / 新标的调研
- 估值框架：前向 PE / PE 消化 / PEG / 30x 锚点

---

## v1.0 — 2026-04

内部版本（未开源）。

- 五层架构 · 13 端点
- 行情 / 研报 / 新闻 / 基础数据 / 公告
