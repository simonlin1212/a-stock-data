---
name: a-stock-data
description: 当任务需要写代码实际获取A股及相关市场数据时使用——行情/K线/逐笔(腾讯日周月前后复权+分钟线+当日逐笔、通达信官网全市场盘后包、百度)、研报(东财+新浪+同花顺+iwencai)、信号(热点/北向/龙虎榜/解禁/行业/板块资金流)、资金面(融资融券/大宗/股东户数/分红/资金流/ETF份额)、新闻(财联社/东财/华尔街见闻/新闻联播)、财务三表/F10/估值历史/ST名单、公告(巨潮)、打板(涨停池/连板/炸板率/监控池/异动)、ETF期权、舆情互动(互动易/上证e互动/热榜)、筹码分布、复权因子、申万行业变迁、宏观与利率(社融/PMI/中债收益率曲线/回购定盘利率/LPR/全球宏观日历)、指数成分/权重/估值/交易日历、期货与大宗商品(五家期货交易所日行情/商品与股指期权/持仓排名/期货日K含大商所/实时期货/A50/上海金)、事件驱动(业绩预告/机构调研/增减持/回购/股权质押/新股申购)、可转债等真实数据。十五层·87端点(含5备胎)·34个来源·内嵌全部可运行代码，自包含零外部文件；优先用腾讯/交易所官方等不封IP源，东财接口已内置限流防封，主源被封可查「备用源速查」降级。仅在需要调用数据接口取数时使用：A股概念解释、投资观点讨论、策略问答等无需取数的话题不要加载本skill。
origin: custom
version: 3.10.1
---

> 📦 项目主页：https://github.com/simonlin1212/a-stock-data — 更新、反馈、支持作者
> 
> 作者：Simon 林 · X [@linsizhen](https://x.com/linsizhen) · 邮箱：simonlin0423@gmail.com

# A股全栈数据工具包 V3.10.1

十五层数据架构，87 个能力端点（82 主端点 + 5 备胎）、34 个来源。V3.10 新增的 2 个入口于 2026-09-22 实测，V3.9 新增的 25 个入口于 2026-09-20 实测；旧端点的验证日期见各章节。覆盖主板/创业板/科创板/ST，北交所覆盖依端点而异；已有备胎的数据可按「备用源速查」降级。

> **V3.10.1（成交量单位与对账口径更正 · 逐笔提速与盘后核对，2026-10-07 · #57）：** 入口数、来源数不变，返回的数据不变。
> - §1.2 `tencent_kline()` 的 `volume`：**科创板（688 / 689）是股**，其余是手；此前文档全写成「手」，按此换算科创板会大 100 倍。
>   备用源速查里「成交额 = 量(手) × 100 × 均价」同样更正。
> - §1.2 补成交量对账口径：科创板以外日线是整手、最近一个交易日的分钟量也是整手（下一个交易日才回填成精确股数）；
>   1 分钟线 09:30 那根只有集合竞价、13:01 开盘价是上午收盘价；深市整分时刻的成交腾讯与 Baostock 分在相邻两根；无成交分钟：第一笔成交以前沪深都没有行，之后深市会缺行。
> - §1.4 `tencent_ticks()` 改走复用连接、自动重试的 `V39_RETRY_SESSION`：一次约 70 秒 → 约 25 秒；连接失败、等响应超时、
>   429 / 5xx 自动重试，不再一次抖动就整次失败（读响应体中途卡住不重试）。
>   新增 `frame.attrs["complete"]`，15:31 以后用快照的盘后成交额核对盘后定价各笔（此前末尾缺笔完全看不出；低价 ETF 一两手的小额缺笔仍看不出）。
> - §13.7 `futures_kline()` 同样自动重试，单次超时收短到 (5, 20) 秒；补上中金所主力连续只从 2017-01-17 起。

> **V3.10.0（逐笔替代 / 期货日 K / 行情层重排，2026-09-22）：** 85→87 个能力入口（82 主 + 5 备胎），来源数不变（34）。
> - **§1.4 腾讯逐笔 `tencent_ticks()`**：替代 #52 后返回空的 mootdx `transaction()`。最近一个交易日的全部分笔（沪深个股 + ETF），
>   收盘后与行情快照的当日成交额核对，连续竞价段缺笔直接报错；只有当日、不含北交所。
> - **§13.7 新浪期货日 K `futures_kline()`**：单个合约或主力连续的逐日 K 线，六家交易所含大商所（此前大商所只有实时价）；
>   实测价格与交易所官方逐日一致。
> - **行情层重排**：能用的在前，mootdx 行情命令移到 §1.7 留档。新旧编号对照见 Layer 1 开头；下面历史版本说明里写的仍是旧编号。
> - **期货修正**：上期能源在各类数据首日前抛 `ValueError`（此前报成「格式可能已变」的 `RuntimeError`），期权首日更正为 2021-06-21；
>   上期所日行情实测最早 2002-01-07、中金所 2010-04-16，文档原写 2015 年。

> **V3.9.0（期货大宗 / 事件驱动 / 可转债 / 利率 + 四个 issue，2026-09-20）：** 新增 §13 期货与大宗商品、§14 事件驱动、
> §15 可转债三层，并在原有各层补齐 K 线、研报、ETF 份额、新闻、ST 名单、沪市问答、利率曲线等入口。
> 12→15 层，60→85 个能力入口（80 主 + 5 备胎），22→34 个来源（新增通达信官网盘后包、华尔街见闻、央视网、上证e互动、
> 中债、中国货币网、上期所、上期能源、郑商所、中金所、广期所、上金所）；无新增安装依赖，保留 Python 3.9。
> - **#52 mootdx 行情命令失效**：通达信公开服务器的 K 线 / 盘口 / 逐笔返回 0 行，财务与 F10 正常。`tdx_client(check='finance')`
>   让财务 / F10 按财务命令验活；K 线改走 §1.5 腾讯 / §1.6 通达信盘后包，`tdx_client()` 失败时的报错直接指路。
> - **#49 商品期货 / 期权**：§13 接入五家期货交易所官方日行情与商品 / 股指期权、四家（广期所除外）的会员持仓排名，另有新浪实时期货（含大商所）、
>   A50 期指与上海金交所现货。大商所官网有反爬，日行情未接入。
> - **#53 研报来源**：新增 §2.4 新浪研报列表，作为东财之外的第二来源（只有列表，无评级与目标价）。
> - **#55 聚宽代码**：`norm_ticker()` / `get_prefix()` 认 `.XSHG` / `.XSHE`，新增 `to_joinquant()`；FAQ 说明回测能力边界。
> - 新端点统一返回带 `source` / `source_url` / `fetched_at` 的 DataFrame，「确实没有」与「接口坏了」分开报错。
>   25 个新入口于 2026-09-20 用本文件原文代码实测，见 [本次数据源整合记录](docs/source-integration-v3.9.0.md)。

> **V3.8.0（官方指数与交易基础数据，2026-09-05）：** 新增 §12 指数与交易日历层，
> 中证/国证成分与权重、中证 PE/股息率、深交所整月日历，以及沪深官方两融、北交所行情两个备胎。
> 11→12 层，54→60 个能力入口，19→22 个来源（新增中证、国证、北交所）；无新增安装依赖，保留 Python 3.9。
> 国证当前文件是月末快照；历史调样、集合竞价、需 Key 的同花顺增强 API 暂不算已支持。
> 实测记录、候选取舍和边界见 [本次数据源整合记录](docs/source-integration-v3.8.0.md)。

> **V3.7.2（北交所号段判定对齐，2026-09-02）：**`_natural_market()`（`norm_ticker()` 校验显式前缀是否自相矛盾）与 §8.5 `_anomaly_market()`（异动记录→交易所）此前只枚举 `43/83/87` 三个前两位与 `920`，而 `get_prefix()` 用 `startswith(("4", "8"))` + `startswith("92")` 覆盖整个北交所号段——同一份文件两套规则（#51）。现统一为 `startswith(("4", "8", "92"))`。实测（2026-09-01）北交所在市代码只有 `43x/83x/87x/920x` 四段、`921` 段尚未启用，故**不改变任何现有标的的判定结果**，修的是一致性与前向兼容。
>
> **V3.7.1（后缀路由修复，2026-08-20）：**`get_prefix()` 认显式前缀（`sh000016`）却不认等价的后缀写法（`000016.SH`）——而 `norm_ticker()` 文档明文支持后缀式，且 `em_market_code()`/`em_secid()`（V3.7.0 新增）把**未归一化的原串**直接喂给 `get_prefix()`：`000016.SH` 以 `0` 开头落到默认深市分支，secid 拼成 `0.000016`（深康佳A）而非 `1.000016`（上证50 指数），**静默返回另一只标的的数据**。已在 `get_prefix()` 开头加后缀识别分支（`.sh/.sz/.bj` 与显式前缀等价透传），号段推断与沪指数白名单逻辑不变。⚠️ 走「前缀+原串拼接」的端点（`tencent_quote()`、新浪财报等）仍只认纯 6 位或前缀式——后缀式会把 `.SH` 拼进请求串，**先过 `norm_ticker()` 再传**的总原则不变。
>
> **V3.7.0（宏观层 + 筹码分布 + 复权因子 + 估值历史，2026-08-19）：**新增 **1 个数据层、7 个端点、4 个数据源**（baostock / 申万 / 人民银行 / 国家统计局，全部零注册零 key）。全部端点于 2026-08-19 实跑验证。
>
> - **§4.6 筹码分布 CYQ** — 补上本层名实不符的窟窿：Layer 4 叫「资金面 / **筹码**层」但 §4.1~§4.5 全是资金面数据，一直没有真正的筹码分布。**东财没有公开 CYQ 接口**（实测 `push2`/`push2his` 的 `cyq/get` 均 404），本端点用 OHLC + 换手率**本地推演**，零新增数据源。输出获利比例 / 平均成本 / 90-70 成本区间与集中度 / 筹码峰。⚠️ 初始筹码**播种为首日全部流通盘**——从全零起步会把窗口前的存量持仓一笔勾销（两个 1% 换手日会被算成 50/50，真实应约 99%/1%）。
> - **§6.5 估值历史** — §1.2 腾讯只有**当日**估值快照，本端点给**日频历史序列**（实测茅台 2016-01-04 起 2581 行），并一次补齐此前完全缺失的四项：**换手率**（筹码分布的必需输入）、**停牌状态**、**ST 标记**（实测 000004 有 276 天 isST=1）、历史 PE/PB/PS/PCF。⚠️ **baostock 不支持北交所**，服务端报 `10004011`，本实现在**登录前**就拦掉抛 `ValueError`。
> - **§1.4 复权因子** — §1.1 通达信 `bars()` 是**不复权**数据，跨除权日直接比价必错。新浪 qfq/hfq 因子序列一次 HTTP 约 1.8KB。⚠️ 响应末尾挂着 `/* base64 */` 注释块，**不能用 `$` 锚定正则**，须用 `raw_decode`。
> - **§6.6 上市/退市日** — 唯一能拿到**退市日期**的零鉴权源，配合 §1.2 `is_stale` 可在筛选阶段剔除僵尸标的。
> - **§6.7 申万行业变迁史** — §3.7 东财只有**当前**行业归属，用它做历史研究是**前视偏差**。本端点给每只股票的行业变迁（实测 12,893 行 / 5,905 只 / 38 个一级行业；有标的历史变更过 10 次）。⚠️ 申万官方只发代码不发中文名。
> - **§11.1/§11.2 宏观层（新）** — 人民银行社融（月度 12 列）+ 国家统计局 PMI。⚠️ 社融链路是三级跳，未发布月份**整行丢弃**而非返回 NaN（否则调用方会把 12 行当 12 个月真数据）；PMI 正文是全角括号**内带空格**，空白必须**整个删掉**才匹配得到。

> **V3.6.1（龙虎榜空窗口崩溃修复，2026-08-09 · #45）：**`dragon_tiger_board()` 在回看窗口内无上榜记录时抛 `UnboundLocalError`——而大市值 / 低换手率标的（如贵州茅台）常态无上榜，等于**调用即崩**，调用方还无法区分「无数据」与「接口异常」。已修，空窗口返回语义一致的空结构。
>
> **V3.6.0（静默失败修复 + 重点监控池/日内异动，2026-07-31 · #15）：**
> - **🔴 北交所老号段（43/83/87）会返回僵尸数据且不报错**：实测在市 342 只中 **336 只已迁至 `920xxx`**（锦波生物 `832982`→`920982`、贝特瑞 `835185`→`920185`），老码在东财研报静默返回 **0 篇**、在腾讯行情返回**定格报价**（成交量 0，价差达 17%~100%+）却仍是 HTTP 200。新增全局警告章节；`tencent_quote()` 增加 `is_stale`/`stale_reason` 标志（实测老码 2/2 命中、正常票 4/4 无误报）；`eastmoney_reports()` 遇老码**抛 ValueError 而非返回空**。
> - **🔴 §2.1/§2.2 研报层 ticker 未归一化（静默空）**：`eastmoney_reports("SH600519")` / `"600519.SH"` 一律返回 **0 篇**（reportapi 只认纯 6 位），而文档「Ticker 格式归一化」明文承诺全接口支持带前缀写法——**承诺与实现不符，且失败方式是静默空**，调用方会误读成「该标的无研报覆盖」。新增 `norm_ticker()` 实现（解析失败抛 ValueError，绝不返回空串），`eastmoney_reports()` / `ths_eps_forecast()` 接入。
> - **§8.4 `em_stock_monitor()` 东财重点监控池新增（#15）**：交易所风险警示 / 重点监控名单 + 生效时间窗，零鉴权静态 JSON。
> - **§8.5 `em_price_anomaly()` / `em_price_anomaly_count()` 日内异动池新增（#15）**：交易所「严重异常波动」口径的异动明细与按标的聚合统计，含 12 条异动规则码全解释。⚠️ 必须带 `team=h5` 等固定参数，缺失返回 `unknow team`——已做 `result!=0` 冒泡而非静默返回空。
> - **§2.1 行业研报去硬编码日期**：`begin` 默认由固定的 `2024-01-01` 改为「相对今天往前两年」，避免时间窗越用越旧。
> - 端点 44 → 47。实测 24/24 通过（含前缀格式 4/4、老号段拦截、新端点真数据、异动接口拒绝冒泡）。
>
> **V3.5.0（板块资金流向，2026-07-23 · #37）：**
> - **§3.8 `board_fund_flow()` 板块资金流向新增**：补上此前缺失的**板块级资金流**——行业/概念/地域三类板块 × 今日/5日/10日三周期，主力净流入额/净占比 + 超大/大/中/小单四档明细 + 领涨股。与 §3.7 板块排名**同源同接口**（东财 push2 `clist`），此前只请求了价格/涨跌家数字段，本版补请求 `f62/f184/f66...` 资金流字段即覆盖。走 `em_get` 限流防封。端点 43 → 44。
> - 实测（2026-07-23）：行业今日 100 个板块主力净额降序（电力设备 64.66亿 = 超大 43.55亿 + 大 21.11亿）、概念 5 日、地域 10 日均真实返回；参数校验拒绝非法 board_type/period。
>
> **V3.4.1（前缀路由 + mootdx 验活修复，2026-07-23）：**
> - **§1.2/§市场前缀规则 前缀路由修复（#40 #41）**：`5` 开头沪市 ETF（`510300`/`588200` 等）、沪深指数（`000300`/`000016` 等）此前落到 `else → sz`，腾讯接口返回空**或错票**（`000016` 被误判为 `sz000016` *ST康佳A，静默返回不相干标的的数据，比返空更危险）。`get_prefix()` 与 `tencent_quote()` 两处同步修复：`5x→sh`、沪指数白名单、支持显式前缀（`sh000001`/`sz000001`）透传解决 `000001`（上证指数 vs 平安银行）歧义。
> - **§1.1 `tdx_client()` 真实取数验活（#43）**：`_probe()` 仅做 TCP 握手，握手成功 ≠ 能取数——坏服务器可握手通过却回 2 字节空 body，导致**静默返回空 DataFrame 或连接崩溃**且走不到 fallback。新增 `_validate()`：每个候选 server 必须真实拉一根 K 线成功才采用，并对 `factory()` 连接异常做 try/except 跳过，全部失败才抛明确错误。
> - **备用源速查 K线行新增腾讯 m5 分钟 K 线（#43）**：同花顺 K 线备胎只有 30/60 分，mootdx 一挂就无 5 分钟源。补腾讯 `ifzq.gtimg.cn` 分钟 K（m1/m5/m15/m30/m60，零鉴权不封 IP）。⚠️ 第 7 字段是**换手率基点**不是成交额（差 3 个数量级），成交额需自算。
>
> **V3.4.0（接口质量 + 备用源韧性，2026-07-11）：**
> - **§5.2 财联社快讯复活**：旧 nodeapi 2026-05 下线后，改走官方 `v1/roll/get_roll_list` + 本地签名（`sign=md5(sha1(排序query))`，零 key），V3.2 移除的全市场电报能力恢复，与东财 7×24 互为独立备份。实测 errno=0。
> - **新增「备用源速查 & 降级策略」章节**：十层主源→独立备胎速查表（不同域名/不同风控面）+ 3 个实测备胎函数——`dragon_tiger_backup()`（沪深交易所官方龙虎榜，含营业部席位）、`fund_flow_backup()`（新浪日度资金流）、`announcements_backup()`（深市深交所官方/沪市东财公告+PDF）。端点 40 → 43，数据源 13 → 15（新增沪深交易所官方）。
> - **§3.6 解禁字段修复**：东财 `RPT_LIFT_STAGE` 改列名致 `type`/`shares` 恒空 → 改 `FREE_SHARES_TYPE`/`FREE_SHARES`，并新增 `able_shares`（实际可流通股数，更贴近真实抛压）。
> - **§3.7 行业排名排序修复**：clist 请求补 `fid=f3`，`top`/`bottom` 现按涨跌幅真实排序（此前缺排序字段，切片结果非涨幅序）。
> - **§3.2 深股通标注**：北向盘中披露收紧后 sgt 分钟序列不可靠（hgt 可用），权威北向用 HKEX 官方日统计（见备用源速查）。
> - **体验**：顶部新增「端点路由速查」总表（§→函数→用途→源，可按需局部读取）；FAQ 新增东财被封对策 / 财联社复活 / mootdx 库烂尾说明。
>
> **V3.2.3（行业研报新增）：**
> - **§2.1 东财行业研报 `eastmoney_industry_reports()`**：研报层补上行业研报端点（此前只有个股研报）。与个股研报**同端点** `reportapi.eastmoney.com/report/list`，仅 `qType=1`；`industry_code="*"` 拉全行业、传东财行业码（如 `1238`=IT服务Ⅱ）精确过滤，PDF 复用 `download_pdf()`，走 `em_get` 限流。端点数 27 → 28。
> - 实测（2026-06-20）：全行业 `hits=47928`、按行业码 `1238` 过滤 `hits=1863`，首篇 PDF `H3_{infoCode}_1.pdf` 下载成功（2.5MB，`%PDF` 头）；行业码表端点（`bxpa` 等）404 不存在，用 `"*"` 拉取后从结果反查行业码。

> **V3.2.2（失效接口替换 + 隐藏 Bug 修复）：**
> - **§3.3 概念板块归属（#18）**：百度 PAE `getrelatedblock` 失效（`ResultCode 10003` + 空数组）→ 改用东财 `slist`（`spt=3`）`eastmoney_concept_blocks()`，一次请求拿全个股所属板块（行业/概念/地域 + BK码 + 涨跌幅 + 龙头股），零鉴权走 `em_get` 限流。
> - **§7.1 巨潮公告 orgId（#19）**：硬编码 `gssx0{code}` 致大量 601xxx 股票 `totalAnnouncement=0` → 新增 `_cninfo_orgid()` 动态查官方映射表 `szse_stock.json`（6198 只股，模块级缓存），硬编码降为 fallback。
> - **综合示例修复**：示例仍调用 v3.1 已删的 `baidu_fund_flow_history` → 改 `eastmoney_fund_flow_minute`。
> - **§4.5/§5.1 风控说明**：部分大陆住宅 IP 被东财间歇风控（`HTTP 000`/空）非代码 Bug，加重试/换网络提示。
> - 新代码原样 exec smoke test 实测：板块归属 茅台27/五粮液28/绿的谐波21；公告 平安601318/工行601398 原失效股恢复。
>
> **V3.2.1（Bug 修复）：** 修复两个内嵌函数的解析逻辑（预先存在，非 V3.2 引入）——
> - **§5.1 东财个股新闻**：东财实际返回里 `result.cmsArticleWebOld` 直接就是文章列表，旧写法对 list 调 `.get("list")` 触发 AttributeError / 返回空 → 改为遍历 `cmsArticleWebOld` 列表本身。
> - **§6.4 新浪财报三表**：新浪实际结构是 `result.data.report_list`（按报告期为键的 dict，每期 `data` 才是行项列表），旧写法取 `result.data.{lrb}` 永久返回空 → 改为遍历 `report_list` 期次、从每期 `data` 按 `item_title` 提取。
> - 两函数均用茅台 600519 公开 API（零 key）实测返回非空、字段正确。
>
> **V3.2（防封 + 失效修复）：**
> - **数据源优先级 + 东财防封**：明确「通达信(mootdx)/腾讯不封IP 优先用，东财仅用于其独有数据」原则；新增统一节流入口 `em_get()`，所有东财接口内置串行限流（间隔≥1s+随机抖动）+ 会话复用，AI 抄代码即自带防封。详见「数据源优先级 & 东财防封」章节。
> - **财联社快讯下线（#14）**：`cls.cn` 旧 API 全面 404，标注弃用并改用东财全球资讯。
>
> **V3.1 修复：** 替换 4 个失效接口（百度 PAE 资金流→东财 push2、大宗交易 RPT 报表名更新、机构席位改用 BUY/SELL 明细筛选）+ 修复东财全球资讯 req_trace 参数 + 修复巨潮公告 orgId 格式。
>
> **V3.0 Breaking Change**：彻底移除 akshare 依赖，所有数据源改为直连 HTTP API（仅 mootdx 保留 TCP）。
> ⚠️ V3.7 起 §6.5/§6.6 另需第三方客户端 `baostock`（TCP），因此「零第三方封装依赖」现仅适用于其余端点。

**使用方式：** 将本文件放入 `~/.claude/skills/a-stock-data/SKILL.md`，Claude Code 会自动识别并在 A 股相关对话中激活。

```
行情层（实时，不封IP）
├── 腾讯财经 API   → PE/PB/市值/换手率/涨跌停/指数/ETF (HTTP)
├── 腾讯 K 线      → 沪深日/周/月前后复权 + 1~60 分钟，三入口轮换 (V3.9 新增)
├── 通达信盘后包   → 某交易日沪深北全市场日线含成交额 (tdx.com.cn HTTP，V3.9 新增)
├── 腾讯逐笔       → 最近一个交易日的分笔成交明细，沪深个股 + ETF (HTTP，V3.10 新增)
├── 百度股市通     → K线带MA5/10/20 (V3.0 新增，HTTP)
├── 新浪复权因子   → qfq/hfq 因子序列 + 套用到不复权K线 (V3.7 新增)
└── mootdx        → K线 + 五档盘口 + 逐笔成交 (TCP 7709；⚠️ 2026-09 起行情命令返回空，#52，留档)

研报层
├── 东财 reportapi → 个股研报 + 行业研报 + PDF下载 + 评级 + 三年EPS
├── 同花顺 THS     → 一致预期EPS (直连 basic.10jqka.com.cn)
├── iwencai        → NL语义搜索研报 (唯一能力，需X-Claw)
└── 新浪研报列表   → 标题/机构/研究员/日期，研报第二来源 (V3.9 新增)

信号层
├── 同花顺热点     → 当日强势股 + 题材归因 reason tags (零鉴权 73ms)
├── 同花顺北向     → hgt/sgt 分钟资金流向 + 本地自缓存历史
├── 东财 slist     → 个股所属板块/概念归属 (V3.2.2 替换百度PAE)
├── 东财 push2     → 个股资金流向 分钟级 (V3.1 替换百度PAE)
├── 龙虎榜席位     → 上榜记录 + 买卖席位 TOP5 + 机构动向 (datacenter-web)
├── 全市场龙虎榜   → 每日全市场上榜股票 + 净买额排名 (datacenter-web)
├── 限售解禁日历   → 历史解禁 + 未来90天待解禁 (datacenter-web)
├── 行业板块排名   → 东财行业涨跌/上涨下跌家数 (V3.0 替换同花顺)
└── 板块资金流向   → 行业/概念/地域 × 今日/5日/10日 主力+超大/大/中/小四档 (push2, V3.5)

资金面 / 筹码层
├── 融资融券明细   → 日级融资余额/买入/偿还 + 融券 (datacenter-web)
├── 大宗交易       → 成交价/量 + 买卖方营业部 (datacenter-web)
├── 股东户数变化   → 季度股东户数 + 环比变化 (datacenter-web)
├── 分红送转       → 历史每股派息/送股/转增 (datacenter-web)
├── 个股资金流120日 → 主力/大单/中单/小单 日级净流入 (push2his)
├── 筹码分布 CYQ   → 获利比例/平均成本/90-70成本区间/筹码峰 (本地计算，V3.7 新增)
└── ETF 份额       → 上交所按日归档 / 深交所当前快照，万份 (V3.9 新增)

新闻层
├── 东财个股新闻   → 个股相关新闻 (search-api-web JSONP)
├── 财联社快讯     → 全市场实时电报 (v1 API+本地签名零key，✅V3.4 复活)
├── 东财全球资讯   → 7×24 财经快讯 (np-weblist，与财联社互备)
├── 华尔街见闻     → 7×24 快讯，按频道 + 翻页游标 (V3.9 新增)
└── 新闻联播       → 当日条目标题 + 文字稿 (央视网，V3.9 新增)

基础数据层
├── mootdx finance → 季报快照 (37字段, EPS/ROE/净利)
├── mootdx F10     → 最新提示 (公告/报道/大宗/两融/风险提示摘要；2026-09 起只剩这一类)
├── 东财个股信息   → 行业/总股本/流通股/市值/上市日期 (push2)
├── 新浪财报三表   → 资产负债表/利润表/现金流量表 (quotes.sina.cn)
├── baostock 估值历史 → 日频 PE/PB/PS/PCF + 换手率 + 停牌 + ST (不支持北交所，V3.7 新增)
├── baostock 标的信息 → 上市日/退市日/状态 (V3.7 新增)
├── 申万行业分类   → 行业归属变迁史，消除前视偏差 (仅代码无中文名，V3.7 新增)
└── ST 名单        → 沪深京 ST / *ST 当日快照 (东财，baostock 兜底，V3.9 新增)

公告层
├── 巨潮 cninfo    → 公告全文检索+下载 (cninfo.com.cn)
└── mootdx F10     → 最新公告摘要

打板层 (V3.3 新增)
├── 东财涨停池     → 连板数/几天几板/封板资金/炸板次数/行业 (push2ex)
├── 东财炸板池     → 涨停后开板 + 振幅/涨速 (push2ex)
├── 东财跌停池     → 封单资金/连续跌停/开板次数 (push2ex)
├── 东财昨涨停池   → 昨涨停今表现，算晋级率/赚钱效应 (push2ex)
└── 同花顺涨停揭秘 → 涨停原因题材/封板成功率/板型 (10jqka)

ETF期权层 (V3.3 新增)
├── 合约清单       → 50ETF/300ETF/科创50/500ETF 各月认购认沽 (新浪)
├── T型报价        → 买卖五档/持仓量/行权价/最新价 (新浪)
└── 希腊字母+IV    → Delta/Gamma/Theta/Vega/隐含波动率 (新浪)

舆情互动层 (V3.3 新增)
├── 互动易问答     → 投资者提问+公司回复 (巨潮，深市)
├── 上证e互动      → 沪市投资者提问+公司回复 (上交所运营的独立平台，V3.9 新增)
├── 同花顺热榜     → 人气值/概念标签/排名变化 (10jqka)
├── 东财人气榜     → 排名+排名变化+名称价格 (emappdata)
└── 东财概念命中   → 个股被归到哪些概念在炒+热度 (emappdata)

宏观与利率层 (V3.7 新增，V3.9 扩展)
├── 人民银行社融   → 社会融资规模增量 月度12列 (pbc.gov.cn，三级跳取 xls 附件)
├── 国家统计局PMI  → 制造业/非制造业/综合 + 大中小型企业分档 (stats.gov.cn)
├── 中债收益率曲线 → 国债 / 商业银行 AAA / 中短票 AAA，3月~30年 (V3.9 新增)
├── 回购定盘利率   → FR001/007/014 + FDR (中国货币网，V3.9 新增)
├── LPR            → 1 年 / 5 年全历史 (东财，V3.9 新增)
└── 全球宏观日历   → 公布值/预期/前值 + 重要事件 (华尔街见闻，V3.9 新增)

指数与交易日历层 (V3.8 新增)
├── 中证指数       → 当前成分 / 月末权重 / 近期 PE 与股息率
├── 国证指数       → 最近公布的成分与权重（月末快照）
└── 深交所日历     → 官方整月交易标志（完整性校验）

期货与大宗商品层 (V3.9 新增，#49)
├── 期货日行情     → 上期所/上期能源/郑商所/中金所/广期所 官方收盘数据
├── 期权日行情     → 商品期权 + 股指期权，Delta / 隐含波动率（中金所不公布这两项）
├── 持仓排名       → 会员成交量 / 持买 / 持卖前 20 名
├── 实时期货       → 新浪实时价（含大商所品种）
├── 期货日 K       → 新浪单合约 / 主力连续逐日 K 线（含大商所，V3.10 新增）
├── A50 期指       → 富时中国 A50 连续合约报价
└── 上海金现货     → 上金所 Au99.99 / Au(T+D) / Ag(T+D) 日线

事件驱动层 (V3.9 新增)
├── 业绩预告 · 机构调研 · 股东增减持 · 股票回购
└── 股权质押（中国结算周度） · 新股申购日历   (均为东财 datacenter)

可转债层 (V3.9 新增)
└── 可转债全表     → 条款 + 转股价 / 债价 / 转股价值 / 溢价率 (东财)

官方备胎扩展 (V3.8 新增)
├── 上交所/深交所  → 两融明细（分交易所调用，金额元、余量股/份）
└── 北交所         → 当前行情与五档快照（必须核对交易日）
```

## 端点路由速查（按需定位，不必通读全文）

只需一类数据时，按下表定位章节（§）局部读取。除 iwencai 需 API Key 外全部零 key。

| § | 函数 | 拿什么 | 源 |
|---|------|--------|----|
| 前置 | `norm_ticker(code)` | 任意写法→纯6位（`SH600519`/`600519.SH`/`600519.XSHG` 皆可；解析失败抛错不返空） | 本地 |
| 前置 | `to_joinquant(code)` | 转聚宽代码 `600519.XSHG` / `000001.XSHE`（北交所不转换） | 本地 |
| 1.1 | `tencent_quote(codes)` | 实时价/PE/PB/市值/换手/涨跌停/指数/ETF（带 `is_stale` 僵尸报价标志） | 腾讯 |
| 1.2 | `tencent_kline(code, period, adjust, start, end, count)` | 日/周/月前后复权 + 1~60 分钟 K 线（沪深，不含北交所） | 腾讯 |
| 1.3 | `tdx_daily_package(date)` | 某交易日沪深北全部证券日线（含成交额） | 通达信官网 |
| 1.4 | `tencent_ticks(code)` | 最近一个交易日的分笔成交（价/手/元/主动买卖；沪深个股+ETF，不含北交所） | 腾讯 |
| 1.5 | `baidu_kline_with_ma(code)` | 日K线带 MA5/10/20 | 百度 |
| 1.6 | `sina_adjust_factor(code, kind)` / `apply_adjust(bars, factors)` | 复权因子 qfq/hfq + 套用到不复权K线 | 新浪 |
| 1.7 | `tdx_client()` → `.bars()` / `.quotes()` / `.transaction()` | K线(多周期,不复权) / 五档盘口 / 逐笔成交（⚠️ 2026-09 起返回空，#52，留档） | 通达信 |
| 2.1 | `eastmoney_reports(code)` / `download_pdf(rec)` | 个股研报+评级+三年EPS / 研报PDF | 东财 |
| 2.1 | `eastmoney_industry_reports(industry_code)` | 行业研报 | 东财 |
| 2.2 | `ths_eps_forecast(code)` | 机构一致预期 EPS | 同花顺 |
| 2.3 | `iwencai_search(query)` / `iwencai_query(query)` | NL 语义搜研报/选股（需 Key） | iwencai |
| 2.4 | `sina_research_reports(code=None, page=1)` | 研报列表：标题/类型/机构/研究员（无评级） | 新浪 |
| 3.1 | `ths_hot_reason()` | 当日强势股+题材归因 | 同花顺 |
| 3.2 | `hsgt_realtime()` | 北向分钟流向（hgt 可用 / sgt 仅参考） | 同花顺 |
| 3.3 | `eastmoney_concept_blocks(code)` | 个股所属板块/概念归属 | 东财 |
| 3.4 | `eastmoney_fund_flow_minute(code)` | 个股资金流（分钟级） | 东财 |
| 3.5 | `dragon_tiger_board(code, date)` | 个股龙虎榜+买卖席位 TOP5 | 东财 |
| 3.6 | `lockup_expiry(code, date)` | 解禁历史+未来90天待解禁 | 东财 |
| 3.7 | `industry_comparison()` | 行业板块涨跌排名 | 东财 |
| 3.8 | `board_fund_flow(board_type, period)` | 板块资金流向（行业/概念/地域 × 今日/5日/10日，主力+四档） | 东财 |
| 3.9 | `daily_dragon_tiger(date)` | 全市场龙虎榜+净买额排名 | 东财 |
| 4.1 | `margin_trading(code)` | 融资融券明细 | 东财 |
| 4.2 | `block_trade(code)` | 大宗交易+营业部 | 东财 |
| 4.3 | `holder_num_change(code)` | 股东户数变化 | 东财 |
| 4.4 | `dividend_history(code)` | 分红送转历史 | 东财 |
| 4.5 | `stock_fund_flow_120d(code)` | 个股资金流（120日，日级） | 东财 |
| 4.6 | `chip_distribution(df)` | 筹码分布（获利比例/平均成本/90-70成本区间/筹码峰） | 本地计算 |
| 4.7 | `etf_shares(date, exchange)` | ETF 份额（万份）：上交所历史日期 / 深交所当前快照 | 上交所/深交所 |
| 5.1 | `eastmoney_stock_news(code)` | 个股新闻 | 东财 |
| 5.2 | `cls_telegraph()` | 财联社电报（7×24，本地签名零key） | 财联社 |
| 5.3 | `eastmoney_global_news()` | 全球资讯（7×24） | 东财 |
| 5.4 | `wallstreetcn_lives(channel, limit, cursor)` | 7×24 快讯（按频道，可翻页） | 华尔街见闻 |
| 5.5 | `cctv_news(date, with_content=True)` | 新闻联播条目 + 文字稿（政策信号研究用） | 央视网 |
| 6.1 | `tdx_client(check='finance').finance(symbol)` | 季报快照 37 字段 | 通达信 |
| 6.2 | `tdx_client(check='finance').F10(symbol, name)` | F10 文本（2026-09 起服务端只剩「最新提示」一类） | 通达信 |
| 6.3 | `eastmoney_stock_info(code)` | 行业/股本/市值/上市日期 | 东财 |
| 6.4 | `sina_financial_report(code, type)` | 财报三表 | 新浪 |
| 6.5 | `baostock_valuation_history(code, s, e)` | 估值历史 PE/PB/PS/PCF + 换手率 + 停牌 + ST（**不支持北交所**） | baostock |
| 6.6 | `baostock_stock_basic(code)` | 上市日 / **退市日** / 状态 | baostock |
| 6.7 | `sw_industry_history()` / `sw_industry_as_of(df, code, d)` | 申万行业**变迁史**（消除前视偏差，仅代码无中文名） | 申万 |
| 6.8 | `st_stock_list()` | 沪深京 ST / *ST 当日名单 | 东财（baostock 兜底） |
| 7.1 | `cninfo_announcements(code)` | 公告检索+PDF 下载 | 巨潮 |
| 7.2 | `tdx_client(check='finance').F10(symbol, name='最新提示')` | 最新公告摘要 | 通达信 |
| 8.1 | `em_zt_pool` / `em_zb_pool` / `em_dt_pool` / `em_yzt_pool` | 涨停/炸板/跌停/昨涨停四池 | 东财 |
| 8.2 | `ths_limit_up_pool(date)` | 涨停原因题材+封板成功率+板型 | 同花顺 |
| 8.3 | `limit_up_sentiment(date)` | 炸板率/连板高度/连板梯队 | 东财(四池组合) |
| 8.4 | `em_stock_monitor()` | 重点监控池（风险警示名单+生效时间窗） | 东财 |
| 8.5 | `em_price_anomaly()` / `em_price_anomaly_count()` | 日内异动明细 / 按标的聚合异动统计（严重异常波动） | 东财 |
| 9.1 | `sina_option_codes` / `sina_option_tquote` / `sina_option_greeks` | ETF期权合约清单 / T型报价 / 希腊字母+IV | 新浪 |
| 10.1 | `cninfo_irm(code)` | 互动易问答（提问+公司回复，深市） | 巨潮 |
| 10.2 | `ths_hot_list()` / `em_hot_rank()` / `em_hot_concept(code)` | 热榜/人气榜/概念命中 | 同花顺+东财 |
| 10.3 | `sse_e_interaction(code=None, kind='answered')` | 上证e互动问答（沪市） | 上证e互动（上交所运营） |
| 11.1 | `pboc_social_financing(year)` | 社会融资规模增量（月度12列） | 人民银行 |
| 11.2 | `nbs_pmi()` | 制造业/非制造业/综合 PMI + 大中小型企业 | 国家统计局 |
| 11.3 | `chinabond_yield_curve(start, end, curve)` | 国债 / 银行 AAA / 中短票 AAA 收益率曲线 3月~30年 | 中债 |
| 11.4 | `repo_fixing_rates(kind)` | 回购定盘利率 FR / FDR 001·007·014 | 中国货币网 |
| 11.5 | `lpr_history()` | LPR 1 年 / 5 年全历史 | 东财 |
| 11.6 | `macro_calendar(start, end, country, min_importance)` | 全球宏观日历（公布值/预期/前值） | 华尔街见闻 |
| 12.1 | `index_constituents(index_code, provider)` | 最近公布的沪深北指数成分；csi/cni 显式选源 | 中证/国证 |
| 12.2 | `index_weights(index_code, provider)` | 最近公布的指数权重（百分数），保留真实日期 | 中证/国证 |
| 12.3 | `index_valuation(index_code)` | 两种口径 PE、股息率；不含 PB | 中证 |
| 12.4 | `trading_calendar(year, month)` | 官方整月交易日历 | 深交所 |
| 13.1 | `futures_daily(date, exchange)` | 期货日行情（SHFE/INE/CZCE/CFFEX/GFEX） | 五家期货交易所 |
| 13.2 | `options_daily(date, exchange)` | 商品期权 / 股指期权日行情 + Delta / IV（中金所不公布这两项） | 五家期货交易所 |
| 13.3 | `futures_position_rank(date, exchange, symbol)` | 会员成交 / 持买 / 持卖前 20 名 | 上期所/能源/郑商所/中金所 |
| 13.4 | `futures_realtime(symbols)` | 实时期货（含大商所品种） | 新浪 |
| 13.5 | `a50_futures()` | 富时中国 A50 期指 | 新浪 |
| 13.6 | `sge_spot(instrument)` | 上海金交所现货日线（黄金/白银/铂金） | 上金所 |
| 13.7 | `futures_kline(symbol, start, end)` | 期货日 K：单个合约 / 主力连续的逐日序列（含大商所） | 新浪 |
| 14.1 | `earnings_forecast(code, report_date, limit)` | 业绩预告 | 东财 |
| 14.2 | `institution_survey(code, start, end, detail, limit)` | 机构调研（汇总 / 逐机构） | 东财 |
| 14.3 | `holder_trades(code, direction, start, end, limit)` | 股东增减持 | 东财 |
| 14.4 | `share_buyback(code, progress, limit)` | 股票回购方案与进度 | 东财 |
| 14.5 | `equity_pledge(code, date, limit)` | 股权质押比例（中国结算周度，仅沪深） | 东财 |
| 14.6 | `ipo_calendar(limit)` | 新股申购日历 | 东财 |
| 15.1 | `convertible_bonds(include_delisted=False)` | 可转债条款 + 转股价值 / 溢价率 | 东财 |
| 官方备胎扩展 | `margin_trading_backup(date, exchange, code=None)` | 单所两融明细（先执行 §12 helper） | 上交所/深交所 |
| 官方备胎扩展 | `bse_quote_backup(date, code=None)` | 北交所全板/单票当前快照（先执行 §12 helper） | 北交所 |
| 备用源速查 | `dragon_tiger_backup` / `fund_flow_backup` / `announcements_backup` | 龙虎榜/资金流/公告官方备胎（主源被封时降级） | 交易所官方+新浪+东财(沪市公告) |
| 估值公式 | `forward_pe` / `pe_digestion` / `calc_peg` / `full_valuation(code)` | 前向PE / PE消化时间 / PEG / 单票估值全景 | 本地计算 |

## 数据源优先级 & 东财防封（重要，先读）

### 优先级原则：能用腾讯 / 交易所官方，就别用东财

| 优先级 | 数据源 | 协议 | 封 IP 风险 | 覆盖 |
|--------|--------|------|-----------|------|
| **1（首选）** | **腾讯财经** | HTTP | **不封 IP**（K 线单入口约 600 次后限流，§1.2 三入口轮换） | 实时价、PE/PB/市值/换手率/涨跌停、指数、ETF、日周月/分钟 K 线、当日逐笔 |
| **2** | **交易所 / 官方机构** | HTTP | 极低（避免高频） | 通达信盘后包、沪深北交易所、五家期货交易所、上金所、中债、货币网、中证/国证 |
| **3** | 新浪 / 巨潮 / 同花顺 / 华尔街见闻 | HTTP | 低 | 财报三表、复权因子、公告、一致预期/热点、研报列表、快讯 |
| **4** | **mootdx（通达信）** | TCP 7709 二进制 | 不封 IP | 财务快照、F10 正常；**K 线 / 盘口 / 逐笔 2026-09 起返回空（#52）** |
| **5（仅独有数据才用）** | **东财 eastmoney** | HTTP | **有风控，会封 IP** | 见下 |

**凡是行情 / K线 / 实时价 / 市值 / 财务三表能从腾讯、交易所官方或新浪拿到的，一律走它们**——实测不封 IP，可放心使用（仍应控制频率）。

### 东财只用于它「独有、别处拿不到」的数据

下列能力默认走东财（须限流）；已有交易所备胎的龙虎榜、两融可按文末速查表切换，不应视为东财独占：

> 龙虎榜席位 · 全市场龙虎榜 · 限售解禁日历 · 融资融券 · 大宗交易 · 股东户数 · 分红送转 · 个股资金流向（分钟/日级）· 行业板块排名 · 研报列表/PDF · 个股新闻 · 全球资讯 · ST 名单 · LPR · 事件驱动（业绩预告/机构调研/增减持/回购/质押/新股）· 可转债

### 东财风控阈值（社区实测，2026-05）

| 行为 | 触发封禁的阈值 | 风险 |
|------|---------------|------|
| 每秒请求数 | > 5 次/秒 | 高 |
| 单 IP 并发连接 | ≥ 10 | 高 |
| 1 分钟请求总数 | ≥ 200 次 | 中高 |
| 5 分钟请求总数 | ≥ 300 次 | 触发封禁 |
| User-Agent | 空 UA / 无浏览器特征 | 中 |

被封表现：连续请求后 `403` / `429` / 连接超时 / 返回空数据。临时封禁通常几分钟到几小时。

### ⚠️ 实测封禁案例（2026-06-30，一手数据，感谢 [@luodada99](https://github.com/luodada99) issue #36）

上表是社区口径；下面这条是**真实踩到 IP 级封禁**的完整记录，比阈值表更有参考价值：

- **触发方式**：选股脚本 10 线程并发、**完全不走 `em_get()` 限流**，1 小时内发出 45000+ 请求（三个版本的脚本同时跑全市场 5208 只）
- **后果**：`push2` / `push2his` **全系列** `RemoteDisconnected`，**IP 级封禁持续 20+ 小时**——不是"几分钟到几小时"那种临时限速
- **关键观察一**：`datacenter-web.eastmoney.com` **不受影响**——东财不同子域走不同 WAF，`push2` 被封不代表整个东财都不能用
- **关键观察二**：**腾讯 K 线（`web.ifzq.gtimg.cn`）连续 5000+ 次后会返回空**，但这是**限流不是封 IP**，降速或换新浪即可恢复
- **降级实测**：东财被封时，第一只股票花 10.9s 完成"检测被封 + 降级"，之后每只 0.4s 走腾讯，数据准确

**这个案例正是「限流是铁律」的实证**：`em_get()` 的默认间隔（1s + 抖动、串行）下，1 小时最多约 3000 次请求，与踩坑者的 45000 次差一个数量级。

**被封后的降级路径**（各层备胎详见「备用源速查」章节）：

| 被封端点 | 替代方案 | 差异 |
|---|---|---|
| `push2/clist/get`（股票列表） | `datacenter-web` + 腾讯行情批量 | 行业字段来自 datacenter 的 `BOARD_NAME` |
| `push2his/kline/get`（K线） | 腾讯 `fqkline/get`（前复权）→ 新浪 `getKLineData`（不复权） | 腾讯有前复权，新浪没有；量的单位新浪是股，腾讯科创板是股、其余是手（见 §1.2） |
| `push2/stock/get`（个股） | 腾讯 `qt.gtimg.cn` | 腾讯无行业/概念字段 |

### 防封铁律（调用东财时必须遵守）

1. **串行，不并发**——绝不对东财开多线程/协程并发请求
2. **每次间隔 ≥ 1 秒 + 随机抖动**（QPS ≤ 2），批量筛选时调大到 1.5~2 秒
3. **复用 HTTP 会话**（Keep-Alive），不要每次新建连接
4. **带正常 UA + Referer**（本 SKILL 各端点已配好）
5. **批量场景每只股票之间 sleep**——AI 跑批量循环（如筛选 100 只股逐个拉龙虎榜/资金流）是被封的头号元凶

### 已内置限流：所有东财请求走 `em_get()`

本 SKILL 提供统一的节流入口 `em_get()`（定义见下方「东财数据中心统一查询（共用 helper）」），它自动做到：串行限流（最小间隔 `EM_MIN_INTERVAL=1.0s` + 随机抖动）+ 复用 `EM_SESSION`（Keep-Alive）+ 默认 UA。**所有 `eastmoney.com` 端点的代码块都已改用 `em_get` 而非裸 `requests.get`**，AI 直接抄代码即自带防封。批量任务把 `EM_MIN_INTERVAL` 调大即可进一步降速。

> 注：`em_get` / `EM_SESSION` / `EM_MIN_INTERVAL` 是所有东财代码块共用的前置定义，使用任一东财端点前需先执行「共用 helper」代码块。

---

## When to Activate

- 用户需要**指数成分、指数权重、指数 PE / 股息率、官方交易日历、沪深官方两融或北交所行情备份**（V3.8）。
- 用户要看**商品期货 / 期权 / 持仓排名 / A50 / 黄金现货**，或**业绩预告 / 机构调研 / 增减持 / 回购 / 股权质押 / 新股申购 / 可转债**，
  或**国债收益率曲线 / 回购利率 / LPR / 全球宏观日历**、**ETF 份额**、**ST 名单**、**新闻联播**、**沪市互动问答**、**全市场当日日线**（V3.9）。
- 用户要把代码转成**聚宽格式**（`600519.XSHG`）或问**能否回测**（V3.9，见 FAQ）。

- 用户要查 A 股个股估值（一致预期 / PE / PEG / PE消化）
- 用户要拉实时行情（价格 / 五档盘口 / K线 / 涨跌停价）
- 用户要搜研报（按主题 / 按标的 / 按行业 / 下载PDF）
- 用户要看**当日强势股 / 题材归因 / 概念热点**
- 用户要看**北向资金动向**（沪股通/深股通分钟流向）
- 用户要看**概念板块归属**（行业/概念/地域）
- 用户要看**个股资金流向**（主力/散户/超大单/大单分钟级）
- 用户要看**龙虎榜席位**（营业部 + 机构买卖）
- 用户要看**全市场龙虎榜**（当日所有上榜股票 + 净买额排名）
- 用户要看**限售解禁日历**（历史解禁 + 未来待解禁）
- 用户要做**行业横向对比**（涨跌排名 / 资金流入 / 领涨股）
- 用户要看**融资融券 / 两融数据**（融资余额 + 融券余额）
- 用户要看**大宗交易**（成交价/量 + 买卖方营业部）
- 用户要看**股东户数变化**（筹码集中度）
- 用户要看**分红送转历史**（每股派息 + 送股 + 转增）
- 用户要看**指数/ETF行情**（上证指数 / 沪深300 / 创业板指 / ETF）
- 用户要看**涨停 / 打板情绪**（涨停池 / 连板梯队 / 炸板率 / 跌停 / 涨停原因题材）
- 用户要看**ETF 期权**（T型报价 / 希腊字母 Delta·Gamma·Theta·Vega / 隐含波动率 IV）
- 用户要看**投资者互动问答**（公司如何回应某传闻/利好 · 互动易）
- 用户要看**市场热度 / 人气榜**（同花顺热榜 / 东财人气榜 / 个股概念命中）
- 用户要看新闻资讯（个股新闻 / 财联社快讯 / 全球资讯）
- 用户要查公告（巨潮公告全文）
- 用户要做产业链调研 / 批量横向对比
- 关键词：估值、一致预期、机构预测、市盈率、PEG、市值、研报、产业链、行业研究、K线、盘口、公告、新闻、**强势股、题材、热点、概念归因、北向资金、沪股通、深股通、概念板块、资金流向、主力、龙虎榜、席位、营业部、全市场龙虎榜、净买入、解禁、限售、行业对比、行业轮动、融资融券、两融、大宗交易、股东户数、筹码集中、分红、派息、送股、指数、ETF、涨停、打板、连板、炸板、跌停、涨停原因、封板、晋级率、ETF期权、希腊字母、隐含波动率、互动易、投资者关系、热榜、人气榜、市场热度、期货、商品期权、股指期权、持仓排名、A50、黄金、上海金、业绩预告、机构调研、增减持、回购、股权质押、新股申购、打新、可转债、转股溢价率、国债收益率、收益率曲线、回购利率、FR007、LPR、宏观日历、ETF份额、ST、新闻联播、上证e互动、聚宽、回测**

---

## Prerequisites

```bash
pip install mootdx requests pandas stockstats numpy baostock xlrd openpyxl
```

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| mootdx | >= 0.10 | TCP 财务快照+F10（非 HTTP 依赖之一；K 线/盘口/逐笔 2026-09 起返回空，#52）；0.11.x 用 `tdx_client()` 规避 BESTIP bug，见下节 |
| requests | any | 所有HTTP API直连 |
| pandas | any | 数据处理+HTML表格解析 |
| stockstats | any | 技术指标计算（RSI/MACD/BOLL等） |
| numpy | any | §4.6 筹码分布的网格计算 |
| baostock | >= 0.8 | §6.5/§6.6 估值历史·换手率·停牌·ST·退市日，§6.8 ST 名单兜底（TCP，免注册免 key；**不支持北交所**） |
| xlrd | >= 2.0 | 读 `.xls`（§6.7 申万行业分类、§12 中证） |
| openpyxl | any | 读 `.xlsx`（§11.1 社融、§12 国证、深交所两融） |

> **架构：** 除 mootdx 与 baostock（均为 TCP 客户端库）外，所有数据源均为直连 HTTP API，不经第三方数据封装。每个 HTTP 端点的底层 URL/参数完全暴露，方便调试和定制。

### iwencai API Key（仅语义搜索需要）

```bash
# 环境变量方式
export IWENCAI_API_KEY="your_key_here"
export IWENCAI_BASE_URL="https://openapi.iwencai.com"

# 申请地址: https://www.iwencai.com/skillhub
# 注册后安装 SkillHub CLI，再安装 report-search 技能即可获得 Key
```

其他数据源（腾讯 / 东财 / 同花顺 / 百度股市通 / 新浪 / 巨潮 / 财联社 / mootdx / baostock / 申万 / 人民银行 / 国家统计局 / 沪深北交易所 / 中证 / 国证 / 通达信官网 / 华尔街见闻 / 央视网 / 中债 / 中国货币网 / 五家期货交易所 / 上金所）全部免费，无需 key。

### mootdx 客户端（必读，规避 0.11.x BESTIP 空串 bug）

> **已知 bug（mootdx 0.11.x）：** 全新安装后 `Quotes.factory(market='std')` 裸调用可能抛 `ValueError: not enough values to unpack (expected 2, got 0)`。
> 根因：`~/.mootdx/config.json` 的 `BESTIP.HQ` 初始是空字符串 `""`（不是缺失键），mootdx 用 `dict.get(key, default)` 取不到 default，拆包失败。**老用户（config 曾填充过 IP）不会触发，所以容易漏测。**
> **不要靠锁版本解决：** 锁 `mootdx==0.10.12` 在部分环境（如干净的 Python 3.9）下 `import mootdx` 会因 numpy/pandas 二进制不兼容直接崩。正确做法是用下面的 `tdx_client()`——显式传 server 绕过 BESTIP，对 0.10 / 0.11 都适用。

**统一用以下 helper 创建客户端（所有 mootdx 调用都走它）：**

```python
import socket
from mootdx.quotes import Quotes

# 实测可用的备选服务器（按延迟排序，2026-06 验证）
_TDX_SERVERS = [
    ('119.97.185.59', 7709), ('124.70.133.119', 7709), ('116.205.183.150', 7709),
    ('123.60.73.44', 7709),  ('116.205.163.254', 7709), ('121.36.225.169', 7709),
    ('123.60.70.228', 7709), ('124.71.9.153', 7709),    ('110.41.147.114', 7709),
    ('124.71.187.122', 7709),
]

def _probe(ip, port, timeout=2.0):
    """TCP 握手探测（快速粗筛）。注意：握手成功 ≠ 能取数，必须再经 _validate 验活。"""
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False

def _validate(client, market: str = 'std', check: str = 'bars') -> bool:
    """真实取数验活：坏服务器可 TCP 握手通过却回 2 字节空 body → 静默空表。用一次真实请求兜底。

    check='bars'   ：用 K 线请求验活（§1.7 行情类调用）；
    check='finance'：财务快照、F10 类别表里的「最新提示」及其正文都要取到才算活（§6.1 财务 / §6.2、§7.2 F10 调用），
                     只验财务会选中「财务正常、F10 为空」的服务器，F10 随后静默给空文本；
                     只看类别表非空，又会放过只回别的类别或畸形对象的服务器。
    两者要分开：2026-09 起通达信公开服务器的行情类命令（bars / quotes / transaction）普遍返回空表，
    而 finance / F10「最新提示」/ 除权除息仍正常（#52）。财务类调用若仍用 K 线验活，会被误判成「全部不可达」。
    验活样本 '000001' 是 A 股代码，只对 market='std' 有意义。其它市场（如扩展行情 'ext'）
    用它必然取不到数，会把所有正常服务器都判死、误报「全部不可达」，故非 std 时跳过验活。
    """
    if market != 'std':
        return True
    try:
        if check == 'finance':
            cats = client.F10C(symbol='000001')
            if not any(isinstance(c, dict) and c.get('name') == '最新提示' for c in cats):
                return False
            text = client.F10(symbol='000001', name='最新提示')
            if not isinstance(text, str) or not text.strip():
                return False
            df = client.finance(symbol='000001')
        else:
            df = client.bars(symbol='000001', frequency=9, offset=1)
        return df is not None and not df.empty
    except Exception:
        return False

def tdx_client(market='std', check='bars'):
    """
    创建 mootdx 客户端，规避 0.11.x BESTIP.HQ 空串 bug + 坏服务器静默空表（#43）。
    check: 'bars'（默认，K 线 / 盘口 / 逐笔）或 'finance'（财务快照 / F10），决定用哪类请求验活（#52）。
    每个候选都必须「真实取数验活」通过才采用（_probe TCP 握手是假阳性来源）：
      1) 顺序探测 _TDX_SERVERS，对 probe 通过者再 _validate 真实取数，取第一个验活成功的；
      2) 全部失败 → 回退 mootdx 自带 bestip 测速选优（同样验活）；
      3) 再回退裸 factory（老用户 config 已有可用 BESTIP 时成立）；
      4) 仍失败 → 抛 RuntimeError，明确报错而非静默返回空表 / 崩溃。
    """
    if check not in ('bars', 'finance'):
        raise ValueError("check 只能是 'bars' 或 'finance'")
    for ip, port in _TDX_SERVERS:
        if not _probe(ip, port):
            continue
        try:
            c = Quotes.factory(market=market, server=(ip, port))
            if _validate(c, market, check):
                return c
        except Exception:
            continue                                        # 握手过但取数崩 → 跳过下一台
    for kwargs in ({'bestip': True}, {}):                   # fallback: bestip 测速 / 裸 factory
        try:
            c = Quotes.factory(market=market, **kwargs)
            if _validate(c, market, check):
                return c
        except Exception:
            continue
    hint = ("海外网络通常全部超时（TCP 7709），请走国内代理或更新 _TDX_SERVERS 列表。")
    if check == 'bars':
        hint += ("若国内网络也如此：2026-09 起通达信公开服务器的 K 线 / 盘口 / 逐笔命令普遍返回空（#52），"
                 "K 线改用 §1.2 tencent_kline()（日周月 + 1~60 分钟）或 §1.3 tdx_daily_package()"
                 "（全市场当日日线含成交额），逐笔改用 §1.4 tencent_ticks()（当日）；"
                 "财务与 F10 用 tdx_client(check='finance') 仍可取。")
    raise RuntimeError("所有 mootdx 服务器均无法取到数据（TCP 可达但返回空 / 被 reset）。" + hint)

# 用法：client = tdx_client()                  # K 线 / 盘口 / 逐笔（#52：目前普遍取不到，见 §1.7 警告）
#       client = tdx_client(check='finance')   # 财务快照 / F10（正常）
```

> **海外 IP 用户：** mootdx 走通达信 TCP 7709，海外环境通常全部超时。`tdx_client()` 会快速失败给出明确报错，而非死等。
>
> **⚠️ 行情命令失效（#52，2026-09-20 实测）：** 内置 10 台服务器逐台测试，TCP 均可达，`finance` / `xdxr` 正常、
> `F10` 只剩「最新提示」一类（见 §6.2），但 `bars` / `quotes` / `transaction` 全部返回 0 行。财务与 F10 调用请传 `check='finance'`；
> K 线改走 §1.2 腾讯 / §1.3 通达信盘后包，实时价与五档走 §1.1 腾讯，当日逐笔走 §1.4 腾讯。

### 市场前缀规则（全局通用）

```python
# 沪市指数白名单：与深市 000xxx 个股同段，需白名单区分（沪深300/上证50/中证500/科创50/中证1000/上证180）
SH_INDEX = {"000300", "000905", "000016", "000688", "000852", "000010"}

def get_prefix(code: str) -> str:
    """6位代码 → 市场前缀（sh/sz/bj）。支持显式前缀/后缀（sh000016 / 000016.SH）透传以解决歧义。"""
    c = code.lower().strip()
    if c.endswith((".sh", ".sz", ".bj")):    # 后缀写法与前缀等价：000016.SH ≡ sh000016。
        return c[-2:]                        # 不认后缀会让 000016.SH 落到默认深市 → 静默查成深康佳A
    if c.endswith((".xshg", ".xshe")):       # 聚宽写法（#55）：.XSHG=上交所 / .XSHE=深交所，000001.XSHG=上证指数
        return "sh" if c.endswith(".xshg") else "sz"
    if c.startswith(("sh", "sz", "bj")):     # 显式前缀透传（如 sh000001=上证指数 vs sz000001=平安银行）
        return c[:2]
    if c.startswith("92"):                   # 北交所 2024-10 起的新股号段，必须先于下面的 9x 判断
        return "bj"
    if c.startswith(("5", "6", "9")):        # 5x=沪 ETF/LOF，6/9=沪个股（900xxx=沪 B 股）
        return "sh"
    if c.startswith(("4", "8")):             # 4x/8x=北交所【老号段，多数已迁 920，见下方警告】
        return "bj"
    if c in SH_INDEX:                         # 沪深300/上证50 等沪指数（000xxx）
        return "sh"
    return "sz"                              # 深市个股/ETF（00/30/15x/16x/159 等），深指数 399xxx 亦走 sz

```

> **歧义说明：** `000001` 默认按个股→`sz000001`（平安银行）；要上证指数请显式传 `sh000001`。`000016` 默认按沪指数→上证50；要深康佳A 请传 `sz000016`。

> ### ⚠️ 北交所老号段（43/83/87）已基本作废 — 会拿到僵尸数据且不报错
>
> **2026-07-31 实测：** 东财北交所在市 342 只中 **336 只已是 `920xxx` 号段**，仅剩 3 只老码且全部停牌。存量公司代码已整体迁移（如 锦波生物 `832982`→`920982`、贝特瑞 `835185`→`920185`）。
>
> **危险在于老码不会报错，而是返回看似正常的脏数据：**
>
> | 接口 | 传老码 `832982` | 传新码 `920982` |
> |------|----------------|----------------|
> | 腾讯行情 | 返回 **112.60、成交量 0**（定格在迁移日） | 131.74，正常成交 ✅ |
> | 腾讯行情（贝特瑞） | `835185` → 45.91、成交量 0 | `920185` → 21.05 ✅ |
> | 东财研报 | **0 篇**（静默空） | 79 篇 ✅ |
>
> 老码行情价与真实价可差 17%~100%+，直接拿去算估值会得出完全错误的结论。
>
> **判定僵尸报价：** `成交量 == 0 且 最新价 == 昨收` → 极可能是已迁移的废码（真停牌股同样满足，两者都不该用于估值）。`tencent_quote()` 已内置该检测并置 `is_stale` 标志，见 §1.1。
>
> **拿新码：** 用 `push2` 北交所全量清单 `fs=m:0+t:81+s:2048` 按名称反查现行代码。

### Ticker 格式归一化

`norm_ticker()` 把下列写法统一成纯 6 位数字：

> ⚠️ **不是所有端点都自动归一化**（V3.6.0 前这里写的是「所有接口统一支持」，与实现不符，已改正）。
> - **已内置归一化**：§2.1 `eastmoney_reports()`、§2.2 `ths_eps_forecast()`。
> - **只认纯 6 位或显式 `sh`/`sz`/`bj` 前缀**（其余端点）：`tencent_quote()` 等走 `get_prefix()` 路由的函数
>   支持 `600519` 和 `sh600519`，但**不认后缀式** `600519.SH`——实测会拼成 `sh600519.SH` 并返回空载荷（静默失败）。
> - **结论**：拿到用户输入的代码，**先过一遍 `norm_ticker()` 再传给任何端点**，最省事也最安全。
>   例外：输入本身带市场信息且落在 000 歧义段（`000001.SH` / `000001.XSHG` = 上证指数）时，`norm_ticker()` 会丢掉市场，
>   应改用 `get_prefix(c) + norm_ticker(c)` 得到 `sh000001` 再传。聚宽代码互转见下方 `to_joinquant()`（#55）。

| 输入 | 归一化结果 |
|------|-----------|
| `688017` | `688017` |
| `SH688017` / `sh688017` | `688017` |
| `688017.SH` / `688017.sh` | `688017` |
| `SZ000001` | `000001` |
| `BJ920982` | `920982` |
| `600519.XSHG` / `000001.XSHE`（聚宽写法，#55） | `600519` / `000001` |

```python
import re

# 整串锚定匹配，只认下表列出的写法；市场标识前缀、后缀**二选一，不能同时出现**。
# ⚠️ 两个坑都会造成「静默拿到另一只股票的数据」，比报错危险得多：
#   ① 别用 re.search(r"\d{6}") 从任意串里"捞"6 位："6005190"/"foo600519bar" 会被截成 600519。
#   ② 别让前后缀同时可选：`SH000001.SZ` 这种自相矛盾的写法会被照单全收，
#      而 000001 恰是歧义码（sh000001=上证指数 / sz000001=平安银行），静默丢掉市场信息＝选错标的。
# 捕获组：1=前缀市场 2=前缀式代码 | 3=后缀式代码 4=后缀市场
# 市场标识要**同时**从前缀和后缀取——只认 startswith("sh") 会漏掉 `000001.SH` 这种后缀写法。
_TICKER_RE = re.compile(
    r"^(?:(sh|sz|bj)(\d{6})|(\d{6})(?:\.(sh|sz|bj|xshg|xshe))?)$", re.IGNORECASE)
_JQ_SUFFIX = {"xshg": "sh", "xshe": "sz"}    # 聚宽后缀 → 市场（#55）；聚宽未公开北交所后缀，不猜

def _natural_market(digits: str) -> str:
    """6 位码的自然归属市场。仅用于校验显式前缀是否自相矛盾。
    注意 000xxx 是沪指数/深个股共用的歧义段，由调用处单独处理，不走这里。"""
    if digits.startswith(("4", "8", "92")):
        return "bj"                      # 北交所：与 get_prefix() 同一套号段规则（92x 现行 / 4x·8x 老号段，#51）
    if digits[0] in ("5", "6", "9"):
        return "sh"                      # 5x 沪 ETF/LOF，6xx 沪个股，9xx 沪 B 股
    return "sz"                          # 00x/30x/15x/16x/39x 等

def norm_ticker(code: str, stock_only: bool = False) -> str:
    """任意受支持写法 → 纯 6 位数字代码。

    支持 600519 / SH600519 / sh600519 / 600519.SH / BJ920982 等。
    stock_only=True：个股专用接口（研报、一致预期等）传这个，会拒绝显式指数写法。
    ⚠️ 不匹配时**抛 ValueError，绝不静默返回空串或猜一个代码**——
    否则调用方会把「代码格式写错」误读成「这只票没有数据」，
    或者更糟：拿到另一只股票的数据还以为是对的。
    """
    raw = str(code).strip()
    m = _TICKER_RE.match(raw)
    if not m:
        raise ValueError(
            f"无法把 {code!r} 解析为 6 位股票代码；"
            f"支持格式：600519 / SH600519 / sh600519 / 600519.SH / 600519.XSHG（聚宽）"
            f"（前缀与后缀二选一，不能同时写）"
        )
    digits = m.group(2) or m.group(3)
    market = (m.group(1) or m.group(4) or "").lower()      # 前缀式与后缀式都要认
    market = _JQ_SUFFIX.get(market, market)                  # 600519.XSHG ≡ 600519.SH
    # 归一化会丢掉市场标识，若标识与号段矛盾就会静默落到另一只票上，必须在这里拦。
    if market:
        if digits.startswith("000"):
            # 000xxx 是**沪市指数 / 深市个股共用**的歧义段，显式标识在这里是「消歧」不是「矛盾」：
            #   sh000001=上证指数 vs sz000001=平安银行；sh000016=上证50 vs sz000016=深康佳A。
            if market == "bj":
                raise ValueError(f"{code!r} 市场标识与号段矛盾：000xxx 不属北交所。")
            # 沪市个股只有 600/601/603/605/688/689（B 股 900），**不存在 000xxx 沪市个股**，
            # 所以「显式 sh + 000 段」必然是指数。实测不拦的话：sh000001→平安银行研报 100 篇、
            # sh000016→深康佳A、sh000039→中集集团 84 篇，全是别人的数据。
            if stock_only and market == "sh":
                raise ValueError(
                    f"{code!r} 指向沪市指数而非个股（沪市无 000xxx 个股），本接口只服务个股。"
                    f"要查同号段的深市个股请显式传 sz{digits}。"
                )
        else:
            nat = _natural_market(digits)
            if market != nat:
                raise ValueError(
                    f"{code!r} 的市场标识与号段矛盾：{digits} 属 {nat} 市，而不是 {market} 市。"
                    f"（改用 {nat}{digits} 或去掉市场标识）"
                )
    return digits

# 用法
norm_ticker("SH600519")      # '600519'
norm_ticker("600519.SH")     # '600519'
norm_ticker("bj920982")      # '920982'
norm_ticker("6005190")       # ValueError（7 位，不会被截成 600519）
norm_ticker("茅台")           # ValueError
norm_ticker("SH000001.SZ")   # ValueError（前后缀矛盾，不猜市场）
norm_ticker("SH000001", stock_only=True)     # ValueError（上证指数，不是平安银行）
norm_ticker("000001.SH", stock_only=True)    # ValueError（后缀写法同样拦下）
norm_ticker("SZ600519")                      # ValueError（600519 是沪市，标识矛盾）
norm_ticker("sz000016")                      # '000016'（深康佳A，000 段的显式消歧，合法）
norm_ticker("600519.XSHG")                   # '600519'（聚宽写法，#55）
norm_ticker("600519.XSHE")                   # ValueError（600519 是沪市，聚宽后缀同样校验）


def em_market_code(code: str) -> int:
    """东财 secid 的市场号：**沪=1，深/北=0**（V3.7.0 新增 · #46）。

    ⚠️ 绝不要用 `code.startswith("6")` 判市场 —— 那会把**沪市 ETF（51x）**、
    **科创板 ETF（588x）**、**沪 B 股（900x）** 全部错判成深市，接口返回 `data: null`。
    2026-08-19 实测：510300 / 588000 / 600519 / 688112 / 900901 → m=1；
    300750 / 159915 / 920982 / 832982 → m=0（北交所与深市共用 m=0）。
    """
    return 1 if get_prefix(code) == "sh" else 0


def em_secid(code: str) -> str:
    """东财 push2/push2his 的 secid，如 `1.600519` / `0.300750`。"""
    return f"{em_market_code(code)}.{norm_ticker(code)}"


def to_joinquant(code: str) -> str:
    """任意受支持写法 → 聚宽代码，如 `600519.XSHG` / `000001.XSHE`（#55）。

    000 段歧义码按 get_prefix() 的规则走：`to_joinquant("sh000001")` → `000001.XSHG`（上证指数），
    `to_joinquant("000001")` → `000001.XSHE`（平安银行）。反方向（聚宽 → 本 Skill）用
    `get_prefix(c) + norm_ticker(c)` 得到 `sh000001` 这类显式前缀写法，再传给各端点。
    北交所：聚宽公开文档与 jqdatasdk 源码（2026-09-20 查）只有 .XSHG / .XSHE，没查到北交所后缀，抛 ValueError 不猜。
    """
    digits, market = norm_ticker(code), get_prefix(code)
    if market == "bj":
        raise ValueError(f"{code!r} 是北交所证券；聚宽公开文档未给出北交所后缀，不做转换")
    return f"{digits}.{'XSHG' if market == 'sh' else 'XSHE'}"
```

### 东财数据中心统一查询（共用 helper）

龙虎榜/解禁/融资融券/大宗交易/股东户数/分红 共用同一 base URL：

```python
import time
import random
import requests

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
DATACENTER_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"

# ── 东财防封：全局节流 + 会话复用 ────────────────────────────────────
# 东财系 HTTP 接口（push2 / datacenter / reportapi / search / np-weblist）有风控：
#   每秒 >5 次 / 单 IP 并发 ≥10 / 1 分钟 ≥200 次  →  临时封 IP。
# 所有 eastmoney.com 请求一律走 em_get()：串行限流（最小间隔 + 随机抖动）+ 复用
# Keep-Alive 会话，批量调用时自动降速，避免被封。详见「数据源优先级 & 东财防封」章节。
EM_SESSION = requests.Session()
EM_SESSION.headers.update({"User-Agent": UA})
# 连接级自动重试：瞬态连接错误 / 429 / 5xx 指数退避重试（住宅IP偶发风控更稳）。
# 注意：403 不重试（东财风控信号，重试无益反而加重；按下方 EM_MIN_INTERVAL 降频应对）。
try:
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    _em_adapter = HTTPAdapter(max_retries=Retry(
        total=3, connect=3, backoff_factor=0.6,
        status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"]))
    EM_SESSION.mount("https://", _em_adapter)
    EM_SESSION.mount("http://", _em_adapter)
except Exception:
    pass  # 老版本 urllib3 缺 allowed_methods 等参数时降级为无重试，不影响主流程
from typing import Optional     # 3.9 兼容：不能写 `dict | None`（那是 3.10+ 语法）

EM_MIN_INTERVAL = 1.0          # 两次东财请求最小间隔(秒)；批量筛选建议调大到 1.5~2
_em_last_call = [0.0]          # 模块级上次请求时间戳

def em_get(url: str, params: Optional[dict] = None, headers: Optional[dict] = None,
           timeout: int = 15, **kwargs):
    """东财统一请求入口：自动节流 + 复用 session + 默认 UA。
    所有 eastmoney.com 接口都应通过它请求，避免高频被封 IP。"""
    wait = EM_MIN_INTERVAL - (time.time() - _em_last_call[0])
    if wait > 0:
        time.sleep(wait + random.uniform(0.1, 0.5))
    try:
        return EM_SESSION.get(url, params=params, headers=headers, timeout=timeout, **kwargs)
    finally:
        _em_last_call[0] = time.time()

def eastmoney_datacenter(report_name: str, columns: str = "ALL",
                          filter_str: str = "", page_size: int = 50,
                          sort_columns: str = "", sort_types: str = "-1") -> list[dict]:
    """东财数据中心统一查询 — 龙虎榜/解禁/融资融券/大宗交易/股东户数/分红 共用（已内置限流）"""
    params = {
        "reportName": report_name, "columns": columns,
        "filter": filter_str, "pageNumber": "1", "pageSize": str(page_size),
        "sortColumns": sort_columns, "sortTypes": sort_types,
        "source": "WEB", "client": "WEB",
    }
    r = em_get(DATACENTER_URL, params=params, timeout=15)
    d = r.json()
    if d.get("result") and d["result"].get("data"):
        return d["result"]["data"]
    return []
```

### V3.9.0 共用 helper（§1.2 腾讯 K 线起的所有 V3.9.0 / V3.10.0 新端点都依赖它）

先执行上面的 `get_prefix` / `norm_ticker` / 东财 `em_get` 代码块，再执行本块。V3.9.0 新端点统一返回 DataFrame，
末尾附 `source` / `source_url` / `fetched_at` 三列。**「确实没有数据」与「接口坏了」分开处理**：前者返回空表或抛
`ValueError`（非交易日、日期太早），后者抛 `RuntimeError`（结构改变、重复行、全市场 0 行），不把错误页当空结果。
东财请求一律经 `em_get()` 限流；`_em_datacenter_strict()` 与旧 `eastmoney_datacenter()` 的区别是会翻页、并把错误码抛出来。

<!-- v39-helpers:start -->
```python
import functools
import math
import re
from datetime import date as _date_cls, datetime, timezone

import pandas as pd
import requests

V39_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# 一次要翻几十页（§1.4 腾讯逐笔）或偶尔握手卡住（§13.7 新浪期货日 K）的请求走这个会话：复用连接，
# 连接失败、握手或等响应头超时、429 / 5xx 指数退避重试（写法同 EM_SESSION）；读响应体中途超时不重试，
# 也不按服务端给的 Retry-After 等待。
V39_RETRY_SESSION = requests.Session()
try:
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    _v39_retry_adapter = HTTPAdapter(max_retries=Retry(
        total=3, connect=3, backoff_factor=0.6, respect_retry_after_header=False,
        status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"]))
    V39_RETRY_SESSION.mount("https://", _v39_retry_adapter)
    V39_RETRY_SESSION.mount("http://", _v39_retry_adapter)
except Exception:
    # 老版本 urllib3（< 1.26）缺 allowed_methods：不重试，也不复用连接（复用的连接被服务端断开时没有重试兜底），同 v3.10.0
    V39_RETRY_SESSION = None


def _v39_http(url, params=None, data=None, headers=None, method="GET", timeout=(10, 40),
              allow_status=(), allow_redirects=True, session=None):
    """非东财的 HTTP 请求：带浏览器 UA。网络错误、非 2xx 一律抛 RuntimeError（不把错误页当数据）；
    allow_status 里的状态码（源用 404 表示「当天没发布」时）原样返回，由调用方判断。
    session：传 V39_RETRY_SESSION 复用连接并自动重试（哪些情况重试见它的定义）；不传每次新建连接、不重试。"""
    merged = {"User-Agent": V39_UA}
    merged.update(headers or {})
    try:
        response = (session or requests).request(method, url, params=params, data=data, headers=merged,
                                                 timeout=timeout, allow_redirects=allow_redirects)
        if response.status_code not in allow_status:
            response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"请求 {url} 失败: {type(exc).__name__}: {exc}") from exc
    return response


def _v39_json(response):
    """解析 JSON；不是 JSON 抛 RuntimeError。json 的解析错误是 ValueError 的子类，
    不转换会被调用方当成「确实没有数据」。"""
    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError(f"{getattr(response, 'url', '')} 返回的不是 JSON，可能是错误页") from exc


def _v39_date(value):
    """'2026-09-18' / '20260918' / date 对象 → '2026-09-18'；其他写法抛 ValueError。"""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, _date_cls):
        return value.isoformat()
    text = str(value).strip()
    fmt = "%Y%m%d" if re.fullmatch(r"[0-9]{8}", text) else "%Y-%m-%d"
    return datetime.strptime(text, fmt).date().isoformat()


def _v39_src_date(value):
    """来源返回的日期 → 'YYYY-MM-DD'；认不出抛 RuntimeError（源格式变了，不是参数写错）。"""
    try:
        return _v39_date(value)
    except ValueError as exc:
        raise RuntimeError(f"来源返回了无法识别的日期 {value!r}") from exc


def _v39_num(value):
    """'1,234.50' → 1234.5；空串 / '-' / '--' / None → None；其他非数字抛 RuntimeError
    （来源给了认不出的值是「源的格式变了」，不能和参数错误的 ValueError 混在一起）。
    JSON 布尔值同样抛错：float(True)=1.0 会把格式错误静默写成价格 / 成交量。"""
    if value is None:
        return None
    if isinstance(value, bool):
        raise RuntimeError(f"来源在数值字段给了布尔值 {value!r}")
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            return None
        return float(value)
    text = str(value).replace(",", "").strip()
    if text in ("", "-", "--", "None", "null"):
        return None
    try:
        number = float(text)
    except ValueError as exc:
        raise RuntimeError(f"来源返回了无法识别的数值 {value!r}") from exc
    return number if math.isfinite(number) else None


def _v39_rows(value, what):
    """来源里可能整段缺失的行列表：字段没有（None）按空处理，其余必须是对象列表。
    写成 `value or []` 会把 {} / '' / 0 这类结构改变也当成空表，静默丢掉整段数据。"""
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise RuntimeError(f"{what} 应为对象列表，实际是 {type(value).__name__}: {str(value)[:120]}")
    return value


def _v39_labels(value, what):
    """来源的标签数组（频道名之类）：None 按空处理，其余必须是字符串列表。
    直接 `value or []` 再 join，来源把数组改成字符串时会被拆成单字（'ab' → 'a,b'）。"""
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise RuntimeError(f"{what} 应为字符串列表，实际是 {type(value).__name__}: {str(value)[:120]}")
    return value


def _v39_req_num(value, what):
    """必填数值（价格、成交量）：在 _v39_num 之上，空值 / NaN / inf 也抛 RuntimeError，不能当缺失放过。"""
    number = _v39_num(value)
    if number is None:
        raise RuntimeError(f"来源的 {what} 为空或不是有限数值: {value!r}")
    return number


def _v39_contract(func):
    """统一异常契约：来源行缺字段时 row["X"] 会漏出 KeyError，调用方按「参数错 / 没数据」处理就会
    把「来源格式变了」当成正常情况。这里把它转成带函数名和字段名的 RuntimeError。
    （函数内所有按用户参数取字典的地方都先校验过参数，不会走到这里。）"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as exc:
            raise RuntimeError(f"{func.__name__}: 来源数据缺少字段 {exc}，格式可能已变") from exc
    return wrapper


def _v39_count(value, what):
    """来源自报的页数 / 条数 → 非负 int。只认 int 或纯数字串；bool 抛错（int(True)=1 会让
    「只返回 1 条」通过完整性核对），其他写法也抛 RuntimeError。"""
    text = str(value).strip() if isinstance(value, (int, str)) and not isinstance(value, bool) else ""
    if not re.fullmatch(r"[0-9]+", text):
        raise RuntimeError(f"{what} 不是非负整数: {value!r}")
    return int(text)


def _v39_frame(rows, source, url, columns=None):
    """统一出表：附 source / source_url / fetched_at。rows 为空时返回带列名的空表，
    是否允许为空由调用方判断（「确实没有」与「接口坏了」要分开处理）。"""
    frame = pd.DataFrame(rows, columns=columns)
    frame["source"] = source
    frame["source_url"] = url
    frame["fetched_at"] = datetime.now(timezone.utc).isoformat()
    return frame


def _em_datacenter_strict(report_name, filter_str="", sort_columns="", sort_types="",
                          page_size=500, max_rows=5000, columns="ALL", extra=None):
    """东财 datacenter 严格版：code=0 取数据；第 1 页就 9201(返回数据为空) → []；其他错误码直接抛。

    与旧 eastmoney_datacenter() 的区别：后者把任何失败都变成 []，调用方分不清
    「这只票确实没有」和「参数写错/被风控」。sortTypes 个数必须与 sortColumns 一致，
    否则东财返回 9501「排序字段和顺序数量不一致」。
    翻页中途失败（第 2 页起 9201、空页、非末页不满页、缺 pages / count、总页数或总条数变了、
    最终条数与 count 不符）抛 RuntimeError，不把部分结果当完整结果返回。
    payload / result 不是对象、data 不是由对象组成的列表，同样抛 RuntimeError。
    只有「第 1 页、pages=1、data 为空」才算确实没有数据。
    max_rows 只在来源自报总数 count > max_rows 时提前截断；count 不超过上限的，一律走完分页并核对总数。
    """
    n_cols = len([c for c in sort_columns.split(",") if c]) if sort_columns else 0
    n_types = len([t for t in sort_types.split(",") if t]) if sort_types else 0
    if n_cols != n_types:
        raise ValueError(f"sortColumns({n_cols}) 与 sortTypes({n_types}) 个数不一致")
    rows, page, first = [], 1, None
    while True:
        params = {"reportName": report_name, "columns": columns, "filter": filter_str,
                  "pageNumber": str(page), "pageSize": str(page_size),
                  "sortColumns": sort_columns, "sortTypes": sort_types,
                  "source": "WEB", "client": "WEB"}
        params.update(extra or {})
        try:
            response = em_get(DATACENTER_URL, params=params, timeout=20)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"东财 {report_name} 请求失败: {type(exc).__name__}: {exc}") from exc
        payload = _v39_json(response)
        if not isinstance(payload, dict):
            raise RuntimeError(f"东财 {report_name} 返回的不是 JSON 对象: {str(payload)[:100]}")
        if payload.get("code") == 9201:
            if page == 1:
                return []
            raise RuntimeError(f"东财 {report_name} 第 {page} 页返回「数据为空」，"
                               f"前面已取 {len(rows)} 条，结果不完整")
        if payload.get("code") != 0 or not payload.get("result"):
            raise RuntimeError(f"东财 {report_name} 返回错误: "
                               f"{payload.get('code')} {payload.get('message')}")
        result = payload["result"]
        if not isinstance(result, dict):
            raise RuntimeError(f"东财 {report_name} 的 result 不是对象: {str(result)[:100]}")
        pages, count, data = result.get("pages"), result.get("count"), result.get("data")
        if data is None:
            data = []
        if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
            raise RuntimeError(f"东财 {report_name} 第 {page} 页的 data 不是由对象组成的列表，格式可能已变")
        if (any(isinstance(v, bool) or not isinstance(v, int) for v in (pages, count))
                or pages < 1 or count < 0):
            raise RuntimeError(f"东财 {report_name} 缺少分页信息（pages={pages!r}, count={count!r}）")
        if first is None:
            first = (pages, count)
        elif (pages, count) != first:
            raise RuntimeError(f"东财 {report_name} 翻页时总页数 / 总条数从 {first} 变成 {(pages, count)}，"
                               "结果可能错位，请重试")
        if not data and (page > 1 or pages > 1):
            raise RuntimeError(f"东财 {report_name} 第 {page}/{pages} 页是空的，结果不完整")
        if page < pages and len(data) != int(page_size):
            raise RuntimeError(f"东财 {report_name} 第 {page}/{pages} 页只有 {len(data)} 条"
                               f"（非末页应为 {page_size} 条），结果不完整")
        rows.extend(data)
        # 只有来源自报的总数确实超过上限才提前截断；否则（count <= max_rows 却已拿到更多行）
        # 必须走完分页并核对总数，不然「data 比 count 还多」这种格式异常会被当成正常截断放过
        if len(rows) >= max_rows and count > max_rows:
            return rows[:max_rows]
        if page >= pages:
            if len(rows) != count:
                raise RuntimeError(f"东财 {report_name} 翻页后 {len(rows)} 条，与总数 {count} 不符")
            return rows
        page += 1


def _em_day(value):
    """东财日期串 '2026-09-18 00:00:00' → '2026-09-18'；空值 → None；认不出的写法抛 RuntimeError
    （只截前 10 个字符会把 '2026/09/18' 原样放行，再拿去和日期串比较就会比错）。"""
    return _v39_src_date(str(value)[:10]) if value else None
```
<!-- v39-helpers:end -->

---

## Layer 1: 行情层（实时，不封IP）

> **V3.10.0 起本层重排：能用的在前，2026-09 起失效的 mootdx 行情命令移到最后（§1.7，留档）。**
> 旧编号 → 新编号：1.2→1.1 腾讯实时、1.5→1.2 腾讯 K 线、1.6→1.3 通达信盘后包、1.3→1.5 百度、1.4→1.6 新浪复权因子、1.1→1.7 mootdx；
> §1.4 腾讯逐笔为新增。CHANGELOG 与文件开头的历史版本说明里写的仍是旧编号。

### 1.1 腾讯财经 API — PE/PB/市值/换手率/涨跌停/指数/ETF

HTTP GET，GBK 编码，`~` 分隔 88 个字段，不封IP。

```python
import urllib.request

def tencent_quote(codes: list[str]) -> dict[str, dict]:
    """
    批量拉取腾讯财经实时行情。
    codes: ["688017", "300476", "002463"]
    也支持指数: ["000001", "000300", "399006"]
    也支持ETF: ["510050", "510300"]
    返回: {code: {name, price, pe_ttm, pb, mcap, ...}}
    """
    # 前缀路由：与全局 get_prefix() 一致。5x 沪ETF / 000300 等沪指数不能落到 sz（会返回空或错票）。
    SH_INDEX = {"000300", "000905", "000016", "000688", "000852", "000010"}   # 沪指数白名单
    prefixed = []
    key_of = {}          # 带前缀的查询键 → 调用方原始写法，保证结果键与入参一一对应
    for c in codes:
        low = c.lower()
        if low.startswith(("sh", "sz", "bj")):        # 显式前缀透传，解决 000001 等歧义
            p = low
        elif c.startswith("92"):                      # 北交所 920 号段须先于 9x 判断
            p = f"bj{c}"
        elif c in SH_INDEX or c.startswith(("5", "6", "9")):
            p = f"sh{c}"
        elif c.startswith(("4", "8")):
            p = f"bj{c}"
        else:
            p = f"sz{c}"
        prefixed.append(p)
        key_of[p] = c    # 显式前缀入参原样返回，裸代码返回裸代码

    url = "https://qt.gtimg.cn/q=" + ",".join(prefixed)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    resp = urllib.request.urlopen(req, timeout=10)
    data = resp.read().decode("gbk")

    result = {}
    for line in data.strip().split(";"):
        if not line.strip() or "=" not in line or '"' not in line:
            continue
        key = line.split("=")[0].split("_")[-1]
        vals = line.split('"')[1].split("~")
        if len(vals) < 53:
            continue
        # 用入参原样做键：批量里同时传 sh000001 与 sz000001 时，若都退回裸 6 位码
        # 会撞成同一个键、后者静默覆盖前者，显式前缀这个特性就白做了。
        code = key_of.get(key, key[2:])
        result[code] = {
            "name":         vals[1],
            "price":        float(vals[3]) if vals[3] else 0,
            "last_close":   float(vals[4]) if vals[4] else 0,
            "open":         float(vals[5]) if vals[5] else 0,
            "change_amt":   float(vals[31]) if vals[31] else 0,
            "change_pct":   float(vals[32]) if vals[32] else 0,
            "high":         float(vals[33]) if vals[33] else 0,
            "low":          float(vals[34]) if vals[34] else 0,
            "amount_wan":   float(vals[37]) if vals[37] else 0,
            "turnover_pct": float(vals[38]) if vals[38] else 0,
            "pe_ttm":       float(vals[39]) if vals[39] else 0,
            "amplitude_pct":float(vals[43]) if vals[43] else 0,
            # ⚠️ 44=流通市值、45=总市值（曾标反）。总股本≠流通股本时差数倍，见上方踩坑提醒二
            "float_mcap_yi":float(vals[44]) if vals[44] else 0,
            "mcap_yi":      float(vals[45]) if vals[45] else 0,
            "pb":           float(vals[46]) if vals[46] else 0,
            "limit_up":     float(vals[47]) if vals[47] else 0,
            "limit_down":   float(vals[48]) if vals[48] else 0,
            "vol_ratio":    float(vals[49]) if vals[49] else 0,
            "pe_static":    float(vals[52]) if vals[52] else 0,
        }
        # 僵尸报价检测：腾讯对「已迁移的北交所老码 / 长期停牌股」照样返回 HTTP 200 +
        # 一份定格在最后交易日的报价（成交量 0、最新价==昨收），不报任何错。
        # 直接拿去算估值会得出完全错误的结论（实测 bj832982 报 112.60，真实新码 920982 为 131.74）。
        q = result[code]
        q["is_stale"] = (q["amount_wan"] == 0 and q["price"] == q["last_close"] and q["price"] > 0)
        if q["is_stale"] and key[2:4] in ("43", "83", "87"):
            q["stale_reason"] = "北交所老号段，多数已迁至 920xxx，请按名称反查现行代码"
        elif q["is_stale"]:
            q["stale_reason"] = "成交量为 0（停牌 / 未开盘 / 废码），报价非当日真实成交"
    return result

# 用法: 个股
quotes = tencent_quote(["688017", "300476", "002463"])
for code, q in quotes.items():
    print(f"{q['name']}({code}): {q['price']}元 PE={q['pe_ttm']} PB={q['pb']} 市值={q['mcap_yi']}亿")

# 用法: 指数 — sh000001=上证指数, sh000300=沪深300, sz399006=创业板指
index_quotes = tencent_quote(["000001", "000300", "399006"])

# 用法: ETF — sh510050=上证50ETF, sh510300=沪深300ETF
etf_quotes = tencent_quote(["510050", "510300"])
```

#### 腾讯财经字段索引速查（实测校准 2026-05-03）

| 索引 | 含义 | 示例 |
|------|------|------|
| 1 | 名称 | 绿的谐波 |
| 3 | 当前价 | 224.12 |
| 4 | 昨收 | 215.01 |
| 5 | 今开 | 214.10 |
| 9-18 | 买一~买五(价+量) | |
| 19-28 | 卖一~卖五(价+量) | |
| 31 | 涨跌额 | 9.11 |
| 32 | 涨跌幅% | 4.24 |
| 33 | 最高 | 229.62 |
| 34 | 最低 | 214.10 |
| 37 | 成交额(万) | 187040 |
| 38 | 换手率% | 4.55 |
| **39** | **PE(TTM)** | 300.45 |
| **43** | **振幅%（不是PB！）** | 7.22 |
| **44** | **流通市值(亿)** | 410.88 |
| **45** | **总市值(亿)** | 410.88 |
| **46** | **PB(市净率)** | 11.51 |
| **47** | **涨停价** | 258.01 |
| **48** | **跌停价** | 172.01 |
| 49 | 量比 | 1.20 |
| **52** | **PE(静)** | 314.76 |

> **踩坑提醒一：** 网上很多教程把索引 43 写成 PB，实测是振幅%。PB 在索引 46。
>
> **踩坑提醒二（2026-07-26 修正）：** **44 是流通市值、45 才是总市值**，此前本表标反了。
> 多数股票两者相等，所以看不出来；但**总股本 ≠ 流通股本的票（科创板/次新股/有限售股）会差出数倍**。
> 实测中船特气(688146)：`f[44]=356.15亿`(流通股本 1.45亿股)、`f[45]=1300.61亿`(总股本 5.29亿股)，**差 3.65 倍**。
> 用市值做筛选时取错会把大市值公司误判成小盘股。可用 `f[45] ÷ 现价` 反推总股本核对（与东财 `f84` 一致）。
> 参考：东财 push2 的 `f116`=总市值 / `f117`=流通市值 方向与腾讯相反，实测确认无误，勿混用。

### 1.2 腾讯 K 线 — 日/周/月前后复权 + 1~60 分钟（V3.9.0 新增 · #52）

§1.7 mootdx K 线失效（#52）后的主力 K 线源。三个入口是同一后端、限流各自独立：某入口返回空或异常时冷却 120 秒、换下一个，
三个都不可用才抛错（#52 实测单入口约 600 次后返回空 JSON）。**只支持沪深**：腾讯对北交所只返回最新 1 根日线、
区间和分钟线都是空的（2026-09-20 实测 920021 / 920982 / 920185），函数遇北交所代码直接抛 `ValueError`，北交所日线用 §1.3。

| 参数 | 说明 |
|---|---|
| `period` | `day` / `week` / `month`：默认前复权，可 `adjust='hfq'` 或 `adjust=''`（不复权）；`m1` / `m5` / `m15` / `m30` / `m60`：只有不复权、只能取最近 ≤320 根 |
| `start` / `end` | 仅日周月可用，自动按段翻页（单段 <640 根）；不给 `start` 时取最近 `count` 根（≤640） |
| 返回列 | `code` / `adjust`（仅日周月）/ `date` / `open` / `high` / `low` / `close` / `volume`；分钟线另有 `turnover_rate_pct`，日期列名为 `datetime` |
| `volume` 单位 | **科创板（688 / 689）是股**，其余是手：沪深主板、创业板、B 股、ETF（含科创板 ETF 588）、LOF、REITs 1 手 = 100 股 / 份，可转债 1 手 = 10 张，指数也是手；日周月线、分钟线、复权与否都是这个规则 |

> ⚠️ **腾讯前复权是等差口径**（逐次减去每股分红）：茅台 2020-01-02 原始价 1130.00、腾讯 qfq 870.741，差额正是此后累计分红；
> 高分红老股早年会被减成负数（茅台 2015 年约 -117.6）。本函数遇到 ≤0 价格直接抛错。**长区间回测请取 `adjust=''`，
> 再用 §1.6 的比例因子复权**。本接口**没有成交额**，需要成交额用 §1.3。

> ⚠️ **成交量按股对账前先看这几条**（#57，2026-10-05 对照通达信盘后包与 Baostock 实测）：
> - **整手取整**：科创板以外，日线的量是当日总股数取整到手——2020-03-11 起基本是四舍五入（实测差 −52～+50 股），更早是舍去零头（差 −99～0 股），
>   日线不会回填，周 / 月线是日线相加。分钟线**最近一个交易日**也是逐根整手，要到下一个交易日才回填成精确股数（会出现 34967.59 这样的小数手），
>   回填后当日各根合计与盘后包逐股一致；确切的回填时点没测出来。科创板的分钟量当天就是精确股数。
>   ⇒ **最近一个交易日的分钟量别拿来按股精确对账**。本函数 m1 最多 320 根（约 1.3 天），要拿整天已回填的数据用 m5 / m60（320 根约 6 / 80 个交易日）。
> - **1 分钟线**每天 241 根：09:30 那根只有开盘集合竞价（竞价没成交就没有这根），m5 及以上把竞价并进第一根。
>   13:01 那根的开盘价是上午收盘价、不是午后第一笔，用 m1 自己合成 5 分钟线时 13:05 的开盘价会和腾讯原生 m5 / Baostock 对不上。
> - **深市分钟边界**：整分那一刻（hh:mm:00）的成交，腾讯算进下一根（m1、原生 m5 都是；11:30:00 那一刻例外，留在 11:30 那根），Baostock 算进上一根，所以深市逐根量价对不上
>   （改按开始时刻分桶也拼不回来）、全天合计一致；沪市已回填的日子腾讯原生 m5 与 Baostock 5 分钟逐根一致。
> - **没有成交的分钟**：当天第一笔成交以前沪深都没有行（集合竞价没成交时连 09:30 那根也没有；09-30 抽 54 只沪深 B 股，第一笔晚于 09:30 的 43 只都从第一笔那分钟才有行）。
>   第一笔以后，沪市没有成交的分钟给一根量为 0、四个价基本都等于上一根收盘的行，不缺行；深市大多也这样，但会整根缺失
>   （09-30 抽 51 只低成交深市股，25 只共缺 64 分钟，抽查的缺失分钟逐笔里都没有成交）。按分钟格点对齐时要自己处理缺行。

<!-- v39-tencent-kline:start -->
```python
import time
from datetime import date, datetime, timedelta

# 三个入口是同一后端，但限流各自独立（#52 实测单域名约 600 次后返回空 JSON）。
TENCENT_KLINE_HOSTS = ["https://web.ifzq.gtimg.cn",
                       "https://proxy.finance.qq.com/ifzqgtimg",
                       "https://ifzq.gtimg.cn"]
_TENCENT_HOST_COOLDOWN = 120          # 某入口失败后暂停使用的秒数
_tencent_host_down_until = {}
_TENCENT_MINUTES = ("m1", "m5", "m15", "m30", "m60")
_TENCENT_SPAN_DAYS = {"day": 700, "week": 3650, "month": 18250}   # 每段 < 640 根


def _tencent_kline_call(path, param):
    """按顺序尝试三个入口；空响应或异常视为该入口被限流，冷却后换下一个。返回 (data, 实际成功的入口)。"""
    errors = []
    for host in TENCENT_KLINE_HOSTS:
        if _tencent_host_down_until.get(host, 0) > time.time():
            continue
        try:
            response = _v39_http(host + path, params={"param": param},
                                 headers={"Referer": "https://gu.qq.com/"}, timeout=(8, 20))
            payload = _v39_json(response) if response.text.strip() else {}
        except RuntimeError as exc:
            errors.append(f"{host}: {type(exc.__cause__ or exc).__name__}")
            _tencent_host_down_until[host] = time.time() + _TENCENT_HOST_COOLDOWN
            continue
        if not isinstance(payload, dict):    # 顶层变成数组 / 字符串：当作这个入口坏了，换下一个
            errors.append(f"{host}: 顶层是 {type(payload).__name__}，不是对象")
            _tencent_host_down_until[host] = time.time() + _TENCENT_HOST_COOLDOWN
            continue
        if payload.get("msg") == "param error":
            raise ValueError(f"腾讯 K 线参数错误（区间过长或代码不存在）: {param}")
        if isinstance(payload.get("data"), dict) and payload["data"]:
            return payload["data"], host
        errors.append(f"{host}: 空响应")
        _tencent_host_down_until[host] = time.time() + _TENCENT_HOST_COOLDOWN
    raise RuntimeError("腾讯 K 线三个入口均不可用（可能被限流，稍后重试）: " + "; ".join(errors))


@_v39_contract
def tencent_kline(code, period="day", adjust=None, start=None, end=None, count=320):
    """腾讯 K 线 — 日/周/月（默认前复权）与 1/5/15/30/60 分钟（不复权）。

    period: day / week / month / m1 / m5 / m15 / m30 / m60
    adjust: None=日周月默认 qfq、分钟默认不复权；可显式传 'qfq' / 'hfq' / ''（不复权）
    start/end: 仅日周月可用，'YYYY-MM-DD'；给了 start 会自动按段分页（单次最多 640 根）
    count: 不给 start 时取最近 count 根；日周月 ≤ 640，分钟 ≤ 320
    成交量单位：科创板（688/689）是股，其余是手；科创板以外，最近一个交易日的分钟量是整手、下一个交易日才回填成精确股数（见 §1.2 说明）。
    本接口**没有成交额**，需要成交额用 §1.3 通达信盘后包。
    不支持北交所：腾讯对北交所只返回最新 1 根日线，区间与分钟线为空（2026-09-20 实测），直接抛 ValueError。
    """
    period = str(period).lower()
    if get_prefix(code) == "bj":
        raise ValueError("腾讯 K 线不支持北交所（只返回最新 1 根日线、分钟线为空）；"
                         "北交所日线请用 §1.3 tdx_daily_package(date) 按交易日取")
    symbol = get_prefix(code) + norm_ticker(code)
    if period in _TENCENT_MINUTES:
        if adjust not in (None, ""):
            raise ValueError("分钟线只有不复权数据，adjust 请留空")
        if start or end:
            raise ValueError("分钟线只能取最近 count 根，不支持 start/end")
        if not 1 <= int(count) <= 320:
            raise ValueError("分钟线 count 范围 1–320")
        data, host = _tencent_kline_call("/appstock/app/kline/mkline", f"{symbol},{period},,{int(count)}")
        node = data.get(symbol)
        if not isinstance(node, dict) or not isinstance(node.get(period), list):
            raise RuntimeError(f"腾讯分钟线 {symbol} 的返回里没有 {period} 列表，格式可能已变")
        rows, seen = [], set()
        try:
            for item in node[period]:
                stamp = datetime.strptime(item[0], "%Y%m%d%H%M")
                if stamp in seen:
                    raise RuntimeError(f"腾讯分钟线 {symbol} 同一时刻 {stamp} 出现两次，结果不可信")
                seen.add(stamp)
                rows.append({"datetime": stamp.strftime("%Y-%m-%d %H:%M"),
                             "open": _v39_req_num(item[1], "open"), "high": _v39_req_num(item[3], "high"),
                             "low": _v39_req_num(item[4], "low"), "close": _v39_req_num(item[2], "close"),
                             "volume": _v39_req_num(item[5], "volume"),
                             # 第 8 个字段是换手率「基点」，÷100 才是百分数；它不是成交额。
                             "turnover_rate_pct": _v39_num(item[7]) / 100 if len(item) > 7
                             and _v39_num(item[7]) is not None else None})
        except (ValueError, TypeError, IndexError, KeyError) as exc:      # 源格式变了（行变短 / 变成对象），不是参数错
            raise RuntimeError(f"腾讯分钟线 {symbol} 行格式改变: {exc}") from exc
        if not rows:
            raise RuntimeError(f"腾讯分钟线 {symbol} {period} 返回 0 根")
        frame = _v39_frame(rows, "tencent", host + "/appstock/app/kline/mkline")
        frame.insert(0, "code", symbol)
        return frame

    if period not in _TENCENT_SPAN_DAYS:
        raise ValueError("period 只能是 day/week/month 或 m1/m5/m15/m30/m60")
    adjust = "qfq" if adjust is None else adjust
    if adjust not in ("qfq", "hfq", ""):
        raise ValueError("adjust 只能是 'qfq' / 'hfq' / ''")
    if start:
        first = datetime.strptime(_v39_date(start), "%Y-%m-%d").date()
        last = datetime.strptime(_v39_date(end), "%Y-%m-%d").date() if end else date.today()
        if first > last:
            raise ValueError("start 不能晚于 end")
        windows, cursor = [], first
        while cursor <= last:
            stop = min(cursor + timedelta(days=_TENCENT_SPAN_DAYS[period] - 1), last)
            windows.append((cursor.isoformat(), stop.isoformat(), 640))
            cursor = stop + timedelta(days=1)
    else:
        if end:
            raise ValueError("只给 end 时请同时给 start")
        if not 1 <= int(count) <= 640:
            raise ValueError("日周月 count 范围 1–640")
        windows = [("", "", int(count))]

    by_date, used_hosts = {}, []
    for s, e, n in windows:
        data, host = _tencent_kline_call("/appstock/app/fqkline/get",
                                         f"{symbol},{period},{s},{e},{n},{adjust}")
        if host not in used_hosts:
            used_hosts.append(host)
        node = data.get(symbol)
        # 有除权的标的返回 qfqday / hfqweek…；从未除权的标的（以及指数）只返回 day/week/month，
        # 此时复权价与原始价相同。只认其中一个 key 会静默丢掉另一类标的（#52 补充）。
        # 复权 key 在就只用它：它为空而 day 有数据时，拿 day 顶上就是把原始价标成复权价，直接抛错。
        # 空列表是正常的（上市前、长期停牌的区间，实测 688981 在 2019 年返回 day=[]）；
        # 连这两个 key 都没有说明返回格式变了，不能把这一段当成 0 根跳过。
        key = adjust + period
        if not isinstance(node, dict) or not isinstance(node.get(key, node.get(period)), list):
            raise RuntimeError(f"腾讯 K 线 {symbol} {s or '最近'}~{e or ''} 的返回里没有 {key} / {period}，"
                               "格式可能已变")
        items = node.get(key, node.get(period))
        if key != period and key in node and not items and node.get(period):
            raise RuntimeError(f"腾讯 K 线 {symbol} {s}~{e} 的 {key} 为空、{period} 却有数据，"
                               "不能拿原始价冒充复权价")
        try:
            for item in items:
                day = _v39_src_date(item[0])
                # 每段只接受段内日期（实测腾讯按 K 线日期过滤，周 / 月线也不越界）；
                # 越界说明拿到的是别的请求或缓存页，只按总区间过滤会把缺掉的几段静默吞掉
                if s and not s <= day <= e:
                    raise RuntimeError(f"腾讯 K 线 {symbol} 请求 {s}~{e} 却返回了 {day}，结果不可信")
                if day in by_date:          # 各段互不重叠，同一天出现两次只能是源数据有问题
                    raise RuntimeError(f"腾讯 K 线 {symbol} 日期 {day} 出现两次，结果不可信")
                # 必填数值走 _v39_req_num：float() 会把 true 读成 1.0、把 'nan' 放进结果
                by_date[day] = {"date": day, "open": _v39_req_num(item[1], "open"),
                                "high": _v39_req_num(item[3], "high"), "low": _v39_req_num(item[4], "low"),
                                "close": _v39_req_num(item[2], "close"), "volume": _v39_req_num(item[5], "volume")}
        except (ValueError, TypeError, IndexError, KeyError) as exc:      # 源格式变了（行变短 / 变成对象），不是参数错
            raise RuntimeError(f"腾讯 K 线 {symbol} 行格式改变: {exc}") from exc
    rows = [by_date[k] for k in sorted(by_date)]
    if start:
        rows = [r for r in rows if windows[0][0] <= r["date"] <= windows[-1][1]]
    if not rows:
        raise RuntimeError(f"腾讯 K 线 {symbol} {period} 在所给区间内 0 根（未上市/停牌区间/代码有误）")
    # 腾讯 qfq 是「逐次减去每股分红」的等差口径（茅台 2020-01-02：原始 1130.00，qfq 870.741，
    # 差额 259.259 正是此后累计分红），高分红股的早年价格会被减成负数（茅台 2015 年 -117.6）。
    # 负价不能拿去算收益率，直接拒绝；长区间请用 adjust='' 再按 §1.6 比例口径复权。
    if any(min(r["open"], r["high"], r["low"], r["close"]) <= 0 for r in rows):
        raise RuntimeError(f"腾讯 {adjust or '原始'} 价格出现 ≤0（等差复权口径的副作用）；"
                           "请改用 adjust='' 取不复权价，再用 §1.6 sina_adjust_factor + apply_adjust")
    # 分段请求可能落在不同入口，source_url 列出实际用到的全部入口
    frame = _v39_frame(rows, "tencent", " | ".join(h + "/appstock/app/fqkline/get" for h in used_hosts))
    frame.insert(0, "code", symbol)
    frame.insert(1, "adjust", adjust or "none")
    return frame
```
<!-- v39-tencent-kline:end -->

```python
day = tencent_kline("600519", start="2025-01-01")            # 前复权日线，自动分段
raw = tencent_kline("600519", adjust="", count=250)            # 不复权 → 可交给 §1.6 apply_adjust
m5 = tencent_kline("300750", period="m5", count=96)           # 最近 96 根 5 分钟线
idx = tencent_kline("sh000001", period="week", count=100)     # 指数（上证指数要写 sh 前缀）
```

### 1.3 通达信官网盘后包 — 某交易日全市场日线含成交额（V3.9.0 新增 · #52）

通达信官网每天发布的增量数据包（HTTP 下载约 2.7MB），一次拿到**沪深北全部证券**当日的昨收、开高低收、成交量（股）、
成交额（元）。它走 HTTP，和 §1.7 失效的 TCP 行情命令是两条路。适合收盘后全市场截面筛选、每日落库。
二进制布局参考 [jing2uo/tdx2db](https://github.com/jing2uo/tdx2db)（MIT），已与腾讯收盘价对拍。
非交易日、或当天包还没发布（通常收盘后数小时）抛 `ValueError`，不返回空表。

<!-- v39-tdx-package:start -->
```python
import io
import math
import re
import struct
import zipfile
import zlib

TDX_PACKAGE_URL = "https://www.tdx.com.cn/products/data/data/g4day/{ymd}.zip"
# 盘后包从这一天起带北交所文件（2026-09-20 二分实测：20220505 无、20220506 有）
TDX_BJ_FIRST_DAY = "20220506"
# 每个市场有收盘价的最少行数。2026-09-20 实测 2021-08-16 ~ 2026-09-18 共 11 个包的最小值：
# 沪 16202、深 3641（2022 年以前深市大部分代码当日无价）、京 87（2022-05-06），下限取明显低于最小值的整数
TDX_MIN_PRICED = {"sh": 10000, "sz": 3000, "bj": 50}


def _tdx_parse_package(content, ymd):
    """解析通达信每日增量包：每个市场一对 .cod（代码表，150 字节/条）+ .md1（行情块，512 字节/块）。
    布局参考 jing2uo/tdx2db（MIT）的 tdx/merge.go，已用 600519/000001/920000 与腾讯收盘价对拍。"""
    archive = zipfile.ZipFile(io.BytesIO(content))
    names = set(archive.namelist())
    rows = []
    for market in ("sh", "sz", "bj"):
        cod_name, md1_name = f"{market}{ymd[2:]}.cod", f"{market}{ymd[2:]}.md1"
        if (market == "bj" and ymd < TDX_BJ_FIRST_DAY
                and cod_name not in names and md1_name not in names):
            continue            # 这天之前的包还没有北交所文件；之后缺文件按格式改变报错
        if cod_name not in names or md1_name not in names:
            raise RuntimeError(f"通达信盘后包缺少 {cod_name}/{md1_name}，格式可能已变")
        cod, md1 = archive.read(cod_name), archive.read(md1_name)
        if len(cod) % 150 or len(md1) % 512:
            raise RuntimeError(f"{market} 代码表或行情块长度不是整块，文件可能被截断")
        if len(cod) // 150 != len(md1) // 512:
            raise RuntimeError(f"{market} 代码表 {len(cod) // 150} 条、行情块 {len(md1) // 512} 块，对不上")
        before, codes, seqs = len(rows), set(), set()
        for offset in range(0, len(cod), 150):
            record = cod[offset:offset + 150]
            # 11 个真实包（2021-08 ~ 2026-09）的代码全是 6 位 ASCII 数字；用 replace 解码会把坏字节变成 '\ufffd00000' 放行
            code = record[0:6].rstrip(b"\x00 ").decode("ascii", "replace")
            seq = struct.unpack("<H", record[32:34])[0]
            if not re.fullmatch(r"[0-9]{6}", code):
                raise RuntimeError(f"通达信盘后包 {market} 代码表出现非 6 位数字代码 {code!r}，格式可能已变")
            if code in codes or seq in seqs:
                raise RuntimeError(f"通达信盘后包 {market} 代码表有重复的代码 / 行情块序号（{code!r}, seq={seq}）")
            codes.add(code)
            seqs.add(seq)
            block = md1[seq * 512:(seq + 1) * 512]
            if len(block) != 512:
                raise RuntimeError(f"{market}{code} 行情块越界（seq={seq}）")
            prev_close = struct.unpack("<d", block[4:12])[0]
            open_, high, low, close = struct.unpack("<4d", block[12:44])
            amount = struct.unpack("<d", block[72:80])[0]
            # NaN 能绕过 close <= 0 被当成有价记录计入下限；11 个真实包里没有一个非有限值
            if not all(math.isfinite(v) for v in (prev_close, open_, high, low, close, amount)):
                raise RuntimeError(f"通达信盘后包 {market}{code} 行情块出现非有限数值，文件可能已损坏")
            if close <= 0:
                continue        # 880/881 等通达信自编板块指数当日无价，整块为 0，不是证券
            volume = struct.unpack("<Q", block[56:64])[0]
            raw_name = record[40:72].split(b"\x00")[0]
            try:                # replace 会把坏字节变成「�」当成正常名称返回（11 个真实包实测零替换字符）
                name = raw_name.decode("gbk").strip()
            except UnicodeDecodeError as exc:
                raise RuntimeError(f"通达信盘后包 {market}{code} 的名称不是 GBK，文件可能已损坏") from exc
            if not name:
                raise RuntimeError(f"通达信盘后包 {market}{code} 有价格却没有名称，文件可能已损坏")
            rows.append({"date": f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}", "market": market,
                         "code": code,
                         "name": name,
                         "prev_close": round(prev_close, 4), "open": round(open_, 4),
                         "high": round(high, 4), "low": round(low, 4),
                         "close": round(close, 4), "volume": volume,
                         "amount": round(amount, 2)})
        # 逐市场核对下限：只检查总行数会让沪深撑过门槛、北交所静默缺失
        if len(rows) - before < TDX_MIN_PRICED[market]:
            raise RuntimeError(f"通达信盘后包 {market} 市场只有 {len(rows) - before} 条有价记录"
                               f"（实测下限 {TDX_MIN_PRICED[market]}），文件可能残缺或格式已变")
    return rows


@_v39_contract
def tdx_daily_package(date):
    """通达信官网每日盘后包 — 某一交易日沪深北全部证券的日线（含成交额）。

    走 HTTP 下载（约 2.7MB），与 #52 失效的 TCP 行情命令是两条路。
    个股 volume 单位是「股」、amount 单位是「元」；指数等特殊代码的 volume 为通达信原值。
    非交易日或当日包尚未发布时官网返回 404，本函数抛 ValueError，不返回空表。
    历史包实测 2022-01-04、2023-01-03 可取，2021-01-04 已 404，未逐日验证；
    2022-05-06 之前的包没有北交所文件，只返回沪深，之后缺北交所文件会报错。
    某个市场有价记录少于 TDX_MIN_PRICED 的实测下限、代码不是 6 位数字或重复、行情块序号重复、
    代码表与行情块条数对不上、价格 / 成交额不是有限数，
    都按文件残缺抛 RuntimeError，不把部分市场当全市场返回。
    """
    ymd = _v39_date(date).replace("-", "")
    url = TDX_PACKAGE_URL.format(ymd=ymd)
    response = _v39_http(url, timeout=(10, 90), allow_status=(404,))
    if response.status_code == 404:
        raise ValueError(f"{date} 没有通达信盘后包：非交易日、当日包尚未发布（通常收盘后数小时），或早于官网保留范围（实测 2021-01-04 已没有）")
    if not response.content.startswith(b"PK"):
        raise RuntimeError("通达信盘后包不是 zip 文件，可能是错误页")
    try:
        rows = _tdx_parse_package(response.content, ymd)
    except (zipfile.BadZipFile, zlib.error, EOFError) as exc:      # 以 PK 开头但压缩包坏了 / 下载被截断
        raise RuntimeError(f"通达信盘后包 {url} 无法解压: {type(exc).__name__}: {exc}") from exc
    return _v39_frame(rows, "tdx", url)
```
<!-- v39-tdx-package:end -->

```python
snap = tdx_daily_package("2026-09-18")
print(len(snap), snap[snap.code == "600519"][["close", "volume", "amount"]])
```

### 1.4 腾讯逐笔成交 — 当日分笔明细（V3.10.0 新增 · 替代 §1.7 mootdx `transaction`）

§1.7 mootdx `transaction()` 2026-09 起返回空（#52）后的逐笔来源：腾讯行情页「成交明细」接口，一页 70 笔，逐页翻到空页为止，
全天 60–70 页、约 20–30 秒（复用连接；连接失败、等响应超时、429 / 5xx 自动重试）。先执行 Prerequisites 的 V3.9.0 共用 helper。

- **只有最近一个交易日**，没有历史；覆盖沪深个股（含创业板、科创板）与 ETF。北交所、指数没有，直接抛 `ValueError`。
- 是约 3 秒一笔的**分笔**（同一时刻撮合的多笔合并成一笔），不是交易所 Level-2 逐笔委托 / 逐笔成交。
  09:25 那一笔就是开盘集合竞价的撮合结果。
- `volume` 单位「手」（科创板也是手，和 §1.2 K 线不同：科创板按股成交、这里每笔取整成手，全天累加与真实股数有误差，成交越清淡越大：09-30 实测 688981 +0.013%、688001 −0.052%，成交清淡的 688184 +0.20%、688459 −0.16%）、`amount` 单位元；`side`：B = 主动买、S = 主动卖、M = 中性（集合竞价、盘后定价多为 M）。
- 收盘后 15:05–15:30 的盘后定价（固定价格）成交也在结果里（`time` 晚于 15:00:59 的行）；实测沪深主板、创业板、科创板、ETF 都有，
  不计入腾讯行情的当日成交额。
- **完整性核对：** 收盘后调用时，连续竞价段（≤ 15:00:59）的成交额合计要与腾讯行情快照的当日成交额相符，差超过 0.1% + 1000 元抛 `RuntimeError`
  （2026-09-22 实测 000001 / 600519 / 300750 / 688981 / 159915 / 000002 / 603286 相差 0–285 元）。
  盘中调用拿到的是截至取数时刻的逐笔，成交额还在变，不做这项核对，也不保证完整（翻页途中遇到空页就当作结束）。
- 腾讯偶尔缓存了盘后某一页的旧版本，会缺几笔盘后成交（实测 300750 缺 6 笔、159915 缺 7 笔，都在 15:14 以后）。
  连续竞价段缺号直接抛 `RuntimeError`，稍后重试；盘后段中间缺的序号记在 `frame.attrs["missing_seq"]`，末尾缺的从序号上看不出来。
- **`frame.attrs["complete"]`**：15:31 以后调用（看取数前那次快照的时刻），再用快照的盘后成交额（下标 58 的字段，万元）核对 15:00:59 以后的各笔，
  差不超过「笔数 + 1」元算对上（每笔金额取整到元）。
  `True` = 序号连续，连续竞价段和盘后定价的金额都对上；`False` = 盘后定价有缺笔（中间缺号，或末尾缺的金额超出容差），稍后重试；
  `None` = 没有缺号，但还在盘中、不到 15:31，或快照没有这个字段，没法核对。
  末尾缺的笔金额小时看不出来：低价 ETF 一笔 1–2 手只有几十元，落在容差里仍是 `True`（09-30 的 512170 盘后 46 笔、容差 47 元，缺一笔 1 手 35 元判不出）。
  2026-10-05 实测 10 只（沪深主板、创业板、科创板、ETF）09-30 的盘后各笔合计与该字段差 0–3 元。
- 开盘前（9:25 撮合前）调用可能拿不到上一交易日的逐笔。

<!-- v310-tencent-ticks:start -->
```python
import re
import time

TENCENT_TICK_URL = "https://stock.gtimg.cn/data/index.php"
TENCENT_QT_URL = "https://qt.gtimg.cn/q="
_TICK_MAX_PAGES = 300            # 一页 70 笔；2026-09-22 实测最活跃的票全天约 4800 笔 / 69 页
_TICK_SESSION_END = "15:00:59"   # 连续竞价 + 收盘集合竞价到此为止（科创板收盘那笔在 15:00:02），之后是盘后定价


def _tencent_qt_snapshot(symbol):
    """腾讯行情快照 → (交易日 'YYYY-MM-DD', 时刻 'HHMMSS', 当日成交额 元, 盘后定价成交额 元)。代码不存在抛 ValueError。
    盘后定价成交额是下标 58 的字段（万元、4 位小数）；字段没有或认不出时为 None，只是不做盘后核对。"""
    response = _v39_http(TENCENT_QT_URL + symbol, timeout=(5, 15), session=V39_RETRY_SESSION)
    text = response.content.decode("gbk", "replace")
    if "v_pv_none_match" in text:
        raise ValueError(f"腾讯没有 {symbol} 这个代码")
    match = re.search(rf'v_{symbol}="([^"]*)"', text)
    if not match:
        raise RuntimeError(f"腾讯行情快照 {symbol} 的返回里没有 v_{symbol} 变量，格式可能已变")
    fields = match.group(1).split("~")
    if len(fields) < 36 or not re.fullmatch(r"[0-9]{14}", fields[30]):
        raise RuntimeError(f"腾讯行情快照 {symbol} 字段数 {len(fields)} 或时间字段不对，格式可能已变")
    parts = fields[35].split("/")          # 「最新价/成交量/成交额(元)」；科创板的成交量是股、其余是手，所以只用成交额
    if len(parts) != 3:
        raise RuntimeError(f"腾讯行情快照 {symbol} 的价/量/额字段是 {fields[35]!r}，格式可能已变")
    after_hours = fields[58] if len(fields) > 58 else ""
    after_hours = round(float(after_hours) * 1e4, 2) if re.fullmatch(r"\d+(\.\d+)?", after_hours) else None
    return _v39_src_date(fields[30][:8]), fields[30][8:], _v39_req_num(parts[2], "成交额"), after_hours


def _tencent_tick_page(symbol, page):
    """第 page 页逐笔（0 起）→ 记录列表；翻过最后一页时腾讯返回空内容，返回 None。"""
    response = _v39_http(TENCENT_TICK_URL, params={"appn": "detail", "action": "data", "c": symbol, "p": page},
                         timeout=(5, 15), session=V39_RETRY_SESSION)
    text = response.content.decode("gbk", "replace").strip()
    if not text:
        return None
    match = re.fullmatch(rf'v_detail_data_{symbol}=\[(\d+),"([^"]*)"\];?', text)
    if not match or int(match.group(1)) != page:
        raise RuntimeError(f"腾讯逐笔 {symbol} 第 {page} 页不是预期格式: {text[:80]!r}")
    if not match.group(2):
        return None
    records = []
    try:
        for item in match.group(2).split("|"):
            seq, clock, price, change, volume, amount, side = item.split("/")
            if not re.fullmatch(r"\d\d:\d\d:\d\d", clock) or side not in ("B", "S", "M"):
                raise ValueError(item)
            records.append({"seq": int(seq), "time": clock, "price": _v39_req_num(price, "price"),
                            "change": _v39_req_num(change, "change"), "volume": _v39_req_num(volume, "volume"),
                            "amount": _v39_req_num(amount, "amount"), "side": side})
    except ValueError as exc:      # 字段数不对 / 序号不是整数 / 方向认不出：源格式变了，不是参数错
        raise RuntimeError(f"腾讯逐笔 {symbol} 第 {page} 页记录格式改变: {exc}") from exc
    return records


@_v39_contract
def tencent_ticks(code):
    """腾讯逐笔成交（分笔）— 最近一个交易日的全部成交明细，沪深个股与 ETF。

    一行一笔：date / code / time / seq（腾讯序号）/ price / change（较上一笔）/ volume（手）/ amount（元）/
    side（B 主动买 · S 主动卖 · M 中性）。约 3 秒一笔的分笔，不是 Level-2 逐笔。
    北交所、指数、代码不存在、当日没有成交抛 ValueError。收盘后调用会用行情快照的当日成交额核对连续竞价段，
    对不上抛 RuntimeError；盘后定价段腾讯偶尔缺几笔：中间缺的序号在 frame.attrs["missing_seq"]，
    15:31 以后再用快照的盘后成交额核对，结果在 frame.attrs["complete"]（True 对上 / False 有缺 / None 没法核对；
    低价 ETF 一两手的小额缺笔可能看不出）。
    """
    prefix, ticker = get_prefix(code), norm_ticker(code)
    if prefix == "bj":
        raise ValueError("腾讯逐笔不支持北交所（返回空）；北交所日线见 §1.3 tdx_daily_package")
    if (prefix, ticker[:3]) in (("sh", "000"), ("sz", "399")):
        raise ValueError(f"{prefix}{ticker} 是指数，没有逐笔成交")
    symbol = prefix + ticker
    day, clock, amount_before, after_hours_before = _tencent_qt_snapshot(symbol)
    if amount_before == 0:
        raise ValueError(f"{symbol} 在 {day} 没有成交（停牌、尚未开盘或集合竞价未撮合）")
    rows, missing = [], []
    for page in range(_TICK_MAX_PAGES):
        records = _tencent_tick_page(symbol, page)
        if records is None:
            break
        for r in records:
            expected = rows[-1]["seq"] + 1 if rows else 0
            if r["seq"] < expected or (rows and r["time"] < rows[-1]["time"]):
                raise RuntimeError(f"腾讯逐笔 {symbol} 序号或时间倒退（第 {page} 页 {r['seq']} {r['time']}），结果不可信")
            if r["seq"] > expected:
                if r["time"] <= _TICK_SESSION_END:
                    raise RuntimeError(f"腾讯逐笔 {symbol} 缺序号 {expected}–{r['seq'] - 1}（{r['time']} 之前，第 {page} 页），"
                                       "腾讯该页缓存不完整，稍后重试")
                missing.extend(range(expected, r["seq"]))
            rows.append(r)
        time.sleep(0.1)
    else:
        raise RuntimeError(f"腾讯逐笔 {symbol} 翻到第 {_TICK_MAX_PAGES} 页仍未结束，格式可能已变")
    if not rows:
        if clock < "092500":
            raise ValueError(f"{symbol} 集合竞价尚未撮合（{clock}），还没有逐笔")
        raise RuntimeError(f"{symbol} 在 {day} 成交 {amount_before:.0f} 元，腾讯逐笔却为空："
                           "开盘前腾讯可能已清空上一交易日的明细，否则是接口变了")
    day_after, clock_after, amount_after, after_hours_after = _tencent_qt_snapshot(symbol)
    if day_after != day:
        raise RuntimeError(f"取数期间交易日从 {day} 变成 {day_after}，请重试")
    session = sum(r["amount"] for r in rows if r["time"] <= _TICK_SESSION_END)
    # 两次快照成交额相同说明取数期间没有新成交（收盘后 / 午休 / 停牌），此时连续竞价段逐笔合计应与当日成交额相符
    if amount_after == amount_before and abs(session - amount_before) > amount_before * 0.001 + 1000:
        raise RuntimeError(f"腾讯逐笔 {symbol} 连续竞价段成交额 {session:.0f} 元，与行情快照 {amount_before:.0f} 元对不上，"
                           "逐笔可能不全")
    # 盘后定价 15:30 结束（深市最后一笔可能正好在 15:30:00）。取数前的快照已在 15:31 以后、两次快照一致时，
    # 15:00:59 以后各笔成交额合计应等于快照的盘后成交额（每笔取整到元，差不超过笔数 + 1 元）；
    # 中间缺号、末尾缺笔都会对不上，但末尾缺的金额小于容差（低价 ETF 一两手）时看不出。盘中 / 15:31 前没法核对，记 None。
    after_hours = [r["amount"] for r in rows if r["time"] > _TICK_SESSION_END]
    complete = None
    if missing:
        complete = False
    elif (amount_after == amount_before and after_hours_before is not None
          and after_hours_after == after_hours_before and clock >= "153100"):
        complete = abs(sum(after_hours) - after_hours_before) <= len(after_hours) + 1
    frame = _v39_frame(rows, "tencent", f"{TENCENT_TICK_URL}?appn=detail&action=data&c={symbol}",
                       ["time", "seq", "price", "change", "volume", "amount", "side"])
    frame.insert(0, "date", day)
    frame.insert(1, "code", symbol)
    frame.attrs["missing_seq"] = missing
    frame.attrs["complete"] = complete
    return frame
```
<!-- v310-tencent-ticks:end -->

```python
ticks = tencent_ticks("000001")                     # 平安银行最近一个交易日全部分笔
ticks.attrs["complete"]                             # 15:31 以后：True 对上 / False 盘后有缺笔；盘中为 None
auction = ticks[ticks.time < "09:30:00"]            # 开盘集合竞价撮合那一笔（科创板在 09:25:0x）
buy = ticks.loc[ticks.side == "B", "amount"].sum()  # 主动买入额
etf = tencent_ticks("510300")                       # ETF 同样可用
```

### 1.5 百度股市通 K线 — 带MA5/MA10/MA20（V3.0 新增）

**核心价值：** 返回时自带均线数据，无需本地计算。

```python
import requests

def baidu_kline_with_ma(code: str, start_time: str = "") -> dict:
    """百度股市通K线 — 独有能力: 返回时自带 ma5/ma10/ma20 均价"""
    url = "https://finance.pae.baidu.com/selfselect/getstockquotation"
    params = {
        "all": "1", "isIndex": "false", "isBk": "false", "isBlock": "false",
        "isFutures": "false", "isStock": "true", "newFormat": "1",
        "group": "quotation_kline_ab", "finClientType": "pc",
        "code": code, "start_time": start_time, "ktype": "1",
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/vnd.finance-web.v1+json",
        "Origin": "https://gushitong.baidu.com",
        "Referer": "https://gushitong.baidu.com/",
    }
    r = requests.get(url, params=params, headers=headers, timeout=10)
    d = r.json()
    result = d.get("Result", {})
    md = result.get("newMarketData", {})
    keys = md.get("keys", [])  # includes: ma5avgprice, ma10avgprice, ma20avgprice
    rows = md.get("marketData", "").split(";")
    return {"keys": keys, "rows": rows}

# 用法
data = baidu_kline_with_ma("600519")
print("字段:", data["keys"][:10])
print("最近5根K线:", data["rows"][-5:])
# keys 包含: time, open, close, high, low, volume, amount, ma5avgprice, ma10avgprice, ma20avgprice 等
```

### 1.6 新浪复权因子 — qfq / hfq（V3.7.0 新增）

**核心价值：** §1.7 `tdx_client().bars()`、§1.2 `tencent_kline(adjust='')`、§1.3 `tdx_daily_package()` 返回的是**不复权**数据，跨除权日直接比价必然出错。
本端点给出复权因子序列，一次 HTTP、约 1.8KB、零鉴权。

```python
import json
import re

import requests


def sina_adjust_factor(code: str, kind: str = "qfq") -> list:
    """新浪复权因子序列 — kind='qfq'(前复权) | 'hfq'(后复权)，按日期倒序（最新在前）"""
    if kind not in ("qfq", "hfq"):
        raise ValueError(f"kind 只能是 'qfq' 或 'hfq'，收到 {kind!r}")
    # 数字位用 norm_ticker() 剥掉前后缀（否则 "sz000016" 会拼成 "szsz000016" ——
    # zfill(6) 对 8 字符输入不做任何事）。
    raw = str(code).strip()
    digits = norm_ticker(raw)
    # 市场：**显式写法优先**——前缀或 `.SH` 后缀直接采信（V3.7.1 起 get_prefix() 也认后缀，
    # 本地显式匹配保留，语义不变）。都没写显式市场时，才用 get_prefix() 按号段推断
    # （它已处理 92 必须先于 9x）。
    m = re.match(r"^(sh|sz|bj)", raw, re.I) or re.search(r"\.(sh|sz|bj|xshg|xshe)$", raw, re.I)
    prefix = {"xshg": "sh", "xshe": "sz"}.get(m.group(1).lower(), m.group(1).lower()) if m else get_prefix(digits)
    symbol = f"{prefix}{digits}"
    url = f"https://finance.sina.com.cn/realstock/company/{symbol}/{kind}.js"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0",
                                   "Referer": "https://finance.sina.com.cn/"}, timeout=10)
    r.raise_for_status()
    # 🔴 响应形如 `var sh600519qfq={...}` 且**末尾挂着 /* base64 */ 注释块**，
    #    不能用 $ 锚定正则。从第一个 { 起用 raw_decode，让解析器自己在 JSON 结束处停下。
    text = r.text
    brace = text.find("{")
    if brace < 0:
        raise RuntimeError(f"新浪复权因子响应无 JSON（{symbol}/{kind}）: {text[:120]}")
    try:
        data, _ = json.JSONDecoder().raw_decode(text[brace:])
    except json.JSONDecodeError as e:
        raise RuntimeError(f"新浪复权因子 JSON 解析失败（{symbol}/{kind}）: {e}") from e
    return [{"date": it["d"], "factor": float(it["f"])} for it in data.get("data", [])]


def apply_adjust(bars, factors: list, kind: str = "qfq",
                 price_keys=("open", "high", "low", "close")):
    """把复权因子套到不复权 K 线上。

    `bars` 接受两种形态：
      - **§1.7 `tdx_client().bars()` 的 DataFrame**（日期列名是 `datetime`）或 §1.2 `tencent_kline(adjust='')` 的 DataFrame（`date` 列）→ 返回 DataFrame
      - list[dict]（需含 `date` 键）→ 返回 list[dict]

    🔴 **qfq 与 hfq 的运算方向相反，必须传对 kind**：
      - `qfq`（前复权）因子是**除数**：`前复权价 = 不复权价 ÷ factor`
      - `hfq`（后复权）因子是**乘数**：`后复权价 = 不复权价 × factor`
    传错方向不会报错，只会把历史价格放大/缩小几倍（见下方实测对照表）。

    因子表是「生效日 → 因子」的阶梯，每根 K 线取**不晚于它**的最近一个因子。
    """
    if kind not in ("qfq", "hfq"):
        raise ValueError(f"kind 只能是 'qfq' 或 'hfq'，收到 {kind!r}")
    # 🔴 因子为空时绝不能「原样返回」—— 那会把不复权价当成复权价交出去，
    #    调用方拿到的数字看着正常却是错的（新浪对不支持的标的就返回空 data）。
    if not factors:
        raise ValueError(
            "复权因子列表为空，无法复权。请先确认 sina_adjust_factor() 是否取到数据"
            "（新浪对不支持的标的会返回空 data），不要用未复权价继续计算。"
        )

    is_df = hasattr(bars, "columns") and hasattr(bars, "to_dict")
    if is_df:
        # mootdx bars() 的日期列叫 datetime，且可能带时分秒，统一截成 YYYY-MM-DD
        date_col = next((c for c in ("date", "datetime") if c in bars.columns), None)
        if date_col is None:
            raise ValueError(f"DataFrame 需含 date 或 datetime 列，实际列={list(bars.columns)}")
        rows = bars.to_dict("records")
        for r in rows:
            r["date"] = str(r[date_col])[:10]
    else:
        rows = [dict(b) for b in bars]
        for r in rows:
            if "date" not in r:
                raise ValueError(f"每根 K 线需含 'date' 键，实际键={sorted(r)}")
            r["date"] = str(r["date"])[:10]

    fac = sorted(factors, key=lambda x: x["date"])
    out, i, cur = [], 0, None
    for bar in sorted(rows, key=lambda b: b["date"]):
        while i < len(fac) and fac[i]["date"] <= bar["date"]:
            cur = fac[i]["factor"]
            i += 1
        # 🔴 早于最早因子日的 K 线不能原样放行 —— 那会让一份结果里混着「已复权」和
        #    「未复权」两种价格且无从分辨。新浪的因子表通常带 1900-01-01 哨兵
        #    （实测 600519/000001/300750/688981/000004/601398 六只均是），
        #    真出现未覆盖行，说明因子表异常，必须显式失败。
        if cur is None:
            raise RuntimeError(
                f"K 线日期 {bar['date']} 早于因子序列最早日 {fac[0]['date']}，"
                "无法复权；不返回未复权价以免与已复权行混淆。"
            )
        if cur == 0:
            raise RuntimeError(f"复权因子为 0（{bar['date']}），无法换算")
        nb = dict(bar)
        for k in price_keys:
            if k in nb and nb[k] is not None:
                v = float(nb[k])
                nb[k] = round(v / cur if kind == "qfq" else v * cur, 4)
        nb["adj_factor"] = cur
        out.append(nb)
    if is_df:
        import pandas as pd
        res = pd.DataFrame(out)
        # mootdx 的 bars() 带 DatetimeIndex，重建 DataFrame 会退化成 RangeIndex，
        # 下游按时间切片 / resample / 时间对齐 join 都会失效。按排序后的顺序还原索引。
        if getattr(bars, "index", None) is not None and not isinstance(
            bars.index, pd.RangeIndex
        ):
            order = sorted(range(len(bars)), key=lambda n: str(bars.iloc[n][date_col])[:10])
            res.index = bars.index[order]
            res.index.name = bars.index.name
        return res
    return out


# 用法
qfq = sina_adjust_factor("600519", "qfq")
hfq = sina_adjust_factor("600519", "hfq")
print(len(qfq), "条 | 最新", qfq[0], "| 最早", qfq[-1])
# 实测 2026-08-19：33 条
#   qfq 最新 {'date': '2026-06-26', 'factor': 1.0}          ← 前复权以最新为基准
#   hfq 最早 {'date': '1900-01-01', 'factor': 1.0}          ← 后复权以最早为基准

bars = [{"date": "2015-01-05", "close": 202.52}]         # 茅台当日不复权收盘价
print(apply_adjust(bars, qfq, kind="qfq"))                # → 143.46（前复权，除法）
print(apply_adjust(bars, hfq, kind="hfq"))                # → 1274.28（后复权，乘法）
```

**方向实测对照（2026-08-19，以 baostock `adjustflag` 为基准交叉验证）**

| 日期 | 不复权 | baostock 前复权 | `raw × qfq` | `raw ÷ qfq` |
|------|--------|----------------|-------------|-------------|
| 2015-01-05 | 202.52 | **143.46** | 285.90 ❌ | **143.46** ✅ |
| 2026-08-14 | 1341.99 | 1341.99 | 1341.99 ✅ | 1341.99 ✅ |

> `qfq` 因子恒 ≥ 1 且越往历史越大，**乘上去会把历史价格放大**，必须做除法。
> 2026 那行两种算法都对，是因为最新日因子恰为 1.0 —— **只用最近日期做验证会漏掉这个 bug**。
>
> ⚠️ **hfq 的基准与 baostock 不同**：新浪 `raw × hfq` 与 baostock 后复权价差一个**恒定倍数**
> （实测 1.1582，2015 与 2026 两点一致）。后复权序列整体缩放不影响收益率与形态，
> 但**不要把新浪后复权价与其它源的后复权价直接比数值**。

> ⚠️ **北交所无复权因子**：实测 `bj920982` 返回 **404**（新浪未提供北交所的 qfq/hfq 文件），
> 本函数会抛 `HTTPError`。北交所标的请改用 §1.3 通达信盘后包的不复权日线，并自行按分红送转推导。
>
> **自检口径（实测 2026-08-19 校准）：**
> - `qfq` 序列**最新**一条因子恒为 `1.0`；`hfq` 序列**最早**一条恒为 `1.0`。
> - 同一日期上 **`qfq(d) × hfq(d)` 恒等于一个常数**（该标的全期总复权系数，茅台实测 `8.882513`）。
>   ⚠️ 两者**不是倒数**（乘积不为 1），比值 `hfq/qfq` 也**不恒定**（茅台 33 个日期有 32 种取值）——
>   两个基准不同的归一化序列，只有乘积守恒。
> 不满足以上任一条，说明响应被截断或标的代码写错。

### 1.7 mootdx — K线 + 五档盘口 + 逐笔成交（⚠️ 2026-09 起行情命令失效，留档）

TCP 二进制协议，连通达信服务器(7709)，无需注册，不封IP。

> **⚠️ 2026-09 起本节普遍取不到数（#52）：** 通达信公开服务器 TCP 仍可达，但 `bars` / `quotes` / `transaction`
> 返回 0 行（2026-09-20 逐台实测内置 10 台，全部如此）；`tdx_client()` 会在约 1 分钟测速后抛出带指引的 RuntimeError。
> 替代：**K 线 → §1.2 `tencent_kline()`**（沪深日周月前/后复权 + 1~60 分钟）或 **§1.3 `tdx_daily_package()`**（沪深北全市场某日含成交额，北交所日线只能走这里）；
> **实时价 / 五档 → §1.1 腾讯**；**逐笔 → §1.4 `tencent_ticks()`**（只有当日）。财务与 F10（§6.1 / §6.2 / §7.2）不受影响。以下代码保留，服务器恢复后可照常使用。

```python
from mootdx.quotes import Quotes

client = tdx_client()  # 见 Prerequisites 的 tdx_client() helper（规避 0.11.x BESTIP bug；等价 Quotes.factory(market='std')）

# === K线数据 ===
# ⚠️ 参数名是 frequency（不是 category！传 category 会被 **kwargs 静默吞掉，
#    永远退化成默认 frequency=9 日线，拿不到分钟数据）。
# mootdx 0.11.7 实测频率值表：
#   0=5分钟  1=15分钟  2=30分钟  3=60分钟(1小时)  4=日线  5=周线  6=月线
#   8=1分钟  9=日线(默认)  10=季线  11=年线        （7=1分钟除权口径,少用）
klines = client.bars(symbol='688017', frequency=9, offset=10)    # 日线
min1   = client.bars(symbol='688017', frequency=8, offset=240)   # 1分钟（一个交易日≈240根）
min5   = client.bars(symbol='688017', frequency=0, offset=48)    # 5分钟
# 返回: open, close, high, low, vol, amount, datetime
# ⚠️ 复权：bars 返回【不复权】原始价（通达信原始数据，无 adjust 参数）。
#    跨除权除息日做估值/回测前需自行复权，或改用带前复权的日K数据源（腾讯财经）。

# === 实时报价 ===
quotes = client.quotes(symbol=['688017', '300476'])
# 返回 46 个字段:
#   price(现价), open, high, low, last_close(昨收)
#   bid1~bid5, ask1~ask5, bid_vol1~bid_vol5, ask_vol1~ask_vol5
#   vol(成交量), amount(成交额), servertime

# === 逐笔成交（非交易时间返回空）===
trades = client.transaction(symbol='688017', date='20260502')
# 返回: time, price, vol, num, buyorsell(0买/1卖/2中性)
```

**mootdx 不提供 PE / PB / 市值 / 换手率 / 涨跌停价** — 这些走腾讯财经。

---

## Layer 2: 研报层

### 2.1 东财研报 API — 研报列表 + PDF下载（主力）

A级接口（公开JSON API），reportapi.eastmoney.com，免费无key。

```python
import requests
import re
import time
from datetime import date, timedelta   # 注意用 date/timedelta，不要 import datetime 模块：
                                       # 本 SKILL 多处有 `from datetime import datetime`，会把模块名遮蔽掉
from pathlib import Path
from typing import Optional            # 3.9 兼容：不能写 `str | None`（那是 3.10+ 语法）

REPORT_API = "https://reportapi.eastmoney.com/report/list"
PDF_TPL = "https://pdf.dfcfw.com/pdf/H3_{info_code}_1.pdf"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

def eastmoney_reports(code: str, max_pages: int = 5) -> list[dict]:
    """拉取指定股票的研报列表。

    code 支持 600519 / SH600519 / 600519.SH 等写法（内部归一化为纯 6 位）。
    ⚠️ reportapi 只认纯 6 位数字：传 "SH600519" 会返回 hits=0，
       看起来像「这只票没研报」，实际是格式没归一化——务必先过 norm_ticker()。
    返回 [] 仅表示东财确无该标的研报覆盖（格式错误已在上游抛 ValueError）。
    """
    code = norm_ticker(code, stock_only=True)   # 格式错/显式指数码直接抛错，不静默返回 []
    all_records = []
    for page in range(1, max_pages + 1):
        params = {
            "industryCode": "*", "pageSize": "100", "industry": "*",
            "rating": "*", "ratingChange": "*",
            "beginTime": "2000-01-01", "endTime": "2030-01-01",
            "pageNo": str(page), "fields": "", "qType": "0",
            "orgCode": "", "code": code, "rcode": "",
            "p": str(page), "pageNum": str(page), "pageNumber": str(page),
        }
        r = em_get(REPORT_API, params=params,
                   headers={"Referer": "https://data.eastmoney.com/"}, timeout=30)  # 已内置限流
        d = r.json()
        rows = d.get("data") or []
        if not rows:
            break
        all_records.extend(rows)
        if page >= (d.get("TotalPage", 1) or 1):
            break
    # 正向识别「查无结果」的真实原因，不把废码静默当成「无研报覆盖」
    if not all_records and code[:2] in ("43", "83", "87"):
        raise ValueError(
            f"{code} 属北交所老号段（43/83/87），东财研报库已不再按老码索引。"
            f"北交所存量标的已基本迁至 920xxx（如 832982→920982）；"
            f"请按股票名称反查现行 920 代码后重试。详见「北交所老号段」警告。"
        )
    return all_records

def download_pdf(record: dict, target_dir: str = "./reports") -> Optional[str]:
    """下载单份研报PDF，返回保存路径或None"""
    info_code = record.get("infoCode", "")
    if not info_code:
        return None
    date = (record.get("publishDate") or "")[:10]
    org = re.sub(r'[\\/:*?"<>|]', "_", record.get("orgSName") or "未知")[:40]
    title = re.sub(r'[\\/:*?"<>|]', "_", record.get("title", ""))[:80]
    fname = f"{date}_{org}_{title}.pdf"
    target = Path(target_dir) / fname
    if target.exists():
        return str(target)
    url = PDF_TPL.format(info_code=info_code)
    r = em_get(url, headers={"Referer": "https://data.eastmoney.com/"}, timeout=60)
    if r.status_code == 200 and len(r.content) >= 1024:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(r.content)
        return str(target)
    return None

# 用法
reports = eastmoney_reports("688017")
print(f"共 {len(reports)} 篇研报")
for r in reports[:5]:
    print(f"  {r.get('publishDate','')[:10]} | {r.get('orgSName')} | {r.get('title','')[:60]}")
```

#### 研报 record 关键字段

| 字段 | 含义 |
|------|------|
| title | 研报标题 |
| publishDate | 发布日期 |
| orgSName | 机构简称 |
| infoCode | 用于拼 PDF URL |
| predictThisYearEps | 今年EPS预测 |
| predictNextYearEps | 明年EPS预测 |
| predictNextTwoYearEps | 后年EPS预测 |
| emRatingName | 评级(买入/增持/...) |
| indvInduName | 行业分类 |

#### 行业研报列表（qType=1）

与个股研报**同一端点**（`reportapi.eastmoney.com/report/list`），仅 `qType` 不同：`qType=0` 个股研报，`qType=1` 行业研报。返回 record 可直接喂给上面的 `download_pdf()`（PDF 模板通用）。

```python
from datetime import date, timedelta   # 本块单独拷贝也能跑；勿写成 import datetime（会被 §3+ 的
                                       # `from datetime import datetime` 遮蔽掉模块名）

def eastmoney_industry_reports(industry_code: str = "*", max_pages: int = 5,
                               begin: str = "") -> list[dict]:
    """拉取行业研报列表（qType=1）。
    industry_code="*" = 全行业；传东财行业码（如 "1238"=IT服务Ⅱ）= 单行业。
    行业名 / 行业码在每条 record 的 industryName / industryCode 字段。
    begin 留空 = 近两年（相对今天算，避免硬编码日期越用越旧）。"""
    if not begin:
        begin = (date.today() - timedelta(days=730)).isoformat()
    all_records = []
    for page in range(1, max_pages + 1):
        params = {
            "industryCode": industry_code, "pageSize": "100", "industry": "*",
            "rating": "*", "ratingChange": "*",
            "beginTime": begin, "endTime": "2030-01-01",
            "pageNo": str(page), "fields": "", "qType": "1",
        }
        r = em_get(REPORT_API, params=params,
                   headers={"Referer": "https://data.eastmoney.com/"}, timeout=30)  # 已内置限流
        d = r.json()
        rows = d.get("data") or []
        if not rows:
            break
        all_records.extend(rows)
        if page >= (d.get("TotalPage", 1) or 1):
            break
    return all_records

# 用法
# 1) 全行业最新研报
reports = eastmoney_industry_reports("*", max_pages=2)
print(f"共 {len(reports)} 篇行业研报")
for r in reports[:5]:
    print(f"  {r.get('publishDate','')[:10]} | {r.get('industryName')} | {r.get('orgSName')} | {r.get('title','')[:50]}")

# 2) 单行业（IT服务Ⅱ，行业码 1238）+ 下载首篇 PDF（复用 2.1 的 download_pdf）
it = eastmoney_industry_reports("1238", max_pages=1)
if it:
    download_pdf(it[0])
```

行业研报特有/常用字段（其余字段同 2.1 个股研报）：

| 字段 | 含义 |
|------|------|
| industryName | 行业名称（如 IT服务Ⅱ、风电设备、光伏设备） |
| industryCode | 东财行业代码（用于 `industry_code` 精确过滤） |
| emRatingName | 行业评级（买入/增持/中性/...） |
| reportType | 报告类型 |
| attachPages / attachSize | PDF 页数 / 大小(KB) |
| infoCode | 喂给 `download_pdf()` 拼 PDF URL |

> **行业码怎么拿：** 东财行业码不是通用记忆码，没有公开的码表端点（`bxpa` 等已 404）。常用做法：先用 `industry_code="*"` 拉一批，从结果的 `industryName`/`industryCode` 找到目标行业的码，再用该码精确过滤。

### 2.2 同花顺一致预期EPS（直连 basic.10jqka.com.cn）

```python
import requests
import pandas as pd
from io import StringIO

def ths_eps_forecast(code: str) -> pd.DataFrame:
    """
    同花顺机构一致预期EPS。
    直连 basic.10jqka.com.cn，解析HTML表格。
    code 支持 688017 / SH688017 / 688017.SH 等写法（内部归一化为纯 6 位）。
    返回 DataFrame: 年度, 预测机构数, 最小值, 均值, 最大值
    "均值" = 机构一致预期EPS
    """
    code = norm_ticker(code, stock_only=True)   # URL 路径只认纯 6 位，带前缀会 404 到空表
    url = f"https://basic.10jqka.com.cn/new/{code}/worth.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://basic.10jqka.com.cn/",
    }
    r = requests.get(url, headers=headers, timeout=15)
    r.encoding = "gbk"
    dfs = pd.read_html(StringIO(r.text))
    # 找含"每股收益"的表格
    for df in dfs:
        cols = [str(c) for c in df.columns]
        if any("每股收益" in c or "均值" in c for c in cols):
            return df
    # fallback: 返回第一个表
    return dfs[0] if dfs else pd.DataFrame()

# 用法
df = ths_eps_forecast("688017")
print(df)
# "预测机构数" < 3 的要谨慎
```

### 2.3 iwencai — NL语义搜索研报（唯一能力）

需要 API Key + X-Claw Headers（SkillHub 2.0 强制要求）。

```python
import os
import json
import secrets
import requests

IWENCAI_BASE = os.environ.get("IWENCAI_BASE_URL", "https://openapi.iwencai.com")
IWENCAI_KEY = os.environ.get("IWENCAI_API_KEY", "")

def _claw_headers(call_type: str = "normal") -> dict:
    """SkillHub 2.0 必须的 X-Claw 鉴权头"""
    return {
        "X-Claw-Call-Type": call_type,
        "X-Claw-Skill-Id": "report-search",
        "X-Claw-Skill-Version": "2.0.0",
        "X-Claw-Plugin-Id": "none",
        "X-Claw-Plugin-Version": "none",
        "X-Claw-Trace-Id": secrets.token_hex(32),
    }

def iwencai_search(query: str, channel: str = "report", size: int = 50) -> list[dict]:
    """
    iwencai 语义搜索。
    channel: "report"(研报) / "announcement"(公告) / "news"(新闻)
    size: 默认10, 实测可调到50（隐藏参数）
    """
    headers = {
        "Authorization": f"Bearer {IWENCAI_KEY}",
        "Content-Type": "application/json",
        **_claw_headers(),
    }
    payload = {
        "channels": [channel],
        "app_id": "AIME_SKILL",
        "query": query,
        "size": size,
    }
    r = requests.post(
        f"{IWENCAI_BASE}/v1/comprehensive/search",
        json=payload, headers=headers, timeout=30,
    )
    if r.status_code != 200:
        raise RuntimeError(f"iwencai HTTP {r.status_code}: {r.text[:200]}")
    data = r.json()
    if data.get("status_code", 0) != 0:
        raise RuntimeError(f"iwencai error: {data.get('status_msg', '')}")
    return data.get("data") or []

def iwencai_query(query: str, page: int = 1, limit: int = 50) -> list[dict]:
    """
    iwencai NL数据查询（结构化字段）。
    例: "贵州茅台 ROE" → DataFrame-like rows
    """
    headers = {
        "Authorization": f"Bearer {IWENCAI_KEY}",
        "Content-Type": "application/json",
        **_claw_headers(),
    }
    payload = {
        "query": query,
        "page": str(page),
        "limit": str(limit),
        "is_cache": "1",
        "expand_index": "true",
    }
    r = requests.post(
        f"{IWENCAI_BASE}/v1/query2data",
        json=payload, headers=headers, timeout=30,
    )
    if r.status_code != 200:
        raise RuntimeError(f"iwencai HTTP {r.status_code}: {r.text[:200]}")
    data = r.json()
    if data.get("status_code", 0) != 0:
        raise RuntimeError(f"iwencai error: {data.get('status_msg', '')}")
    return data.get("datas") or []

def dedup_articles(articles: list[dict]) -> list[dict]:
    """同一uid仅保留score最高的段落"""
    best = {}
    for a in articles:
        uid = a.get("uid", "") or f"{a.get('title','')}|{a.get('publish_date','')}"
        score = float(a.get("score", 0))
        if uid not in best or score > float(best[uid].get("score", 0)):
            best[uid] = a
    return sorted(best.values(), key=lambda x: x.get("publish_date", ""), reverse=True)

# 用法: NL语义搜索研报
articles = iwencai_search("人形机器人 行星滚柱丝杠 2026", channel="report", size=50)
articles = dedup_articles(articles)
for a in articles[:5]:
    extra = a.get("extra") or {}
    if isinstance(extra, str):
        extra = json.loads(extra)
    print(f"{a.get('publish_date','')[:10]} | {extra.get('organization','')} | {a.get('title','')[:60]}")
```

**iwencai 的唯一价值：** NL 主题搜索。"人形机器人 行星滚柱丝杠" 这种跨主题检索只有 iwencai 能做。按标的搜研报走东财 reportapi 更稳定。

### 2.4 新浪研报列表 — 研报第二来源（V3.9.0 新增 · #53）

东财研报（§2.1）之外的独立来源：标题、研报类型、日期、机构、研究员与详情页链接。**不含评级与目标价**（需要这些用 §2.1）。
新浪对连续请求会返回假的「没有找到相关内容」空页（HTTP 200，和真的没有研报一模一样），
本函数强制两次请求间隔 6 秒，遇到空页再等一次重试，批量翻页会比较慢。

<!-- v39-sina-reports:start -->
```python
import re
import time
import html as _html

SINA_REPORT_URL = "https://vip.stock.finance.sina.com.cn/q/go.php/vReport_List/kind/{kind}/index.phtml"
_SINA_REPORT_ROW = re.compile(
    r"<tr>\s*<td>\d+</td>\s*<td class=\"tal f14\">\s*<a[^>]*?title=\"([^\"]*)\"[^>]*?"
    r"href=\"([^\"]*?/rptid/(\d+)/[^\"]*)\"[^>]*>.*?</a>\s*</td>\s*"
    r"<td>([^<]*)</td>\s*<td>([^<]*)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>", re.S)


# 实测（2026-09-20）：个股研报搜索两次请求间隔 1 秒时，第二次起返回「没有找到相关内容..」
# 空页（HTTP 200，与真的没有研报长得一样）；间隔 ≥5 秒恢复正常。因此强制最小间隔，
# 并对空页等待后重试一次，仍为空才当作「该股确实没有」。
SINA_REPORT_MIN_INTERVAL = 6.0
_sina_report_last = [0.0]


def _sina_report_page(url, params):
    for attempt in range(2):
        wait = SINA_REPORT_MIN_INTERVAL - (time.time() - _sina_report_last[0])
        if wait > 0:
            time.sleep(wait)
        try:
            response = _v39_http(url, params=params,
                                 headers={"Referer": "https://finance.sina.com.cn/"})
        finally:
            _sina_report_last[0] = time.time()
        text = response.content.decode("gbk", "replace")
        if "没有找到相关内容" not in text:
            return response, text
    return response, text


def _sina_text(fragment):
    return _html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


@_v39_contract
def sina_research_reports(code=None, page=1):
    """新浪研报列表 — 研报标题/类型/日期/机构/研究员（#53 的第二来源）。

    code=None 返回全市场最新；给代码则只看该股。每页约 40 条，page 从 1 开始。
    只给列表与详情页链接，不含评级与目标价（需要这些用 §2.1 东财）。
    新浪对连续请求会返回假的「没有找到」空页，本函数内置 6 秒最小间隔，批量翻页会比较慢。
    """
    if int(page) < 1:
        raise ValueError("page 从 1 开始")
    if code is None:
        url = SINA_REPORT_URL.format(kind="lastest")
        params = {"p": int(page)}
    else:
        url = SINA_REPORT_URL.format(kind="search")
        symbol = norm_ticker(code, stock_only=True)
        # 北交所必须带 bj 前缀：只给 6 位数字时新浪返回「没有找到」空页（2026-09-20 实测 920982）
        if get_prefix(code) == "bj":
            symbol = "bj" + symbol
        params = {"symbol": symbol, "t1": "all", "p": int(page)}
    response, text = _sina_report_page(url, params)
    if "tb_01" not in text or "研究员" not in text:
        raise RuntimeError("新浪研报页面结构改变（找不到研报表格）")
    rows = []
    for title, href, rptid, kind, day, org, author in _SINA_REPORT_ROW.findall(text):
        rows.append({"date": _v39_src_date(day.strip()), "title": _html.unescape(title).strip(),
                     "type": kind.strip(), "org": _sina_text(org), "author": _sina_text(author),
                     "report_id": rptid,
                     "url": ("https:" + href) if href.startswith("//") else href})
    # 每页序号都从 1 编起（2026-09-20 实测第 2、3 页也是 1…40）；带序号的行必须全部解析出来。
    # 0 行只有页面写着「没有找到相关内容」（翻过末页 / 该股没有研报）才算真的没有
    numbered = len(re.findall(r"<tr>\s*<td>\d+</td>", text))
    if len(rows) != numbered or (not rows and "没有找到相关内容" not in text):
        raise RuntimeError(f"新浪研报表格有 {numbered} 行带序号、解析出 {len(rows)} 条，行结构可能已变")
    return _v39_frame(rows, "sina", response.url,
                      ["date", "title", "type", "org", "author", "report_id", "url"])
```
<!-- v39-sina-reports:end -->

```python
latest = sina_research_reports()                  # 全市场最新一页（约 40 条）
moutai = sina_research_reports("600519", page=1)  # 只看某只股票
```

---

## Layer 3: 信号层

### 3.1 同花顺热点 — 当日强势股 + 题材归因 reason tags（独家）

**核心价值：** 不只告诉你"哪些走强"，还告诉你**"为什么走强"** —— 同花顺编辑部人工运营的题材标签。

```python
import requests
import pandas as pd

def ths_hot_reason(date: str = None) -> pd.DataFrame:
    """
    同花顺当日强势股归因。
    date: 'YYYY-MM-DD' 格式，None=今天
    返回 DataFrame，含每只股票的题材标签 (reason)。

    实测: 73ms 拿到 ~125 只 + 完整字段
    """
    from datetime import date as _date
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

    # 字段重命名（中文友好）
    rename_map = {
        "name": "名称", "code": "代码", "reason": "题材归因",
        "close": "收盘价", "zhangdie": "涨跌额", "zhangfu": "涨幅%",
        "huanshou": "换手率%", "chengjiaoe": "成交额",
        "chengjiaoliang": "成交量", "ddejingliang": "大单净量",
        "market": "市场",
    }
    df = df.rename(columns=rename_map)
    return df

# 用法
df = ths_hot_reason("2026-05-09")
print(f"当日强势股: {len(df)} 只")
print(df[["代码", "名称", "涨幅%", "题材归因"]].head(10))
```

#### 同花顺热点字段速查

| 原字段 | 中文 | 说明 |
|---|---|---|
| code | 代码 | 6 位股票代码 |
| name | 名称 | 简称 |
| **reason** | **题材归因** | **核心字段，人工运营 tags，如"算力租赁+Token工厂+AI政务"** |
| zhangfu | 涨幅% | 当日涨幅 |
| huanshou | 换手率% | 当日换手 |
| chengjiaoe | 成交额 | 元 |
| chengjiaoliang | 成交量 | 股 |
| ddejingliang | 大单净量 | 主力净流入指标 |
| close | 收盘价 | 元 |
| zhangdie | 涨跌额 | 元 |
| market | 市场 | 沪/深/北 |

### 3.2 同花顺北向资金 — hsgtApi 实时分钟流向 + 本地自缓存历史

> **⚠️ 深股通实时流向近期不可靠（2026-07 实测）：** 沪股通(hgt)分钟序列完整，但深股通(sgt)
> 常只回传零星几个点、末值量级异常。根因是北向自 2024-08 起收紧盘中实时披露，非本代码问题。
> 结论：**hgt 可用于当日情绪，sgt 仅供参考**；要权威北向数据用 HKEX 官方日统计
> （`hkex.com.hk/chi/csm/DailyStat/data_tab_daily_YYYYMMDDc.js`，见文末「备用源速查」）。

> **已知行业性问题：** eastmoney 全系北向数据自 2024-08 后净买额字段返回 NaN/0，属上游断供。已改为**本地 CSV 自缓存模式**——每次拉实时数据后自动写入本地 CSV，历史越跑越丰富。

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

# === 自缓存辅助函数 ===

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
    """读取最近 N 天北向历史"""
    path = _northbound_cache_path()
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    return df.tail(n)

# 用法 1: 实时分钟流向
df = hsgt_realtime()
print(f"分钟点数: {len(df)}")
print(df.tail(5))

# 用法 2: 自动缓存今日收盘数据
if not df.empty:
    last = df.dropna().iloc[-1]
    _save_northbound_snapshot("2026-05-17", last["hgt_yi"], last["sgt_yi"])

# 用法 3: 读取历史
hist = _load_northbound_history(20)
print(hist)
```

### 3.3 东财 slist — 个股所属板块/概念归属（V3.2.2 替换百度）

**核心价值：** 一次调用拿到个股所属的全部板块（行业 + 概念 + 地域混合），含板块代码（BK码）、当日涨跌幅、板块龙头股。题材归因、板块联动分析必备。

> **V3.2.2 替换说明：** 百度 PAE `getrelatedblock` 接口已失效（实测返回 `ResultCode 10003` + 空数组，#18），改用东财 `slist` 个股所属板块接口（`spt=3`，一次请求拿全，零鉴权）。东财把行业/概念/地域混在**一个列表**里返回，板块名本身已自解释（如「食品饮料」是行业、「贵州板块」是地域、「酿酒概念」是概念），AI 直接用板块名做题材归因即可。

```python
def eastmoney_concept_blocks(code: str) -> dict:
    """
    个股所属板块/概念归属（东财 slist，一次请求拿全，已内置限流）。
    返回: {total, boards: [{name, code(BK码), change_pct, lead_stock}], concept_tags: [板块名...]}
    boards 混合 行业/概念/地域，板块名自解释；concept_tags 是所有板块名的便捷列表。
    """
    market_code = em_market_code(code)      # #46：不能用 startswith("6")，见 helper 注释
    params = {
        "fltt": "2", "invt": "2",
        "secid": f"{market_code}.{code}",
        "spt": "3", "pi": "0", "pz": "200", "po": "1",
        "fields": "f12,f14,f3,f128",
    }
    headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
    try:
        r = em_get("https://push2.eastmoney.com/api/qt/slist/get",
                   params=params, headers=headers, timeout=15)
        d = r.json()
    except Exception as e:
        print(f"[WARN] 东财板块归属请求失败: {e}")
        return {"total": 0, "boards": [], "concept_tags": []}

    diff = (d.get("data") or {}).get("diff") or {}
    items = diff.values() if isinstance(diff, dict) else diff
    boards = []
    for it in items:
        boards.append({
            "name": it.get("f14", ""),         # 板块名
            "code": it.get("f12", ""),         # BK 板块代码
            "change_pct": it.get("f3", ""),    # 板块当日涨跌幅
            "lead_stock": it.get("f128", ""),  # 板块龙头股
        })
    return {
        "total": len(boards),
        "boards": boards,
        "concept_tags": [b["name"] for b in boards],
    }

# 用法
blocks = eastmoney_concept_blocks("600519")
print(f"共 {blocks['total']} 个板块")
print("板块归属:", blocks["concept_tags"])
# → ['食品饮料', '白酒Ⅲ', '白酒Ⅱ', '贵州板块', '酿酒概念', 'HS300_', ...]
```

> **注意：** 东财不区分行业/概念/地域类型（混在一个列表返回）。如需精确分类可按板块名判断，或另查全市场板块清单（`clist` + `m:90+t:1/2/3`）——但后者每次需多发请求、大页易触发风控，不推荐在批量场景用。

### 3.4 东财 push2 — 个股资金流向（分钟级）

盘中实时分钟级资金流（主力/大单/中单/小单/超大单净流入）。

> **V3.1 替换说明：** 百度 PAE `fundflow` 和 `fundsortlist` 接口已于 2026-05 下线（返回 null），改用东财 push2 资金流 API。日级资金流见 Layer 4.5 `stock_fund_flow_120d()`。

```python
import requests

def eastmoney_fund_flow_minute(code: str) -> list[dict]:
    """
    个股资金流向（分钟级，当日盘中）。
    code: 6位股票代码
    返回: [{time, main_net, small_net, mid_net, large_net, super_net}, ...]
    单位: 元
    """
    # #46：secid 必须走 em_secid()。旧的 `startswith("6")` 会把沪市 ETF(51x)、
    # 科创 ETF(588x)、沪 B(900x) 错判成深市 → 接口返回 `data: null`。
    # ⚠️ 但要分清两件事：**路由修好 ≠ ETF 就有资金流**。2026-08-19 同批次实测，
    #    600519/300750 各返回 100 条，而 510300/588000 即便 secid 正确仍为 0 条 ——
    #    东财这个**个股**资金流接口本身不覆盖 ETF。ETF 资金流请另找端点。
    secid = em_secid(code)
    url = "https://push2.eastmoney.com/api/qt/stock/fflow/kline/get"
    params = {
        "secid": secid, "klt": 1,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57",
    }
    headers = {
        "User-Agent": UA,
        "Referer": "https://quote.eastmoney.com/",
        "Origin": "https://quote.eastmoney.com",
    }
    try:
        r = em_get(url, params=params, headers=headers, timeout=10)
        d = r.json()
    except Exception as e:
        print(f"[WARN] push2 资金流请求失败: {e}")
        return []

    rows = []
    # #46：接口对不存在/路由错误的 secid 返回 `"data": null`，
    # `.get("data", {})` 拿到的是 None 而非 {}，直接 .get() 会 AttributeError。
    for line in (d.get("data") or {}).get("klines") or []:
        parts = line.split(",")
        if len(parts) >= 6:
            rows.append({
                "time": parts[0],
                "main_net": float(parts[1]),
                "small_net": float(parts[2]),
                "mid_net": float(parts[3]),
                "large_net": float(parts[4]),
                "super_net": float(parts[5]),
            })
    return rows

# 用法: 分钟级实时资金流
realtime = eastmoney_fund_flow_minute("000858")
if realtime:
    last = realtime[-1]
    signal = "bullish" if last["main_net"] > 0 else "bearish"
    print(f"主力净流入: {last['main_net']:.0f}元 → {signal}")
    # 统计全天主力净流入
    total = sum(r["main_net"] for r in realtime)
    print(f"全天主力累计: {total/1e4:.0f}万元")
```

> **注意：** push2 资金流金额单位是**元**（非万元），使用时注意换算。`klt=1` 分钟级，`klt=101` 日级。

### 3.5 龙虎榜席位 — 个股上榜记录 + 买卖席位 TOP5 + 机构动向

直连东财 datacenter API，不依赖第三方封装。

```python
import requests
from datetime import datetime, timedelta

def dragon_tiger_board(code: str, trade_date: str, look_back: int = 30) -> dict:
    """
    龙虎榜数据聚合。
    trade_date: YYYY-MM-DD
    look_back: 回看天数
    返回: {records: [...], seats: {buy: [...], sell: [...]}, institution: {...}}
    """
    start = datetime.strptime(trade_date, "%Y-%m-%d") - timedelta(days=look_back)
    start_str = start.strftime("%Y-%m-%d")

    # 1. 上榜记录
    records = []
    data = eastmoney_datacenter(
        "RPT_DAILYBILLBOARD_DETAILSNEW",
        filter_str=f"(TRADE_DATE>='{start_str}')(TRADE_DATE<='{trade_date}')(SECURITY_CODE=\"{code}\")",
        page_size=50,
        sort_columns="TRADE_DATE", sort_types="-1",
    )
    for row in data:
        records.append({
            "date": str(row.get("TRADE_DATE", ""))[:10],
            "reason": row.get("EXPLANATION", ""),
            "net_buy": round((row.get("BILLBOARD_NET_AMT") or 0) / 10000, 1),
            "turnover": round(float(row.get("TURNOVERRATE") or 0), 2),
        })

    # 2. 最近上榜的买卖席位
    # ⚠️ buy_data/sell_data 必须在 if 之前初始化：第 3 步无条件遍历它们，
    # 而回看窗口内无上榜记录（大市值 / 低换手率标的的常态）时 if 分支不执行，
    # 变量从未绑定 → UnboundLocalError，调用方拿到的是崩溃而不是"空结果"（#45）。
    buy_data, sell_data = [], []
    seats = {"buy": [], "sell": []}
    if records:
        latest_date = records[0]["date"]
        # 买入席位
        buy_data = eastmoney_datacenter(
            "RPT_BILLBOARD_DAILYDETAILSBUY",
            filter_str=f"(TRADE_DATE='{latest_date}')(SECURITY_CODE=\"{code}\")",
            page_size=10,
            sort_columns="BUY", sort_types="-1",
        )
        for row in buy_data[:5]:
            seats["buy"].append({
                "name": row.get("OPERATEDEPT_NAME", ""),
                "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                "net": round((row.get("NET") or 0) / 10000, 1),
            })
        # 卖出席位
        sell_data = eastmoney_datacenter(
            "RPT_BILLBOARD_DAILYDETAILSSELL",
            filter_str=f"(TRADE_DATE='{latest_date}')(SECURITY_CODE=\"{code}\")",
            page_size=10,
            sort_columns="SELL", sort_types="-1",
        )
        for row in sell_data[:5]:
            seats["sell"].append({
                "name": row.get("OPERATEDEPT_NAME", ""),
                "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                "net": round((row.get("NET") or 0) / 10000, 1),
            })

    # 3. 机构买卖统计（从买卖席位明细中筛选 OPERATEDEPT_CODE="0" 即机构专用席位）
    institution = {"buy_amt": 0, "sell_amt": 0, "net_amt": 0}
    for detail_data, side in [(buy_data, "buy"), (sell_data, "sell")]:
        for row in detail_data:
            if str(row.get("OPERATEDEPT_CODE", "")) == "0":
                amt = (row.get("BUY") or 0) if side == "buy" else (row.get("SELL") or 0)
                if side == "buy":
                    institution["buy_amt"] += amt
                else:
                    institution["sell_amt"] += amt
    institution["buy_amt"] = round(institution["buy_amt"] / 10000, 1)
    institution["sell_amt"] = round(institution["sell_amt"] / 10000, 1)
    institution["net_amt"] = round(institution["buy_amt"] - institution["sell_amt"], 1)

    return {"records": records, "seats": seats, "institution": institution}

# 用法
data = dragon_tiger_board("002475", "2026-05-17")
print(f"近30日上榜 {len(data['records'])} 次")
for r in data["records"]:
    print(f"  {r['date']}: {r['reason']}")
if data["seats"]["buy"]:
    print("买入席位 TOP5:")
    for s in data["seats"]["buy"]:
        print(f"  {s['name']}: 买{s['buy_amt']}万 卖{s['sell_amt']}万 净{s['net']}万")
```

> **ST 股注意：** 5% 涨跌停更容易触发龙虎榜（"连续三日偏离值累计达12%"），科创板 20% 涨跌停则较少触发。

### 3.6 限售解禁日历 — 历史解禁 + 未来 90 天待解禁

```python
from datetime import datetime, timedelta

def lockup_expiry(code: str, trade_date: str, forward_days: int = 90) -> dict:
    """
    限售解禁日历。
    返回: {history: [...], upcoming: [...]}
    """
    # 1. 历史解禁记录
    history_data = eastmoney_datacenter(
        "RPT_LIFT_STAGE",
        filter_str=f"(SECURITY_CODE=\"{code}\")",
        page_size=15,
        sort_columns="FREE_DATE", sort_types="-1",
    )
    history = []
    for row in history_data:
        history.append({
            "date": str(row.get("FREE_DATE", ""))[:10],
            "type": row.get("FREE_SHARES_TYPE", ""),        # 解禁类型(东财2026改列名, 旧LIMITED_STOCK_TYPE已废)
            "shares": row.get("FREE_SHARES", 0),             # 本次解禁股数(万股)
            "able_shares": row.get("ABLE_FREE_SHARES", 0),   # 实际可流通股数(万股, 更贴近真实抛压)
            "ratio": row.get("FREE_RATIO", 0),               # 占总股本比(小数, ×100 得百分比)
        })

    # 2. 未来待解禁
    end_date = datetime.strptime(trade_date, "%Y-%m-%d") + timedelta(days=forward_days)
    end_str = end_date.strftime("%Y-%m-%d")
    upcoming_data = eastmoney_datacenter(
        "RPT_LIFT_STAGE",
        filter_str=f"(SECURITY_CODE=\"{code}\")(FREE_DATE>='{trade_date}')(FREE_DATE<='{end_str}')",
        page_size=20,
        sort_columns="FREE_DATE", sort_types="1",
    )
    upcoming = []
    for row in upcoming_data:
        upcoming.append({
            "date": str(row.get("FREE_DATE", ""))[:10],
            "type": row.get("FREE_SHARES_TYPE", ""),        # 解禁类型(东财2026改列名, 旧LIMITED_STOCK_TYPE已废)
            "shares": row.get("FREE_SHARES", 0),             # 本次解禁股数(万股)
            "able_shares": row.get("ABLE_FREE_SHARES", 0),   # 实际可流通股数(万股, 更贴近真实抛压)
            "ratio": row.get("FREE_RATIO", 0),               # 占总股本比(小数, ×100 得百分比)
        })

    return {"history": history, "upcoming": upcoming}

# 用法
data = lockup_expiry("002475", "2026-05-17")
print(f"历史解禁 {len(data['history'])} 批")
for h in data["history"][:5]:
    print(f"  {h['date']}: {h['type']} 数量={h['shares']}")
if data["upcoming"]:
    print(f"未来90天待解禁 {len(data['upcoming'])} 批")
else:
    print("未来90天无待解禁")
```

**限售股类型参考：**
- 首发原股东限售股份（IPO 后 1-3 年）
- 首发机构配售股份（IPO 战略配售）
- 定向增发机构配售股份（6-18 个月）
- 股权激励限售股份

### 3.7 行业板块排名（V3.0 改用东财 — 同花顺加了反爬401）

东财行业板块涨跌幅排名，一次调用看全市场行业轮动。

```python
import requests

def industry_comparison(top_n: int = 20) -> dict:
    """
    全行业涨跌幅排名（东财行业板块，~100 个行业）。
    返回: {top: [...], bottom: [...], total: int}
    """
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1", "pz": "100", "po": "1", "np": "1",
        "fltt": "2", "invt": "2", "fid": "f3",   # fid=f3 + po=1：按涨跌幅降序（缺 fid 时 top/bottom 切片非按涨幅排）
        "fs": "m:90+t:2",
        "fields": "f2,f3,f4,f12,f13,f14,f104,f105,f128,f136,f140,f141,f207",
    }
    headers = {"User-Agent": UA}
    r = em_get(url, params=params, headers=headers, timeout=15)
    d = r.json()
    items = (d.get("data") or {}).get("diff") or []        # #46 同因
    if not items:
        return {"top": [], "bottom": [], "total": 0}

    rows = []
    for i, item in enumerate(items):
        rows.append({
            "rank": i + 1,
            "name": item.get("f14", ""),
            "change_pct": item.get("f3", 0),
            "code": item.get("f12", ""),
            "up_count": item.get("f104", 0),
            "down_count": item.get("f105", 0),
            "leader": item.get("f140", ""),
            "leader_change": item.get("f136", 0),
        })

    return {
        "top": rows[:top_n],
        "bottom": rows[-top_n:],
        "total": len(rows),
    }

# 用法
data = industry_comparison(20)
print(f"共 {data['total']} 个行业")
print("\nTOP 10 涨幅:")
for r in data["top"][:10]:
    print(f"  {r['rank']}. {r['name']}: {r['change_pct']}% 涨{r['up_count']}跌{r['down_count']} 领涨{r['leader']}")
print("\nBOTTOM 5 跌幅:")
for r in data["bottom"][-5:]:
    print(f"  {r['rank']}. {r['name']}: {r['change_pct']}%")
```

### 3.8 板块资金流向（行业/概念/地域 × 今日/5日/10日）

东财板块资金流向——主力净流入额/净占比 + 超大/大/中/小单四档，覆盖行业、概念、地域三类板块，今日/5日/10日三个周期。与 §3.7 板块排名**同源同接口**（push2 `clist`），只是补请求了资金流字段（`f62/f184/f66...`）。走 `em_get` 限流防封。

```python
import requests

# 板块类型 → 东财 fs 参数
_BOARD_FS = {"industry": "m:90+t:2", "concept": "m:90+t:3", "region": "m:90+t:1"}
# 周期 → (排序fid, 主力净额, 主力净占比, 涨跌幅, 领涨股name)；四档明细仅今日
_BOARD_PERIOD = {
    "today": ("f62",  "f62",  "f184", "f3",   "f204"),
    "5d":    ("f164", "f164", "f165", "f109", "f257"),
    "10d":   ("f174", "f174", "f175", "f160", None),   # 10日领涨股名称字段不稳定，省略
}

def board_fund_flow(board_type: str = "industry", period: str = "today",
                    top_n: int = 20) -> dict:
    """
    板块资金流向排名（按主力净流入降序）。
    board_type: industry(行业) / concept(概念) / region(地域)
    period:     today(今日) / 5d(5日) / 10d(10日)
    返回: {board_type, period, total, rows:[{rank, name, code, change_pct,
           main_net(主力净额,元), main_pct(主力净占比,%), leader(领涨股),
           # 仅 today：super_large_net/large_net/medium_net/small_net(超大/大/中/小单净额,元)}]}
    注：板块级只有 今日/5日/10日（无 3日，个股级才有）。主力净额 = 超大单 + 大单。
    """
    if board_type not in _BOARD_FS:
        raise ValueError(f"board_type 须为 {list(_BOARD_FS)}")
    if period not in _BOARD_PERIOD:
        raise ValueError(f"period 须为 {list(_BOARD_PERIOD)}")
    fid, f_main, f_pct, f_chg, f_leader = _BOARD_PERIOD[period]

    fields = ["f12", "f14", f_chg, f_main, f_pct]
    if f_leader:
        fields.append(f_leader)
    if period == "today":
        fields += ["f66", "f72", "f78", "f84"]   # 超大/大/中/小单净额

    url = "https://push2.eastmoney.com/api/qt/clist/get"
    base = {
        "pz": "200", "po": "1", "np": "1",
        "fltt": "2", "invt": "2", "fid": fid,       # fid + po=1：按该周期主力净额降序
        "fs": _BOARD_FS[board_type],
        "fields": ",".join(dict.fromkeys(fields)),  # 去重保序
    }
    # ⚠️ 板块数超过单页上限：实测行业 496 个、概念 495 个，写死 pz=200 会把两者都截断，
    # total 也会误报成 200。先取第一页拿真实 total，需要更多才翻页（多数调用 top_n≤200，
    # 只发一次请求；em_get 有限流，不无谓翻页）。
    def _page(pn: int):
        r = em_get(url, params={**base, "pn": str(pn)},
                   headers={"User-Agent": UA}, timeout=15)
        d = r.json().get("data") or {}
        return (d.get("diff") or []), int(d.get("total") or 0)

    _PAGE = 200
    items, total = _page(1)
    pn = 2
    while len(items) < top_n:
        if total and len(items) >= total:
            break                      # 已取满接口声明的总数
        more, _ = _page(pn)
        if not more:
            break                      # 防御：API 提前返空则停止，避免死循环
        items += more
        pn += 1
        if len(more) < _PAGE:
            break                      # 不足一页＝已到末页（total 缺失时的收敛条件）
    total = max(total, len(items))

    rows = []
    for i, it in enumerate(items):
        row = {
            "rank": i + 1,
            "name": it.get("f14", ""),
            "code": it.get("f12", ""),
            "change_pct": it.get(f_chg, 0),
            "main_net": it.get(f_main, 0),          # 主力净流入净额（元）
            "main_pct": it.get(f_pct, 0),           # 主力净流入净占比（%）
            "leader": it.get(f_leader, "") if f_leader else "",
        }
        if period == "today":
            row.update({
                "super_large_net": it.get("f66", 0),
                "large_net":       it.get("f72", 0),
                "medium_net":      it.get("f78", 0),
                "small_net":       it.get("f84", 0),
            })
        rows.append(row)

    return {"board_type": board_type, "period": period,
            "total": total, "rows": rows[:top_n]}

# 用法
d = board_fund_flow("industry", "today", 10)
print(f"行业板块今日主力净流入 TOP{len(d['rows'])}（共 {d['total']} 个）:")
for r in d["rows"]:
    print(f"  {r['rank']}. {r['name']}: 主力 {r['main_net']/1e8:.2f}亿 ({r['main_pct']}%) "
          f"涨跌{r['change_pct']}% 超大{r['super_large_net']/1e8:.2f}亿 领涨{r['leader']}")

# 概念板块 5 日资金流
concept_5d = board_fund_flow("concept", "5d", 10)
# 地域板块 10 日资金流
region_10d = board_fund_flow("region", "10d", 10)
```

### 3.9 全市场龙虎榜

每日全市场龙虎榜汇总——当日所有触发龙虎榜的股票 + 上榜原因 + 买卖净额 + 换手率。

```python
from datetime import datetime

def daily_dragon_tiger(trade_date: str = None, min_net_buy: float = None) -> dict:
    """
    全市场龙虎榜。
    trade_date: YYYY-MM-DD（默认当日）
    min_net_buy: 净买入下限（万元），None 不过滤
    返回: {date, total_records, stocks: [{code, name, reason, close, change_pct,
           net_buy_wan, buy_wan, sell_wan, turnover_pct}]}
    """
    if trade_date is None:
        trade_date = datetime.now().strftime("%Y-%m-%d")

    data = eastmoney_datacenter(
        "RPT_DAILYBILLBOARD_DETAILSNEW",
        filter_str=f"(TRADE_DATE>='{trade_date}')(TRADE_DATE<='{trade_date}')",
        page_size=500,
        sort_columns="BILLBOARD_NET_AMT", sort_types="-1",
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

# 用法
data = daily_dragon_tiger("2026-05-16")
print(f"{data['date']} 龙虎榜共 {data['total_records']} 条记录")
for s in data["stocks"][:10]:
    print(f"  {s['code']} {s['name']}: {s['reason']} | 净买{s['net_buy_wan']}万 涨跌{s['change_pct']}%")

# 只看净买入 > 5000 万的
data = daily_dragon_tiger("2026-05-16", min_net_buy=5000)
print(f"\n净买入 > 5000万: {data['total_records']} 条")
```

### 3.10 信号层组合用法：题材热度 + 资金验证

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

# 同时拉北向当日流向，看资金流方向是否对应题材
df_north = hsgt_realtime()
hgt_close = df_north["hgt_yi"].dropna().iloc[-1] if not df_north.empty else 0
sgt_close = df_north["sgt_yi"].dropna().iloc[-1] if not df_north.empty else 0
print(f"\n北向收盘累计: 沪股通 {hgt_close} 亿 / 深股通 {sgt_close} 亿")

# V3.0: 叠加行业对比，看哪些行业资金在流入
comp = industry_comparison(10)
print("\n行业涨幅 TOP 5:")
for r in comp["top"][:5]:
    print(f"  {r['name']}: {r['change_pct']}% 涨{r['up_count']}跌{r['down_count']}")
```

---

## Layer 4: 资金面 / 筹码层（V3.0 新增）

### 4.1 融资融券明细

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
    rows = []
    for row in data:
        rows.append({
            "date": str(row.get("DATE", ""))[:10],
            "rzye": row.get("RZYE", 0),       # 融资余额(元)
            "rzmre": row.get("RZMRE", 0),      # 融资买入额
            "rzche": row.get("RZCHE", 0),      # 融资偿还额
            "rqye": row.get("RQYE", 0),        # 融券余额(元)
            "rqmcl": row.get("RQMCL", 0),      # 融券卖出量
            "rqchl": row.get("RQCHL", 0),      # 融券偿还量
            "rzrqye": row.get("RZRQYE", 0),    # 融资融券余额合计
        })
    return rows

# 用法
data = margin_trading("600519")
for d in data[:5]:
    print(f"{d['date']}: 融资余额={d['rzye']/1e8:.2f}亿 融券余额={d['rqye']/1e8:.2f}亿")
```

### 4.2 大宗交易

```python
def block_trade(code: str, page_size: int = 20) -> list[dict]:
    """
    大宗交易记录。
    返回: [{date, price, vol, amount, buyer, seller, premium_pct}]
    """
    data = eastmoney_datacenter(
        "RPT_DATA_BLOCKTRADE",
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
            "vol": row.get("DEAL_VOLUME", 0),
            "amount": row.get("DEAL_AMT", 0),
            "buyer": row.get("BUYER_NAME", ""),
            "seller": row.get("SELLER_NAME", ""),
        })
    return rows

# 用法
data = block_trade("600519")
for d in data[:5]:
    print(f"{d['date']}: 价格={d['price']} 溢价={d['premium_pct']}% 买方={d['buyer']}")
```

### 4.3 股东户数变化

```python
def holder_num_change(code: str, page_size: int = 10) -> list[dict]:
    """
    股东户数变化（季度级）。
    返回: [{date, holder_num, change_num, change_ratio, avg_shares}]
    """
    data = eastmoney_datacenter(
        "RPT_HOLDERNUMLATEST",
        filter_str=f'(SECURITY_CODE="{code}")',
        page_size=page_size,
        sort_columns="END_DATE", sort_types="-1",
    )
    rows = []
    for row in data:
        rows.append({
            "date": str(row.get("END_DATE", ""))[:10],
            "holder_num": row.get("HOLDER_NUM", 0),
            "change_num": row.get("HOLDER_NUM_CHANGE", 0),
            "change_ratio": row.get("HOLDER_NUM_RATIO", 0),  # 环比%
            "avg_shares": row.get("AVG_FREE_SHARES", 0),     # 户均持股
        })
    return rows

# 用法
data = holder_num_change("600519")
for d in data[:5]:
    print(f"{d['date']}: 股东数={d['holder_num']} 变化={d['change_ratio']}% 户均={d['avg_shares']}")
# 股东户数持续减少 = 筹码集中 = 主力吸筹信号
```

### 4.4 分红送转历史

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
    rows = []
    for row in data:
        rows.append({
            "date": str(row.get("EX_DIVIDEND_DATE", ""))[:10],
            "bonus_rmb": row.get("PRETAX_BONUS_RMB", 0),    # 每股派息(税前)
            "transfer_ratio": row.get("TRANSFER_RATIO", 0),  # 每10股转增
            "bonus_ratio": row.get("BONUS_RATIO", 0),        # 每10股送股
            "plan": row.get("ASSIGN_PROGRESS", ""),           # 进度
        })
    return rows

# 用法
data = dividend_history("600519")
for d in data[:5]:
    print(f"{d['date']}: 每股派息={d['bonus_rmb']}元 转增={d['transfer_ratio']} 送={d['bonus_ratio']}")
```

### 4.5 个股资金流（120日，日级）

```python
import requests

def stock_fund_flow_120d(code: str) -> list[dict]:
    """
    个股资金流（日级，最近120个交易日）。
    返回: [{date, main_net(主力净流入), small_net, mid_net, large_net, super_net}]
    单位: 元
    """
    market_code = em_market_code(code)      # #46
    url = "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
    params = {
        "secid": f"{market_code}.{code}",
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65",
        "lmt": "120",
    }
    headers = {
        "User-Agent": UA,
        "Referer": "https://quote.eastmoney.com/",
        "Origin": "https://quote.eastmoney.com",
    }
    try:
        r = em_get(url, params=params, headers=headers, timeout=15)
        d = r.json()
    except Exception as e:
        print(f"[WARN] push2 资金流请求失败: {e}")
        return []
    klines = (d.get("data") or {}).get("klines") or []     # #46 同因

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

# 统计近20日主力净流入
recent_20 = data[-20:]
total_main = sum(d["main_net"] for d in recent_20)
print(f"\n近20日主力累计净流入: {total_main/1e8:.2f}亿")
```

> **⚠️ 大陆住宅 IP 间歇封锁（#18）：** push2/push2his 系列对**部分大陆住宅宽带 IP** 有连接级风控，表现为偶发 `HTTP 000`（连接被拒/超时）或返回空——**这不是代码问题**（同一代码在其他网络/时段实测正常）。遇到时：① 隔几分钟重试；② 换网络环境（如手机热点）；③ 降低请求频率（调大 `EM_MIN_INTERVAL`）。日级资金流务实替代：用 §1.2 腾讯 K 线或 §1.3 通达信盘后包的量价数据（mootdx 行情命令已失效，#52），或换时段重试。

---

### 4.6 筹码分布 CYQ — 获利比例 / 平均成本 / 成本区间（V3.7.0 新增）

**核心价值：** 本层叫「资金面 / **筹码**层」，但 §4.1~§4.5 全是融资融券、大宗、股东户数这类
**资金面**数据，一直缺真正的**筹码分布**。本端点补齐。

🔴 **东财没有公开 CYQ 接口**（2026-08-19 实测 `push2/api/qt/stock/cyq/get` 与 `push2his` 两种写法**均 404**）。
业界通行做法是**本地推演**：历史筹码按换手率衰减，当日成交量按三角分布撒进 `[low, high]` 区间。
**零新增数据源** —— OHLC 与换手率都从 §6.5 baostock 一次取齐（见下方用法）。

```python
import numpy as np
import pandas as pd


def _triangular_weights(grid: np.ndarray, low: float, high: float, avg: float) -> np.ndarray:
    """当日筹码在价格网格上的三角分布权重（峰值在均价，面积归一）"""
    w = np.zeros_like(grid)
    if not np.isfinite([low, high, avg]).all() or high < low:
        return w
    if high - low < 1e-9:                       # 一字板：全部堆在一个价位
        w[np.argmin(np.abs(grid - low))] = 1.0
        return w
    avg = min(max(avg, low), high)              # 均价必须落在当日区间内
    left = (grid >= low) & (grid <= avg)
    right = (grid > avg) & (grid <= high)
    if avg - low > 1e-9:
        w[left] = (grid[left] - low) / (avg - low)
    else:
        w[left] = 1.0
    if high - avg > 1e-9:
        w[right] = (high - grid[right]) / (high - avg)
    else:
        w[right] = 1.0
    total = w.sum()
    if total > 0:
        return w / total
    # 🔴 兜底：当日振幅窄于网格步长时，可能一个网格点都没落进 [low, high]，
    #    权重会全为 0。若就此跳过该日，连它的换手衰减也会一并丢失 ——
    #    低波动标的（银行股等）+ 长窗口下这会累积成很大的偏差。映射到最近网格点。
    w[np.argmin(np.abs(grid - avg))] = 1.0
    return w


def chip_distribution(df: pd.DataFrame, grid_size: int = 300, decay: float = 1.0) -> dict:
    """筹码分布 — df 需含 high/low/close/turn（turn 为百分数，0.31 表示 0.31%）

    decay: 换手衰减系数。1.0=按真实换手率换手；同花顺口径常用 1.5~2.0 加快历史筹码消散。
    """
    # 🔴 必须带 date 并按时间升序：换手衰减是有方向的时序递推，
    #    若传入常见的「最新在前」倒序，衰减会反向推、且 close.iloc[-1] 会把最老的
    #    收盘价当成现价 —— 结果完全错却不会报错。这里强制要求 date 并自行排序。
    need = {"date", "high", "low", "close", "turn"}
    missing = need - set(df.columns)
    if missing:
        raise ValueError(f"chip_distribution 缺少列: {sorted(missing)}（date 用于强制时间升序）")
    d = df.dropna(subset=["high", "low", "close", "turn"]).copy()
    d = d[d["high"] > 0]
    if d.empty:
        raise ValueError("chip_distribution: 有效行数为 0（检查是否全是停牌日，或字段类型不对）")
    d = d.sort_values("date").reset_index(drop=True)

    lo, hi = float(d["low"].min()), float(d["high"].max())
    pad = (hi - lo) * 0.02 or max(lo * 0.02, 0.01)
    grid = np.linspace(lo - pad, hi + pad, grid_size)

    # 🔴 初始筹码必须播种成「首日全部流通盘」，不能从全零开始。
    #    从零起步等于假设窗口之前没有任何持仓，再把窗口内的少量换手归一化成 100%：
    #    两个 1% 换手日（价 10 和 100）会被算成约 50/50，而真实情况是约 99% 仍在 10 附近。
    chips = None
    for row in d.itertuples(index=False):
        t = float(row.turn) / 100.0 * decay
        t = min(max(t, 0.0), 1.0)               # 换手率兜到 [0,1]，防异常值把筹码一次清零
        avg = (float(row.high) + float(row.low) + float(row.close)) / 3.0
        w = _triangular_weights(grid, float(row.low), float(row.high), avg)
        if w.sum() <= 0:
            continue
        if chips is None:
            chips = w.copy()                    # 首日分布 = 期初全部流通筹码
            continue
        chips = chips * (1.0 - t) + w * t
    if chips is None:
        raise RuntimeError("chip_distribution: 所有交易日的价格区间都无效，无法构建分布")

    total = chips.sum()
    if total <= 0:
        raise RuntimeError("chip_distribution: 筹码总量为 0，无法计算指标")
    chips = chips / total

    price = float(d["close"].iloc[-1])
    cum = np.cumsum(chips)

    def price_at(q: float) -> float:
        return float(np.interp(q, cum, grid))

    p05, p15, p85, p95 = (price_at(q) for q in (0.05, 0.15, 0.85, 0.95))
    peak_i = int(np.argmax(chips))
    return {
        "price": price,
        "profit_ratio": float(chips[grid <= price].sum()),      # 获利比例
        "avg_cost": float((grid * chips).sum()),                # 平均成本
        "cost_90": (p05, p95),
        "cost_70": (p15, p85),
        "concentration_90": float((p95 - p05) / (p95 + p05)) if p95 + p05 else None,
        "concentration_70": float((p85 - p15) / (p85 + p15)) if p85 + p15 else None,
        "peak_price": float(grid[peak_i]),                      # 筹码峰
        "histogram": [(float(pp), float(cc)) for pp, cc in zip(grid, chips) if cc > 1e-6],
    }


# 用法 — 输入用 §6.5 baostock（一次拿齐 OHLC + 换手率）
import baostock as bs

bs_code = _bs_code("600519")
with bs_session():
    rs = bs.query_history_k_data_plus(
        bs_code, "date,open,high,low,close,turn,tradestatus",
        start_date="2026-02-01", end_date="2026-08-18", frequency="d", adjustflag="2",
    )                                            # 2=前复权，筹码成本必须用复权价
    k = _rs_to_df(rs)
for c in ("open", "high", "low", "close", "turn"):
    k[c] = pd.to_numeric(k[c], errors="coerce")
k = k[k["tradestatus"] == "1"]                   # 停牌日不参与换手衰减

r = chip_distribution(k)
print(f"现价 {r['price']:.2f} | 获利比例 {r['profit_ratio']*100:.2f}% | 平均成本 {r['avg_cost']:.2f}")
print(f"90%成本区间 {r['cost_90'][0]:.2f}~{r['cost_90'][1]:.2f} 集中度 {r['concentration_90']*100:.2f}%")
print(f"筹码峰 {r['peak_price']:.2f}")
# 实测 2026-08-19（131 个交易日，窗口累计换手 46.5%）：
#   现价 1297.99 | 获利比例 15.44% | 平均成本 1371.31
#   90%成本区间 1207.89~1425.16 集中度 8.25% | 筹码峰 1398.99
#   ← 窗口累计换手不足 100%，多数筹码仍是期初高位持仓，故均成本高于现价、获利盘偏低
```

**读法与自检**

| 指标 | 含义 | 性质 |
|------|------|------|
| `profit_ratio` | 现价**之下**的持仓占比 = 浮盈盘 | **硬约束**：必在 [0,1] |
| `avg_cost` | 加权平均持仓成本 | **硬约束**：必落在网格最低~最高之间 |
| `cost_90` / `cost_70` | 5%~95% / 15%~85% 分位价格区间 | **硬约束**：`cost_90` 必包含 `cost_70` |
| `concentration_*` | `(高-低)/(高+低)`，越小越集中 | **硬约束**：90% 集中度必大于 70% |
| `peak_price` | 筹码最密集的价位（套牢/支撑区） | **启发式**：通常落在 `cost_90` 内 |

> ⚠️ **下面两条是启发式，不是不变量，不要拿它们当断言去拒绝结果：**
> - 「`price < avg_cost` ⇔ `profit_ratio < 50%`」在**对称**分布下成立，但**右偏**分布里
>   均值被右尾拉高，现价可能同时低于均值、又高于中位数 —— 此时两者方向相反是正常的。
> - 「`peak_price` 落在 `cost_90` 内」绝大多数时候成立，但一个**窄而高的尖峰**若恰好位于
>   5% 分位之外，峰值就会落在区间外，这仍是合法结果。

> ⚠️ **这是推演不是实测持仓**。券商软件各家衰减系数与分布模型不同，数值不会完全一致，
> 看的是**形态与相对变化**（获利盘是在增加还是减少、筹码峰在上方还是下方），不是绝对值对齐。
> 输入必须用**前复权**价（`adjustflag="2"`），用不复权价跨除权日会把成本算错。

### 4.7 ETF 份额 — 上交所按日归档 + 深交所当前快照（V3.9.0 新增）

ETF 份额变化是看资金申购赎回的直接口径。两所都是官方数据，单位**万份**。
**上交所**可按历史日期查询（实测 2023-01-03 仍有 446 只）；**深交所只提供最新一天**，`date` 与快照日期不符直接抛错，
历史份额需要自己按日留存（深交所注明 T 日晚为预估值、T+1 早为确认值）。两所的类别字段口径不同，没有硬并成一列。

<!-- v39-etf-shares:start -->
```python
import re
import time

SSE_ETF_SHARES_URL = "https://query.sse.com.cn/commonQuery.do"
SZSE_FUND_LIST_URL = "https://fund.szse.cn/api/report/ShowReport/data"


def _etf_shares_sse(day):
    params = {"sqlId": "COMMON_SSE_ZQPZ_ETFZL_XXPL_ETFGM_SEARCH_L", "STAT_DATE": day,
              "isPagination": "true", "pageHelp.pageSize": 10000, "pageHelp.pageNo": 1,
              "pageHelp.beginPage": 1, "pageHelp.cacheSize": 1, "pageHelp.endPage": 1}
    response = _v39_http(SSE_ETF_SHARES_URL, params=params,
                         headers={"Referer": "https://www.sse.com.cn/"})
    payload = _v39_json(response)
    result = payload.get("result") if isinstance(payload, dict) else None
    page_help = payload.get("pageHelp") if isinstance(payload, dict) else None
    if (not isinstance(result, list) or not all(isinstance(r, dict) for r in result)
            or not isinstance(page_help, dict)):
        raise RuntimeError("上交所 ETF 规模接口返回结构改变")
    # 服务端把每页压到 2000 条（请求 10000 也回 pageSize=2000，2026-09-20 实测当日共 912 条）；
    # 条数必须等于它自报的 total，超过一页或只回了一部分都不能当完整快照
    total = _v39_count(page_help.get("total"), "上交所 ETF 规模 pageHelp.total")
    if len(result) != total:
        raise RuntimeError(f"上交所 ETF 规模返回 {len(result)} 条，与自报总数 {total} 不符，结果不完整")
    if not result:
        raise ValueError(f"上交所 {day} 没有 ETF 份额数据：非交易日或尚未发布")
    rows = []
    for rec in result:
        if rec.get("STAT_DATE") != day:
            raise RuntimeError("上交所返回了其他日期的数据")
        try:
            rows.append({"date": day, "exchange": "SH", "code": rec["SEC_CODE"],
                         "name": rec["SEC_NAME"], "etf_type": rec.get("ETF_TYPE"),
                         "shares_10k": _v39_req_num(rec["TOT_VOL"], "上交所 ETF 份额")})
        except KeyError as exc:
            raise RuntimeError(f"上交所 ETF 规模字段缺失: {exc!r}") from exc
    return rows, response.url


def _etf_shares_szse(day):
    rows, page, first, url = [], 1, None, SZSE_FUND_LIST_URL
    while first is None or page <= first[1]:
        response = _v39_http(SZSE_FUND_LIST_URL,
                             params={"SHOWTYPE": "JSON", "CATALOGID": "1000_lf", "TABKEY": "tab1",
                                     "selectJjlb": "ETF", "PAGENO": page},
                             headers={"Referer": "https://fund.szse.cn/"})
        payload = _v39_json(response)
        table = payload[0] if isinstance(payload, list) and payload else None
        meta = table.get("metadata") if isinstance(table, dict) else None
        data = table.get("data") if isinstance(table, dict) else None
        if not isinstance(meta, dict) or not isinstance(data, list):
            raise RuntimeError(f"深交所基金列表第 {page} 页的返回结构变了（缺 metadata / data）")
        # subname 是这份快照的数据日期（实测 '2026-09-18'）。缺失或写法变了先按来源坏掉报错，
        # 否则下面会说成「快照日期是 None，不是 2026-09-18」，把结构损坏伪装成用户要了历史日期。
        snap = (_v39_src_date(meta.get("subname")),
                _v39_count(meta.get("pagecount"), "深交所基金列表 pagecount"),
                _v39_count(meta.get("recordcount"), "深交所基金列表 recordcount"))
        if snap[1] < 1:
            raise RuntimeError(f"深交所基金列表 pagecount={snap[1]}，分页信息异常")
        if first is None:
            # 深交所只提供「当前」规模快照，metadata.subname 是它的数据日期。
            if snap[0] != day:
                raise ValueError(f"深交所当前规模快照日期是 {snap[0]}，不是 {day}；"
                                 "深市只能取最新一天，历史份额请自行按日留存")
            first = snap
        elif snap != first:     # 翻页途中快照换了日期或总数：拼出来的是两份快照的混合
            raise RuntimeError(f"深交所 ETF 列表翻页时快照从 {first} 变成 {snap}，请重试")
        if not data:        # 预期内的页是空的：返回前几页会被当成完整快照
            raise RuntimeError(f"深交所 ETF 列表第 {page}/{first[1]} 页是空的，结果不完整")
        for rec in data:
            try:
                code = re.search(r"<u>(\d{6})</u>", rec["sys_key"])
                name = re.search(r"<u>(.*?)</u>", rec["jjjcurl"])
                shares = re.search(r">([\d,\.]+)</a>", rec["dqgm"])
            except (KeyError, TypeError) as exc:
                raise RuntimeError(f"深交所基金列表字段缺失: {exc!r}") from exc
            if not (code and name and shares):
                raise RuntimeError("深交所基金列表字段格式改变")
            rows.append({"date": day, "exchange": "SZ", "code": code.group(1),
                         "name": name.group(1), "fund_category": rec.get("tzlb"),
                         "shares_10k": _v39_req_num(shares.group(1), "深交所 ETF 份额"),
                         "manager": rec.get("glrmc"), "listing_date": rec.get("ssrq")})
        url = response.url
        page += 1
        time.sleep(0.3)
    if len(rows) != first[2]:
        raise RuntimeError(f"深交所 ETF 列表取到 {len(rows)} 条，与它自报的总数 {first[2]} 不符")
    return rows, url


@_v39_contract
def etf_shares(date, exchange="SH"):
    """ETF 份额（万份）— 上交所按日归档，深交所只有当前快照。

    date: 'YYYY-MM-DD'。上交所可查历史日期（实测 2023-01-03 仍有 446 只）；
    深交所只返回最新一天，date 与快照日期不符直接抛错（深交所注明 T 日晚为预估、T+1 早为确认值）。
    exchange: 'SH' 或 'SZ'。两所单位都是万份。上交所的 etf_type 是单市/跨市/跨境等，
    深交所给的是 fund_category（股票基金/债券基金…），两者口径不同，没有混成一列。
    """
    day = _v39_date(date)
    exchange = str(exchange).upper()
    if exchange == "SH":
        rows, url = _etf_shares_sse(day)
    elif exchange == "SZ":
        rows, url = _etf_shares_szse(day)
    else:
        raise ValueError("exchange 只能是 'SH' 或 'SZ'")
    frame = _v39_frame(rows, exchange.lower() + "se", url)
    if frame.duplicated(["code"]).any():
        raise RuntimeError("ETF 份额数据代码重复，不能当成完整快照")
    return frame
```
<!-- v39-etf-shares:end -->

```python
sh = etf_shares("2026-09-18", "SH")
sz = etf_shares("2026-09-18", "SZ")     # 若深交所最新快照不是这一天，会抛 ValueError 并告诉快照日期
```

---

## Layer 5: 新闻层

### 5.1 东财个股新闻（直连 search-api-web）

```python
import requests
import re
import json

def eastmoney_stock_news(code: str, page_size: int = 20) -> list[dict]:
    """
    东财个股新闻（JSONP 接口）。
    返回: [{title, content, time, source, url}]
    """
    # 构造 JSONP 参数
    cb = "jQuery_news"
    url = "https://search-api-web.eastmoney.com/search/jsonp"
    inner_params = json.dumps({
        "uid": "",
        "keyword": code,
        "type": ["cmsArticleWebOld"],
        "client": "web",
        "clientType": "web",
        "clientVersion": "curr",
        "param": {"cmsArticleWebOld": {"searchScope": "default", "sort": "default",
                  "pageIndex": 1, "pageSize": page_size, "preTag": "", "postTag": ""}},
    }, separators=(',', ':'))
    params = {"cb": cb, "param": inner_params}
    headers = {"User-Agent": UA, "Referer": "https://so.eastmoney.com/"}
    r = em_get(url, params=params, headers=headers, timeout=15)

    # 解析 JSONP
    text = r.text
    json_str = text[text.index("(") + 1 : text.rindex(")")]
    d = json.loads(json_str)

    rows = []
    # 东财实际返回里 result.cmsArticleWebOld 直接就是文章列表（非 {list:[...]} 嵌套）
    articles = d.get("result", {}).get("cmsArticleWebOld", []) or []
    for a in articles:
        rows.append({
            "title": re.sub(r'<[^>]+>', '', a.get("title", "")),
            "content": re.sub(r'<[^>]+>', '', a.get("content", ""))[:200],
            "time": a.get("date", ""),
            "source": a.get("mediaName", ""),
            "url": a.get("url", ""),
        })
    return rows

# 用法
news = eastmoney_stock_news("688017")
for n in news[:5]:
    print(f"  {n['time']} | {n['source']} | {n['title']}")
```

> **⚠️ 间歇性返回空（#18）：** 部分大陆住宅 IP 调本接口会只拿到 `passportWeb`（股民资料）而无 `cmsArticleWebOld`（文章列表）——这是东财对该 IP 的间歇风控，非代码问题。代码已对空结果安全返回 `[]`；遇到时隔几分钟或换网络重试即可。

### 5.2 财联社快讯（直连 cls.cn，v1 API + 本地签名）✅ 已复活（2026-07）

> **✅ 2026-07 复活：** 旧接口 `cls.cn/nodeapi/telegraphList` 2026-05 下线（站点改
> Next.js，旧址返回 HTML 而非 JSON，#14）。现走新版 `cls.cn/v1/roll/get_roll_list`——它
> 强制校验 `sign`，但签名**纯本地计算、无需任何 key**：`sign = md5(sha1(按 key 字典序
> 拼接的 query 串))`。财联社快讯偏 A 股财经、时效强，与 §5.3 东财 7×24 **互为独立备份**
> （两条不同源、不同风控面，一条被封另一条仍在）。2026-07-11 实测 errno=0 正常返回。

```python
import requests
import hashlib
from datetime import datetime

def cls_telegraph(page_size: int = 50) -> list[dict]:
    """
    财联社电报（全市场实时快讯）。v1 API + 本地签名，零 key。
    返回: [{title, content, time}]  time 已转为 'YYYY-MM-DD HH:MM:SS'
    """
    params = {"appName": "CailianpressWeb", "os": "web", "sv": "7.7.5",
              "last_time": "", "refresh_type": "1", "rn": str(page_size)}
    # 签名：md5(sha1(按 key 字典序拼接的 query 串))，纯本地算、无需 key
    qs = "&".join(f"{k}={params[k]}" for k in sorted(params))
    sign = hashlib.md5(hashlib.sha1(qs.encode()).hexdigest().encode()).hexdigest()
    url = f"https://www.cls.cn/v1/roll/get_roll_list?{qs}&sign={sign}"
    headers = {"User-Agent": UA, "Referer": "https://www.cls.cn/"}
    r = requests.get(url, headers=headers, timeout=10)
    d = r.json()

    rows = []
    for item in (d.get("data") or {}).get("roll_data") or []:   # #46 同因
        ts = item.get("ctime")
        t = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else ""
        rows.append({
            "title": item.get("title", "") or item.get("brief", ""),
            "content": item.get("content", "") or item.get("brief", ""),
            "time": t,
        })
    return rows

# 用法
news = cls_telegraph()
for n in news[:10]:
    print(f"  {n['time']} | {n['title'][:60]}")
```

### 5.3 东财全球资讯（7x24）

```python
import requests

import uuid

def eastmoney_global_news(page_size: int = 50) -> list[dict]:
    """
    东方财富全球财经资讯（7x24 滚动）。
    返回: [{title, summary, time}]
    """
    url = "https://np-weblist.eastmoney.com/comm/web/getFastNewsList"
    params = {
        "client": "web", "biz": "web_724",
        "fastColumn": "102", "sortEnd": "",
        "pageSize": str(page_size),
        "req_trace": str(uuid.uuid4()),
    }
    headers = {"User-Agent": UA, "Referer": "https://kuaixun.eastmoney.com/"}
    r = em_get(url, params=params, headers=headers, timeout=10)
    d = r.json()

    rows = []
    for item in (d.get("data") or {}).get("fastNewsList") or []:  # #46 同因
        rows.append({
            "title": item.get("title", ""),
            "summary": item.get("summary", "")[:200],
            "time": item.get("showTime", ""),
        })
    return rows

# 用法
news = eastmoney_global_news()
for n in news[:10]:
    print(f"  {n['time']} | {n['title']}")
```

### 5.4 华尔街见闻 7×24 快讯（V3.9.0 新增）

新闻层第三个来源，与 §5.2 财联社、§5.3 东财互为备份。`channel` 常用 `global-channel`（要闻）/ `a-stock-channel`（A 股）。
`importance` 取见闻的 score 字段，实测只有 1 / 2，100 条里约 6 条为 2（头条级快讯）。时间为北京时间。
翻页：把返回表的 `attrs['next_cursor']` 传给下一次的 `cursor`。

<!-- v39-wscn-lives:start -->
```python
import re
from datetime import datetime, timedelta, timezone

WSCN_LIVES_URL = "https://api-one-wscn.awtmt.com/apiv1/content/lives"
_CN_TZ = timezone(timedelta(hours=8))


@_v39_contract
def wallstreetcn_lives(channel="global-channel", limit=50, cursor=None):
    """华尔街见闻 7×24 快讯（新闻层第三来源，与 §5.2 财联社 / §5.3 东财互备）。

    channel: global-channel（要闻，默认）/ a-stock-channel（A 股）等频道名。
    limit ≤ 100。翻页：把返回表的 attrs['next_cursor'] 传给下一次的 cursor。
    importance 取见闻的 score 字段：实测只有 1 / 2，100 条里约 6 条为 2（头条级快讯）。时间为北京时间。
    """
    if not re.fullmatch(r"[a-z0-9-]+-channel", str(channel)):
        raise ValueError("channel 形如 'global-channel' / 'a-stock-channel'")
    if not 1 <= int(limit) <= 100:
        raise ValueError("limit 范围 1–100")
    params = {"channel": channel, "limit": int(limit)}
    if cursor:
        params["cursor"] = cursor
    response = _v39_http(WSCN_LIVES_URL, params=params)
    payload = _v39_json(response)
    if not isinstance(payload, dict) or payload.get("code") != 20000 or not isinstance(payload.get("data"), dict):
        raise RuntimeError(f"华尔街见闻返回错误: {str(payload)[:200]}")
    items = _v39_rows(payload["data"].get("items"), "华尔街见闻快讯的 items")
    rows = []
    try:
        for item in items:
            stamp = item["display_time"]
            if isinstance(stamp, bool) or not isinstance(stamp, (int, float)):
                raise TypeError(f"display_time={stamp!r}")
            rows.append({"id": item["id"],
                         "time": datetime.fromtimestamp(stamp, _CN_TZ).strftime("%Y-%m-%d %H:%M:%S"),
                         "title": item.get("title") or "",
                         "content": (item.get("content_text") or "").strip(),
                         "importance": item.get("score"),
                         "channels": ",".join(_v39_labels(item.get("channels"), "快讯 channels")),
                         "url": item.get("uri") or ""})
    except (KeyError, TypeError, AttributeError, ValueError, OverflowError, OSError) as exc:
        raise RuntimeError(f"华尔街见闻快讯条目格式改变: {type(exc).__name__}: {exc}") from exc
    if not rows:
        raise RuntimeError(f"华尔街见闻 {channel} 返回 0 条（频道名可能不存在）")
    frame = _v39_frame(rows, "wallstreetcn", response.url)
    frame.attrs["next_cursor"] = payload["data"].get("next_cursor")
    return frame
```
<!-- v39-wscn-lives:end -->

### 5.5 央视《新闻联播》文字稿（V3.9.0 新增）

央视网官方页面：当日条目标题 + 逐条正文（`with_content=True` 约 15 次请求）。页面结构 2016 / 2019 / 2021 年改过三次，
三种写法都能解析。个别老视频已被下架，其 `content` 为 None（标题仍在）。当晚约 20:00 后更新，未发布抛 `ValueError`。
**内容以时政为主：可用于政策信号研究，做短视频文案时不要引用。**

<!-- v39-cctv-news:start -->
```python
import html as _html
import re
import time

CCTV_DAY_URL = "https://tv.cctv.com/lm/xwlb/day/{ymd}.shtml"


def _cctv_body(url):
    text = _v39_http(url).content.decode("utf-8", "replace")
    if len(text) < 1000 and "error.html" in text:
        return None                         # 单条视频已被央视下架（页面只剩跳错误页的脚本）
    match = (re.search(r'<div class="content_area"[^>]*>(.*?)</div>', text, re.S)
             or re.search(r'<div class="cnt_bd"[^>]*>(.*?)</div>', text, re.S))
    if not match:
        raise RuntimeError(f"新闻联播正文页结构改变: {url}")
    body = re.sub(r"</p>|<br\s*/?>", "\n", match.group(1))
    body = _html.unescape(re.sub(r"<[^>]+>", "", body))
    body = "\n".join(line.strip() for line in body.splitlines() if line.strip())
    return re.sub(r"^央视网消息\s*[（(]新闻联播[)）]\s*[：:]", "", body)


@_v39_contract
def cctv_news(date, with_content=True):
    """央视《新闻联播》当日条目（央视网官方页面）— 标题 + 文字稿。

    with_content=True 会逐条打开详情页取正文（约 15 次请求）；False 只要标题和链接。
    个别老视频已被下架，其 content 为 None（标题仍在）。
    内容以时政为主：可用于政策信号研究，**做短视频文案时不要引用**。
    """
    ymd = _v39_date(date).replace("-", "")
    url = CCTV_DAY_URL.format(ymd=ymd)
    response = _v39_http(url, allow_status=(404,))
    if response.status_code == 404:
        raise ValueError(f"{date} 没有新闻联播页面（日期过早或尚未发布，当晚约 20:00 后更新）")
    text = response.content.decode("utf-8", "replace")
    rows = []
    # 央视网改版过三次：2016 标题是 <a> 的文本，2019–2020 在 <div class="title">，
    # 2021 起在 <a title="">。逐个 <li> 按这三种位置依次找。
    for chunk in text.split("<li")[1:]:
        link = re.search(r'href="([^"]*/VIDE[^"]+)"', chunk)
        if not link:
            continue
        href = link.group(1)
        title = (re.search(r'title="([^"]+)"', chunk) or re.search(r'class="title">(.*?)</div>', chunk, re.S)
                 or re.search(r"<a[^>]*>(.*?)</a>", chunk, re.S))
        title = _html.unescape(re.sub(r"<[^>]+>", "", title.group(1))).strip() if title else ""
        if not title or re.match(r"《新闻联播》\s*\d{8}|新闻联播完整版", title):
            continue                        # 第一条是整期节目视频，不是单条新闻
        title = re.sub(r"^\[视频\]", "", title).strip()
        rows.append({"date": _v39_date(ymd), "title": title,
                     "url": ("https:" + href) if href.startswith("//") else href})
    if not rows:
        raise RuntimeError(f"新闻联播 {ymd} 页面没有解析出条目，结构可能已变")
    if with_content:
        for row in rows:
            row["content"] = _cctv_body(row["url"])
            time.sleep(0.2)
    return _v39_frame(rows, "cctv", url)
```
<!-- v39-cctv-news:end -->

```python
flash = wallstreetcn_lives("a-stock-channel", limit=50)
more = wallstreetcn_lives("a-stock-channel", limit=50, cursor=flash.attrs["next_cursor"])
xwlb = cctv_news("2026-09-18", with_content=False)
```

---

## Layer 6: 基础数据层

### 6.1 mootdx 财务快照（37字段季报数据）

```python
from mootdx.quotes import Quotes

client = tdx_client(check='finance')  # 见 Prerequisites 的 tdx_client()；财务/F10 按 finance 验活（#52：K 线命令失效不影响这里）

# market: 0=深圳, 1=上海
fin = client.finance(symbol='688017')
# 返回 37 个字段的季报快照:
#   liutongguben(流通股本), zongguben(总股本)
#   eps(每股收益), bvps(每股净资产), roe(净资产收益率%)
#   profit(净利润), income(主营收入)
#   meigujingzichan(每股净资产), meigugongjijin(每股公积金)
#   meiguweifeipeili(每股未分配利润)
#   等37个季报财务字段
```

### 6.2 mootdx F10（公司文本资料）

```python
from mootdx.quotes import Quotes

client = tdx_client(check='finance')  # 见 Prerequisites 的 tdx_client()；财务/F10 按 finance 验活（#52：K 线命令失效不影响这里）

# 先用 F10C 列出服务器实际提供的类别，不要写死类别名：
# 请求不存在的类别时 mootdx 不报错，而是返回 {类别: 文本} 的 dict，按字符串切片会抛 TypeError。
for cat in client.F10C(symbol='688017'):
    text = client.F10(symbol='688017', name=cat['name'])
    print(f"=== {cat['name']} ===")
    print(text[:200] if text else "(空)")
```

> **⚠️ 2026-09 起 F10 只剩「最新提示」一类（#52 同一次服务端变化）：** 内置 10 台服务器 2026-09-20 逐台实测，
> `F10C` 只返回「最新提示」（内含 最新提示 / 互动问答 / 最新公告 / 最新报道 / 最新异动 / 大宗交易 / 融资融券 / 风险提示 8 个小节，
> 约 1.2 万字）；原来的公司概况、财务分析、股东研究、股本结构、资本运作、业内点评、行业分析、公司大事 8 类不再返回。
> 替代：行业 / 股本 / 市值 → §6.3；财务 → §6.1、§6.4；股东户数 → §4.3；增减持 → §14.3；回购 → §14.4；质押 → §14.5；
> 公司公告与大事 → §7.1 巨潮。

### 6.3 东财个股基本面（直连 push2 API）

```python
import requests

def eastmoney_stock_info(code: str) -> dict:
    """
    东财个股基本面信息。
    返回: {code, name, industry, total_shares, float_shares, mcap, float_mcap, list_date}
    """
    market_code = em_market_code(code)      # #46
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "fltt": "2", "invt": "2",
        "fields": "f57,f58,f84,f85,f127,f116,f117,f189,f43",
        "secid": f"{market_code}.{code}",
    }
    headers = {"User-Agent": UA}
    r = em_get(url, params=params, headers=headers, timeout=10)
    d = r.json().get("data", {})
    return {
        "code": d.get("f57", ""),
        "name": d.get("f58", ""),
        "industry": d.get("f127", ""),
        "total_shares": d.get("f84", 0),     # 总股本(股)
        "float_shares": d.get("f85", 0),     # 流通股(股)
        "mcap": d.get("f116", 0),            # 总市值(元)
        "float_mcap": d.get("f117", 0),      # 流通市值(元)
        "list_date": str(d.get("f189", "")), # 上市日期 YYYYMMDD
        "price": d.get("f43", 0),
    }

# 用法
info = eastmoney_stock_info("688017")
print(f"{info['name']}({info['code']}): 行业={info['industry']} 总市值={info['mcap']/1e8:.0f}亿 上市={info['list_date']}")
```

### 6.4 新浪财报三表（资产负债表/利润表/现金流量表）

```python
import requests

def sina_financial_report(code: str, report_type: str = "lrb", num: int = 8) -> list[dict]:
    """
    新浪财报三表。
    code: 6位代码
    report_type: "fzb"(资产负债表) / "lrb"(利润表) / "llb"(现金流量表)
    num: 取最近 N 期（默认 8 期）
    返回: 按报告期倒序的记录列表，每期一条 dict：
          {"报告期": "2026-03-31", "<科目>": "<值>", "<科目>_同比": <同比>, ...}
          （item_value 为新浪原始字符串数值，仅在有同比时附 "_同比" 键）
    """
    prefix = get_prefix(code)               # #46：51x/588x/900x 也是沪市
    paper_code = f"{prefix}{code}"
    url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
    params = {
        "paperCode": paper_code,
        "source": report_type,
        "type": "0",
        "page": "1",
        "num": str(num),
    }
    headers = {"User-Agent": UA}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    # 新浪实际结构: result.data.report_list 是「按报告期(如 '20260331')为键」的 dict,
    # 每期对象的 data 字段才是行项列表 [{item_title, item_value, item_tongbi}]。
    # #46 同因：任一层为 null 时 `.get(k, {})` 返回 None，链式 .get 会 AttributeError
    _j = r.json() or {}
    report_list = ((_j.get("result") or {}).get("data") or {}).get("report_list") or {}

    rows = []
    for period in sorted(report_list.keys(), reverse=True)[:num]:
        obj = report_list[period]
        rec = {"报告期": f"{period[:4]}-{period[4:6]}-{period[6:8]}"}
        for it in obj.get("data", []) or []:
            title = it.get("item_title", "")
            if not title or it.get("item_value") is None:
                continue
            rec[title] = it.get("item_value")
            tongbi = it.get("item_tongbi")
            if tongbi not in (None, ""):
                rec[title + "_同比"] = tongbi
        rows.append(rec)
    return rows

# 用法: 利润表
lrb = sina_financial_report("600519", "lrb")
for item in lrb[:3]:
    print(f"报告期: {item.get('报告期', '')} 净利润: {item.get('净利润', '')}")

# 用法: 资产负债表
fzb = sina_financial_report("600519", "fzb")

# 用法: 现金流量表
llb = sina_financial_report("600519", "llb")
```

---

### 6.5 baostock 估值历史 — PE/PB/PS/PCF + 换手率 + 停牌 + ST（V3.7.0 新增）

**核心价值：** §1.1 腾讯只给**当日**估值快照，本端点给**日频历史序列**（可回溯至 2016），
一次调用同时拿到四个我们此前完全没有的字段：**换手率**（筹码分布的必需输入）、
**停牌状态**、**ST 标记**、**历史估值**。

🔴 **北交所不支持**：baostock 服务端直接拒绝 4/8/92/920 号段，报
`10004011 股票代码未标识sh或sz`（2026-08-19 实测）。本实现在**登录前**就拦掉并抛 `ValueError`，
不浪费一次会话，也不会静默返回空表。

```python
from contextlib import contextmanager

import baostock as bs
import pandas as pd


@contextmanager
def bs_session():
    """baostock 登录会话 — 必须用上下文管理器，异常路径也保证 logout"""
    lg = bs.login()
    if lg.error_code != "0":
        raise RuntimeError(f"baostock 登录失败: {lg.error_code} {lg.error_msg}")
    try:
        yield
    finally:
        bs.logout()


def _rs_to_df(rs) -> pd.DataFrame:
    """baostock ResultData → DataFrame；错误码转异常，绝不静默返回空表"""
    if rs.error_code != "0":
        raise RuntimeError(f"baostock 查询失败: {rs.error_code} {rs.error_msg}")
    rows = []
    while rs.next():
        rows.append(rs.get_row_data())
    return pd.DataFrame(rows, columns=rs.fields)


def _bs_code(code: str) -> str:
    """6位代码 → baostock 格式；北交所在登录前就拦掉"""
    code = str(code).zfill(6)
    if code[:2] in ("60", "68", "90"):
        return f"sh.{code}"
    if code[:2] in ("00", "30", "20"):
        return f"sz.{code}"
    raise ValueError(
        f"baostock 不支持该代码: {code}（北交所 4/8/92/920 号段会被服务端拒绝，"
        f"报 10004011 股票代码未标识sh或sz）。北交所估值请改用 §1.1 腾讯当日快照。"
    )


def baostock_valuation_history(code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """估值历史序列 — PE/PB/PS/PCF + 换手率 + 停牌 + ST，日频"""
    bs_code = _bs_code(code)          # 先校验，失败就不必登录
    fields = "date,code,close,peTTM,pbMRQ,psTTM,pcfNcfTTM,turn,tradestatus,isST"
    with bs_session():
        rs = bs.query_history_k_data_plus(
            bs_code, fields, start_date=start_date, end_date=end_date,
            frequency="d", adjustflag="3",     # 3=不复权，与 §1.2 tencent_kline(adjust='') 口径一致
        )
        df = _rs_to_df(rs)
    for c in ("close", "peTTM", "pbMRQ", "psTTM", "pcfNcfTTM", "turn"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


# 用法
df = baostock_valuation_history("600519", "2016-01-04", "2026-08-18")
print(len(df), "行", df.iloc[0]["date"], "→", df.iloc[-1]["date"])
print(df.tail(2)[["date", "close", "peTTM", "pbMRQ", "psTTM", "turn", "isST"]].to_string(index=False))
# 实测 2026-08-19：2581 行；2026-08-18 peTTM=19.93 pbMRQ=6.46 psTTM=9.37 turn=0.3098

# ST 标记实测有效：000004 在 2024-01 至今的 610 个交易日里有 276 天 isST=1
st = baostock_valuation_history("000004", "2024-01-01", "2026-08-18")
print("isST 分布:", st["isST"].value_counts().to_dict())     # {'0': 334, '1': 276}

# 停牌：tradestatus == "0"
print("停牌天数:", (df["tradestatus"] == "0").sum())
```

**字段说明**

| 字段 | 含义 | 备注 |
|------|------|------|
| `peTTM` `pbMRQ` `psTTM` `pcfNcfTTM` | 市盈率TTM / 市净率MRQ / 市销率TTM / 市现率TTM | 负值代表亏损，不要直接排序 |
| `turn` | 换手率（**百分数**，0.31 = 0.31%） | §4.6 筹码分布的必需输入 |
| `tradestatus` | `1`=正常交易 `0`=停牌 | 算指标前应过滤掉停牌日 |
| `isST` | `1`=ST/*ST `0`=正常 | 历史逐日标记，可还原「当时是不是 ST」 |

---

### 6.6 baostock 标的基本信息 — 上市日 / 退市日 / 状态（V3.7.0 新增）

**核心价值：** 唯一能拿到**退市日期**的零鉴权源。配合 §1.1 的 `is_stale` 僵尸报价标志，
可以在回测/筛选阶段直接剔除已退市标的。

```python
def baostock_stock_basic(code: str) -> dict:
    """标的基本信息 — ipoDate(上市日) / outDate(退市日，在市为空) / status(1=上市 0=退市)"""
    bs_code = _bs_code(code)
    with bs_session():
        df = _rs_to_df(bs.query_stock_basic(code=bs_code))
    return df.iloc[0].to_dict() if not df.empty else {}


# 用法
print(baostock_stock_basic("600519"))
# 实测：{'code': 'sh.600519', 'code_name': '贵州茅台', 'ipoDate': '2001-08-27',
#        'outDate': '', 'type': '1', 'status': '1'}   ← outDate 为空 = 仍在市
```

> 🔴 **已退市标的的除权除息，三个源全缺**（2026-08 交叉验证）：通达信 `xdxr()` 即使传对
> `market=2` 也返回 0 条、东财历史快照同样没有、baostock 直接拒绝北交所代码。
> 已退市标的（尤其北交所）**做复权必然对不上**，不是本工具包的缺陷，是源侧的保留策略。

---

### 6.7 申万行业分类历史 — 消除行业前视偏差（V3.7.0 新增）

**核心价值：** §3.7 `industry_comparison()` 用东财，**只有当前归属**。做历史研究时用今天的
行业分类去套过去，是典型的**前视偏差**。本端点给出每只股票的**行业变迁史**。

⚠️ 申万官方只发布**代码**不发布中文名（名称表是另一份未公开发布）。
东财/通达信的行业名**不能**直接套——分类体系不同，代码不通用。

```python
import io

from typing import Optional

import pandas as pd
import requests

SW_URL = "https://www.swsresearch.com/swindex/pdf/SwClass2021/StockClassifyUse_stock.xls"


def sw_industry_history() -> pd.DataFrame:
    """申万行业归属变迁史 — 每只股票每次行业调整一行"""
    try:
        r = requests.get(SW_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
        r.raise_for_status()
    except requests.exceptions.SSLError as e:
        # 2026-08-19 实测：纯 certifi 环境握手正常，证书链完整，无需手动补中间证书。
        # 保留此分支是为了在站点证书回归时给出可操作的提示，而不是吞掉异常。
        raise RuntimeError(
            "申万站点 SSL 握手失败。2026-08 实测其证书链正常，若你遇到此错误，"
            "多半是本机 CA 包过旧或中间人代理：先试 `pip install -U certifi`。"
            f"原始错误: {e}"
        ) from e
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"股票代码": "code", "计入日期": "start_date",
                            "行业代码": "industry_code", "更新日期": "update_date"})
    missing = {"code", "start_date", "industry_code"} - set(df.columns)
    if missing:
        raise RuntimeError(f"申万表结构变了，缺列 {sorted(missing)}；实际列={list(df.columns)}")
    df["code"] = df["code"].astype(str).str.zfill(6)
    df["industry_code"] = df["industry_code"].astype(str).str.zfill(6)
    # 层级码要补成规范的 6 位（申万官方一级是 480000、二级是 480300），
    # 直接截断成 "48"/"4803" 无法与官方指数/名称表 join。
    df["l1_code"] = df["industry_code"].str[:2] + "0000"    # 一级，如 480000
    df["l2_code"] = df["industry_code"].str[:4] + "00"      # 二级，如 480300
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    return df.sort_values(["code", "start_date"]).reset_index(drop=True)


def sw_industry_as_of(df: pd.DataFrame, code: str, as_of: str) -> Optional[dict]:
    """某只股票在 as_of 日所属的申万行业（取不晚于该日的最后一次调整）"""
    code = str(code).zfill(6)
    sub = df[(df["code"] == code) & (df["start_date"] <= pd.Timestamp(as_of))]
    if sub.empty:
        return None                  # 该日尚未上市 / 无归属记录
    row = sub.iloc[-1]
    return {"code": code, "as_of": as_of,
            "industry_code": row["industry_code"],
            "l1_code": row["l1_code"], "l2_code": row["l2_code"],
            "since": row["start_date"].strftime("%Y-%m-%d")}


# 用法
sw = sw_industry_history()
print(len(sw), "行 |", sw["code"].nunique(), "只标的 |",
      sw["l1_code"].nunique(), "个一级行业")
# 实测 2026-08-19：12893 行 | 5905 只 | 38 个一级 / 194 个二级 / 553 个三级

# 前视偏差验证：平安银行在不同时点属于不同行业
for d in ("2013-01-01", "2016-01-01", "2026-08-18"):
    print(d, sw_industry_as_of(sw, "000001", d))
# 2013-01-01 → 440101（一级 440000，自 1991-04-03）
# 2016-01-01 → 480101（一级 480000，自 2014-02-21）
# 2026-08-18 → 480301（一级 480000 / 二级 480300，自 2021-07-30）
```

> **典型用法：** 做行业轮动回测时，每个调仓日调用 `sw_industry_as_of()` 取**当时**的归属，
> 而不是用一张当前分类表贯穿全程。实测有标的历史上变更过 **10 次**行业。

### 6.8 ST / *ST 名单 — 全市场风险警示快照（V3.9.0 新增）

沪深走东财「风险警示板」过滤（含 B 股）；北交所不在这个过滤里，改为拉北交所全表按名称筛。
东财 push2 与 push2delay 都连不上时，退到 §6.5 baostock 证券列表按名称筛——**只有沪深、没有价格**，
`attrs['coverage']` 与 `attrs['fallback_reason']` 会写明。走 push2delay 时价格约有 15 分钟延迟（`source_url` 可看出走的哪个域）。
需要回测用的**历史** ST 状态，用 §6.5 `baostock_valuation_history()` 的 `isST` 列。

<!-- v39-st-list:start -->
```python
import requests

EM_CLIST_HOSTS = ["https://push2.eastmoney.com", "https://push2delay.eastmoney.com"]


def _em_clist_all(fs, fields, page_size=100):
    """东财 clist 全量翻页。主域网络失败时换 push2delay（同一接口，行情延迟约 15 分钟）。
    网络层全部失败抛 requests.ConnectionError；服务端返回异常内容（含非 JSON 的错误页）抛 RuntimeError，
    不换域重试，也不会让 st_stock_list 退到只有沪深的备胎。"""
    errors = []
    for host in EM_CLIST_HOSTS:
        url = host + "/api/qt/clist/get"
        rows, page, total = [], 1, None
        try:
            while True:
                response = em_get(url, params={"pn": page, "pz": page_size, "po": 1, "np": 1,
                                               "fltt": 2, "invt": 2, "fid": "f12",
                                               "fs": fs, "fields": fields}, timeout=15)
                response.raise_for_status()
                payload = _v39_json(response)
                data = payload.get("data") if isinstance(payload, dict) else None
                if not isinstance(data, dict) or payload.get("rc") != 0 or not data:
                    raise RuntimeError(f"东财 clist 返回异常或无数据（fs={fs}）: {str(payload)[:100]}")
                page_total = _v39_count(data.get("total"), f"东财 clist total（fs={fs}）")
                diff = _v39_rows(data.get("diff"), f"东财 clist 的 diff（fs={fs}）")
                if total is None:
                    total = page_total
                elif page_total != total:   # 翻页途中名单变了：拼出来的是两份名单的混合
                    raise RuntimeError(f"东财 clist 翻页时 total 从 {total} 变成 {page_total}，请重试")
                rows.extend(diff)
                if not diff or len(rows) >= total:
                    break
                page += 1
        except requests.RequestException as exc:
            errors.append(f"{host}: {type(exc).__name__}")
            continue
        if len(rows) != total:
            raise RuntimeError(f"东财 clist 翻页后 {len(rows)} 条，与 total={total} 不符")
        return rows, url
    raise requests.ConnectionError("东财 push2 / push2delay 均不可达: " + "; ".join(errors))


@_v39_contract
def st_stock_list():
    """全市场 ST / *ST 名单（风险警示）— 当日快照。

    沪深：东财「风险警示板」过滤（含 B 股）；北交所：东财不纳入该过滤，改为拉北交所全表按名称筛。
    东财两个域名都连不上时退到 baostock 证券列表按名称筛（**只有沪深、没有价格**，attrs 里注明）。
    price / pct_change 在走 push2delay 时约有 15 分钟延迟（source_url 可看出走的是哪个域）。
    """
    fields = "f12,f13,f14,f2,f3"
    try:
        shsz, url = _em_clist_all("m:0+f:4,m:1+f:4", fields)
        bj, bj_url = _em_clist_all("m:0+t:81+s:2048", fields)
    except requests.ConnectionError as exc:
        return _st_list_baostock(str(exc))
    # 两边原始集合都不该为空：北交所全表空了还标「沪深京」，会把缺失说成「北交所没有 ST」
    if not shsz or not bj:
        raise RuntimeError(f"东财风险警示板 {len(shsz)} 条、北交所全表 {len(bj)} 条，"
                           "有一边为空，不能当成沪深京完整名单")
    if bj_url != url:
        url = url + " | " + bj_url      # 两次调用可能落在不同域名（push2 / push2delay）
    rows = []
    for rec, is_bj in [(r, False) for r in shsz] + [(r, True) for r in bj]:
        # 代码 / 市场号 / 名称都是身份字段：f13 缺失或变样按「深市」处理会给出错误市场，
        # 名称为空则北交所那半边会被静默筛掉，结果却仍标「沪深京」。
        # 2026-09-20 实测两张表共 562 行：f12 全是 6 位、f13 只有 int 0/1、f14 无空值。
        code, market_id, name = rec["f12"], rec["f13"], str(rec["f14"]).strip()
        if (not re.fullmatch(r"[0-9]{6}", str(code)) or isinstance(market_id, bool)
                or market_id not in (0, 1)):
            raise RuntimeError(f"东财 clist 返回了认不出的代码 / 市场号: f12={code!r} f13={market_id!r}")
        if not name:
            raise RuntimeError(f"东财 clist 里 {code} 没有名称，ST 判定要靠名称，不能当成完整名单")
        if is_bj and "ST" not in name.upper():
            continue
        rows.append({"code": code,
                     "market": "bj" if is_bj else ("sh" if market_id == 1 else "sz"),
                     "name": name, "st_type": "*ST" if name.startswith("*") else "ST",
                     "price": _v39_num(rec.get("f2")), "pct_change": _v39_num(rec.get("f3"))})
    frame = _v39_frame(rows, "eastmoney", url)
    if frame.empty or frame.duplicated(["code"]).any():
        raise RuntimeError("ST 名单为空或代码重复，不能当成完整快照")
    frame.attrs["coverage"] = "沪深京"
    return frame


def _st_list_baostock(reason):
    import baostock as bs
    # 用名称模糊查询（约 300 条、2 秒）；不带参数的全量查询实测会在服务端卡住
    with bs_session():
        basic = _rs_to_df(bs.query_stock_basic(code_name="ST"))
    # type 1 = 股票，status 1 = 上市
    picked = basic[(basic["type"] == "1") & (basic["status"] == "1")
                   & basic["code_name"].str.upper().str.contains("ST")]
    rows = [{"code": c.split(".")[1], "market": c.split(".")[0], "name": n,
             "st_type": "*ST" if n.startswith("*") else "ST", "price": None, "pct_change": None}
            for c, n in zip(picked["code"], picked["code_name"])]
    frame = _v39_frame(rows, "baostock", "baostock.query_stock_basic")
    if frame.empty:
        raise RuntimeError("baostock 证券列表里没有筛出 ST，结果不可信")
    frame.attrs["coverage"] = "沪深（东财不可达，baostock 不含北交所）"
    frame.attrs["fallback_reason"] = reason
    return frame
```
<!-- v39-st-list:end -->

```python
st = st_stock_list()
print(st.attrs["coverage"], len(st), st.st_type.value_counts().to_dict())
```

---

## Layer 7: 公告层

### 7.1 巨潮公告（直连 cninfo.com.cn）

```python
import requests
from datetime import datetime

def _cninfo_ts_to_date(ts):
    """巨潮 announcementTime 返回 Unix 毫秒整数，需转换为日期字符串。"""
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
    return str(ts)[:10] if ts else ""

# 巨潮 股票→orgId 映射（模块级缓存，首次调用时拉取一次，全程复用）
_CNINFO_ORGID_MAP = {}

def _cninfo_orgid(code: str) -> str:
    """查股票真实 orgId。巨潮 orgId 并非统一 `gssx0{code}` 格式（如 601318→9900002221、
    601398→jjxt0000019、688017→9900041602），硬编码会导致大量股票（尤其 601xxx 段）
    返回 totalAnnouncement=0、查不到公告（#19）。优先动态查官方映射表，查不到再回退硬编码。"""
    global _CNINFO_ORGID_MAP
    if not _CNINFO_ORGID_MAP:
        try:
            r = requests.get("http://www.cninfo.com.cn/new/data/szse_stock.json",
                             headers={"User-Agent": UA}, timeout=15)
            _CNINFO_ORGID_MAP = {s["code"]: s["orgId"]
                                 for s in r.json().get("stockList", [])}
        except Exception as e:
            print(f"[WARN] 巨潮 orgId 映射表拉取失败，回退硬编码规则: {e}")
    org = _CNINFO_ORGID_MAP.get(code)
    if org:
        return org
    # fallback：老格式（仅部分老股票如 600519/600036 适用）
    # #46：改用 get_prefix()，原先只认 6/8/4，会把 51x 沪 ETF、900x 沪 B、920x 北交所判错
    return f"gs{get_prefix(code)}0{code}"

def cninfo_announcements(code: str, page_size: int = 30) -> list[dict]:
    """
    巨潮公告全文检索。
    返回: [{title, type, date, url}]
    """
    url = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
    org_id = _cninfo_orgid(code)   # 动态查真实 orgId（#19 修复，自带硬编码 fallback）

    payload = {
        "stock": f"{code},{org_id}",
        "tabName": "fulltext",
        "pageSize": str(page_size),
        "pageNum": "1",
        "column": "",
        "category": "",
        "plate": "",
        "seDate": "",
        "searchkey": "",
        "secid": "",
        "sortName": "",
        "sortType": "",
        "isHLtitle": "true",
    }
    headers = {
        "User-Agent": UA,
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.cninfo.com.cn/new/disclosure",
        "Origin": "https://www.cninfo.com.cn",
    }
    r = requests.post(url, data=payload, headers=headers, timeout=15)
    d = r.json()

    rows = []
    for item in d.get("announcements", []) or []:
        rows.append({
            "title": item.get("announcementTitle", ""),
            "type": item.get("announcementTypeName", ""),
            "date": _cninfo_ts_to_date(item.get("announcementTime")),
            "url": f"https://www.cninfo.com.cn/new/disclosure/detail?annoId={item.get('announcementId', '')}",
        })
    return rows

# 用法
anns = cninfo_announcements("688017")
for a in anns[:10]:
    print(f"  {a['date']} | {a['type']} | {a['title']}")
```

### 7.2 mootdx F10 公告摘要

```python
from mootdx.quotes import Quotes
client = tdx_client(check='finance')  # 见 Prerequisites 的 tdx_client()；财务/F10 按 finance 验活（#52：K 线命令失效不影响这里）
text = client.F10(symbol='688017', name='最新提示')
# 包含最近的公告/分红/股东大会决议等摘要
```

---

## Layer 8: 打板层（涨停 / 炸板 / 跌停 / 题材情绪，V3.3.0 新增）

> 连板梯队、炸板率、晋级率、涨停原因题材——打板与题材跟踪的高频需求（#23 / #15）。东财四池走 `push2ex.eastmoney.com`（与现有 push2 同源，已纳入 `em_get()` 限流）；涨停原因题材增强用同花顺。**全部免登录、零鉴权。**

### 8.1 东财涨停板池 — 涨停 / 炸板 / 跌停 / 昨日涨停

```python
import requests

ZTB_UT = "7eea3edcaed734bea9cbfc24409ed989"

def _fmt_zt_time(t) -> str:
    """涨停板时间整数 → HH:MM:SS（92500 → 09:25:00）。"""
    s = str(t).zfill(6)
    return f"{s[0:2]}:{s[2:4]}:{s[4:6]}"

def _em_zt_api(endpoint: str, sort: str, date: str) -> list[dict]:
    """东财涨停板行情中心通用请求（push2ex，走 em_get 限流）。
    endpoint: getTopicZTPool / getTopicZBPool / getTopicDTPool / getYesterdayZTPool
    返回 data.pool 原始列表（data 为 null = 非交易日 / 参数错）。"""
    url = f"https://push2ex.eastmoney.com/{endpoint}"
    params = {"ut": ZTB_UT, "dpt": "wz.ztzt", "Pageindex": 0,
              "pagesize": 10000, "sort": sort, "date": date}
    headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
    try:
        r = em_get(url, params=params, headers=headers, timeout=10)
        return (r.json().get("data") or {}).get("pool") or []
    except Exception as e:
        print(f"[WARN] 涨停板池 {endpoint} 请求失败: {e}")
        return []

def em_zt_pool(date: str) -> list[dict]:
    """涨停池。date=YYYYMMDD（交易日）。
    返回每只: code/name/price/pct/amount/float_cap/turnover/limit_days(连板数)/
    first_seal/last_seal(封板时间)/seal_fund(封板资金,元)/break_times(炸板次数)/
    industry/zt_stat(N天M板)"""
    out = []
    for p in _em_zt_api("getTopicZTPool", "fbt:asc", date):
        out.append({"code": p["c"], "name": p["n"], "price": p["p"] / 1000,
            "pct": round(p["zdp"], 2), "amount": p["amount"], "float_cap": p["ltsz"],
            "turnover": round(p["hs"], 2), "limit_days": p["lbc"],
            "first_seal": _fmt_zt_time(p["fbt"]), "last_seal": _fmt_zt_time(p["lbt"]),
            "seal_fund": p["fund"], "break_times": p["zbc"], "industry": p.get("hybk", ""),
            "zt_stat": f'{(p.get("zttj") or {}).get("days","?")}天{(p.get("zttj") or {}).get("ct","?")}板'})
    return out

def em_zb_pool(date: str) -> list[dict]:
    """炸板池（涨停后开板）。返回 code/name/price/limit_price(涨停价)/pct/turnover/
    first_seal/break_times/amplitude(振幅)/speed(涨速)/industry/zt_stat"""
    out = []
    for p in _em_zt_api("getTopicZBPool", "fbt:asc", date):
        out.append({"code": p["c"], "name": p["n"], "price": p["p"] / 1000,
            "limit_price": p["ztp"] / 1000, "pct": round(p["zdp"], 2),
            "turnover": round(p["hs"], 2), "first_seal": _fmt_zt_time(p["fbt"]),
            "break_times": p["zbc"], "amplitude": round(p["zf"], 2),
            "speed": round(p["zs"], 2), "industry": p.get("hybk", ""),
            "zt_stat": f'{(p.get("zttj") or {}).get("days","?")}天{(p.get("zttj") or {}).get("ct","?")}板'})
    return out

def em_dt_pool(date: str) -> list[dict]:
    """跌停池。返回 code/name/price/pct/turnover/pe/seal_fund(封单资金)/last_seal/
    board_amount(板上成交额)/dt_days(连续跌停)/open_times(开板次数)/industry"""
    out = []
    for p in _em_zt_api("getTopicDTPool", "fund:asc", date):
        out.append({"code": p["c"], "name": p["n"], "price": p["p"] / 1000,
            "pct": round(p["zdp"], 2), "turnover": round(p["hs"], 2), "pe": p.get("pe"),
            "seal_fund": p["fund"], "last_seal": _fmt_zt_time(p["lbt"]),
            "board_amount": p.get("fba"), "dt_days": p.get("days"),
            "open_times": p.get("oc"), "industry": p.get("hybk", "")})
    return out

def em_yzt_pool(date: str) -> list[dict]:
    """昨日涨停池（昨涨停今表现，算晋级率/赚钱效应）。返回 code/name/price/
    pct(今日涨幅)/turnover/amplitude/speed/y_first_seal(昨封板时间)/
    y_limit_days(昨连板)/industry/zt_stat"""
    out = []
    for p in _em_zt_api("getYesterdayZTPool", "zs:desc", date):
        out.append({"code": p["c"], "name": p["n"], "price": p["p"] / 1000,
            "pct": round(p["zdp"], 2), "turnover": round(p["hs"], 2),
            "amplitude": round(p["zf"], 2), "speed": round(p["zs"], 2),
            "y_first_seal": _fmt_zt_time(p["yfbt"]), "y_limit_days": p["ylbc"],
            "industry": p.get("hybk", ""), "zt_stat": f'{(p.get("zttj") or {}).get("days","?")}天{(p.get("zttj") or {}).get("ct","?")}板'})
    return out

# 用法
zt = em_zt_pool("20260626")
print(f"今日涨停 {len(zt)} 只")
for s in zt[:3]:
    print(f"  {s['name']} {s['zt_stat']} 封板{s['seal_fund']/1e8:.2f}亿 {s['industry']}")
```

> **坑：** ① 价格字段 `price`/`limit_price` 已 ÷1000（原始值是 ×1000 整数）。② 四池只有 `sort` 不同（涨停/炸板=`fbt:asc`、跌停=`fund:asc`、昨涨停=`zs:desc`），`dpt` 都是 `wz.ztzt`。③ `date` 必须传交易日，非交易日 `data` 返回 null。④ 金额单位均为**元**。

### 8.2 同花顺涨停揭秘 — 涨停原因题材 + 封板成功率 + 板型

```python
from datetime import datetime

def ths_limit_up_pool(date: str) -> list[dict]:
    """同花顺涨停揭秘（涨停原因 + 封板质量增强源）。date=YYYYMMDD。
    返回每只: code/name/price/pct/reason(涨停原因题材)/board_type(换手板/一字板/T字板)/
    seal_rate(封板成功率,0~1)/break_times(炸板次数)/seal_amount(封单额,元)/
    high_days(几天几板)/first_time(首次涨停时间)/is_again(是否回封 0/1)"""
    url = "https://data.10jqka.com.cn/dataapi/limit_up/limit_up_pool"
    params = {"page": 1, "limit": 200,
              "field": "199112,10,9001,330323,330324,330325,9002,330329,133971,133970,1968584,3475914,9003,9004",
              "filter": "HS,GEM2STAR", "order_field": "330324", "order_type": "0", "date": date}
    try:
        r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=10)
        info = (r.json().get("data") or {}).get("info", [])
    except Exception as e:
        print(f"[WARN] 同花顺涨停揭秘请求失败: {e}")
        return []
    out = []
    for it in info:
        ft = it.get("first_limit_up_time")
        out.append({"code": it.get("code"), "name": it.get("name"),
            "price": it.get("latest"), "pct": it.get("change_rate"),
            "reason": it.get("reason_type", ""), "board_type": it.get("limit_up_type", ""),
            "seal_rate": it.get("limit_up_suc_rate"), "break_times": it.get("open_num") or 0,
            "seal_amount": it.get("order_amount"), "high_days": it.get("high_days", ""),
            "first_time": datetime.fromtimestamp(int(ft)).strftime("%H:%M:%S") if ft else "",
            "is_again": it.get("is_again_limit")})
    return out

# 用法: 涨停原因题材归因
for s in ths_limit_up_pool("20260626")[:5]:
    print(f"  {s['name']} {s['high_days']} | {s['reason']} | 封板率{s['seal_rate']}")
```

> **坑：** `first_limit_up_time` 是 **Unix 秒时间戳**（要 `datetime.fromtimestamp`），不是 HHMMSS。`field` 那串是同花顺内部字段 ID，照抄即可。`filter=HS,GEM2STAR` 控制板块范围（沪深主板 + 创业板 + 科创板）。

### 8.3 打板情绪速算 — 炸板率 / 连板高度 / 连板梯队

```python
def limit_up_sentiment(date: str) -> dict:
    """打板情绪温度计：连板梯队 + 炸板率 + 涨跌停对比。"""
    zt, zb, dt = em_zt_pool(date), em_zb_pool(date), em_dt_pool(date)
    ladder = {}
    for s in zt:
        ladder[s["limit_days"]] = ladder.get(s["limit_days"], 0) + 1
    zt_n, zb_n = len(zt), len(zb)
    return {"date": date, "zt_count": zt_n, "zb_count": zb_n, "dt_count": len(dt),
        "break_rate": round(zb_n / (zt_n + zb_n) * 100, 1) if (zt_n + zb_n) else 0,  # 炸板率%
        "max_height": max((s["limit_days"] for s in zt), default=0),                 # 最高连板
        "ladder": dict(sorted(ladder.items()))}                                       # 连板梯队 {板数:家数}

# 用法
s = limit_up_sentiment("20260626")
print(f"涨停{s['zt_count']} 炸板{s['zb_count']}(炸板率{s['break_rate']}%) "
      f"跌停{s['dt_count']} 最高{s['max_height']}连板")
print(f"连板梯队: {s['ladder']}")
```

> 晋级率（昨涨停今仍涨停 / 昨涨停总数）可用 `em_yzt_pool()` 的 `pct >= 9.8` 计数除以总数自算。

### 8.4 东财重点监控池（V3.6.0 新增 · #15）

东财 App「重点监控」名单：被交易所风险警示 / 重点监控的标的及其**生效时间窗**。零鉴权静态 JSON，全量返回不分页。

```python
from datetime import datetime, timedelta, timezone   # 不要 import datetime 模块：§8.2 的 `from datetime import datetime` 会遮蔽它

# A 股的"今天"按北京时间算。用本机 date.today() 在海外时区会错开一天
# （如新西兰比北京早 4~5 小时，北京傍晚时本机已跨到次日），
# 监控窗口首日/末日会因此提前纳入或提前剔除。
CN_TZ = timezone(timedelta(hours=8))

def cn_today() -> str:
    """北京时间的今天（YYYY-MM-DD）。"""
    return datetime.now(CN_TZ).date().isoformat()

MONITOR_URL = "https://mobappconfig.securities.eastmoney.com/emcfg/stock_monitor.json"

# ⚠️ MARKET 是三值且**含字母 "B"**（北交所），不是 0/1 二值。
# 写成 `"SH" if MARKET=="1" else "SZ"` 会把北交所标的整片错标成 SZ——
# 实测 2026-07-31 全量 16 只里就有 3 只 MARKET="B"（*ST康乐 920575 等）。
_MONITOR_MARKET = {"1": "SH", "0": "SZ", "B": "BJ"}

def em_stock_monitor(only_active: bool = True) -> list[dict]:
    """东财重点监控池。
    only_active=True 只留今天仍在监控窗口内的（按 VALIDATESTARTDATE~VALIDATEENDDATE 过滤）。
    返回: [{code, name, market, start, end, link}]
    """
    r = em_get(MONITOR_URL, headers={"Referer": "https://vipmoney.eastmoney.com/"}, timeout=20)
    rows = r.json() or []
    today = cn_today()
    out = []
    for x in rows:
        start, end = x.get("VALIDATESTARTDATE", ""), x.get("VALIDATEENDDATE", "")
        if only_active and not (start <= today <= end):
            continue
        raw_mkt = str(x.get("MARKET", "")).upper()
        out.append({
            "code":   x.get("STKCODE", ""),
            "name":   x.get("STKNAME", ""),
            # 未知取值不猜市场，原样带出（`?<原值>`），避免静默标错
            "market": _MONITOR_MARKET.get(raw_mkt, f"?{raw_mkt}"),
            "start":  start, "end": end,
            "link":   x.get("LINK_URL", ""),
        })
    return out

# 用法
pool = em_stock_monitor()
print(f"当前重点监控 {len(pool)} 只")
for s in pool[:5]:
    print(f"  {s['code']} {s['name']}({s['market']}) 监控期 {s['start']}~{s['end']}")
```

| 字段 | 含义 |
|------|------|
| STKCODE / STKNAME | 代码 / 名称 |
| MARKET | `"1"`=沪市，`"0"`=深市，**`"B"`=北交所**（三值且含字母，别当 0/1 二值处理） |
| VALIDATESTARTDATE / VALIDATEENDDATE | 监控生效起 / 止日（通常 14 天窗口） |
| LINK_URL | 东财 App 内详情页（可空） |

### 8.5 东财日内异动池 — 严重异常波动（V3.6.0 新增 · #15）

交易所「严重异常波动」口径的异动标的：连续 N 日同向异动、累计偏离值触发阈值等。两个端点同源，**零鉴权，但必须带 `team=h5` 等固定参数**，否则返回 `{"result":1001,"msg":"unknow team"}`。

```python
ANOMALY_BASE = "https://dycalchis.eastmoney.com/price-anomaly"
# 东财 H5 固定公共参数，缺 team 会被拒（unknow team）
HQ_PARAMS = {"team": "h5", "product": "EastMoney", "client": "WAP",
             "version": "9001", "name": "WAP", "user": "123"}

# 异动规则码（e 字段）→ 文字说明；s==6 且 e∈{4,5,6,7} 时按 e*10 取更严阈值那档
ANOMALY_RULES = {
    1:  "主板连续10个交易日内4次出现同向异常波动",
    2:  "创业板连续10个交易日内3次出现同向异常波动",
    3:  "科创板连续10个交易日内3次出现同向异常波动",
    4:  "连续十个交易日内日收盘价涨跌幅偏离值累计达到+100%",
    5:  "连续十个交易日内日收盘价涨跌幅偏离值累计达到-50%",
    6:  "连续三十个交易日内日收盘价涨跌幅偏离值累计达到+200%",
    7:  "连续三十个交易日内日收盘价涨跌幅偏离值累计达到-70%",
    8:  "北交所连续10个交易日内3次出现同向异常波动",
    40: "连续十个交易日内日收盘价涨跌幅偏离值累计达到+150%",
    50: "连续十个交易日内日收盘价涨跌幅偏离值累计达到-60%",
    60: "连续30个交易日内日收盘价涨跌幅偏离值累计达到+300%",
    70: "连续30个交易日内日收盘价涨跌幅偏离值累计达到-75%",
}

def _anomaly_market(code, m, board=None) -> str:
    """异动记录 → 交易所。
    ⚠️ 不能只看 m：东财体系里**北交所与深市同为 m=0**（拉北交所清单用的就是 `m:0+t:81`），
       只按 `m==1 else "SZ"` 会把北交所标的错标成 SZ——而异动规则码 8 正是北交所专用，
       说明北交所记录确实会出现在本接口。代码号段无歧义，优先用它判。
    """
    c = str(code or "")
    if c.startswith(("4", "8", "92")) or board == 8:   # 与 get_prefix() 同一套号段规则（#51）
        return "BJ"
    return "SH" if m == 1 else "SZ"

def _anomaly_get(path: str, page_size: int, page_no: int, **extra) -> dict:
    params = {**HQ_PARAMS, "pageSize": str(page_size), "pageNo": str(page_no), **extra}
    r = em_get(f"{ANOMALY_BASE}/{path}", params=params,
               headers={"Referer": "https://vipmoney.eastmoney.com/"}, timeout=20)
    d = r.json()
    if d.get("result") != 0:
        # 正向识别：接口用 result!=0 表达拒绝，不能当成「今天没异动」静默吞掉
        raise RuntimeError(f"东财异动接口拒绝: result={d.get('result')} msg={d.get('msg')!r}")
    return d

def em_price_anomaly(page_size: int = 200, page_no: int = 1) -> dict:
    """日内异动明细（price-anomaly/list）。返回 {date, items:[...]}"""
    d = _anomaly_get("list", page_size, page_no)
    items = []
    for x in d.get("data") or []:
        e = x.get("e")
        key = e * 10 if (x.get("s") == 6 and e in (4, 5, 6, 7)) else e
        items.append({
            "code": x.get("c"), "name": x.get("n"),
            "market": _anomaly_market(x.get("c"), x.get("m"), x.get("s")),
            "change_pct": x.get("a"),          # 当日涨跌幅%
            "deviation": x.get("x"),           # 累计偏离值%
            "days": x.get("d"),                # 统计窗口天数
            "board": x.get("s"),               # 板块码：1=主板 4=创业板 6=科创板(阈值加严) 8=北交所
            "rule_code": key,
            "rule": ANOMALY_RULES.get(key, f"未知规则码 {key}"),
            "is_today": x.get("o") != 2,
        })
    return {"date": str(d.get("date", "")), "pages": d.get("pages", 0), "items": items}

def em_price_anomaly_count(page_size: int = 50, page_no: int = 1,
                           sort_key: str = "", sort_dir: str = "") -> dict:
    """异动统计（price-anomaly/count）：按标的聚合的异动次数 + 现价。"""
    d = _anomaly_get("count", page_size, page_no, sortKey=sort_key, sortDir=sort_dir)
    items = [{
        "code": x.get("c"), "name": x.get("n"),
        "market": _anomaly_market(x.get("c"), x.get("m"), x.get("s")),
        "price": x.get("p"),                 # 最新价（已核对腾讯行情，3/3 一致）
        "change_pct": x.get("a"),            # 涨跌幅%（已核对腾讯行情，3/3 一致）
        "times": x.get("t"),                 # 窗口内异动次数
        "deviation": x.get("x"),             # 累计偏离值%
        "days": x.get("d"),                  # 统计窗口天数
        "board": x.get("s"),
    } for x in d.get("data") or []]
    return {"date": str(d.get("date", "")), "pages": d.get("pages", 0), "items": items}

# 用法
a = em_price_anomaly(page_size=200)
print(f"{a['date']} 日内异动 {len(a['items'])} 条")
for s in a["items"][:5]:
    print(f"  {s['code']} {s['name']} {s['change_pct']}% 偏离{s['deviation']}%/{s['days']}日 | {s['rule']}")

c = em_price_anomaly_count(page_size=50)
for s in c["items"][:5]:
    print(f"  {s['code']} {s['name']} {s['price']}元 {s['change_pct']}% 异动{s['times']}次")

# 与重点监控池交叉：异动 且 已在监控名单 = 最高风险
monitor_codes = {x["code"] for x in em_stock_monitor()}
hot = [s for s in a["items"] if s["code"] in monitor_codes]
print(f"异动且在监控池: {[(s['code'], s['name']) for s in hot]}")
```

> **字段来源说明：** `p`/`a`（最新价、涨跌幅）已与腾讯行情逐条核对（3/3 完全一致）；`m`/`c`/`n`/`e`/`x`/`d`/`o` 的语义取自东财前端 `formatNewData` 的字段映射（`x`→DEVUATION_VALUE、`d`→MAX_DAYS、`a`→CHANGE_RATE、`o`→IS_HAPPEN）。
>
> **两端点同名字母含义不同：** `list` 的 `t` 是涨跌幅目标值（浮点），`count` 的 `t` 是异动次数（整数）——不要跨端点复用解析逻辑。
>
> **`open` 字段**为盘口开闭标志；`date` 为交易日（`YYYYMMDD`）。非交易时段返回上一交易日数据，属正常。

---

## Layer 9: ETF 期权层（T型报价 + 希腊字母 + IV，V3.3.0 新增）

> 50ETF / 300ETF / 科创50ETF / 500ETF 期权（#13）。走新浪源——**T型报价、希腊字母、隐含波动率均由交易所/新浪预先算好，无需本地算 BSM**。免费直连，唯一注意带 `Referer`。

### 9.1 合约清单 + T型报价 + 希腊字母

```python
import requests

SINA_OPT_HDR = {"Referer": "https://stock.finance.sina.com.cn/", "User-Agent": UA}

def _opt_f(x):
    try: return float(x)
    except Exception: return x

def _sina_opt_list(param: str) -> list:
    """新浪 hq.sinajs.cn 取值（GBK，逗号分隔，去 var hq_str_XXX="..." 壳）。"""
    r = requests.get(f"https://hq.sinajs.cn/list={param}", headers=SINA_OPT_HDR, timeout=10)
    r.encoding = "gbk"
    t = r.text
    return t.split('"')[1].split(",") if '"' in t else []

def sina_option_codes(underlying: str = "510050", call: bool = True) -> dict:
    """ETF期权合约清单。underlying: 510050/510300/588000/510500。call=True认购/False认沽。
    返回 {月份YYMM: [合约代码,...]}，第一个 key 即近月。"""
    cate = {"510050": "50ETF", "510300": "300ETF",
            "588000": "科创50ETF", "510500": "500ETF"}.get(underlying, "50ETF")
    url = ("https://stock.finance.sina.com.cn/futures/api/openapi.php/"
           f"StockOptionService.getStockName?exchange=null&cate={cate}")
    try:
        months = requests.get(url, headers=SINA_OPT_HDR, timeout=10).json()["result"]["data"]["contractMonth"]
    except Exception as e:
        print(f"[WARN] 期权月份获取失败: {e}")
        return {}
    months = [m.replace("-", "")[2:] for m in months[1:]]  # 丢首个，转 YYMM
    flag = "OP_UP_" if call else "OP_DOWN_"
    out = {}
    for m in months:
        codes = [c.replace("CON_OP_", "") for c in _sina_opt_list(f"{flag}{underlying}{m}")
                 if c.startswith("CON_OP_")]
        if codes:
            out[m] = codes
    return out

def sina_option_tquote(code: str) -> dict:
    """期权T型报价。返回 bid_vol/bid/last/ask/ask_vol/open_interest(持仓量)/pct/
    strike(行权价)/prev_close/open/limit_up/limit_down/name/amplitude/high/low/volume/amount。"""
    v = _sina_opt_list(f"CON_OP_{code}")
    if len(v) < 43:
        return {}
    return {"bid_vol": _opt_f(v[0]), "bid": _opt_f(v[1]), "last": _opt_f(v[2]),
        "ask": _opt_f(v[3]), "ask_vol": _opt_f(v[4]), "open_interest": _opt_f(v[5]),
        "pct": _opt_f(v[6]), "strike": _opt_f(v[7]), "prev_close": _opt_f(v[8]),
        "open": _opt_f(v[9]), "limit_up": _opt_f(v[10]), "limit_down": _opt_f(v[11]),
        "name": v[37], "amplitude": _opt_f(v[38]), "high": _opt_f(v[39]),
        "low": _opt_f(v[40]), "volume": _opt_f(v[41]), "amount": _opt_f(v[42])}

def sina_option_greeks(code: str) -> dict:
    """期权希腊字母 + 隐含波动率。返回 name/volume/delta/gamma/theta/vega/
    iv(隐含波动率,小数)/high/low/trade_code/strike/last/theory(理论价值)。"""
    raw = _sina_opt_list(f"CON_SO_{code}")
    if len(raw) < 16:
        return {}
    v = [raw[0]] + raw[4:]  # ⚠️ raw[1:4] 是 3 个空串，必须跳过否则字段错位
    return {"name": v[0], "volume": _opt_f(v[1]), "delta": _opt_f(v[2]),
        "gamma": _opt_f(v[3]), "theta": _opt_f(v[4]), "vega": _opt_f(v[5]),
        "iv": _opt_f(v[6]), "high": _opt_f(v[7]), "low": _opt_f(v[8]),
        "trade_code": v[9], "strike": _opt_f(v[10]), "last": _opt_f(v[11]), "theory": _opt_f(v[12])}

# 用法: 取 50ETF 近月平值附近一档的 T型报价 + 希腊字母
codes = sina_option_codes("510050", call=True)
near = list(codes)[0]                       # 近月
c = codes[near][len(codes[near]) // 2]      # 中间档≈平值附近
q, g = sina_option_tquote(c), sina_option_greeks(c)
print(f"{q['name']} 行权价{q['strike']} 最新{q['last']} 持仓{q['open_interest']:.0f}")
print(f"  Delta={g['delta']} Gamma={g['gamma']} Theta={g['theta']} Vega={g['vega']} IV={g['iv']:.2%}")
```

> **坑：** ① 新浪源 **GBK 编码**、**逗号分隔**、需去 `var hq_str_XXX="..."` 壳。② 必带 `Referer: https://stock.finance.sina.com.cn/`，否则 403。③ 希腊字母解析 **`[raw[0]] + raw[4:]`**——`raw[1:4]` 是 3 个空串，不跳过则 Delta/IV 全错位。④ `iv` 是小数（0.1735 = 17.35%）。⑤ 300ETF(510300)、科创50ETF(588000) 同理，换 `underlying` 即可。

---

## Layer 10: 舆情互动层（互动易问答 + 热榜 + 人气榜，V3.3.0 新增）

> 投资者互动问答 + 市场热度——AI 问答与选题的独家信源。**互动易**（巨潮）能答"公司怎么回应某传闻/利好"，别处拿不到；**同花顺热榜 / 东财人气榜**给"当下最热个股 + 被归到什么概念在炒"。全部免登录、零鉴权。

### 10.1 互动易问答（巨潮 — 投资者提问 + 公司回复）

```python
import requests
from datetime import datetime

def cninfo_irm(code: str, page_size: int = 30, page_num: int = 1) -> list[dict]:
    """互动易问答（巨潮，深市公司）。code: 6位代码。沪市公司实测返回 0 条，请用 §10.3 sse_e_interaction()。
    返回每条: code/company/question(投资者提问)/answer(公司回复,None=未回复)/
    answerer(回答方)/ask_time。"""
    try:
        r1 = requests.post("https://irm.cninfo.com.cn/newircs/index/queryKeyboardInfo",
            data={"keyWord": code}, headers={"User-Agent": UA}, timeout=10)
        d1 = r1.json().get("data") or []
        if not d1:
            return []
        org_id = d1[0].get("secid")
        # ⚠️ 第二步参数必须放 query string（POST 但 body 空），否则 HTTP 400
        params = {"_t": 1, "stockcode": code, "orgId": org_id, "pageSize": page_size,
                  "pageNum": page_num, "keyWord": "", "startDay": "", "endDay": ""}
        r2 = requests.post("https://irm.cninfo.com.cn/newircs/company/question",
            params=params, headers={"User-Agent": UA}, timeout=10)
        rows = r2.json().get("rows") or []
    except Exception as e:
        print(f"[WARN] 互动易请求失败: {e}")
        return []
    out = []
    for it in rows:
        pd = it.get("pubDate")
        out.append({"code": it.get("stockCode"), "company": it.get("companyShortName"),
            "question": it.get("mainContent"), "answer": it.get("attachedContent"),
            "answerer": it.get("attachedAuthor"),
            "ask_time": datetime.fromtimestamp(pd / 1000).strftime("%Y-%m-%d %H:%M") if pd else ""})
    return out

# 用法: 看公司怎么回应投资者关切
for q in cninfo_irm("002594", page_size=30):
    if q["answer"]:
        print(f"  Q: {q['question'][:30]}\n  A[{q['answerer']}]: {q['answer'][:50]}")
```

> **坑：** ① 第二步参数放 **query string**（不是 body），否则 400。② `orgId` 取自第一步的 `secid`（即便前缀是 `gshk`，靠 `stockcode` 过滤照样拿 A 股问答）。③ 最新提问常未回复（`answer=None`），回复率因公司而异（实测立讯精密 002475 回复多、京东方 000725 几乎不回）。④ 时间是毫秒时间戳。⑤ **沪市公司查不到**（2026-09-20 实测 600519 / 600000 / 688981 均 0 条，互动易只覆盖深市），沪市问答用 §10.3 上证e互动。⑥ 请求失败时本函数打印 WARN 并返回 `[]`，与「确实没有问答」无法区分，批量使用时注意日志。

### 10.2 同花顺热榜 + 东财人气榜（市场热度 + 概念命中）

```python
EM_HOT_BODY = {"appId": "appId01", "globalId": "786e4c21-70dc-435a-93bb-38"}

def ths_hot_list(period: str = "hour") -> list[dict]:
    """同花顺热榜（单接口拿名称+人气+概念标签+排名变化）。period: hour/day。
    返回每只: rank/code/name/heat(人气值)/pct/rank_chg(排名变化)/concepts(概念标签)/tag。"""
    try:
        r = requests.get("https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/stock",
            params={"stock_type": "a", "type": period, "list_type": "normal"},
            headers={"User-Agent": UA}, timeout=10)
        lst = (r.json().get("data") or {}).get("stock_list") or []
    except Exception as e:
        print(f"[WARN] 同花顺热榜失败: {e}")
        return []
    out = []
    for it in lst:
        tag = it.get("tag") or {}
        out.append({"rank": it.get("order"), "code": it.get("code"), "name": it.get("name"),
            "heat": it.get("rate"), "pct": it.get("rise_and_fall"), "rank_chg": it.get("hot_rank_chg"),
            "concepts": tag.get("concept_tag") or [], "tag": tag.get("popularity_tag", "")})
    return out

def em_hot_rank(top: int = 50) -> list[dict]:
    """东财人气榜（排名 + 排名变化 + 名称/价格）。返回 rank/code/name/price/pct/rank_chg。"""
    try:
        r = requests.post("https://emappdata.eastmoney.com/stockrank/getAllCurrentList",
            json={**EM_HOT_BODY, "marketType": "", "pageNo": 1, "pageSize": top},
            headers={"User-Agent": UA}, timeout=10)
        data = r.json().get("data") or []
        if not data:
            return []
        # 人气榜只给带前缀代码，用 push2 ulist.np 批量补名称/价格
        secids = [("0." if it["sc"].startswith("SZ") else "1.") + it["sc"][2:] for it in data]
        u = requests.get("https://push2.eastmoney.com/api/qt/ulist.np/get",
            params={"ut": "f057cbcbce2a86e2866ab8877db1d059", "fltt": 2, "invt": 2,
                    "fields": "f14,f3,f12,f2", "secids": ",".join(secids)},
            headers={"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}, timeout=10)
        diff = (u.json().get("data") or {}).get("diff") or []
        if isinstance(diff, dict):                       # push2 的 diff 有时是 dict
            diff = list(diff.values())
        nm = {x["f12"]: (x.get("f14"), x.get("f2"), x.get("f3")) for x in diff}
    except Exception as e:
        print(f"[WARN] 东财人气榜失败: {e}")
        return []
    out = []
    for it in data:
        code = it["sc"][2:]
        name, price, pct = nm.get(code, ("", None, None))
        out.append({"rank": it["rk"], "code": code, "name": name,
            "price": price, "pct": pct, "rank_chg": it.get("hisRc")})
    return out

def em_hot_concept(code: str) -> list[dict]:
    """东财个股热门概念命中（这只票当下被市场归到哪些概念在炒）。
    返回 [{concept, bk, hit(命中热度)}, ...]，按热度降序。"""
    try:
        prefix = get_prefix(code).upper()   # #46；emappdata 用大写 SH/SZ/BJ
        r = requests.post("https://emappdata.eastmoney.com/stockrank/getHotStockRankList",
            json={**EM_HOT_BODY, "srcSecurityCode": prefix + code},
            headers={"User-Agent": UA}, timeout=10)
        data = r.json().get("data") or []
    except Exception as e:
        print(f"[WARN] 东财个股概念失败: {e}")
        return []
    return [{"concept": x.get("conceptName"), "bk": x.get("conceptId"),
             "hit": x.get("hitCount")} for x in data]

# 用法
for s in ths_hot_list()[:5]:
    print(f"  #{s['rank']} {s['name']} 热度{s['heat']} {s['concepts']} {s['tag']}")
hot = em_hot_rank(10)        # 东财人气榜 TOP10
print("人气第一:", hot[0]["name"], "概念命中:", em_hot_concept(hot[0]["code"])[:3])
```

> **坑：** ① 东财人气榜 `getAllCurrentList` 只返回带前缀代码（SZ/SH），名称要再走 `ulist.np` 补（`SZ`→`0.`、`SH`→`1.`）。② `ulist.np` 的 `diff` 偶尔是 dict（按序号为键），已做 `list(values())` 归一化。③ 同花顺热榜 `type` 可选 `hour`/`day`。

### 10.3 上证e互动 — 沪市投资者问答（V3.9.0 新增）

上交所官方问答平台。§10.1 巨潮互动易**实测对沪市返回 0 条**（2026-09-20，600519 / 600000 / 688981），
沪市公司的问答只能走这里。`code=None` 看全市场；给沪市代码（60 / 68 / 900 开头）只看该公司。
`kind='answered'` 为最新已回复问答，`kind='questions'` 为最新提问（含未回复，`answer` 为 None）。
平台只开放近期问答，公司维度实测约近 1 个月。首次查某家公司要在公司列表里定位 uid（倍增 + 二分，约 10–13 次请求），之后走缓存。
北交所公司两个平台都没有。

<!-- v39-sse-e:start -->
```python
import html as _html
import re

SSE_E_BASE = "https://sns.sseinfo.com"
_sse_uid_cache = {}                 # 证券代码 → 上证e互动公司 uid
_sse_company_pages = {}             # 页码 → [(code, uid)]，二分查找时复用
_SSE_COMPANY_END = "没有任何上市公司的信息"
# 没有问答时的提示：公司维度「近1个月暂无回复 / 暂无提问」，全市场翻过末页「暂时没有问答内容」（2026-09-20 实测）
_SSE_EMPTY_NOTE = re.compile(r'class="m_feed_note"[^>]*>[^<]*(暂无|暂时没有)[^<]*<')


def _sse_company_page(page):
    if page not in _sse_company_pages:
        response = _v39_http(SSE_E_BASE + "/allcompany.do", method="POST",
                             data={"code": "0", "order": "2", "areaId": "0", "page": page},
                             headers={"Referer": SSE_E_BASE + "/"})
        payload = _v39_json(response)
        content = payload.get("content") if isinstance(payload, dict) else None
        if not isinstance(content, str):    # 末页之后也返回字符串（2026-09-20 实测），缺 content 是格式变了
            raise RuntimeError(f"上证e互动公司列表第 {page} 页的返回结构变了（没有 content 字符串）")
        pairs = [(code, uid) for uid, code in
                 re.findall(r"uid=['\"]?(\d+)['\"]?[^>]*>\s*<img[^>]*company/(\d{6})\.png", content)]
        # 末页之后固定返回「没有任何上市公司的信息」（2026-09-20 实测第 74 页起）。
        # 第 1 页为空、或者别的页既解析不出公司又没有这句话，只能是页面格式变了，不能说成「公司不存在」
        if not pairs and (page == 1 or _SSE_COMPANY_END not in content):
            raise RuntimeError(f"上证e互动公司列表第 {page} 页解析出 0 家公司，页面格式可能已变")
        _sse_company_pages[page] = pairs
        for code, uid in pairs:
            _sse_uid_cache[code] = uid
    return _sse_company_pages[page]


def _sse_company_uid(code):
    """上证e互动按公司 uid 查询；公司列表按代码升序分页（每页 32 家），倍增 + 二分定位。"""
    if code in _sse_uid_cache:
        return _sse_uid_cache[code]
    low, high = 1, 1
    while _sse_company_page(high):      # 先倍增找到末页之后的空页
        if _sse_company_page(high)[-1][0] >= code:
            break
        low, high = high, high * 2
    while low <= high:
        mid = (low + high) // 2
        pairs = _sse_company_page(mid)
        if not pairs or code < pairs[0][0]:
            high = mid - 1
        elif code > pairs[-1][0]:
            low = mid + 1
        else:
            break
    if code not in _sse_uid_cache:
        raise ValueError(f"上证e互动没有 {code}（公司不在上交所，或已退市）")
    return _sse_uid_cache[code]


def _sse_text(fragment):
    return _html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def _sse_time(text):
    match = re.search(r"(\d{4})年(\d{2})月(\d{2})日\s*(\d{2}:\d{2})", text)
    return f"{match.group(1)}-{match.group(2)}-{match.group(3)} {match.group(4)}" if match else None


def _sse_required_time(item_id, text):
    """问答时间必须解析出来：认不出还照常返回，就是把「时间格式变了」变成了一列 None。"""
    when = _sse_time(text)
    if when is None:
        raise RuntimeError(f"上证e互动第 {item_id} 条的提问时间认不出: {text!r}")
    return when


def _sse_parse_feed(text):
    """「最新回复」与「最新提问」两种列表的标记不同（问题框有没有 id），
    所以不靠 id 区分问答，而是以回复块 class="m_feed_detail m_qa" 为界切成问题段和回复段。"""
    rows = []
    for chunk in re.split(r'<div class="m_feed_item[^"]*" id="item-', text)[1:]:
        numbered = re.match(r"(\d+)", chunk)
        if not numbered:
            raise RuntimeError(f"上证e互动条目 id 不是数字，页面结构可能已变: {chunk[:60]}")
        item_id = numbered.group(1)
        # 注意全市场列表的问题块 class 是 "m_feed_detail m_qa_detail"，只能按完整 class 值切
        ask_part, _, answer_part = chunk.partition('class="m_feed_detail m_qa"')
        question = re.search(r'<div class="m_feed_txt"[^>]*>\s*<a[^>]*>:(.*?)\((\d{6})\)</a>(.*?)</div>',
                             ask_part, re.S)
        asker = re.search(r'rel="face"[^>]*?title="([^"]*)"', ask_part, re.S)
        ask_time = re.search(r'<div class="m_feed_from"[^>]*>\s*<span>([^<]+)</span>', ask_part)
        if not question or not ask_time:
            raise RuntimeError(f"上证e互动第 {item_id} 条结构改变，无法解析问题或时间")
        answer = answer_time = None
        if answer_part:
            body = re.search(r'<div class="m_feed_txt"[^>]*>(.*?)</div>', answer_part, re.S)
            when = re.search(r'<div class="m_feed_from"[^>]*>\s*<span>([^<]+)</span>', answer_part)
            if not body or not when:
                raise RuntimeError(f"上证e互动第 {item_id} 条有回复块但解析不出回复内容或回复时间")
            answer, answer_time = _sse_text(body.group(1)), _sse_time(when.group(1))
            if answer_time is None:     # 实测 500 条问答（含 250 条回复）时间字段无一缺失
                raise RuntimeError(f"上证e互动第 {item_id} 条的回复时间认不出: {when.group(1)!r}")
        rows.append({"id": item_id, "code": question.group(2), "name": _sse_text(question.group(1)),
                     "asker": asker.group(1) if asker else None,
                     "question": _sse_text(question.group(3)),
                     "question_time": _sse_required_time(item_id, ask_time.group(1)),
                     "answer": answer, "answer_time": answer_time})
    return rows


_SSE_KIND = {"answered": 11, "questions": 10}


@_v39_contract
def sse_e_interaction(code=None, kind="answered", page=1, page_size=10):
    """上证e互动 — 投资者提问与沪市上市公司回复（上交所官方平台）。

    code=None 看全市场，给沪市代码（60/68/900 开头）只看该公司。
    kind='answered'：最新已回复问答；kind='questions'：最新提问（含未回复，answer 为 None）。
    平台只开放近期问答：公司维度实测约近 1 个月，更早的翻页为空。
    §10.1 巨潮互动易实测对沪市返回 0 条（2026-09-20，600519/600000/688981），沪市问答只能走本函数。
    首次查某家公司要先在公司列表里定位 uid（倍增 + 二分，约 10–13 次请求），之后走缓存。
    """
    if kind not in _SSE_KIND:
        raise ValueError("kind 只能是 'answered' 或 'questions'")
    if int(page) < 1 or not 1 <= int(page_size) <= 50:
        raise ValueError("page 从 1 开始，page_size 范围 1–50")
    if code is None:
        response = _v39_http(SSE_E_BASE + "/ajax/feeds.do",
                             params={"type": _SSE_KIND[kind], "pageSize": int(page_size), "lastid": -1,
                                     "show": 1, "page": int(page)},
                             headers={"Referer": SSE_E_BASE + "/"})
    else:
        digits = norm_ticker(code, stock_only=True)
        if get_prefix(code) != "sh":
            raise ValueError(f"{code} 不是沪市证券；深市互动问答请用 §10.1 cninfo_irm")  # 北交所两处都没有
        response = _v39_http(SSE_E_BASE + "/ajax/userfeeds.do", method="POST",
                             data={"typeCode": "company", "type": _SSE_KIND[kind], "pageSize": int(page_size),
                                   "uid": _sse_company_uid(digits), "page": int(page)},
                             headers={"Referer": SSE_E_BASE + "/"})
    text = response.content.decode("utf-8", "replace")
    rows = _sse_parse_feed(text)
    # 只有带明确的「暂无 / 暂时没有」提示才算真没有问答；解析出 0 条又没有这句提示，是页面结构变了
    if not rows and not _SSE_EMPTY_NOTE.search(text):
        raise RuntimeError("上证e互动返回的页面既没有问答也没有「暂无」提示，结构可能已变")
    if code is not None and any(r["code"] != digits for r in rows):
        raise RuntimeError("上证e互动返回了其他公司的问答，uid 映射可能已变")
    return _v39_frame(rows, "sse_e", response.url,
                      ["id", "code", "name", "asker", "question", "question_time",
                       "answer", "answer_time"])
```
<!-- v39-sse-e:end -->

```python
feed = sse_e_interaction()                              # 全市场最新已回复
mine = sse_e_interaction("600519", kind="questions")    # 某公司最新提问（含未回复）
```

---

## Layer 11: 宏观与利率层（社融 / PMI / 收益率曲线 / 回购利率 / LPR / 宏观日历）

> A股是流动性驱动市场，社融是**领先指标**、PMI 是**同步指标**。两者都由官方直接发布，零鉴权。
> ⚠️ 本层是**月频**数据，不要当日频信号用；发布日固定（社融次月中旬、PMI 月末），
> 未发布月份**不会**出现在返回里（见下方 fail-fast 说明）。
>
> **社融支持范围：2021 年起**（2026-08-19 实测 2021~2026 六年全部可解析，每年 12 行且不跨年）。
> 2020 及更早是旧版式——表头与项目名合并在一个单元格、且附表带「2017 年以来」的历史区，
> 传入这些年份会**抛错而不是返回可疑数据**。

### 11.1 人民银行 — 社会融资规模增量

**核心价值：** 官方口径的全社会流动性投放，A股中期最重要的宏观变量。中英双语 12 列。

**链路是三级跳**（索引 → 年份页 → 专题页 → xls 附件），任何一级结构变更都会 fail-fast 抛错，不静默返回空。

```python
import io
import re
from typing import Optional

import pandas as pd
import requests

_UA = {"User-Agent": "Mozilla/5.0"}
PBC_BASE = "https://www.pbc.gov.cn"
PBC_INDEX = f"{PBC_BASE}/diaochatongjisi/116219/116319/index.html"


def _macro_get(url: str, timeout: int = 30) -> str:
    r = requests.get(url, headers=_UA, timeout=timeout)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return r.text


def _abs_pbc(href: str) -> str:
    return href if href.startswith("http") else PBC_BASE + href


def pboc_social_financing(year: Optional[int] = None) -> pd.DataFrame:
    """人民银行「社会融资规模增量统计表」— 月度，单位亿元；year=None 取最新年"""
    idx = _macro_get(PBC_INDEX)
    years = re.findall(r"""href=["']([^"']+)["'][^>]*>\s*(\d{4})年统计数据\s*</a>""", idx)
    if not years:
        raise RuntimeError("人民银行索引页未找到「XXXX年统计数据」链接，页面结构可能已变更")
    table = {int(y): href for href, y in years}
    target = max(table) if year is None else year
    if target not in table:
        raise ValueError(f"人民银行无 {target} 年数据，可选年份: {sorted(table, reverse=True)[:8]}")

    ypage = _macro_get(_abs_pbc(table[target]))
    topics = re.findall(r"""href=["']([^"']+)["'][^>]*>\s*(社会融资规模)\s*</a>""", ypage)
    if not topics:
        raise RuntimeError(f"{target} 年页未找到「社会融资规模」专题链接")

    tpage = _macro_get(_abs_pbc(topics[0][0]))
    books = re.findall(r"""href=["']([^"']+\.xlsx?)["']""", tpage)
    if not books:
        raise RuntimeError(f"{target} 年社融专题页未找到 xls/xlsx 附件")

    content = requests.get(_abs_pbc(books[0]), headers=_UA, timeout=60).content
    raw = pd.read_excel(io.BytesIO(content), header=None)

    start = None                      # 表头是中英双行 + 单位说明，用「月份」列定位数据起点
    for i in range(len(raw)):
        if str(raw.iloc[i, 0]).strip() == "月份":
            start = i
            break
    if start is None:
        raise RuntimeError(
            f"{target} 年社融表没有独立的「月份」表头单元格。"
            "**2020 及更早采用旧版式**（表头与项目名合并在同一单元格，且附表含 2017 年以来的历史区），"
            "本端点仅支持 **2021 年起**（2026-08-19 实测 2021~2026 全部可解析）。"
        )

    cols = ["month", "afre_total", "rmb_loans", "fx_loans", "entrusted_loans",
            "trust_loans", "undiscounted_bankers_acceptance", "corporate_bonds",
            "government_bonds", "equity_financing", "abs_by_depository", "loans_written_off"]
    df = raw.iloc[start + 3:].copy().iloc[:, :len(cols)]
    df.columns = cols
    df = df[df["month"].astype(str).str.match(r"^\d{4}\.\d{1,2}$", na=False)].copy()
    for c in cols[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    def _month_label(v):
        """`2026.01` → 2026-01；`2026.1` → 2026-10。

        Excel 把 `2026.10` 的尾零吃掉读成浮点 `2026.1`，与 1 月的 `2026.01` 撞车。
        1 月在表里始终写作两位 `.01`，因此**单个小数位必然是被吃了尾零的 x0 月**。
        按单元格逐行解析（而不是按行序编号），跨年工作簿也不会错位。
        """
        m = re.match(r"^(\d{4})\.(\d{1,2})$", str(v).strip())
        if not m:
            return None
        year_s, mon_s = m.group(1), m.group(2)
        if len(mon_s) == 1:
            mon_s += "0"
        return f"{year_s}-{int(mon_s):02d}"

    df["month"] = [_month_label(v) for v in df["month"]]
    df = df[df["month"].notna()]
    # 旧工作簿底部会附「表1：2017年以来各月…」的历史区，只保留目标年，防跨年污染
    df = df[df["month"].str.startswith(f"{target}-")].reset_index(drop=True)

    # 未发布月份整行为空 —— 必须丢掉，否则调用方会把 12 行当成 12 个月的真数据。
    df = df.dropna(subset=["afre_total"]).reset_index(drop=True)
    if df.empty:
        raise RuntimeError(f"社融表解析后无有效月份（{target} 年），格式可能已变更")
    return df


# 用法
df = pboc_social_financing()          # 最新年（只含已发布月份）
print(df[["month", "afre_total", "rmb_loans", "government_bonds"]].to_string(index=False))
# 实测 2026-08-19：返回 7 行（2026-01 ~ 2026-07），2026-01 社融增量 72,185 亿
# 全部 12 列：month / afre_total(社融增量) / rmb_loans(人民币贷款) / fx_loans(外币贷款) /
#   entrusted_loans(委托贷款) / trust_loans(信托贷款) /
#   undiscounted_bankers_acceptance(未贴现银行承兑汇票) / corporate_bonds(企业债券) /
#   government_bonds(政府债券) / equity_financing(非金融企业境内股票融资) /
#   abs_by_depository(存款类金融机构ABS) / loans_written_off(贷款核销)

hist = pboc_social_financing(2024)    # 指定年份
print(len(hist), "个月, 全年社融增量", f"{hist['afre_total'].sum():,.0f}", "亿元")
# 实测：12 个月, 322,588 亿元
```

---

### 11.2 国家统计局 — 采购经理指数 PMI

**核心价值：** 制造业景气度同步指标，50 是荣枯线。月末发布，比上市公司财报早一个季度反映景气。

```python
import re

import requests

NBS_INDEX = "https://www.stats.gov.cn/sj/zxfb/"
_UA = {"User-Agent": "Mozilla/5.0"}


def _macro_get(url: str, timeout: int = 30) -> str:
    """与 §11.1 同名同实现 —— 本块按「端点路由速查」单独取用时也能独立跑，
    不必先执行 §11.1。两处同时执行时后定义覆盖前者，行为一致，无副作用。"""
    r = requests.get(url, headers=_UA, timeout=timeout)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return r.text


def nbs_pmi() -> dict:
    """国家统计局最新 PMI — 制造业 / 非制造业商务活动 / 综合产出 + 大中小型企业"""
    idx = _macro_get(NBS_INDEX)
    links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>\s*([^<]{6,80}?)\s*</a>', idx)
    hit = next(((u, t) for u, t in links if "采购经理指数" in t), None)
    if not hit:
        raise RuntimeError("国家统计局最新发布页未找到「采购经理指数」条目")
    href, title = hit
    url = href if href.startswith("http") else NBS_INDEX + href.lstrip("./")

    html = _macro_get(url)
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.S)
    text = re.sub(r"<[^>]+>", "", text)
    # 🔴 正文是全角括号且**括号内带空格**（`（ PMI ）为 49.2%`）。
    #    必须把空白**整个删掉**；只做「压成单个空格」会一条都匹配不到。
    text = re.sub(r"[\s\u3000\xa0]+", "", text)

    def grab(pat):
        m = re.search(pat, text)
        return float(m.group(1)) if m else None

    ym = re.search(r"(\d{4})年(\d{1,2})月", title)

    # 分档措辞统计局用过三种版式，逐层回退；解析不到留 None（属可选字段）。
    #   ① 全合并：大、中、小型企业PMI分别为 A%、B%和C%
    #   ② 半拆：  大型企业PMI为 A%…；中、小型企业PMI分别为 B%和C%
    #   ③ 全拆：  大型企业PMI为 A%…；中型企业PMI为 B%…；小型企业PMI为 C%
    # 注：③ 的单条正则要求「…企业PMI为」，不会误匹配 ①② 里的「…企业PMI分别为」。
    large = medium = small = None
    combined = re.search(r"大、中、小型企业PMI分别为([\d.]+)%、([\d.]+)%和([\d.]+)%", text)
    if combined:
        large, medium, small = (float(x) for x in combined.groups())
    else:
        m_ms = re.search(r"中、小型企业PMI分别为([\d.]+)%和([\d.]+)%", text)
        if m_ms:                            # ② 中小型合并一句
            medium, small = (float(x) for x in m_ms.groups())
        for _name, _pat in (("large", r"大型企业PMI为([\d.]+)%"),
                            ("medium", r"中型企业PMI为([\d.]+)%"),
                            ("small", r"小型企业PMI为([\d.]+)%")):
            _m = re.search(_pat, text)      # ③ 各自单独成句
            if _m:
                _v = float(_m.group(1))
                if _name == "large":
                    large = _v
                elif _name == "medium" and medium is None:
                    medium = _v
                elif _name == "small" and small is None:
                    small = _v

    result = {
        "title": title.strip(),
        "period": f"{ym.group(1)}-{int(ym.group(2)):02d}" if ym else None,
        "manufacturing_pmi": grab(r"(?<!非)制造业采购经理指数（PMI）为([\d.]+)%"),
        "non_manufacturing_pmi": grab(r"非制造业商务活动指数为([\d.]+)%"),
        "composite_pmi": grab(r"综合PMI产出指数为([\d.]+)%"),
        "pmi_large": large,
        "pmi_medium": medium,
        "pmi_small": small,
        "source_url": url,
    }
    # 三个主指标是本端点的承诺输出，解析不到必须 fail-fast ——
    # 统计局改一次措辞就静默返回一串 None，调用方会当成「本月没数据」。
    core = ("manufacturing_pmi", "non_manufacturing_pmi", "composite_pmi")
    absent = [k for k in core if result[k] is None]
    if absent:
        raise RuntimeError(
            f"PMI 正文措辞可能已变更，无法解析 {absent}；请核对页面：{url}"
        )
    return result


# 用法
p = nbs_pmi()
print(p["period"], "制造业", p["manufacturing_pmi"], "非制造业", p["non_manufacturing_pmi"])
# 实测 2026-08-19：2026-07 制造业 49.2 / 非制造业 49.0 / 综合 49.3
#                  大型 49.5 / 中型 49.7 / 小型 47.4（均在荣枯线下）
```

> **解读口径：** PMI > 50 扩张、< 50 收缩；连续两月同向才算趋势。
> 大/中/小型企业分档能看结构分化——小型企业长期低于大型是常态，看的是**差值变化**不是绝对值。

### 11.3 中债收益率曲线 — 国债 / 商业银行 AAA / 中短票 AAA（V3.9.0 新增）

中央结算公司官方数据，3 月到 30 年共 8 档期限，单位 %。`curve='all'` 一次返回三条曲线（按 `curve` 列区分）。
官网单次查询超过 1 年会静默返回 0 行，本函数按 360 天切片；一周以上的切片 0 行视为接口口径变化并抛错。
中短期票据曲线没有 30 年，该列为 None。三条曲线的起点不同（国债 2006-03-01、中短票 2006-12-25、商业银行 2009-12-24，2026-09-20 实测），
start 更早时从起点开始取；每段返回的日期必须落在该段内，`all` 模式按起点核对**返回的每一天**该有的曲线是否齐全，不齐抛 `RuntimeError`。
中债不公布债券市场交易日历、页面也没有总条数，整天缺失无法判定（只有整段 7 天以上 0 行才报错）。

<!-- v39-chinabond:start -->
```python
import re
from datetime import date, datetime, timedelta

CHINABOND_HISTORY_URL = "https://yield.chinabond.com.cn/cbweb-pbc-web/pbc/historyQuery"
CHINABOND_CURVES = {"all": "ycqx", "treasury": "hzsylqx", "bank_aaa": "syyhsylqx", "mtn_aaa": "zdqpjsylqx"}
_CHINABOND_HEADER = ["曲线名称", "日期", "3月", "6月", "1年", "3年", "5年", "7年", "10年", "30年"]
_CHINABOND_TENORS = ["3m", "6m", "1y", "3y", "5y", "7y", "10y", "30y"]
CHINABOND_CURVE_NAMES = {"treasury": "中债国债收益率曲线", "bank_aaa": "中债商业银行普通债收益率曲线(AAA)",
                         "mtn_aaa": "中债中短期票据收益率曲线(AAA)"}
# 官网上各曲线的第一天（2026-09-20 实测）；all 模式按日期核对当天应有的曲线是否齐全
CHINABOND_FIRST_DAY = {"treasury": "2006-03-01", "mtn_aaa": "2006-12-25", "bank_aaa": "2009-12-24"}


@_v39_contract
def chinabond_yield_curve(start, end=None, curve="all"):
    """中债收益率曲线（中央结算公司官方）— 国债 / 商业银行普通债 AAA / 中短期票据 AAA。

    curve: 'all' / 'treasury'（国债）/ 'bank_aaa' / 'mtn_aaa'。收益率单位为 %。
    期限 3 月到 30 年共 8 档；中短期票据曲线没有 30 年，该列为 None。
    官网单次查询超过 1 年会静默返回 0 行，本函数按 360 天切片。
    各曲线起点：国债 2006-03-01、中短期票据 2006-12-25、商业银行 2009-12-24；
    start 早于起点时从起点开始取。all 模式下 2006-03-01 至 2006-12-24 每天只有国债一条，
    2006-12-25 至 2009-12-23 每天两条（国债 + 中短期票据），2009-12-24 起三条；
    返回的每一天都按这个规则核对曲线是否齐全，缺一条抛 RuntimeError。
    中债不公布债券市场交易日历，页面也没有总条数，所以整天缺失（某个交易日一条都没返回）
    无法判定，只有整段切片 7 天以上 0 行才报错；需要严格逐日核对请自备交易日历比对 date 列。
    """
    if curve not in CHINABOND_CURVES:
        raise ValueError("curve 只能是 " + " / ".join(CHINABOND_CURVES))
    first = datetime.strptime(_v39_date(start), "%Y-%m-%d").date()
    last = datetime.strptime(_v39_date(end), "%Y-%m-%d").date() if end else date.today()
    if first > last:
        raise ValueError("start 不能晚于 end")
    wanted = [k for k in CHINABOND_CURVE_NAMES if curve in ("all", k)]
    begin = datetime.strptime(min(CHINABOND_FIRST_DAY[k] for k in wanted), "%Y-%m-%d").date()
    if last < begin:
        raise ValueError(f"中债 {curve} 曲线从 {begin} 起才有数据")
    first = max(first, begin)
    by_name = {CHINABOND_CURVE_NAMES[k]: k for k in wanted}
    rows, cursor, url, seen = [], first, CHINABOND_HISTORY_URL, {}
    while cursor <= last:
        stop = min(cursor + timedelta(days=359), last)
        response = _v39_http(CHINABOND_HISTORY_URL,
                             params={"startDate": cursor.isoformat(), "endDate": stop.isoformat(),
                                     "gjqx": 0, "qxId": CHINABOND_CURVES[curve], "locale": "cn_ZH"})
        text = re.sub(r"<!--.*?-->", "", response.content.decode("utf-8", "replace"), flags=re.S)
        tables = text.split("<table")
        table_rows = re.findall(r"<tr[^>]*>(.*?)</tr>", tables[-1], re.S) if len(tables) > 2 else []
        cells = [[re.sub(r"<[^>]+>|\s+", "", c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
                 for r in table_rows]
        if not cells or cells[0] != _CHINABOND_HEADER:
            raise RuntimeError("中债收益率页面表头改变，不能按原列序解析")
        chunk = 0
        for rec in cells[1:]:
            if len(rec) != len(_CHINABOND_HEADER):
                raise RuntimeError(f"中债收益率行列数不对: {rec}")
            day = _v39_src_date(rec[1])
            if not cursor.isoformat() <= day <= stop.isoformat():
                raise RuntimeError(f"中债 请求 {cursor}~{stop} 却返回了 {day} 的曲线，结果不可信")
            if rec[0] not in by_name:
                raise RuntimeError(f"中债 返回了未请求的曲线「{rec[0]}」（请求的是 {curve}）")
            seen.setdefault(day, set()).add(by_name[rec[0]])
            row = {"date": day, "curve": rec[0]}
            row.update({k: _v39_num(v) for k, v in zip(_CHINABOND_TENORS, rec[2:])})
            rows.append(row)
            chunk += 1
        if chunk == 0 and (stop - cursor).days >= 6:
            raise RuntimeError(f"中债 {cursor}~{stop} 一周以上却 0 行，接口口径可能变了")
        url = response.url
        cursor = stop + timedelta(days=1)
    if not rows:
        raise ValueError(f"{first}~{last} 没有中债收益率（区间内无交易日）")
    for day, keys in seen.items():
        expected = {k for k in wanted if CHINABOND_FIRST_DAY[k] <= day}
        if keys != expected:
            raise RuntimeError(f"中债 {day} 缺少曲线 {sorted(expected - keys)}，结果不完整")
    frame = _v39_frame(rows, "chinabond", url)
    frame = frame.sort_values(["date", "curve"]).reset_index(drop=True)
    if frame.duplicated(["date", "curve"]).any():
        raise RuntimeError("中债收益率出现重复的 日期+曲线")
    return frame
```
<!-- v39-chinabond:end -->

### 11.4 银行间回购定盘利率 FR / FDR（V3.9.0 新增）

中国货币网（外汇交易中心）官方 CSV：`kind='FR'` 全市场回购定盘利率 FR001 / FR007 / FR014（约近 3 年），
`kind='FDR'` 银银间 FDR001 / FDR007 / FDR014（约近 1 年）。单位 %。看资金面松紧的日频指标。

<!-- v39-repo-fixing:start -->
```python
CHINAMONEY_FIXING_URL = "https://www.chinamoney.com.cn/r/cms/www/chinamoney/data/currency/{name}-chrt.csv"


@_v39_contract
def repo_fixing_rates(kind="FR"):
    """银行间回购定盘利率（中国货币网 / 外汇交易中心官方）。

    kind='FR'：全市场回购定盘利率 FR001/FR007/FR014（约近 3 年）；
    kind='FDR'：银银间回购定盘利率 FDR001/FDR007/FDR014（约近 1 年）。单位 %。
    """
    names = {"FR": "frr", "FDR": "fdr"}
    kind = str(kind).upper()
    if kind not in names:
        raise ValueError("kind 只能是 'FR' 或 'FDR'")
    url = CHINAMONEY_FIXING_URL.format(name=names[kind])
    response = _v39_http(url, headers={"Referer": "https://www.chinamoney.com.cn/chinese/bkfrr/"})
    rows = []
    for line in response.content.decode("utf-8-sig").splitlines():
        if not line.strip():
            continue
        parts = line.split(",")
        # 每行是「日期,,,,,,隔夜,7天,14天」：中间 5 列恒为空，不为空说明格式改了
        if len(parts) != 9 or any(p.strip() for p in parts[1:6]):
            raise RuntimeError(f"货币网定盘利率 CSV 格式改变: {line[:60]}")
        # 三个期限都是核心指标：整行为空（'2026-09-18,,,,,,,,'）列数照样是 9，
        # 用 _v39_num 会返回日期有效、利率全 None 的行。实测 FR 748 行 / FDR 249 行零空值。
        rows.append({"date": _v39_src_date(parts[0]),
                     kind + "001": _v39_req_num(parts[6], f"{kind}001"),
                     kind + "007": _v39_req_num(parts[7], f"{kind}007"),
                     kind + "014": _v39_req_num(parts[8], f"{kind}014")})
    if not rows:
        raise RuntimeError(f"货币网 {kind} 定盘利率为空")
    frame = _v39_frame(rows, "chinamoney", url).sort_values("date").reset_index(drop=True)
    if frame.duplicated(["date"]).any():
        raise RuntimeError("定盘利率日期重复")
    return frame
```
<!-- v39-repo-fixing:end -->

### 11.5 LPR 贷款市场报价利率全历史（V3.9.0 新增）

东财数据中心。2013-10 至 2019-08 为旧机制的逐日 1 年期 LPR（`lpr_5y` 为 None，5 年期 2019-08-20 才设立）；
2019-08 改革后每月 20 日报价。同一报表里 2013 年前的行是旧贷款基准利率，已剔除。

<!-- v39-lpr:start -->
```python
@_v39_contract
def lpr_history():
    """贷款市场报价利率 LPR 全历史。单位 %。
    2013-10 至 2019-08 为旧机制的逐日 1 年期 LPR（lpr_5y 为 None，5 年期品种 2019-08-20 才设立）；
    2019-08 改革后每月 20 日报价。东财同一报表里还混着旧贷款基准利率调整行（实测最早 1991-04-21、最晚 2015-10-24，共 38 行），
    LPR 字段为空，已剔除；不为空却认不出的值会报错，不会返回空的 lpr_1y。"""
    rows = _em_datacenter_strict("RPTA_WEB_RATE", sort_columns="TRADE_DATE", sort_types="1",
                                 columns="TRADE_DATE,LPR1Y,LPR5Y")
    out = [{"date": _v39_src_date(str(r["TRADE_DATE"])[:10]), "lpr_1y": _v39_req_num(r["LPR1Y"], "LPR 1 年期"),
            "lpr_5y": _v39_num(r.get("LPR5Y"))}
           for r in rows if r.get("LPR1Y") is not None]
    if not out:
        raise RuntimeError("东财 LPR 报表里没有 LPR 数据")
    return _v39_frame(out, "eastmoney", DATACENTER_URL + "?reportName=RPTA_WEB_RATE")
```
<!-- v39-lpr:end -->

### 11.6 全球宏观日历（华尔街见闻）（V3.9.0 新增）

经济数据的公布值 / 预期 / 前值 + 重要事件（央行议息等）。区间含两端最多 92 天，接口单次只允许一周，本函数按 7 天切片。
`importance` 1–4，数字越大越重要（实测 4 = 工业增加值、社零这类头条数据）；`kind`：`data` 经济数据 / `event` 事件。
已开始的整周返回 0 条说明接口异常，抛 `RuntimeError`；单日、周末或三周以后的日期可能确实没有条目，整个区间为空时抛 `ValueError`。

<!-- v39-macro-calendar:start -->
```python
from datetime import datetime, timedelta, timezone

WSCN_MACRO_URL = "https://api-one-wscn.awtmt.com/apiv1/finance/macrodatas"
_CN_TZ = timezone(timedelta(hours=8))


def _blank_none(value):
    """空串 → None；数值 0 与字符串 '0' 原样保留（`value or None` 会把数值 0 变成缺失）。"""
    return None if value is None or value == "" else value


@_v39_contract
def macro_calendar(start, end=None, country=None, min_importance=1):
    """全球宏观日历（华尔街见闻）— 经济数据公布值/预期/前值 + 重要事件。

    start/end: 'YYYY-MM-DD'（北京时间，含两端）；end 默认 start 后 6 天；区间含两端最多 92 天。
    接口单次只允许一周，本函数按 7 天切片。country 例: '中国' / '美国'；
    importance 1–4，数字越大越重要（实测 4 = 工业增加值、社零这类头条数据），min_importance 按它过滤。
    kind: data=经济数据，event=事件。
    满 7 天且已开始的窗口 0 条抛 RuntimeError（实测过去任一周都有 150 条以上）；
    单日、周末或三周以后的日期可能确实为空（2026-09-19 周六 0 条），整个区间都没有条目时抛 ValueError；
    min_importance 只收 1–4，区间有条目但按 country / min_importance 筛完为空也抛 ValueError（不返回空表）。
    """
    first = datetime.strptime(_v39_date(start), "%Y-%m-%d").date()
    last = datetime.strptime(_v39_date(end), "%Y-%m-%d").date() if end else first + timedelta(days=6)
    if first > last or (last - first).days > 91:
        raise ValueError("区间需满足 start ≤ end 且含两端不超过 92 天")
    if isinstance(min_importance, bool) or str(min_importance) not in ("1", "2", "3", "4"):
        raise ValueError("min_importance 只能是 1–4（数字越大越重要）")
    rows, cursor, url = {}, first, WSCN_MACRO_URL
    today = datetime.now(_CN_TZ).date()
    while cursor <= last:
        stop = min(cursor + timedelta(days=6), last)
        begin = int(datetime(cursor.year, cursor.month, cursor.day, tzinfo=_CN_TZ).timestamp())
        finish = int(datetime(stop.year, stop.month, stop.day, 23, 59, 59, tzinfo=_CN_TZ).timestamp())
        response = _v39_http(WSCN_MACRO_URL, params={"start": begin, "end": finish})
        payload = _v39_json(response)
        if not isinstance(payload, dict) or payload.get("code") != 20000:
            raise RuntimeError(f"华尔街见闻宏观日历返回错误: {str(payload)[:200]}")
        items = payload.get("data").get("items") if isinstance(payload.get("data"), dict) else None
        if items is None:
            items = []
        if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
            raise RuntimeError("华尔街见闻宏观日历的 items 不是由对象组成的列表，格式可能已变")
        if not items and stop - cursor == timedelta(days=6) and cursor <= today:
            raise RuntimeError(f"华尔街见闻 {cursor}~{stop} 宏观日历 0 条（整周不该为空），接口可能改了")
        for item in items:
            stamp = item.get("public_date")
            if "id" not in item or isinstance(stamp, bool) or not isinstance(stamp, (int, float)):
                raise RuntimeError(f"华尔街见闻宏观日历条目缺 id 或 public_date 格式改变: "
                                   f"id={item.get('id')!r} public_date={stamp!r}")
            try:
                when = datetime.fromtimestamp(stamp, _CN_TZ)
            except (ValueError, OverflowError, OSError) as exc:
                raise RuntimeError(f"华尔街见闻宏观日历时间戳无效: {stamp!r}") from exc
            # 每段只接受段内日期：接口若回了别的时间段（缓存 / 忽略参数），按 id 去重会把缺掉的几段静默吞掉
            if not cursor <= when.date() <= stop:
                raise RuntimeError(f"华尔街见闻 请求 {cursor}~{stop} 却返回了 {when:%Y-%m-%d} 的条目，结果不可信")
            # 各段互不重叠，2026-09-20 实测 31 周 5976 条没有重复 id；重复了按 id 存会静默丢掉一条
            level = item.get("importance")
            if isinstance(level, bool) or not isinstance(level, int) or level not in (1, 2, 3, 4):
                # 不校验的话 importance=True/99 会照常出表，"2" 还会让下面的筛选漏出原生 TypeError
                raise RuntimeError(f"华尔街见闻宏观日历 importance 超出 1–4: {level!r}")
            if item["id"] in rows:
                raise RuntimeError(f"华尔街见闻宏观日历 id {item['id']!r} 出现两次，结果不可信")
            rows[item["id"]] = {
                "time": when.strftime("%Y-%m-%d %H:%M"),
                "country": item.get("country"), "title": item.get("title"),
                "kind": {"FD": "data", "FE": "event"}.get(item.get("calendar_type"), item.get("calendar_type")),
                "importance": level, "actual": _blank_none(item.get("actual")),
                "forecast": _blank_none(item.get("forecast")), "previous": _blank_none(item.get("previous")),
                "revised": _blank_none(item.get("revised")), "unit": item.get("unit") or None,
                "period": item.get("period") or None}
        url = response.url
        cursor = stop + timedelta(days=1)
    if not rows:
        raise ValueError(f"{first}~{last} 没有宏观日历条目（单日、周末或较远的未来日期可能确实没有）")
    frame = _v39_frame(sorted(rows.values(), key=lambda r: r["time"]), "wallstreetcn", url)
    if country:
        frame = frame[frame["country"] == country]
    frame = frame[frame["importance"].fillna(0) >= int(min_importance)].reset_index(drop=True)
    if frame.empty:     # 整个区间是有条目的，筛完没了：country 写错 / 重要度门槛太高
        raise ValueError(f"{first}~{last} 有条目，但 country={country!r} / min_importance={min_importance} "
                         "筛完是空的（country 例: '中国' / '美国'）")
    return frame
```
<!-- v39-macro-calendar:end -->

```python
curve = chinabond_yield_curve("2026-01-01", curve="treasury")
fr = repo_fixing_rates("FR")
lpr = lpr_history()
cal = macro_calendar("2026-09-21", country="中国", min_importance=3)
```

---

## Layer 12: 指数与交易日历（V3.8.0）

补齐指数成分、权重、指数估值与官方交易日历。以下完整代码块可独立执行，仅使用已有的
`requests pandas xlrd openpyxl`；不依赖前面章节的股票代码推断规则。指数代码必须是 **6 位纯数字**，
`provider="csi"` 表示中证，`provider="cni"` 表示国证，不能把股票代码直接当指数查询。

| 函数 | 契约 |
|---|---|
| `index_constituents(index_code, provider="csi")` | 官方最近发布的成分快照；中证日度文件、国证月末文件，真实日期在 `date` 列 |
| `index_weights(index_code, provider="csi")` | 最近公布的权重；`weight_percent=0.433` 表示 **0.433%**，不是 43.3% |
| `index_valuation(index_code)` | 仅中证公开估值文件：两种股本口径 PE、两种股息率；**不提供 PB、不承诺全历史** |
| `trading_calendar(year, month)` | 深交所整月日历；逐日返回 `is_open`，不靠工作日推断，也不把未发布月份当休市 |

**日期边界：** 当前成分与权重可能不同日，不能按行号拼接或将月末权重标成今天。
这些快照不提供历史时点成分；国证的 `download-history` 名字虽带 history，本次接口实际返回
单个月末快照。历史调样另有接口，暂不纳入本版。调用方应先检查 `date`，做历史回测时不能拿
当前成分代替当时成分。网络失败、结构变化、重复记录或不完整日历均抛异常，不伪装为空结果。

### 12.1–12.4 自包含实现

<!-- official-data-core:start -->
```python
import calendar
import math
import re
from datetime import datetime, timezone
from io import BytesIO

import pandas as pd
import requests


def _official_code(value):
    value = str(value).strip()
    if not re.fullmatch(r"[0-9]{6}", value):
        raise ValueError("代码必须是 6 位纯数字；指数 provider 与证券交易所不是同一概念")
    return value


def _official_date(value):
    value = str(value).strip()
    fmt = "%Y%m%d" if re.fullmatch(r"[0-9]{8}", value) else "%Y-%m-%d"
    return datetime.strptime(value, fmt).date().isoformat()


def _official_number(value, required=False):
    if pd.isna(value) or str(value).strip() in ("", "-", "--"):
        if required:
            raise RuntimeError("官方源缺少必需数值")
        return None
    number = float(str(value).replace(",", ""))
    if not math.isfinite(number):
        raise RuntimeError("官方源返回非有限数值")
    return number


def _official_get(url, params=None, referer=None):
    response = requests.get(
        url, params=params,
        headers={"User-Agent": "Mozilla/5.0", "Referer": referer or url},
        timeout=(10, 40),
    )
    response.raise_for_status()
    return response


def _official_excel(response):
    try:
        frame = pd.read_excel(BytesIO(response.content), dtype=str)
    except (ValueError, OSError) as exc:
        raise RuntimeError("官方源未返回可解析的 Excel；可能未发布或响应结构改变") from exc
    # 两种中证文件的表头空格略有差异，按完整列名去空白后匹配。
    frame.columns = [re.sub(r"\s+", "", str(c)) for c in frame.columns]
    return frame


def _official_columns(frame, names):
    missing = set(names) - set(frame.columns)
    if missing:
        raise RuntimeError("官方数据列缺失: " + ", ".join(sorted(missing)))


def _official_frame(rows, keys, source, url):
    frame = pd.DataFrame(rows)
    if frame.empty or frame.duplicated(keys).any():
        raise RuntimeError("官方数据为空或主键重复，不能当成完整快照")
    frame["source"] = source
    frame["source_url"] = url
    frame["fetched_at"] = datetime.now(timezone.utc).isoformat()
    return frame.sort_values(keys).reset_index(drop=True)


def _official_index_members(index_code, provider, weights):
    index_code = _official_code(index_code)
    if provider not in ("csi", "cni"):
        raise ValueError("provider 必须是 csi（中证）或 cni（国证）")
    if provider == "csi":
        kind = "closeweight" if weights else "cons"
        url = ("https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/"
               f"autofile/{kind}/{index_code}{kind}.xls")
        response = _official_get(url)
        data = _official_excel(response)
        cols = ["日期Date", "指数代码IndexCode", "成份券代码ConstituentCode",
                "成份券名称ConstituentName", "交易所Exchange"]
        if weights:
            cols.append("权重(%)weight")
    else:
        url = "https://www.cnindex.com.cn/sample-detail/download-history"
        response = _official_get(url, {"indexcode": index_code})
        data = _official_excel(response)
        cols = ["日期", "样本代码", "样本简称", "权重（%）"]
    _official_columns(data, cols)
    rows = []
    for rec in data.to_dict("records"):
        if provider == "csi":
            if str(rec["指数代码IndexCode"]).zfill(6) != index_code:
                raise RuntimeError("中证返回了不同指数的数据")
            code = str(rec["成份券代码ConstituentCode"]).zfill(6)
            exchanges = {"上海证券交易所": "SH", "深圳证券交易所": "SZ", "北京证券交易所": "BJ"}
            exchange = exchanges.get(rec["交易所Exchange"])
            if exchange is None:
                raise ValueError("本端点仅支持沪深北成分，请使用相应市场的数据工具")
            row = {"date": _official_date(rec["日期Date"]), "index_code": index_code,
                   "code": _official_code(code), "name": rec["成份券名称ConstituentName"],
                   "exchange": exchange}
            weight = rec.get("权重(%)weight")
        else:
            # 国证没有交易所列；A 股文件保留六位文本。港股 00700 不能补成 000700/SZ。
            code = _official_code(rec["样本代码"])
            exchange = ("SH" if code.startswith("6") else "SZ" if code.startswith(("0", "3"))
                        else "BJ" if code.startswith(("4", "8", "92")) else None)
            if exchange is None:
                raise ValueError("国证该指数包含本端点不支持的证券类型")
            row = {"date": _official_date(rec["日期"]), "index_code": index_code,
                   "code": code, "name": rec["样本简称"], "exchange": exchange}
            weight = rec["权重（%）"]
        if weights:
            row["weight_percent"] = _official_number(weight, required=True)
        rows.append(row)
    frame = _official_frame(rows, ["date", "code", "exchange"], provider, response.url)
    if frame["date"].nunique() != 1:
        raise RuntimeError("成分文件混有多个日期，不能当作单日快照")
    if weights and (not frame.weight_percent.between(0, 100).all()
                    or not 99 <= frame.weight_percent.sum() <= 101):
        raise RuntimeError("权重范围或合计异常；可能文件残缺或不是百分数口径")
    return frame


def index_constituents(index_code, provider="csi"):
    """最近公布的沪深北成分；date 是源文件日期，不是抓取日。"""
    return _official_index_members(index_code, provider, weights=False)


def index_weights(index_code, provider="csi"):
    """最近公布的指数权重，weight_percent 单位为百分数。"""
    return _official_index_members(index_code, provider, weights=True)


def index_valuation(index_code):
    """中证近期 PE/股息率文件；不含 PB，两种股本口径不混用。"""
    index_code = _official_code(index_code)
    url = ("https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/"
           f"autofile/indicator/{index_code}indicator.xls")
    response = _official_get(url)
    data = _official_excel(response)
    mapping = {"市盈率1（总股本）P/E1": "pe_total",
               "市盈率2（计算用股本）P/E2": "pe_calculation",
               "股息率1（总股本）D/P1": "dividend_yield_total_percent",
               "股息率2（计算用股本）D/P2": "dividend_yield_calculation_percent"}
    _official_columns(data, ["日期Date", "指数代码IndexCode", *mapping])
    rows = []
    for rec in data.to_dict("records"):
        if str(rec["指数代码IndexCode"]).zfill(6) != index_code:
            raise RuntimeError("中证估值文件返回了不同指数")
        rows.append({"date": _official_date(rec["日期Date"]), "index_code": index_code,
                     **{dest: _official_number(rec[src]) for src, dest in mapping.items()}})
    return _official_frame(rows, ["date", "index_code"], "csi", response.url)


def trading_calendar(year, month):
    """深交所完整自然月日历。未发布或缺日抛错，周末调休不视为交易日。"""
    if type(year) is not int or type(month) is not int or not 1 <= month <= 12:
        raise ValueError("year/month 必须为整数，month 在 1–12 之间")
    last = calendar.monthrange(year, month)[1]
    expected = {datetime(year, month, day).date().isoformat() for day in range(1, last + 1)}
    url = "https://www.szse.cn/api/report/exchange/onepersistenthour/monthList"
    response = _official_get(url, {"month": f"{year}-{month}"})
    data = response.json().get("data")
    if not isinstance(data, list) or not data:
        raise RuntimeError("深交所尚未返回该月日历；不能推断全月休市")
    rows = []
    for rec in data:
        if str(rec.get("jybz")) not in ("0", "1") or not rec.get("jyrq"):
            raise RuntimeError("深交所日历字段异常")
        rows.append({"date": _official_date(rec["jyrq"]), "is_open": str(rec["jybz"]) == "1"})
    frame = _official_frame(rows, ["date"], "szse", response.url)
    if set(frame.date) != expected:
        raise RuntimeError("日历月份错位或日期不完整，不能继续调度")
    return frame
```
<!-- official-data-core:end -->

```python
members = index_constituents("000300")
weights = index_weights("399006", provider="cni")
valuation = index_valuation("000300")
days = trading_calendar(2026, 9)
print(members[["date", "code", "name"]].head())
print(weights[["date", "code", "weight_percent"]].head())
print(valuation.tail(1))
print(days.loc[days.is_open, "date"].tolist())
```

原始端点的发现与交叉核对参考：
[AKShare 中证成分](https://github.com/akfamily/akshare/blob/main/akshare/index/index_cons.py)、
[AKShare 中证估值](https://github.com/akfamily/akshare/blob/main/akshare/index/index_stock_zh_csindex.py)、
[AKShare 国证](https://github.com/akfamily/akshare/blob/main/akshare/index/index_cni.py)、
[Qlib 交易日历](https://github.com/microsoft/qlib/blob/main/scripts/data_collector/utils.py)。
本实现直接读取官方文件/API，不调用上述项目的包装库。

## Layer 13: 期货与大宗商品（V3.9.0 新增 · #49）

A 股之外的商品与股指衍生品：交易所官方日行情、商品期权、会员持仓排名，加新浪日 K 与实时行情、A50 期指与上海金交所现货。
先执行 Prerequisites 的 V3.9.0 共用 helper，再执行下面整块。

| 函数 | 覆盖 | 说明 |
|---|---|---|
| `futures_daily(date, exchange)` | 上期所 SHFE / 上期能源 INE / 郑商所 CZCE / 中金所 CFFEX / 广期所 GFEX | 一行一个合约：开高低收、结算、昨结、成交量、持仓、成交额（万元） |
| `options_daily(date, exchange)` | 同上五所的商品期权 / 股指期权 | 行权价、看涨看跌、Delta、隐含波动率（逐合约或按系列） |
| `futures_position_rank(date, exchange, symbol=None)` | SHFE / INE / CZCE / CFFEX | 成交量 / 持买单 / 持卖单前 20 名会员 |
| `futures_realtime(symbols)` | 全部六家（含大商所） | 新浪实时价 / 盘口；`RB0` 主力连续、`CU2610` 具体合约 |
| `futures_kline(symbol, start, end)` | 全部六家（含大商所） | 新浪日 K：单个合约或主力连续的逐日开高低收、结算、成交量、持仓（V3.10.0） |
| `a50_futures()` | 富时中国 A50 | 新浪连续合约报价，盘前 / 夜盘看外资情绪 |
| `sge_spot(instrument)` | 上海黄金交易所 | 现货日线 2016-12 至今：`Au99.99` / `Au(T+D)` / `Ag(T+D)` … |

**边界：** 大商所（DCE）官网有 JS 反爬（纯 HTTP 返回 412），官方日行情未接入；大商所品种（豆粕 M、铁矿 I…）的逐日 K 线用 `futures_kline`（新浪），实时用 `futures_realtime`。
各所实测可用起点：上期所 2002-01-07 起（2021 年及以前无成交额，`turnover_10k` 为 None）；上期能源 2018-03 开业；
郑商所 2015-09-21 起（更早是另一套格式，未接入）；中金所 2010-04-16 开业即有；广期所 2022-12 开业。
上期所的官方文件里混着上期能源的品种，已按能源中心同日文件剔除，SHFE 与 INE 两次调用不会重复；能源中心对照文件在它开始发布之后缺失时抛错，不会把能源品种算进上期所。
中金所持仓排名按各品种上市日确定当天应有的品种（IF 2010-04-16 … TL 2023-04-21），已上市品种缺文件抛错，不返回部分品种。
中金所日行情 / 期权的 CSV 里没有交易日列，用同目录 `index.xml` 每行的 tradingday 核对，并逐合约比对成交量 / 收盘价 / 持仓量，对不上抛错。
非交易日 / 未发布 / 该品种当时未上市抛 `ValueError`；交易所返回其他日期、表头改变、代码重复、文件不全抛 `RuntimeError`。
ETF 期权不在这里，见 Layer 9。

### 13.1–13.7 自包含实现

<!-- v39-futures:start -->
```python
import csv
import io
import json
import re
from xml.etree import ElementTree

FUTURES_EXCHANGES = ("SHFE", "INE", "CZCE", "CFFEX", "GFEX")
_SHFE_HOSTS = {"SHFE": "https://www.shfe.com.cn", "INE": "https://www.ine.cn"}
CZCE_FILE_URL = "https://www.czce.com.cn/cn/DFSStaticFiles/{kind}/{year}/{ymd}/{name}.txt"
CZCE_FIRST_DAY = "20150921"      # 郑商所现行文件路径的第一天；更早是另一套无表头 CSV，未接入
CFFEX_DAILY_URL = "http://www.cffex.com.cn/fzjy/mrhq/{ym}/{dd}/{ymd}_1.csv"
CFFEX_DAILY_XML = "http://www.cffex.com.cn/fzjy/mrhq/{ym}/{dd}/index.xml"
CFFEX_RANK_URL = "http://www.cffex.com.cn/sj/ccpm/{ym}/{dd}/{product}_1.csv"
# 各品种持仓排名文件的第一天（2026-09-20 逐个二分实测，前一交易日都是 302 缺文件）
CFFEX_RANK_FIRST_DAY = {"IF": "20100416", "IH": "20150416", "IC": "20150416", "IM": "20220722",
                        "TS": "20180817", "TF": "20130906", "T": "20150320", "TL": "20230421"}
GFEX_DAILY_URL = "http://www.gfex.com.cn/u/interfacesWebTiDayQuotes/loadList"
SINA_HQ_URL = "https://hq.sinajs.cn/list="
SINA_FUT_KLINE_URL = ("https://stock2.finance.sina.com.cn/futures/api/jsonp.php/var%20_{code}="
                      "/InnerFuturesNewService.getDailyKLine")
SGE_DAILY_URL = "https://www.sge.com.cn/graph/Dailyhq"
_CFFEX_SINA_PRODUCTS = ("IF", "IH", "IC", "IM", "TS", "TF", "T", "TL")
_DCE_HINT = ("大商所官网有 JS 反爬（纯 HTTP 返回 412），不提供官方日行情；大商所品种（豆粕 M、铁矿 I、塑料 L…）"
             "请用 futures_kline('M0') 取逐日 K 线（新浪），futures_realtime('M0') 取实时/收盘快照")
_FUT_COLUMNS = ["date", "exchange", "symbol", "product", "open", "high", "low", "close", "settle",
                "pre_settle", "volume", "open_interest", "oi_change", "turnover_10k"]
_OPT_COLUMNS = ["date", "exchange", "symbol", "series", "option_type", "strike", "open", "high",
                "low", "close", "settle", "pre_settle", "volume", "open_interest", "oi_change",
                "turnover_10k", "delta", "iv_pct", "series_iv_pct"]
_RANK_COLUMNS = ["date", "exchange", "level", "symbol", "rank", "volume_member", "volume",
                 "volume_chg", "long_member", "long_oi", "long_chg", "short_member", "short_oi",
                 "short_chg"]


def _fut_price(value):
    """期货/期权价格：0 不是有效价格（无成交时交易所填 0 或空），统一成 None。"""
    number = _v39_num(value)
    return None if number == 0 else number


def _fut_product(code):
    """合约代码的品种字母（rb2610 -> rb、IF2609 -> IF）；不是字母开头说明来源格式变了。"""
    match = re.match(r"[A-Za-z]+", str(code))
    if not match:
        raise RuntimeError(f"合约代码 {code!r} 不是字母开头，格式可能已变")
    return match.group(0)


def _fut_exchange(exchange):
    exchange = str(exchange).upper()
    if exchange == "DCE":
        raise ValueError(_DCE_HINT)
    if exchange not in FUTURES_EXCHANGES:
        raise ValueError("exchange 只能是 " + " / ".join(FUTURES_EXCHANGES) + "（大商所见 futures_kline / futures_realtime）")
    return exchange


def _shfe_json(exchange, path, ymd, key, allow_missing=False):
    """上期所 / 上期能源的 .dat（实为 JSON）。非交易日官网 404；allow_missing 时返回 (None, url)。
    key 是调用方要读的行列表字段（o_curinstrument / o_cursor）；顶层不是对象、它不是由对象组成的列表，抛 RuntimeError。"""
    url = f"{_SHFE_HOSTS[exchange]}/data/tradedata/{path}{ymd}.dat"
    first = _INE_FIRST_DAY.get(path) if exchange == "INE" else None
    if first and ymd < first:
        # 能源中心首日前有些日子也发文件，但里面没有该类合约；按「当时还没有」处理，不能报成格式改变
        if allow_missing:
            return None, url
        raise ValueError(f"上期能源该类数据从 {first} 起才有（{ymd} 早于首日）")
    response = _v39_http(url, timeout=(10, 60), allow_status=(404,))
    payload = None
    if response.status_code != 404:
        try:
            payload = json.loads(response.content.decode("utf-8"))
        except ValueError as exc:       # 含 UnicodeDecodeError：错误页不是「没有数据」
            raise RuntimeError(f"{exchange} {url} 返回的不是 JSON，可能是错误页") from exc
        rows = payload.get(key) if isinstance(payload, dict) else None
        if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
            raise RuntimeError(f"{exchange} {url} 的 {key} 不是由对象组成的列表，格式可能已变")
        reported = payload.get("report_date")
        if reported is not None and str(reported) != ymd:
            raise RuntimeError(f"{exchange} 返回的 report_date={reported}，不是 {ymd}")
        # 早年文件没有 report_date（上期所 2015 年的排名文件），只能以文件名里的日期为准；
        # 能源中心 2019 年的排名文件则是「没有 report_date + 列表为空」的空壳，按没有数据处理
        if reported is None and not any(v for v in payload.values() if isinstance(v, list)):
            payload = None
    if payload is None:
        if allow_missing:
            return None, url
        raise ValueError(f"{exchange} {ymd} 没有数据：非交易日、尚未发布或该品种当时未上市")
    return payload, url


def _czce_text(kind, name, ymd):
    if ymd < CZCE_FIRST_DAY:
        raise ValueError(f"郑商所数据从 {CZCE_FIRST_DAY} 起接入（更早的文件是另一套格式）")
    url = CZCE_FILE_URL.format(kind=kind, year=ymd[:4], ymd=ymd, name=name)
    response = _v39_http(url, timeout=(10, 60), allow_status=(404,))
    if response.status_code == 404:
        raise ValueError(f"郑商所 {ymd} 没有 {name}：非交易日或尚未发布")
    try:
        text = response.content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = response.content.decode("gbk")   # 2017 年及以前的文件是 GBK
    if f"({ymd[:4]}-{ymd[4:6]}-{ymd[6:]})" not in text.split("\n", 1)[0] + text[:200]:
        raise RuntimeError(f"郑商所 {name} 标题里的日期不是 {ymd}")
    return text, url


# 郑商所 2021 年前的表头叫「品种月份 / 品种代码」「空盘量」，与现在的「合约代码」「持仓量」是同一列
_CZCE_HEADER_ALIAS = {"品种月份": "合约代码", "品种代码": "合约代码", "空盘量": "持仓量"}


def _czce_table(text, header_prefix):
    """郑商所竖线分隔表：返回 (表头, 数据行)，千分位逗号已去掉，小计/总计已剔除。"""
    lines = [line for line in text.splitlines() if "|" in line]
    header = [_CZCE_HEADER_ALIAS.get(c.strip(), c.strip()) for c in lines[0].split("|")] if lines else []
    if not header or header[0] != header_prefix:
        raise RuntimeError("郑商所文件表头改变")
    rows = []
    for line in lines[1:]:
        cells = [c.strip().replace(",", "") for c in line.split("|")]
        if not cells[0] or cells[0].endswith(("小计", "总计", "合计")):
            continue                            # 期权文件还有「AP合计」这类品种合计行
        rows.append(dict(zip(header, cells)))
    return header, rows


def _cffex_csv(url, allow_missing=False):
    response = _v39_http(url, timeout=(10, 60), allow_status=(302, 404), allow_redirects=False)
    # 中金所缺文件时 302 跳到 error_404 页面
    if response.status_code in (302, 404):
        if allow_missing:
            return None
        raise ValueError(f"中金所没有该文件（非交易日或尚未发布）: {url}")
    return list(csv.reader(io.StringIO(response.content.decode("gbk"))))


def _cffex_daily_table(ymd):
    """中金所日行情 CSV（期货 + 期权同一个文件）。CSV 里没有交易日列，同目录的 index.xml 每行都带
    tradingday；用它核对交易日，并逐合约核对成交量 / 收盘价 / 持仓量，对不上就抛 RuntimeError，
    不把别的交易日的文件标成这一天（2010–2026 抽 5 天实测两者逐合约一致）。"""
    url = CFFEX_DAILY_URL.format(ym=ymd[:6], dd=ymd[6:], ymd=ymd)
    table = _cffex_csv(url)
    if not table or table[0][:3] != ["合约代码", "今开盘", "最高价"]:
        raise RuntimeError("中金所日行情表头改变")
    xml_url = CFFEX_DAILY_XML.format(ym=ymd[:6], dd=ymd[6:])
    response = _v39_http(xml_url, timeout=(10, 60), allow_status=(302, 404), allow_redirects=False)
    if response.status_code in (302, 404):
        raise RuntimeError(f"中金所 {ymd} 有行情 CSV 却没有 index.xml，无法核对交易日: {xml_url}")
    if b"<!DOCTYPE" in response.content or b"<!ENTITY" in response.content:
        raise RuntimeError(f"中金所 index.xml 含 DOCTYPE / ENTITY，拒绝解析: {xml_url}")
    try:
        nodes = ElementTree.fromstring(response.content).findall("dailydata")
    except ElementTree.ParseError as exc:
        raise RuntimeError(f"中金所 index.xml 无法解析: {exc}") from exc
    witness = {}
    for node in nodes:
        values = {k: (node.findtext(k) or "").strip() for k in
                  ("instrumentid", "tradingday", "volume", "closeprice", "openinterest")}
        if values["tradingday"] != ymd:
            raise RuntimeError(f"中金所 index.xml 的交易日是 {values['tradingday']}，不是 {ymd}")
        witness[values["instrumentid"]] = tuple(_v39_num(values[k]) for k in ("volume", "closeprice", "openinterest"))
    header = [c.strip() for c in table[0]]
    csv_rows = {}
    for rec in table[1:]:
        code = rec[0].strip() if rec else ""
        if not code or code in ("小计", "合计", "总计"):
            continue
        r = dict(zip(header, rec))
        csv_rows[code] = tuple(_v39_num(r.get(k)) for k in ("成交量", "今收盘", "持仓量"))
    if not witness or len(witness) != len(nodes) or csv_rows != witness:
        diff = sorted(set(csv_rows) ^ set(witness)) or sorted(k for k in csv_rows if csv_rows[k] != witness.get(k))
        raise RuntimeError(f"中金所 {ymd} 行情 CSV 与 index.xml 对不上（{len(csv_rows)} / {len(witness)} 个合约，"
                           f"例如 {diff[:3]}），不能确认 CSV 属于这一天")
    return table, url


_CFFEX_RANK_SUB = ["会员简称", "成交量", "比上一交易日增减", "会员简称", "持买单量", "比上一交易日增减",
                   "会员简称", "持卖单量", "比上一交易日增减"]


def _cffex_rank_rows(table, product, ymd):
    """中金所持仓排名 CSV → 行。只在核对过两行表头的「排名」段里取数，列顺序不对就抛错。
    2015 年前后的旧文件在排名段前面还有一段「会员类别」合计（表头同样以 交易日,合约 开头），跳过。"""
    out, in_rank, i = [], False, 0
    while i < len(table):
        cells = [c.strip() for c in table[i]]
        if cells[:2] == ["交易日", "合约"]:
            in_rank = cells[2:3] == ["排名"]
            if in_rank:
                sub = [c.strip() for c in table[i + 1][3:12]] if i + 1 < len(table) else []
                if cells[3:12:3] != ["成交量排名", "持买单量排名", "持卖单量排名"] or sub != _CFFEX_RANK_SUB:
                    raise RuntimeError(f"中金所 {product} 持仓排名表头变了: {cells} / {sub}")
                i += 1
        elif cells[2:3] and cells[2].isdigit():
            if not in_rank:
                raise RuntimeError(f"中金所 {product} 持仓排名在排名表头之前出现数据行: {cells}")
            if len(cells) < 12:
                raise RuntimeError(f"中金所 {product} 持仓排名行缺列: {cells}")
            if cells[0] != ymd:
                raise RuntimeError(f"中金所 {product} 持仓排名交易日是 {cells[0]}，不是 {ymd}")
            out.append({"level": "contract", "symbol": cells[1], "rank": int(cells[2]),
                        "volume_member": _rank_member(cells[3]), "volume": _v39_num(cells[4]),
                        "volume_chg": _v39_num(cells[5]),
                        "long_member": _rank_member(cells[6]), "long_oi": _v39_num(cells[7]),
                        "long_chg": _v39_num(cells[8]),
                        "short_member": _rank_member(cells[9]), "short_oi": _v39_num(cells[10]),
                        "short_chg": _v39_num(cells[11])})
        i += 1
    return out


def _gfex_rows(ymd, trade_type):
    response = _v39_http(GFEX_DAILY_URL, method="POST", data={"trade_date": ymd, "trade_type": trade_type},
                         headers={"Referer": "http://www.gfex.com.cn/gfex/rihq/hqsj_tjsj.shtml"})
    payload = _v39_json(response)
    if not isinstance(payload, dict) or str(payload.get("code")) != "0":
        raise RuntimeError(f"广期所返回错误: {str(payload)[:200]}")
    # 广期所的行里没有交易日字段，只在 param 里回显请求参数；回显不符说明拿到的不是这次请求的结果。
    # 非交易日它返回空表（只剩合计行），不会回退到最近交易日（2026-09-19 周六实测）。
    param = payload.get("param")
    if not isinstance(param, dict):
        raise RuntimeError(f"广期所没有回显请求参数（param 应为对象）: {str(payload)[:200]}")
    data = _v39_rows(payload.get("data"), "广期所 data")
    if param.get("trade_date") not in ([ymd], ymd) or param.get("trade_type") not in ([str(trade_type)], str(trade_type)):
        raise RuntimeError(f"广期所回显的请求参数 {param} 与请求的 {ymd}/{trade_type} 不符")
    rows = []
    for r in data:
        if str(r.get("variety", "")).endswith(("小计", "总计")):
            continue
        # 实测（2022-12-22、2026-09-18/19）只有小计 / 总计行没有 delivMonth；字段改名时不能把合约行全部滤掉、报成非交易日
        if not r.get("delivMonth"):
            raise RuntimeError(f"广期所合约行缺 delivMonth，格式可能已变: {str(r)[:120]}")
        rows.append(r)
    if not rows:
        raise ValueError(f"广期所 {ymd} 没有行情：非交易日或尚未发布")
    return rows, response.url


# 能源中心各文件的第一天（2026-09-20 二分实测）：日行情 2018-03-26 开业即有；持仓排名 2020-07-03 起
# （07-02 仍是空壳，当时上期所排名里也没有能源品种）；期权日行情 2021-06-21 原油期权上市起
# （06-15~18 已发文件但里面没有期权合约，2026-09-22 复测）
_INE_FIRST_DAY = {"future/dailydata/kx": "20180326", "future/dailydata/pm": "20200703",
                  "option/dailydata/kx": "20210621"}


def _shfe_ine_ids(path, ymd, key, field):
    """上期所文件里混有上期能源的品种；取能源中心同一天的 ID 集合用来剔除。
    能源中心该文件第一天之前没有文件（或是空壳），上期所文件里也没有能源品种，返回空集合；
    第一天起缺文件不能当成「没有能源品种」，否则 sc 等合约会被标成上期所，直接抛 RuntimeError。"""
    payload, url = _shfe_json("INE", path, ymd, key, allow_missing=True)
    ids = {str(r[field]).strip() for r in payload[key]} if payload else set()
    if not ids and ymd >= _INE_FIRST_DAY[path]:
        raise RuntimeError(f"上期能源 {ymd} 的对照文件缺失或为空（{url}），无法从上期所数据里剔除能源品种；"
                           "可能尚未发布，稍后重试")
    return ids


@_v39_contract
def futures_daily(date, exchange):
    """期货日行情（交易所官方收盘数据）— 上期所 / 上期能源 / 郑商所 / 中金所 / 广期所。

    exchange: 'SHFE' / 'INE' / 'CZCE' / 'CFFEX' / 'GFEX'；大商所（DCE）官网有反爬，见 futures_kline / futures_realtime。
    一行一个合约（不含小计），settle 为当日结算价，turnover_10k 单位万元，价格为 0 的统一成 None。
    上期所的官方文件里也包含上期能源的品种（原油、20号胶等），这里按能源中心同日文件剔除，
    所以 SHFE 与 INE 两次调用不会重复。非交易日抛 ValueError。
    实测可用起点：上期所 2002-01-07 起（2021 年及以前没有成交额，turnover_10k 为 None）；
    上期能源 2018-03 开业；郑商所 2015-09-21 起（更早是另一套格式，未接入）；中金所 2010-04-16 开业即有；广期所 2022-12 开业。
    """
    exchange = _fut_exchange(exchange)
    day = _v39_date(date)
    ymd = day.replace("-", "")
    rows = []
    if exchange in ("SHFE", "INE"):
        payload, url = _shfe_json(exchange, "future/dailydata/kx", ymd, "o_curinstrument")
        skip = (_shfe_ine_ids("future/dailydata/kx", ymd, "o_curinstrument", "PRODUCTID")
                if exchange == "SHFE" else set())
        for r in payload["o_curinstrument"]:
            month = str(r.get("DELIVERYMONTH", "")).strip()
            product_id = r["PRODUCTID"].strip()
            # 期货品种 ID 以 _f 结尾（cu_f）；sc_tas 是原油 TAS 指令，价格恒为 0，不是独立合约。
            # 不用 PRODUCTCLASS 判断：这个字段 2023 年才出现
            if not product_id.endswith("_f") or not month.isdigit() or product_id in skip:
                continue
            rows.append({"symbol": product_id[:-2] + month,
                         "product": r["PRODUCTNAME"].strip(),
                         "open": _fut_price(r["OPENPRICE"]), "high": _fut_price(r["HIGHESTPRICE"]),
                         "low": _fut_price(r["LOWESTPRICE"]), "close": _fut_price(r["CLOSEPRICE"]),
                         "settle": _fut_price(r["SETTLEMENTPRICE"]),
                         "pre_settle": _fut_price(r["PRESETTLEMENTPRICE"]),
                         "volume": _v39_num(r["VOLUME"]), "open_interest": _v39_num(r["OPENINTEREST"]),
                         "oi_change": _v39_num(r["OPENINTERESTCHG"]),
                         "turnover_10k": _v39_num(r.get("TURNOVER"))})   # 2021 年及以前的文件没有成交额，为 None
    elif exchange == "CZCE":
        text, url = _czce_text("Future", "FutureDataDaily", ymd)
        _, table = _czce_table(text, "合约代码")
        for r in table:
            rows.append({"symbol": r["合约代码"], "product": _fut_product(r["合约代码"]),
                         "open": _fut_price(r["今开盘"]), "high": _fut_price(r["最高价"]),
                         "low": _fut_price(r["最低价"]), "close": _fut_price(r["今收盘"]),
                         "settle": _fut_price(r["今结算"]), "pre_settle": _fut_price(r["昨结算"]),
                         "volume": _v39_num(r["成交量(手)"]), "open_interest": _v39_num(r["持仓量"]),
                         "oi_change": _v39_num(r["增减量"]), "turnover_10k": _v39_num(r["成交额(万元)"])})
    elif exchange == "CFFEX":
        table, url = _cffex_daily_table(ymd)
        for rec in table[1:]:
            code = rec[0].strip()
            if not code or code in ("小计", "合计", "总计") or "-C-" in code or "-P-" in code:
                continue
            r = dict(zip(table[0], rec))
            rows.append({"symbol": code, "product": _fut_product(code),
                         "open": _fut_price(r["今开盘"]), "high": _fut_price(r["最高价"]),
                         "low": _fut_price(r["最低价"]), "close": _fut_price(r["今收盘"]),
                         "settle": _fut_price(r["今结算"]), "pre_settle": _fut_price(r["前结算"]),
                         "volume": _v39_num(r["成交量"]), "open_interest": _v39_num(r["持仓量"]),
                         "oi_change": _v39_num(r["持仓变化"]), "turnover_10k": _v39_num(r["成交金额"])})
    else:
        data, url = _gfex_rows(ymd, 0)
        for r in data:
            rows.append({"symbol": r["varietyOrder"] + r["delivMonth"], "product": r["variety"],
                         "open": _fut_price(r["open"]), "high": _fut_price(r["high"]),
                         "low": _fut_price(r["low"]), "close": _fut_price(r["close"]),
                         "settle": _fut_price(r["clearPrice"]), "pre_settle": _fut_price(r["lastClear"]),
                         "volume": _v39_num(r["volumn"]), "open_interest": _v39_num(r["openInterest"]),
                         "oi_change": _v39_num(r["diffI"]), "turnover_10k": _v39_num(r["turnover"])})
    if not rows:
        raise RuntimeError(f"{exchange} {day} 解析出 0 个期货合约，格式可能已变")
    for row in rows:
        row["date"], row["exchange"] = day, exchange
    frame = _v39_frame(rows, exchange.lower(), url, _FUT_COLUMNS)
    if frame.duplicated(["symbol"]).any():
        raise RuntimeError(f"{exchange} {day} 期货合约代码重复")
    return frame


# 郑商所 CF/RM/OI/SR 另有带两位字母后缀的系列（如 CF701MSC14400），后缀并入 series 原样保留
_OPTION_CODE = re.compile(r"^([A-Za-z]+\d{3,4}(?:[A-Z]{2})?)-?([CP])-?(\d+(?:\.\d+)?)$")


@_v39_contract
def options_daily(date, exchange):
    """商品期权 / 股指期权日行情（交易所官方）— 上期所 / 上期能源 / 郑商所 / 中金所 / 广期所。

    series：期权系列（商品期权 = 标的期货合约，如 cu2610；中金所 = HO/IO/MO + 月份；
    郑商所部分品种另有 CF701MS 这类带后缀的系列，按官方代码原样保留，与 CF701 分开）。
    delta：交易所公布值（中金所不公布，为 None）。
    iv_pct：逐合约隐含波动率 %（郑商所、广期所公布）；series_iv_pct：上期所/能源中心按系列公布的
    隐含波动率（官方 SIGMA × 100）。ETF 期权不在这里，见 Layer 9。非交易日抛 ValueError。
    各所期权上市时间不同（上期所铜期权 2018-09、郑商所白糖期权 2017-04），之前的日期抛 ValueError。
    """
    exchange = _fut_exchange(exchange)
    day = _v39_date(date)
    ymd = day.replace("-", "")
    rows = []
    if exchange in ("SHFE", "INE"):
        payload, url = _shfe_json(exchange, "option/dailydata/kx", ymd, "o_curinstrument")
        skip = (_shfe_ine_ids("option/dailydata/kx", ymd, "o_curinstrument", "PRODUCTID")
                if exchange == "SHFE" else set())
        sigma_rows = _v39_rows(payload.get("o_cursigma"), f"{exchange} {url} 的 o_cursigma")
        if not all("INSTRUMENTID" in r for r in sigma_rows):
            raise RuntimeError(f"{exchange} {url} 的 o_cursigma 行没有 INSTRUMENTID")
        # 字典推导会让重复的 INSTRUMENTID 静默相互覆盖，返回错误的隐含波动率。
        # 2026-09-20 抽查 10 个交易日（2018-09-21 期权首日起）：只有按品种汇总的「小计」行
        # 重复且 SIGMA 恒为空，真实系列 ID 不重复、SIGMA 无空值。
        sigma = {}
        for r in sigma_rows:
            series_id = str(r["INSTRUMENTID"]).strip()
            if series_id in ("小计", "合计", "总计"):
                continue
            if not series_id:
                raise RuntimeError(f"{exchange} {url} 的 o_cursigma 有空的 INSTRUMENTID")
            if series_id in sigma:
                raise RuntimeError(f"{exchange} {url} 的 o_cursigma 里 {series_id} 出现两次，"
                                   "隐含波动率会互相覆盖")
            sigma[series_id] = _v39_req_num(r.get("SIGMA"), f"{exchange} {series_id} 的 SIGMA")
        for r in payload["o_curinstrument"]:
            code = str(r.get("INSTRUMENTID", "")).strip()
            kind = {"1": "C", "2": "P"}.get(str(r.get("OPTIONSTYPE")))
            if kind is None or r["PRODUCTID"].strip() in skip:
                continue                        # 小计 / 总计 行 OPTIONSTYPE 为空
            parsed = _OPTION_CODE.match(code)
            if not parsed or parsed.group(2) != kind:
                raise RuntimeError(f"{exchange} 期权 {code} 的代码与 OPTIONSTYPE={r.get('OPTIONSTYPE')} 不一致")
            series = str(r["UNDERLYINGINSTRID"]).strip()
            if series not in sigma:     # 实测 10 个交易日里主表每个系列都有 sigma 行
                raise RuntimeError(f"{exchange} {url} 的 o_cursigma 里没有系列 {series}，结果不完整")
            iv = sigma[series]
            rows.append({"symbol": code, "series": series, "option_type": kind,
                         "strike": _v39_num(r["STRIKEPRICE"]),
                         "open": _fut_price(r["OPENPRICE"]), "high": _fut_price(r["HIGHESTPRICE"]),
                         "low": _fut_price(r["LOWESTPRICE"]), "close": _fut_price(r["CLOSEPRICE"]),
                         "settle": _fut_price(r["SETTLEMENTPRICE"]),
                         "pre_settle": _fut_price(r["PRESETTLEMENTPRICE"]),
                         "volume": _v39_num(r["VOLUME"]), "open_interest": _v39_num(r["OPENINTEREST"]),
                         "oi_change": _v39_num(r["OPENINTERESTCHG"]), "turnover_10k": _v39_num(r["TURNOVER"]),
                         "delta": _v39_num(r.get("DELTA")), "iv_pct": None,
                         "series_iv_pct": round(iv * 100, 4) if iv is not None else None})
    elif exchange == "CZCE":
        text, url = _czce_text("Option", "OptionDataDaily", ymd)
        if "无交易记录" in text:
            raise ValueError(f"郑商所 {ymd} 没有期权成交记录（郑商所期权 2017-04-19 起上市）")
        _, table = _czce_table(text, "合约代码")
        for r in table:
            parsed = _OPTION_CODE.match(r["合约代码"])
            if not parsed:
                raise RuntimeError(f"郑商所期权代码无法解析: {r['合约代码']}")
            rows.append({"symbol": r["合约代码"], "series": parsed.group(1), "option_type": parsed.group(2),
                         "strike": _v39_num(parsed.group(3)),
                         "open": _fut_price(r["今开盘"]), "high": _fut_price(r["最高价"]),
                         "low": _fut_price(r["最低价"]), "close": _fut_price(r["今收盘"]),
                         "settle": _fut_price(r["今结算"]), "pre_settle": _fut_price(r["昨结算"]),
                         "volume": _v39_num(r["成交量(手)"]), "open_interest": _v39_num(r["持仓量"]),
                         "oi_change": _v39_num(r["增减量"]), "turnover_10k": _v39_num(r["成交额(万元)"]),
                         "delta": _v39_num(r["DELTA"]), "iv_pct": _v39_num(r["隐含波动率"]),
                         "series_iv_pct": None})
    elif exchange == "CFFEX":
        table, url = _cffex_daily_table(ymd)
        for rec in table[1:]:
            code = rec[0].strip()
            if "-C-" not in code and "-P-" not in code:
                continue
            parsed = _OPTION_CODE.match(code)
            if not parsed:
                raise RuntimeError(f"中金所期权代码无法解析: {code}")
            r = dict(zip(table[0], rec))
            rows.append({"symbol": code, "series": parsed.group(1), "option_type": parsed.group(2),
                         "strike": _v39_num(parsed.group(3)),
                         "open": _fut_price(r["今开盘"]), "high": _fut_price(r["最高价"]),
                         "low": _fut_price(r["最低价"]), "close": _fut_price(r["今收盘"]),
                         "settle": _fut_price(r["今结算"]), "pre_settle": _fut_price(r["前结算"]),
                         "volume": _v39_num(r["成交量"]), "open_interest": _v39_num(r["持仓量"]),
                         "oi_change": _v39_num(r["持仓变化"]), "turnover_10k": _v39_num(r["成交金额"]),
                         "delta": None, "iv_pct": None, "series_iv_pct": None})
    else:
        data, url = _gfex_rows(ymd, 1)
        for r in data:
            parsed = _OPTION_CODE.match(r["delivMonth"])
            if not parsed:
                raise RuntimeError(f"广期所期权代码无法解析: {r['delivMonth']}")
            rows.append({"symbol": r["delivMonth"], "series": parsed.group(1), "option_type": parsed.group(2),
                         "strike": _v39_num(parsed.group(3)),
                         "open": _fut_price(r["open"]), "high": _fut_price(r["high"]),
                         "low": _fut_price(r["low"]), "close": _fut_price(r["close"]),
                         "settle": _fut_price(r["clearPrice"]), "pre_settle": _fut_price(r["lastClear"]),
                         "volume": _v39_num(r["volumn"]), "open_interest": _v39_num(r["openInterest"]),
                         "oi_change": _v39_num(r["diffI"]), "turnover_10k": _v39_num(r["turnover"]),
                         "delta": _v39_num(r["delta"]), "iv_pct": _v39_num(r["impliedVolatility"]),
                         "series_iv_pct": None})
    if not rows:
        raise RuntimeError(f"{exchange} {day} 解析出 0 个期权合约，格式可能已变")
    for row in rows:
        row["date"], row["exchange"] = day, exchange
    frame = _v39_frame(rows, exchange.lower(), url, _OPT_COLUMNS)
    if frame.duplicated(["symbol"]).any():
        raise RuntimeError(f"{exchange} {day} 期权合约代码重复")
    return frame


def _rank_member(value):
    value = str(value or "").strip()
    return value if value and value != "-" else None


@_v39_contract
def futures_position_rank(date, exchange, symbol=None):
    """期货会员成交量 / 持买单 / 持卖单前 20 名（交易所官方持仓排名）。

    exchange: 'SHFE' / 'INE' / 'CZCE' / 'CFFEX'（广期所、大商所未接入）。
    level='contract' 为单个合约；level='product' 为品种合计，只有郑商所公布（symbol 为品种字母，如 AP）。
    上期所 / 能源中心文件里的 cuall 行是按会员类型的汇总、没有名次，已剔除。
    symbol 可选，按合约或品种过滤（不区分大小写）。中金所按 IF/IH/IC/IM/TS/TF/T/TL 各取一个文件，
    当天已上市的品种缺任何一个都抛 RuntimeError（不返回部分品种）；source_url 列出实际读取的文件。
    上期能源 2019 年的排名文件是空的（抛 ValueError），实测 2021 年起有数据。
    """
    exchange = _fut_exchange(exchange)
    if exchange == "GFEX":
        raise ValueError("广期所持仓排名未接入")
    day = _v39_date(date)
    ymd = day.replace("-", "")
    rows = []
    if exchange in ("SHFE", "INE"):
        payload, url = _shfe_json(exchange, "future/dailydata/pm", ymd, "o_cursor")
        skip = (_shfe_ine_ids("future/dailydata/pm", ymd, "o_cursor", "INSTRUMENTID")
                if exchange == "SHFE" else set())
        for r in payload["o_cursor"]:
            code = str(r["INSTRUMENTID"]).strip()
            rank = _v39_num(r["RANK"])
            if rank is None:
                raise RuntimeError(f"{exchange} {code} 持仓排名缺名次字段")
            # RANK 1–20 为会员名次；999 = 该合约合计，-1 / 0 = 按会员类型汇总
            if not 1 <= rank <= 20 or code in skip:
                continue
            rows.append({"level": "contract", "symbol": code,
                         "rank": int(rank),
                         "volume_member": _rank_member(r["PARTICIPANTABBR1"]), "volume": _v39_num(r["CJ1"]),
                         "volume_chg": _v39_num(r["CJ1_CHG"]),
                         "long_member": _rank_member(r["PARTICIPANTABBR2"]), "long_oi": _v39_num(r["CJ2"]),
                         "long_chg": _v39_num(r["CJ2_CHG"]),
                         "short_member": _rank_member(r["PARTICIPANTABBR3"]), "short_oi": _v39_num(r["CJ3"]),
                         "short_chg": _v39_num(r["CJ3_CHG"])})
    elif exchange == "CZCE":
        text, url = _czce_text("Future", "FutureDataHolding", ymd)
        level = code = None
        for line in text.splitlines():
            head = re.match(r"^(品种|合约)：\s*(\S+)\s+日期：", line)
            if head:
                level = "product" if head.group(1) == "品种" else "contract"
                found = re.search(r"[A-Za-z]+\d*$", head.group(2))
                if not found:
                    raise RuntimeError(f"郑商所持仓排名表头认不出品种 / 合约: {line[:60]}")
                code = found.group(0)
                continue
            cells = [c.strip().replace(",", "") for c in line.split("|")]
            if len(cells) < 10 or not cells[0].isdigit():
                continue                        # 表头、合计行
            if code is None:
                raise RuntimeError("郑商所持仓排名在品种/合约标题之前出现数据行")
            rows.append({"level": level, "symbol": code, "rank": int(cells[0]),
                         "volume_member": _rank_member(cells[1]), "volume": _v39_num(cells[2]),
                         "volume_chg": _v39_num(cells[3]),
                         "long_member": _rank_member(cells[4]), "long_oi": _v39_num(cells[5]),
                         "long_chg": _v39_num(cells[6]),
                         "short_member": _rank_member(cells[7]), "short_oi": _v39_num(cells[8]),
                         "short_chg": _v39_num(cells[9])})
    else:
        expected = [p for p, first in CFFEX_RANK_FIRST_DAY.items() if ymd >= first]
        if not expected:
            raise ValueError("中金所持仓排名从 2010-04-16（沪深300 期货上市）起才有")
        urls, missing = [], []
        for product in expected:                # 当时还没上市的品种（如 2022 年前的 IM）不请求
            file_url = CFFEX_RANK_URL.format(ym=ymd[:6], dd=ymd[6:], product=product)
            table = _cffex_csv(file_url, allow_missing=True)
            if table is None:
                missing.append(product)
                continue
            urls.append(file_url)
            parsed = _cffex_rank_rows(table, product, ymd)
            rows.extend(parsed)
            if not parsed:
                raise RuntimeError(f"中金所 {product} {day} 持仓排名文件解析出 0 行，格式可能已变")
        if len(missing) == len(expected):
            raise ValueError(f"中金所 {day} 没有持仓排名：非交易日或尚未发布")
        if missing:
            raise RuntimeError(f"中金所 {day} 缺少已上市品种 {'/'.join(missing)} 的持仓排名，结果不完整"
                               "（可能尚未全部发布，稍后重试）")
        url = " | ".join(urls)
    if not rows:
        raise RuntimeError(f"{exchange} {day} 持仓排名解析出 0 行，格式可能已变")
    for row in rows:
        row["date"], row["exchange"] = day, exchange
    frame = _v39_frame(rows, exchange.lower(), url, _RANK_COLUMNS)
    if frame.duplicated(["level", "symbol", "rank"]).any():
        raise RuntimeError(f"{exchange} {day} 持仓排名 合约+名次 重复")
    if symbol:
        frame = frame[frame["symbol"].str.upper() == str(symbol).upper()].reset_index(drop=True)
    return frame


def _sina_hq(codes):
    response = _v39_http(SINA_HQ_URL + ",".join(codes), headers={"Referer": "https://finance.sina.com.cn/"})
    out = {}
    for key, body in re.findall(r'var hq_str_([^=]+)="([^"]*)"', response.content.decode("gbk", "replace")):
        out[key] = body.split(",") if body else []
    # 代码不存在时新浪照样回一个空内容的变量（实测 nf_ZZ9999）；一个变量都没有说明页面变了，
    # 否则会把格式改变报成「代码不存在或已摘牌」
    if not out:
        raise RuntimeError(f"新浪行情页没有 hq_str 变量（{response.url}），格式可能已变")
    return out, response.url


@_v39_contract
def futures_realtime(symbols):
    """国内期货实时行情（新浪）— 覆盖全部六家交易所，大商所品种只能走这里。

    symbols: 'RB0'（主力连续）/ 'CU2610' / 'IF2609' / 'M0' 等，可传列表；带不带 'nf_' 前缀都行。
    中金所品种（IF/IH/IC/IM/TS/TF/T/TL）另有 pre_close / 涨跌停价。无效代码抛 ValueError。
    盘中是实时价；收盘后是当日收盘快照，结算价以 futures_daily 为准。
    """
    if isinstance(symbols, str):
        symbols = [symbols]
    if not isinstance(symbols, (list, tuple, set)) or not symbols:
        raise ValueError("symbols 需为非空的代码或代码列表（例 'RB0' / ['RB0', 'IF2609']）")
    codes = []
    for raw in symbols:
        code = str(raw).strip()
        code = code[3:] if code.lower().startswith("nf_") else code
        if not re.fullmatch(r"[A-Za-z]{1,2}\d{1,4}", code):
            raise ValueError(f"期货代码格式不对: {raw}（例 RB0 / CU2610 / IF2609）")
        codes.append(code.upper())
    data, url = _sina_hq(["nf_" + c for c in codes])
    rows = []
    for code in codes:
        fields = data.get("nf_" + code)
        if not fields:
            raise ValueError(f"新浪没有期货 {code} 的行情（代码不存在或已摘牌）")
        product = _fut_product(code)
        if product in _CFFEX_SINA_PRODUCTS:
            if len(fields) < 50:
                raise RuntimeError(f"新浪中金所期货 {code} 字段数 {len(fields)}，格式可能已变")
            rows.append({"symbol": code, "name": fields[49], "datetime": f"{fields[36]} {fields[37]}",
                         "open": _fut_price(fields[0]), "high": _fut_price(fields[1]),
                         "low": _fut_price(fields[2]), "last": _fut_price(fields[3]),
                         "bid": _fut_price(fields[16]), "ask": _fut_price(fields[26]),
                         "bid_vol": _v39_num(fields[17]), "ask_vol": _v39_num(fields[27]),
                         "volume": _v39_num(fields[4]), "open_interest": _v39_num(fields[6]),
                         "pre_settle": _fut_price(fields[14]), "pre_close": _fut_price(fields[13]),
                         "upper_limit": _fut_price(fields[9]), "lower_limit": _fut_price(fields[10]),
                         "avg_price": _fut_price(fields[48])})
        else:
            if len(fields) < 28:
                raise RuntimeError(f"新浪商品期货 {code} 字段数 {len(fields)}，格式可能已变")
            clock = fields[1].zfill(6)
            rows.append({"symbol": code, "name": fields[0],
                         "datetime": f"{fields[17]} {clock[:2]}:{clock[2:4]}:{clock[4:]}",
                         "open": _fut_price(fields[2]), "high": _fut_price(fields[3]),
                         "low": _fut_price(fields[4]), "last": _fut_price(fields[8]),
                         "bid": _fut_price(fields[6]), "ask": _fut_price(fields[7]),
                         "bid_vol": _v39_num(fields[11]), "ask_vol": _v39_num(fields[12]),
                         "volume": _v39_num(fields[14]), "open_interest": _v39_num(fields[13]),
                         "pre_settle": _fut_price(fields[10]), "pre_close": None,
                         "upper_limit": None, "lower_limit": None, "avg_price": _fut_price(fields[27])})
    return _v39_frame(rows, "sina", url)


@_v39_contract
def futures_kline(symbol, start=None, end=None):
    """国内期货日 K 线（新浪）— 单个合约或主力连续的逐日序列，覆盖全部六家交易所（含大商所）。

    symbol: 'RB0' / 'M0'（主力连续）或 'RB2601' / 'M2601' / 'IF2612'；郑商所也写 4 位年月（'MA2601'），带不带 'nf_' 前缀都行。
    start/end: 'YYYY-MM-DD'，可只给一端。主力连续换月当天会跳空，未做复权。
    实测（2026-09-22）价格与交易所官方 futures_daily 逐日一致，成交量 / 持仓偶有 ≤0.1% 的出入，精确值以 futures_daily 为准。
    结算价新浪给得不全（给 0 的统一成 None）：中金所品种基本没有；主力连续早年缺得多（CU0 5285 根缺 1364 根，
    最晚缺到 2024-09-25），需要结算价用 futures_daily。具体合约只能取到约 2022 年起到期的，更早的新浪返回空；
    中金所主力连续（IF0 / IC0 / IH0 / T0 / TF0）只从 2017-01-17 起，更早的用 futures_daily。
    新浪每次都返回该代码的全部历史（RB0 约 0.5 MB），start / end 是取回后本地筛选。
    代码不存在 / 太老、区间内没有 K 线抛 ValueError；返回格式改变抛 RuntimeError。
    """
    code = str(symbol).strip()
    code = code[3:] if code.lower().startswith("nf_") else code
    if not re.fullmatch(r"[A-Za-z]{1,2}\d{1,4}", code):
        raise ValueError(f"期货代码格式不对: {symbol}（例 RB0 / RB2601 / MA2601）")
    code = code.upper()
    lo = _v39_date(start) if start else None
    hi = _v39_date(end) if end else None
    if lo and hi and lo > hi:
        raise ValueError(f"start {lo} 晚于 end {hi}")
    response = _v39_http(SINA_FUT_KLINE_URL.format(code=code), params={"symbol": code}, timeout=(5, 20),
                         headers={"Referer": "https://finance.sina.com.cn/"}, session=V39_RETRY_SESSION)
    text = response.content.decode("gbk", "replace")
    match = re.search(rf"var _{re.escape(code)}=\((.*)\);?\s*$", text, re.S)
    if not match:
        raise RuntimeError(f"新浪期货日 K {code} 的返回不是预期的 JSONP（{response.url}），格式可能已变")
    body = match.group(1).strip()
    if body == "null":
        raise ValueError(f"新浪没有期货 {code} 的日 K：代码不存在，或是约 2022 年以前到期的老合约"
                         "（郑商所也要写 4 位年月，如 MA2601）")
    try:
        items = json.loads(body)
    except ValueError as exc:
        raise RuntimeError(f"新浪期货日 K {code} 的返回不是 JSON，格式可能已变") from exc
    rows, seen = [], set()
    for r in _v39_rows(items, f"新浪期货日 K {code}"):
        day = _v39_src_date(r["d"])
        if day in seen:
            raise RuntimeError(f"新浪期货日 K {code} 同一天 {day} 出现两次，结果不可信")
        seen.add(day)
        if (lo and day < lo) or (hi and day > hi):
            continue
        rows.append({"date": day, "symbol": code,
                     "open": _fut_price(r["o"]), "high": _fut_price(r["h"]),
                     "low": _fut_price(r["l"]), "close": _fut_price(r["c"]),
                     "settle": _fut_price(r["s"]),       # 新浪没有结算价时给 0 → None
                     "volume": _v39_num(r["v"]), "open_interest": _v39_num(r["p"])})
    if not rows:
        raise ValueError(f"新浪期货 {code} 在所给区间内没有日 K（合约当时未上市或已到期）")
    rows.sort(key=lambda row: row["date"])
    return _v39_frame(rows, "sina", response.url,
                      ["date", "symbol", "open", "high", "low", "close", "settle", "volume", "open_interest"])


@_v39_contract
def a50_futures():
    """富时中国 A50 期指（新浪 hf_CHA50CFD，连续合约报价）— 盘前/夜盘看 A 股外资情绪。"""
    data, url = _sina_hq(["hf_CHA50CFD"])
    fields = data.get("hf_CHA50CFD")
    if not fields or len(fields) < 14:
        raise RuntimeError("新浪 A50 期指行情为空或字段数不对")
    row = {"name": fields[13], "datetime": f"{fields[12]} {fields[6]}",
           "last": _fut_price(fields[0]), "open": _fut_price(fields[8]),
           "high": _fut_price(fields[4]), "low": _fut_price(fields[5]),
           "bid": _fut_price(fields[2]), "ask": _fut_price(fields[3]),
           "pre_settle": _fut_price(fields[7])}
    if row["last"] is None:
        raise RuntimeError("新浪 A50 期指最新价为空")
    return _v39_frame([row], "sina", url)


@_v39_contract
def sge_spot(instrument="Au99.99"):
    """上海黄金交易所现货日线（官方）— 2016-12 至今。

    instrument 例: 'Au99.99' / 'Au(T+D)' / 'mAu(T+D)' / 'Ag(T+D)' / 'Ag99.99' / 'Pt99.95'。
    黄金单位 元/克，白银 元/千克。无成交日交易所填 0，这里剔除；代码不存在时上金所返回全 0，抛 ValueError。
    少数日子收盘价略超出高低区间是原始数据如此，日期列在 attrs['ohlc_anomaly_dates']。
    """
    response = _v39_http(SGE_DAILY_URL, method="POST", data={"instid": instrument},
                         headers={"Referer": "https://www.sge.com.cn/"})
    payload = _v39_json(response)
    series = payload.get("time") if isinstance(payload, dict) else None
    if not isinstance(series, list):
        raise RuntimeError("上金所日线返回结构改变")
    rows = []
    for rec in series:
        if not isinstance(rec, list) or len(rec) != 5:
            raise RuntimeError(f"上金所日线字段数不对: {rec}")
        prices = [_v39_num(v) for v in rec[1:]]
        # 实测 7 个品种约 1.5 万条全是数字，无成交填 0；空值 / NaN 说明格式变了，不能当无成交跳过
        if None in prices:
            raise RuntimeError(f"上金所日线出现空值或非有限数值: {rec}")
        if not all(prices):
            continue
        open_, close, low, high = prices
        rows.append({"date": _v39_src_date(rec[0]), "instrument": instrument, "open": open_,
                     "high": high, "low": low, "close": close})
    if not rows:
        raise ValueError(f"上金所没有 {instrument} 的有效行情（代码不存在时返回全 0）")
    # 实测 Au99.99 在 2017–2018 年有 17 天收盘价略超出当日高低区间（上金所原始数据如此，
    # 不是高低列颠倒）。个别日子保留原值、记在 attrs；大面积不成立才说明字段顺序变了。
    bad = [r["date"] for r in rows if not r["low"] <= min(r["open"], r["close"]) <= max(r["open"], r["close"]) <= r["high"]]
    if len(bad) > 0.05 * len(rows):
        raise RuntimeError(f"上金所日线 {len(bad)}/{len(rows)} 天高低开收关系不成立，字段顺序可能已变")
    frame = _v39_frame(rows, "sge", response.url)
    frame.attrs["ohlc_anomaly_dates"] = bad
    return frame
```
<!-- v39-futures:end -->

```python
cu = futures_daily("2026-09-18", "SHFE")
io_opt = options_daily("2026-09-18", "CFFEX")                  # 沪深300 股指期权 IO
rank = futures_position_rank("2026-09-18", "CFFEX", symbol="IF2610")
live = futures_realtime(["RB0", "M0", "IF0"])                   # M0 = 大商所豆粕主力
m_hist = futures_kline("M0", start="2026-01-01")                # 大商所豆粕主力连续的逐日 K 线
print(a50_futures()[["datetime", "last"]], sge_spot("Au99.99").tail(3))
```

---

## Layer 14: 事件驱动（V3.9.0 新增）

公司层面的事件型数据，全部来自东财数据中心（经 `em_get()` 限流，股权质押数据的原始来源是中国结算每周统计）。
`code` 不给时为全市场、按公告日倒序取 `limit` 条（上限 5000）。**全市场 0 行抛错；带了个股 / 日期条件的 0 行是「确实没有」，返回空表。**
`code` 只收个股：`sh000001` / `000001.XSHG` 这类显式沪市指数写法直接抛 `ValueError`（归一化成 000001 会查到平安银行）。
翻页排序字段都能唯一确定一行，并逐页检查重复（实测只按质押比例排序时 2212 行里重复 1 行、漏 1 行）。

| 函数 | 数据 | 单位 / 口径 |
|---|---|---|
| `earnings_forecast(code=None, report_date=None, limit=500)` | 业绩预告 | 一次预告按指标拆多行（归母净利 / 扣非 / 营收…）；金额元，变动为同比 % |
| `institution_survey(code=None, start=None, end=None, detail=False, limit=500)` | 机构调研 | `detail=False` 一次调研一行 + 机构家数；`True` 一家机构一行 |
| `holder_trades(code=None, direction=None, start=None, end=None, limit=500)` | 股东增减持 | 万股；变动股数带符号（减持为负）；占总股本 / 流通股 % |
| `share_buyback(code=None, progress=None, limit=500)` | 股票回购 | 方案上下限与已实施部分；股、元、占总股本 % |
| `equity_pledge(code=None, date=None, limit=5000)` | 股权质押比例 | 中国结算每周统计（通常周五）；万股、万元；**只覆盖沪深**，北交所代码抛错 |
| `ipo_calendar(limit=100)` | 新股申购日历 | 含尚未申购的排期；中签率 %、首日涨幅 % |

### 14.1–14.6 自包含实现

<!-- v39-events:start -->
```python
import json


def _v39_limit(limit, upper=5000):
    limit = int(limit)
    if not 1 <= limit <= upper:
        raise ValueError(f"limit 范围 1–{upper}")
    return limit


def _em_event_filter(code=None, date_field=None, start=None, end=None, extra=""):
    """拼东财 datacenter filter：个股代码 + 公告日期区间 + 额外条件。start 晚于 end 在请求前抛 ValueError。"""
    if start and end and _v39_date(start) > _v39_date(end):
        raise ValueError("start 不能晚于 end")
    parts = [extra] if extra else []
    if code is not None:
        parts.append(f'(SECURITY_CODE="{norm_ticker(code, stock_only=True)}")')
    if start:
        parts.append(f"({date_field}>='{_v39_date(start)}')")
    if end:
        parts.append(f"({date_field}<='{_v39_date(end)}')")
    return "".join(parts)


def _em_event_rows(report, filter_str, sort_columns, sort_types, limit, narrowed, extra=None,
                   equal=None, dates=None):
    """narrowed=False（全市场、不带任何条件）时 0 行说明接口坏了，直接抛错；
    带了个股 / 日期条件时 0 行是「确实没有」，返回空表。

    排序字段必须能唯一确定一行：东财按页切片，排序有并列时翻页会重复一行、同时漏掉另一行
    （实测质押表只按质押比例排序时 2212 行里重复 1 行、漏 1 行）。出现完全相同的行就直接抛错。

    服务端筛选只是请求：equal={字段: 值}、dates={日期字段: (起, 止)} 逐行核对返回的行，
    接口忽略筛选或回了别的缓存页时抛 RuntimeError，不把别的标的 / 报告期 / 日期当结果返回。"""
    rows = _em_datacenter_strict(report, filter_str, sort_columns, sort_types,
                                 page_size=min(limit, 500), max_rows=limit, extra=extra)
    if not rows and not narrowed:
        raise RuntimeError(f"东财 {report} 全市场返回 0 行，接口可能改了")
    if len({json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows}) != len(rows):
        raise RuntimeError(f"东财 {report} 翻页返回了重复行（排序不唯一），结果不完整")
    for r in rows:
        for field, value in (equal or {}).items():
            if r.get(field) != value:
                raise RuntimeError(f"东财 {report} 请求 {field}={value}，却返回了 {r.get(field)!r}，结果不可信")
        for field, (lo, hi) in (dates or {}).items():
            day = _v39_src_date(str(r.get(field) or "")[:10])
            if (lo and day < lo) or (hi and day > hi):
                raise RuntimeError(f"东财 {report} 请求 {field} 在 {lo or ''}~{hi or ''}，却返回了 {day}，结果不可信")
    return rows


_FORECAST_COLUMNS = ["code", "name", "notice_date", "report_date", "indicator", "forecast_type",
                     "amount_lower", "amount_upper", "change_pct_lower", "change_pct_upper",
                     "prior_year_amount", "content", "reason"]


@_v39_contract
def earnings_forecast(code=None, report_date=None, limit=500):
    """业绩预告（东财数据中心，沪深京全市场）。

    code 不给 = 全市场最新 limit 条（按公告日倒序）；report_date 为报告期，如 '2026-09-30'。
    一次预告会拆成多行：indicator 是预告指标（归母净利润 / 扣非净利润 / 营业收入…）。
    金额单位 元，change_pct 为同比变动 %。
    """
    limit = _v39_limit(limit)
    period = _v39_date(report_date) if report_date else None
    extra = f"(REPORT_DATE='{period}')" if period else ""
    filter_str = _em_event_filter(code, extra=extra)
    rows = _em_event_rows("RPT_PUBLIC_OP_NEWPREDICT", filter_str,
                          "NOTICE_DATE,SECURITY_CODE,REPORT_DATE,PREDICT_FINANCE_CODE", "-1,1,-1,1",
                          limit, narrowed=bool(code or report_date),
                          equal={} if code is None else {"SECURITY_CODE": norm_ticker(code, stock_only=True)},
                          dates={"REPORT_DATE": (period, period)} if period else None)
    out = [{"code": r["SECURITY_CODE"], "name": r.get("SECURITY_NAME_ABBR"),
            "notice_date": _em_day(r.get("NOTICE_DATE")), "report_date": _em_day(r.get("REPORT_DATE")),
            "indicator": r.get("PREDICT_FINANCE"), "forecast_type": r.get("PREDICT_TYPE"),
            "amount_lower": _v39_num(r.get("PREDICT_AMT_LOWER")),
            "amount_upper": _v39_num(r.get("PREDICT_AMT_UPPER")),
            "change_pct_lower": _v39_num(r.get("ADD_AMP_LOWER")),
            "change_pct_upper": _v39_num(r.get("ADD_AMP_UPPER")),
            "prior_year_amount": _v39_num(r.get("PREYEAR_SAME_PERIOD")),
            "content": r.get("PREDICT_CONTENT"), "reason": r.get("CHANGE_REASON_EXPLAIN")}
           for r in rows]
    return _v39_frame(out, "eastmoney", DATACENTER_URL + "?reportName=RPT_PUBLIC_OP_NEWPREDICT",
                      _FORECAST_COLUMNS)


_SURVEY_COLUMNS = ["code", "name", "notice_date", "survey_date", "survey_end", "org_count",
                   "survey_way", "place", "receptionist"]


@_v39_contract
def institution_survey(code=None, start=None, end=None, detail=False, limit=500):
    """机构调研（东财数据中心，汇总自上市公司投资者关系活动记录表）。

    detail=False：一次调研一行，org_count 为参与机构家数；
    detail=True：一家机构一行，多出 org_name / org_type / investigators（很多记录表不写机构类型和人名，为 None）。
    start / end 按公告日（notice_date）筛选；survey_date 是实际接待日，通常早于公告日几天。
    """
    limit = _v39_limit(limit)
    extra = '(IS_SOURCE="1")' + ("" if detail else '(NUMBERNEW="1")')
    filter_str = _em_event_filter(code, "NOTICE_DATE", start, end, extra)
    sort = (("NOTICE_DATE,SECURITY_CODE,RECEIVE_START_DATE,NUMBERNEW", "-1,1,-1,1") if detail
            else ("NOTICE_DATE,SECURITY_CODE,RECEIVE_START_DATE", "-1,1,-1"))
    equal = {"IS_SOURCE": "1"} if detail else {"IS_SOURCE": "1", "NUMBERNEW": "1"}
    if code is not None:
        equal["SECURITY_CODE"] = norm_ticker(code, stock_only=True)
    rows = _em_event_rows("RPT_ORG_SURVEYNEW", filter_str, sort[0], sort[1], limit,
                          narrowed=bool(code or start or end), equal=equal,
                          dates={"NOTICE_DATE": (start and _v39_date(start), end and _v39_date(end))}
                          if start or end else None)
    out = []
    for r in rows:
        row = {"code": r["SECURITY_CODE"], "name": r.get("SECURITY_NAME_ABBR"),
               "notice_date": _em_day(r.get("NOTICE_DATE")), "survey_date": _em_day(r.get("RECEIVE_START_DATE")),
               "survey_end": _em_day(r.get("RECEIVE_END_DATE")), "org_count": _v39_num(r.get("SUM")),
               "survey_way": r.get("RECEIVE_WAY_EXPLAIN"), "place": r.get("RECEIVE_PLACE"),
               "receptionist": r.get("RECEPTIONIST")}
        if detail:
            row.update({"org_name": r.get("RECEIVE_OBJECT"), "org_type": r.get("ORG_TYPE"),
                        "investigators": r.get("INVESTIGATORS")})
        out.append(row)
    columns = _SURVEY_COLUMNS + (["org_name", "org_type", "investigators"] if detail else [])
    return _v39_frame(out, "eastmoney", DATACENTER_URL + "?reportName=RPT_ORG_SURVEYNEW", columns)


_HOLDER_COLUMNS = ["code", "name", "holder", "direction", "change_shares_10k", "change_pct_total",
                   "change_pct_float", "after_shares_10k", "after_pct_total", "after_float_shares_10k",
                   "after_pct_float", "avg_price", "channel", "start_date", "end_date", "notice_date"]


@_v39_contract
def holder_trades(code=None, direction=None, start=None, end=None, limit=500):
    """股东增减持（东财数据中心，重要股东二级市场 / 大宗交易等变动公告）。

    direction: None / '增持' / '减持'。start / end 按公告日筛选。
    股数单位 万股；change_shares_10k 带符号（减持为负）；*_pct_total 占总股本 %，*_pct_float 占流通股 %。
    avg_price 为公告披露的成交均价，很多公告不披露，为 None。channel 为变动方式（二级市场 / 大宗交易 / 协议转让…）。
    """
    limit = _v39_limit(limit)
    if direction not in (None, "增持", "减持"):
        raise ValueError("direction 只能是 None / '增持' / '减持'")
    extra = f'(DIRECTION="{direction}")' if direction else ""
    filter_str = _em_event_filter(code, "NOTICE_DATE", start, end, extra)
    equal = {"DIRECTION": direction} if direction else {}
    if code is not None:
        equal["SECURITY_CODE"] = norm_ticker(code, stock_only=True)
    rows = _em_event_rows("RPT_SHARE_HOLDER_INCREASE", filter_str,
                          "NOTICE_DATE,SECURITY_CODE,HOLDER_NAME,START_DATE,END_DATE", "-1,1,1,1,1",
                          limit, narrowed=bool(code or start or end), equal=equal,
                          dates={"NOTICE_DATE": (start and _v39_date(start), end and _v39_date(end))}
                          if start or end else None)
    out = []
    for r in rows:
        signed = _v39_num(r.get("CHANGE_NUM_SYMBOL"))
        if signed is not None and r.get("DIRECTION") in ("增持", "减持") and (signed < 0) != (r["DIRECTION"] == "减持"):
            raise RuntimeError(f"东财增减持方向与变动股数符号不一致: {r['SECURITY_CODE']} {r['HOLDER_NAME']}")
        out.append({"code": r["SECURITY_CODE"], "name": r.get("SECURITY_NAME_ABBR"),
                    "holder": r.get("HOLDER_NAME"), "direction": r.get("DIRECTION"),
                    "change_shares_10k": signed,
                    # 东财字段名 AFTER_CHANGE_RATE 实为「本次变动占总股本比例」（与变动股数 / 总股本对得上）
                    "change_pct_total": _v39_num(r.get("AFTER_CHANGE_RATE")),
                    "change_pct_float": _v39_num(r.get("CHANGE_FREE_RATIO")),
                    "after_shares_10k": _v39_num(r.get("AFTER_HOLDER_NUM")),
                    "after_pct_total": _v39_num(r.get("HOLD_RATIO")),
                    "after_float_shares_10k": _v39_num(r.get("FREE_SHARES")),
                    "after_pct_float": _v39_num(r.get("FREE_SHARES_RATIO")),
                    "avg_price": _v39_num(r.get("TRADE_AVERAGE_PRICE")), "channel": r.get("MARKET"),
                    "start_date": _em_day(r.get("START_DATE")), "end_date": _em_day(r.get("END_DATE")),
                    "notice_date": _em_day(r.get("NOTICE_DATE"))})
    return _v39_frame(out, "eastmoney", DATACENTER_URL + "?reportName=RPT_SHARE_HOLDER_INCREASE",
                      _HOLDER_COLUMNS)


_BUYBACK_PROGRESS = {"001": "董事会预案", "002": "股东大会通过", "003": "股东大会否决",
                     "004": "实施中", "005": "停止实施", "006": "完成实施"}
_BUYBACK_COLUMNS = ["code", "name", "progress", "progress_code", "plan_start", "plan_end", "price_cap",
                    "shares_lower", "shares_upper", "amount_lower", "amount_upper",
                    "pct_total_lower", "pct_total_upper", "done_shares", "done_amount",
                    "done_price_low", "done_price_high", "latest_notice", "objective"]


@_v39_contract
def share_buyback(code=None, progress=None, limit=500):
    """股票回购（东财数据中心）— 回购方案与实施进度，一个方案一行、按最新公告日倒序。

    progress: None 或 '董事会预案' / '股东大会通过' / '股东大会否决' / '实施中' / '停止实施' / '完成实施'。
    股数单位 股，金额单位 元，pct_total_* 为占公告前一日总股本 %。done_* 为已回购部分（未开始实施为 None）。
    东财另有 007 / 008 两个进度码（2026-09-20 实测 5516 条里共 13 条），它自己的页面也不显示名称，
    这里 progress 为 None、progress_code 保留原码。
    """
    limit = _v39_limit(limit)
    codes = {v: k for k, v in _BUYBACK_PROGRESS.items()}
    if progress is not None and progress not in codes:
        raise ValueError("progress 只能是 " + " / ".join(codes))
    equal = {}
    if code is not None:
        equal["DIM_SCODE"] = norm_ticker(code, stock_only=True)     # 这张表的代码字段叫 DIM_SCODE
    if progress:
        equal["REPURPROGRESS"] = codes[progress]
    filter_str = "".join(f'({field}="{value}")' for field, value in equal.items())
    rows = _em_event_rows("RPTA_WEB_GETHGLIST_NEW", filter_str, "UPD,DIM_SCODE,REPURCODE", "-1,1,1",
                          limit, narrowed=bool(equal), equal=equal)
    out = []
    for r in rows:
        out.append({"code": r["DIM_SCODE"], "name": r.get("SECURITYSHORTNAME"),
                    "progress": _BUYBACK_PROGRESS.get(r.get("REPURPROGRESS")),
                    "progress_code": r.get("REPURPROGRESS"),
                    "plan_start": _em_day(r.get("REPURSTARTDATE")), "plan_end": _em_day(r.get("REPURENDDATE")),
                    "price_cap": _v39_num(r.get("REPURPRICECAP")),
                    "shares_lower": _v39_num(r.get("REPURNUMLOWER")), "shares_upper": _v39_num(r.get("REPURNUMCAP")),
                    "amount_lower": _v39_num(r.get("REPURAMOUNTLOWER")),
                    "amount_upper": _v39_num(r.get("REPURAMOUNTLIMIT")),
                    "pct_total_lower": _v39_num(r.get("ZSZXX")), "pct_total_upper": _v39_num(r.get("ZSZSX")),
                    "done_shares": _v39_num(r.get("REPURNUM")), "done_amount": _v39_num(r.get("REPURAMOUNT")),
                    "done_price_low": _v39_num(r.get("REPURPRICELOWER1")),
                    "done_price_high": _v39_num(r.get("REPURPRICECAP1")),
                    "latest_notice": _em_day(r.get("UPDATEDATE")), "objective": r.get("REPUROBJECTIVE")})
    return _v39_frame(out, "eastmoney", DATACENTER_URL + "?reportName=RPTA_WEB_GETHGLIST_NEW", _BUYBACK_COLUMNS)


_PLEDGE_COLUMNS = ["date", "code", "name", "industry", "pledge_ratio_pct", "pledged_shares_10k",
                   "pledged_mktcap_10k", "pledge_count", "unrestricted_pledged_10k", "restricted_pledged_10k"]


@_v39_contract
def equity_pledge(code=None, date=None, limit=5000):
    """股权质押比例（中国结算每周统计，经东财数据中心）。

    code 给了：该股历次统计（按日期倒序）；date 给了：该统计日全市场；都不给：最近一个统计日全市场；
    两个都给抛 ValueError（不会静默丢掉其中一个）。
    中国结算按周发布（通常为周五），date 不是统计日会得到 ValueError。
    pledge_ratio_pct 为质押股数占总股本 %；股数单位 万股，市值单位 万元。
    只覆盖沪深（2026-09-20 实测全市场 2212 条没有北交所），北交所代码直接抛 ValueError，不返回空表。
    """
    limit = _v39_limit(limit)
    if code is not None and date is not None:
        raise ValueError("code 与 date 只能给一个：code 取该股历次统计，date 取该统计日全市场")
    if code is not None and get_prefix(code) == "bj":
        raise ValueError(f"{code} 是北交所证券；中国结算质押统计只覆盖沪深，没有北交所数据")
    report = "RPT_CSDC_LIST"
    url = DATACENTER_URL + "?reportName=" + report
    if code is not None:
        rows = _em_event_rows(report, _em_event_filter(code), "TRADE_DATE", "-1", limit, narrowed=True,
                              equal={"SECURITY_CODE": norm_ticker(code, stock_only=True)})
    else:
        if date is None:
            latest = _em_event_rows(report, "", "TRADE_DATE", "-1", 1, narrowed=False)
            date = latest[0]["TRADE_DATE"]
        day = _v39_date(str(date)[:10])
        rows = _em_event_rows(report, f"(TRADE_DATE='{day}')", "PLEDGE_RATIO,SECURITY_CODE", "-1,1",
                              limit, narrowed=True, dates={"TRADE_DATE": (day, day)})
        if not rows:
            raise ValueError(f"{day} 不是中国结算质押统计日（按周发布，通常为周五）")
    out = []
    for r in rows:
        total = _v39_num(r.get("REPURCHASE_BALANCE"))
        free, locked = _v39_num(r.get("REPURCHASE_UNLIMITED_BALANCE")), _v39_num(r.get("REPURCHASE_LIMITED_BALANCE"))
        if None not in (total, free, locked) and abs(free + locked - total) > max(1.0, total * 0.001):
            raise RuntimeError(f"东财质押数据 无限售 + 限售 ≠ 合计: {r['SECURITY_CODE']} {r['TRADE_DATE']}")
        out.append({"date": _em_day(r.get("TRADE_DATE")), "code": r["SECURITY_CODE"],
                    "name": r.get("SECURITY_NAME_ABBR"), "industry": r.get("INDUSTRY"),
                    "pledge_ratio_pct": _v39_num(r.get("PLEDGE_RATIO")), "pledged_shares_10k": total,
                    "pledged_mktcap_10k": _v39_num(r.get("PLEDGE_MARKET_CAP")),
                    "pledge_count": _v39_num(r.get("PLEDGE_DEAL_NUM")),
                    "unrestricted_pledged_10k": free, "restricted_pledged_10k": locked})
    frame = _v39_frame(out, "eastmoney", url, _PLEDGE_COLUMNS)
    if frame.duplicated(["date", "code"]).any():
        raise RuntimeError("东财质押数据 日期+代码 重复")
    return frame


_IPO_COLUMNS = ["code", "name", "apply_code", "exchange", "board", "apply_date", "ballot_date", "pay_date",
                "listing_date", "issue_price", "issue_pe", "industry_pe", "issue_shares_10k",
                "online_shares", "apply_upper_shares", "top_apply_mktcap_10k", "win_rate_pct",
                "first_close", "first_close_chg_pct"]


@_v39_contract
def ipo_calendar(limit=100):
    """新股申购日历（东财数据中心，沪深京）— 按申购日倒序，包含尚未申购的排期。

    issue_price 在定价前为 None。issue_shares_10k 单位万股；online_shares / apply_upper_shares 单位股；
    top_apply_mktcap_10k 为顶格申购需配市值（万元）；win_rate_pct 为网上中签率 %；
    first_close_chg_pct 为上市首日收盘涨幅 %（未上市为 None）。
    """
    limit = _v39_limit(limit)
    rows = _em_event_rows("RPTA_APP_IPOAPPLY", "", "APPLY_DATE,SECURITY_CODE", "-1,-1", limit, narrowed=False)
    out = [{"code": r["SECURITY_CODE"], "name": r.get("SECURITY_NAME"), "apply_code": r.get("APPLY_CODE"),
            "exchange": r.get("TRADE_MARKET"),
            # MARKET 是「深交所主板 / 深交所创业板」这类准确板块；MARKET_TYPE_NEW 会把未上市的标成「深交所其他」，
            # 但北交所新股只有后者
            "board": r.get("MARKET") or r.get("MARKET_TYPE_NEW"),
            "apply_date": _em_day(r.get("APPLY_DATE")), "ballot_date": _em_day(r.get("BALLOT_NUM_DATE")),
            "pay_date": _em_day(r.get("BALLOT_PAY_DATE")), "listing_date": _em_day(r.get("LISTING_DATE")),
            "issue_price": _v39_num(r.get("ISSUE_PRICE")) or None,     # 定价前东财填 null 或 0
            "issue_pe": _v39_num(r.get("AFTER_ISSUE_PE")), "industry_pe": _v39_num(r.get("INDUSTRY_PE")),
            "issue_shares_10k": _v39_num(r.get("ISSUE_NUM")), "online_shares": _v39_num(r.get("ONLINE_ISSUE_NUM")),
            "apply_upper_shares": _v39_num(r.get("ONLINE_APPLY_UPPER")),
            "top_apply_mktcap_10k": _v39_num(r.get("TOP_APPLY_MARKETCAP")),
            "win_rate_pct": _v39_num(r.get("ONLINE_ISSUE_LWR")),
            "first_close": _v39_num(r.get("CLOSE_PRICE")),
            "first_close_chg_pct": _v39_num(r.get("LD_CLOSE_CHANGE"))}
           for r in rows]
    frame = _v39_frame(out, "eastmoney", DATACENTER_URL + "?reportName=RPTA_APP_IPOAPPLY", _IPO_COLUMNS)
    if frame.duplicated(["code"]).any():
        raise RuntimeError("东财新股日历代码重复")
    return frame
```
<!-- v39-events:end -->

```python
fc = earnings_forecast(report_date="2026-09-30")
sv = institution_survey("688062", detail=True)
cut = holder_trades(direction="减持", start="2026-09-01")
bb = share_buyback(progress="实施中")
pl = equity_pledge()                                 # 最近一个统计日全市场
ipo = ipo_calendar(limit=30)
```

---

## Layer 15: 可转债（V3.9.0 新增）

东财数据中心可转债全表：基本条款（评级、规模、转股起始日、到期日）+ 最新转股价 / 债价 / 正股价 / 转股价值 / 溢价率。
行情类字段由东财服务端按最新报价填入（盘中为实时价，停牌或未上市为 None）。
`status`：`upcoming` 已发行未上市 / `listed` 交易中 / `delisted` 已摘牌（`include_delisted=True` 才返回）/ `unknown` 判断不了（不猜）。
东财在赎回 / 到期公告后会提前填上摘牌日，摘牌日之前仍算 `listed`；上市日也可能提前填上，上市日之前算 `upcoming`（按北京时间判断）。
退市板块的转债（404001–404005，如 404005 普利退债）东财不填上市日和摘牌日，按交易市场 `STAS00` 判为 `delisted`。

### 15.1 自包含实现

<!-- v39-cb:start -->
```python
from datetime import datetime, timedelta, timezone

_CB_QUOTES = ("f2~01~CONVERT_STOCK_CODE~CONVERT_STOCK_PRICE,f235~10~SECURITY_CODE~TRANSFER_PRICE,"
              "f236~10~SECURITY_CODE~TRANSFER_VALUE,f2~10~SECURITY_CODE~CURRENT_BOND_PRICE,"
              "f237~10~SECURITY_CODE~TRANSFER_PREMIUM_RATIO")
_CB_COLUMNS = ["code", "name", "status", "stock_code", "stock_name", "rating", "issue_size_100m",
               "apply_date", "apply_code", "listing_date", "delist_date", "expire_date", "convert_start",
               "initial_convert_price", "convert_price", "bond_price", "stock_price", "convert_value",
               "premium_pct"]


@_v39_contract
def convertible_bonds(include_delisted=False):
    """可转债全表（东财数据中心）— 基本条款 + 最新转股价 / 债价 / 正股价 / 转股价值 / 溢价率。

    status: 'upcoming'（已发行未上市）/ 'listed'（交易中）/ 'delisted'（已摘牌，include_delisted=True 才返回）/
    'unknown'（交易市场不认识，或既没有上市日也没有申购日，不猜）。
    退市板块的转债（代码 404xxx、TRADE_MARKET=STAS00，如 404005 普利退债）东财不填上市日和摘牌日，按 delisted 处理。
    行情类字段由东财服务端按最新报价填入：盘中为实时价，停牌或未上市为 None。
    转股价值 = 100 / 转股价 × 正股价；premium_pct = 债价 / 转股价值 − 1（%）。issue_size_100m 单位亿元。
    """
    rows = _em_datacenter_strict("RPT_BOND_CB_LIST", "", "PUBLIC_START_DATE,SECURITY_CODE", "-1,1",
                                 page_size=500, max_rows=20000,
                                 extra={"quoteColumns": _CB_QUOTES, "quoteType": "0"})
    if not rows:
        raise RuntimeError("东财可转债列表为空，接口可能改了")
    today = datetime.now(timezone(timedelta(hours=8))).date().isoformat()   # 按北京时间，不看本机时区
    out = []
    for r in rows:
        listing, delist = _em_day(r.get("LISTING_DATE")), _em_day(r.get("DELIST_DATE"))
        market = r.get("TRADE_MARKET")
        # 东财在发布赎回/到期公告后就会填上未来的摘牌日，摘牌日之前仍在交易；
        # 上市日同理可能提前填上，上市日之前算 upcoming
        if (delist and delist <= today) or market == "STAS00":     # STAS00 = 退市板块，已从沪深摘牌
            status = "delisted"
        elif market not in ("CNSESH", "CNSESZ"):
            status = "unknown"
        elif listing and listing <= today:
            status = "listed"
        elif listing or r.get("PUBLIC_START_DATE"):
            status = "upcoming"
        else:
            status = "unknown"
        if status == "delisted" and not include_delisted:
            continue
        out.append({"code": r["SECURITY_CODE"], "name": r.get("SECURITY_NAME_ABBR"), "status": status,
                    "stock_code": r.get("CONVERT_STOCK_CODE"), "stock_name": r.get("SECURITY_SHORT_NAME"),
                    "rating": r.get("RATING"), "issue_size_100m": _v39_num(r.get("ACTUAL_ISSUE_SCALE")),
                    "apply_date": _em_day(r.get("PUBLIC_START_DATE")), "apply_code": r.get("CORRECODE"),
                    "listing_date": listing, "delist_date": delist, "expire_date": _em_day(r.get("EXPIRE_DATE")),
                    "convert_start": _em_day(r.get("TRANSFER_START_DATE")),
                    "initial_convert_price": _v39_num(r.get("INITIAL_TRANSFER_PRICE")),
                    "convert_price": _v39_num(r.get("TRANSFER_PRICE")),
                    "bond_price": _v39_num(r.get("CURRENT_BOND_PRICE")),
                    "stock_price": _v39_num(r.get("CONVERT_STOCK_PRICE")),
                    "convert_value": _v39_num(r.get("TRANSFER_VALUE")),
                    "premium_pct": _v39_num(r.get("TRANSFER_PREMIUM_RATIO"))})
    frame = _v39_frame(out, "eastmoney", DATACENTER_URL + "?reportName=RPT_BOND_CB_LIST", _CB_COLUMNS)
    if frame.duplicated(["code"]).any():
        raise RuntimeError("东财可转债列表代码重复")
    return frame
```
<!-- v39-cb:end -->

```python
cb = convertible_bonds()
cheap = cb[(cb.status == "listed") & (cb.premium_pct < 10)].sort_values("premium_pct")
print(len(cb), cheap[["code", "name", "bond_price", "convert_value", "premium_pct"]].head())
```

---

## 估值计算公式

### 前向PE

```python
def forward_pe(price: float, eps_forecast: float) -> float:
    """前向PE = 当前股价 / 未来年度一致预期EPS"""
    if eps_forecast <= 0:
        return float("inf")
    return price / eps_forecast
```

### PE消化时间

```python
import math

def pe_digestion(current_pe: float, cagr: float, target_pe: float = 30) -> float:
    """
    当前PE消化到目标PE需要多少年。
    target_pe 固定30x（A股成长股合理估值锚点）。
    cagr: 用 下一年EPS / 当年EPS - 1
    """
    if current_pe <= target_pe:
        return 0.0
    if cagr <= 0:
        return float("inf")
    return math.log(current_pe / target_pe) / math.log(1 + cagr)
```

### PEG

```python
def calc_peg(pe: float, cagr: float) -> float:
    """
    PEG = 前向PE / (CAGR * 100)
    PEG < 1   → 便宜
    PEG 1-1.5 → 合理
    PEG > 1.5 → 贵
    """
    if cagr <= 0:
        return float("inf")
    return pe / (cagr * 100)
```

### 投资框架速查

```
壁垒 → 增速 → PE消化 → PEG校验

1. 有壁垒吗？(tech_moat / capacity_moat) → 没有则排除
2. 增速多少？(CAGR > 30% 才有意义)
3. PE多久消化到30x？(< 2年合理, > 4年太贵)
4. PEG多少？(< 1 便宜, 1-1.5 合理, > 1.5 贵)

30x PE 锚点: A股成长股的合理估值重力线，所有行业统一用30x。
期权定价例外: PEG > 3 但壁垒极深时，本质是看涨期权，不适用PEG框架。
```

---

## 完整调研流程

### 流程 A: 单票完整估值（30秒）

当年 EPS 为正时，`digest_years` 在 PE 已达到或低于 30x 时为 `0`；PE 高于 30x 且预期增长为正时返回消化年数。
若当年 EPS 缺失或非正，或 PE 高于 30x 但下一年预测缺失、盈利不增长，无法得出有限消化时间，返回 `None`（JSON 中为 `null`）。

```python
import requests
import urllib.request
import math
import pandas as pd

def full_valuation(code: str) -> dict:
    """单票完整估值分析"""
    # 1. 腾讯实时行情
    # 92 必须先判：北交所 2024-10 起启用 920xxx 号段，裸 startswith("9") 会误判成沪市，
    # 腾讯对 sh920xxx 返回空载荷（静默失败）。900xxx 沪市 B 股仍走 sh。
    prefix = ("bj" if code.startswith(("92", "8"))
              else "sh" if code.startswith(("6", "9")) else "sz")
    url = f"https://qt.gtimg.cn/q={prefix}{code}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    resp = urllib.request.urlopen(req, timeout=10)
    data = resp.read().decode("gbk")
    vals = data.split('"')[1].split("~")
    price = float(vals[3])
    mcap = float(vals[45])   # 45=总市值（44 是流通市值，见「腾讯行情字段」踩坑提醒二）
    pe_ttm = float(vals[39]) if vals[39] else 0
    pb = float(vals[46]) if vals[46] else 0

    # 2. 机构一致预期（直连同花顺）
    df = ths_eps_forecast(code)
    eps_cur = eps_next = None
    analyst_count = 0
    if not df.empty and len(df.columns) >= 3:
        # 按列名取「均值」=机构一致预期EPS（见 ths_eps_forecast 文档）。
        # 不按 iloc 位置取——同花顺表格列序会变；且旧版误用 iloc[2]＝「最小值」
        # 当成一致预期，导致 pe_forward/PEG 系统性偏差，此处一并修正。
        def _pick(row, name):
            for c in df.columns:
                if name in str(c):
                    return row.get(c)
            return None
        try:
            r0 = df.iloc[0]
            v = _pick(r0, "均值");          eps_cur = float(v) if pd.notna(v) else None
            cnt = _pick(r0, "预测机构数");  analyst_count = int(cnt) if pd.notna(cnt) else 0
            if len(df) >= 2:
                vn = _pick(df.iloc[1], "均值"); eps_next = float(vn) if pd.notna(vn) else None
        except (ValueError, TypeError) as e:
            print(f"[WARN] full_valuation EPS 解析失败({e})，估值可能不完整")

    # 3. 估值指标
    pe_fwd = price / eps_cur if eps_cur else float("inf")
    cagr = (eps_next / eps_cur - 1) if (eps_cur and eps_next) else 0
    peg = pe_fwd / (cagr * 100) if cagr > 0 else float("inf")
    digest = (
        pe_digestion(pe_fwd, cagr)
        if eps_cur is not None and eps_cur > 0 else float("inf")
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
        "digest_years": round(digest, 1) if math.isfinite(digest) else None,
        "analyst_count": analyst_count,
    }

# 用法
result = full_valuation("688017")
print(result)
```

### 流程 B: 批量估值对比

```python
stocks = ["688017", "300308", "300476", "002463"]
for code in stocks:
    try:
        r = full_valuation(code)
        print(f"{r['name']}({code}): PE_fwd={r['pe_fwd']}x PEG={r['peg']} 消化={r['digest_years']}年 覆盖={r['analyst_count']}家")
    except Exception as e:
        print(f"{code}: 失败 - {e}")
```

### 流程 C: 主题研报批量检索

```python
# Step 1: iwencai 多 query 语义搜索
queries = [
    "人形机器人产业链深度 2026",
    "人形机器人减速器 丝杠",
    "特斯拉Optimus 国产供应链",
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

### 流程 D: 新标的快速调研（V3.0 增强版）

```python
code = "688017"

# 1. 有无机构覆盖？
forecast = ths_eps_forecast(code)
print(f"机构覆盖: {'有' if not forecast.empty else '无'}")

# 2. 实时估值
quotes = tencent_quote([code])
q = quotes[code]
print(f"PE={q['pe_ttm']} PB={q['pb']} 市值={q['mcap_yi']}亿")

# 3. PE消化 → 用 full_valuation()
# 4. PEG校验

# 5. 概念板块归属
blocks = eastmoney_concept_blocks(code)
print(f"板块: {', '.join(blocks['concept_tags'][:10])}")

# 6. 资金流向（分钟级，当日盘中）
flow = eastmoney_fund_flow_minute(code)
if flow:
    total = sum(f["main_net"] for f in flow)
    print(f"当日主力累计净流入: {total/1e4:.0f}万")

# 7. 资金流向（东财120日）
flow_120 = stock_fund_flow_120d(code)
if flow_120:
    total = sum(d["main_net"] for d in flow_120[-20:])
    print(f"近20日主力累计净流入: {total/1e8:.2f}亿")

# 8. 龙虎榜
dtb = dragon_tiger_board(code, "2026-05-17")
print(f"近30日上龙虎榜: {len(dtb['records'])} 次")

# 9. 解禁预警
lockup = lockup_expiry(code, "2026-05-17")
print(f"未来90天待解禁: {len(lockup['upcoming'])} 批")

# 10. 融资融券
margin = margin_trading(code, page_size=5)
if margin:
    print(f"最新融资余额: {margin[0]['rzye']/1e8:.2f}亿")

# 11. 股东户数
holders = holder_num_change(code)
if holders:
    print(f"最新股东数: {holders[0]['holder_num']} 环比{holders[0]['change_ratio']}%")
```

---

## 官方两融与北交所行情备胎（V3.8.0）

先执行 Layer 12 的完整自包含代码块，再执行下列代码块。新增两个**能力入口**，按入口计数，
不将同一函数的交易所路由重复算成端点。使用 `margin_trading_backup("2026-09-03", "SH")`
或 `"SZ"` 分别取数，`code="600519"` 可在完整快照中筛选个股；未指定代码时包含源侧融资融券标的（也含 ETF）。
两所发布进度可能不同，不能将单所结果标成沪深全市场。源未发布该日数据时抛错，完整列表中
个股未命中则返回有列定义的空表。

**单位及字段：** `margin_balance` / `margin_buy` / `short_balance` 为元；
`short_volume` / `short_sell_volume` 为股或份。上交所 `short_balance` 源值为空时保留为空，
不以余量乘价格冒充官方金额。该备胎并非东财所有字段的等价替代，深交所不含两种偿还字段。

`bse_quote_backup("2026-09-04", code="920021")` 只接受沪深北中的 **北交所纯 6 位代码**；
省略 `code` 拉全板。首参是调用方期望的交易日，必须与源侧每行日期一致，返回五档盘快照
（价格元、量股）、OHLC、成交量额、`pe_source`（官网字段口径未细分，不称 PE-TTM）。
**这是当前快照，没有历史回填，也未验证盘中更新延迟；不是逐笔 Level-2。**

<!-- official-data-backups:start -->
```python
import json
import time


def _official_total(value):
    if not re.fullmatch(r"[0-9]+", str(value)):
        raise RuntimeError("官方分页总数必须为非负整数")
    return int(value)


def _official_margin_code(value, exchange):
    code = _official_code(value)
    prefixes = ("5", "6", "900") if exchange == "SH" else ("0", "1", "2", "3")
    if not code.startswith(prefixes):
        raise ValueError("两融证券代码与请求的交易所不符")
    return code


def margin_trading_backup(trade_date, exchange, code=None):
    """一次只取一个交易所。未发布抛错；完整源中筛不到 code 才返回空表。"""
    trade_date = _official_date(trade_date)
    exchange = str(exchange).upper()
    if exchange not in ("SH", "SZ"):
        raise ValueError("exchange 必须为 SH 或 SZ；本函数不覆盖北交所两融")
    if code is not None:
        code = _official_margin_code(code, exchange)
    if exchange == "SH":
        url = "https://query.sse.com.cn/marketdata/tradedata/queryMargin.do"
        response = _official_get(url, {
            "isPagination": "true", "tabType": "mxtype", "detailsDate": trade_date.replace("-", ""),
            "pageHelp.pageSize": 5000, "pageHelp.pageNo": 1, "pageHelp.beginPage": 1,
            "pageHelp.cacheSize": 1, "pageHelp.endPage": 1,
        }, "https://www.sse.com.cn/")
        page = response.json().get("pageHelp") or {}
        data = page.get("data")
        if not isinstance(data, list) or not data or len(data) != _official_total(page.get("total")):
            raise RuntimeError("上交所该日数据未发布或分页不完整")
        fields = {"rzye": "margin_balance", "rzmre": "margin_buy", "rqylje": "short_balance",
                  "rqyl": "short_volume", "rqmcl": "short_sell_volume"}
        rows = []
        for rec in data:
            if _official_date(rec.get("opDate")) != trade_date:
                raise RuntimeError("上交所两融数据日期不符")
            if not set(fields).issubset(rec):
                raise RuntimeError("上交所两融字段发生变化")
            rows.append({"date": trade_date, "code": _official_margin_code(rec["stockCode"], exchange),
                         "name": rec.get("securityAbbr"), "exchange": exchange,
                         **{dest: _official_number(rec[src], required=(src != "rqylje"))
                            for src, dest in fields.items()}})
    else:
        url = "https://www.szse.cn/api/report/ShowReport"
        response = _official_get(url, {"SHOWTYPE": "xlsx", "CATALOGID": "1837_xxpl",
                                      "TABKEY": "tab2", "txtDate": trade_date}, "https://www.szse.cn/")
        data = _official_excel(response)
        fields = {"融资余额(元)": "margin_balance", "融资买入额(元)": "margin_buy",
                  "融券余额(元)": "short_balance", "融券余量(股/份)": "short_volume",
                  "融券卖出量(股/份)": "short_sell_volume"}
        _official_columns(data, ["证券代码", "证券简称", *fields])
        rows = [{"date": trade_date, "code": _official_margin_code(str(rec["证券代码"]).zfill(6), exchange),
                 "name": rec["证券简称"], "exchange": exchange,
                 **{dest: _official_number(rec[src], required=True) for src, dest in fields.items()}}
                for rec in data.to_dict("records")]
    frame = _official_frame(rows, ["date", "code"], "sse" if exchange == "SH" else "szse", response.url)
    return frame if code is None else frame.loc[frame.code == code].reset_index(drop=True)


def bse_quote_backup(trade_date, code=None):
    """北交所当前全板/单票快照；拒绝用当前数据回填其他交易日。"""
    trade_date = _official_date(trade_date)
    if code is not None:
        code = _official_code(code)
        if not code.startswith(("4", "8", "92")):
            raise ValueError("请输入北交所代码（4/8/92 开头）")
    page_url = "https://www.bse.cn/nq/quotation.html"
    url = "https://www.bse.cn/nqhqController/nqhq_en.do"
    raw_rows = []
    total = None
    with requests.Session() as session:
        session.headers.update({"User-Agent": "Mozilla/5.0", "Referer": page_url,
                                "Accept": "application/json, text/javascript, */*; q=0.01"})
        # 官网有时设置匿名 Cookie 后 302 回自己；不跟随重定向，避免循环。
        session.get(page_url, timeout=(10, 40), allow_redirects=False).raise_for_status()
        for page_number in range(100):
            form = {"page": page_number, "type_en": '["B"]', "sortfield": "hqzqdm",
                    "sorttype": "asc", "xxfcbj_en": "[2]", "zqdm": code or ""}
            response = session.post(url, data=form, timeout=(10, 40), allow_redirects=False)
            if 300 <= response.status_code < 400:
                session.get(page_url, timeout=(10, 40), allow_redirects=False).raise_for_status()
                response = session.post(url, data=form, timeout=(10, 40), allow_redirects=False)
            response.raise_for_status()
            if response.status_code != 200:
                raise RuntimeError("北交所匿名会话尚未建立")
            payload = response.text.strip()
            match = re.fullmatch(r"[A-Za-z_$][\w$]*\((.*)\);?", payload, re.S)
            data = json.loads(match.group(1) if match else payload)
            if not isinstance(data, list) or len(data) != 1 or not isinstance(data[0].get("content"), list):
                raise RuntimeError("北交所行情响应结构异常")
            current_total = _official_total(data[0].get("totalElements"))
            if total is not None and total != current_total:
                raise RuntimeError("分页期间北交所记录总数变化，请重试")
            total = current_total
            batch = data[0]["content"]
            if total < 0 or not batch:
                raise RuntimeError("北交所未返回目标行情或分页提前结束")
            raw_rows.extend(batch)
            if len(raw_rows) >= total:
                break
            time.sleep(0.2)
        if len(raw_rows) != total:
            raise RuntimeError("北交所分页不完整，不能标记全板成功")
    fields = {"hqjrkp": "open", "hqzgcj": "high", "hqzdcj": "low", "hqzjcj": "close",
              "hqzrsp": "previous_close", "hqcjsl": "volume", "hqcjje": "amount"}
    rows = []
    for rec in raw_rows:
        if _official_date(rec.get("hqjsrq")) != trade_date:
            raise RuntimeError("北交所快照不是请求的交易日；本接口不提供历史回填")
        ticker = _official_code(rec.get("hqzqdm"))
        if not ticker.startswith(("4", "8", "92")) or (code is not None and ticker != code):
            raise RuntimeError("北交所返回了请求范围之外的标的")
        row = {"date": trade_date, "code": ticker, "name": rec.get("hqzqjc"), "exchange": "BJ",
               "quote_time": str(rec.get("hqgxsj", "")), "pe_source": _official_number(rec.get("hqsyl1")),
               **{dest: _official_number(rec.get(src), required=True) for src, dest in fields.items()}}
        for level in range(1, 6):
            for src, dest in (("hqbjw", "bid_price"), ("hqbsl", "bid_volume"),
                              ("hqsjw", "ask_price"), ("hqssl", "ask_volume")):
                row[f"{dest}_{level}"] = _official_number(rec.get(f"{src}{level}"), required=True)
        rows.append(row)
    return _official_frame(rows, ["date", "code"], "bse", url)
```
<!-- official-data-backups:end -->

```python
sh_margin = margin_trading_backup("2026-09-03", "SH", code="600519")
sz_margin = margin_trading_backup("2026-09-03", "SZ", code="000001")
bj_quote = bse_quote_backup("2026-09-04", code="920021")
```

端点与字段交叉参考 [CNEquity 两融适配](https://github.com/rootSunc/CNEquity/blob/main/src/cnequity/adapters/exchange/margin_trading.py)
及 [北交所适配](https://github.com/rootSunc/CNEquity/blob/main/src/cnequity/adapters/bse/daily_quotes.py)。
本版只参考官方端点与字段契约，数据直接来自交易所。

## 数据源优先级

| 优先级 | 数据源 | 用途 | 可靠性 | 封IP风险 |
|--------|--------|------|--------|---------|
| 1 | **腾讯财经** (HTTP) | 实时PE/PB/市值/换手率/涨跌停/指数/ETF + 日周月/分钟 K 线（§1.2）+ 当日逐笔（§1.4） | 稳定 | 低（K 线单入口约 600 次后限流，已三入口轮换） |
| 2 | **mootdx** (TCP) | 财务快照+F10；K线/五档/逐笔 2026-09 起返回空（#52） | 财务/F10 稳定，行情命令失效 | 极低 |
| 3 | **东财 datacenter** (HTTP) | 龙虎榜/解禁/融资融券/大宗交易/股东户数/分红/个股信息 | 稳定 | 低 |
| 4 | **东财 push2/push2his** (HTTP) | 行业板块/个股资金流分钟级+120日 | 稳定 | 低 |
| 5 | **iwencai** (OpenAPI) | NL主题搜索研报(唯一能力) | 需X-Claw Header | 低 |
| 6 | **东财 reportapi/PDF** (HTTP) | 完整研报图表、评级 | 稳定 | 低 |
| 7 | **同花顺热点** (HTTP) | 当日强势股+题材归因 reason tags | 稳定 73ms | 极低（零鉴权） |
| 8 | **同花顺 hsgtApi** (HTTP) | 北向资金分钟级+自缓存历史 | 稳定 | 极低（零鉴权） |
| 9 | **百度股市通** (HTTP) | 概念板块+K线带MA | 稳定 | 极低（零鉴权） |
| 10 | **新浪财经** (HTTP) | 资产负债表/利润表/现金流量表 | 稳定 | 低 |
| 11 | **同花顺 basic** (HTTP) | 一致预期EPS | 稳定(需UA) | 低 |
| 12 | **财联社** (HTTP) | 全市场实时电报 | 稳定 | 低 |
| 13 | **巨潮 cninfo** (HTTP) | 公告全文检索+下载 | 稳定 | 低 |
| 14 | **上交所官方** (HTTP，备胎) | 龙虎榜全文/实时五档/两融明细 | 一手官方源，两融须核对日期与完整性 | 零鉴权，避免高频请求 |
| 15 | **深交所官方** (HTTP) | 龙虎榜/公告+PDF/实时五档/两融明细/交易日历 | 一手官方源，日历须完整、两融须已发布 | 零鉴权，避免高频请求 |
| 16 | **baostock** (TCP，V3.7) | 估值历史PE/PB/PS/PCF+换手率+停牌+ST+上市退市日 | 稳定（免注册） | 极低；**不支持北交所** |
| 17 | **申万研究** (HTTP，V3.7) | 行业分类变迁史（公开 XLS） | 稳定 | 极低（公开文件） |
| 18 | **人民银行** (HTTP，V3.7) | 社会融资规模增量（月度，2021 年起） | 稳定（官方站） | 极低 |
| 19 | **国家统计局** (HTTP，V3.7) | PMI 制造业/非制造业/综合+大中小型 | 稳定（官方站） | 极低 |
| 20 | **中证指数** (HTTP，V3.8) | 指数成分/权重/两种口径 PE 与股息率 | 官方文件，2026-09-05 验证 | 零鉴权，避免高频重复下载 |
| 21 | **国证指数** (HTTP，V3.8) | 最近公布的指数成分/权重 | 官方月末文件，2026-09-05 验证 | 零鉴权，避免高频重复下载 |
| 22 | **北交所官方** (HTTP，V3.8，备胎) | 当前行情/五档/成交量额 | 当前快照，须核对日期 | 匿名 Cookie 会话，分页限速 |
| 23 | **通达信官网盘后包** (HTTP，V3.9) | 某交易日沪深北全市场日线（含成交额） | 官方文件，2026-09-20 抽查 2022-01-04、2023-01-03 可取（2021-01-04 已没有），未逐日验证 | 极低（单个 zip 约 2~3 MB） |
| 24 | **华尔街见闻** (HTTP，V3.9) | 7×24 快讯 + 全球宏观日历 | 稳定 | 低 |
| 25 | **央视网** (HTTP，V3.9) | 新闻联播条目 + 文字稿 | 稳定，当天节目约 20:00 后才有 | 极低 |
| 26 | **上证e互动** (HTTP，V3.9) | 沪市投资者问答 | 官方源 | 零鉴权，避免高频请求 |
| 27 | **中债（中央结算公司）** (HTTP，V3.9) | 国债 / 银行 AAA / 中短票 AAA 收益率曲线 | 官方源，单次区间 ≤ 1 年 | 极低 |
| 28 | **中国货币网（外汇交易中心）** (HTTP，V3.9) | 回购定盘利率 FR / FDR | 官方源，FR 约近 3 年、FDR 约近 1 年 | 极低 |
| 29 | **上期所** (HTTP，V3.9) | 期货 / 期权日行情 + 会员持仓排名 | 官方源 | 零鉴权，避免高频请求 |
| 30 | **上期能源** (HTTP，V3.9) | 原油 / 国际铜等期货期权日行情 + 持仓排名 | 官方源（与上期所同格式） | 零鉴权，避免高频请求 |
| 31 | **郑商所** (HTTP，V3.9) | 期货 / 期权日行情 + 持仓排名 | 官方源 | 零鉴权，避免高频请求 |
| 32 | **中金所** (HTTP，V3.9) | 股指 / 国债期货 + 股指期权日行情 + 持仓排名 | 官方源 | 零鉴权，避免高频请求 |
| 33 | **广期所** (HTTP，V3.9) | 工业硅 / 碳酸锂等期货期权日行情 | 官方源 | 零鉴权，避免高频请求 |
| 34 | **上金所** (HTTP，V3.9) | 黄金 / 白银 / 铂金现货日线 | 官方源 | 零鉴权，避免高频请求 |

> V3.9 复用的已有来源不重复计数：腾讯（§1.2 K 线）、新浪（§2.4 研报、§13.4 实时期货、§13.5 A50）、
> 东财（§6.8 ST 名单、§11.5 LPR、Layer 14 事件驱动、Layer 15 可转债）、上交所 / 深交所（§4.7 ETF 份额）。
> 上证e互动虽由上交所运营，但域名和接口独立，单列为第 26 个来源。
> V3.10 的 §1.4 腾讯逐笔、§13.7 新浪期货日 K 同样复用已有来源，来源数不变。
> 大商所官网有反爬，未接入；大商所品种的逐日 K 线用 §13.7、实时价用 §13.4（均为新浪）。

**原则：** 行情走腾讯（§1.2 K 线、§1.4 逐笔）+ 通达信官网盘后包，mootdx 只用于财务 / F10（#52）；研报走东财+iwencai，新浪作第二来源；资金面走东财 datacenter+push2，**信号层走同花顺+百度+东财直连接口**；期货、利率、黄金走交易所与官方机构。除 mootdx / baostock 两个 TCP 客户端外全部直连 HTTP。

**降级：** 任一主源被封/失效时，先查下方「备用源速查 & 降级策略」——每类数据都备有一条**不同域名、不同风控面**的独立备胎（交易所官方/新浪/同花顺），东财被封时它们不受牵连。

---

## 备用源速查 & 降级策略（东财/主源被封时用）

**何时用：** 主源报错 403/连接重置（东财 IP 级风控）、返回空、或需权威一手数据交叉验证时。**东财系接口共用同一风控面，某台住宅 IP 被封会成片失联**——下表列出部分核心数据的备胎（不同域名、不同风控面；打板/期权/舆情/事件驱动/可转债暂无独立备胎）。既有备胎的验证记录为 2026-07-11；两融与北交所备胎在 2026-09-05 跑通真实数据；V3.9 的研报备胎与改过主源的 K 线行在 2026-09-20 实测。历史验证不代表今天全部接口仍然可用。

| 数据类型 | 主源(本 skill) | 独立备胎 | 备胎端点 / 说明 |
|---|---|---|---|
| 实时行情+五档 | 腾讯（mootdx 盘口 #52 失效） | 交易所官方 | 沪 `yunhq.sse.com.cn:32041/v1/sh1/snap/{code}`、深 `szse.cn/api/market/ssjjhq/getTimeData?marketId=1&code={code}`；北 `bse_quote_backup(date, code)` 是当前快照，盘中延迟未标定 |
| 融资融券 | 东财 datacenter | 上交所/深交所官方 | `margin_trading_backup(date, "SH"/"SZ", code=None)`，按交易所分别取；上交所融券余额金额可能为空 |
| K线(全历史) | 腾讯 §1.2 / 百度 | 同花顺 | `d.10jqka.com.cn/v6/line/hs_{code}/01/last.js`（01日/11周/21月/30/60分；2001至今；JSONP剥壳） |
| K线(当日全市场) | 通达信盘后包 §1.3 | 腾讯 §1.2 逐只取 | 盘后包实测 2022-01-04、2023-01-03 可取（2021-01-04 已 404），取不到的日期逐只走 §1.2 |
| K线(分钟) | 腾讯 §1.2（m1~m60，≤320根） | 同花顺 | 同上一行，只有 30 / 60 分钟；1 / 5 / 15 分钟在 mootdx 恢复前暂无独立备胎 |
| 逐笔成交 | 腾讯 §1.4（只有当日；mootdx 逐笔 #52 失效） | 暂无 | 新浪 `CN_Bill.GetBillList` 只返回大单，不是全部成交，不能当备胎 |
| 研报列表 | 东财 reportapi | 新浪 §2.4 | `sina_research_reports()`：只有标题/类型/机构/研究员/日期，无评级与目标价 |
| 龙虎榜 | 东财 datacenter | 沪深交易所官方 | `dragon_tiger_backup()`（见下，含营业部席位） |
| 个股资金流 | 东财 push2 | 新浪 | `fund_flow_backup()`（见下，日度四档单净额） |
| 公告 | 巨潮 | 深交所官方/东财 | `announcements_backup()`（见下，深市深交所+PDF，沪市东财+PDF） |
| 财务三表 | 新浪/mootdx | 同花顺 F10 | `basic.10jqka.com.cn/api/stock/finance/{code}_debt.json`（`_benefit`利润/`_cash`现金流；仅 UA，5连发不封） |
| 个股新闻 | 东财 search | 新浪7x24 | `zhibo.sina.com.cn/api/zhibo/feed?zhibo_id=152&page_size=20&dire=f`（`ext.stocks` 带个股关联可过滤） |
| 快讯 | 东财7x24(§5.3) | 财联社(§5.2) | 两条已互备；再加金十 `jin10.com/flash_newest.js` |
| 券商评级+目标价 | 同花顺一致预期 | 巨潮 webapi | `p_sysapi1089?tdate=YYYY-MM-DD`，需头 `Accept-Enckey`=base64(AES-128-CBC(unix秒, key=iv=`1234567887654321`)) |
| 北向(权威) | 同花顺 hexin | HKEX 官方 | `hkex.com.hk/chi/csm/DailyStat/data_tab_daily_{YYYYMMDD}c.js`（成交额/额度/十大活跃股） |

> ⛔ **已死透别用**（2026-07 实测）：网易财经(126.net 整站下线)、和讯、凤凰行情、腾讯资金流(ff_ 已死)、雪球免登录深度数据(需 token)。mootdx **库**已烂尾(2024 停更)；**2026-09 起通达信公开服务器的 K 线 / 盘口 / 逐笔命令返回空（#52）**，财务与 F10 照常——行情改走 §1.1–§1.4（腾讯实时 / 腾讯 K 线 / 盘后包 / 腾讯逐笔），财务用 `tdx_client(check='finance')`。
>
> ⚠️ **腾讯分钟 K 线字段坑**（§1.2 `tencent_kline()` 已按此解析，不返回成交额）：返回数组 `[时间, 开, 收, 高, 低, 量, {}, 换手率基点]`，量的单位科创板是股、其余是手（见 §1.2）——第 8 个字段（下标 7）**不是成交额，是换手率基点**（当日各根累加 ÷100 = 当日换手率%）。当成交额读会小三个数量级；成交额需自算 `成交数量 × 均价`（成交数量：科创板就是量（股）；可转债是量 × 10（张）；沪深主板、创业板、B 股、ETF、LOF、REITs 是量 × 100；指数不适用）。

```python
import json, urllib.request, ssl
_ctx = ssl.create_default_context(); _ctx.check_hostname = False; _ctx.verify_mode = ssl.CERT_NONE

def dragon_tiger_backup(trade_date: str) -> dict:
    """龙虎榜官方备用源（东财被封时用）：上交所+深交所官方，零鉴权权威一手，含营业部席位。"""
    out = {"date": trade_date, "sse_raw": "", "szse": []}
    su = (f"https://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON"
          f"&CATALOGID=1842_xxpl&TABKEY=tab1&txtStart={trade_date}&txtEnd={trade_date}&random=0.9")
    req = urllib.request.Request(su, headers={"User-Agent": UA,
          "Referer": "https://www.szse.cn/disclosure/supervision/dealinfo/index.html"})
    with urllib.request.urlopen(req, timeout=15, context=_ctx) as r:
        d = json.loads(r.read())
    for row in d[0].get("data", []):
        out["szse"].append({"code": row.get("zqdm"), "name": row.get("zqjc"),
                            "amount": row.get("cjje"), "reason": row.get("plyy")})
    eu = (f"https://query.sse.com.cn/infodisplay/showTradePublicFile.do?"
          f"jsonCallBack=cb&isPagination=false&dateTx={trade_date}")
    req = urllib.request.Request(eu, headers={"User-Agent": UA,
          "Referer": "https://www.sse.com.cn/disclosure/diclosure/public/"})
    with urllib.request.urlopen(req, timeout=15) as r:
        t = r.read().decode("utf-8", "ignore")
    out["sse_raw"] = "\n".join(json.loads(t[t.index("(")+1:t.rindex(")")]).get("fileContents", []))
    return out

def fund_flow_backup(code: str, days: int = 60) -> list:
    """个股资金流备用源（东财被封时用）：新浪，日度四档单净额。"""
    # 92 先判：920xxx 是北交所，误判成 sh/sz 时新浪返回空数组（实测 bj920002 有数据、sh/sz 为 []）
    pre = ("bj" if code.startswith(("92", "8"))
           else "sh" if code.startswith(("6", "9")) else "sz") + code
    u = (f"https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
         f"MoneyFlow.ssl_qsfx_zjlrqs?page=1&num={days}&sort=opendate&asc=0&daima={pre}")
    req = urllib.request.Request(u, headers={"User-Agent": UA, "Referer": "https://finance.sina.com.cn/"})
    with urllib.request.urlopen(req, timeout=15) as r:
        t = r.read().decode("utf-8", "ignore")
    arr = json.loads(t[t.index("["):t.rindex("]")+1])
    return [{"date": x.get("opendate"), "close": x.get("trade"),
             "net_amount": x.get("netamount"), "turnover": x.get("turnover")} for x in arr]

def announcements_backup(code: str, page_size: int = 20) -> list:
    """公告备用源（巨潮被封时用）：深市走深交所官方，沪市走东财，均带 PDF 直链。"""
    if code.startswith(("0", "3")):
        body = json.dumps({"channelCode": ["listedNotice_disc"], "pageSize": page_size,
                           "pageNum": 1, "stock": [code]}).encode()
        req = urllib.request.Request("https://www.szse.cn/api/disc/announcement/annList", data=body,
              headers={"User-Agent": UA, "Content-Type": "application/json",
                       "Referer": "https://www.szse.cn/disclosure/listed/notice/index.html"})
        with urllib.request.urlopen(req, timeout=15, context=_ctx) as r:
            d = json.loads(r.read())
        return [{"title": a.get("title"), "time": a.get("publishTime", "")[:10],
                 "pdf": "https://disc.static.szse.cn/download" + a.get("attachPath", "")}
                for a in d.get("data", [])]
    u = (f"https://np-anotice-stock.eastmoney.com/api/security/ann?sr=-1&page_size={page_size}"
         f"&page_index=1&ann_type=A&client_source=web&stock_list={code}&f_node=0&s_node=0")
    req = urllib.request.Request(u, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        d = json.loads(r.read())
    return [{"title": a.get("title"), "time": a.get("notice_date", "")[:10],
             "pdf": f"https://pdf.dfcfw.com/pdf/H2_{a.get('art_code','')}_1.pdf"}
            for a in (d.get("data") or {}).get("list") or []]     # #46 同因

# 用法（主源失败时降级）
lhb = dragon_tiger_backup("2026-07-10")   # 深市结构化 + 沪市全文(含营业部)
flow = fund_flow_backup("600519", 60)     # 近60日资金流
anns = announcements_backup("000858")     # 深市走深交所, 沪市走东财
```

---

## FAQ

### Q: 东财接口 403 / 连接重置，是被封了吗，怎么办？
A: 东财系接口（datacenter/push2/push2ex/reportapi/search/np-weblist）共用同一套风控，IP 被封会成片失联。三步处理：① 停止请求等 30-60 分钟（IP 级临时封通常自动解除），或换网络（手机热点）立刻恢复；② 长批任务确认全部走 `em_get()`，并调大 `EM_MIN_INTERVAL`；③ 数据不能等 → 用上方「备用源速查 & 降级策略」的独立备胎（交易所官方/新浪/同花顺，不同风控面，东财被封时不受牵连）。

### Q: 财联社快讯不是 V3.2 标注下线了吗？
A: 已复活（V3.4.0，见 §5.2）。2026-05 死的是旧 `nodeapi` 系接口；官方新版 `v1/roll/get_roll_list` 一直可用，只是强制 `sign` 校验——而 sign 纯本地可算（`md5(sha1(按 key 字典序拼接的 query 串))`），零 key。与 §5.3 东财 7×24 互为独立备份。

### Q: mootdx 取不到 K 线 / `tdx_client()` 报「所有 mootdx 服务器均无法取到数据」（#52）
A: 2026-09-20 逐台实测内置 10 台服务器，TCP 都能连上，财务、除权除息正常，F10 只剩「最新提示」一类，但 K 线、五档盘口、逐笔成交都返回 0 行。这是服务器端的变化，换 mootdx 版本解决不了。替代方案：
- 沪深日 / 周 / 月 K 线（前后复权）和 1~60 分钟 K 线 → §1.2 `tencent_kline()`
- 某交易日沪深北全市场日线（含成交额；北交所日线只能走这里）→ §1.3 `tdx_daily_package()`
- 实时价与五档 → §1.1 腾讯，或「备用源速查」里的交易所官方五档
- 当日逐笔成交 → §1.4 `tencent_ticks()`（只有最近一个交易日，不含北交所）
- 财务快照 / F10 → `tdx_client(check='finance')`，照常可用

`tdx_client()` 在 K 线模式下要先测速，全部失败大约需要 1 分钟才报错。

### Q: mootdx 库听说停更了，还能用吗？
A: 库确实烂尾（最后 commit 2024-07，官网下线，BESTIP bug 无官方修复）。本 skill 的 `tdx_client()` 已内置 IP 探测绕开 BESTIP bug；目前只用它取财务与 F10（见上一条）。

### Q: mootdx 和腾讯有什么区别？
A: 以前互补：mootdx 管价格 / 盘口 / K 线，腾讯管估值（PE/PB/市值/换手率/涨跌停价）。#52 之后价格与 K 线都走腾讯，mootdx 只剩财务快照和 F10。两者都不封 IP。

### Q: 能直接回测吗？能接聚宽吗？（#55）
A: 本 skill 只负责取数，**不带回测引擎**。回测要把数据交给自己的框架或聚宽。
- 代码格式：`norm_ticker()` / `get_prefix()` 认聚宽写法 `600519.XSHG` / `000001.XSHE`；`to_joinquant()` 把任意写法转成聚宽代码。聚宽公开文档没有北交所后缀，北交所代码会直接报错，不做转换。
- 复权：聚宽 `get_price` 默认前复权（`fq='pre'`）。对拍时用 §1.2 `tencent_kline(adjust='qfq')`，或用 §1.6 复权因子自己换算。
- 防未来函数：历史估值用 §6.5，历史行业归属用 §6.7，历史指数成分要注意 §12 只给当前快照。

### Q: 研报只能从东财拿吗？（#53）
A: 不是。§2.4 `sina_research_reports()` 是第二来源，可按个股或全市场翻页，东财被封时也能用。它只有标题、类型、机构、研究员和日期，没有评级和目标价。评级与目标价仍用 §2.1 东财或 §2.2 同花顺一致预期。

### Q: 有商品期货和期权吗？大商所呢？（#49）
A: 有，见 Layer 13。§13.1 / §13.2 取上期所、上期能源、郑商所、中金所、广期所官方的期货日行情和期权日行情，§13.3 取前四家的会员持仓排名（广期所未接）；§13.4 取新浪实时价，§13.5 取 A50 期指，§13.6 取上金所现货。**大商所官网有反爬，日行情没接**；大商所品种（豆粕、铁矿石等）的实时价可用 §13.4。

### Q: 沪市公司的互动易问答为什么是空的？
A: 巨潮互动易只覆盖深市公司，沪市公司实测返回 0 条。沪市请用 §10.3 `sse_e_interaction()`（上证e互动）。部分公司近一个月确实没有回复，返回空表属正常。

### Q: V3.0 为什么移除 akshare？
A: akshare 本质是对东财/同花顺/新浪等公开 API 的封装，中间层增加了故障点（版本兼容 bug、pandas 3.0 ArrowInvalid 等）。V3.0 直连底层 HTTP API，零中间依赖，更稳定可控。

### Q: iwencai 返回 401
A: 检查两点：(1) API Key 是否有效 (2) 是否携带了 X-Claw-* Headers。SkillHub 2.0 后必须带 X-Claw Headers，否则一律 401。

### Q: 同花顺一致预期 ths_eps_forecast 返回空
A: 该股票无机构覆盖。小盘/次新/ST 股常见。可 fallback 到东财 reportapi 里的 predictThisYearEps 字段。

### Q: 东财 PDF 下载 403
A: 必须带 `Referer: https://data.eastmoney.com/` header。

### Q: 腾讯 API 返回乱码
A: 编码是 GBK，必须 `decode("gbk")`。

### Q: 腾讯 API 字段 43 是 PB 吗？
A: **不是！** 43=振幅%，46=PB。网上很多教程写错了，这里是实测校准结果。

### Q: iwencai search 返回条数太少
A: `size` 参数默认 10，调到 50。隐藏参数，文档未写明但实测可用。

### Q: 哪些数据源需要 API Key？
A: 只有 iwencai 需要。其余 33 个来源（腾讯 / 东财 / 同花顺 / 新浪 / 巨潮 / 财联社 / 交易所与期货交易所 / 中债 / 货币网等）全部免费无 key。

### Q: 同花顺热点接口需要 cookie 吗？
A: **不需要**。仅 User-Agent 即可，零鉴权 73ms 拿到 ~125 只当日强势股。但**不要去打 search.10jqka.com.cn 的 iwencai NL 选股接口** —— 那个有 hexin-v cookie JS 签名鉴权，跟热点接口完全两码事。

### Q: 百度股市通 ResultCode 有时是 0 有时是 "0"？
A: 已知坑。`ResultCode` 返回类型不稳定——有时 int，有时 string。代码里必须用 `str(d.get("ResultCode", -1)) != "0"` 统一比较。

### Q: 北向资金历史数据为什么只有最近几天？
A: 本地自缓存模式。eastmoney 全系北向数据自 2024-08 起断供（净买额字段返回 NaN/0）。每次调用实时 API 后自动写入本地 CSV，历史越跑越丰富。

### Q: 行业板块为什么从同花顺换成东财？
A: 同花顺 `stock_board_industry_summary_ths` 接口 2026 年初加了反爬 401（需要登录态）。东财 push2 行业板块数据（`m:90+t:2`）是完美替代，零鉴权且字段更丰富。

### Q: 在海外服务器跑，mootdx 接口超时？
A: mootdx 走 TCP 直连通达信行情服务器，需国内 IP 才稳定。海外环境建议走代理。腾讯财经和百度股市通不受影响。

### Q: 不用 Claude Code，能用吗？
A: 能。SKILL.md 本质是 Markdown + 内嵌 Python 代码。Codex、OpenClaw 或任何 AI 编程助手都能读取。你也可以直接把 Python 代码段复制出来在自己的脚本里跑。

---

## 安装说明

```bash
# 1. 创建 skill 目录
mkdir -p ~/.claude/skills/a-stock-data

# 2. 将本文件复制为 SKILL.md
cp SKILL.md ~/.claude/skills/a-stock-data/SKILL.md

# 3. 安装 Python 依赖
pip install mootdx requests pandas stockstats numpy baostock xlrd openpyxl

# 4. (可选) 配置 iwencai API Key
export IWENCAI_API_KEY="your_key_here"

# 5. 启动 Claude Code，说"查一下688017的估值"即可自动激活
```

---

> 📦 https://github.com/simonlin1212/a-stock-data — Star ⭐ 是最好的支持
