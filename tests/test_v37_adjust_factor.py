"""Offline regression tests for §1.6, executing the Python shipped in SKILL.md."""

import ast
import json
import re
import sys
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_v39_sources import _block_defining, _defs_only  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "sina_adjust"
CODE = _block_defining("sina_adjust_factor")
FUNDS = ("sh511010", "sh513100", "sz159919", "sz161226")


def load_adjust_code():
    ns = {}
    blocks = []
    for name in ("get_prefix", "norm_ticker", "sina_adjust_factor"):
        block = _block_defining(name)
        if block not in blocks:
            blocks.append(block)
            exec(_defs_only(block), ns)
    return ns


def fixture_rows(code, kind):
    text = (FIXTURES / (code + "-" + kind + ".js")).read_text(encoding="utf-8")
    return json.JSONDecoder().raw_decode(text[text.index("{"):])[0]["data"]


class SinaAdjustTests(unittest.TestCase):
    def setUp(self):
        self.ns = load_adjust_code()
        self.apply = self.ns["apply_adjust"]

    def factors(self, code, kind="qfq", status=200):
        suffix = ".html" if status == 404 else ".js"
        response = requests.Response()
        response.status_code = status
        response.url = "https://example.test/" + code + "/" + kind + ".js"
        response.encoding = "utf-8"
        response._content = (FIXTURES / (code + "-" + kind + suffix)).read_bytes()
        with patch("requests.get", return_value=response) as get:
            result = self.ns["sina_adjust_factor"](code, kind)
        self.assertTrue(get.call_args[0][0].endswith("/" + code + "/" + kind + ".js"))
        return result

    def test_fund_fields_match_raw_fixtures(self):
        for code in FUNDS[:3]:
            for kind in ("qfq", "hfq"):
                with self.subTest(code=code, kind=kind):
                    expected = [{"date": r["d"], "factor": float(r["f"]),
                                 "split": float(r["s"]), "dividend": float(r["u"])}
                                for r in fixture_rows(code, kind)]
                    self.assertEqual(self.factors(code, kind), expected)

    def test_all_tencent_checkpoints(self):
        points = json.loads((FIXTURES / "checkpoints.json").read_text(encoding="utf-8"))["points"]
        self.assertEqual(len(points), 36)
        for point in points:
            self.assertIsNotNone(point["tencent_qfq"])
            self.assertIsNotNone(point["tencent_hfq"])
        tables = {(code, kind): self.factors(code, kind)
                  for code in FUNDS[:3] for kind in ("qfq", "hfq")}
        for point in points:
            for kind in ("qfq", "hfq"):
                expected = point["tencent_" + kind]
                with self.subTest(code=point["code"], date=point["date"], kind=kind):
                    rows = self.apply([{"date": point["date"], "close": point["close"]}],
                                      tables[point["code"], kind], kind)
                    self.assertLessEqual(abs(rows[0]["close"] - expected), 0.001)

    def test_stock_fields_unchanged(self):
        for kind in ("qfq", "hfq"):
            expected = [{"date": r["d"], "factor": float(r["f"])}
                        for r in fixture_rows("sh600519", kind)]
            actual = self.factors("sh600519", kind)
            self.assertEqual(json.dumps(actual), json.dumps(expected))
            self.assertTrue(all(set(r) == {"date", "factor"} for r in actual))

    def test_stock_prices_unchanged(self):
        bars = [{"date": "2015-01-05", "close": 202.52}]
        for kind, expected in (("qfq", 143.46), ("hfq", 1274.28)):
            factors = self.factors("sh600519", kind)
            result = self.apply(bars, factors, kind)[0]
            factor = max((r for r in factors if r["date"] <= bars[0]["date"]),
                         key=lambda r: r["date"])["factor"]
            legacy = round(202.52 / factor if kind == "qfq" else 202.52 * factor, 4)
            self.assertEqual(result, {"date": bars[0]["date"], "close": legacy, "adj_factor": factor})
            self.assertAlmostEqual(result["close"], expected, places=2)

    def test_stock_none_factor_preserves_runtime_error(self):
        factors = [{"date": "1900-01-01", "factor": None}]
        for kind in ("qfq", "hfq"):
            for prices in ({"close": 10}, {"close": "bad"}, {"close": None}, {}):
                with self.subTest(kind=kind, prices=prices):
                    with self.assertRaisesRegex(RuntimeError, "早于因子序列最早日"):
                        self.apply([dict(date="2020-01-01", **prices)], factors, kind)
            self.assertEqual(self.apply([], factors, kind), [])

    def test_stock_malformed_rows_preserve_legacy_exception_types(self):
        # Expected types follow bf447c1's direct d lookup and float(f) conversion.
        cases = (({"d": "1900-01-01"}, KeyError),
                 ({"d": "1900-01-01", "f": "bad"}, ValueError),
                 ({"d": "1900-01-01", "f": None}, TypeError),
                 ({"f": "1"}, KeyError))
        for kind in ("qfq", "hfq"):
            for row, expected in cases:
                response = requests.Response()
                response.status_code = 200
                response._content = ('var x=' + json.dumps({"data": [row]}) + ';').encode()
                with self.subTest(kind=kind, row=row), patch("requests.get", return_value=response):
                    with self.assertRaises(expected) as raised:
                        self.ns["sina_adjust_factor"]("sh600519", kind)
                    self.assertIs(type(raised.exception), expected)

    def test_sentinel_before_first_real_event(self):
        for code in FUNDS[:3]:
            for kind in ("qfq", "hfq"):
                with self.subTest(code=code, kind=kind):
                    factors = self.factors(code, kind)
                    sentinel = next(r for r in factors if r["date"] == "1900-01-01")
                    self.assertTrue(all(r["date"] > "2000-01-01" for r in factors if r is not sentinel))
                    result = self.apply([{"date": "2000-01-01", "close": 100}], factors, kind)[0]
                    expected = (100 / sentinel["split"] - sentinel["dividend"] if kind == "qfq"
                                else (100 + sentinel["dividend"]) * sentinel["split"])
                    self.assertEqual(result["close"], round(expected, 4))
                    self.assertEqual(result["adj_split"], sentinel["split"])
                    self.assertEqual(result["adj_dividend"], sentinel["dividend"])

    def test_sentinel_only_fund_keeps_prices(self):
        for kind in ("qfq", "hfq"):
            factors = self.factors("sz161226", kind)
            self.assertEqual(factors, [{"date": "1900-01-01", "factor": 1.0,
                                        "split": 1.0, "dividend": 0.0}])
            self.assertEqual(self.apply([{"date": "2020-01-01", "close": 1.2345}], factors, kind)[0]["close"],
                             1.2345)

    def test_http_404_remains_http_error(self):
        with self.assertRaises(requests.HTTPError):
            self.factors("sh508000", status=404)

    def test_mixed_or_partial_fund_fields_rejected(self):
        stock = {"date": "1900-01-01", "factor": 1.0}
        fund = dict(stock, split=1.0, dividend=0.0)
        for factors in ([stock, fund], [fund, stock], [dict(stock, split=1.0)],
                        [dict(stock, dividend=0.0)]):
            with self.subTest(factors=factors), self.assertRaisesRegex(RuntimeError, "口径混杂"):
                self.apply([{"date": "2020-01-01", "close": 10}], factors)

    def test_nonpositive_fund_split_rejected(self):
        for split in (0, -1):
            with self.subTest(split=split), self.assertRaisesRegex(RuntimeError, "split"):
                self.apply([{"date": "2020-01-01", "close": 10}],
                           [{"date": "1900-01-01", "factor": 1, "split": split, "dividend": 0}])

    def test_fund_factor_must_be_one(self):
        for factor in (0, 2):
            with self.subTest(factor=factor), self.assertRaisesRegex(RuntimeError, "factor"):
                self.apply([{"date": "2020-01-01", "close": 10}],
                           [{"date": "1900-01-01", "factor": factor, "split": 1, "dividend": 0}])

    def test_nonpositive_fund_qfq_recommends_hfq(self):
        factors = [{"date": "1900-01-01", "factor": 1, "split": 2, "dividend": 5}]
        for close in (10, 8):
            with self.subTest(close=close), self.assertRaisesRegex(RuntimeError, "hfq"):
                self.apply([{"date": "2020-01-01", "close": close}], factors)
            self.assertEqual(self.apply([{"date": "2020-01-01", "close": close}], factors, "hfq")[0]["close"],
                             (close + 5) * 2)

    def test_fund_qfq_rounded_zero_rejected(self):
        factors = [{"date": "1900-01-01", "factor": 1,
                    "split": 1, "dividend": 1.00099}]
        with self.assertRaisesRegex(RuntimeError, "hfq"):
            self.apply([{"date": "2020-01-01", "close": 1.001}], factors)

    def test_dataframe_dates_index_and_metadata(self):
        try:
            import pandas as pd
        except ImportError:
            self.skipTest("pandas is not installed")
        bars = pd.DataFrame({"datetime": pd.to_datetime(["2022-01-14 15:00", "2022-01-12 15:00"]),
                             "close": [1.015, 5.192]}, index=pd.DatetimeIndex(["2022-01-14", "2022-01-12"], name="day"))
        original = bars.copy(deep=True)
        result = self.apply(bars, self.factors("sh513100"))
        self.assertEqual(result.date.tolist(), ["2022-01-12", "2022-01-14"])
        self.assertEqual(result.close.tolist(), [1.0384, 1.015])
        self.assertEqual(result.adj_split.tolist(), [5.0, 1.0])
        self.assertEqual(result.adj_dividend.tolist(), [0.0, 0.0])
        self.assertEqual(result.adj_factor.tolist(), [1.0, 1.0])
        self.assertTrue(result.index.equals(original.index[::-1]))
        self.assertEqual(result.index.name, "day")
        pd.testing.assert_frame_equal(bars, original)

    def test_python39_syntax(self):
        ast.parse(CODE, feature_version=(3, 9))
        self.assertIsNone(re.search(r"\w\s*\|\s*None\b", CODE))

    def test_fund_fixture_invariants(self):
        for code, product, total in zip(FUNDS, (1, 5, 0.4245239277782239, 1), (5.3905, 0, 0.4062, 0)):
            with self.subTest(code=code):
                qfq, hfq = self.factors(code), self.factors(code, "hfq")
                self.assertEqual((qfq[0]["split"], qfq[0]["dividend"]), (1, 0))
                self.assertEqual((hfq[-1]["split"], hfq[-1]["dividend"]), (1, 0))
                raw_q, raw_h = fixture_rows(code, "qfq"), fixture_rows(code, "hfq")
                by_date = {r["d"]: r for r in raw_h}
                self.assertEqual({r["d"] for r in raw_q}, set(by_date))
                products, sums = [], []
                for row in raw_q:
                    other = by_date[row["d"]]
                    products.append(Decimal(row["s"]) * Decimal(other["s"]))
                    sums.append(Decimal(row["u"]) + Decimal(other["u"]))
                self.assertLessEqual(max(products) - min(products), Decimal("4e-17"))
                self.assertAlmostEqual(float(products[0]), product, places=15)
                self.assertEqual(set(sums), {Decimal(str(total))})

    def test_existing_empty_early_and_zero_checks(self):
        bars = [{"date": "2020-01-01", "close": 10}]
        with self.assertRaises(ValueError):
            self.apply(bars, [])
        with self.assertRaisesRegex(RuntimeError, "早于"):
            self.apply(bars, [{"date": "2021-01-01", "factor": 1}])
        with self.assertRaisesRegex(RuntimeError, "因子为 0"):
            self.apply(bars, [{"date": "1900-01-01", "factor": 0}])

    def test_list_prices_metadata_and_inputs_unchanged(self):
        bars = [{"date": "2022-01-12", "open": 5.192, "high": 5.3, "low": 5.1, "close": 5.2,
                 "volume": 100, "optional": None}]
        for kind in ("qfq", "hfq"):
            factors = self.factors("sh513100", kind)
            original = json.dumps((bars, factors))
            result = self.apply(bars, factors, kind)[0]
            for key in ("open", "high", "low", "close"):
                self.assertEqual(result[key], round(bars[0][key] / 5, 4) if kind == "qfq" else bars[0][key])
            self.assertEqual(result["volume"], 100)
            self.assertIsNone(result["optional"])
            self.assertEqual((result["adj_factor"], result["adj_split"], result["adj_dividend"]),
                             (1, 5 if kind == "qfq" else 1, 0))
            self.assertEqual(json.dumps((bars, factors)), original)

    def test_malformed_fund_fields_are_runtime_errors(self):
        for fields in ('"s":"bad","u":"0"', '"s":"1"', '"u":"0"'):
            response = requests.Response()
            response.status_code = 200
            response._content = ('var x={"data":[{"d":"1900-01-01","f":"1",' + fields + '}]};').encode()
            with self.subTest(fields=fields), patch("requests.get", return_value=response):
                with self.assertRaises(RuntimeError):
                    self.ns["sina_adjust_factor"]("sh511010")

    def test_invalid_kind_is_value_error_without_network(self):
        with patch("requests.get", side_effect=AssertionError("network")):
            with self.assertRaises(ValueError):
                self.ns["sina_adjust_factor"]("sh511010", "bad")
        with self.assertRaises(ValueError):
            self.apply([], [], "bad")


if __name__ == "__main__":
    unittest.main()
