<p align="center"><a href="README.md">简体中文</a> | <a href="README_en.md">English</a> | <b>日本語</b></p>

<h1 align="center">a-stock-data</h1>

<p align="center">
  <b>中国 A 株向けフルスタックデータツールキット — 15 レイヤー · 87 エンドポイント · 34 データソース · 認証不要（iwencai を除く）</b>
</p>

<p align="center">
  株価・K 線 · リサーチレポート · 市場シグナル · 資金フロー・価格帯別出来高 · ニュース · 基礎財務 · 開示資料 · ストップ高 ·
  ETF オプション · センチメント · マクロ・金利 · 指数・取引カレンダー · 先物・コモディティ · イベントドリブン · 転換社債
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License"></a>
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white" alt="Python">
  <a href="https://github.com/simonlin1212/a-stock-data/stargazers"><img src="https://img.shields.io/github/stars/simonlin1212/a-stock-data?style=social" alt="Stars"></a>
  <br>
  <img src="https://img.shields.io/badge/layers-15-2ea44f.svg" alt="レイヤー数">
  <img src="https://img.shields.io/badge/endpoints-87-2ea44f.svg" alt="エンドポイント数">
  <img src="https://img.shields.io/badge/sources-34-2ea44f.svg" alt="データソース数">
  <img src="https://img.shields.io/badge/auth-zero-success.svg" alt="認証不要">
</p>

<p align="center">
  <a href="#データカバレッジ-15-カテゴリ">カバレッジ</a> ·
  <a href="#アーキテクチャ">アーキテクチャ</a> ·
  <a href="#クイックスタート">クイックスタート</a> ·
  <a href="#87-のエンドポイント">エンドポイント</a> ·
  <a href="./CHANGELOG.md">変更履歴</a>
</p>

中国 A 株市場向けのフルスタックデータツールキットです — 15 レイヤー構成 · 87 の機能エンドポイント（メイン 82 + バックアップ 5） · 34 のデータソース · 2 つの TCP クライアントライブラリ（mootdx / baostock）を除き、すべて HTTP で直接呼び出します

34 のソースから取得した A 株および関連市場の生データを、AI コーディングアシスタントがすぐに使えるツールキットにまとめた、単体で完結する Skill ファイルです。Tencent の K 線のページングパラメーター、TDX 日次終値パッケージのバイナリ構造、Eastmoney の PDF で必要な Referer ヘッダー、iwencai の X-Claw 認証などを覚える必要はありません。すべて処理済みです。さらに、メインのソースにブロックされたときに頼れる、バックアップソースのクイックリファレンスも用意しています。

> [Claude Code](https://github.com/anthropics/claude-code) · [Codex](https://github.com/openai/codex) · [OpenClaw](https://github.com/openclaw/openclaw) · [WorkBuddy](https://www.workbuddy.cn/) · [Muse](https://muse.ai/) · [Grok Bot](https://x.ai/bot) に対応しています
>
> Skill ファイルは構造化された Markdown と埋め込みの Python で構成されています。コンテキスト注入に対応した AI コーディングアシスタントであれば、どれでも利用できます。

> **V3.10.4（2026-11-04 · #64 ファンドの権利調整）:** §1.6 の Sina 権利調整係数をファンド（ETF / LOF）に使った場合、`f` しか読み取っておらず、ファンドではこれが常に 1 のため、調整が行われていませんでした。分割比率 `s` と 1 口あたりの累積分配金 `u` も読み取るようになりました。前方調整は `raw / s - u`、後方調整は `(raw + u) * s` です。株式の結果、エントリー数、ソース数は変わりません。
>
> **V3.10.3（2026-10-23 · SSE e-Interaction の時刻列）:** §10.3 `sse_e_interaction()` は相対的な回答時刻（`昨天 18:22` — 「昨日 18:22」）を受け取ります。パーサーは絶対時刻しか受け付けず、ページ全体でエラーを送出していました。現在は相対時刻と絶対時刻のどちらも `YYYY-MM-DD HH:MM`（北京時間）に正規化され、解析できない時刻は引き続きエラーを送出します。エントリー数、ソース数、返されるデータは変わりません。
>
> **V3.10.2（2026-10-11 · #58）:** `full_valuation()` の PE 消化年数を修正しました。予想 PE が 30 倍を超え、予想利益が伸びていない（または翌年の予想がない）場合、以前は PE がすでに消化済みであるかのように 0 年を返していましたが、現在は推定できないことを示す `None` を返します。現在の EPS がない、または正でない場合も `None` を返します。エントリー数とソース数は変わりません。
>
> **V3.10.1（2026-10-07 · #57）:** §1.2 の Tencent K 線の出来高単位を修正しました。**STAR マーケット（688 / 689）は株数単位**で、それ以外はロット単位です。ドキュメントではすべてロット単位と記載していたため、旧ドキュメントに従って換算した STAR の出来高は 100 倍大きくなっていました。また、株数単位の出来高を TDX 日次終値パッケージや Baostock と照合するためのルールも追加しました。§1.4 のティックは、プール化された自動リトライ付きのセッションを使うようになり（1 回の呼び出しが約 70 秒 → 約 25 秒）、`frame.attrs["complete"]` を追加しました。これは 15:31 以降、時間外の固定価格取引の欠落をチェックします。§13.7 の先物日足 K 線もリトライするようになりました。エントリー数、ソース数、返されるデータは変わりません。
>
> **V3.10.0（2026-09-22）:** TDX の公開サーバーが K 線、板情報、ティックの提供を停止したこと（#52）を受け、株価レイヤーでは動作するソースを先に並べ（Tencent → Tencent K 線 → TDX 日次終値パッケージ → Tencent ティック）、mootdx をアーカイブとして最後に移しました。新機能: §1.4 `tencent_ticks()` — 直近の取引日の Tencent 日中ティック、約 3 秒ごとに 1 つのスナップショット（mootdx のティックを置き換え） — と §13.7 `futures_kline()` — Sina の先物日足 K 線、連続限月または個別限月、**DCE にも対応**。Layer 1 の番号を振り直しました。新旧の対応表は CHANGELOG にあります。
>
> **V3.9.0（2026-09-20）:** 3 つの新しいレイヤー — 先物・コモディティ、イベントドリブン、転換社債 — に加え、既存レイヤーに Tencent K 線、TDX 公式の日次終値パッケージ、Sina のリサーチレポート、ETF の口数、イールドカーブなどを追加し、合計 25 のエントリーを新設しました。壊れていた TDX 公開サーバーの K 線コマンド（#52）は HTTP 経由に切り替えました。詳しくは [CHANGELOG](./CHANGELOG.md)（中国語）を参照してください。

---

## データカバレッジ (15 カテゴリ)

<table>
<thead>
<tr><th nowrap>#</th><th nowrap>カテゴリ</th><th>データ</th><th>主なソース</th></tr>
</thead>
<tbody>
<tr><td nowrap>1</td><td nowrap>株価 / K 線</td><td>現在値、PE/PB/時価総額/売買回転率、日足/週足/月足の前方・後方調整および 1〜60 分足の K 線、ある取引日の全市場の日足（売買代金付き）、権利調整係数、指数 / ETF</td><td>Tencent、TDX 公式サイト、Baidu、Sina</td></tr>
<tr><td nowrap>2</td><td nowrap>リサーチ</td><td>個別銘柄 / 業界レポートと PDF、レーティング、3 年分の EPS 予想、コンセンサス EPS、自然言語検索、レポート一覧</td><td>Eastmoney、Sina、THS、iwencai</td></tr>
<tr><td nowrap>3</td><td nowrap>市場シグナル</td><td>注目銘柄とテーマ、北向き資金、所属セクター、資金フロー、龍虎榜、ロックアップ解除、業界ランキング、セクター別資金フロー</td><td>THS、Eastmoney</td></tr>
<tr><td nowrap>4</td><td nowrap>資金フロー / 価格帯別出来高</td><td>信用取引、ブロックトレード、株主数、配当、120 日間の資金フロー、価格帯別出来高（チップ分布）、ETF の口数</td><td>Eastmoney、SSE、SZSE、ローカル計算</td></tr>
<tr><td nowrap>5</td><td nowrap>ニュース</td><td>個別銘柄ニュース、CLS 速報、7×24 ライブニュース、CCTV 新聞聯播の原稿</td><td>Eastmoney、CLS、Wallstreetcn、CCTV</td></tr>
<tr><td nowrap>6</td><td nowrap>基礎財務</td><td>四半期スナップショット、F10、財務諸表、バリュエーション履歴、上場/上場廃止日、SW 業界分類の履歴、ST 銘柄一覧</td><td>TDX (mootdx)、Sina、baostock、SW、Eastmoney</td></tr>
<tr><td nowrap>7</td><td nowrap>開示資料</td><td>SSE / SZSE / BSE 全体の開示資料</td><td>cninfo</td></tr>
<tr><td nowrap>8</td><td nowrap>ストップ高</td><td>ストップ高 / 張り付き崩れ / ストップ安 / 前日ストップ高の各プール、ストップ高の理由、監視銘柄リスト、日中の異常変動</td><td>Eastmoney、THS</td></tr>
<tr><td nowrap>9</td><td nowrap>ETF オプション</td><td>T 字型気配、グリークス、インプライド・ボラティリティ</td><td>Sina</td></tr>
<tr><td nowrap>10</td><td nowrap>センチメント</td><td>cninfo IRM（深セン）、SSE e-Interaction（上海）、THS 人気ランキング、Eastmoney 人気順位、コンセプトのヒット</td><td>cninfo、SSE e-Interaction、THS、Eastmoney</td></tr>
<tr><td nowrap>11</td><td nowrap>マクロ・金利</td><td>社会融資総量、PMI、国債および信用債のイールドカーブ、レポ定盤金利、LPR、世界のマクロ指標カレンダー</td><td>PBoC、NBS、ChinaBond、China Money (CFETS)、Eastmoney、Wallstreetcn</td></tr>
<tr><td nowrap>12</td><td nowrap>指数・カレンダー</td><td>CSI / CNI の構成銘柄とウェイト、CSI の PE と配当利回り、SZSE の取引カレンダー</td><td>CSI、CNI、SZSE</td></tr>
<tr><td nowrap>13</td><td nowrap>先物・コモディティ</td><td>先物の日次相場、商品および指数オプション、会員の建玉ランキング、リアルタイム先物、FTSE China A50、SGE 現物</td><td>SHFE、INE、CZCE、CFFEX、GFEX、Sina、SGE</td></tr>
<tr><td nowrap>14</td><td nowrap>イベントドリブン</td><td>業績予想、機関投資家の調査訪問、株主の売買、自社株買い、株式担保、IPO カレンダー</td><td>Eastmoney</td></tr>
<tr><td nowrap>15</td><td nowrap>転換社債</td><td>発行条件、転換価格、転換価値、乖離率、上場 / 上場廃止の状況</td><td>Eastmoney</td></tr>
</tbody>
</table>

さらに 5 つのバックアップがあります: 公式の龍虎榜、Sina の資金フロー、開示資料、SSE/SZSE 公式の信用取引データ、BSE の現在の相場 — メインのソースがブロックされたときに使います。

---

## アーキテクチャ

```
China A-Share Full-Stack Data · 15-Layer Architecture · V3.10.4
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

> 15 のレイヤーには **バックアップソースとフォールバック戦略** の付録が含まれます: 龍虎榜、資金フロー、開示資料に加え、SSE/SZSE 公式の信用取引データと、5 段階の板情報付きの BSE の現在の相場です。カバー範囲とソースの日付は SKILL.md を参照してください。

---

## クイックスタート

**3 ステップ、2 分で完了します。**

```bash
# 1. Create skill directory
mkdir -p ~/.claude/skills/a-stock-data

# 2. Download SKILL.md
curl -o ~/.claude/skills/a-stock-data/SKILL.md \
  https://raw.githubusercontent.com/simonlin1212/a-stock-data/main/SKILL.md

# 3. Install dependencies (V3.0: akshare no longer needed; V3.9 adds none)
pip install mootdx requests pandas stockstats numpy baostock xlrd openpyxl
```

Claude Code を起動して「688017 のバリュエーションを確認して」と伝えると、スキルが自動的に有効になります。

> **Codex / OpenClaw のユーザー:** SKILL.md の内容をシステムプロンプトまたはプロジェクトのコンテキストファイルに貼り付けてください。埋め込まれた Python コードはそのまま実行できます。

---

## 87 のエンドポイント

メインのエントリーが 82、バックアップが 5 あります。数は機能エントリー単位で数えています。1 つの関数内の CSI/CNI や SSE/SZSE のルートは 1 つとして数え、ヘルパーやリサーチ候補は含みません。

> **数え方:** 以下の表は 88 行ありますが、機能エンドポイントとしては 87 と数えます — 「Eastmoney 業界レポート」は「Eastmoney reportapi」と **同じエンドポイント** を共有しており（`qType` パラメーターが違うだけ）、「THS 北向き資金（履歴）」はローカルで自作したキャッシュ（独立したエンドポイントではない）なので、どちらも数えません。一方、「EM 日中異常変動プール」の 1 行は **2 つ** のエンドポイント（`list` / `count`）をカバーしているため、1 つ加えます。88 − 1 − 1 + 1 = 87 です。ティッカーのヘルパー `to_joinquant()` は数えません。

### 株価データ（リアルタイム、IP ブロックなし）

<table>
<thead>
<tr><th nowrap>エンドポイント</th><th>データ</th></tr>
</thead>
<tbody>
<tr><td nowrap>Tencent Finance</td><td>PE(TTM) / PB / 時価総額 / 浮動株時価総額 / 売買回転率 / 値幅制限 / 指数 / ETF</td></tr>
<tr><td nowrap><strong>Tencent K 線</strong></td><td>SSE/SZSE の日足/週足/月足の前方・後方調整 + 1/5/15/30/60 分足。Tencent の 3 つのホストをローテーションします。BSE は対象外（V3.9 新規）</td></tr>
<tr><td nowrap><strong>TDX 日次終値パッケージ</strong></td><td>ある取引日の SSE/SZSE/BSE 全銘柄の日足（売買代金付き）。2〜3 MB の zip 1 つ。2022-01-04 と 2023-01-03 は取得可能なことを確認済み、2021-01-04 は削除済み、すべての日は検証していません。2022-05-06 より前のパッケージには BSE のファイルがありません（V3.9 新規）</td></tr>
<tr><td nowrap><strong>Tencent ティック</strong></td><td>直近の取引日の全ティック（約 3 秒ごとのスナップショットで、Level-2 の約定ごとのデータではありません）: 時刻 / 価格 / 出来高 / 売買代金 / 売買区分。SSE/SZSE の株式 + ETF、BSE は対象外。大引け後は合計をその日の売買代金と照合します（V3.10 新規、mootdx のティックを置き換え）</td></tr>
<tr><td nowrap><strong>Baidu K 線</strong></td><td>日足 K 線 + MA5/MA10/MA20 移動平均を含む（V3.0 新規）</td></tr>
<tr><td nowrap><strong>Sina 権利調整係数</strong></td><td>qfq / hfq の係数系列 + 未調整のローソク足への適用（V3.7 新規）</td></tr>
<tr><td nowrap>mootdx 株価データ（アーカイブ）</td><td>ローソク足（複数期間） + 板情報 + ティック + 46 フィールドの気配（⚠️ TDX の公開サーバーは 2026-09 以降空のデータを返します。FAQ #52 を参照。足データには Tencent K 線 / 日次終値パッケージを、約定には Tencent ティックを使ってください）</td></tr>
</tbody>
</table>

### リサーチレポート

| エンドポイント | データ |
|----------|------|
| Eastmoney reportapi | 個別銘柄のレポート一覧 + レーティング + 3 年分の EPS 予想 |
| Eastmoney 業界レポート | 業界レポート一覧（qType=1、同じエンドポイント） + 業界名/コード + レーティング（V3.2.3） |
| Eastmoney PDF | リサーチレポートの PDF 全文、個別銘柄・業界（Referer 認証は処理済み） |
| THS コンセンサス EPS | 機関投資家のコンセンサス EPS（basic.10jqka.com.cn に直接アクセス） |
| iwencai 自然言語検索 | 自然言語によるテーマ横断のレポート検索 |
| **Sina レポート一覧** | タイトル / 種類 / 証券会社 / アナリスト / 日付 — Eastmoney 以外の 2 つ目のソース。レーティングや目標株価はなし（V3.9 新規、#53） |

### シグナル

| エンドポイント | データ |
|----------|------|
| THS 注目銘柄 | 当日の強い銘柄 + セクター要因タグ（編集部による注釈） |
| THS 北向き資金（リアルタイム） | 滬股通の分単位の資金フロー（上流の開示が厳しくなって以降、深股通は信頼できません — 正確なデータは HKEX のバックアップを参照） |
| THS 北向き資金（履歴） | ローカルで自作キャッシュした日次の履歴 |
| Eastmoney 所属セクター | 銘柄が属するすべてのセクター（業界/コンセプト/地域の混在） + BK コード + 当日の騰落率 + 主導銘柄（V3.2.2、Baidu PAE を置き換え、1 リクエスト） |
| **Eastmoney 資金フロー** | 主力 / 大口 / 中口 / 小口 / 超大口注文の分単位の純流入（V3.1、Baidu PAE を置き換え） |
| 龍虎榜 | 掲載記録 + 買い/売り上位 5 社の証券会社 + 機関投資家の動向 |
| 日次の龍虎榜（全市場） | 当日掲載の全銘柄 + 純買いランキング + 掲載理由 |
| ロックアップ解除カレンダー | 過去の解除実績 + 90 日以内の解除予定アラート |
| **業界ランキング** | Eastmoney の業界別騰落率/値上がり・値下がり銘柄数（V3.0、THS 401 を置き換え） |
| **セクター別資金フロー** | 業界/コンセプト/地域 × 当日/5 日/10 日の主力純流入額と比率 + 超大口/大口/中口/小口の区分 + 主導銘柄（V3.5、業界ランキングと同じエンドポイント） |

### 資金フロー / 株主構成（V3.0 新規）

| エンドポイント | データ |
|----------|------|
| **信用取引** | 日次の融資残高 / 買付 / 返済 + 貸株残高 |
| **ブロックトレード** | 約定価格/数量 + 買い手/売り手の証券会社 + プレミアム率 |
| **株主数** | 四半期ごとの株主数 + 前期比の変化 + 1 株主あたりの平均保有株数 |
| **配当履歴** | 1 株あたりの現金配当 / 株式配当 / 資本準備金の株式転換 |
| **120 日間の資金フロー** | 主力 / 大口 / 中口 / 小口注文の日次の純流入 |
| **価格帯別出来高 (CYQ)** | 含み益比率 / 平均コスト / 90-70 のコストレンジと集中度 / チップのピーク（ローカル計算、V3.7 新規） |
| **ETF の口数** | SSE の日次アーカイブ（2022-01-04 も取得可能なことを確認済み） / SZSE の現在のスナップショット、1 万口単位（V3.9 新規） |

### ニュース

<table>
<thead>
<tr><th nowrap>エンドポイント</th><th>データ</th></tr>
</thead>
<tbody>
<tr><td nowrap>個別銘柄ニュース</td><td>Eastmoney の銘柄別ニュース（search-api-web に直接アクセス）</td></tr>
<tr><td nowrap>CLS 速報</td><td>市場全体のリアルタイム速報（v1 API + ローカル署名、キー不要、✅V3.4.0 で復活、グローバルニュースと相互にバックアップ）</td></tr>
<tr><td nowrap>グローバルニュース</td><td>Eastmoney のグローバル金融ニュース（np-weblist に直接アクセス、7×24）</td></tr>
<tr><td nowrap><strong>Wallstreetcn ライブ</strong></td><td>チャンネル別の 7×24 ライブニュース、ページングカーソル付き（V3.9 新規）</td></tr>
<tr><td nowrap><strong>CCTV 新聞聯播</strong></td><td>新聞聯播の項目タイトル + 原稿（cctv.com、北京時間の 20:00 頃以降に更新、V3.9 新規）</td></tr>
</tbody>
</table>

### 基礎財務 + 開示資料

| エンドポイント | データ |
|----------|------|
| 四半期スナップショット | 37 フィールド（EPS / ROE / 純利益 / 売上高...） |
| F10 テキスト | 「最新メモ」（開示資料 / ニュース / ブロックトレード / 信用取引 / リスク警告の要約）。2026-09 以降、サーバーはこのカテゴリしか返しません |
| Eastmoney 銘柄情報 | 業界 / 発行済株式数 / 浮動株 / 時価総額 / 上場日（push2 に直接アクセス） |
| Sina 財務諸表 | 貸借対照表 / 損益計算書 / キャッシュフロー計算書（quotes.sina.cn に直接アクセス） |
| cninfo 開示資料 | 全取引所の開示資料 |
| **バリュエーション履歴** | 日次の PE/PB/PS/PCF + 売買回転率 + 売買停止 + ST フラグ（2016 年まで遡る。**北京証券取引所は非対応**、V3.7 新規） |
| **上場 / 上場廃止日** | ipoDate / outDate / status（上場廃止日を認証なしで取得できる唯一のソース、V3.7 新規） |
| **SW 業界分類の履歴** | 銘柄ごとのすべての業界再分類（ルックアヘッドバイアスを排除。コードのみで中国語名はなし、V3.7 新規） |
| **ST 銘柄一覧** | 当日の SSE/SZSE/BSE の ST および *ST 銘柄と株価。Eastmoney に接続できない場合は baostock にフォールバック（SSE/SZSE のみ、株価なし）（V3.9 新規） |

### ストップ高 / ストップ安（V3.3 新規）

| エンドポイント | データ |
|----------|------|
| EM ストップ高プール | 連続ストップ高 / N 日 M 回ストップ高 / 張り付き資金 / 崩れた回数 / 張り付いた時刻 / 業界 |
| EM 張り付き崩れプール | ストップ高後に崩れた銘柄 + 振幅 / 速度 |
| EM ストップ安プール | 張り付き資金 / 連続ストップ安 / 崩れた回数 / ストップ安での売買回転率 |
| EM 前日ストップ高プール | 前日のストップ高銘柄の当日の値動き（連続ストップ高への昇格率 / 利益効果） |
| THS ストップ高インサイト | ストップ高の理由テーマ / 張り付き成功率 / ボードの種類 / 張り付き金額 |
| EM 監視銘柄プール | 取引所のリスク警告 / 監視銘柄リスト + 有効期間（V3.6 新規） |
| EM 日中異常変動プール | 深刻な価格異常の詳細 + 銘柄ごとの集計件数 + 全 12 種類の異常ルールの解説（V3.6 新規） |

### ETF オプション（V3.3 新規）

| エンドポイント | データ |
|----------|------|
| オプション銘柄一覧 | 50ETF / 300ETF / STAR50 ETF / 500ETF の月別コール・プット銘柄 |
| T 字型気配 | 売買 5 段階の気配 / 建玉 / 権利行使価格 / 直近値 / 出来高 |
| グリークス + IV | Delta / Gamma / Theta / Vega / インプライド・ボラティリティ / 理論価格（取引所算出、ローカルの BSM 計算なし） |

### センチメントと対話（V3.3 新規）

<table>
<thead>
<tr><th nowrap>エンドポイント</th><th>データ</th></tr>
</thead>
<tbody>
<tr><td nowrap>投資家 Q&amp;A (IRM)</td><td>投資家の質問 + 企業の公式回答（cninfo、深セン上場企業。企業が噂やニュースにどう対応するかがわかる唯一のソース）</td></tr>
<tr><td nowrap><strong>SSE e-Interaction</strong></td><td>cninfo IRM がカバーしていない上海上場企業の投資家の質問 + 回答（V3.9 新規）</td></tr>
<tr><td nowrap>THS 人気ランキング</td><td>人気度 / コンセプトタグ / 順位の変化</td></tr>
<tr><td nowrap>EM 人気順位</td><td>順位 + 順位の変化 + 銘柄名/株価</td></tr>
<tr><td nowrap>EM 銘柄のコンセプトヒット</td><td>市場がこの銘柄をどのコンセプトに分類しているか + 注目度</td></tr>
</tbody>
</table>

### マクロ・金利（V3.7 新規、V3.9 で拡張）

<table>
<thead>
<tr><th nowrap>エンドポイント</th><th>データ</th></tr>
</thead>
<tbody>
<tr><td nowrap><strong>PBoC 社会融資総量</strong></td><td>実体経済への資金供給総量、月次、12 列（人民元/委託/信託貸付、未割引の銀行引受手形、社債・国債、株式による資金調達、ABS、貸倒償却）</td></tr>
<tr><td nowrap><strong>NBS PMI</strong></td><td>製造業 / 非製造業 / 総合 PMI + 大企業 / 中企業 / 小企業の内訳</td></tr>
<tr><td nowrap><strong>ChinaBond イールドカーブ</strong></td><td>国債 / 商業銀行 AAA / 短期債 AAA、3 か月〜30 年（V3.9 新規）</td></tr>
<tr><td nowrap><strong>レポ定盤金利</strong></td><td>FR001 / FR007 / FR014 と対応する FDR の各年限（China Money。FR は約 3 年分、FDR は約 1 年分の履歴、V3.9 新規）</td></tr>
<tr><td nowrap><strong>LPR</strong></td><td>1 年 / 5 年の全履歴（2013〜2019 年の旧制度における日次の気配を含む、V3.9 新規）</td></tr>
<tr><td nowrap><strong>世界のマクロ指標カレンダー</strong></td><td>実績値 / 予想値 / 前回値 / 改定値と重要度（Wallstreetcn、V3.9 新規）</td></tr>
</tbody>
</table>

### 指数データと取引カレンダー

| エンドポイント | データ |
|----------|------|
| 指数構成銘柄 | CSI の最新構成銘柄と、CNI が公表した最新の月末構成銘柄。実際のソースの日付で、過去の構成銘柄の遡及はなし |
| 指数ウェイト | CSI/CNI が公表した最新のウェイト（パーセントポイント）。日付は構成銘柄と異なる場合があります |
| 指数バリュエーション | 2 種類の株式資本の基準による CSI の PE と配当利回り。直近のファイルで、PB や全履歴は保証されません |
| 公式取引カレンダー | SZSE の取引カレンダー（月単位で完全）。欠けている日、未公表の月、不明なフラグはエラーを送出します |

### 先物・コモディティ（V3.9 新規、#49）

<table>
<thead>
<tr><th nowrap>エンドポイント</th><th>データ</th></tr>
</thead>
<tbody>
<tr><td nowrap><strong>先物の日次相場</strong></td><td>SHFE / INE / CZCE / CFFEX / GFEX の公式の終値データ: 四本値、清算価格、出来高、建玉とその増減、売買代金</td></tr>
<tr><td nowrap><strong>オプションの日次相場</strong></td><td>商品および指数オプション: 権利行使価格、清算価格、出来高と建玉、Delta、インプライド・ボラティリティ（SHFE / INE はシリーズ単位、CZCE / GFEX は銘柄単位。CFFEX は Delta も IV も公表していません）</td></tr>
<tr><td nowrap><strong>会員の建玉ランキング</strong></td><td>出来高 / 買い建玉 / 売り建玉の上位 20 会員とその増減（SHFE、INE、CZCE、CFFEX）</td></tr>
<tr><td nowrap><strong>リアルタイム先物</strong></td><td>6 つの先物取引所すべての Sina のリアルタイム価格と最良気配（DCE の銘柄にはこれを使用）。値幅制限は CFFEX の銘柄のみ</td></tr>
<tr><td nowrap><strong>先物日足 K 線</strong></td><td>連続限月（<code>RB0</code> / <code>M0</code>、2005 年まで遡る）または個別限月（2022 年頃以降に満期を迎えるもの）の Sina の日足。DCE を含む 6 取引所すべてに対応。価格は公式の日次データと一致しますが、清算価格は不完全です（V3.10 新規）</td></tr>
<tr><td nowrap><strong>FTSE China A50</strong></td><td>FTSE China A50 の連続限月先物の相場</td></tr>
<tr><td nowrap><strong>SGE 現物</strong></td><td>上海黄金取引所の Au99.99 / Au(T+D) / Ag(T+D) / Pt99.95 などの日足</td></tr>
</tbody>
</table>

> DCE のウェブサイトは JavaScript チャレンジを使っているため（通常の HTTP では 412 が返る）、公式の日次相場は統合していません。DCE の履歴には先物日足 K 線を、リアルタイム価格にはリアルタイム先物を使ってください。

### イベントドリブン（V3.9 新規）

| エンドポイント | データ |
|----------|------|
| **業績予想** | 予想の種類、予想額と変動率のレンジ、前年の数値、理由 |
| **機関投資家の調査訪問** | 調査の概要（機関数、方法、場所）または機関ごとの詳細 |
| **株主の売買** | 株主、売買の方向、変動した株数と比率、変動後の保有数、平均価格、経路 |
| **自社株買い** | 上限価格、予定株数と金額のレンジ、これまでの取得株数と金額、進捗 |
| **株式担保** | CSDC の週次の担保比率、担保株数と評価額、担保件数（SSE/SZSE のみ） |
| **IPO カレンダー** | 申込 / 抽選 / 払込 / 上場の日程、公募価格と PE、当選率、初日のパフォーマンス |

### 転換社債（V3.9 新規）

<table>
<thead>
<tr><th nowrap>エンドポイント</th><th>データ</th></tr>
</thead>
<tbody>
<tr><td nowrap><strong>転換社債</strong></td><td>対象株式、格付け、発行規模、転換価格、転換価値、乖離率、上場 / 満期 / 上場廃止の日付と状況</td></tr>
</tbody>
</table>

### バックアップソース（メインのソースが失敗したときのフォールバック）

| エンドポイント | データ |
|----------|------|
| 公式の龍虎榜バックアップ | SSE + SZSE の公式 API、認証不要、権威ある一次情報、証券会社の席位を含む（Eastmoney にブロックされたとき） |
| 資金フローのバックアップ | Sina の日次 4 区分の注文の純フロー（超大口 / 大口 / 中口 / 小口 + 純流入） |
| 開示資料のバックアップ | 深セン銘柄は SZSE 公式、上海銘柄は Eastmoney、どちらも PDF への直接リンク付き（cninfo にブロックされたとき） |
| 公式の信用取引バックアップ | SSE/SZSE を個別に照会。金額は人民元、数量は株数/口数。SSE の貸株残高が欠けている場合は null のまま |
| BSE 相場のバックアップ | 市場全体または単一銘柄の四本値、出来高、売買代金、5 段階の板スナップショット。セッションの日付を検証します。過去データの遡及や日中の遅延の検証はなし |

> さらに、**レイヤーごとのメイン → 独立したバックアップの対応表**（取引所公式 / THS F10 / HKEX / cninfo webapi / Jin10 — すべて異なるレート制限の系統）と「停止が確認されたソース」の一覧があります — SKILL.md の「Backup Sources & Fallback Strategy」セクションを参照してください。V3.9 からは、メインの K 線ソースは Tencent で、全市場の日足は TDX パッケージから、レポート一覧は Sina から取得できます。

### 認証

iwencai を除き、統合されたすべてのソースでユーザー登録や API キーは不要です。CSI、CNI、BSE（V3.8）と、V3.9 で追加した 12 のソース（TDX 公式サイト、Wallstreetcn、CCTV、SSE e-Interaction、ChinaBond、China Money、5 つの先物取引所、SGE）はユーザーの認証情報を必要としません。BSE は匿名のサイト Cookie を確立します。API キーが必要なのは iwencai のセマンティック検索だけです（[こちらで申請](https://www.iwencai.com/skillhub)）。オプションのリサーチ候補はこれらの機能に含まれません。

---

## 使用例

AI アシスタントにこう伝えるだけです:

| シナリオ | プロンプト |
|----------|--------|
| バリュエーション | 「688017 を評価して — PE / PEG / 投資回収期間を教えて」 |
| セクター要因 | 「今日強い銘柄はどれで、どのセクターが牽引している？」 |
| リサーチレポート | 「人型ロボットのサプライチェーン、特にボールねじと減速機に関する最新レポート」 |
| 北向き資金 | 「今日の北向き資金の動きはどう？」 |
| コンセプトセクター | 「688017 はどのコンセプトセクターに属している？」 |
| 資金フロー | 「今日、機関の資金は 000858 に流入している？流出している？」 |
| 龍虎榜 | 「002475 は最近龍虎榜に載った？どの証券会社が買っている？」 |
| 日次の龍虎榜 | 「今日の龍虎榜で純買いが最も多かった銘柄は？」 |
| ロックアップ解除 | 「この銘柄で今後 3 か月以内にロックアップ解除はある？」 |
| 業界ローテーション | 「今日最も上がった業界はどれで、資金はどこに流れている？」 |
| 信用取引 | 「600519 の融資残高の最近の推移は？」 |
| ブロックトレード | 「この銘柄で最近ブロックトレードはあった？プレミアム？ディスカウント？」 |
| 株主数 | 「000858 の株主数は増えている？減っている？」 |
| 配当 | 「茅台はこれまでにいくら配当を出してきた？」 |
| ETF の相場 | 「510050（SSE 50 ETF）の価格と今日の騰落率は？」 |
| ストップ高のセンチメント | 「今日ストップ高になった銘柄はいくつ？最多の連続ストップ高と崩れた比率は？」 |
| ストップ高のテーマ | 「今日のストップ高を牽引したテーマは？複数日連続のものはどれ？」 |
| 監視銘柄プール | 「今、取引所の監視銘柄リストに載っているのはどの銘柄で、いつまで？」 |
| 日中の異常変動 | 「今日深刻な価格異常があった銘柄はどれで、どのルールに該当した？」 |
| 異常変動 × 監視銘柄 | 「今日の異常変動銘柄のうち、すでに監視銘柄リストに載っているのは？」 |
| ETF オプション | 「アット・ザ・マネーの 50ETF オプションのインプライド・ボラティリティと Delta は？」 |
| 投資家 Q&A | 「最近投資家は BYD に何を質問していて、会社はどう答えた？」 |
| 市場の注目度 | 「今日最も注目されている銘柄はどれで、どのコンセプトに分類されている？」 |
| ニュースと開示資料 | 「300476 の最近のニュースと開示資料を取得して」 |
| 市場速報 | 「今、CLS 速報に大きな市場ニュースは出ている？」 |
| 一括比較 | 「この半導体 5 銘柄のバリュエーションを比較して」 |
| **価格帯別出来高** | 「600519 はどれくらいが含み益で、平均コストとチップのピークはどこ？」 |
| **バリュエーション履歴** | 「茅台の PE は過去 10 年で何パーセンタイル？売買回転率も見せて」 |
| **ST / 売買停止** | 「000004 はいつ ST に指定された？売買停止になったことはある？」 |
| **業界分類の変化** | 「000001 は 2016 年にどの SW 業界に属していた？今と同じ？」 |
| **マクロ環境** | 「最新の社会融資総量と PMI は？流動性は緩和的？引き締め的？」 |
| 指数構成銘柄 | 「CSI 300 の最新の構成銘柄とそのソースの日付を一覧にして」 |
| 指数ウェイト | 「ChiNext の最新の公表ウェイトを、実際の日付を保持したまま表示して」 |
| 指数バリュエーション | 「CSI 300 の最近の PE と配当利回りを、2 つの基準それぞれで表示して」 |
| 取引カレンダー | 「SZSE によると、2026 年 9 月の営業日はどの日？」 |
| 信用取引のバックアップ | 「Eastmoney が使えないので、2026-09-03 の SSE と SZSE の信用取引データを個別に取得して」 |
| BSE のバックアップ | 「920021 の現在の BSE 公式スナップショットを取得して、セッションの日付を検証して」 |
| **権利調整済み K 線** | 「600519 の 2025 年以降の前方調整済み日足と、300750 の直近 96 本の 5 分足」 |
| **全市場の日足** | 「2026-09-18 の SSE/SZSE/BSE 全銘柄の終値と売買代金、売買代金の上位 20 銘柄」 |
| **2 つ目のレポートソース** | 「Eastmoney が落ちているので、Sina で 600519 の最近のレポートを一覧にして」 |
| **ETF の口数** | 「510300 の口数は過去半年で増えた？減った？」 |
| **7×24 ライブニュース** | 「Wallstreetcn の A 株チャンネルの最新 50 件」 |
| **CCTV 新聞聯播** | 「今夜の新聞聯播ではどの業界が取り上げられた？」 |
| **ST 銘柄一覧** | 「現在 ST と *ST の銘柄はいくつあり、BSE ではいくつ？」 |
| **上海の Q&A** | 「浦発銀行は最近 SSE e-Interaction で何と回答している？」 |
| **イールドカーブ** | 「10 年国債利回りは今年どう推移し、AAA 短期債とのスプレッドは？」 |
| **短期金融市場の金利** | 「過去 1 か月の FR007 と、LPR が最後に変更されたのはいつ？」 |
| **マクロ指標カレンダー** | 「来週発表される主要なマクロ指標は？先週の発表は予想と比べてどうだった？」 |
| **先物の日次相場** | 「SHFE の鉄筋と銅の各限月の、昨日の清算価格と建玉」 |
| **商品オプション** | 「昨日の SHFE 銅オプションの Delta とインプライド・ボラティリティ」 |
| **建玉ランキング** | 「IF2610 の上位 20 会員の買い/売り建玉の増減」 |
| **コモディティ** | 「大豆粕は今いくらで、A50 先物と SGE の金は？」 |
| **業績予想** | 「第 3 四半期の業績予想で、最も大きな増益が見込まれているのは？」 |
| **機関投資家の調査訪問** | 「最近 688062 を調査訪問した機関は？」 |
| **株主の売買 / 自社株買い** | 「今月売っている株主は誰で、自社株買いをしている会社はどこ？」 |
| **株式担保** | 「担保比率が最も高い会社はどこ？」 |
| **IPO カレンダー** | 「今週申し込める IPO はどれで、公募時の PE はいくら？」 |
| **転換社債** | 「今、転換乖離率が最も低い転換社債はどれ？」 |
| **JoinQuant のティッカー** | 「これらのティッカーを JoinQuant 形式に変換して」 |

### 4 つの組み込みリサーチワークフロー

<table>
<thead>
<tr><th nowrap>ワークフロー</th><th>内容</th><th nowrap>所要時間</th></tr>
</thead>
<tbody>
<tr><td nowrap>個別銘柄のバリュエーション</td><td>現在値 → コンセンサス EPS → 予想 PE / PEG / PE 回収年数</td><td nowrap>30 秒</td></tr>
<tr><td nowrap>一括比較</td><td>バリュエーションの横並びランキング</td><td nowrap>1 分</td></tr>
<tr><td nowrap>テーマリサーチ</td><td>iwencai の複数キーワードによる自然言語検索 + Eastmoney PDF との相互参照</td><td nowrap>2 分</td></tr>
<tr><td nowrap>新規銘柄のリサーチ</td><td>カバレッジ → バリュエーション → コンセプト → 資金フロー → 龍虎榜 → ロックアップ → 信用取引</td><td nowrap>1 分</td></tr>
</tbody>
</table>

---


## データソースの優先順位（V3.9 で IP ブロックのリスク順に再ランク付け）

> **原則: Tencent や取引所 / 公的機関が提供しているデータには Eastmoney を使わないこと。** Tencent、公式ソース、Sina から取得できる株価、K 線、現在値、時価総額、財務諸表は、必ずそれらから取得します。mootdx の株価コマンドは 2026-09 以降空のデータを返すため（#52）、mootdx は財務スナップショットと F10 にのみ使います。Eastmoney はそこにしかないデータにのみ使い、すべてレート制限付きの `em_get()` を経由します。

<table>
<thead>
<tr><th nowrap>優先順位</th><th>ソース</th><th nowrap>プロトコル</th><th>IP ブロックのリスク</th><th>用途</th></tr>
</thead>
<tbody>
<tr><td nowrap><strong>1（最優先）</strong></td><td>Tencent Finance</td><td nowrap>HTTP</td><td><strong>ブロックされない</strong>（K 線のホストの 1 つは約 600 回の呼び出しでレート制限がかかるため、3 つのホストをローテーション）</td><td>現在値 / PE / PB / 時価総額 / 売買回転率 / 値幅制限 / 指数 / ETF / 日足・週足・月足と分足の K 線</td></tr>
<tr><td nowrap><strong>2</strong></td><td>取引所 / 公的機関</td><td nowrap>HTTP</td><td>非常に低い（短時間の集中アクセスは避ける）</td><td>TDX パッケージ、SSE / SZSE / BSE、5 つの先物取引所、SGE、ChinaBond、China Money、CSI / CNI、PBoC、NBS</td></tr>
<tr><td nowrap><strong>3</strong></td><td>Sina / cninfo / THS / Baidu / CLS / Wallstreetcn / CCTV / SW</td><td nowrap>HTTP</td><td>低い</td><td>財務諸表、権利調整係数、レポート一覧、リアルタイム先物、開示資料、コンセンサス EPS、注目銘柄と北向き資金、移動平均付き K 線、ライブニュース、新聞聯播、業界分類の履歴</td></tr>
<tr><td nowrap><strong>4</strong></td><td>mootdx (TDX)</td><td nowrap>TCP 7709</td><td>ブロックされない</td><td>財務スナップショットと F10 の &quot;最新メモ&quot; は動作します。<strong>K 線 / 板情報 / ティックは 2026-09 以降空のデータを返します（#52）</strong>。ティックは現在 Tencent の §1.4 から取得します</td></tr>
<tr><td nowrap><strong>4</strong></td><td>baostock</td><td nowrap>TCP</td><td>低い（登録不要）</td><td>バリュエーション履歴 PE/PB/PS/PCF + 売買回転率 + 売買停止 + ST + 上場/上場廃止日（<strong>北京証券取引所は対象外</strong>）</td></tr>
<tr><td nowrap>キーが必要</td><td>iwencai</td><td nowrap>OpenAPI</td><td>低い</td><td>自然言語によるセマンティックなレポート検索（キーが必要な唯一のソース）</td></tr>
<tr><td nowrap><strong>最後（独自データのみ）</strong></td><td><strong>Eastmoney</strong> datacenter / push2 / reportapi / search / np-weblist</td><td nowrap>HTTP</td><td><strong>中 — レート制限のリスクあり</strong></td><td>龍虎榜 / ロックアップ解除 / 信用取引 / ブロックトレード / 株主 / 配当 / 資金フロー / レポート PDF / ニュース / ST 銘柄一覧 / LPR / イベントドリブン / 転換社債（すべて <code>em_get()</code> 経由）</td></tr>
</tbody>
</table>

<details>
<summary><b>全 34 ソース</b></summary>

| # | ソース | 主な用途 |
|---|--------|----------|
| 1 | Tencent Finance | 現在のバリュエーション、指数 / ETF、日足・週足・月足と分足の K 線 |
| 2 | mootdx (TDX TCP) | 財務スナップショット、F10（株価コマンドは故障中、#52） |
| 3 | Eastmoney datacenter | 龍虎榜、ロックアップ解除、信用取引、ブロックトレード、株主、配当、イベントドリブン、転換社債、LPR |
| 4 | Eastmoney push2 / push2his | 業界ボード、資金フロー、銘柄情報、ST 銘柄一覧 |
| 5 | iwencai | 自然言語によるレポート検索（キーが必要） |
| 6 | Eastmoney reportapi / PDF | レポート一覧、レーティング、PDF |
| 7 | THS 注目銘柄 | 注目銘柄とテーマ、ストップ高インサイト、人気ランキング |
| 8 | THS hsgtApi | 北向き資金 |
| 9 | Baidu Finance | 移動平均付き K 線 |
| 10 | Sina Finance | 財務諸表、権利調整係数、ETF オプション、レポート一覧、リアルタイム先物、A50 |
| 11 | THS basic | コンセンサス EPS |
| 12 | CLS (Cailianpress) | 速報ニュース |
| 13 | cninfo | 開示資料、IRM Q&A |
| 14 | SSE 公式 | 龍虎榜、板情報、信用取引、ETF の口数 |
| 15 | SZSE 公式 | 龍虎榜、開示資料、板情報、信用取引、取引カレンダー、ETF の口数 |
| 16 | baostock | バリュエーション履歴、上場/上場廃止日、ST 銘柄一覧のフォールバック |
| 17 | SW Research | 業界分類の履歴 |
| 18 | PBoC | 社会融資総量 |
| 19 | NBS | PMI |
| 20 | CSI | 構成銘柄、ウェイト、PE と配当利回り |
| 21 | CNI | 構成銘柄、ウェイト |
| 22 | BSE 公式 | 現在の相場と板情報 |
| 23 | TDX 公式の日次終値パッケージ | ある取引日の SSE/SZSE/BSE 全市場の日足（売買代金付き） |
| 24 | Wallstreetcn | 7×24 ライブニュース、世界のマクロ指標カレンダー |
| 25 | CCTV | 新聞聯播の項目と原稿 |
| 26 | SSE e-Interaction | 上海の投資家 Q&A |
| 27 | ChinaBond | 国債および信用債のイールドカーブ |
| 28 | China Money (CFETS) | レポ定盤金利 FR / FDR |
| 29 | SHFE | 先物 / オプションの日次相場、建玉ランキング |
| 30 | INE | 原油 / 国際銅の先物とオプション、建玉ランキング |
| 31 | CZCE | 先物 / オプションの日次相場、建玉ランキング |
| 32 | CFFEX | 指数 / 債券先物、指数オプション、建玉ランキング |
| 33 | GFEX | 工業用シリコン / 炭酸リチウムの先物とオプションの日次相場 |
| 34 | SGE | 金 / 銀 / プラチナ現物の日足 |

</details>

> **アーキテクチャ:** mootdx と baostock（どちらも TCP クライアントライブラリ）を除き、すべてのソースはサードパーティのデータラッパーを介さず、HTTP API を直接呼び出します。**Eastmoney の API にはレート制限があり、すべての呼び出しは `em_get()` を経由して直列にスロットリングされます。バッチ処理では `EM_MIN_INTERVAL` を大きくしてください。**
>
> **フォールバック:** メインのソースが失敗した場合は、SKILL.md の「Backup Sources & Fallback Strategy」セクションを確認してください。一部の主要なデータ種別には、**レート制限が別々の異なるドメイン** に独立したバックアップがあります。すべての機能にバックアップがあるわけではありません。取得後は必ず日付と完全性を確認してください。

---

## FAQ

**指数ウェイトの日付が今日になっていないのはなぜ？過去のバックテストに使える？**
構成銘柄とウェイトは異なる日に公表される場合があります。CNI のエンドポイントは月末のスナップショットを返し、`date` はソースの日付です。現在の構成銘柄は過去の構成銘柄ではありません。このリリースでは、入れ替えの履歴は統合しておらず、欠けている指数の PB をゼロで代用することもしていません。

**2 つの新しいバックアップはどう実行する？**
SKILL.md の Layer 12 のコードブロック全体を実行し、次に公式の信用取引/BSE バックアップのブロックを実行してください。信用取引データは `SH` と `SZ` で個別に照会します。BSE では想定するセッションの日付が必要です。日付の不一致、不完全なページング、未公表のデータはエラーを送出します。

**mootdx が K 線を返さない / `tdx_client()` がデータを返せるサーバーがないと言う（#52）**
2026-09-20 に組み込みの 10 台のサーバーそれぞれでテストしました。すべて TCP 接続を受け付け、財務データと権利落ちデータを返しますが、F10 は「最新メモ」カテゴリしか返さず、K 線、板情報、ティックは 0 行で返ってきます。これはサーバー側の変更で、mootdx のバージョンを変えても解決しません。代替手段:
> - SSE/SZSE の日足 / 週足 / 月足の K 線（権利調整済み）と 1〜60 分足 → §1.2 `tencent_kline()`
> - ある取引日の SSE/SZSE/BSE 全市場の日足（売買代金付き。BSE の日足を取得できる唯一の経路） → §1.3 `tdx_daily_package()`
> - 現在値と板情報 → §1.1 Tencent、またはバックアップ表にある取引所公式の板情報
> - 日中のティック → §1.4 `tencent_ticks()`（直近の取引日のみ、BSE は対象外）
> - 財務スナップショット / F10 の「最新メモ」 → 引き続き動作する `tdx_client(check='finance')`。F10 の他の 8 カテゴリ（会社概要、株主など）はもう返されません — 代替手段は SKILL.md の §6.2 を参照してください
>
> K 線モードの `tdx_client()` は最初にサーバーを探索するため、すべて失敗した場合はエラーが送出されるまで約 1 分かかります。

**easy_tdx（PR #54）や THS の公式 API は含まれている？**
いいえ。easy_tdx は同じ TDX プロトコルの別のクライアントであり、新しいデータソースではありません。また #52 は HTTP で解決済みのため、PR #54 はマージしません。このプロジェクトでは、直接照会できるソースのみを統合します。THS のサービスにはユーザーキーが必要です。集合競売の統合には Python 3.10+ への対応作業が必要です。[v3.8.0](docs/source-integration-v3.8.0.md) と [v3.9.0](docs/source-integration-v3.9.0.md) の統合記録（中国語）を参照してください。V3.9 ではインストールする依存関係は増えていません。

**バックテストに使える？JoinQuant で動く？（#55）**
このスキルはデータを取得するもので、**バックテストエンジンはありません**。データは独自のフレームワークや JoinQuant に渡してください。
> - ティッカー: `norm_ticker()` / `get_prefix()` は JoinQuant のコード `600519.XSHG` / `000001.XSHE` を受け付けます。`to_joinquant()` は対応する任意の形式を JoinQuant のコードに変換します。JoinQuant の公開ドキュメントには BSE のサフィックスが記載されていないため、BSE のコードは推測せずにエラーを送出します。
> - 権利調整: JoinQuant の `get_price` はデフォルトで前方調整（`fq='pre'`）です。§1.2 `tencent_kline(adjust='qfq')` と比較するか、§1.6 の権利調整係数を自分で適用してください。
> - ルックアヘッドバイアス: 過去のバリュエーションには §6.5 を、過去の業界分類には §6.7 を使ってください。§12 の指数構成銘柄は現在のスナップショットのみです。

**リサーチレポートのソースは Eastmoney だけ？（#53）**
いいえ。§2.4 `sina_research_reports()` は 2 つ目のソースで、銘柄別または市場全体でページングでき、Eastmoney にブロックされても動作し続けます。タイトル、種類、証券会社、アナリスト、日付はありますが、レーティングや目標株価はありません。それらには Eastmoney のレポートか THS のコンセンサスを使ってください。

**商品先物やオプションはカバーされている？DCE は？（#49）**
はい。「先物・コモディティ」を参照してください。先物とオプションの公式の日次データは SHFE、INE、CZCE、CFFEX、GFEX から取得し、会員の建玉ランキングは最初の 4 つ（GFEX 以外）をカバーします。Sina のリアルタイム先物、FTSE China A50、SGE 現物も含まれます。**DCE のウェブサイトはスクリプトからのアクセスをブロックするため、公式の日次相場は統合していません**。大豆粕や鉄鉱石などの DCE の銘柄には、履歴には V3.10 の `futures_kline('M0')`（Sina、連続限月または個別限月）を、リアルタイム価格には Sina のリアルタイム先物を使ってください。

**上海上場企業で cninfo IRM の回答が空なのはなぜ？**
cninfo IRM は深セン上場企業しかカバーしておらず、上海のティッカーでは 0 行が返ります。上海には §10.3 `sse_e_interaction()`（SSE e-Interaction）を使ってください。直近 1 か月に回答が本当にない企業もあるため、空の表が正しい場合もあります。

## 検証

`python3 -m unittest discover -s tests -v` は、出荷されるコードを SKILL.md から直接抽出し、ネットワークアクセスなしで日付、フィールド、銘柄のルーティング、単位、ページング、エラーの伝播をチェックします（V3.10.4 時点でオフラインテスト 208 件、加えてデフォルトでスキップされるライブテスト 4 件）。

ライブテストはオプトインです。日付は、ソースがすでにデータを公表した取引日である必要があります:

```bash
# V3.10's tick and futures K-line entries, plus the §1.2 K-line volume-unit check (downloads one TDX end-of-day package)
ASTOCK_LIVE_V310=1 python3 -m unittest tests.test_v310_sources -v
# the 25 entries added in V3.9 (31 live calls)
ASTOCK_LIVE_V39=2026-09-18 python3 -m unittest tests.test_v39_sources -v
# the V3.8 official margin and BSE backups
ASTOCK_LIVE_TRADE_DATE=2026-09-04 ASTOCK_LIVE_MARGIN_DATE=2026-09-03 python3 -m unittest tests.test_official_data -v
```

エントリーごとの行数とデータの範囲は [v3.9.0 の統合記録](docs/source-integration-v3.9.0.md) に、V3.8 については [v3.8.0](docs/source-integration-v3.8.0.md) にあります（どちらも中国語）。

## 変更履歴

[CHANGELOG.md](./CHANGELOG.md) を参照してください。

---

## 免責事項

このプロジェクトはデータアクセスのツールのみを提供するもので、投資助言ではありません。投資にはリスクが伴います。

---

## ライセンス

[Apache License 2.0](./LICENSE)

**作者:** Simon Lin · X [@linsizhen](https://x.com/linsizhen) · Email: [simonlin0423@gmail.com](mailto:simonlin0423@gmail.com)
