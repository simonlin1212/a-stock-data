"""a-stock-data-next 端点迁移 smoke test。

默认只做导入、函数存在性和无网络公式校验。传入 --network 后执行全端点 best-effort
真实 API 探测：函数抛异常记为 WARN，返回空但无异常记为 OK，避免单个外部源波动阻断整体验证。
"""

from __future__ import annotations

import argparse
import importlib.util
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CLIENT = ROOT / "a_stock_client.py"

REQUIRED_FUNCTIONS = [
    "get_prefix",
    "normalize_code",
    "em_get",
    "eastmoney_datacenter",
    "mootdx_bars",
    "mootdx_quotes",
    "mootdx_transactions",
    "mootdx_finance",
    "mootdx_f10",
    "mootdx_f10_section",
    "tencent_quote",
    "baidu_kline_with_ma",
    "eastmoney_reports",
    "download_pdf",
    "ths_eps_forecast",
    "get_iwencai_api_key",
    "_claw_headers",
    "iwencai_search",
    "iwencai_query",
    "dedup_articles",
    "ths_hot_reason",
    "hsgt_realtime",
    "_northbound_cache_path",
    "_save_northbound_snapshot",
    "_load_northbound_history",
    "eastmoney_concept_blocks",
    "baidu_concept_blocks",
    "eastmoney_fund_flow_minute",
    "dragon_tiger_board",
    "lockup_expiry",
    "industry_comparison",
    "daily_dragon_tiger",
    "margin_trading",
    "block_trade",
    "holder_num_change",
    "dividend_history",
    "stock_fund_flow_120d",
    "eastmoney_stock_news",
    "cls_telegraph",
    "eastmoney_global_news",
    "eastmoney_stock_info",
    "sina_financial_report",
    "_cninfo_ts_to_date",
    "_cninfo_orgid",
    "cninfo_announcements",
    "forward_pe",
    "pe_digestion",
    "calc_peg",
    "full_valuation",
]


def load_client():
    spec = importlib.util.spec_from_file_location("a_stock_client", CLIENT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", action="store_true", help="执行少量真实网络端点检查")
    args = parser.parse_args()

    client = load_client()
    missing = [name for name in REQUIRED_FUNCTIONS if not callable(getattr(client, name, None))]
    if missing:
        print("FAIL 缺失函数:", ", ".join(missing))
        return 1
    print(f"OK 函数清单完整: {len(REQUIRED_FUNCTIONS)}")

    assert client.normalize_code("SH688017") == "688017"
    assert client.normalize_code("688017.SH") == "688017"
    assert client.forward_pe(20, 2) == 10
    assert client.calc_peg(30, 0.3) == 1
    assert client.cls_telegraph() == []
    print("OK 无网络基础校验通过")

    if args.network:
        today = datetime.now().strftime("%Y-%m-%d")

        checks = [
            ("腾讯行情", lambda: client.tencent_quote(["600519"])),
            ("百度K线", lambda: client.baidu_kline_with_ma("600519")),
            ("东财研报", lambda: client.eastmoney_reports("600519", max_pages=1)),
            ("同花顺一致预期", lambda: client.ths_eps_forecast("600519")),
            ("iwencai研报搜索", lambda: client.iwencai_search("贵州茅台 研报", size=5)),
            ("同花顺热点", lambda: client.ths_hot_reason()),
            ("北向实时", lambda: client.hsgt_realtime()),
            ("东财板块归属", lambda: client.eastmoney_concept_blocks("600519")),
            ("东财分钟资金流", lambda: client.eastmoney_fund_flow_minute("600519")),
            ("龙虎榜席位", lambda: client.dragon_tiger_board("600519", today)),
            ("限售解禁", lambda: client.lockup_expiry("600519", today)),
            ("行业排名", lambda: client.industry_comparison(5)),
            ("全市场龙虎榜", lambda: client.daily_dragon_tiger(today)),
            ("融资融券", lambda: client.margin_trading("600519", page_size=3)),
            ("大宗交易", lambda: client.block_trade("600519", page_size=3)),
            ("股东户数", lambda: client.holder_num_change("600519", page_size=3)),
            ("分红送转", lambda: client.dividend_history("600519", page_size=3)),
            ("120日资金流", lambda: client.stock_fund_flow_120d("600519")),
            ("东财个股新闻", lambda: client.eastmoney_stock_news("600519", page_size=5)),
            ("财联社兼容stub", lambda: client.cls_telegraph()),
            ("东财全球资讯", lambda: client.eastmoney_global_news(page_size=5)),
            ("东财个股信息", lambda: client.eastmoney_stock_info("600519")),
            ("新浪利润表", lambda: client.sina_financial_report("600519", "lrb", num=2)),
            ("新浪资产负债表", lambda: client.sina_financial_report("600519", "fzb", num=2)),
            ("新浪现金流量表", lambda: client.sina_financial_report("600519", "llb", num=2)),
            ("巨潮公告", lambda: client.cninfo_announcements("600519", page_size=3)),
            ("mootdx报价", lambda: client.mootdx_quotes(["600519"])),
            ("mootdxK线", lambda: client.mootdx_bars("600519", offset=2)),
            ("mootdx财务", lambda: client.mootdx_finance("600519")),
        ]

        ok = 0
        warn = 0
        for name, fn in checks:
            try:
                result = fn()
                size = len(result) if hasattr(result, "__len__") else 1
                print(f"OK {name}: size={size}")
                ok += 1
            except Exception as exc:
                print(f"WARN {name}: {type(exc).__name__}: {str(exc)[:160]}")
                warn += 1
        print(f"网络验证完成: OK={ok}, WARN={warn}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
