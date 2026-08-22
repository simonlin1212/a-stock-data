import os
import re
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


class FakeResponse:
    def __init__(self, status_code=200, payload=None, json_error=False):
        self.status_code = status_code
        self.payload = payload
        self.json_error = json_error

    def json(self):
        if self.json_error:
            raise ValueError("invalid json")
        return self.payload


class FakeRequests:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.response


def load_endpoint():
    skill = (Path(__file__).parents[1] / "SKILL.md").read_text(encoding="utf-8")
    section = skill.split("### 10.3 X 公开帖子搜索", 1)[1].split("\n---\n", 1)[0]
    match = re.search(r"```python\n(.*?)\n```", section, re.DOTALL)
    if match is None:
        raise AssertionError("§10.3 Python block not found")
    namespace = {}
    requests_module = types.ModuleType("requests")
    with patch.dict(sys.modules, {"requests": requests_module}):
        exec(compile(match.group(1), "SKILL.md §10.3", "exec"), namespace)
    return namespace["xquik_stock_mentions"], namespace


class XquikStockMentionsTests(unittest.TestCase):
    def test_normalizes_bounded_public_search(self):
        payload = {
            "tweets": [{
                "id": "123",
                "text": "public post",
                "createdAt": "2026-08-21T09:00:00Z",
                "url": "https://x.com/investor/status/123",
                "lang": "zh",
                "likeCount": 4,
                "retweetCount": 3,
                "replyCount": 2,
                "quoteCount": 1,
                "viewCount": 100,
                "author": {
                    "id": "9",
                    "username": "investor",
                    "name": "Investor",
                    "followers": 500,
                    "verified": False,
                },
            }],
            "has_next_page": True,
            "next_cursor": "cursor-2",
        }
        fake = FakeRequests(FakeResponse(payload=payload))
        endpoint, namespace = load_endpoint()
        namespace["requests"] = fake

        with patch.dict(os.environ, {"XQUIK_API_KEY": "test-key"}):
            result = endpoint(
                "贵州茅台 OR 600519",
                limit=20,
                since_date="2026-08-15",
                until_date="2026-08-22",
                language="zh",
                cursor="cursor-1",
            )

        self.assertEqual(result["source"], "xquik")
        self.assertEqual(result["query"], "贵州茅台 OR 600519")
        self.assertTrue(result["has_more"])
        self.assertEqual(result["next_cursor"], "cursor-2")
        self.assertEqual(result["posts"][0]["author"]["username"], "investor")
        self.assertEqual(result["posts"][0]["reposts"], 3)
        self.assertEqual(len(fake.calls), 1)
        url, request = fake.calls[0]
        self.assertEqual(url, "https://xquik.com/api/v1/x/tweets/search")
        self.assertEqual(request["params"]["limit"], 20)
        self.assertEqual(request["params"]["sinceDate"], "2026-08-15")
        self.assertEqual(request["params"]["untilDate"], "2026-08-22")
        self.assertEqual(request["params"]["language"], "zh")
        self.assertEqual(request["params"]["cursor"], "cursor-1")
        self.assertNotIn("test-key", request["params"].values())
        self.assertEqual(request["headers"]["x-api-key"], "test-key")
        self.assertEqual(request["headers"]["xquik-api-contract"], "2026-04-29")

    def test_rejects_invalid_or_unbounded_inputs_before_network(self):
        endpoint, namespace = load_endpoint()
        fake = FakeRequests(FakeResponse(payload={"tweets": []}))
        namespace["requests"] = fake
        cases = [
            (("",), {}),
            (("600519",), {"limit": 0}),
            (("600519",), {"limit": 101}),
            (("600519",), {"limit": True}),
            (("600519",), {"since_date": "2026/08/15"}),
            (("600519",), {"since_date": "2026-08-22", "until_date": "2026-08-15"}),
            (("600519",), {"language": " "}),
            (("600519",), {"cursor": " "}),
        ]
        with patch.dict(os.environ, {"XQUIK_API_KEY": "test-key"}):
            for args, kwargs in cases:
                with self.subTest(args=args, kwargs=kwargs):
                    with self.assertRaises(ValueError):
                        endpoint(*args, **kwargs)
        self.assertEqual(fake.calls, [])

    def test_requires_key_without_exposing_or_sending_a_request(self):
        endpoint, namespace = load_endpoint()
        fake = FakeRequests(FakeResponse(payload={"tweets": []}))
        namespace["requests"] = fake
        with patch.dict(os.environ, {"XQUIK_API_KEY": ""}):
            with self.assertRaisesRegex(RuntimeError, "XQUIK_API_KEY"):
                endpoint("600519")
        self.assertEqual(fake.calls, [])

    def test_reports_auth_credit_rate_and_service_failures(self):
        expected = {401: "鉴权失败", 402: "额度不足", 429: "请求过快", 503: "HTTP 503"}
        for status, message in expected.items():
            with self.subTest(status=status):
                endpoint, namespace = load_endpoint()
                namespace["requests"] = FakeRequests(FakeResponse(status_code=status))
                with patch.dict(os.environ, {"XQUIK_API_KEY": "test-key"}):
                    with self.assertRaisesRegex(RuntimeError, message):
                        endpoint("600519")

    def test_rejects_invalid_success_payloads(self):
        responses = [
            FakeResponse(payload=None, json_error=True),
            FakeResponse(payload=[]),
            FakeResponse(payload={"results": []}),
            FakeResponse(payload={"tweets": ["not-an-object"]}),
            FakeResponse(payload={"tweets": [{"author": "not-an-object"}]}),
        ]
        for response in responses:
            with self.subTest(response=response):
                endpoint, namespace = load_endpoint()
                namespace["requests"] = FakeRequests(response)
                with patch.dict(os.environ, {"XQUIK_API_KEY": "test-key"}):
                    with self.assertRaises(RuntimeError):
                        endpoint("600519")


if __name__ == "__main__":
    unittest.main()
