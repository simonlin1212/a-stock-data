# Changelog

## v3.3.2 — 2026-06-30

### 优化（适配器V2: 东财优先 + 智能限流 + 并发降到2）

- **`tools/data_fallback.py`** 重大升级 — 从「纯备用源」改为「东财优先 + 智能防封 + 三级降级」架构：
  - **K线优先东财**：优先尝试 `push2his.eastmoney.com`（前复权，数据最准确），失败后降级到腾讯，再降级到新浪
  - **`em_get()` 限流防封核心**：Session复用（减少TCP连接）+ 串行限流（间隔≥2s + 随机抖动0.1-0.5s）+ 指数退避重试（1s/2s/4s）+ 封禁自动检测（连续3次 `RemoteDisconnected` → 标记封禁 → 后续自动跳过东财）
  - **并发降到2**：`patch_module()` 自动替换 `step3_price_increase_filter`，将 `ThreadPoolExecutor(max_workers=10)` 改为 `max_workers=2`，大幅降低触发风控概率
  - **封禁状态可视化**：step3启动时显示当前东财封禁状态（`[东财已封禁, 使用备用源]` 或正常）
  - 测试验证：东财被封时第一只股票10.9s完成检测+降级，后续股票0.4s/只走腾讯，数据准确

### 防封策略对比

| 项目 | V3.3.1（原方案） | V3.3.2（优化后） |
|------|------------------|------------------|
| K线数据源 | 腾讯优先 → 新浪降级 | **东财优先** → 腾讯 → 新浪 |
| 东财限流 | 无（直接requests.get） | **em_get()**: 间隔≥2s + 随机抖动 + Session复用 |
| 封禁检测 | 无 | **连续3次失败 → 自动标记封禁 → 后续跳过东财** |
| 重试机制 | 无 | **指数退避: 1s → 2s → 4s** |
| 并发数 | 10线程 | **2线程** |
| 东财可用时 | 不使用东财 | **优先使用东财（数据最准确）** |
| 东财被封时 | 直接用腾讯 | **自动检测 → 降级到腾讯（无感知切换）** |

## v3.3.1 — 2026-06-30

### 新增（东财封禁实战分析 + 备用数据源适配器）

- **`docs/anti-ban-case-study.md`** — 2026-06-30 真实封禁案例全记录：用户选股脚本（V2/V3/V4三版本）因「10线程并发 + 零限流 + 15000+请求/次 × 3版本」触发东财IP级封禁（push2/push2his 全系列 `RemoteDisconnected`，持续全天未恢复）。文档包含封禁现象、根因分析（六大因素）、时间线、可用备用源清单、腾讯行情字段实测映射表、防封铁律、选股脚本改造示例代码、多版本扫描时间规划。
- **`tools/data_fallback.py`** — 东财 push2/push2his 被封时的 Monkey-patch 适配器：用 `datacenter-web`(股票列表) + `qt.gtimg.cn`(腾讯实时行情) + `web.ifzq.gtimg.cn`(腾讯前复权K线) + `money.finance.sina.com.cn`(新浪K线降级) 替代被封接口。已实测完成全市场5208只股票扫描（V2→70只 / V3→170只），数据准确。支持成交量复权、多源降级、快速失败切换。

### 关键发现

| 发现 | 详情 |
|------|------|
| **push2 封禁是IP级** | DNS正常解析到 `61.129.129.196`，但直连IP也被拒（`RemoteDisconnected`），确认是服务端IP黑名单 |
| **datacenter-web不受影响** | `datacenter-web.eastmoney.com` 与 push2 不同服务器/不同WAF策略，封禁期间始终可用 |
| **腾讯K线高频后限流** | `web.ifzq.gtimg.cn` 在连续请求5000+次后开始返回空（非封IP，限流），需降级到新浪 |
| **新浪K线稳定** | `money.finance.sina.com.cn` 全程稳定，但不支持前复权（降级方案） |
| **封禁恢复时间未知** | 本次封禁从16:15持续至次日，超过20小时未恢复，远超之前文档中「隔几分钟重试」的估计 |

### 文档更新
- README FAQ 新增「东财 push2 被封怎么办」条目，指向备用数据源适配器和封禁分析文档
- README 数据源优先级表补充：push2/push2his 封禁后可用 datacenter-web + 腾讯 + 新浪 组合替代

### 测试
- 备用适配器实测（2026-06-30 18:44-19:00）：V2全市场5208只→70只、V3主板3042只→170只，K线数据与东财原接口一致（收盘价/涨跌幅吻合），VAR7吸筹计算正常

## v3.3.0 — 2026-06-28

### 新增三层（端点 28 → 40，层数 7 → 10）

**Layer 8 打板层（#23 / #15）**
- **东财涨停板四池**（`push2ex.eastmoney.com`，与现有 push2 同源、走 `em_get` 限流）：`em_zt_pool`（涨停池：连板数 / 几天几板 / 封板资金 / 炸板次数 / 首末封板时间 / 行业）、`em_zb_pool`（炸板池：振幅 / 涨速）、`em_dt_pool`（跌停池：封单资金 / 连续跌停 / 开板次数）、`em_yzt_pool`（昨日涨停池：自算晋级率 / 赚钱效应）。
- **同花顺涨停揭秘** `ths_limit_up_pool`：涨停原因题材 / 封板成功率 / 一字·换手·T字板 / 封单额 / 几天几板。
- **打板情绪速算** `limit_up_sentiment`：炸板率 / 连板高度 / 连板梯队分布。

**Layer 9 ETF 期权层（#13）**
- 新浪源：`sina_option_codes`（50ETF / 300ETF / 科创50ETF / 500ETF 合约清单）、`sina_option_tquote`（T型报价：买卖五档 / 持仓量 / 行权价）、`sina_option_greeks`（希腊字母 Delta / Gamma / Theta / Vega + 隐含波动率 + 理论价值）。**交易所预算好，无需本地算 BSM。**

**Layer 10 舆情互动层**
- `cninfo_irm`（互动易问答：投资者提问 + 公司官方回复，AI 问答独家信源）、`ths_hot_list`（同花顺热榜：人气值 / 概念标签 / 排名变化）、`em_hot_rank`（东财人气榜 + 名称转换）、`em_hot_concept`（个股概念命中）。

### 文档
- **ETF 显式说明**：ETF 行情 / K线一直支持（腾讯 + mootdx，代码直接当股票查），README 使用示例表显式补上 ETF 例子，避免被看漏。
- README（中英）架构图、端点清单、使用示例、亮点区，SKILL.md 触发场景 + 关键词，全部同步到 10 层 40 端点。

### 测试
- 三层全部本机实测真实数据（数据日 20260626）：涨停池 60 只 / 炸板 35 / 跌停 30 / 昨涨停 86 / 同花顺涨停揭秘 60，字段映射 + `price÷1000` + 时间格式化全对；ETF 期权 50ETF/300ETF 合约清单 + T型报价 + 希腊字母（Delta 0.535 平值校验对齐、IV 17.35%）；互动易（比亚迪 50 条中 12 条有公司回复）+ 同花顺热榜 100 条 + 东财人气榜（名称转换）+ 个股概念命中全通。
- **实测纠正的 3 个坑**：东财四池价格字段 ÷1000（非 ÷10000）；互动易第二步参数放 query string（否则 400）；期权希腊字母解析 `[raw[0]] + raw[4:]`（跳 3 个空位）。

### 说明
- 数据源数（13）不变——三个新层用的 push2ex / 新浪 / 巨潮 / 同花顺 / 东财均为已有数据源品牌。

## v3.2.5 — 2026-06-28

### 修复（实测坐实的真 Bug · #31 / #28）
- **§1.1 mootdx K线参数名写错，分钟数据恒退化为日线（#31，CRITICAL）**：旧代码 `client.bars(symbol=..., category=4, ...)` 用了不存在的参数名 `category`。mootdx `bars()` 真实签名是 `bars(symbol, frequency=9, start=0, offset=800, **kwargs)`——`category` 被 `**kwargs` **静默吞掉**，`frequency` 永远取默认值 **9（日线）**。后果：任何 agent 想取分钟/周/月 K 线全部静默退化成日线、且不报错（用户只能自行 fallback 到新浪 API）。**修复**：参数名改 `frequency`，并按 mootdx 0.11.7 源码重写频率值表（旧表 `7=1分钟…11=60分钟` 整段错误）。补 1 分钟（`frequency=8`）/ 5 分钟（`frequency=0`）示例。
- **§1.1 复权口径未说明（#28）**：mootdx `bars` 返回**不复权**原始价（通达信原始数据，签名无 `adjust` 参数），跨除权除息日做估值/回测会失真。文档此前零说明 → 补明确警示：跨除权日需自行复权或改用带前复权的日 K 数据源（腾讯财经）。
- **§full_valuation 机构一致预期 EPS 取错列（HIGH）**：旧代码 `row.iloc[2]` 按位置取，而同花顺 `ths_eps_forecast` 表列序为 `年度/预测机构数/最小值/均值/最大值`——`iloc[2]` 实为「**最小值**」，并非文档声明的「均值＝机构一致预期EPS」。导致 `pe_forward`/`PEG`/估值摘要**系统性偏差**（取值偏低）。**修复**：改按列名 `均值` / `预测机构数` 取，抗列序漂移；解析失败由静默 `except: pass` 改为打印 `[WARN]`。

### 优化
- **§东财 `em_get()` 增加连接级自动重试**（glm review P1.3）：挂载 `HTTPAdapter + urllib3.Retry`（`total=3`、指数退避、`status_forcelist=[429,500,502,503,504]`、仅 GET）。403 不重试（东财风控信号，靠 `EM_MIN_INTERVAL` 降频应对）。老版本 urllib3 缺参数时降级为无重试，不影响主流程。
- **§download_pdf 文件名加固**：`org`（机构简称）与 `title` 一致做 `re.sub` 路径字符清洗 + 截断，避免机构名含 `/` 等字符拼坏保存路径。

### 测试
- 本机实跑 mootdx 0.11.7 坐实 #31：`bars(category=8)` 索引全为 `15:00`（日线，复现退化）；`bars(frequency=8)` 索引 `14:59/15:00`（真 1 分钟）、`frequency=0` 为 5 分钟间隔；`bars` 签名确认无 `category`/`adjust`。
- 实跑同花顺 `worth.html`（600519）坐实 EPS 取列错误：`iloc[2]=最小值=66.27` vs `均值=68.82`；修复后按列名取到 `68.82`。
- `em_get` Retry 挂载 smoke test 通过（`HTTPAdapter` 正常 mount）。

### 说明
- 端点数（28）、数据源数不变；本版为 bugfix + 文档修正。感谢 @hhsacsb（#31）、#28 提问者，及社区 glm review（@taicilang-lcy，#27）。

## v3.2.4 — 2026-06-20

### 修复（mootdx 0.11.x 兼容 · #26 / PR #7）
- **mootdx 0.11.x 全新安装 BESTIP 空串崩溃**：干净环境下 `Quotes.factory(market='std')` 裸调用会抛 `ValueError: not enough values to unpack (expected 2, got 0)`。根因：`~/.mootdx/config.json` 的 `BESTIP.HQ` 初始为空字符串 `""`（非缺失键），mootdx 内部 `dict.get(key, default)` 取不到 default，拆包失败。**老用户（config 曾填充过 IP）不触发，故此前多次实测漏掉。**
- **解法：新增 `tdx_client()` helper（Prerequisites 章节），所有 4 处 mootdx 调用统一改走它。** 顺序探测内置可用服务器列表 `_TDX_SERVERS`（TCP 握手），用第一个可达的显式 `server=(ip,port)` 绕过 BESTIP；三级 fallback（bestip 测速 → 裸 factory → 明确 RuntimeError）保证 IP 列表老化/换网/老用户场景都能工作。
- **明确不锁版本**：锁 `mootdx==0.10.12` 在部分环境（干净 Python 3.9）下 `import mootdx` 因 numpy/pandas 二进制不兼容直接崩，比 0.11.x 更糟。helper 对 0.10 / 0.11 通用，故依赖仍保持 `mootdx>=0.10`。

### 测试
- helper 探测逻辑实测（2026-06-20，本机网络）：`_TDX_SERVERS` 10/10 TCP 可达；语法 `py_compile` 通过。
- 早前隔离实测（临时 venv，mootdx 0.11.7）：强制 `BESTIP.HQ=""` 稳定复现 ValueError；改用 `server=(ip,port)` 显式传参后 `bars()` 正常取回 5 根。

### 说明
- 端点数（28）、数据源数不变；纯兼容性补丁。致谢 PR #7（@ericheroster）提供 helper 思路，本版在其基础上加了三级 fallback 防 IP 老化。

## v3.2.3 — 2026-06-20

### 新增（端点）
- **§2.1 东财行业研报 `eastmoney_industry_reports()`**：研报层补上行业研报端点（此前只有个股研报）。与个股研报**同一端点** `reportapi.eastmoney.com/report/list`，仅 `qType` 不同（`0`=个股 / `1`=行业）。`industry_code="*"` 拉全行业（实测约 47928 篇 / 4793 页），传东财行业码（如 `1238`=IT服务Ⅱ，实测 1863 篇）精确过滤；返回 record 复用 §2.1 的 `download_pdf()` 下载 PDF（模板通用），走 `em_get` 限流。新增字段说明：`industryName`/`industryCode`/`emRatingName`/`reportType`/`attachPages`/`attachSize`。
- 同步架构树研报层一行：「东财 reportapi → 个股研报 + 行业研报 + PDF下载 + 评级 + 三年EPS」。

### 测试
- 实测（2026-06-20，真实公开 API，零 key）：全行业 `qType=1` 返回 `hits=47928`、`TotalPage=4793`，字段含 `industryName`/`industryCode`；按行业码 `1238` 过滤 `hits=1863`；首篇 PDF（`AP202606181823678972`）`H3_{infoCode}_1.pdf` 模板下载成功（2512829 bytes，`%PDF` 头）。
- 行业码表端点（`bxpa` 等）实测 404 不存在 → 文档注明用 `industry_code="*"` 拉取后从结果反查行业码，无独立码表。

### 变更
- 端点数 27 → 28（新增东财行业研报）；数据源数不变（仍走东财 reportapi）。

## v3.2.2 — 2026-06-03

### 修复（失效接口替换 + 隐藏 Bug）
- **§3.3 概念板块归属（#18）**：百度 PAE `getrelatedblock` 接口失效（实测返回 `ResultCode 10003` + 空数组）→ 替换为东财 `slist`（`spt=3`）个股所属板块接口 `eastmoney_concept_blocks()`，**一次请求**拿全行业/概念/地域混合板块列表（板块名 + BK码 + 涨跌幅 + 龙头股），零鉴权、走 `em_get` 限流。函数名 `baidu_concept_blocks` → `eastmoney_concept_blocks`。
- **§7.1 巨潮公告 orgId 硬编码（#19）**：旧代码用 `gssx0{code}` 规则硬编码 orgId，但巨潮 orgId 并非统一格式（601318→`9900002221`、601398→`jjxt0000019`、688017→`9900041602`），导致大量股票（尤其 601xxx 段）`totalAnnouncement=0` 查不到公告 → 新增 `_cninfo_orgid()`，动态查官方映射表 `szse_stock.json`（模块级缓存，6198 只股），硬编码规则降为 fallback。
- **综合用法示例隐藏崩溃**：示例第 6 步仍调用 v3.1 已删除的 `baidu_fund_flow_history()`（`recent['mainIn']`）→ 改为 `eastmoney_fund_flow_minute()`；第 5 步 `baidu_concept_blocks` → `eastmoney_concept_blocks`。

### 文档（诚实标注，非代码 Bug）
- **§4.5 120日资金流 / §5.1 个股新闻**：实测代码本身正常（多网络/时段返回完整数据），但**部分大陆住宅 IP** 会被东财 push2/search-api 连接级间歇风控（表现 `HTTP 000` 或只返回 `passportWeb`）→ 两节各加 ⚠️ 说明：隔几分钟重试 / 换网络 / 调大 `EM_MIN_INTERVAL`。这是 IP 级风控，非代码问题（#18 报告者环境复现，作者多环境实测正常）。

### 测试
- 新代码原样 exec smoke test（含 `em_get` 助手）实测：`eastmoney_concept_blocks` 茅台 27 / 五粮液 28 / 绿的谐波 21 个板块均非空、分类正确；`cninfo_announcements` 平安 601318（2454条）/ 工行 601398（2483条）原失效股恢复，茅台 600519 老规则 fallback 兼容。
- §1.3 百度 K线（同 PAE 主机）实测仍正常（`ResultCode 0`，2001 根），百度作为数据源保留。

### 说明
- 端点数（27）、数据源数不变（百度因 K线 保留，东财 slist 已在册）；本次为失效接口替换 + orgId 动态化 + 示例修复。

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
