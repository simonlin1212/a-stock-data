"""Exercise the valuation functions shipped in SKILL.md with offline data."""
import ast
import json
import math
import re
import unittest
import urllib.request
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd


def load_valuation_functions():
    skill = (Path(__file__).resolve().parents[1] / "SKILL.md").read_text(encoding="utf-8")
    names = {"pe_digestion", "full_valuation"}
    functions = []
    for block in re.findall(r"```python\n(.*?)\n```", skill, re.S):
        if not any(f"def {name}(" in block for name in names):
            continue
        functions.extend(node for node in ast.parse(block).body
                         if isinstance(node, ast.FunctionDef) and node.name in names)
    if {node.name for node in functions} != names or len(functions) != len(names):
        raise AssertionError("Expected one shipped definition of each valuation function")
    namespace = {"math": math, "pd": pd, "urllib": urllib}
    exec(compile(ast.Module(body=functions, type_ignores=[]), "SKILL.md:valuation", "exec"), namespace)
    return namespace


class ValuationTests(unittest.TestCase):
    def setUp(self):
        self.ns = load_valuation_functions()

    def valuation(self, price, current_eps=10, next_eps=10, empty=False):
        fields = ["0"] * 50
        fields[1], fields[3], fields[39], fields[45], fields[46] = "Fixture", str(price), "50", "100", "2"
        quote = ('v_sh600519="' + "~".join(fields) + '";').encode("gbk")
        rows = [] if empty else [[2026, current_eps, 3], [2027, next_eps, 3]]
        forecast = pd.DataFrame(rows, columns=["年份", "均值", "预测机构数"])
        with patch.object(urllib.request, "urlopen", return_value=BytesIO(quote)), \
                patch.dict(self.ns, {"ths_eps_forecast": MagicMock(return_value=forecast)}):
            return self.ns["full_valuation"]("600519")

    def test_high_pe_without_earnings_growth_is_not_zero_years(self):
        for next_eps in (10, 8, 0):
            with self.subTest(next_eps=next_eps):
                result = self.valuation(500, next_eps=next_eps)
                self.assertEqual(result["pe_fwd"], 50)
                self.assertIsNone(result["digest_years"])
                self.assertTrue(math.isinf(self.ns["pe_digestion"](50, next_eps / 10 - 1)))
                json.dumps(result, allow_nan=False)

    def test_high_pe_with_missing_next_forecast_is_unknown(self):
        self.assertIsNone(self.valuation(500, next_eps=None)["digest_years"])

    def test_positive_growth_retains_finite_digestion_time(self):
        result = self.valuation(500, next_eps=20)
        self.assertEqual(result["digest_years"], 0.7)
        self.assertEqual(result["cagr_pct"], 100)
        self.assertEqual(result["peg"], 0.5)

    def test_pe_already_at_or_below_target_needs_zero_years(self):
        for price in (100, 300):
            for next_eps in (10, 8, None):
                with self.subTest(price=price, next_eps=next_eps):
                    self.assertEqual(self.valuation(price, next_eps=next_eps)["digest_years"], 0)

    def test_missing_zero_or_negative_current_eps_is_unknown(self):
        for current_eps in (None, 0, -5):
            with self.subTest(current_eps=current_eps):
                self.assertIsNone(self.valuation(500, current_eps=current_eps)["digest_years"])

    def test_empty_forecast_is_unknown(self):
        result = self.valuation(500, empty=True)
        self.assertIsNone(result["pe_fwd"])
        self.assertIsNone(result["digest_years"])
        json.dumps(result, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
