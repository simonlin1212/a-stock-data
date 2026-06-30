# -*- coding: utf-8 -*-
"""
数据源适配器 V2 - 东财优先 + 智能限流防封 + 自动降级

K线优先级: 东财push2his(带限流) → 腾讯K线(前复权) → 新浪K线(降级)
股票列表: datacenter-web + 腾讯行情
实时行情: 腾讯行情API

防封机制:
  - em_get() 限流: Session复用 + 间隔≥2s + 随机抖动 + 指数退避重试
  - 封禁检测: 连续3次RemoteDisconnected → 标记EM_BANNED → 自动切换备用源
  - 并发控制: patch_module替换step3，max_workers=2

使用方式 (monkey-patch):
  import data_fallback
  data_fallback.patch_module(stock_screener)
  stock_screener.main()
"""
import requests
import time
import json
import random
import threading
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================
#  请求头
# ============================================================
_HEADERS_EM = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://quote.eastmoney.com/',
    'Accept': '*/*',
}
_HEADERS_TX = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# ============================================================
#  东财限流防封核心: em_get()
# ============================================================
# Session复用（减少TCP连接数）
_EM_SESSION = requests.Session()
_EM_SESSION.headers.update(_HEADERS_EM)
_retry_strategy = Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
_EM_SESSION.mount('https://', HTTPAdapter(max_retries=_retry_strategy, pool_connections=1, pool_maxsize=2))
_EM_SESSION.mount('http://', HTTPAdapter(max_retries=_retry_strategy, pool_connections=1, pool_maxsize=2))

# 限流参数
EM_MIN_INTERVAL = 2.0   # 东财请求最小间隔(秒)，全市场扫描建议≥2s
EM_MAX_RETRIES = 3      # 最大重试次数
EM_BAN_THRESHOLD = 3    # 连续失败N次后判定为封禁

# 全局状态（线程安全）
_em_lock = threading.Lock()
_last_em_time = 0.0
_em_fail_count = 0
_EM_BANNED = False      # 东财是否已被封禁


def _check_em_banned():
    """检查东财是否已被封禁（线程安全）"""
    return _EM_BANNED


def _mark_em_failure():
    """记录一次东财请求失败，达到阈值则标记封禁（线程安全）"""
    global _em_fail_count, _EM_BANNED
    with _em_lock:
        _em_fail_count += 1
        if _em_fail_count >= EM_BAN_THRESHOLD:
            if not _EM_BANNED:
                print(f"  [防封警告] 东财连续{_em_fail_count}次失败，自动切换到备用数据源！", flush=True)
                _EM_BANNED = True


def _mark_em_success():
    """记录一次东财请求成功，重置失败计数（线程安全）"""
    global _em_fail_count
    with _em_lock:
        _em_fail_count = 0


def em_get(url, params=None, timeout=15):
    """
    东财统一限流请求入口 - 防封核心函数
    
    特性:
      1. Session复用（减少TCP连接）
      2. 串行限流（间隔≥EM_MIN_INTERVAL + 随机抖动）
      3. 封禁检测（连续失败→自动标记封禁→后续跳过东财）
      4. 指数退避重试（1s, 2s, 4s）
    
    返回: Response对象 或 None（被封禁/请求失败）
    """
    global _last_em_time

    # 封禁检测：如果东财已被封，直接返回None
    if _check_em_banned():
        return None

    for attempt in range(EM_MAX_RETRIES):
        # 串行限流：确保请求间隔
        with _em_lock:
            now = time.time()
            elapsed = now - _last_em_time
            wait = EM_MIN_INTERVAL + random.uniform(0.1, 0.5) - elapsed
            if wait > 0:
                time.sleep(wait)
            _last_em_time = time.time()

        try:
            r = _EM_SESSION.get(url, params=params, timeout=timeout)
            # 检测封禁特征
            if r.status_code == 200 and len(r.text) > 10:
                _mark_em_success()
                return r
            else:
                _mark_em_failure()
                if _check_em_banned():
                    return None
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ChunkedEncodingError) as e:
            # 检测封禁特征: RemoteDisconnected
            err_str = str(e)
            if 'RemoteDisconnected' in err_str or 'Connection aborted' in err_str:
                _mark_em_failure()
                if attempt < EM_MAX_RETRIES - 1:
                    backoff = 2 ** attempt  # 1s, 2s, 4s
                    time.sleep(backoff)
                if _check_em_banned():
                    return None
            else:
                _mark_em_failure()
                if attempt < EM_MAX_RETRIES - 1:
                    time.sleep(1)
        except Exception:
            _mark_em_failure()
            if attempt < EM_MAX_RETRIES - 1:
                time.sleep(1)

    return None


# ============================================================
#  腾讯行情字段索引 (基于 qt.gtimg.cn 返回格式)
# ============================================================
TX_FIELD_PRICE = 3        # 当前价格
TX_FIELD_PREV_CLOSE = 4   # 昨收价
TX_FIELD_CHANGE_PCT = 32  # 涨跌幅(%)
TX_FIELD_PE = 39          # PE(动态)
TX_FIELD_TOTAL_MV = 45    # 总市值(亿元)
TX_FIELD_CIRC_MV = 44     # 流通市值(亿元)


def _tx_code(code):
    """将股票代码转为腾讯格式 (sh600000 / sz000001)"""
    if code.startswith(('6', '9')):
        return f'sh{code}'
    return f'sz{code}'


def _em_secid(code):
    """将股票代码转为东财secid格式 (1.600000 / 0.000001)"""
    if code.startswith(('6', '9')):
        return f'1.{code}'
    return f'0.{code}'


# ============================================================
#  K线获取: 东财优先 → 腾讯 → 新浪
# ============================================================
def _get_klines_eastmoney(code, days):
    """
    东财push2his获取日K线（前复权）— 通过em_get限流
    返回: list of [date, open, close, high, low, volume, amount] 或 None
    """
    if _check_em_banned():
        return None

    secid = _em_secid(code)
    fetch_count = days + 50
    url = 'https://push2his.eastmoney.com/api/qt/stock/kline/get'
    params = {
        'secid': secid,
        'fields1': 'f1,f2,f3',
        'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58',  # 日期,开,收,高,低,成交量,成交额,振幅
        'klt': '101',     # 日K
        'fqt': '1',       # 前复权
        'end': '20500101',
        'lmt': str(fetch_count),
        'ut': 'f057cbcbce2a86e2866ab8877db1d059',
    }

    r = em_get(url, params=params, timeout=15)
    if r is None:
        return None

    try:
        data = r.json()
        klines = data.get('data', {}).get('klines', [])
        if klines:
            return klines
    except Exception:
        _mark_em_failure()

    return None


def _get_klines_tencent(code, days):
    """腾讯K线API获取前复权日K线 (1次快速尝试, 失败则降级)"""
    prefix = 'sh' if code.startswith(('6', '9')) else 'sz'
    tx_symbol = f'{prefix}{code}'
    fetch_count = days + 50
    url = 'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get'

    try:
        params = {'param': f'{tx_symbol},day,,,{fetch_count},qfq'}
        r = requests.get(url, params=params, headers=_HEADERS_TX, timeout=8)
        data = r.json()
        stock_data = data.get('data', {}).get(tx_symbol, {})
        klines = stock_data.get('day', stock_data.get('qfqday', []))
        if klines:
            return klines, tx_symbol, url
    except Exception:
        pass
    return None, tx_symbol, url


def _get_klines_sina(code, days):
    """新浪K线API获取日K线 (不复权, 作为降级方案)"""
    prefix = 'sh' if code.startswith(('6', '9')) else 'sz'
    sina_symbol = f'{prefix}{code}'
    url = 'https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData'
    params = {'symbol': sina_symbol, 'scale': '240', 'datalen': str(days + 50), 'ma': 'no'}

    for attempt in range(2):
        try:
            r = requests.get(url, params=params, headers=_HEADERS_TX, timeout=12)
            if r.status_code == 200 and r.text.strip():
                data = json.loads(r.text)
                if data:
                    return data
        except Exception:
            pass
        time.sleep(0.3 * (attempt + 1))
    return None


def fallback_get_klines(code, days=60, adjust_volume=True):
    """
    获取日K线数据
    
    优先级:
      ① 东财push2his (前复权, 带em_get限流防封) — 最准确
      ② 腾讯K线 (前复权) — 东财被封/失败时降级
      ③ 新浪K线 (不复权) — 腾讯也失败时的末位降级
    
    返回格式: [{"date", "open", "close", "high", "low", "volume", "amount"}, ...]
    """
    fetch_count = days + 50

    # ① 东财push2his (优先, 带限流)
    if not _check_em_banned():
        em_klines = _get_klines_eastmoney(code, days)
        if em_klines:
            result = []
            for k in em_klines:
                parts = k.split(',')
                if len(parts) < 7:
                    continue
                try:
                    result.append({
                        'date': parts[0],
                        'open': float(parts[1]),
                        'close': float(parts[2]),
                        'high': float(parts[3]),
                        'low': float(parts[4]),
                        'volume': float(parts[5]),
                        'amount': float(parts[6]) if parts[6] else float(parts[5]) * float(parts[2]),
                    })
                except (ValueError, IndexError):
                    continue
            if result:
                return result[-days:]

    # ② 腾讯K线 (降级, 前复权)
    klines_tx, tx_symbol, tx_url = _get_klines_tencent(code, days)
    if klines_tx:
        result = []
        for k in klines_tx:
            if len(k) < 6:
                continue
            try:
                result.append({
                    'date': k[0],
                    'open': float(k[1]),
                    'close': float(k[2]),
                    'high': float(k[3]),
                    'low': float(k[4]),
                    'volume': float(k[5]),
                    'amount': float(k[5]) * float(k[2]) if float(k[2]) > 0 else 0,
                })
            except (ValueError, IndexError):
                continue

        # 成交量复权
        if adjust_volume and result:
            try:
                params_raw = {'param': f'{tx_symbol},day,,,{fetch_count},'}
                r2 = requests.get(tx_url, params=params_raw, headers=_HEADERS_TX, timeout=15)
                data2 = r2.json()
                stock_data2 = data2.get('data', {}).get(tx_symbol, {})
                klines_raw = stock_data2.get('day', stock_data2.get('qtday', []))
                if klines_raw and len(klines_raw) == len(result):
                    for i, k in enumerate(klines_raw):
                        if len(k) >= 3:
                            raw_close = float(k[2])
                            if raw_close > 0 and result[i]['close'] > 0:
                                factor = result[i]['close'] / raw_close
                                result[i]['volume'] = result[i]['volume'] * factor
                                result[i]['amount'] = result[i]['amount'] * factor
            except Exception:
                pass

        if result:
            return result[-days:]

    # ③ 新浪K线 (末位降级, 不复权)
    klines_sina = _get_klines_sina(code, days)
    if klines_sina:
        result = []
        for k in klines_sina:
            try:
                vol = float(k.get('volume', 0))
                close = float(k.get('close', 0))
                result.append({
                    'date': k.get('day', ''),
                    'open': float(k.get('open', 0)),
                    'close': close,
                    'high': float(k.get('high', 0)),
                    'low': float(k.get('low', 0)),
                    'volume': vol / 100 if vol > 1000 else vol,
                    'amount': vol * close if close > 0 else 0,
                })
            except (ValueError, TypeError):
                continue
        if result:
            return result[-days:]

    return []


# ============================================================
#  股票列表 + 实时行情
# ============================================================
def fallback_get_all_stocks():
    """
    获取全A股列表 (datacenter + 腾讯行情)
    返回: [{"code", "name", "price", "change_pct", "market_cap", "pe", "industry"}, ...]
    """
    print("  [备用数据源] datacenter-web + 腾讯行情", flush=True)

    # 步骤1: 从 datacenter 获取股票基础列表
    dc_url = 'https://datacenter-web.eastmoney.com/api/data/v1/get'
    stock_list = []
    page = 1
    seen_codes = set()

    while True:
        params = {
            'sortColumns': 'SECURITY_CODE', 'sortTypes': 1,
            'pageSize': 500, 'pageNumber': page,
            'reportName': 'RPT_LICO_FN_CPD',
            'columns': 'SECURITY_CODE,SECURITY_NAME_ABBR,SECUCODE,TRADE_MARKET,BOARD_NAME,ISNEW',
            'filter': '(ISNEW=1)'
        }
        try:
            r = requests.get(dc_url, params=params, headers=_HEADERS_EM, timeout=30)
            data = r.json().get('result', {})
            items = data.get('data', [])
        except Exception:
            items = []

        if not items:
            break

        for item in items:
            code = item.get('SECURITY_CODE', '')
            name = item.get('SECURITY_NAME_ABBR', '')
            board = item.get('BOARD_NAME', '') or ''
            if not code or not code[0].isdigit():
                continue
            if code[0] not in ('6', '0', '3'):
                continue
            if code in ('000001',) and name == '上证指数':
                continue
            if code in seen_codes:
                continue
            seen_codes.add(code)
            stock_list.append((code, name, board))

        if len(items) < 500:
            break
        page += 1
        if page % 5 == 0:
            print(f"  [datacenter] 已获取 {len(stock_list)} 只...", flush=True)

    print(f"  [datacenter] 共 {len(stock_list)} 只A股", flush=True)

    # 步骤2: 用腾讯行情API批量获取实时数据
    stocks = []
    batch_size = 60
    total_batches = (len(stock_list) + batch_size - 1) // batch_size
    code_board = {c: b for c, n, b in stock_list}

    for batch_idx in range(total_batches):
        start = batch_idx * batch_size
        end = min(start + batch_size, len(stock_list))
        batch = stock_list[start:end]

        tx_codes = [_tx_code(c) for c, n, b in batch]
        tx_url = f'http://qt.gtimg.cn/q={",".join(tx_codes)}'

        try:
            r = requests.get(tx_url, headers=_HEADERS_TX, timeout=15)
            r.encoding = 'gbk'
            text = r.text
        except Exception:
            time.sleep(0.5)
            continue

        for line in text.strip().split(';'):
            line = line.strip()
            if not line or '=' not in line:
                continue
            try:
                val = line.split('=', 1)[1].strip(';').strip('"')
                parts = val.split('~')
                if len(parts) < 50:
                    continue

                code = parts[2]
                name = parts[1]

                def _safe_float(s, default=0):
                    try:
                        return float(s) if s and s != '' else default
                    except (ValueError, TypeError):
                        return default

                price = _safe_float(parts[TX_FIELD_PRICE])
                change_pct = _safe_float(parts[TX_FIELD_CHANGE_PCT])
                total_mv_yi = _safe_float(parts[TX_FIELD_TOTAL_MV])
                market_cap = total_mv_yi * 1e8
                pe = _safe_float(parts[TX_FIELD_PE])

                stocks.append({
                    'code': code,
                    'name': name,
                    'price': price,
                    'change_pct': change_pct,
                    'market_cap': market_cap,
                    'pe': pe,
                    'industry': code_board.get(code, ''),
                })
            except Exception:
                continue

        if (batch_idx + 1) % 10 == 0:
            print(f"  [腾讯行情] 已获取 {len(stocks)}/{len(stock_list)} 只...", flush=True)
        time.sleep(0.15)

    print(f"  [腾讯行情] 共获取 {len(stocks)} 只股票实时数据", flush=True)
    return stocks


def fallback_get_stock_info(code):
    """获取个股信息 (腾讯行情API)"""
    prefix = 'sh' if code.startswith(('6', '9')) else 'sz'
    try:
        r = requests.get(f'http://qt.gtimg.cn/q={prefix}{code}', headers=_HEADERS_TX, timeout=10)
        r.encoding = 'gbk'
        parts = r.text.split('=', 1)[1].strip(';').strip('"').split('~')
        if len(parts) < 50:
            return {'sector': '', 'concepts': '', 'market_cap': 0, 'pe': 0}

        def _safe_float(s, default=0):
            try:
                return float(s) if s and s != '' else default
            except (ValueError, TypeError):
                return default

        return {
            'sector': '',
            'concepts': '',
            'market_cap': _safe_float(parts[TX_FIELD_TOTAL_MV]) * 1e8,
            'pe': _safe_float(parts[TX_FIELD_PE]),
        }
    except Exception:
        return {'sector': '', 'concepts': '', 'market_cap': 0, 'pe': 0}


def fallback_get_big_order_net(code, dates, days=120):
    """主力净流入数据 - 备用源不可用，返回空"""
    return {}


def fallback_get_risk_warnings(code):
    """风险公告 - 备用源不可用，返回空"""
    return []


# ============================================================
#  并发控制: 替换step3，max_workers=2
# ============================================================
def _make_step3_low_concurrency(ss_module):
    """
    生成一个低并发的step3函数（max_workers=2）
    替换原始的10线程版本，防止东财封禁
    
    逻辑与原step3完全一致，仅修改并发数
    """
    original_process = ss_module._process_one_stock_price_increase
    np = ss_module.np
    threading_mod = ss_module.threading
    time_mod = ss_module.time

    def step3_low_concurrency(stocks):
        result = []
        total = len(stocks)
        processed = [0]
        lock = threading_mod.Lock()

        def process_with_progress(s):
            r = original_process(s)
            with lock:
                processed[0] += 1
                idx = processed[0]
                if idx % 50 == 0 or idx == total:
                    print(f"    进度: {idx}/{total} ({idx*100//total}%) | 已筛选出: {len(result)} 只", flush=True)
            return r

        ban_status = " [东财已封禁, 使用备用源]" if _check_em_banned() else ""
        print(f"    启动2线程并行获取K线数据{ban_status}...", flush=True)
        t0 = time_mod.time()
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_stock = {
                executor.submit(process_with_progress, s): s
                for s in stocks
            }
            for future in as_completed(future_to_stock):
                res = future.result()
                if res is not None:
                    result.append(res)

        elapsed = time_mod.time() - t0
        print(f"    耗时: {elapsed:.1f}秒 | 筛选出: {len(result)} 只")
        return result

    return step3_low_concurrency


# ============================================================
#  Monkey-patch 入口
# ============================================================
def patch_module(ss_module):
    """
    Monkey-patch stock_screener 模块
    
    替换:
      - get_all_stocks → datacenter + 腾讯行情
      - get_klines → 东财(限流) → 腾讯 → 新浪 (三级降级)
      - get_stock_info → 腾讯行情
      - get_big_order_net → 空
      - get_risk_warnings → 空
      - step3_price_increase_filter → max_workers=2 (防封)
    
    防封特性:
      - 东财请求统一走em_get()限流（间隔≥2s + 随机抖动 + Session复用）
      - 连续3次RemoteDisconnected → 自动标记封禁 → 后续K线走腾讯/新浪
      - 并发从10降为2，大幅降低触发风控概率
    """
    ss_module.get_all_stocks = fallback_get_all_stocks
    ss_module.get_klines = fallback_get_klines
    ss_module.get_stock_info = fallback_get_stock_info
    ss_module.get_big_order_net = fallback_get_big_order_net
    ss_module.get_risk_warnings = fallback_get_risk_warnings

    # 替换step3为低并发版本
    if hasattr(ss_module, 'step3_price_increase_filter'):
        ss_module.step3_price_increase_filter = _make_step3_low_concurrency(ss_module)

    print("=" * 60)
    print("  数据源适配器 V2 已启用")
    print("  K线优先级: 东财(限流2s) → 腾讯 → 新浪")
    print("  并发控制: 2线程 (原10线程)")
    print("  防封机制: em_get限流 + 封禁自动检测 + 三级降级")
    print("=" * 60)
