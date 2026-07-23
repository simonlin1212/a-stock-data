# Changelog

## v3.5.0 — 2026-07-23

板块资金流向（#37 收口）。**端点 43 → 44，数据源 15 / 层数 10 不变（新端点与行业排名同源）。**

### 新增
- **§3.8 `board_fund_flow()` 板块资金流向**：补上此前缺失的**板块级资金流**——`board_type` 支持行业(industry)/概念(concept)/地域(region) 三类，`period` 支持今日(today)/5日(5d)/10日(10d) 三周期，按主力净流入降序返回：主力净额 + 主力净占比 + 涨跌幅 + 领涨股，**今日周期额外含超大/大/中/小单四档明细**。
  - 与 §3.7 `industry_comparison()` **同源同接口**（东财 push2 `clist`，`fs=m:90+t:2/t:3/t:1`）——此前只请求了价格/涨跌家数字段（`f2,f3,f104,f105...`），本版补请求资金流字段（今日 `f62/f184/f66/f72/f78/f84`、5日 `f164/f165/f257`、10日 `f174/f175`）即覆盖。正如 #37 报告者 + trae 的诊断：「同一个接口，只查了几列没查全」。
  - 走 `em_get()` 限流防封（东财源）；非法 `board_type`/`period` 抛 `ValueError`。
  - **坑记录**：板块级只有今日/5日/10日（**无 3日**，个股级才有）；东财 `clist` 返回的 `total` 字段不可信（行业板块报 496 实际 100 个），代码用 `len(items)`；10日领涨股名称字段（f267/f268 均为数字）未干净识别，故 10日省略领涨名。

### 测试（真实数据 smoke test，2026-07-23）
- 行业·今日：100 个板块主力净额降序，电力设备 64.66亿（= 超大 43.55亿 + 大 21.11亿，主力=超大+大校验通过）+ 四档明细 + 领涨股。
- 概念·5日（黄金概念 81.71亿）、地域·10日（宁夏板块）均真实返回；`f109`(5日涨跌)/`f160`(10日涨跌) 字段验证正确。
- 参数校验：非法 board_type='x' / period='3d' 均被 `ValueError` 拒绝。
- 全文件 48 个 Python 代码块 `py_compile` 零语法错误。

## v3.4.1 — 2026-07-23

前缀路由 + mootdx 验活 bug 修复（社区实测反馈收口）。**端点 43 · 数据源 15 · 层数 10 均不变，纯质量修复。**

### 修复

- **§1.2 `tencent_quote()` / §市场前缀规则 `get_prefix()` 前缀路由错判（#40 #41）**：`5` 开头沪市 ETF（`510300` / `510050` / `588200`）、沪深指数（`000300` / `000016` / `000905` 等）此前落到 `else → sz`，腾讯 `qt.gtimg.cn` 对 `sz510300` / `sz000300` 返回空 —— **更危险的是 `000016` 被拼成 `sz000016`（*ST康佳A），静默返回完全不相干标的的数据**。§1.2 docstring 自带的 ETF / 指数示例本身因此跑不通。修复：两处同步改为 `5x → sh` + 沪指数白名单 `SH_INDEX{000300,000905,000016,000688,000852,000010}` + 支持显式前缀 `sh/sz/bj` 透传（解决 `000001` 上证指数 vs 平安银行歧义）。
- **§1.1 `tdx_client()` 探测通过 ≠ 能取数，静默返回空表（#43）**：原 `_probe()` 只做 `socket.create_connection` TCP 握手，坏服务器可握手通过却对真实取数请求回 2 字节空 body（`tdxpy` 按 header 声称的根数解析越界 → `struct.error` 被 `raise_exception=False` 吞掉 → mootdx 包成空 DataFrame），或直接 `ConnectionReset` 使 `tdx_client()` 崩溃且走不到 fallback。新增 `_validate()`：每个候选 server 必须真实拉一根 K 线（`bars('000001', frequency=9, offset=1)`）非空才采用；`factory()` 连接异常改 try/except 跳过下一台；bestip / 裸 factory fallback 同样验活；全部失败才抛明确 `RuntimeError`。**把「静默空表 / 崩溃」变成「自动切到可用源，或明确报错」。**

### 新增

- **备用源速查 K线行补腾讯分钟 K 线（#43）**：同花顺 K 线备胎只有 30/60 分，mootdx 一挂就无 5 分钟源。补腾讯 `ifzq.gtimg.cn/appstock/app/kline/mkline`（`m1/m5/m15/m30/m60`，≤320 根，零鉴权不封 IP，需 `Referer: https://gu.qq.com/`）。⚠️ 文档标注字段坑：返回数组第 7 个字段是**换手率基点**不是成交额（当成交额读会小三个数量级），成交额需自算 `量(手) × 100 × 均价`。

### 测试（全部真实数据 smoke test，2026-07-23）

- `get_prefix()` 11 例路由全对：`510300/588200 → sh`、`000300/000016 → sh`、`159915/399006 → sz`、`600519 → sh`、`000001 → sz`、`830799 → bj`、显式 `sh000001 → sh` / `sz000016 → sz`。
- `tencent_quote()` 真实拉数：沪深300ETF华泰柏瑞 / 上证50ETF华夏 / 沪深300指数 / 上证50指数 / 创业板ETF易方达 / 贵州茅台 / 平安银行 —— 名称与现价全部命中（修复前 ETF/指数全部 NO DATA 或返错票）。
- 新 `tdx_client()`：本机 10 台 pin 服全部 `_probe` 假阳性（握手通、取数 reset），正确跳过 → fallback bestip 验活通过 → 返回 600519 真实日线；修复前会崩溃 / 返空表。
- 腾讯 m5：`603986` 返回 10 根、8 字段、第 7 字段确为换手率基点，验证通过。

## v3.4.0 — 2026-07-11

接口质量修复 + 备用源韧性层。**端点 40 → 43（新增 3 个官方备胎函数），数据源 13 → 15（新增沪深交易所官方），层数 10 不变。**

### 修复（接口质量普查，40 端点全量实测后收口）
- **§5.2 财联社快讯复活（#14 收口）**：2026-05 下线的是旧 `nodeapi` 系接口；官方新版 `cls.cn/v1/roll/get_roll_list` 一直可用，只是强制 `sign` 校验——sign 纯本地可算（`md5(sha1(按 key 字典序拼接的 query 串))`），零 key。`cls_telegraph()` 重写接入新版，V3.2 移除的全市场电报能力恢复，与 §5.3 东财 7×24 互为独立备份（不同源、不同风控面）。
- **§3.6 `lockup_expiry` 字段名 bug**：东财 `RPT_LIFT_STAGE` 报表改列名，旧 `LIMITED_STOCK_TYPE` / `FREE_SHARES_NUM` 恒空 → 改 `FREE_SHARES_TYPE` / `FREE_SHARES`，并新增 `able_shares`（`ABLE_FREE_SHARES`，实际可流通股数，更贴近真实抛压）。
- **§3.7 `industry_comparison` 排序 bug**：clist 请求缺排序字段，`top`/`bottom` 切片并非按涨幅排序 → 补 `fid=f3`，现按涨跌幅真实降序。
- **§3.2 深股通标注**：北向盘中实时披露 2024-08 起收紧，沪股通(hgt)分钟序列完整、深股通(sgt)常只回零星几个点且末值量级异常（上游问题非代码 bug）→ 加显著警示：hgt 可用于当日情绪、sgt 仅供参考，权威北向用 HKEX 官方日统计。

### 新增：备用源速查 & 降级策略（韧性层）
- **十层主源 → 独立备胎速查表**：每类数据一条不同域名、不同风控面的备胎（交易所官方 / 新浪 / 同花顺 / HKEX / 巨潮 webapi / 金十），东财 IP 被封成片失联时可即时降级。附「已死透别用」名单（网易 / 和讯 / 凤凰 / 腾讯资金流 / 雪球免登录深度数据）。
- **3 个官方备胎函数（全部实测）**：`dragon_tiger_backup()`（上交所 `showTradePublicFile.do` + 深交所 `1842_xxpl`，零鉴权权威一手，含营业部席位）、`fund_flow_backup()`（新浪 `MoneyFlow.ssl_qsfx_zjlrqs`，日度四档单净额）、`announcements_backup()`（深市走深交所官方 `annList`、沪市走东财，均带 PDF 直链）。
- 新增数据源：**上交所官方**（query.sse.com.cn / yunhq.sse.com.cn）、**深交所官方**（szse.cn）。

### 体验
- **顶部新增「端点路由速查」总表**（§ → 函数 → 用途 → 源）：60+ 内嵌函数首次有一页总览，agent 可按表定位章节局部读取，不必通读全文。
- **FAQ 新增 3 条**：东财 403/连接重置三步处理（等待/降频/查备胎）、财联社为何复活、mootdx 库烂尾但通达信协议照常（含 easy_tdx 预案）。
- 数据源优先级章节补「降级」原则；架构树新闻层同步财联社复活状态。

### 测试（全部真实数据 smoke test）
- 财联社 v1+sign：HTTP 200 / errno=0，真实电报直出。
- 解禁（600519）：`type` / `shares` / `able_shares` 三字段非空。
- 行业排名：`top` 按涨跌幅降序（当日 TOP1 航天装备 +10.36%）。
- 3 个备胎函数：深交所龙虎榜 JSON 直出、上交所全文（含营业部五强）、新浪 60 日资金流、深市公告含 `disc.static.szse.cn` PDF 直链——全部跑通。
- 全文件 Python 代码块逐块 `py_compile`，零语法错误。

## v3.3.1 — 2026-07-10

元数据与文档变更，**端点与代码零改动**（40 端点 · 10 层 · 13 数据源不变）。

### 触发范围收窄（#29）
- **frontmatter `description` 重写**：明确「仅在需要写代码实际获取 A 股数据时使用」，并显式排除 A 股概念解释 / 投资观点讨论 / 策略问答等无需取数的话题——此前过宽的 description 会让 agent 在任何 A 股相关对话中误加载整个 SKILL.md（约 50K token），误触发才是最大的 token 浪费。

### 单文件形态定调（#21 / #22 / #27 / #29 收口）
- **产品决策**：单文件自包含（拷一个文件就能用、离线可携、便于分发）是本项目的有意选择，长期保持，不做目录化拆分。README FAQ 新增说明与两条降耗建议（收窄触发 + token 敏感用户按需局部读取的用法）。
- 感谢 @Arkzf2 的渐进式披露完整实现（PR #22）与 @iOSleep @taicilang-lcy @ywxkdz 的推动讨论——方案已存档，若未来端点规模翻倍导致单文件不可持续，将重新评估。

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
