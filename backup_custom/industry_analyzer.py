#!/usr/bin/env python3
"""
industry_analyzer.py
====================
研报文件夹 → 产业链结构化分析 → 多 Tab HTML 看板

配套 industry_report_downloader.py 使用：先按行业批量下载研报 PDF，
再用本脚本读取整个文件夹，抽取文本、调用 LLM 做产业链分析，
最后结合 tencent_quote 实时行情，生成 industry_dashboard.py 看板。

完整流水线
----------
  ① 加载 PDF       读取文件夹内全部 PDF
  ② 文本抽取       pdfplumber → pypdf → pdfminer 优雅降级
  ③ LLM map        逐篇抽取关键事实（成本/BOM/龙头/壁垒/风险/估值线索）
  ④ LLM reduce     合成结构化分析 JSON（严格 schema）
  ⑤ 估值补全       对核心标的调 tencent_quote 拉实时 现价/PE/PB/市值
  ⑥ 渲染看板       industry_dashboard.render_dashboard → analysis.html

依赖
----
pip install requests pdfplumber            # 或 pypdf / pdfminer.six
LLM 走 OpenAI 兼容接口，通过环境变量配置：
  export LLM_API_KEY="sk-..."
  export LLM_BASE_URL="https://api.openai.com/v1"   # DeepSeek/Moonshot/Qwen/本地Ollama 均可
  export LLM_MODEL="gpt-4o-mini"

用法
----
# 分析整个文件夹，生成看板
python industry_analyzer.py --input ./reports/半导体 --industry 半导体 -o 半导体看板.html

# 只跑文本抽取与 LLM 分析，导出中间 JSON（便于调试 / 二次渲染）
python industry_analyzer.py --input ./reports/半导体 --industry 半导体 --dump-json analysis.json

# 已有 analysis.json，跳过 LLM，仅补全估值并渲染
python industry_analyzer.py --from-json analysis.json -o 看板.html

# 不调 LLM（无 Key 时），用占位骨架 + 估值层，先看看流程
python industry_analyzer.py --input ./reports/半导体 --industry 半导体 --no-llm
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from industry_dashboard import render_dashboard

# ─────────────────────────── 全局常量 ───────────────────────────

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

LLM_API_KEY  = os.environ.get("LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
LLM_MODEL    = os.environ.get("LLM_MODEL", "gpt-4o-mini")


# ─────────────────────────── Step ②: PDF 文本抽取 ───────────────────────────

def _extract_with_pdfplumber(path: Path, max_pages: int) -> str:
    import pdfplumber
    chunks = []
    with pdfplumber.open(str(path)) as pdf:
        for i, page in enumerate(pdf.pages):
            if i >= max_pages:
                break
            chunks.append(page.extract_text() or "")
    return "\n".join(chunks)


def _extract_with_pypdf(path: Path, max_pages: int) -> str:
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    chunks = []
    for i, page in enumerate(reader.pages):
        if i >= max_pages:
            break
        chunks.append(page.extract_text() or "")
    return "\n".join(chunks)


def _extract_with_pdfminer(path: Path, max_pages: int) -> str:
    from pdfminer.high_level import extract_text
    return extract_text(str(path), maxpages=max_pages) or ""


def extract_pdf_text(path: Path, max_pages: int = 30) -> str:
    """优雅降级抽取 PDF 文本：pdfplumber → pypdf → pdfminer"""
    for fn in (_extract_with_pdfplumber, _extract_with_pypdf, _extract_with_pdfminer):
        try:
            txt = fn(path, max_pages)
            if txt and txt.strip():
                return txt
        except ImportError:
            continue
        except Exception as e:
            print(f"    [WARN] {fn.__name__} 抽取 {path.name} 失败: {e}")
            continue
    return ""


def load_corpus(folder: str, max_pages: int = 30, max_files: int | None = None) -> list[dict]:
    """
    读取文件夹内全部 PDF，抽取文本。
    返回: [{"file": "xxx.pdf", "text": "..."}]
    """
    root = Path(folder)
    if not root.exists():
        raise FileNotFoundError(f"目录不存在: {folder}")

    pdfs = sorted(root.rglob("*.pdf"))
    if max_files:
        pdfs = pdfs[:max_files]

    if not pdfs:
        raise FileNotFoundError(f"目录内未找到 PDF: {folder}")

    print(f"  发现 {len(pdfs)} 个 PDF，开始抽取文本...")
    corpus = []
    for i, p in enumerate(pdfs, 1):
        text = extract_pdf_text(p, max_pages=max_pages)
        status = f"{len(text)} 字符" if text else "空(可能为扫描件/图片)"
        print(f"  [{i:3d}/{len(pdfs)}] {p.name[:50]:<50} → {status}")
        if text:
            corpus.append({"file": p.name, "text": text})
    return corpus


# ─────────────────────────── LLM 客户端（OpenAI 兼容） ───────────────────────────

def llm_chat(messages: list[dict], temperature: float = 0.2,
             max_tokens: int = 4096, retries: int = 2) -> str:
    """调用 OpenAI 兼容 /chat/completions 接口，返回文本内容"""
    if not LLM_API_KEY:
        raise RuntimeError("未设置 LLM_API_KEY 环境变量")

    url = f"{LLM_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    last_err = None
    for attempt in range(retries + 1):
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=120)
            if r.status_code != 200:
                last_err = f"HTTP {r.status_code}: {r.text[:200]}"
                time.sleep(2 * (attempt + 1))
                continue
            data = r.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            last_err = str(e)
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"LLM 调用失败: {last_err}")


def _parse_json_loose(text: str) -> Any:
    """从 LLM 输出中宽松解析 JSON（容忍 ```json 代码块包裹）"""
    text = text.strip()
    # 去掉 markdown 代码块围栏
    m = re.search(r"```(?:json)?\s*(.+?)\s*```", text, re.DOTALL)
    if m:
        text = m.group(1).strip()
    # 截取首个 { 到末个 }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]
    return json.loads(text)


# ─────────────────────────── Step ③: LLM map（逐篇抽取事实） ───────────────────────────

MAP_SYSTEM = (
    "你是资深产业链证券分析师。下面是一篇研报的正文片段，请抽取与【产业链结构】相关的"
    "关键事实，输出简洁中文要点（不超过 400 字）。重点关注：\n"
    "1) 产业链/赛道环节划分与各环节成本占比\n"
    "2) BOM 组成、单机用量\n"
    "3) 各模块龙头公司（含股票代码）及其竞争优势、技术壁垒、工艺\n"
    "4) 替代风险、技术路线之争、安全/壁垒高的环节\n"
    "5) 核心标的的业绩增速、估值线索、不可替代性\n"
    "只输出要点本身，不要客套话。若该片段无相关信息，输出『无相关信息』。"
)


def map_reports(corpus: list[dict], max_chars: int = 6000,
                use_llm: bool = True) -> list[dict]:
    """对每篇研报抽取关键事实。返回 [{"file","facts"}]"""
    facts = []
    total = len(corpus)
    for i, doc in enumerate(corpus, 1):
        text = doc["text"][:max_chars]
        if not use_llm:
            facts.append({"file": doc["file"], "facts": text[:1200]})
            continue
        print(f"  [map {i:3d}/{total}] {doc['file'][:45]} ...", end="", flush=True)
        try:
            out = llm_chat(
                [{"role": "system", "content": MAP_SYSTEM},
                 {"role": "user", "content": text}],
                temperature=0.1, max_tokens=800,
            )
            if "无相关信息" not in out:
                facts.append({"file": doc["file"], "facts": out.strip()})
            print(" ✓")
        except Exception as e:
            print(f" ✗ ({e})")
        time.sleep(0.2)
    return facts


# ─────────────────────────── Step ④: LLM reduce（合成结构化 JSON） ───────────────────────────

REDUCE_SCHEMA_HINT = """{
  "overview": {
    "panorama": "产业全景，一段话概述产业链结构与价值量分布",
    "cost_structure": [{"module":"模块名","pct":数字(百分比),"note":"说明"}],
    "module_importance": [{"module":"","importance":"高/中/低","score":1-10整数,"reason":""}],
    "module_leaders": [{"module":"","leaders":["公司A","公司B"],"note":""}],
    "leader_replaceability": [{"module":"","replaceable":"难/中/易","reason":""}],
    "bom": [{"component":"零部件","pct":数字,"qty":"单机用量","suppliers":["供应商"],"note":""}],
    "milestones": [{"date":"如2024Q1","event":"事件"}]
  },
  "cost_components": [
    {"name":"零部件名","cost_pct":数字,"process":"工艺路线","companies":[{"name":"公司","code":"6位代码"}],"advantages":"优势","barriers":"技术壁垒"}
  ],
  "substitution_risk": {
    "risks": [{"module":"","level":"高/中/低","risk":"风险描述"}],
    "safe_tracks": [{"module":"","reason":"为何是安全赛道"}]
  },
  "valuation": [
    {"name":"公司名","code":"6位股票代码","module":"所属零部件模块","growth":"如30%","irreplaceability":"高/中/低"}
  ]
}"""

REDUCE_SYSTEM = (
    "你是资深产业链证券分析师。下面是从多篇研报中抽取的关键事实汇总。"
    "请综合这些信息，输出一份覆盖整个产业链的结构化分析，严格按照给定 JSON schema 输出。\n\n"
    "要求：\n"
    "- 只输出 JSON，不要任何解释文字或 markdown 代码块；\n"
    "- cost_components 选取 3-6 个最核心的零部件分别展开（工艺/标的企业/优势/技术壁垒）；\n"
    "- valuation 列出研报中提及的核心标的，code 必须是 6 位 A 股代码（如 688017），"
    "不确定代码就留空字符串；不要编造现价/PE/PB（这些由程序后续填充，不要输出）；\n"
    "- 所有 pct 字段用数字（不带 % 号）；\n"
    "- 中文输出，信息以研报事实为准，不臆造。\n\n"
    f"JSON schema:\n{REDUCE_SCHEMA_HINT}"
)


def reduce_facts(industry: str, facts: list[dict],
                 max_chars: int = 40000) -> dict:
    """把所有研报事实合成为最终结构化分析 JSON"""
    merged = "\n\n".join(f"【来自 {f['file']}】\n{f['facts']}" for f in facts)
    if len(merged) > max_chars:
        merged = merged[:max_chars] + "\n...(已截断)"

    user = f"行业/产业：{industry}\n\n以下是从 {len(facts)} 篇研报抽取的关键事实：\n\n{merged}"
    out = llm_chat(
        [{"role": "system", "content": REDUCE_SYSTEM},
         {"role": "user", "content": user}],
        temperature=0.2, max_tokens=4096,
    )
    return _parse_json_loose(out)


def empty_skeleton() -> dict:
    """无 LLM 时的空骨架，保证看板结构完整"""
    return {
        "overview": {
            "panorama": "（未启用 LLM 分析，此处为占位。请配置 LLM_API_KEY 后重新运行。）",
            "cost_structure": [], "module_importance": [], "module_leaders": [],
            "leader_replaceability": [], "bom": [], "milestones": [],
        },
        "cost_components": [],
        "substitution_risk": {"risks": [], "safe_tracks": []},
        "valuation": [],
    }


# ─────────────────────────── Step ⑤: 估值层实时补全 ───────────────────────────

def tencent_quote(codes: list[str]) -> dict[str, dict]:
    """
    腾讯财经批量实时行情（自包含，复用 SKILL.md 端点）。
    返回: {code: {name, price, pe_ttm, pb, mcap_yi}}
    """
    if not codes:
        return {}
    prefixed = []
    for c in codes:
        c = str(c)
        if c.startswith(("6", "9")):
            prefixed.append(f"sh{c}")
        elif c.startswith("8"):
            prefixed.append(f"bj{c}")
        else:
            prefixed.append(f"sz{c}")

    url = "https://qt.gtimg.cn/q=" + ",".join(prefixed)
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.encoding = "gbk"
        data = r.text
    except Exception as e:
        print(f"  [WARN] 腾讯行情请求失败: {e}")
        return {}

    result = {}
    for line in data.strip().split(";"):
        if "=" not in line or '"' not in line:
            continue
        key = line.split("=")[0].split("_")[-1]
        vals = line.split('"')[1].split("~")
        if len(vals) < 53:
            continue
        code = key[2:]
        result[code] = {
            "name":    vals[1],
            "price":   float(vals[3]) if vals[3] else None,
            "pe_ttm":  float(vals[39]) if vals[39] else None,
            "mcap_yi": float(vals[44]) if vals[44] else None,
            "pb":      float(vals[46]) if vals[46] else None,
        }
    return result


def enrich_valuation(analysis: dict) -> dict:
    """对 valuation 列表中的标的补全实时 现价/PE/PB/市值"""
    val = analysis.get("valuation", []) or []
    codes = [str(v.get("code", "")).strip() for v in val if str(v.get("code", "")).strip().isdigit()]
    codes = [c for c in codes if len(c) == 6]
    if not codes:
        print("  (估值层无有效 6 位代码，跳过行情补全)")
        return analysis

    print(f"  拉取 {len(codes)} 只标的实时行情...")
    quotes = tencent_quote(codes)
    for v in val:
        code = str(v.get("code", "")).strip()
        q = quotes.get(code)
        if q:
            v["price"] = q.get("price")
            v["pe"]    = q.get("pe_ttm")
            v["pb"]    = q.get("pb")
            v["mcap"]  = q.get("mcap_yi")
            if not v.get("name") and q.get("name"):
                v["name"] = q["name"]
    return analysis


# ─────────────────────────── 主流水线 ───────────────────────────

def analyze(
    input_dir: str,
    industry: str,
    use_llm: bool = True,
    max_pages: int = 30,
    max_files: int | None = None,
    map_chars: int = 6000,
) -> dict:
    """完整分析流水线，返回 analysis dict"""
    print("Step ① ② · 加载并抽取 PDF 文本")
    corpus = load_corpus(input_dir, max_pages=max_pages, max_files=max_files)
    report_count = len(corpus)

    if use_llm and LLM_API_KEY:
        print(f"\nStep ③ · LLM 逐篇抽取关键事实（模型 {LLM_MODEL}）")
        facts = map_reports(corpus, max_chars=map_chars, use_llm=True)
        print(f"  ✓ 抽得 {len(facts)} 篇有效事实")

        print("\nStep ④ · LLM 合成结构化分析 JSON")
        try:
            analysis = reduce_facts(industry, facts)
        except Exception as e:
            print(f"  [ERROR] reduce 失败，退回空骨架: {e}")
            analysis = empty_skeleton()
    else:
        if use_llm and not LLM_API_KEY:
            print("\n[提示] 未设置 LLM_API_KEY，跳过 LLM 分析，使用空骨架。")
        else:
            print("\n[--no-llm] 跳过 LLM 分析，使用空骨架。")
        analysis = empty_skeleton()

    # 元信息
    analysis["industry"] = industry
    analysis["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    analysis["report_count"] = report_count
    analysis["source_dir"] = input_dir

    print("\nStep ⑤ · 估值层实时行情补全")
    analysis = enrich_valuation(analysis)

    return analysis


# ─────────────────────────── CLI ───────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="研报文件夹 → 产业链结构化分析 → 多 Tab HTML 看板",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", "-i", help="研报 PDF 文件夹（industry_report_downloader 的产物）")
    parser.add_argument("--industry", help="行业/产业名称，用于看板标题与 LLM 提示")
    parser.add_argument("--output", "-o", default="analysis.html", help="输出 HTML 路径（默认 analysis.html）")
    parser.add_argument("--dump-json", help="同时导出中间分析 JSON 到指定路径")
    parser.add_argument("--from-json", help="跳过 PDF/LLM，直接从已有 analysis.json 渲染（仍会补全估值）")
    parser.add_argument("--no-llm", action="store_true", help="不调用 LLM，仅生成骨架 + 估值层（用于调试流程）")
    parser.add_argument("--max-pages", type=int, default=30, help="每篇 PDF 最多抽取页数（默认 30）")
    parser.add_argument("--max-files", type=int, help="最多处理 PDF 数量（默认全部）")
    parser.add_argument("--map-chars", type=int, default=6000, help="每篇研报送入 LLM 的最大字符数（默认 6000）")
    parser.add_argument("--no-quote", action="store_true", help="不补全实时行情")
    return parser.parse_args()


def main():
    args = parse_args()

    # ── 从已有 JSON 渲染 ──
    if args.from_json:
        analysis = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
        if not args.no_quote:
            print("Step ⑤ · 估值层实时行情补全")
            analysis = enrich_valuation(analysis)
        path = render_dashboard(analysis, args.output)
        print(f"\n✓ 看板已生成: {path}")
        return

    # ── 完整流水线 ──
    if not args.input or not args.industry:
        print("错误：需指定 --input 研报文件夹 与 --industry 行业名称。")
        print("（或用 --from-json analysis.json 直接渲染已有分析结果）")
        sys.exit(1)

    print(f"\n=== 产业链研报分析 → HTML 看板 ===")
    print(f"研报目录 : {args.input}")
    print(f"行业     : {args.industry}")
    print(f"LLM      : {'禁用' if args.no_llm else (LLM_MODEL if LLM_API_KEY else '未配置 Key')}")
    print(f"输出      : {args.output}\n")

    analysis = analyze(
        input_dir=args.input,
        industry=args.industry,
        use_llm=not args.no_llm,
        max_pages=args.max_pages,
        max_files=args.max_files,
        map_chars=args.map_chars,
    )

    if args.no_quote:
        # analyze 内部已补全；如需关闭，清空行情字段
        for v in analysis.get("valuation", []):
            for k in ("price", "pe", "pb", "mcap"):
                v.pop(k, None)

    if args.dump_json:
        Path(args.dump_json).write_text(
            json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n✓ 中间分析 JSON 已导出: {Path(args.dump_json).resolve()}")

    print("\nStep ⑥ · 渲染 HTML 看板")
    path = render_dashboard(analysis, args.output)

    print(f"\n{'='*44}")
    print(f"✓ 分析完成！")
    print(f"  研报篇数 : {analysis.get('report_count', 0)}")
    print(f"  核心标的 : {len(analysis.get('valuation', []))} 只")
    print(f"  看板文件 : {path}")


if __name__ == "__main__":
    main()
