"""Test the V3.9.0 Python shipped inside SKILL.md (marker blocks v39-*), not a second implementation.

Offline: python3 -m unittest discover -s tests -v
Live (hits 31 real endpoints, ~2 min): ASTOCK_LIVE_V39=2026-09-18 python3 -m unittest tests.test_v39_sources -v
The live date must be a trading day whose exchange files are already published.
"""

import ast
import importlib.util
import io
import json
import os
import re
import struct
import sys
import threading
import time
import types
import unittest
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests as REAL_REQUESTS

SKILL = (Path(__file__).resolve().parents[1] / "SKILL.md").read_text(encoding="utf-8")
MARKERS = ["v39-helpers", "v39-tencent-kline", "v39-tdx-package", "v39-sina-reports", "v39-etf-shares",
           "v39-wscn-lives", "v39-cctv-news", "v39-st-list", "v39-sse-e", "v39-chinabond", "v39-repo-fixing",
           "v39-lpr", "v39-macro-calendar", "v39-futures", "v39-events", "v39-cb"]
NEW_ENDPOINTS = ["tencent_kline", "tdx_daily_package", "sina_research_reports", "etf_shares",
                 "wallstreetcn_lives", "cctv_news", "st_stock_list", "sse_e_interaction",
                 "chinabond_yield_curve", "repo_fixing_rates", "lpr_history", "macro_calendar",
                 "futures_daily", "options_daily", "futures_position_rank", "futures_realtime",
                 "a50_futures", "sge_spot", "earnings_forecast", "institution_survey", "holder_trades",
                 "share_buyback", "equity_pledge", "ipo_calendar", "convertible_bonds"]


def _python_blocks():
    return re.findall(r"```python\n(.*?)```", SKILL, re.S)


def _block_defining(name):
    hits = [b for b in _python_blocks() if re.search(rf"^def {name}\(", b, re.M)]
    if len(hits) != 1:
        raise RuntimeError(f"{name}: defined in {len(hits)} blocks")
    return hits[0]


def _defs_only(src):
    """Keep imports / constants / defs of a tutorial block; drop the example calls at module level."""
    tree = ast.parse(src)
    names = {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    keep = []
    for node in tree.body:
        if isinstance(node, (ast.Expr, ast.For, ast.While, ast.With)):
            continue
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            calls = {c.func.id for c in ast.walk(node)
                     if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
            if calls & names:
                continue
        keep.append(node)
    tree.body = keep
    return compile(tree, "SKILL.md:prerequisite", "exec")


def _marker_code(marker):
    section = SKILL.split(f"<!-- {marker}:start -->", 1)[1].split(f"<!-- {marker}:end -->", 1)[0]
    return re.search(r"```python\n(.*?)\n```", section, re.S).group(1)


def _exec_with_stubs(stubs, codes, namespace):
    """Stub only modules that are not installed, and remove only those stubs afterwards.
    (patch.dict(sys.modules) would also drop requests/urllib3 imported inside the block; a later
    import then creates a second copy whose exception classes no longer match the except clauses.)"""
    added = [name for name in stubs if name not in sys.modules]
    for name in added:
        sys.modules[name] = stubs[name]
    try:
        for code in codes:
            exec(code, namespace)
    finally:
        for name in added:
            sys.modules.pop(name, None)
    return namespace


def load_shipped_code():
    # only §6.8's fallback needs baostock; offline tests never log in
    stubs = {} if importlib.util.find_spec("baostock") else {"baostock": types.ModuleType("baostock")}
    blocks = []
    for name in ("get_prefix", "norm_ticker", "to_joinquant", "em_get", "bs_session"):
        block = _block_defining(name)
        if block not in blocks:
            blocks.append(block)
    codes = [_defs_only(block) for block in blocks]
    codes += [compile(_marker_code(marker), f"SKILL.md:{marker}", "exec") for marker in MARKERS]
    return _exec_with_stubs(stubs, codes, {})


def load_tdx_client():
    fake_quotes = types.ModuleType("mootdx.quotes")
    fake_quotes.Quotes = MagicMock()
    stubs = {"mootdx": types.ModuleType("mootdx"), "mootdx.quotes": fake_quotes}
    return _exec_with_stubs(stubs, [_defs_only(_block_defining("tdx_client"))], {})


class Response:
    def __init__(self, status=200, content=b"", text=None, payload=None):
        self.status_code = status
        self.content = content
        self.text = text if text is not None else content.decode("latin-1")
        self._payload = payload
        self.url = "https://example.test/response"

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


# 与 SKILL.md 的 TDX_MIN_PRICED 相同，这里写死，不从被测代码里读（读了的话改小下限测试也不会变红）
TDX_FLOOR = {"sh": 10000, "sz": 3000, "bj": 50}


def tdx_zip(ymd, markets, counts=None, empty=(), tweak=None):
    """Synthetic 通达信 g4day package: per market a .cod (150 B/record) + .md1 (512 B/block).
    counts 默认每个市场正好等于下限；`empty` 里的市场两个文件都是 0 条；
    tweak(market, cod, md1) 可以在写入前改字节（造重复代码 / 重复序号 / 多余行情块）。"""
    counts = dict(TDX_FLOOR, **(counts or {}))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        for m_index, market in enumerate(markets):
            cod, md1 = bytearray(), bytearray()
            for seq in range(0 if market in empty else counts[market]):
                record = bytearray(150)
                record[0:6] = f"{m_index}{seq:05d}".encode()
                record[32:34] = struct.pack("<H", seq)
                name = "样本".encode("gbk")
                record[40:40 + len(name)] = name
                cod += record
                block = bytearray(512)
                block[4:12] = struct.pack("<d", 10.0)
                block[12:44] = struct.pack("<4d", 10.1, 10.5, 9.9, 10.2)
                block[56:64] = struct.pack("<Q", 1000)
                block[72:80] = struct.pack("<d", 10200.0)
                md1 += block
            if tweak:
                tweak(market, cod, md1)
            archive.writestr(f"{market}{ymd[2:]}.cod", bytes(cod))
            archive.writestr(f"{market}{ymd[2:]}.md1", bytes(md1))
    return buf.getvalue()


class ShippedCodeShapeTests(unittest.TestCase):
    def test_marker_blocks_in_order_and_all_endpoints_defined(self):
        self.assertEqual(re.findall(r"<!-- (v39-[a-z0-9-]+):start -->", SKILL), MARKERS)
        ns = load_shipped_code()
        missing = [name for name in NEW_ENDPOINTS if not callable(ns.get(name))]
        self.assertEqual(missing, [])
        self.assertEqual(len(NEW_ENDPOINTS), 25)

    def test_every_new_endpoint_is_in_route_table(self):
        table = SKILL.split("## 端点路由速查", 1)[1].split("\n## ", 1)[0]
        missing = [name for name in NEW_ENDPOINTS + ["to_joinquant"] if f"`{name}(" not in table]
        self.assertEqual(missing, [])

    def test_python39_syntax_in_new_blocks(self):
        for marker in MARKERS:
            code = _marker_code(marker)
            with self.subTest(marker=marker):
                self.assertIsNone(re.search(r"\w\s*\|\s*None\b", code), "PEP 604 union breaks Python 3.9")
                ast.parse(code, feature_version=(3, 9))

    def test_backup_sources_keep_tls_verification_enabled(self):
        self.assertNotIn("ssl.CERT_NONE", SKILL)
        self.assertNotIn("check_hostname = False", SKILL)


class ErrorContractTests(unittest.TestCase):
    """来源缺字段时 row["X"] 漏出的 KeyError 会被调用方当成「参数错 / 没这只票」。"""

    def test_every_new_endpoint_is_wrapped(self):
        for name in NEW_ENDPOINTS:
            with self.subTest(name=name):
                self.assertRegex(_block_defining(name), rf"@_v39_contract\ndef {name}\(")

    def test_missing_row_field_becomes_runtime_error(self):
        """全市场业绩预告不带筛选条件，逐行核对不生效，缺 SECURITY_CODE 就只剩 KeyError 这一层。"""
        ns = load_shipped_code()
        good = {"SECURITY_CODE": "600519", "SECURITY_NAME_ABBR": "样本",
                "REPORT_DATE": "2026-09-30 00:00:00", "NOTICE_DATE": "2026-09-18 00:00:00"}
        with patch.dict(ns, {"_em_event_rows": MagicMock(return_value=[good])}):
            self.assertEqual(ns["earnings_forecast"]().code.tolist(), ["600519"])
        broken = [{k: v for k, v in good.items() if k != "SECURITY_CODE"}]
        with patch.dict(ns, {"_em_event_rows": MagicMock(return_value=broken)}), \
                self.assertRaisesRegex(RuntimeError, "earnings_forecast.*缺少字段.*SECURITY_CODE"):
            ns["earnings_forecast"]()


class RepoFixingTests(unittest.TestCase):
    def fixing(self, text):
        ns = load_shipped_code()
        response = Response(content=text.encode("utf-8"))
        with patch.dict(ns, {"_v39_http": MagicMock(return_value=response)}):
            return ns["repo_fixing_rates"]("FR")

    def test_three_tenors_are_required(self):
        """整行为空时列数照样是 9，用 _v39_num 会返回日期有效、三个利率全 None 的行。"""
        out = self.fixing("2026-09-18,,,,,,1.43,1.48,1.46\n")
        self.assertEqual((out.FR001[0], out.FR014[0]), (1.43, 1.46))
        for line in ("2026-09-18,,,,,,,,", "2026-09-18,,,,,,1.43,,1.46",
                     "2026-09-18,,,,,,1.43,1.48,-", "2026-09-18,,,,,,1.43,1.48,x"):
            with self.subTest(line=line), self.assertRaises(RuntimeError):
                self.fixing(line + "\n")


class JoinQuantTickerTests(unittest.TestCase):
    """#55: 聚宽 .XSHG / .XSHE 代码。"""

    def setUp(self):
        self.ns = load_shipped_code()

    def test_joinquant_suffix_accepted(self):
        norm, prefix = self.ns["norm_ticker"], self.ns["get_prefix"]
        self.assertEqual((norm("600519.XSHG"), prefix("600519.XSHG")), ("600519", "sh"))
        self.assertEqual((norm("000001.xshe"), prefix("000001.XSHE")), ("000001", "sz"))
        # 000300.XSHG 是沪深300，不能按数字规则判成深市
        self.assertEqual(prefix("000300.XSHG"), "sh")

    def test_to_joinquant(self):
        to_jq = self.ns["to_joinquant"]
        self.assertEqual(to_jq("sh600519"), "600519.XSHG")
        self.assertEqual(to_jq("000001.SZ"), "000001.XSHE")
        self.assertEqual(to_jq("600519.XSHG"), "600519.XSHG")
        with self.assertRaises(ValueError):
            to_jq("920000.BJ")

    def test_bad_suffix_still_rejected(self):
        for code in ("600519.XSHX", "600519.SS", "60051"):
            with self.subTest(code=code), self.assertRaises(ValueError):
                self.ns["norm_ticker"](code)


class TdxClientTests(unittest.TestCase):
    """#52: 行情命令返回空时，财务 / F10 仍能按 finance 验活。"""

    def setUp(self):
        self.ns = load_tdx_client()

    @staticmethod
    def f10_ok(client):
        client.F10C.return_value = [{"name": "最新提示"}]           # 2026-09 起服务器只剩这一类
        client.F10.return_value = "最新提示☆ ◇000001 平安银行"

    def test_check_argument_validated_before_network(self):
        with patch.dict(self.ns, {"_probe": MagicMock(side_effect=AssertionError("network"))}):
            with self.assertRaises(ValueError):
                self.ns["tdx_client"](check="quotes")

    def test_finance_check_does_not_touch_bars(self):
        client = MagicMock()
        client.bars.side_effect = AssertionError("bars must not be used for finance check")
        client.finance.return_value = MagicMock(empty=False)
        self.f10_ok(client)
        self.assertTrue(self.ns["_validate"](client, "std", "finance"))
        client.finance.return_value = MagicMock(empty=True)
        self.assertFalse(self.ns["_validate"](client, "std", "finance"))

    def test_finance_check_requires_f10_too(self):
        """§6.2 / §7.2 的 F10 也走 finance 模式：只验财务会选中 F10 为空的服务器；
        类别表只看非空，又会放过只回别的类别、或「最新提示」正文读不出来的服务器。"""
        client = MagicMock()
        client.finance.return_value = MagicMock(empty=False)
        self.f10_ok(client)
        self.assertTrue(self.ns["_validate"](client, "std", "finance"))
        for cats in ([], [{"name": "公司概况"}], "最新提示", [None], MagicMock()):
            client.F10C.return_value = cats
            with self.subTest(cats=cats):
                self.assertFalse(self.ns["_validate"](client, "std", "finance"))
        client.F10C.return_value = [{"name": "最新提示"}]
        for text in ("", "  ", None, MagicMock()):
            client.F10.return_value = text
            with self.subTest(text=text):
                self.assertFalse(self.ns["_validate"](client, "std", "finance"))

    def test_bars_dead_finance_alive(self):
        client = MagicMock()
        client.bars.return_value = MagicMock(empty=True)          # #52 现象：K 线 0 行
        client.finance.return_value = MagicMock(empty=False)
        self.f10_ok(client)
        quotes = MagicMock()
        quotes.factory.return_value = client
        with patch.dict(self.ns, {"_probe": MagicMock(return_value=True), "Quotes": quotes}):
            self.assertIs(self.ns["tdx_client"](check="finance"), client)
            with self.assertRaises(RuntimeError) as caught:
                self.ns["tdx_client"]()
        self.assertIn("tencent_kline", str(caught.exception))
        self.assertIn("check='finance'", str(caught.exception))


class HttpHelperTests(unittest.TestCase):
    """约定：「接口坏了」一律 RuntimeError；ValueError 只留给参数错误和「确实没有数据」。"""

    def setUp(self):
        self.ns = load_shipped_code()

    def http(self, **request_kwargs):
        fake = types.SimpleNamespace(request=MagicMock(**request_kwargs),
                                     RequestException=REAL_REQUESTS.RequestException)
        with patch.dict(self.ns, {"requests": fake}):
            return self.ns["_v39_http"]("https://example.test/x", allow_status=(404,))

    def test_network_and_http_errors_become_runtime_errors(self):
        with self.assertRaises(RuntimeError):
            self.http(side_effect=REAL_REQUESTS.ConnectionError("reset"))
        bad = MagicMock(status_code=500)
        bad.raise_for_status.side_effect = REAL_REQUESTS.HTTPError("500")
        with self.assertRaises(RuntimeError):
            self.http(return_value=bad)

    def test_allowed_status_is_returned_for_caller_to_judge(self):
        missing = MagicMock(status_code=404)
        missing.raise_for_status.side_effect = AssertionError("must not raise for allowed status")
        self.assertIs(self.http(return_value=missing), missing)

    def test_em_get_serializes_concurrent_requests_and_releases_after_error(self):
        state = {"active": 0, "peak": 0, "calls": 0}
        state_lock = threading.Lock()

        class Session:
            def get(self, *args, **kwargs):
                with state_lock:
                    state["active"] += 1
                    state["peak"] = max(state["peak"], state["active"])
                    state["calls"] += 1
                    call = state["calls"]
                time.sleep(0.02)
                with state_lock:
                    state["active"] -= 1
                if call == 1:
                    raise REAL_REQUESTS.ConnectionError("first call fails")
                return call

        self.ns["EM_SESSION"] = Session()
        self.ns["EM_MIN_INTERVAL"] = 0
        errors, results = [], []

        def call():
            try:
                results.append(self.ns["em_get"]("https://example.test"))
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=call) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=2)

        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertEqual(state["peak"], 1)
        self.assertEqual(len(errors), 1)
        self.assertEqual(sorted(results), [2, 3])
        self.assertGreater(self.ns["_em_last_call"][0], 0)

    def test_non_json_is_runtime_error(self):
        with self.assertRaises(RuntimeError):
            self.ns["_v39_json"](Response(text="<html>"))

    def test_unrecognised_source_values_are_runtime_errors(self):
        self.assertEqual(self.ns["_v39_num"]("1,234.5"), 1234.5)
        self.assertIsNone(self.ns["_v39_num"]("--"))
        with self.assertRaises(RuntimeError):
            self.ns["_v39_num"]("N/A")
        self.assertEqual((self.ns["_v39_num"](0), self.ns["_v39_num"](7)), (0.0, 7.0))
        for flag in (True, False):                          # float(True)=1.0 会把格式错误写成数值
            with self.subTest(flag=flag), self.assertRaises(RuntimeError):
                self.ns["_v39_num"](flag)
        with self.assertRaises(RuntimeError):
            self.ns["_v39_src_date"]("2026/09/18")
        with self.assertRaises(ValueError):                 # 参数写错仍是 ValueError
            self.ns["_v39_date"]("2026/09/18")
        self.assertEqual(self.ns["_em_day"]("2026-09-18 00:00:00"), "2026-09-18")
        self.assertIsNone(self.ns["_em_day"](None))
        with self.assertRaises(RuntimeError):               # 只截前 10 位会把 '2026/09/18' 原样放行
            self.ns["_em_day"]("2026/09/18 00:00:00")
        self.assertEqual(self.ns["_v39_req_num"]("12.5", "close"), 12.5)
        for bad in (None, "", "-", "nan", float("inf"), True):
            with self.subTest(bad=bad), self.assertRaises(RuntimeError):
                self.ns["_v39_req_num"](bad, "close")


class WscnLivesTests(unittest.TestCase):
    def lives(self, payload):
        ns = load_shipped_code()
        with patch.dict(ns, {"_v39_http": MagicMock(return_value=Response(text="x", payload=payload))}):
            return ns["wallstreetcn_lives"]("a-stock-channel", limit=2)

    def test_malformed_payload_is_runtime_error(self):
        item = {"id": 1, "display_time": 1789358400, "content_text": " 样本 ", "score": 1, "channels": ["a-stock-channel"]}
        out = self.lives({"code": 20000, "data": {"items": [item]}})
        self.assertEqual((out.time[0], out.content[0]), ("2026-09-14 12:00:00", "样本"))
        for payload in ([item], {"code": 20000, "data": [item]}, {"code": 20000, "data": {"items": {"a": 1}}},
                        {"code": 20000, "data": {"items": {}}}, {"code": 20000, "data": {"items": ""}},
                        {"code": 20000, "data": {"items": [None]}},
                        {"code": 20000, "data": {"items": [dict(item, display_time=True)]}},
                        {"code": 20000, "data": {"items": [dict(item, display_time="1789358400")]}},
                        {"code": 20000, "data": {"items": [{"display_time": 1789358400}]}}):
            with self.subTest(payload=payload), self.assertRaises(RuntimeError):
                self.lives(payload)


    def test_channels_must_be_a_list_of_labels(self):
        """`or []` 之后 join：来源把 channels 改成字符串时 'ab' 会被拆成 'a,b'。"""
        item = {"id": 1, "display_time": 1789358400, "content_text": "样本", "score": 1}
        out = self.lives({"code": 20000, "data": {"items": [dict(item, channels=None)]}})
        self.assertEqual(out.channels[0], "")
        for channels in ("ab", {"a": 1}, [1], 0):
            with self.subTest(channels=channels), self.assertRaises(RuntimeError):
                self.lives({"code": 20000, "data": {"items": [dict(item, channels=channels)]}})


class MacroCalendarTests(unittest.TestCase):
    def test_zero_values_kept_blank_values_missing(self):
        ns = load_shipped_code()
        item = {"id": 1, "public_date": 1789358400, "country": "美国", "title": "样本", "calendar_type": "FD",
                "importance": 2, "actual": 0, "forecast": "", "previous": "0", "revised": None,
                "unit": "%", "period": "8月"}
        payload = {"code": 20000, "data": {"items": [item]}}
        http = MagicMock(return_value=Response(text="x", payload=payload))
        with patch.dict(ns, {"_v39_http": http}):
            row = ns["macro_calendar"]("2026-09-14", "2026-09-14").iloc[0]
        self.assertEqual((row.actual, row.forecast, row.previous, row.revised), (0, None, "0", None))

    def test_source_importance_must_be_one_to_four(self):
        """来源给 True / 99 会照常出表，给 "2" 还会让筛选漏出原生 TypeError。"""
        ns = load_shipped_code()
        item = {"id": 1, "public_date": 1789358400, "country": "美国", "title": "样本", "importance": 2}
        for bad in (True, 99, 0, "2", None, 2.0):
            http = MagicMock(return_value=Response(text="x", payload={
                "code": 20000, "data": {"items": [dict(item, importance=bad)]}}))
            with self.subTest(importance=bad), patch.dict(ns, {"_v39_http": http}), \
                    self.assertRaises(RuntimeError):
                ns["macro_calendar"]("2026-09-14", "2026-09-14", min_importance=1)

    def test_importance_and_country_filters_are_checked(self):
        """min_importance=5 / country 写错都会筛成空表；静默返回空表 = 用户以为那天真没数据。"""
        ns = load_shipped_code()
        item = {"id": 1, "public_date": 1789358400, "country": "美国", "title": "样本", "importance": 2}
        http = MagicMock(return_value=Response(text="x", payload={"code": 20000, "data": {"items": [item]}}))
        with patch.dict(ns, {"_v39_http": MagicMock(side_effect=AssertionError("network"))}):
            for bad in (0, 5, True, "高", 2.5):
                with self.subTest(min_importance=bad), self.assertRaises(ValueError):
                    ns["macro_calendar"]("2026-09-14", "2026-09-14", min_importance=bad)
        with patch.dict(ns, {"_v39_http": http}):
            self.assertEqual(len(ns["macro_calendar"]("2026-09-14", "2026-09-14", min_importance=2)), 1)
            for kwargs in ({"min_importance": 3}, {"country": "美"}):
                with self.subTest(**kwargs), self.assertRaises(ValueError):
                    ns["macro_calendar"]("2026-09-14", "2026-09-14", **kwargs)

    def calendar(self, pages, start, end):
        ns = load_shipped_code()
        http = MagicMock(side_effect=[Response(text="x", payload={"code": 20000, "data": {"items": items}})
                                      for items in pages])
        with patch.dict(ns, {"_v39_http": http}):
            return ns["macro_calendar"](start, end)

    def test_empty_full_past_week_is_an_error(self):
        """两周查询第二周整周为空，只返回第一周会被当成完整日历。"""
        item = {"id": 1, "public_date": 1788408000, "country": "美国", "title": "样本", "importance": 2}  # 09-03 12:00
        with self.assertRaises(RuntimeError):
            self.calendar([[item], []], "2026-09-01", "2026-09-14")

    def test_window_returning_other_dates_raises(self):
        """三个周窗口都返回同一条 09-18 的条目：按 id 去重后只剩一条，缺掉的两周被静默吞掉。"""
        item = {"id": 1, "public_date": 1789704000, "country": "美国", "title": "样本", "importance": 2}
        with self.assertRaises(RuntimeError):
            self.calendar([[item]] * 3, "2026-09-01", "2026-09-21")
        # 三周各返回一条落在别的周里的条目（id 不同）：没有重复 id，只有段内日期检查拦得住
        shifted = [[dict(item, id=i, public_date=stamp)] for i, stamp in ((1, 1789012800), (2, 1789704000), (3, 1788408000))]
        with self.assertRaises(RuntimeError):
            self.calendar(shifted, "2026-09-01", "2026-09-21")
        out = self.calendar([[item]], "2026-09-18", "2026-09-18")
        self.assertEqual(out.time.tolist(), ["2026-09-18 12:00"])

    def test_range_limit_is_92_dates_inclusive(self):
        ns = load_shipped_code()
        with patch.dict(ns, {"_v39_http": MagicMock(side_effect=AssertionError("network"))}):
            with self.assertRaises(ValueError):
                ns["macro_calendar"]("2026-06-01", "2026-09-01")      # 相差 92 天 = 93 个日期
            with self.assertRaises(AssertionError):                  # 92 个日期：通过校验、开始请求
                ns["macro_calendar"]("2026-06-01", "2026-08-31")

    def test_duplicate_id_raises(self):
        """同一个 id 两条（时间不同）：按 id 存会只留后一条，2 条变 1 条且不报错。"""
        first = {"id": 7, "public_date": 1789358400, "country": "美国", "title": "样本", "importance": 2}
        second = dict(first, public_date=1789362000, title="样本（改）")
        with self.assertRaises(RuntimeError):
            self.calendar([[first, second]], "2026-09-14", "2026-09-14")
        out = self.calendar([[first, dict(second, id=8)]], "2026-09-14", "2026-09-14")
        self.assertEqual(len(out), 2)

    def test_malformed_items_are_runtime_errors(self):
        for items in ({"a": 1}, [None], [{"id": 1, "public_date": True}], [{"public_date": 1789358400}],
                      [{"id": 1, "public_date": "1789358400"}]):
            with self.subTest(items=items), self.assertRaises(RuntimeError):
                self.calendar([items], "2026-09-14", "2026-09-14")

    def test_empty_single_day_or_far_future_is_no_data(self):
        with self.assertRaises(ValueError):
            self.calendar([[]], "2026-09-19", "2026-09-19")      # 实测这个周六 0 条
        far = date.today() + timedelta(days=60)
        with self.assertRaises(ValueError):
            self.calendar([[]], far.isoformat(), (far + timedelta(days=6)).isoformat())


class TdxPackageTests(unittest.TestCase):
    def setUp(self):
        self.ns = load_shipped_code()

    def fetch(self, response, day="2026-09-18"):
        with patch.dict(self.ns, {"_v39_http": MagicMock(return_value=response)}):
            return self.ns["tdx_daily_package"](day)

    def test_parses_all_three_markets(self):
        out = self.fetch(Response(content=tdx_zip("20260918", ["sh", "sz", "bj"])))
        self.assertEqual(out.market.value_counts().to_dict(), TDX_FLOOR)
        row = out.iloc[0]
        self.assertEqual((row.close, row.high, row.volume, row.amount), (10.2, 10.5, 1000, 10200.0))
        self.assertEqual(set(out.date), {"2026-09-18"})
        self.assertEqual(set(out.source), {"tdx"})

    def test_early_2022_package_without_bse_files(self):
        out = self.fetch(Response(content=tdx_zip("20220104", ["sh", "sz"])), "2022-01-04")
        self.assertEqual(sorted(out.market.unique()), ["sh", "sz"])

    def test_recent_package_without_bse_files_is_an_error(self):
        """2022-05-06 起的包都带北交所；缺了只返回沪深会被当成全市场。"""
        with self.assertRaises(RuntimeError):
            self.fetch(Response(content=tdx_zip("20260918", ["sh", "sz"])))
        out = self.fetch(Response(content=tdx_zip("20220505", ["sh", "sz"])), "2022-05-05")
        self.assertEqual(sorted(out.market.unique()), ["sh", "sz"])

    def test_missing_shanghai_or_shenzhen_is_an_error(self):
        with self.assertRaises(RuntimeError):
            self.fetch(Response(content=tdx_zip("20260918", ["sh", "bj"])))

    def test_market_files_present_but_empty_is_an_error(self):
        """只查文件名、只看总行数时，空的北交所文件会被沪深 13000 行盖过去。"""
        with self.assertRaises(RuntimeError):
            self.fetch(Response(content=tdx_zip("20260918", ["sh", "sz", "bj"], empty=("bj",))))

    def test_bad_name_bytes_or_blank_name_is_an_error(self):
        """decode('gbk', 'replace') 会把坏字节变成「�」当成正常名称（11 个真实包实测零替换字符、零空名称）。"""
        def bad_bytes(market, cod, md1):
            if market == "sh":
                cod[40:44] = b"\xff\xfe\xff\xfe"

        def blank(market, cod, md1):
            if market == "sh":
                cod[40:72] = bytes(32)
        for tweak in (bad_bytes, blank):
            with self.subTest(tweak=tweak.__name__), self.assertRaises(RuntimeError):
                self.fetch(Response(content=tdx_zip("20260918", ["sh", "sz", "bj"], tweak=tweak)))

    def test_each_market_below_its_floor_is_an_error(self):
        """沪 600 + 深 600 + 京 1 这种残缺包不能当全市场返回：每个市场少一条都要报错。"""
        for market in ("sh", "sz", "bj"):
            with self.subTest(market=market), self.assertRaises(RuntimeError):
                self.fetch(Response(content=tdx_zip("20260918", ["sh", "sz", "bj"],
                                                    counts={market: TDX_FLOOR[market] - 1})))

    def test_duplicate_code_blank_code_or_seq_is_an_error(self):
        def dup_code(market, cod, md1):
            if market == "sh":
                cod[150:156] = cod[0:6]

        def dup_seq(market, cod, md1):
            if market == "sz":
                cod[150 + 32:150 + 34] = cod[32:34]     # 条数与块数仍相等，只有序号重复

        def blank_code(market, cod, md1):
            if market == "bj":
                cod[0:6] = bytes(6)

        def extra_block(market, cod, md1):
            if market == "sh":
                md1 += bytes(512)

        for tweak in (dup_code, dup_seq, blank_code, extra_block):
            with self.subTest(tweak=tweak.__name__), self.assertRaises(RuntimeError):
                self.fetch(Response(content=tdx_zip("20260918", ["sh", "sz", "bj"],
                                                    counts={"sh": 10001, "sz": 3001, "bj": 51},
                                                    tweak=tweak)))

    def test_non_digit_code_or_non_finite_value_is_an_error(self):
        """坏字节按 replace 解码会变成 '\ufffd00000' 放行；NaN 收盘价能绕过 close <= 0 被计入下限。"""
        def bad_byte(market, cod, md1):
            if market == "sh":
                cod[0:1] = b"\xff"

        def letter(market, cod, md1):
            if market == "sz":
                cod[0:6] = b"00000A"

        def nan_close(market, cod, md1):
            if market == "sh":
                md1[36:44] = struct.pack("<d", float("nan"))

        def inf_amount(market, cod, md1):
            if market == "bj":
                md1[72:80] = struct.pack("<d", float("inf"))

        def nan_in_unpriced_block(market, cod, md1):     # 收盘价为 0 的块同样要检查
            if market == "sz":
                md1[4:44] = struct.pack("<5d", float("nan"), 0.0, 0.0, 0.0, 0.0)

        for tweak in (bad_byte, letter, nan_close, inf_amount, nan_in_unpriced_block):
            with self.subTest(tweak=tweak.__name__), self.assertRaises(RuntimeError):
                self.fetch(Response(content=tdx_zip("20260918", ["sh", "sz", "bj"],
                                                    counts={"sh": 10001, "sz": 3001, "bj": 51},
                                                    tweak=tweak)))

    def test_404_is_value_error_and_error_page_is_runtime_error(self):
        with self.assertRaises(ValueError):
            self.fetch(Response(status=404))
        with self.assertRaises(RuntimeError):
            self.fetch(Response(content=b"<html>error</html>"))

    def test_corrupt_zip_is_runtime_error(self):
        """以 PK 开头但压缩包坏了（下载被截断），不能漏出 zipfile.BadZipFile。"""
        good = tdx_zip("20260918", ["sh", "sz", "bj"])
        for content in (b"PK\x03\x04broken", good[:len(good) // 2]):
            with self.subTest(size=len(content)), self.assertRaises(RuntimeError):
                self.fetch(Response(content=content))


class TencentKlineTests(unittest.TestCase):
    def setUp(self):
        self.ns = load_shipped_code()
        self.ns["_tencent_host_down_until"].clear()

    def kline(self, rows):
        return Response(text="x", payload={"code": 0, "data": {"sh600519": {"qfqday": rows}}})

    def test_empty_response_fails_over_to_next_host(self):
        http = MagicMock(side_effect=[Response(text=""), self.kline([["2026-09-18", "10", "11", "12", "9", "100"]])])
        with patch.dict(self.ns, {"_v39_http": http}):
            out = self.ns["tencent_kline"]("600519", count=1)
        self.assertEqual(out.close.tolist(), [11.0])
        hosts = [call.args[0] for call in http.call_args_list]
        self.assertTrue(hosts[0].startswith(self.ns["TENCENT_KLINE_HOSTS"][0]))
        self.assertTrue(hosts[1].startswith(self.ns["TENCENT_KLINE_HOSTS"][1]))
        self.assertIn(self.ns["TENCENT_KLINE_HOSTS"][0], self.ns["_tencent_host_down_until"])
        self.assertEqual(set(out.source_url), {self.ns["TENCENT_KLINE_HOSTS"][1] + "/appstock/app/fqkline/get"})

    def test_network_error_fails_over_to_next_host(self):
        http = MagicMock(side_effect=[RuntimeError("timeout"),
                                      self.kline([["2026-09-18", "10", "11", "12", "9", "100"]])])
        with patch.dict(self.ns, {"_v39_http": http}):
            out = self.ns["tencent_kline"]("600519", count=1)
        self.assertEqual(out.close.tolist(), [11.0])

    def test_all_hosts_empty_raises(self):
        http = MagicMock(return_value=Response(text=""))
        with patch.dict(self.ns, {"_v39_http": http}), self.assertRaises(RuntimeError):
            self.ns["tencent_kline"]("600519", count=1)

    def test_unparseable_row_is_runtime_error(self):
        http = MagicMock(return_value=self.kline([["2026-09-18", "N/A", "11", "12", "9", "100"]]))
        with patch.dict(self.ns, {"_v39_http": http}), self.assertRaises(RuntimeError):
            self.ns["tencent_kline"]("600519", count=1)

    def test_window_without_period_key_is_an_error(self):
        """分段取数时某一段缺 qfqday/day，不能当成 0 根跳过、只返回其余几段。"""
        calls = []

        def http(url, params=None, **kwargs):
            calls.append(params["param"])
            if len(calls) == 1:
                node = {"qfqday": [["2020-01-02", "10", "11", "12", "9", "100"]]}
            elif len(calls) == 2:
                node = {}
            else:
                node = {"qfqday": []}
            return Response(text="x", payload={"code": 0, "data": {"sh600519": node}})
        with patch.dict(self.ns, {"_v39_http": MagicMock(side_effect=http)}), self.assertRaises(RuntimeError):
            self.ns["tencent_kline"]("600519", start="2020-01-01", end="2026-09-18")
        self.assertEqual(len(calls), 2)

    def test_unadjusted_key_and_empty_windows_are_fine(self):
        """从未除权的标的只有 day；上市前的窗口是空列表，都不算错。"""
        def http(url, params=None, **kwargs):
            end = params["param"].split(",")[3]
            rows = [["2026-09-18", "10", "11", "12", "9", "100"]] if end == "2026-09-18" else []
            return Response(text="x", payload={"code": 0, "data": {"sh600519": {"day": rows}}})
        with patch.dict(self.ns, {"_v39_http": MagicMock(side_effect=http)}):
            out = self.ns["tencent_kline"]("600519", start="2020-01-01", end="2026-09-18")
        self.assertEqual(out.close.tolist(), [11.0])

    def test_empty_adjusted_key_with_raw_rows_raises(self):
        """某段 qfqday 为空、day 有数据：拿 day 顶上会把原始价标成 qfq；不理它又会静默少一段。"""
        row = ["2026-09-18", "10", "11", "12", "9", "100"]

        def http(url, params=None, **kwargs):
            end = params["param"].split(",")[3]
            node = ({"qfqday": [row]} if end == "2026-09-18"
                    else {"qfqday": [], "day": [["2025-01-02", "10", "11", "12", "9", "100"]]})
            return Response(text="x", payload={"code": 0, "data": {"sh600519": node}})
        with patch.dict(self.ns, {"_v39_http": MagicMock(side_effect=http)}), self.assertRaises(RuntimeError):
            self.ns["tencent_kline"]("600519", start="2024-01-01", end="2026-09-18")    # 两段：~2025-11-30 / ~2026-09-18
        http = MagicMock(return_value=Response(text="x", payload={"code": 0, "data": {"sh600519": {"day": [row]}}}))
        with patch.dict(self.ns, {"_v39_http": http}):                  # 没有复权 key（从未除权）才用 day
            self.assertEqual(self.ns["tencent_kline"]("600519", count=1).close.tolist(), [11.0])

    def test_window_rows_outside_window_raise(self):
        """每段都回同一根 2026-09-18（缓存错页）：只按总区间过滤会静默返回 1 根。"""
        http = MagicMock(return_value=self.kline([["2026-09-18", "10", "11", "12", "9", "100"]]))
        with patch.dict(self.ns, {"_v39_http": http}), self.assertRaises(RuntimeError):
            self.ns["tencent_kline"]("600519", start="2020-01-01", end="2026-09-18")
        # 第一段拿到第二段的日子、第二段为空：没有重复日期，只有段内日期检查拦得住
        http = MagicMock(side_effect=[self.kline([["2026-09-18", "10", "11", "12", "9", "100"]]), self.kline([])])
        with patch.dict(self.ns, {"_v39_http": http}), self.assertRaises(RuntimeError):
            self.ns["tencent_kline"]("600519", start="2024-01-01", end="2026-09-18")
        self.assertEqual(http.call_count, 1)

    def test_non_positive_adjusted_price_rejected(self):
        http = MagicMock(return_value=self.kline([["2015-01-05", "-117.6", "-110", "-100", "-120", "100"]]))
        with patch.dict(self.ns, {"_v39_http": http}), self.assertRaises(RuntimeError):
            self.ns["tencent_kline"]("600519", count=1)

    def test_non_dict_payload_tries_every_host(self):
        """顶层变成数组时 payload.get 会漏出 AttributeError，且不会再试另外两个入口。"""
        http = MagicMock(return_value=Response(text="x", payload=[{"day": []}]))
        with patch.dict(self.ns, {"_v39_http": http}), self.assertRaises(RuntimeError):
            self.ns["tencent_kline"]("600519", count=1)
        self.assertEqual(http.call_count, len(self.ns["TENCENT_KLINE_HOSTS"]))

    def test_minute_payload_without_period_list_is_runtime_error(self):
        """报错要指明缺的是 m5 列表：只断言 RuntimeError 的话，逐行解析的异常转换也能让测试过。"""
        for node in ({}, {"m5": None}, []):
            http = MagicMock(return_value=Response(text="x", payload={"code": 0, "data": {"sh600519": node}}))
            with self.subTest(node=node), patch.dict(self.ns, {"_v39_http": http}), \
                    self.assertRaisesRegex(RuntimeError, "没有 m5 列表"):
                self.ns["tencent_kline"]("600519", period="m5", count=5)

    def test_bool_nan_or_blank_price_is_runtime_error(self):
        """float() 会把 true 读成 1.0、把 'nan' 放进结果；日线和分钟线都要拒。"""
        for bad in (True, "nan", "", None):
            day_row = ["2026-09-18", bad, "11", "12", "9", "100"]
            with self.subTest(bad=bad, period="day"), self.assertRaises(RuntimeError), \
                    patch.dict(self.ns, {"_v39_http": MagicMock(return_value=self.kline([day_row]))}):
                self.ns["tencent_kline"]("600519", count=1)
            minute = Response(text="x", payload={"code": 0, "data": {"sh600519": {
                "m5": [["202609181500", "10", "11", "12", "9", bad]]}}})
            with self.subTest(bad=bad, period="m5"), self.assertRaises(RuntimeError), \
                    patch.dict(self.ns, {"_v39_http": MagicMock(return_value=minute)}):
                self.ns["tencent_kline"]("600519", period="m5", count=1)

    def test_short_or_non_list_row_is_runtime_error(self):
        """行变短 / 变成 null / 变成对象都是源格式变了，日线和分钟线都要转成 RuntimeError，不能漏出原生异常。"""
        for bad in (["2026-09-18", "10", "11"], None, {}):
            with self.subTest(bad=bad, period="day"), self.assertRaisesRegex(RuntimeError, "行格式改变"), \
                    patch.dict(self.ns, {"_v39_http": MagicMock(return_value=self.kline([bad]))}):
                self.ns["tencent_kline"]("600519", count=1)
            minute = Response(text="x", payload={"code": 0, "data": {"sh600519": {"m5": [bad]}}})
            with self.subTest(bad=bad, period="m5"), self.assertRaisesRegex(RuntimeError, "行格式改变"), \
                    patch.dict(self.ns, {"_v39_http": MagicMock(return_value=minute)}):
                self.ns["tencent_kline"]("600519", period="m5", count=1)

    def test_duplicate_date_or_minute_raises(self):
        """同一天 / 同一分钟两根不同的 K 线，只保留后一条会静默换掉收盘价。"""
        rows = [["2026-09-17", "10", "11", "12", "9", "100"], ["2026-09-17", "10", "13", "14", "9", "100"]]
        with patch.dict(self.ns, {"_v39_http": MagicMock(return_value=self.kline(rows))}):
            with self.assertRaises(RuntimeError):
                self.ns["tencent_kline"]("600519", count=2)
        bars = [["202609181455", "10", "11", "12", "9", "100", {}, "50"],
                ["202609181455", "10", "13", "14", "9", "100", {}, "50"]]
        payload = {"code": 0, "data": {"sh600519": {"m5": bars}}}
        with patch.dict(self.ns, {"_v39_http": MagicMock(return_value=Response(text="x", payload=payload))}):
            with self.assertRaises(RuntimeError):
                self.ns["tencent_kline"]("600519", period="m5", count=2)

    def test_argument_errors_before_network(self):
        http = MagicMock(side_effect=AssertionError("network"))
        with patch.dict(self.ns, {"_v39_http": http}):
            for kwargs in ({"period": "m5", "adjust": "qfq"}, {"period": "m5", "count": 321},
                           {"period": "day", "count": 641}, {"period": "year"},
                           {"start": "2026-09-18", "end": "2026-01-01"}, {"end": "2026-09-18"}):
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    self.ns["tencent_kline"]("600519", **kwargs)
            for code in ("920021", "bj920982", "430047.BJ"):     # 腾讯对北交所只给最新 1 根
                with self.subTest(code=code), self.assertRaises(ValueError):
                    self.ns["tencent_kline"](code, count=5)


class SinaReportTests(unittest.TestCase):
    def test_bse_code_sent_with_bj_prefix(self):
        """新浪只认 bj920982；只给数字会返回「没有找到」空页，看起来像该股没有研报。"""
        ns = load_shipped_code()
        page = MagicMock(return_value=(MagicMock(url="https://sina.example"),
                                       "<table class=tb_01>研究员</table>没有找到相关内容.."))
        with patch.dict(ns, {"_sina_report_page": page}):
            for code, expected in (("920982", "bj920982"), ("920982.BJ", "bj920982"), ("sh600519", "600519")):
                ns["sina_research_reports"](code)
                self.assertEqual(page.call_args.args[1]["symbol"], expected)

    ROW = ('<tr><td>{n}</td><td class="tal f14"><a target="_blank" title="样本研报{n}" '
           'href="//stock.finance.sina.com.cn/stock/go.php/vReport_Show/kind/search/rptid/80{n}/index.phtml">'
           '样本</a></td><td>公司</td><td>2026-09-18</td><td><a href="#">某证券</a></td><td>张三</td></tr>')

    def reports(self, body):
        ns = load_shipped_code()
        page = MagicMock(return_value=(MagicMock(url="https://sina.example"),
                                       f"<table class=tb_01><tr><th>研究员</th></tr>{body}</table>"))
        with patch.dict(ns, {"_sina_report_page": page}):
            return ns["sina_research_reports"](page=2)

    def test_rows_must_all_parse_and_empty_needs_not_found_note(self):
        """第 2 页起、行结构改了（序号不一定是 1）也要报错；0 行只认「没有找到相关内容」。"""
        out = self.reports(self.ROW.format(n=1) + self.ROW.format(n=2))
        self.assertEqual(out.report_id.tolist(), ["801", "802"])
        self.assertTrue(self.reports("没有找到相关内容..").empty)
        changed = '<tr><td>7</td><td class="title-v2"><a href="/r/807">新版</a></td></tr>'
        for body in (changed, self.ROW.format(n=1) + changed, ""):
            with self.subTest(body=body), self.assertRaises(RuntimeError):
                self.reports(body)


class EastmoneyStrictTests(unittest.TestCase):
    """「确实没有」(9201 → []) 与「接口坏了」(其他错误码 → 抛错) 必须分开。"""

    def setUp(self):
        self.ns = load_shipped_code()

    def run_strict(self, payload, sort=("A", "-1")):
        em = MagicMock(return_value=Response(text="x", payload=payload))
        with patch.dict(self.ns, {"em_get": em}):
            return self.ns["_em_datacenter_strict"]("RPT_X", "", sort[0], sort[1])

    def test_9201_is_empty_other_codes_raise(self):
        self.assertEqual(self.run_strict({"code": 9201, "message": "返回数据为空"}), [])
        with self.assertRaises(RuntimeError):
            self.run_strict({"code": 9501, "message": "排序字段错误"})
        with self.assertRaises(RuntimeError):
            self.run_strict({"code": 0, "result": None})

    def test_sort_count_mismatch_rejected_before_network(self):
        with self.assertRaises(ValueError):
            self.run_strict({"code": 0}, sort=("A,B", "-1"))

    def paged(self, *results, **kwargs):
        pages = [Response(text="x", payload=r if "code" in r else {"code": 0, "result": r}) for r in results]
        em = MagicMock(side_effect=pages)
        with patch.dict(self.ns, {"em_get": em}):
            return self.ns["_em_datacenter_strict"]("RPT_X", page_size=kwargs.pop("page_size", 1), **kwargs), em

    def test_partial_pagination_raises(self):
        """第 2 页起出错不能把第 1 页当完整结果返回。"""
        first = {"pages": 2, "count": 2, "data": [{"i": 1}]}
        for second in ({"code": 9201, "message": "返回数据为空"}, {"pages": 2, "count": 2, "data": []}):
            with self.subTest(second=second), self.assertRaises(RuntimeError):
                self.paged(first, second)
        for missing in ({"count": 1, "data": [{"i": 1}]}, {"pages": 1, "data": [{"i": 1}]}):
            with self.subTest(missing=missing), self.assertRaises(RuntimeError):
                self.run_strict({"code": 0, "result": missing})             # 缺 pages / count

    def test_empty_first_page_of_many_or_changed_page_count_raises(self):
        """第 1 页 pages=2 却是空的、或翻页中总页数变了，都不能返回部分结果。"""
        for first, second in (({"pages": 2, "count": 2, "data": []}, {"pages": 2, "count": 2, "data": [{"i": 2}]}),
                              ({"pages": 2, "count": 2, "data": [{"i": 1}]}, {"pages": 3, "count": 2, "data": [{"i": 2}]}),
                              # 总条数中途变了、最后又恰好对上新总数：不固定首屏 count 就会放过
                              ({"pages": 2, "count": 1, "data": [{"i": 1}]}, {"pages": 2, "count": 2, "data": [{"i": 2}]})):
            with self.subTest(first=first, second=second), self.assertRaises(RuntimeError):
                self.paged(first, second)
        self.assertEqual(self.run_strict({"code": 0, "result": {"pages": 1, "count": 0, "data": []}}), [])

    def test_short_page_or_count_mismatch_raises(self):
        """每页只回 1 条、总数却报 1000 时，只看 pages 会把 2 条当成完整结果。"""
        short = {"pages": 2, "count": 1000, "data": [{"i": 1}]}
        with self.assertRaises(RuntimeError):
            self.paged(short, dict(short, data=[{"i": 2}]), page_size=500)
        with self.assertRaises(RuntimeError):                               # 总数对得上、但中间页不满页（翻页错位）
            self.paged({"pages": 2, "count": 3, "data": [{"i": 1}]},
                       {"pages": 2, "count": 3, "data": [{"i": 2}, {"i": 3}]}, page_size=2)
        with self.assertRaises(RuntimeError):                               # 单页也要对上总数
            self.run_strict({"code": 0, "result": {"pages": 1, "count": 5, "data": [{"i": 1}]}})
        rows, em = self.paged(*[{"pages": 3, "count": 3, "data": [{"i": i}]} for i in (1, 2, 3)], max_rows=2)
        self.assertEqual((rows, em.call_count), ([{"i": 1}, {"i": 2}], 2))  # 截到 max_rows 就停，不算不完整

    def test_max_rows_does_not_skip_the_completeness_check(self):
        """达到 max_rows 就返回，会把「一页给的比 count 还多」「count 没超上限却还有下一页」当成正常截断。"""
        with self.assertRaises(RuntimeError):       # pages=1 count=1，却给了 500 行
            self.paged({"pages": 1, "count": 1, "data": [{"i": i} for i in range(500)]},
                       page_size=500, max_rows=500)
        with self.assertRaises(RuntimeError):       # count=500 未超上限：必须翻到第 2 页，空页要报错
            self.paged({"pages": 2, "count": 500, "data": [{"i": i} for i in range(500)]},
                       {"pages": 2, "count": 500, "data": []}, page_size=500, max_rows=500)
        rows, em = self.paged({"pages": 2, "count": 501, "data": [{"i": i} for i in range(500)]},
                              page_size=500, max_rows=500)      # count 确实超上限才截断
        self.assertEqual((len(rows), em.call_count), (500, 1))

    def test_transport_errors_are_runtime_not_value_errors(self):
        """JSON 解析错误是 ValueError 子类，不转换就会被当成「确实没有数据」。"""
        with self.assertRaises(RuntimeError):
            self.run_strict(None)                                           # 非 JSON 错误页
        em = MagicMock(side_effect=REAL_REQUESTS.ConnectionError("reset"))
        with patch.dict(self.ns, {"em_get": em}), self.assertRaises(RuntimeError):
            self.ns["_em_datacenter_strict"]("RPT_X")

    def test_malformed_structure_is_runtime_error(self):
        """payload / result 不是对象、data 不是对象列表：不能把字典键当成行、也不能漏出 TypeError。"""
        for payload in ([], {"code": 0, "result": [1]},
                        {"code": 0, "result": {"pages": 1, "count": 1, "data": {"only": "not-a-row"}}},
                        {"code": 0, "result": {"pages": 1, "count": 1, "data": ["x"]}}):
            with self.subTest(payload=payload), self.assertRaises(RuntimeError):
                self.run_strict(payload)

    def test_pagination_stops_at_last_page(self):
        rows, em = self.paged({"pages": 2, "count": 2, "data": [{"i": 1}]}, {"pages": 2, "count": 2, "data": [{"i": 2}]})
        self.assertEqual((rows, em.call_count), ([{"i": 1}, {"i": 2}], 2))


class ConvertibleBondTests(unittest.TestCase):
    def setUp(self):
        self.ns = load_shipped_code()

    def rows(self):
        past = (date.today() - timedelta(days=30)).isoformat() + " 00:00:00"
        future = (date.today() + timedelta(days=30)).isoformat() + " 00:00:00"
        base = {"SECURITY_NAME_ABBR": "样本转债", "TRANSFER_PRICE": "10", "CURRENT_BOND_PRICE": "120",
                "TRADE_MARKET": "CNSESH", "PUBLIC_START_DATE": past}
        return [dict(base, SECURITY_CODE="110001", LISTING_DATE=past, DELIST_DATE=None),
                dict(base, SECURITY_CODE="110002", LISTING_DATE=None, DELIST_DATE=None),
                dict(base, SECURITY_CODE="110003", LISTING_DATE=past, DELIST_DATE=past),
                dict(base, SECURITY_CODE="110004", LISTING_DATE=past, DELIST_DATE=future),
                dict(base, SECURITY_CODE="110005", LISTING_DATE=future, DELIST_DATE=None)]

    def call(self, rows, **kwargs):
        with patch.dict(self.ns, {"_em_datacenter_strict": MagicMock(return_value=rows)}):
            return self.ns["convertible_bonds"](**kwargs)

    def test_status_uses_delist_date_relative_to_today(self):
        out = self.call(self.rows())
        self.assertEqual(dict(zip(out.code, out.status)),
                         {"110001": "listed", "110002": "upcoming", "110004": "listed", "110005": "upcoming"})
        full = self.call(self.rows(), include_delisted=True)
        self.assertEqual(full.set_index("code").status["110003"], "delisted")

    def test_delisting_board_and_undeterminable_rows(self):
        """退市板块 404xxx 东财不填上市/摘牌日，不能被当成 upcoming；判断不了的标 unknown。"""
        base = self.rows()[0]
        rows = [dict(base, SECURITY_CODE="404005", TRADE_MARKET="STAS00", LISTING_DATE=None, PUBLIC_START_DATE=None),
                dict(base, SECURITY_CODE="110006", LISTING_DATE=None, PUBLIC_START_DATE=None),
                dict(base, SECURITY_CODE="110007", TRADE_MARKET="XXXX00")]
        self.assertEqual(dict(zip(*[self.call(rows)[c] for c in ("code", "status")])),
                         {"110006": "unknown", "110007": "unknown"})
        full = self.call(rows, include_delisted=True)
        self.assertEqual(full.set_index("code").status["404005"], "delisted")

    def test_empty_and_duplicate_raise(self):
        with self.assertRaises(RuntimeError):
            self.call([])
        with self.assertRaises(RuntimeError):
            self.call(self.rows()[:1] * 2)


class ExplicitIndexTickerTests(unittest.TestCase):
    """sh000001 / 000001.XSHG 是上证指数；归一化成 000001 会查到平安银行。"""

    def test_event_and_interaction_endpoints_reject_sh_index(self):
        ns = load_shipped_code()
        guard = MagicMock(side_effect=AssertionError("network"))
        with patch.dict(ns, {"_em_event_rows": guard, "_v39_http": guard, "_em_datacenter_strict": guard}):
            for code in ("sh000001", "000001.XSHG", "000016.SH"):
                for call in (lambda: ns["_em_event_filter"](code), lambda: ns["share_buyback"](code),
                             lambda: ns["equity_pledge"](code), lambda: ns["sse_e_interaction"](code)):
                    with self.subTest(code=code), self.assertRaises(ValueError):
                        call()
        self.assertEqual(ns["_em_event_filter"]("sz000001"), '(SECURITY_CODE="000001")')


class EquityPledgeTests(unittest.TestCase):
    def test_bse_code_rejected_not_empty(self):
        """质押统计只覆盖沪深；北交所返回空表会被误读成「没有质押」。"""
        ns = load_shipped_code()
        rows = MagicMock(side_effect=AssertionError("network"))
        with patch.dict(ns, {"_em_event_rows": rows}):
            for code in ("920982", "bj430047"):
                with self.subTest(code=code), self.assertRaises(ValueError):
                    ns["equity_pledge"](code)


    def test_code_and_date_together_rejected(self):
        """两个都给时旧代码静默丢掉 date，返回该股历次记录。"""
        ns = load_shipped_code()
        with patch.dict(ns, {"_em_event_rows": MagicMock(side_effect=AssertionError("network"))}):
            with self.assertRaises(ValueError):
                ns["equity_pledge"]("600519", date="2026-09-18")


class EventFilterVerifyTests(unittest.TestCase):
    """服务端忽略筛选或回了缓存错页时，返回行要逐行核对；每个坏样本只改一处。"""

    def setUp(self):
        self.ns = load_shipped_code()

    def call(self, rows, fn, *args, **kwargs):
        with patch.dict(self.ns, {"_em_datacenter_strict": MagicMock(return_value=rows)}):
            return self.ns[fn](*args, **kwargs)

    def check(self, fn, good, bad_fields, *args, **kwargs):
        self.assertEqual(len(self.call([good], fn, *args, **kwargs)), 1)
        for field, value in bad_fields:
            with self.subTest(fn=fn, field=field), self.assertRaises(RuntimeError):
                self.call([dict(good, **{field: value})], fn, *args, **kwargs)

    def test_rows_must_match_requested_filters(self):
        self.check("earnings_forecast",
                   {"SECURITY_CODE": "600519", "REPORT_DATE": "2026-09-30 00:00:00"},
                   [("SECURITY_CODE", "000001"), ("REPORT_DATE", "2019-12-31 00:00:00")],
                   "600519", report_date="2026-09-30")
        self.check("institution_survey",
                   {"SECURITY_CODE": "600519", "NOTICE_DATE": "2026-09-10 00:00:00", "IS_SOURCE": "1", "NUMBERNEW": "1"},
                   [("SECURITY_CODE", "000001"), ("NOTICE_DATE", "2026-08-31 00:00:00"),
                    ("NOTICE_DATE", "2026-09-19 00:00:00"), ("IS_SOURCE", "0"), ("NUMBERNEW", "2")],
                   "600519", start="2026-09-01", end="2026-09-18")
        self.check("holder_trades",
                   {"SECURITY_CODE": "600519", "NOTICE_DATE": "2026-09-10 00:00:00", "DIRECTION": "减持",
                    "HOLDER_NAME": "股东"},
                   [("SECURITY_CODE", "000001"), ("NOTICE_DATE", "2026-09-19 00:00:00"), ("DIRECTION", "增持")],
                   "600519", direction="减持", start="2026-09-01", end="2026-09-18")
        self.check("share_buyback", {"DIM_SCODE": "600519", "REPURPROGRESS": "004"},
                   [("DIM_SCODE", "000001"), ("REPURPROGRESS", "006")], "600519", progress="实施中")
        self.check("equity_pledge", {"SECURITY_CODE": "600519", "TRADE_DATE": "2026-09-18 00:00:00"},
                   [("SECURITY_CODE", "000001")], "600519")
        self.check("equity_pledge", {"SECURITY_CODE": "600519", "TRADE_DATE": "2026-09-18 00:00:00"},
                   [("TRADE_DATE", "2026-09-11 00:00:00")], date="2026-09-18")

    def test_start_after_end_rejected_before_network(self):
        guard = MagicMock(side_effect=AssertionError("network"))
        with patch.dict(self.ns, {"_em_datacenter_strict": guard}):
            for fn in ("institution_survey", "holder_trades"):
                with self.subTest(fn=fn), self.assertRaises(ValueError):
                    self.ns[fn](start="2026-09-18", end="2026-09-01")


class FuturesArgumentTests(unittest.TestCase):
    def setUp(self):
        self.ns = load_shipped_code()

    def test_dce_rejected_with_pointer_to_realtime(self):
        with patch.dict(self.ns, {"_v39_http": MagicMock(side_effect=AssertionError("network"))}):
            for fn in ("futures_daily", "options_daily"):
                with self.subTest(fn=fn), self.assertRaises(ValueError) as caught:
                    self.ns[fn]("2026-09-18", "DCE")
                self.assertIn("futures_realtime", str(caught.exception))
            with self.assertRaises(ValueError):
                self.ns["futures_daily"]("2026-09-18", "NYMEX")

    def test_realtime_rejects_empty_or_non_list_symbols(self):
        """空列表会去请求空代码串，返回只有溯源列的空表。"""
        with patch.dict(self.ns, {"_v39_http": MagicMock(side_effect=AssertionError("network"))}):
            for symbols in ([], (), set(), 5, None):
                with self.subTest(symbols=symbols), self.assertRaises(ValueError):
                    self.ns["futures_realtime"](symbols)


class EtfSharesSseTests(unittest.TestCase):
    def fetch(self, result, total, day="2026-09-18"):
        ns = load_shipped_code()
        payload = {"result": result, "pageHelp": {"total": total, "pageSize": 2000, "pageCount": 1}}
        if total == "no-pageHelp":
            del payload["pageHelp"]
        with patch.dict(ns, {"_v39_http": MagicMock(return_value=Response(text="x", payload=payload))}):
            return ns["_etf_shares_sse"](day)

    def test_row_count_must_match_page_help_total(self):
        """服务端每页最多 2000 条；只回 1 条而 total=912 时不能当完整快照。"""
        rec = {"STAT_DATE": "2026-09-18", "SEC_CODE": "510300", "SEC_NAME": "样本ETF", "TOT_VOL": "1,234.5"}
        rows, _ = self.fetch([rec, dict(rec, SEC_CODE="510500")], 2)
        self.assertEqual([r["code"] for r in rows], ["510300", "510500"])
        with self.assertRaises(ValueError):                     # 非交易日：result 空、total 0
            self.fetch([], 0, "2026-09-19")
        for result, total in (([rec], 912), ([rec], True), ([rec], None), ([], 3), ([rec, "x"], 2),
                              ([{"STAT_DATE": "2026-09-18"}], 1), ([rec], "no-pageHelp"),
                              ([dict(rec, TOT_VOL="")], 1), ([dict(rec, TOT_VOL="-")], 1)):
            with self.subTest(total=total, n=len(result)), self.assertRaises(RuntimeError):
                self.fetch(result, total)


class EtfSharesSzseTests(unittest.TestCase):
    def setUp(self):
        self.ns = load_shipped_code()

    def page(self, data, pagecount=2, recordcount=2, subname="2026-09-18"):
        rec = {"sys_key": "<u>159001</u>", "jjjcurl": "<u>样本ETF</u>", "dqgm": "<a>1,234.5</a>"}
        meta = {"subname": subname, "pagecount": pagecount, "recordcount": recordcount}
        return Response(text="x", payload=[{"metadata": meta, "data": [dict(rec) for _ in range(data)]}])

    def fetch(self, *pages):
        with patch.dict(self.ns, {"_v39_http": MagicMock(side_effect=list(pages)),
                                  "time": types.SimpleNamespace(sleep=lambda s: None)}):
            return self.ns["_etf_shares_szse"]("2026-09-18")

    def test_complete_pages_match_record_count(self):
        rows, _ = self.fetch(self.page(1), self.page(1))
        self.assertEqual(len(rows), 2)

    def test_unparsable_shares_is_an_error(self):
        """份额是核心指标，认不出就报错，不能返回一列 None。"""
        rec = {"sys_key": "<u>159001</u>", "jjjcurl": "<u>样本ETF</u>", "dqgm": "<a>,</a>"}
        meta = {"subname": "2026-09-18", "pagecount": 2, "recordcount": 2}
        broken = Response(text="x", payload=[{"metadata": meta, "data": [rec]}])
        with self.assertRaises(RuntimeError):
            self.fetch(broken, self.page(1))

    def test_empty_page_or_count_mismatch_raises(self):
        with self.assertRaises(RuntimeError):
            self.fetch(self.page(1), self.page(0))            # 第 2 页空：只返回第 1 页就是部分快照
        with self.assertRaises(RuntimeError):                 # 总数也跟着少报时，只有空页检查拦得住
            self.fetch(self.page(1, recordcount=1), self.page(0, recordcount=1))
        with self.assertRaises(RuntimeError):
            self.fetch(self.page(1, recordcount=3), self.page(1, recordcount=3))

    def test_snapshot_changing_between_pages_raises(self):
        """翻页途中快照换了（总数 / 页数 / 日期），拼出来的是两份快照的混合。"""
        first = self.page(100, pagecount=2, recordcount=150)
        for second in (self.page(20, pagecount=2, recordcount=120), self.page(50, pagecount=3, recordcount=150),
                       self.page(50, pagecount=2, recordcount=150, subname="2026-09-21")):
            with self.subTest(meta=second._payload[0]["metadata"]), self.assertRaises(RuntimeError):
                self.fetch(first, second)
        with self.assertRaises(ValueError):                   # 第 1 页日期不符才是「深市只有当前快照」
            self.fetch(self.page(1, subname="2026-09-17"))

    def test_missing_snapshot_date_is_a_source_error(self):
        """subname 缺失被当成「快照日期是 None，不是 2026-09-18」= 把结构损坏说成用户要了历史日期。"""
        for subname in (None, "", "2026/09/18", 20260918.0, True):
            with self.subTest(subname=subname), self.assertRaises(RuntimeError):
                self.fetch(self.page(1, pagecount=1, recordcount=1, subname=subname))
        rows, _ = self.fetch(self.page(1, pagecount=1, recordcount=1, subname="20260918"))
        self.assertEqual(len(rows), 1)              # 同一天的另一种写法仍算当天

    def test_paging_fields_must_be_real_counts(self):
        """JSON 布尔值 int(True)=1：只给 1 条也能通过完整性核对。"""
        for kwargs in ({"pagecount": True, "recordcount": True}, {"pagecount": 0, "recordcount": 1},
                       {"pagecount": 1, "recordcount": "-1"}, {"pagecount": 1.0, "recordcount": 1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(RuntimeError):
                self.fetch(self.page(1, **kwargs))
        rows, _ = self.fetch(self.page(1, pagecount="1", recordcount="1"))
        self.assertEqual(len(rows), 1)

    def test_malformed_top_level_is_runtime_error(self):
        for payload in ([], {}, [None], [{"data": []}], [{"metadata": {}, "data": None}], [{"metadata": [], "data": []}]):
            with self.subTest(payload=payload), self.assertRaises(RuntimeError):
                self.fetch(Response(text="x", payload=payload))
        rec_missing = self.page(1, pagecount=1, recordcount=1)
        rec_missing._payload[0]["data"][0].pop("dqgm")
        with self.assertRaises(RuntimeError):
            self.fetch(rec_missing)


class SseCompanyListTests(unittest.TestCase):
    def setUp(self):
        self.ns = load_shipped_code()

    def lookup(self, *payloads):
        pages = [Response(text="x", payload=p) for p in payloads]
        self.ns["_sse_uid_cache"].clear()
        self.ns["_sse_company_pages"].clear()
        with patch.dict(self.ns, {"_v39_http": MagicMock(side_effect=pages)}):
            return self.ns["_sse_company_uid"]("600519")

    def test_structure_change_is_not_reported_as_missing_company(self):
        """content 改名或第 1 页解析不出公司，是源坏了，不能说成「上证e互动没有这家公司」。"""
        for payload in ({"renamed_content": "x"}, {"content": None}, [], {"content": "<div>改版了</div>"},
                        {"content": "<font color='red'>没有任何上市公司的信息</font>"}):   # 第 1 页就「没有」：列表坏了
            with self.subTest(payload=payload), self.assertRaises(RuntimeError):
                self.lookup(payload)

    def test_found_and_past_end_pages(self):
        item = "<a href='x?uid={uid}'><img src='/company/{code}.png'></a>"
        page1 = {"content": item.format(uid=11, code="600000") + item.format(uid=12, code="600519")}
        self.assertEqual(self.lookup(page1), "12")
        end = {"content": "<font color='red'>没有任何上市公司的信息</font>"}     # 末页之后的真实返回
        with self.assertRaises(ValueError):                    # 列表正常、确实没有这家 → ValueError
            self.lookup({"content": item.format(uid=11, code="600000")}, end)
        for later in ({"content": "<div>改版了</div>"}, {"content": ""}):   # 后面的页改版：不是「公司不存在」
            with self.subTest(later=later), self.assertRaises(RuntimeError):
                self.lookup({"content": item.format(uid=11, code="600000")}, later)


def sse_item(item_id="123", qtime="2026年09月18日 10:20", atime="2026年09月19日 09:00", answered=True):
    """一条完整的上证e互动问答（问题段 + 可选回复段），结构照实测页面。"""
    html = (f'<div class="m_feed_item m_qa_item" id="item-{item_id}">'
            '<div class="m_feed_detail m_qa_detail">'
            '<div class="m_feed_txt"><a href="#">:浦发银行(600000)</a>问题内容</div>'
            '<img rel="face" title="投资者" />'
            f'<div class="m_feed_from"><span>{qtime}</span></div></div>')
    if answered:
        html += ('<div class="m_feed_detail m_qa">'
                 '<div class="m_feed_txt">回复内容</div>'
                 + (f'<div class="m_feed_from"><span>{atime}</span></div>' if atime else "")
                 + '</div>')
    return html + '</div>'


class SseFeedTests(unittest.TestCase):
    def feed(self, html, code=None):
        ns = load_shipped_code()
        stubs = {"_v39_http": MagicMock(return_value=Response(content=html.encode("utf-8"))),
                 "_sse_company_uid": MagicMock(return_value="12")}
        with patch.dict(ns, stubs):
            return ns["sse_e_interaction"](code)

    def test_item_id_and_times_must_parse(self):
        """时间认不出必须报错，不能变成一列 None；但真时间（含「昨天 18:22」和 ISO 写法）要认，不能当格式变了。
        实测 2026-10-23：回复时间是相对写法，提问时间是绝对写法，两种并存。"""
        out = self.feed(sse_item())
        self.assertEqual((out.id[0], out.code[0], out.question_time[0], out.answer_time[0]),
                         ("123", "600000", "2026-09-18 10:20", "2026-09-19 09:00"))
        iso = self.feed(sse_item(qtime="2026-09-18 10:20", atime="2026-09-19 09:00"))
        self.assertEqual((iso.question_time[0], iso.answer_time[0]), ("2026-09-18 10:20", "2026-09-19 09:00"))
        rel = self.feed(sse_item(atime="昨天 18:22"))
        self.assertRegex(rel.answer_time[0], r"^\d{4}-\d{2}-\d{2} 18:22$")
        for html in (sse_item(item_id="abc"), sse_item(qtime="时间待定"),
                     sse_item(atime="稍后"), sse_item(atime="")):
            with self.subTest(html=html[:80]), self.assertRaises(RuntimeError):
                self.feed(html)

    def test_empty_only_with_explicit_note(self):
        """0 条只在有「暂无 / 暂时没有」提示时才算真没有；只凭 currentPage 字样会把改版页当成空结果。"""
        note = '<div class="center"><a href="javascript:;" class="m_feed_note">{}</a></div>'
        self.assertTrue(self.feed(note.format("暂时没有问答内容")).empty)       # 全市场翻过末页
        self.assertTrue(self.feed(note.format("近1个月暂无回复"), "600519").empty)
        for html in ('<div class="qa_card" data-id="9">新版问答</div><input name="currentPage" value="1">',
                     "", note.format("加载更多")):
            with self.subTest(html=html), self.assertRaises(RuntimeError):
                self.feed(html)


class StListTests(unittest.TestCase):
    def test_empty_bse_universe_is_an_error_and_urls_kept(self):
        ns = load_shipped_code()
        shsz = [{"f12": "600001", "f13": 1, "f14": "*ST样本", "f2": 1.0, "f3": 0.5}]
        bj = [{"f12": "920001", "f13": 0, "f14": "ST北交", "f2": 2.0, "f3": 0.1}]
        with patch.dict(ns, {"_em_clist_all": MagicMock(side_effect=[(shsz, "https://a"), ([], "https://a")])}):
            with self.assertRaises(RuntimeError):
                ns["st_stock_list"]()
        with patch.dict(ns, {"_em_clist_all": MagicMock(side_effect=[(shsz, "https://a"), (bj, "https://b")])}):
            out = ns["st_stock_list"]()
        self.assertEqual(sorted(out.code), ["600001", "920001"])
        self.assertEqual(set(out.source_url), {"https://a | https://b"})

    def test_identity_fields_must_be_well_formed(self):
        """f13 缺失 / 变样按深市处理 = 返回错误市场；名称为空则北交所那半边被静默筛掉，仍标「沪深京」。"""
        ns = load_shipped_code()
        good_sh = {"f12": "600001", "f13": 1, "f14": "*ST样本", "f2": 1.0, "f3": 0.5}
        good_bj = {"f12": "920001", "f13": 0, "f14": "ST北交", "f2": 2.0, "f3": 0.1}
        for bad in ({"f13": 0}, {"f13": None}, {"f13": "1"}, {"f13": True}, {"f13": 2},
                    {"f14": ""}, {"f14": "  "}, {"f12": "60001"}, {"f12": None}):
            rec = dict(good_sh, **bad)
            with self.subTest(bad=bad), patch.dict(ns, {"_em_clist_all": MagicMock(
                    side_effect=[([rec], "https://a"), ([good_bj], "https://a")])}):
                if bad == {"f13": 0}:               # 真的是深市：照常出表，market 跟着变
                    self.assertEqual(ns["st_stock_list"]().market.tolist(), ["sz", "bj"])
                    continue
                with self.assertRaises(RuntimeError):
                    ns["st_stock_list"]()
        for missing in ("f12", "f13", "f14"):       # 字段整个没有：统一契约要求 RuntimeError
            rec = {k: v for k, v in good_sh.items() if k != missing}
            with self.subTest(missing=missing), patch.dict(ns, {"_em_clist_all": MagicMock(
                    side_effect=[([rec], "https://a"), ([good_bj], "https://a")])}), \
                    self.assertRaises(RuntimeError):
                ns["st_stock_list"]()

    def test_clist_diff_must_be_a_list_of_objects(self):
        """`data.get('diff') or []` 会把 {} / '' 当成空页，静默少一页。"""
        ns = load_shipped_code()
        for diff in ({}, "", 0, [1]):
            page = Response(text="x", payload={"rc": 0, "data": {"total": 1, "diff": diff}})
            with self.subTest(diff=diff), patch.dict(ns, {"em_get": MagicMock(return_value=page)}), \
                    self.assertRaises(RuntimeError):
                ns["_em_clist_all"]("m:1", "f12")

    def test_clist_total_changing_between_pages_raises(self):
        """第 1 页报 150、第 2 页改报 120 并只给 20 条时，和最后一页的 total 比会被当成完整。"""
        ns = load_shipped_code()

        def page(total, n):
            return Response(text="x", payload={"rc": 0, "data": {"total": total, "diff": [{"f12": "x"}] * n}})
        with patch.dict(ns, {"em_get": MagicMock(side_effect=[page(150, 100), page(120, 20)])}):
            with self.assertRaises(RuntimeError):
                ns["_em_clist_all"]("m:1", "f12")
        with patch.dict(ns, {"em_get": MagicMock(side_effect=[page(120, 100), page(120, 0)])}):
            with self.assertRaises(RuntimeError):                 # 第 2 页空了：100 条不是完整名单
                ns["_em_clist_all"]("m:1", "f12")
        with patch.dict(ns, {"em_get": MagicMock(side_effect=[page(120, 100), page(120, 20)])}):
            rows, _ = ns["_em_clist_all"]("m:1", "f12")
        self.assertEqual(len(rows), 120)

    def test_clist_malformed_paging_is_runtime_error(self):
        """total=true 经 int() 变成 1，只给 1 条就能过完整性核对；diff 不是列表也不能漏出原生异常。"""
        ns = load_shipped_code()
        for payload in ({"rc": 0, "data": {"total": True, "diff": [{"f12": "x"}]}},
                        {"rc": 0, "data": {"total": 1, "diff": {"0": {"f12": "x"}}}},
                        {"rc": 0, "data": {"total": 1, "diff": ["x"]}}, [], {"rc": 0, "data": [1]}):
            with self.subTest(payload=payload), self.assertRaises(RuntimeError):
                with patch.dict(ns, {"em_get": MagicMock(return_value=Response(text="x", payload=payload))}):
                    ns["_em_clist_all"]("m:1", "f12")


    def test_only_network_failure_falls_back_to_baostock(self):
        """两个域都返回 HTML 错误页是源故障（RuntimeError），不能当成连不上、退到只有沪深的备胎。"""
        ns = load_shipped_code()
        fallback = MagicMock(return_value="baostock")
        html = MagicMock(return_value=Response(text="<html>blocked</html>"))
        with patch.dict(ns, {"em_get": html, "_st_list_baostock": fallback}):
            with self.assertRaises(RuntimeError):
                ns["st_stock_list"]()
        fallback.assert_not_called()
        down = MagicMock(side_effect=REAL_REQUESTS.ConnectionError("refused"))
        with patch.dict(ns, {"em_get": down, "_st_list_baostock": fallback}):
            self.assertEqual(ns["st_stock_list"](), "baostock")
        self.assertEqual(down.call_count, 2)


_KEEP = object()      # 夹具里区分「不传 data」和「传了 {} / '' / 0」


class FuturesCompletenessTests(unittest.TestCase):
    def setUp(self):
        self.ns = load_shipped_code()

    def test_missing_ine_reference_file_is_an_error_after_its_first_day(self):
        """能源中心对照文件缺了还当空集合，上期所结果里会混进 sc 等能源合约。"""
        shfe_json = MagicMock(return_value=(None, "https://www.ine.cn/x"))
        with patch.dict(self.ns, {"_shfe_json": shfe_json}):
            for path, ok_day, bad_day in (("future/dailydata/kx", "20180323", "20180326"),
                                          ("future/dailydata/pm", "20200702", "20200703"),
                                          ("option/dailydata/kx", "20210618", "20210621")):
                with self.subTest(path=path):
                    self.assertEqual(self.ns["_shfe_ine_ids"](path, ok_day, "k", "f"), set())
                    with self.assertRaises(RuntimeError):
                        self.ns["_shfe_ine_ids"](path, bad_day, "k", "f")

    RANK_HEAD = ["交易日", "合约", "排名", "成交量排名", "", "", "持买单量排名", "", "", "持卖单量排名", "", ""]
    RANK_SUB = ["", "", "", "会员简称", "成交量", "比上一交易日增减", "会员简称", "持买单量", "比上一交易日增减",
                "会员简称", "持卖单量", "比上一交易日增减"]

    def rank_table(self, ymd, product):
        return [list(self.RANK_HEAD), list(self.RANK_SUB),
                [ymd, product + "2610", "1", "会员A", "100", "1", "会员B", "200", "2", "会员C", "300", "3"]]

    def test_cffex_rank_header_checked_and_old_layout_parsed(self):
        parse = self.ns["_cffex_rank_rows"]
        row = ["20260918", "IF2610", "1", "会员A", "100", "1", "会员B", "200", "2", "会员C", "300", "3"]
        out = parse(self.rank_table("20260918", "IF"), "IF", "20260918")
        self.assertEqual((out[0]["long_member"], out[0]["short_member"]), ("会员B", "会员C"))
        swapped = list(self.RANK_SUB)
        swapped[6:9], swapped[9:12] = swapped[9:12], swapped[6:9]      # 多空两组对调
        head = list(self.RANK_HEAD)
        head[6], head[9] = head[9], head[6]
        for table in ([self.RANK_HEAD, swapped, row], [head, self.RANK_SUB, row],
                      [row], [self.RANK_HEAD, self.RANK_SUB, row[:9]], [self.RANK_HEAD],
                      [self.RANK_HEAD, self.RANK_SUB, ["20260917"] + row[1:]]):          # 文件里的交易日不是请求日
            with self.subTest(table=table), self.assertRaises(RuntimeError):
                parse(table, "IF", "20260918")
        # 2015 年的旧文件：排名段前面先有一段「会员类别」合计
        old = [["交易日", "合约", "会员类别", "总成交量", "比上交易日增减", "总持买单量", "比上交易日增减",
                "总持卖单量", "比上一交易日增减"],
               ["20150415", "IF1504   ", "期货公司", "2855132", "42848", "58631", "-26977", "58631", "-26977"], [],
               list(self.RANK_HEAD), list(self.RANK_SUB),
               ["20150415", "IF1504   ", "1", "会员A", "100", "1", "会员B", "200", "2", "会员C", "300", "3"]]
        out = parse(old, "IF", "20150415")
        self.assertEqual([(r["symbol"], r["rank"]) for r in out], [("IF1504", 1)])

    def gfex(self, param, data=_KEEP):
        payload = {"code": "0", "param": param,
                   "data": [{"variety": "工业硅", "delivMonth": "2611", "close": "9000"}] if data is _KEEP else data}
        with patch.dict(self.ns, {"_v39_http": MagicMock(return_value=Response(text="x", payload=payload))}):
            return self.ns["_gfex_rows"]("20260918", 0)

    def test_gfex_request_echo_checked(self):
        rows, _ = self.gfex({"trade_date": ["20260918"], "trade_type": ["0"]})
        self.assertEqual(len(rows), 1)
        for param in ({"trade_date": ["20260917"], "trade_type": ["0"]}, {"trade_date": ["20260918"], "trade_type": ["1"]},
                      {}, None):
            with self.subTest(param=param), self.assertRaises(RuntimeError):
                self.gfex(param)

    def test_gfex_structure_checked(self):
        """data 是对象、行不是对象、param 不是对象，都要 RuntimeError，不能漏出 AttributeError。"""
        good = {"trade_date": ["20260918"], "trade_type": ["0"]}
        for data in ({"a": 1}, [1], ["x"]):
            with self.subTest(data=data), self.assertRaises(RuntimeError):
                self.gfex(good, data=data)
        with self.assertRaises(RuntimeError):
            self.gfex(["20260918", "0"])
        # 实测只有小计 / 总计行没有 delivMonth：字段改名时不能把合约行全部滤掉、报成非交易日
        with self.assertRaises(RuntimeError):
            self.gfex(good, data=[{"variety": "工业硅", "month": "2611"}, {"variety": "总计"}])
        with self.assertRaises(ValueError):                     # 非交易日只剩一行总计
            self.gfex(good, data=[{"variety": "总计", "varietyOrder": ""}])
        rows, _ = self.gfex(good, data=[{"variety": "工业硅", "delivMonth": "2611"}, {"variety": "工业硅小计"}])
        self.assertEqual(len(rows), 1)

    def sge(self, payload):
        with patch.dict(self.ns, {"_v39_http": MagicMock(return_value=Response(text="x", payload=payload))}):
            return self.ns["sge_spot"]("Au99.99")

    def test_sge_structure_and_values_checked(self):
        """无成交填 0 照旧剔除；顶层是数组、行不是数组、空值 / NaN / 布尔值都要 RuntimeError。"""
        good = [["2026-09-17", 930.0, 935.0, 929.0, 936.0], ["2026-09-18", 937.0, 947.09, 935.5, 948.9]]
        out = self.sge({"time": good + [["2026-09-19", 0, 0, 0, 0]]})
        self.assertEqual(out.close.tolist(), [935.0, 947.09])
        for payload in (good, {"time": {"a": 1}}, {"time": [dict(zip("abcde", good[0]))]},
                        {"time": good + [["2026-09-19", None, 1, 1, 1]]},
                        {"time": good + [["2026-09-19", float("nan"), 1, 1, 1]]},
                        {"time": good + [["2026-09-19", True, 1, 1, 1]]}):
            with self.subTest(payload=str(payload)[:60]), self.assertRaises(RuntimeError):
                self.sge(payload)

    def test_falsy_containers_are_not_empty_tables(self):
        """`or []` / `or {}` 会把 {} / '' / 0 洗成空表：广期所会报成非交易日，上期所期权会丢掉整列 IV。"""
        good = {"trade_date": ["20260918"], "trade_type": ["0"]}
        for data in ({}, "", 0):
            with self.subTest(data=data), self.assertRaises(RuntimeError):
                self.gfex(good, data=data)
        option = {"o_curinstrument": [{"INSTRUMENTID": "au2612C560", "OPTIONSTYPE": "1", "PRODUCTID": "au_o",
                                       "UNDERLYINGINSTRID": "au2612", "STRIKEPRICE": 560, "OPENPRICE": 1,
                                       "HIGHESTPRICE": 1, "LOWESTPRICE": 1, "CLOSEPRICE": 1,
                                       "SETTLEMENTPRICE": 1, "PRESETTLEMENTPRICE": 1, "VOLUME": 1,
                                       "OPENINTEREST": 1, "OPENINTERESTCHG": 0, "TURNOVER": 1, "DELTA": 0.5}]}
        for sigma in ({}, "", 0, {"a": 1}, [1], [{"SIGMA": 0.2}]):
            payload = dict(option, o_cursigma=sigma)
            stub = MagicMock(return_value=(payload, "https://x"))
            with self.subTest(sigma=sigma), patch.dict(self.ns, {"_shfe_json": stub}), \
                    self.assertRaises(RuntimeError):
                self.ns["options_daily"]("2026-09-18", "SHFE")

    def test_sigma_rows_must_be_unique_and_complete(self):
        """字典推导让重复 INSTRUMENTID 互相覆盖，返回的是最后一行的隐含波动率。
        2026-09-20 抽查 10 个交易日：只有按品种汇总的「小计」行重复且 SIGMA 为空。"""
        inst = {"INSTRUMENTID": "au2612C560", "OPTIONSTYPE": "1", "PRODUCTID": "au_o",
                "UNDERLYINGINSTRID": "au2612", "STRIKEPRICE": 560, "OPENPRICE": 1,
                "HIGHESTPRICE": 1, "LOWESTPRICE": 1, "CLOSEPRICE": 1, "SETTLEMENTPRICE": 1,
                "PRESETTLEMENTPRICE": 1, "VOLUME": 1, "OPENINTEREST": 1, "OPENINTERESTCHG": 0,
                "TURNOVER": 1, "DELTA": 0.5}
        summary = {"INSTRUMENTID": "小计", "SIGMA": "", "PRODUCTID": "au_o"}

        def call(sigma_rows):
            stub = MagicMock(return_value=({"o_curinstrument": [inst], "o_cursigma": sigma_rows}, "https://x"))
            with patch.dict(self.ns, {"_shfe_json": stub,                 # 能源中心品种表另走一次请求
                                      "_shfe_ine_ids": MagicMock(return_value=set())}):
                return self.ns["options_daily"]("2026-09-18", "SHFE")

        out = call([{"INSTRUMENTID": "au2612", "SIGMA": 0.2}, summary])   # 小计行照常跳过
        self.assertEqual(out.series_iv_pct.tolist(), [20.0])
        for sigma_rows in ([{"INSTRUMENTID": "au2612", "SIGMA": 0.2}, {"INSTRUMENTID": "au2612", "SIGMA": 0.9}],
                           [{"INSTRUMENTID": " ", "SIGMA": 0.2}, {"INSTRUMENTID": "au2612", "SIGMA": 0.2}],
                           [{"INSTRUMENTID": "au2612", "SIGMA": ""}],
                           [{"INSTRUMENTID": "au2612", "SIGMA": None}],
                           [{"INSTRUMENTID": "ag2612", "SIGMA": 0.2}],   # 主表的系列没有 sigma 行
                           [summary]):
            with self.subTest(sigma=sigma_rows), self.assertRaises(RuntimeError):
                call(sigma_rows)

    def test_czce_rank_header_without_code_is_an_error(self):
        """表头认不出品种时 re.search(...).group(0) 会漏出 AttributeError。"""
        head = "品种：{}　日期：2026-09-18"
        body = "\n名次|会员|成交量|增减|会员|持买单量|增减|会员|持卖单量|增减\n1|华泰|100|1|银河|200|2|国泰|300|3\n"
        with patch.dict(self.ns, {"_czce_text": MagicMock(return_value=(head.format("SR") + body, "https://x"))}):
            out = self.ns["futures_position_rank"]("2026-09-18", "CZCE")
        self.assertEqual((out.symbol[0], out["rank"][0], out.long_member[0]), ("SR", 1, "银河"))
        with patch.dict(self.ns, {"_czce_text": MagicMock(return_value=(head.format("2026") + body, "https://x"))}):
            with self.assertRaises(RuntimeError):
                self.ns["futures_position_rank"]("2026-09-18", "CZCE")

    def test_product_letters_must_parse(self):
        """合约代码取品种字母用的是 re.match(...).group(0)，认不出会漏出 AttributeError。"""
        self.assertEqual(self.ns["_fut_product"]("rb2610"), "rb")
        for code in ("2610", "", "-RB"):
            with self.subTest(code=code), self.assertRaises(RuntimeError):
                self.ns["_fut_product"](code)

    def test_sina_page_without_variables_is_a_format_change(self):
        """代码不存在时新浪回的是空内容的变量；一个变量都没有是页面变了，不能报成「代码不存在」。"""
        page = Response(content='var hq_str_nf_RB0="";'.encode("gbk"))
        with patch.dict(self.ns, {"_v39_http": MagicMock(return_value=page)}):
            with self.assertRaises(ValueError):
                self.ns["futures_realtime"]("RB0")
        with patch.dict(self.ns, {"_v39_http": MagicMock(return_value=Response(content=b"<html>404</html>"))}):
            with self.assertRaises(RuntimeError):
                self.ns["futures_realtime"]("RB0")

    def rank(self, day, tables):
        csv_mock = MagicMock(side_effect=lambda url, allow_missing=False: tables.get(url.split("/")[-1].split("_")[0]))
        with patch.dict(self.ns, {"_cffex_csv": csv_mock}):
            return self.ns["futures_position_rank"](day, "CFFEX"), csv_mock

    def test_cffex_listed_product_missing_is_an_error(self):
        with self.assertRaises(RuntimeError):
            self.rank("2026-09-18", {"IF": self.rank_table("20260918", "IF")})
        tables = {p: self.rank_table("20150415", p) for p in ("IF", "TF")}
        tables["T"] = [["header"], ["header"]]                      # 文件在但一行都没有
        with self.assertRaises(RuntimeError):
            self.rank("2015-04-15", tables)

    def test_shfe_json_structure_checked(self):
        """顶层是数组、行列表不是由对象组成，都要 RuntimeError，不能漏出 AttributeError / TypeError。"""
        def load(body, key="o_cursor", allow_missing=False):
            response = Response(content=json.dumps(body).encode("utf-8"))
            with patch.dict(self.ns, {"_v39_http": MagicMock(return_value=response)}):
                return self.ns["_shfe_json"]("SHFE", "future/dailydata/pm", "20260918", key, allow_missing)

        good = {"o_cursor": [{"INSTRUMENTID": "cu2610"}], "report_date": "20260918"}
        self.assertEqual(load(good)[0], good)
        self.assertIsNone(load({"o_cursor": []}, allow_missing=True)[0])      # 能源中心 2019 年的空壳
        for body in ([good], {"o_cursor": {"a": 1}, "report_date": "20260918"},
                     {"o_cursor": [1], "report_date": "20260918"}, {"report_date": "20260918"}):
            with self.subTest(body=body), self.assertRaises(RuntimeError):
                load(body)
        sigma = {"o_curinstrument": [], "o_cursigma": [["cu2611", 0.2]], "report_date": "20260918"}
        with patch.dict(self.ns, {"_shfe_json": MagicMock(return_value=(sigma, "https://www.ine.cn/x"))}):
            with self.assertRaises(RuntimeError):
                self.ns["options_daily"]("2026-09-18", "INE")

    def test_shfe_rank_without_rank_field_is_an_error(self):
        payload = {"o_cursor": [{"INSTRUMENTID": "sc2610", "RANK": ""}]}
        with patch.dict(self.ns, {"_shfe_json": MagicMock(return_value=(payload, "https://www.ine.cn/x"))}):
            with self.assertRaises(RuntimeError):
                self.ns["futures_position_rank"]("2026-09-18", "INE")

    def test_cffex_only_requests_products_listed_that_day(self):
        tables = {p: self.rank_table("20150415", p) for p in ("IF", "TF", "T")}
        out, csv_mock = self.rank("2015-04-15", tables)            # IH/IC 次日才上市
        requested = sorted(c.args[0].split("/")[-1].split("_")[0] for c in csv_mock.call_args_list)
        self.assertEqual(requested, ["IF", "T", "TF"])
        self.assertEqual(sorted(out.symbol), ["IF2610", "T2610", "TF2610"])
        self.assertNotIn("{", out.source_url.iloc[0])
        self.assertEqual(out.source_url.iloc[0].count("cffex.com.cn"), 3)
        with self.assertRaises(ValueError):                           # 非交易日：全部缺
            self.rank("2026-09-19", {})
        with self.assertRaises(ValueError):                           # IF 上市之前
            self.rank("2010-04-15", {})


class LprTests(unittest.TestCase):
    def lpr(self, rows):
        ns = load_shipped_code()
        with patch.dict(ns, {"_em_datacenter_strict": MagicMock(return_value=rows)}):
            return ns["lpr_history"]()

    def test_blank_rows_dropped_but_unparsable_values_raise(self):
        """报表里混着旧贷款基准利率行（LPR 为 None，实测 38 行）；这些剔除，
        其余认不出的值要报错，不能返回 lpr_1y 为空的成品行。"""
        good = {"TRADE_DATE": "2026-08-20 00:00:00", "LPR1Y": 3.0, "LPR5Y": 3.5}
        old = {"TRADE_DATE": "2015-10-24 00:00:00", "LPR1Y": None, "LPR5Y": None}
        out = self.lpr([old, good])
        self.assertEqual((len(out), out.lpr_1y[0], out.date[0]), (1, 3.0, "2026-08-20"))
        for bad in ("", "-", "nan", True):
            with self.subTest(bad=bad), self.assertRaises(RuntimeError):
                self.lpr([dict(good, LPR1Y=bad)])


    def test_missing_or_odd_trade_date_is_a_source_error(self):
        """缺 TRADE_DATE 漏出 KeyError、非字符串漏出 TypeError，调用方会当成参数错。"""
        good = {"TRADE_DATE": "2026-08-20 00:00:00", "LPR1Y": 3.0, "LPR5Y": 3.5}
        with self.assertRaises(RuntimeError):
            self.lpr([{k: v for k, v in good.items() if k != "TRADE_DATE"}])
        for bad in (None, True, "2026/08/20", {"v": 1}):
            with self.subTest(bad=bad), self.assertRaises(RuntimeError):
                self.lpr([dict(good, TRADE_DATE=bad)])
        # 8 位数字（含 int）是合法写法，照常解析
        self.assertEqual(self.lpr([dict(good, TRADE_DATE=20260820)]).date[0], "2026-08-20")


class ChinaBondTests(unittest.TestCase):
    TREASURY, BANK, MTN = "中债国债收益率曲线", "中债商业银行普通债收益率曲线(AAA)", "中债中短期票据收益率曲线(AAA)"

    def setUp(self):
        self.ns = load_shipped_code()

    def html(self, rows):
        head = "".join(f"<th>{h}</th>" for h in ["曲线名称", "日期", "3月", "6月", "1年", "3年", "5年", "7年", "10年", "30年"])
        body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in [name, day] + ["1.5"] * 8) + "</tr>"
                       for name, day in rows)
        return Response(content=f"<table></table><table><tr>{head}</tr>{body}</table>".encode())

    def curve(self, pages, start, end, curve="all"):
        http = MagicMock(side_effect=[self.html(rows) for rows in pages])
        with patch.dict(self.ns, {"_v39_http": http}):
            return self.ns["chinabond_yield_curve"](start, end, curve=curve), http

    def test_complete_curves_in_window(self):
        out, _ = self.curve([[(self.TREASURY, "2026-09-18"), (self.BANK, "2026-09-18"), (self.MTN, "2026-09-18")]],
                            "2026-09-18", "2026-09-18")
        self.assertEqual(len(out), 3)
        out, _ = self.curve([[(self.TREASURY, "2008-01-02"), (self.MTN, "2008-01-02")]], "2008-01-02", "2008-01-02")
        self.assertEqual(len(out), 2)                                    # 商业银行曲线 2009-12-24 才开始

    def test_out_of_window_or_incomplete_or_wrong_curve_raises(self):
        """缓存错期、all 只回一条曲线、单条曲线回了别的曲线，都不能当完整结果。"""
        # 断言要认准报错原因：只写 assertRaises(RuntimeError)，统一异常契约把漏出的 KeyError
        # 也转成 RuntimeError 之后，删掉这里的检查测试照样绿
        for rows, start, end, curve, why in (
                ([(self.TREASURY, "2026-09-18")], "2026-01-01", "2026-01-10", "treasury", "却返回了"),
                ([(self.TREASURY, "2026-09-18")], "2026-09-18", "2026-09-18", "all", "缺少曲线"),
                ([(self.BANK, "2026-09-18")], "2026-09-18", "2026-09-18", "treasury", "未请求的曲线")):
            with self.subTest(rows=rows, curve=curve), self.assertRaisesRegex(RuntimeError, why):
                self.curve([rows], start, end, curve)

    def test_start_before_first_day_is_clamped(self):
        _, http = self.curve([[(self.TREASURY, "2006-03-01")]], "2000-01-01", "2006-03-05", "treasury")
        self.assertEqual(http.call_args.kwargs["params"]["startDate"], "2006-03-01")
        with patch.dict(self.ns, {"_v39_http": MagicMock(side_effect=AssertionError("network"))}):
            with self.assertRaisesRegex(ValueError, "2009-12-24 起才有数据"):
                self.ns["chinabond_yield_curve"]("2008-01-01", "2009-12-23", curve="bank_aaa")


class CffexDailyWitnessTests(unittest.TestCase):
    """中金所日行情 CSV 没有交易日列，靠同目录 index.xml 的 tradingday 与逐合约数值核对。"""
    HEADER = ["合约代码", "今开盘", "最高价", "最低价", "成交量", "成交金额", "持仓量", "持仓变化", "今收盘",
              "今结算", "前结算", "涨跌1", "涨跌2", "Delta"]
    ROWS = [["IF2610", "4500", "4520", "4480", "1000", "13500", "20000", "12", "4510", "4508", "4490", "20", "18", "--"],
            ["HO2610-C-3000", "30", "31", "29", "5", "1.5", "80", "-2", "30.5", "30.4", "29", "1.5", "1.4", "--"],
            ["小计", "", "", "", "1005", "", "20080", "", "", "", "", "", "", "--"]]

    def setUp(self):
        self.ns = load_shipped_code()

    def xml(self, day="20260918", volume="1000", drop=False):
        items = [("IF2610", volume, "4510", "20000")] + ([] if drop else [("HO2610-C-3000", "5", "30.5", "80")])
        body = "".join(f"<dailydata><instrumentid>{i}</instrumentid><tradingday>{day}</tradingday><volume>{v}</volume>"
                       f"<closeprice>{c}</closeprice><openinterest>{o}</openinterest></dailydata>" for i, v, c, o in items)
        return Response(content=f'<?xml version="1.0" encoding="UTF-8"?><dailydatas>{body}</dailydatas>'.encode())

    def daily(self, fn, xml_response):
        table = [list(self.HEADER)] + [list(r) for r in self.ROWS]
        with patch.dict(self.ns, {"_cffex_csv": MagicMock(return_value=table),
                                  "_v39_http": MagicMock(return_value=xml_response)}):
            return self.ns[fn]("2026-09-18", "CFFEX")

    def test_matching_witness_parses_futures_and_options(self):
        self.assertEqual(self.daily("futures_daily", self.xml()).symbol.tolist(), ["IF2610"])
        self.assertEqual(self.daily("options_daily", self.xml()).symbol.tolist(), ["HO2610-C-3000"])

    def test_witness_mismatch_raises(self):
        good = self.xml().content
        bad = [self.xml(day="20260917"), self.xml(volume="999"), self.xml(drop=True),
               Response(status=302, content=good),                         # 缺 index.xml（302 跳错误页）
               Response(content=good.replace(b"<dailydatas>", b'<!DOCTYPE dailydatas [<!ENTITY a "b">]><dailydatas>')),
               Response(content=b"<dailydatas>"), Response(content=b"<dailydatas></dailydatas>")]
        for fn in ("futures_daily", "options_daily"):
            for response in bad:
                with self.subTest(fn=fn, body=response.content[:40]), self.assertRaises(RuntimeError):
                    self.daily(fn, response)


class SseInteractionTimeTests(unittest.TestCase):
    """上证e互动的时间列：提问是绝对写法，1 天内的回复是相对写法（「昨天 18:22」，2026-10-23 实测）。"""

    NOW = datetime(2026, 10, 23, 9, 0)

    FEED = """<div class="m_feed_item" id="item-1798068">
      <div class="m_feed_detail m_qa_detail">
        <div class="m_feed_txt"><a href="x">:示例公司(000000)</a>请问今年的分红安排？</div>
        <div class="m_feed_from"><span>2026年10月21日 17:47</span></div>
      </div>
      <div class="m_feed_detail m_qa">
        <div class="m_feed_txt">感谢您的关注，详见公司公告。</div>
        <div class="m_feed_from" style="padding-left: 35px;"><span>昨天 18:22</span></div>
      </div>
    </div>"""

    def setUp(self):
        self.ns = load_shipped_code()

    def sse_time(self, text):
        return self.ns["_sse_time"](text, now=self.NOW)

    def test_relative_reply_time_maps_to_beijing_date(self):
        self.assertEqual(self.sse_time("昨天 18:22"), "2026-10-22 18:22")
        self.assertEqual(self.sse_time("今天 09:05"), "2026-10-23 09:05")
        self.assertEqual(self.sse_time("前天 23:59"), "2026-10-21 23:59")

    def test_other_site_time_shapes(self):
        self.assertEqual(self.sse_time("2026年10月21日 17:47"), "2026-10-21 17:47")
        self.assertEqual(self.sse_time("2026-10-21 17:47"), "2026-10-21 17:47")
        self.assertEqual(self.sse_time("10-20 08:30"), "2026-10-20 08:30")
        self.assertEqual(self.sse_time("35分钟前"), "2026-10-23 08:25")
        self.assertEqual(self.sse_time("3小时前"), "2026-10-23 06:00")
        self.assertEqual(self.sse_time("刚刚"), "2026-10-23 09:00")
        self.assertIsNone(self.sse_time("时间待定"))

    def test_parse_feed_keeps_relative_reply_time(self):
        # _sse_parse_feed 内部用真实「现在」，这里固定住，断言才不随运行日期漂移
        real_time = self.ns["_sse_time"]
        with patch.dict(self.ns, {"_sse_time": lambda text: real_time(text, now=self.NOW)}):
            rows = self.ns["_sse_parse_feed"](self.FEED)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["question_time"], "2026-10-21 17:47")
        self.assertEqual(rows[0]["answer_time"], "2026-10-22 18:22")

    def test_invalid_time_returns_none(self):
        for text in ("昨天 25:00", "09:99"):
            with self.subTest(text=text):
                self.assertIsNone(self.sse_time(text))

    def test_huge_ago_returns_none(self):
        for text in ("999999999天前", "99999999999999999999天前", "999999999999小时前"):
            with self.subTest(text=text):
                self.assertIsNone(self.sse_time(text))
        self.assertEqual(self.sse_time("2天前"), "2026-10-21 09:00")

    def test_invalid_feed_time_fails_loudly(self):
        real_time = self.ns["_sse_time"]
        with patch.dict(self.ns, {"_sse_time": lambda text: real_time(text, now=self.NOW)}):
            for invalid in ("昨天 25:00", "09:99"):
                for original, field in (("昨天 18:22", "回复"),
                                        ("2026年10月21日 17:47", "提问")):
                    with self.subTest(text=invalid, field=field):
                        text = self.FEED.replace(original, invalid)
                        with self.assertRaisesRegex(RuntimeError, field + "时间认不出"):
                            self.ns["_sse_parse_feed"](text)

    def test_month_day_year_rollover(self):
        self.assertEqual(self.ns["_sse_time"]("12-31 18:00", now=datetime(2026, 1, 5, 9, 0)),
                         "2025-12-31 18:00")
        self.assertIsNone(self.ns["_sse_time"]("02-29 10:00", now=datetime(2024, 1, 5, 9, 0)))

    def test_unknown_time_still_fails_loudly(self):
        """认不出就必须报错，不能把「格式变了」悄悄变成一列 None。"""
        text = self.FEED.replace("2026年10月21日 17:47", "时间待定")
        with self.assertRaisesRegex(RuntimeError, "提问时间认不出"):
            self.ns["_sse_parse_feed"](text)
        text = self.FEED.replace("昨天 18:22", "时间待定")
        with self.assertRaisesRegex(RuntimeError, "回复时间认不出"):
            self.ns["_sse_parse_feed"](text)


LIVE_DATE = os.environ.get("ASTOCK_LIVE_V39")


@unittest.skipUnless(LIVE_DATE, "set ASTOCK_LIVE_V39=<trading day YYYY-MM-DD> to hit real endpoints")
class LiveV39Tests(unittest.TestCase):
    def test_all_new_endpoints_return_rows_with_provenance(self):
        ns, d = load_shipped_code(), LIVE_DATE
        month_start = d[:8] + "01"
        calls = [
            ("tencent_kline day", lambda: ns["tencent_kline"]("600519", start=month_start, end=d)),
            ("tencent_kline m5", lambda: ns["tencent_kline"]("300750", period="m5", count=96)),
            ("tdx_daily_package", lambda: ns["tdx_daily_package"](d)),
            ("sina_research_reports", lambda: ns["sina_research_reports"]()),
            ("etf_shares SH", lambda: ns["etf_shares"](d, "SH")),
            ("wallstreetcn_lives", lambda: ns["wallstreetcn_lives"]("a-stock-channel", limit=50)),
            ("cctv_news", lambda: ns["cctv_news"](d, with_content=False)),
            ("st_stock_list", lambda: ns["st_stock_list"]()),
            ("sse_e_interaction", lambda: ns["sse_e_interaction"]()),
            ("chinabond_yield_curve", lambda: ns["chinabond_yield_curve"](month_start, d, curve="all")),
            ("repo_fixing_rates", lambda: ns["repo_fixing_rates"]("FR")),
            ("lpr_history", lambda: ns["lpr_history"]()),
            ("macro_calendar", lambda: ns["macro_calendar"](month_start, d)),
            ("futures_daily SHFE", lambda: ns["futures_daily"](d, "SHFE")),
            ("futures_daily INE", lambda: ns["futures_daily"](d, "INE")),
            ("futures_daily CZCE", lambda: ns["futures_daily"](d, "CZCE")),
            ("futures_daily CFFEX", lambda: ns["futures_daily"](d, "CFFEX")),
            ("futures_daily GFEX", lambda: ns["futures_daily"](d, "GFEX")),
            ("options_daily SHFE", lambda: ns["options_daily"](d, "SHFE")),
            ("options_daily CFFEX", lambda: ns["options_daily"](d, "CFFEX")),
            ("futures_position_rank CFFEX", lambda: ns["futures_position_rank"](d, "CFFEX")),
            ("futures_realtime", lambda: ns["futures_realtime"](["RB0", "M0", "IF0"])),
            ("a50_futures", lambda: ns["a50_futures"]()),
            ("sge_spot", lambda: ns["sge_spot"]("Au99.99")),
            ("earnings_forecast", lambda: ns["earnings_forecast"](limit=50)),
            ("institution_survey", lambda: ns["institution_survey"](limit=50)),
            ("holder_trades", lambda: ns["holder_trades"](limit=50)),
            ("share_buyback", lambda: ns["share_buyback"](limit=50)),
            ("equity_pledge", lambda: ns["equity_pledge"](limit=50)),
            ("ipo_calendar", lambda: ns["ipo_calendar"](limit=30)),
            ("convertible_bonds", lambda: ns["convertible_bonds"]()),
        ]
        for name, fetch in calls:
            with self.subTest(name=name):
                frame = fetch()
                self.assertGreater(len(frame), 0)
                self.assertTrue({"source", "source_url", "fetched_at"} <= set(frame.columns))


if __name__ == "__main__":
    unittest.main()
