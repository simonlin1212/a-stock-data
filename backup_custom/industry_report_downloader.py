#!/usr/bin/env python3
"""
industry_report_downloader.py
==============================
按行业批量下载东财研报 PDF — 基于 a-stock-data SKILL.md V3.1 端点

流程
----
1. 拉取东财全行业列表（~100 个行业）
2. 模糊匹配用户指定的行业关键词，确认目标行业
3. 拉取该行业所有成分股（分页，最多 500 只）
4. 逐股拉取研报列表，按 infoCode 去重
5. 可选过滤：日期范围 / 机构名 / 评级 / 关键词
6. 批量下载 PDF，断点续传（已存在则跳过）
7. 打印下载报告

依赖
----
pip install requests

用法示例
--------
# 下载"半导体"行业最近 90 天所有研报
python industry_report_downloader.py --industry 半导体 --days 90

# 下载"新能源汽车"行业研报，只要评级为"买入"的，最多 50 篇
python industry_report_downloader.py --industry 新能源汽车 --rating 买入 --limit 50

# 列出所有可用行业（不下载）
python industry_report_downloader.py --list-industries

# 指定输出目录
python industry_report_downloader.py --industry 白酒 --output ./reports/baijiu
"""

import argparse
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests

# ─────────────────────────── 全局常量 ───────────────────────────

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

PUSH2_URL    = "https://push2.eastmoney.com/api/qt/clist/get"
REPORT_API   = "https://reportapi.eastmoney.com/report/list"
PDF_TPL      = "https://pdf.dfcfw.com/pdf/H3_{info_code}_1.pdf"

COMMON_HEADERS = {
    "User-Agent": UA,
    "Referer": "https://data.eastmoney.com/",
}

# ─────────────────────────── Step 1: 获取行业列表 ───────────────────────────

def fetch_industry_list() -> list[dict]:
    """
    从东财 push2 拉取全部行业板块（约 100 个）。
    返回: [{"name": "半导体", "code": "BK0438", "change_pct": 1.23, ...}, ...]
    """
    params = {
        "pn": "1", "pz": "200", "po": "1", "np": "1",
        "fltt": "2", "invt": "2",
        "fs": "m:90+t:2",
        "fields": "f2,f3,f4,f12,f13,f14,f104,f105,f140,f136",
    }
    r = requests.get(PUSH2_URL, params=params, headers=COMMON_HEADERS, timeout=15)
    r.raise_for_status()
    items = r.json().get("data", {}).get("diff", []) or []
    result = []
    for item in items:
        result.append({
            "name":         item.get("f14", ""),
            "code":         item.get("f12", ""),       # BK0438 格式
            "change_pct":   item.get("f3", 0),
            "up_count":     item.get("f104", 0),
            "down_count":   item.get("f105", 0),
            "leader_stock": item.get("f140", ""),
        })
    return result


def match_industry(keyword: str, industry_list: list[dict]) -> list[dict]:
    """
    模糊匹配行业名称，返回所有命中项。
    优先返回完全匹配，其次包含匹配。
    """
    exact   = [i for i in industry_list if i["name"] == keyword]
    if exact:
        return exact
    partial = [i for i in industry_list if keyword in i["name"]]
    return partial


# ─────────────────────────── Step 2: 获取成分股 ───────────────────────────

def fetch_industry_stocks(bk_code: str, max_stocks: int = 500) -> list[dict]:
    """
    拉取指定行业板块的所有成分股。
    bk_code: 东财行业代码，如 "BK0438"
    返回: [{"code": "688017", "name": "渝商A", ...}, ...]
    """
    all_stocks = []
    page = 1
    page_size = 100
    while len(all_stocks) < max_stocks:
        params = {
            "pn": str(page), "pz": str(page_size),
            "po": "1", "np": "1",
            "fltt": "2", "invt": "2",
            "fs": f"b:{bk_code}+f:!50",          # b:板块代码  f:!50 排除ST
            "fields": "f12,f14,f2,f3,f5,f6,f15,f16,f17,f18",
        }
        r = requests.get(PUSH2_URL, params=params, headers=COMMON_HEADERS, timeout=15)
        r.raise_for_status()
        data  = r.json().get("data") or {}
        diff  = data.get("diff") or []
        total = int(data.get("total", 0))

        for item in diff:
            all_stocks.append({
                "code":       str(item.get("f12", "")),
                "name":       item.get("f14", ""),
                "price":      item.get("f2", 0),
                "change_pct": item.get("f3", 0),
            })

        if len(all_stocks) >= total or not diff:
            break
        page += 1
        time.sleep(0.2)

    return all_stocks[:max_stocks]


# ─────────────────────────── Step 3: 拉取研报列表 ───────────────────────────

def fetch_reports_for_stock(
    code: str,
    begin_date: str = "2000-01-01",
    end_date:   str = "2099-12-31",
    max_pages:  int = 3,
) -> list[dict]:
    """
    拉取单只股票的研报列表。
    返回原始 record 列表（含 infoCode / title / publishDate / orgSName / emRatingName）
    """
    session = requests.Session()
    session.headers.update(COMMON_HEADERS)
    all_records = []

    for page in range(1, max_pages + 1):
        params = {
            "industryCode": "*", "pageSize": "100",
            "industry": "*", "rating": "*", "ratingChange": "*",
            "beginTime": begin_date, "endTime": end_date,
            "pageNo": str(page), "fields": "",
            "qType": "0", "orgCode": "",
            "code": code, "rcode": "",
            "p": str(page), "pageNum": str(page), "pageNumber": str(page),
        }
        try:
            r = session.get(REPORT_API, params=params, timeout=20)
            r.raise_for_status()
            d = r.json()
        except Exception as e:
            print(f"  [WARN] {code} 第{page}页请求失败: {e}")
            break

        rows = d.get("data") or []
        if not rows:
            break
        all_records.extend(rows)

        total_pages = d.get("TotalPage", 1) or 1
        if page >= total_pages:
            break
        time.sleep(0.25)

    return all_records


def fetch_reports_for_industry(
    stocks:      list[dict],
    begin_date:  str,
    end_date:    str,
    rating_filter: str | None = None,
    keyword_filter: str | None = None,
    max_pages_per_stock: int = 3,
    report_limit: int | None = None,
) -> list[dict]:
    """
    批量拉取行业内所有股票研报，按 infoCode 全局去重。

    去重策略：同一 infoCode（即同一篇研报）只保留一条，
              即使多只成分股都挂载了该研报。
    """
    seen_codes: set[str] = set()
    all_reports: list[dict] = []
    total = len(stocks)

    for idx, stock in enumerate(stocks, 1):
        code = stock["code"]
        name = stock["name"]
        print(f"  [{idx:3d}/{total}] {code} {name} ", end="", flush=True)

        records = fetch_reports_for_stock(
            code,
            begin_date=begin_date,
            end_date=end_date,
            max_pages=max_pages_per_stock,
        )

        new_count = 0
        for rec in records:
            info_code = rec.get("infoCode", "")
            if not info_code or info_code in seen_codes:
                continue

            # 评级过滤
            if rating_filter:
                rating = rec.get("emRatingName", "") or ""
                if rating_filter not in rating:
                    continue

            # 关键词过滤（标题匹配）
            if keyword_filter:
                title = rec.get("title", "") or ""
                if keyword_filter not in title:
                    continue

            seen_codes.add(info_code)
            all_reports.append(rec)
            new_count += 1

            if report_limit and len(all_reports) >= report_limit:
                print(f"→ {new_count} 篇（已达上限）")
                return all_reports

        print(f"→ {new_count} 篇 (累计 {len(all_reports)})")

    return all_reports


# ─────────────────────────── Step 4: 下载 PDF ───────────────────────────

def sanitize_filename(s: str, max_len: int = 80) -> str:
    """清理文件名中的非法字符"""
    return re.sub(r'[\\/:*?"<>|\r\n]', "_", s)[:max_len]


def download_pdf(
    record: dict,
    target_dir: Path,
    dry_run: bool = False,
) -> tuple[str, str]:
    """
    下载单篇研报 PDF。
    返回: (status, filepath)
    status: "ok" | "skip" | "fail" | "dry"
    """
    info_code = record.get("infoCode", "")
    if not info_code:
        return "fail", ""

    date    = (record.get("publishDate") or "")[:10]
    org     = sanitize_filename(record.get("orgSName") or "未知", 20)
    title   = sanitize_filename(record.get("title") or "无标题", 60)
    rating  = sanitize_filename(record.get("emRatingName") or "", 10)
    fname   = f"{date}_{org}_{rating}_{title}.pdf".replace("__", "_")
    fpath   = target_dir / fname

    if fpath.exists() and fpath.stat().st_size > 1024:
        return "skip", str(fpath)

    if dry_run:
        return "dry", str(fpath)

    url = PDF_TPL.format(info_code=info_code)
    try:
        r = requests.get(
            url,
            headers={**COMMON_HEADERS, "Referer": "https://data.eastmoney.com/report/"},
            timeout=60,
            stream=True,
        )
        if r.status_code != 200:
            return "fail", ""
        content = r.content
        if len(content) < 1024:           # 疑似空文件或错误页
            return "fail", ""
        target_dir.mkdir(parents=True, exist_ok=True)
        fpath.write_bytes(content)
        return "ok", str(fpath)
    except Exception as e:
        print(f"\n  [WARN] 下载失败 {info_code}: {e}")
        return "fail", ""


def batch_download(
    reports:    list[dict],
    output_dir: Path,
    delay:      float = 0.5,
    dry_run:    bool = False,
) -> dict:
    """
    批量下载研报 PDF，打印进度，返回统计信息。
    """
    stats = {"ok": 0, "skip": 0, "fail": 0, "dry": 0}
    total = len(reports)

    print(f"\n{'[DRY RUN] ' if dry_run else ''}开始下载 {total} 篇研报 → {output_dir}\n")

    for idx, rec in enumerate(reports, 1):
        date   = (rec.get("publishDate") or "")[:10]
        org    = rec.get("orgSName") or "未知"
        title  = (rec.get("title") or "")[:50]
        rating = rec.get("emRatingName") or ""

        status, fpath = download_pdf(rec, output_dir, dry_run=dry_run)
        stats[status] += 1

        icon = {"ok": "✓", "skip": "↷", "fail": "✗", "dry": "○"}.get(status, "?")
        short_path = Path(fpath).name if fpath else "—"
        print(f"  [{idx:4d}/{total}] {icon} {date} [{org}] [{rating}] {title[:40]}")

        if status == "ok":
            time.sleep(delay)           # 下载成功后才等待，skip/fail 不等

    return stats


# ─────────────────────────── CLI 主入口 ───────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="按行业批量下载东财研报 PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--industry",  "-i", help="行业关键词，如 半导体、新能源汽车、白酒")
    parser.add_argument("--output",    "-o", default="./reports", help="PDF 保存目录（默认 ./reports）")
    parser.add_argument("--days",      "-d", type=int, default=180,
                        help="拉取最近 N 天的研报（默认 180）")
    parser.add_argument("--begin",     help="起始日期 YYYY-MM-DD（覆盖 --days）")
    parser.add_argument("--end",       help="截止日期 YYYY-MM-DD（默认今天）")
    parser.add_argument("--rating",    "-r", help="评级过滤，如 买入、增持（模糊匹配）")
    parser.add_argument("--keyword",   "-k", help="标题关键词过滤，如 深度报告、行业研究")
    parser.add_argument("--limit",     "-n", type=int, help="最多下载 N 篇（不限则全部）")
    parser.add_argument("--max-stocks", type=int, default=500, help="最多抓取行业内成分股数量（默认 500）")
    parser.add_argument("--max-pages-per-stock", type=int, default=3,
                        help="每只股票最多拉取研报页数（默认 3，每页 100 条）")
    parser.add_argument("--delay",     type=float, default=0.5,
                        help="PDF 下载间隔秒数（默认 0.5）")
    parser.add_argument("--dry-run",   action="store_true",
                        help="只列出研报清单，不实际下载 PDF")
    parser.add_argument("--list-industries", action="store_true",
                        help="列出所有可用行业，不下载")
    return parser.parse_args()


def main():
    args = parse_args()

    # ── 列出行业模式 ──
    if args.list_industries:
        print("正在获取东财行业列表...")
        industries = fetch_industry_list()
        print(f"\n共 {len(industries)} 个行业：\n")
        for i, ind in enumerate(industries, 1):
            print(f"  {i:3d}. {ind['name']:<12} {ind['code']}  "
                  f"涨跌 {ind['change_pct']:+.2f}%  "
                  f"↑{ind['up_count']} ↓{ind['down_count']}")
        return

    # ── 必须指定行业 ──
    if not args.industry:
        print("错误：请指定 --industry 行业关键词，或用 --list-industries 查看可用行业。")
        sys.exit(1)

    # ── 日期范围 ──
    end_date   = args.end   or datetime.today().strftime("%Y-%m-%d")
    begin_date = args.begin or (
        datetime.today() - timedelta(days=args.days)
    ).strftime("%Y-%m-%d")

    print(f"\n=== 东财行业研报批量下载 ===")
    print(f"行业关键词 : {args.industry}")
    print(f"日期范围   : {begin_date} ~ {end_date}")
    if args.rating:  print(f"评级过滤   : {args.rating}")
    if args.keyword: print(f"标题关键词 : {args.keyword}")
    if args.limit:   print(f"数量上限   : {args.limit} 篇")
    print(f"输出目录   : {args.output}")
    print()

    # ── Step 1: 拉行业列表，匹配行业 ──
    print("Step 1 · 获取行业列表...")
    industries = fetch_industry_list()
    matched = match_industry(args.industry, industries)

    if not matched:
        print(f"未找到匹配「{args.industry}」的行业。")
        print("可用行业示例：", [i["name"] for i in industries[:20]])
        print("运行 --list-industries 查看全部。")
        sys.exit(1)

    if len(matched) > 1:
        print(f"找到 {len(matched)} 个匹配行业：")
        for idx, m in enumerate(matched, 1):
            print(f"  {idx}. {m['name']} ({m['code']})")
        choice = input("请输入序号选择（默认 1）：").strip()
        idx = int(choice) - 1 if choice.isdigit() else 0
        target_industry = matched[max(0, min(idx, len(matched) - 1))]
    else:
        target_industry = matched[0]

    print(f"  ✓ 目标行业：{target_industry['name']} ({target_industry['code']})")

    # ── Step 2: 拉成分股 ──
    print(f"\nStep 2 · 获取成分股（上限 {args.max_stocks} 只）...")
    stocks = fetch_industry_stocks(target_industry["code"], max_stocks=args.max_stocks)
    print(f"  ✓ 共 {len(stocks)} 只成分股")

    if not stocks:
        print("成分股为空，退出。")
        sys.exit(1)

    # ── Step 3: 拉研报列表 + 去重 ──
    print(f"\nStep 3 · 拉取研报列表（每股最多 {args.max_pages_per_stock} 页 × 100 条）...")
    reports = fetch_reports_for_industry(
        stocks,
        begin_date=begin_date,
        end_date=end_date,
        rating_filter=args.rating,
        keyword_filter=args.keyword,
        max_pages_per_stock=args.max_pages_per_stock,
        report_limit=args.limit,
    )

    # 按发布日期倒序排列
    reports.sort(key=lambda r: r.get("publishDate") or "", reverse=True)

    print(f"\n  ✓ 去重后共 {len(reports)} 篇研报")

    if not reports:
        print("没有符合条件的研报，退出。")
        sys.exit(0)

    # ── 打印摘要表格 ──
    print(f"\n{'─'*80}")
    print(f"{'日期':<12} {'机构':<10} {'评级':<6} {'标题'}")
    print(f"{'─'*80}")
    for rec in reports[:20]:
        date   = (rec.get("publishDate") or "")[:10]
        org    = (rec.get("orgSName") or "")[:10]
        rating = (rec.get("emRatingName") or "")[:6]
        title  = (rec.get("title") or "")[:50]
        print(f"{date:<12} {org:<10} {rating:<6} {title}")
    if len(reports) > 20:
        print(f"  ... 共 {len(reports)} 篇，仅展示前 20 条")
    print(f"{'─'*80}")

    # ── Step 4: 批量下载 PDF ──
    output_dir = Path(args.output) / sanitize_filename(target_industry["name"])
    stats = batch_download(
        reports,
        output_dir=output_dir,
        delay=args.delay,
        dry_run=args.dry_run,
    )

    # ── 最终统计 ──
    print(f"\n{'='*40}")
    print(f"下载完成！")
    print(f"  ✓ 成功 : {stats['ok']} 篇")
    print(f"  ↷ 跳过 : {stats['skip']} 篇（已存在）")
    print(f"  ✗ 失败 : {stats['fail']} 篇")
    if args.dry_run:
        print(f"  ○ 预览 : {stats['dry']} 篇（dry-run 模式，未实际下载）")
    print(f"  📁 目录 : {output_dir.resolve()}")


if __name__ == "__main__":
    main()
