#!/usr/bin/env python3
"""
industry_dashboard.py
=====================
产业链研报分析 → 多 Tab HTML 看板渲染器（纯标准库，零依赖）

输入：industry_analyzer.py 产出的 analysis dict（或 analysis.json）
输出：自包含单文件 HTML（内嵌 CSS + JS，可离线打开）

看板结构（4 个 Tab）
--------------------
1. 总览      产业全景 / 赛道成本构成 / 模块重要性 / 模块龙头 / 龙头可替代性 / BOM 表 / 产业里程碑
2. 成本构成  各零部件成本占比 + 逐个零部件分析（工艺 / 标的企业 / 优势 / 技术壁垒）
3. 替代风险  风险清单 + 安全赛道
4. 估值全景  核心标的：名称 / 代码 / 所属模块 / 现价 / PE / PB / 市值 / 增速 / 不可替代性

用法
----
from industry_dashboard import render_dashboard
render_dashboard(analysis_dict, "analysis.html")

# 或直接渲染一个 JSON 文件
python industry_dashboard.py analysis.json -o analysis.html

# 不带参数时渲染一份内置示例数据，用于预览样式
python industry_dashboard.py --demo -o demo.html
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


# ─────────────────────────── 小工具 ───────────────────────────

def esc(v: Any) -> str:
    """HTML 转义，None → 空字符串"""
    if v is None:
        return ""
    return html.escape(str(v))


def fmt_num(v: Any, suffix: str = "", digits: int = 2) -> str:
    """数字格式化；空值返回 '—'"""
    if v is None or v == "":
        return "—"
    try:
        f = float(v)
        if digits == 0:
            return f"{f:,.0f}{suffix}"
        return f"{f:,.{digits}f}{suffix}"
    except (ValueError, TypeError):
        return f"{esc(v)}{suffix}"


def level_class(level: str) -> str:
    """风险/重要性等级 → CSS class"""
    s = str(level or "")
    if any(k in s for k in ("高", "难", "强", "大")):
        return "lv-high"
    if any(k in s for k in ("中", "一般")):
        return "lv-mid"
    if any(k in s for k in ("低", "易", "弱", "小")):
        return "lv-low"
    return "lv-mid"


# ─────────────────────────── 各 Tab 渲染 ───────────────────────────

def _render_cost_bars(cost_structure: list[dict]) -> str:
    """赛道成本构成 → 水平条形图"""
    if not cost_structure:
        return '<p class="empty">暂无成本构成数据</p>'
    rows = sorted(cost_structure, key=lambda x: float(x.get("pct") or 0), reverse=True)
    max_pct = max((float(r.get("pct") or 0) for r in rows), default=100) or 100
    out = ['<div class="bars">']
    for r in rows:
        pct = float(r.get("pct") or 0)
        width = pct / max_pct * 100
        note = esc(r.get("note", ""))
        out.append(f"""
        <div class="bar-row" title="{note}">
          <div class="bar-label">{esc(r.get('module',''))}</div>
          <div class="bar-track"><div class="bar-fill" style="width:{width:.1f}%"></div></div>
          <div class="bar-val">{pct:.1f}%</div>
        </div>""")
    out.append("</div>")
    return "".join(out)


def _render_overview(ov: dict) -> str:
    parts = ['<div class="tab-pane" id="tab-overview">']

    # 产业全景
    parts.append(f"""
    <section class="card span-2">
      <h3>🌐 产业全景</h3>
      <p class="prose">{esc(ov.get('panorama','')) or '暂无'}</p>
    </section>""")

    # 赛道成本构成
    parts.append(f"""
    <section class="card">
      <h3>💰 赛道成本构成</h3>
      {_render_cost_bars(ov.get('cost_structure', []))}
    </section>""")

    # 模块重要性
    mi = ov.get("module_importance", [])
    mi_rows = "".join(
        f"""<tr>
          <td>{esc(m.get('module',''))}</td>
          <td><span class="badge {level_class(m.get('importance',''))}">{esc(m.get('importance',''))}</span></td>
          <td class="score">{esc(m.get('score','')) if m.get('score') not in (None,'') else '—'}</td>
          <td class="muted">{esc(m.get('reason',''))}</td>
        </tr>"""
        for m in mi
    ) or '<tr><td colspan="4" class="empty">暂无数据</td></tr>'
    parts.append(f"""
    <section class="card">
      <h3>⭐ 模块重要性</h3>
      <table class="grid">
        <thead><tr><th>模块</th><th>重要性</th><th>评分</th><th>理由</th></tr></thead>
        <tbody>{mi_rows}</tbody>
      </table>
    </section>""")

    # 模块龙头
    ml = ov.get("module_leaders", [])
    ml_rows = "".join(
        f"""<tr>
          <td>{esc(m.get('module',''))}</td>
          <td>{''.join(f'<span class="chip">{esc(x)}</span>' for x in (m.get('leaders') or [])) or '—'}</td>
          <td class="muted">{esc(m.get('note',''))}</td>
        </tr>"""
        for m in ml
    ) or '<tr><td colspan="3" class="empty">暂无数据</td></tr>'
    parts.append(f"""
    <section class="card">
      <h3>🏆 模块龙头</h3>
      <table class="grid">
        <thead><tr><th>模块</th><th>龙头企业</th><th>备注</th></tr></thead>
        <tbody>{ml_rows}</tbody>
      </table>
    </section>""")

    # 龙头能否被替代
    lr = ov.get("leader_replaceability", [])
    lr_rows = "".join(
        f"""<tr>
          <td>{esc(m.get('module',''))}</td>
          <td><span class="badge {level_class(m.get('replaceable',''))}">{esc(m.get('replaceable',''))}</span></td>
          <td class="muted">{esc(m.get('reason',''))}</td>
        </tr>"""
        for m in lr
    ) or '<tr><td colspan="3" class="empty">暂无数据</td></tr>'
    parts.append(f"""
    <section class="card">
      <h3>🔄 龙头能否被替代</h3>
      <table class="grid">
        <thead><tr><th>模块</th><th>替代难度</th><th>理由</th></tr></thead>
        <tbody>{lr_rows}</tbody>
      </table>
    </section>""")

    # BOM 表
    bom = ov.get("bom", [])
    bom_rows = "".join(
        f"""<tr>
          <td>{esc(b.get('component',''))}</td>
          <td class="num">{fmt_num(b.get('pct'),'%',1)}</td>
          <td>{esc(b.get('qty',''))}</td>
          <td>{''.join(f'<span class="chip">{esc(x)}</span>' for x in (b.get('suppliers') or [])) or '—'}</td>
          <td class="muted">{esc(b.get('note',''))}</td>
        </tr>"""
        for b in bom
    ) or '<tr><td colspan="5" class="empty">暂无数据</td></tr>'
    parts.append(f"""
    <section class="card span-2">
      <h3>📋 BOM 表组成</h3>
      <table class="grid">
        <thead><tr><th>零部件</th><th>成本占比</th><th>单机用量</th><th>供应商</th><th>备注</th></tr></thead>
        <tbody>{bom_rows}</tbody>
      </table>
    </section>""")

    # 产业里程碑
    ms = ov.get("milestones", [])
    ms_items = "".join(
        f"""<li><span class="ms-date">{esc(m.get('date',''))}</span>
            <span class="ms-event">{esc(m.get('event',''))}</span></li>"""
        for m in ms
    ) or '<li class="empty">暂无里程碑数据</li>'
    parts.append(f"""
    <section class="card span-2">
      <h3>🗓️ 产业里程碑</h3>
      <ul class="timeline">{ms_items}</ul>
    </section>""")

    parts.append("</div>")
    return "".join(parts)


def _render_cost(components: list[dict]) -> str:
    parts = ['<div class="tab-pane" id="tab-cost" hidden>']

    # 顶部：各零部件成本占比汇总
    summary = [{"module": c.get("name", ""), "pct": c.get("cost_pct"), "note": ""} for c in components]
    parts.append(f"""
    <section class="card span-2">
      <h3>🧩 各零部件成本构成</h3>
      {_render_cost_bars(summary)}
    </section>""")

    # 逐个零部件分析卡片
    if not components:
        parts.append('<section class="card span-2"><p class="empty">暂无零部件分析</p></section>')
    for i, c in enumerate(components, 1):
        companies = c.get("companies") or []
        comp_chips = "".join(
            f'<span class="chip">{esc(x.get("name",""))}'
            + (f' <code>{esc(x.get("code",""))}</code>' if x.get("code") else "")
            + "</span>"
            for x in companies
        ) or "—"
        parts.append(f"""
        <section class="card comp-card">
          <h3><span class="comp-idx">零部件 {i}</span> {esc(c.get('name',''))}
            <span class="comp-pct">{fmt_num(c.get('cost_pct'),'%',1)}</span></h3>
          <div class="kv"><span class="k">🔧 工艺</span><span class="v">{esc(c.get('process','')) or '—'}</span></div>
          <div class="kv"><span class="k">🏢 标的企业</span><span class="v">{comp_chips}</span></div>
          <div class="kv"><span class="k">💪 优势</span><span class="v">{esc(c.get('advantages','')) or '—'}</span></div>
          <div class="kv"><span class="k">🛡️ 技术壁垒</span><span class="v">{esc(c.get('barriers','')) or '—'}</span></div>
        </section>""")

    parts.append("</div>")
    return "".join(parts)


def _render_risk(risk: dict) -> str:
    parts = ['<div class="tab-pane" id="tab-risk" hidden>']

    risks = risk.get("risks", [])
    risk_rows = "".join(
        f"""<tr>
          <td>{esc(r.get('module',''))}</td>
          <td><span class="badge {level_class(r.get('level',''))}">{esc(r.get('level',''))}</span></td>
          <td>{esc(r.get('risk',''))}</td>
        </tr>"""
        for r in risks
    ) or '<tr><td colspan="3" class="empty">暂无风险数据</td></tr>'
    parts.append(f"""
    <section class="card">
      <h3>⚠️ 替代 / 竞争风险</h3>
      <table class="grid">
        <thead><tr><th>模块</th><th>风险等级</th><th>风险描述</th></tr></thead>
        <tbody>{risk_rows}</tbody>
      </table>
    </section>""")

    safe = risk.get("safe_tracks", [])
    safe_rows = "".join(
        f"""<tr>
          <td>{esc(s.get('module',''))}</td>
          <td class="muted">{esc(s.get('reason',''))}</td>
        </tr>"""
        for s in safe
    ) or '<tr><td colspan="2" class="empty">暂无数据</td></tr>'
    parts.append(f"""
    <section class="card">
      <h3>🛡️ 安全赛道</h3>
      <table class="grid">
        <thead><tr><th>模块</th><th>安全理由</th></tr></thead>
        <tbody>{safe_rows}</tbody>
      </table>
    </section>""")

    parts.append("</div>")
    return "".join(parts)


def _render_valuation(valuation: list[dict]) -> str:
    rows = "".join(
        f"""<tr>
          <td class="name">{esc(v.get('name',''))}</td>
          <td><code>{esc(v.get('code',''))}</code></td>
          <td><span class="chip">{esc(v.get('module',''))}</span></td>
          <td class="num">{fmt_num(v.get('price'),'',2)}</td>
          <td class="num">{fmt_num(v.get('pe'),'',1)}</td>
          <td class="num">{fmt_num(v.get('pb'),'',2)}</td>
          <td class="num">{fmt_num(v.get('mcap'),'亿',0)}</td>
          <td class="num">{esc(v.get('growth','')) or '—'}</td>
          <td><span class="badge {level_class(v.get('irreplaceability',''))}">{esc(v.get('irreplaceability',''))}</span></td>
        </tr>"""
        for v in valuation
    ) or '<tr><td colspan="9" class="empty">暂无估值数据</td></tr>'
    return f"""
    <div class="tab-pane" id="tab-valuation" hidden>
      <section class="card span-2">
        <h3>📊 核心标的估值一览</h3>
        <p class="muted small">现价 / PE / PB / 市值为 tencent_quote 实时拉取；增速与不可替代性来自研报分析。</p>
        <table class="grid valuation">
          <thead><tr>
            <th>名称</th><th>代码</th><th>所属模块</th><th>现价</th>
            <th>PE(TTM)</th><th>PB</th><th>总市值</th><th>增速</th><th>不可替代性</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </section>
    </div>"""


# ─────────────────────────── CSS / JS ───────────────────────────

_CSS = """
:root{
  --bg:#0f1419; --panel:#1a212b; --panel2:#212b38; --line:#2c3947;
  --txt:#e6edf3; --muted:#8b97a6; --accent:#4ea1ff; --accent2:#2d7fd6;
  --high:#ff5d5d; --mid:#ffb454; --low:#3fd17f; --chip:#26384d;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",Segoe UI,Roboto,sans-serif;
  background:var(--bg);color:var(--txt);line-height:1.6;font-size:14px}
header{padding:24px 32px;border-bottom:1px solid var(--line);
  background:linear-gradient(180deg,#16202c,#0f1419)}
header h1{font-size:22px;font-weight:700}
header .meta{color:var(--muted);font-size:13px;margin-top:6px;display:flex;gap:18px;flex-wrap:wrap}
header .meta b{color:var(--accent)}
.tabs{display:flex;gap:4px;padding:0 32px;background:var(--panel);
  border-bottom:1px solid var(--line);position:sticky;top:0;z-index:10}
.tab-btn{padding:14px 22px;background:none;border:none;color:var(--muted);
  font-size:15px;cursor:pointer;border-bottom:3px solid transparent;font-weight:600}
.tab-btn:hover{color:var(--txt)}
.tab-btn.active{color:var(--accent);border-bottom-color:var(--accent)}
main{padding:24px 32px;max-width:1400px;margin:0 auto}
.tab-pane{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:20px}
.card.span-2{grid-column:1 / -1}
.card h3{font-size:16px;margin-bottom:14px;font-weight:700;display:flex;
  align-items:center;gap:8px;flex-wrap:wrap}
.prose{color:#cdd7e2;white-space:pre-wrap}
.muted{color:var(--muted)}
.small{font-size:12px}
.empty{color:var(--muted);text-align:center;padding:16px;font-style:italic}
table.grid{width:100%;border-collapse:collapse;font-size:13px}
table.grid th{text-align:left;padding:9px 10px;color:var(--muted);
  border-bottom:2px solid var(--line);font-weight:600;white-space:nowrap}
table.grid td{padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
table.grid tr:hover td{background:var(--panel2)}
td.num{text-align:right;font-variant-numeric:tabular-nums}
td.name{font-weight:600}
td.score{text-align:center;font-weight:700;color:var(--accent)}
code{background:#0d1117;padding:1px 6px;border-radius:4px;font-size:12px;color:#9cc7ff}
.chip{display:inline-block;background:var(--chip);color:#bcd4ea;padding:2px 9px;
  border-radius:20px;font-size:12px;margin:2px 3px 2px 0}
.badge{display:inline-block;padding:2px 11px;border-radius:6px;font-size:12px;font-weight:700}
.lv-high{background:rgba(255,93,93,.16);color:var(--high)}
.lv-mid{background:rgba(255,180,84,.16);color:var(--mid)}
.lv-low{background:rgba(63,209,127,.16);color:var(--low)}
.bars{display:flex;flex-direction:column;gap:9px}
.bar-row{display:grid;grid-template-columns:110px 1fr 56px;align-items:center;gap:10px}
.bar-label{font-size:13px;color:#cdd7e2;text-align:right;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap}
.bar-track{background:#0d1117;border-radius:6px;height:18px;overflow:hidden}
.bar-fill{height:100%;background:linear-gradient(90deg,var(--accent2),var(--accent));border-radius:6px}
.bar-val{font-size:13px;font-variant-numeric:tabular-nums;color:var(--accent);font-weight:600}
.timeline{list-style:none;border-left:2px solid var(--line);margin-left:8px}
.timeline li{position:relative;padding:6px 0 14px 22px}
.timeline li::before{content:"";position:absolute;left:-7px;top:11px;width:12px;height:12px;
  border-radius:50%;background:var(--accent);border:2px solid var(--panel)}
.ms-date{display:inline-block;color:var(--accent);font-weight:700;margin-right:10px;min-width:70px}
.ms-event{color:#cdd7e2}
.comp-card .kv{display:grid;grid-template-columns:90px 1fr;gap:10px;padding:7px 0;
  border-bottom:1px solid var(--line)}
.comp-card .kv:last-child{border-bottom:none}
.comp-card .k{color:var(--muted);font-size:13px}
.comp-card .v{color:#cdd7e2}
.comp-idx{background:var(--accent2);color:#fff;padding:2px 9px;border-radius:6px;font-size:12px}
.comp-pct{margin-left:auto;color:var(--accent);font-weight:700}
footer{color:var(--muted);font-size:12px;text-align:center;padding:24px;border-top:1px solid var(--line);margin-top:20px}
@media(max-width:900px){.tab-pane{grid-template-columns:1fr}.card.span-2{grid-column:1}}
"""

_JS = """
function switchTab(id, btn){
  document.querySelectorAll('.tab-pane').forEach(function(p){p.hidden = (p.id !== id);});
  document.querySelectorAll('.tab-btn').forEach(function(b){b.classList.remove('active');});
  btn.classList.add('active');
}
"""


# ─────────────────────────── 主渲染函数 ───────────────────────────

def render_html(analysis: dict) -> str:
    """把 analysis dict 渲染为完整 HTML 字符串"""
    ov   = analysis.get("overview", {}) or {}
    comp = analysis.get("cost_components", []) or []
    risk = analysis.get("substitution_risk", {}) or {}
    val  = analysis.get("valuation", []) or []

    industry = esc(analysis.get("industry", "未命名行业"))
    gen_at   = esc(analysis.get("generated_at", ""))
    n_report = esc(analysis.get("report_count", 0))
    src      = esc(analysis.get("source_dir", ""))

    body = f"""<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{industry} · 产业链研报分析看板</title>
<style>{_CSS}</style>
</head><body>
<header>
  <h1>📈 {industry} · 产业链研报分析看板</h1>
  <div class="meta">
    <span>分析研报 <b>{n_report}</b> 篇</span>
    <span>生成时间 <b>{gen_at}</b></span>
    <span>来源目录 <b>{src}</b></span>
  </div>
</header>

<nav class="tabs">
  <button class="tab-btn active" onclick="switchTab('tab-overview',this)">总览</button>
  <button class="tab-btn" onclick="switchTab('tab-cost',this)">成本构成</button>
  <button class="tab-btn" onclick="switchTab('tab-risk',this)">替代风险</button>
  <button class="tab-btn" onclick="switchTab('tab-valuation',this)">估值全景</button>
</nav>

<main>
  {_render_overview(ov)}
  {_render_cost(comp)}
  {_render_risk(risk)}
  {_render_valuation(val)}
</main>

<footer>
  本看板由 a-stock-data · industry_analyzer 自动生成 · 数据仅供研究，不构成投资建议
</footer>

<script>{_JS}</script>
</body></html>"""
    return body


def render_dashboard(analysis: dict, output_path: str = "analysis.html") -> str:
    """渲染并写入 HTML 文件，返回写入路径"""
    html_str = render_html(analysis)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_str, encoding="utf-8")
    return str(out.resolve())


# ─────────────────────────── 内置示例数据 ───────────────────────────

def demo_analysis() -> dict:
    """一份用于预览样式的示例分析数据（人形机器人产业链）"""
    return {
        "industry": "人形机器人",
        "generated_at": "2026-05-29 14:30",
        "report_count": 42,
        "source_dir": "./reports/人形机器人",
        "overview": {
            "panorama": "人形机器人产业链可分为执行层（关节模组、丝杠、减速器、电机）、"
                        "感知层（力矩传感器、视觉）、控制层（控制器、算法）三大环节。"
                        "其中执行层占整机成本约 60%，是国产替代与价值量最集中的环节。",
            "cost_structure": [
                {"module": "丝杠", "pct": 18, "note": "行星滚柱丝杠，单机用量大"},
                {"module": "减速器", "pct": 16, "note": "谐波减速器为主"},
                {"module": "无框电机", "pct": 14, "note": "高功率密度"},
                {"module": "力矩传感器", "pct": 12, "note": "六维力传感器"},
                {"module": "控制器", "pct": 10, "note": "运动控制核心"},
                {"module": "结构件", "pct": 8, "note": "轻量化"},
            ],
            "module_importance": [
                {"module": "丝杠", "importance": "高", "score": 9, "reason": "工艺壁垒高，国产化率低，价值量大"},
                {"module": "减速器", "importance": "高", "score": 8, "reason": "精度要求高，存量供应商集中"},
                {"module": "力矩传感器", "importance": "中", "score": 7, "reason": "技术路线未定，弹性大"},
                {"module": "结构件", "importance": "低", "score": 4, "reason": "竞争充分，差异化小"},
            ],
            "module_leaders": [
                {"module": "丝杠", "leaders": ["五洲新春", "贝斯特"], "note": "磨削工艺领先"},
                {"module": "减速器", "leaders": ["绿的谐波"], "note": "国内谐波龙头"},
                {"module": "无框电机", "leaders": ["步科股份", "鸣志电器"], "note": "高功率密度方案"},
            ],
            "leader_replaceability": [
                {"module": "丝杠", "replaceable": "难", "reason": "磨床设备+工艺know-how双重壁垒"},
                {"module": "减速器", "replaceable": "中", "reason": "新进入者增多，但精度仍有差距"},
                {"module": "结构件", "replaceable": "易", "reason": "通用加工，可替代性强"},
            ],
            "bom": [
                {"component": "行星滚柱丝杠", "pct": 18, "qty": "14根/台", "suppliers": ["五洲新春", "贝斯特"], "note": "直线关节核心"},
                {"component": "谐波减速器", "pct": 16, "qty": "14个/台", "suppliers": ["绿的谐波"], "note": "旋转关节"},
                {"component": "无框力矩电机", "pct": 14, "qty": "28个/台", "suppliers": ["步科股份"], "note": "旋转+直线驱动"},
                {"component": "六维力矩传感器", "pct": 12, "qty": "4个/台", "suppliers": ["柯力传感"], "note": "手腕/脚踝"},
            ],
            "milestones": [
                {"date": "2024Q1", "event": "特斯拉 Optimus Gen2 发布，灵巧手自由度提升"},
                {"date": "2024Q4", "event": "国内多家厂商发布人形机器人本体，量产规划落地"},
                {"date": "2025H1", "event": "丝杠/减速器国产送样验证加速"},
                {"date": "2026", "event": "预计进入小批量量产，成本快速下降"},
            ],
        },
        "cost_components": [
            {
                "name": "行星滚柱丝杠", "cost_pct": 18,
                "process": "棒料 → 粗车 → 热处理 → 精磨（螺纹磨床）→ 滚柱装配 → 检测。核心在螺纹磨削精度。",
                "companies": [{"name": "五洲新春", "code": "603667"}, {"name": "贝斯特", "code": "300580"}],
                "advantages": "国内磨削设备积累深厚，良率与一致性提升快",
                "barriers": "高精度螺纹磨床依赖进口，工艺know-how需长期积累，认证周期长",
            },
            {
                "name": "谐波减速器", "cost_pct": 16,
                "process": "柔轮成形 → 齿形加工 → 热处理 → 装配 → 精度检测。柔轮疲劳寿命是关键。",
                "companies": [{"name": "绿的谐波", "code": "688017"}],
                "advantages": "国内唯一规模化量产谐波减速器企业，客户验证充分",
                "barriers": "柔轮材料与齿形设计壁垒高，海外哈默纳科先发优势明显",
            },
            {
                "name": "无框力矩电机", "cost_pct": 14,
                "process": "定子绕组 → 转子磁钢 → 灌封 → 动平衡 → 测试。功率密度与散热为核心。",
                "companies": [{"name": "步科股份", "code": "688160"}, {"name": "鸣志电器", "code": "603728"}],
                "advantages": "国产电机性价比高，可定制化程度高",
                "barriers": "高功率密度与高温退磁控制存在技术门槛",
            },
        ],
        "substitution_risk": {
            "risks": [
                {"module": "减速器", "level": "高", "risk": "RV减速器路线若被采用，谐波份额承压；新进入者增多"},
                {"module": "力矩传感器", "level": "高", "risk": "技术路线未定，电流环估算方案可能替代物理传感器"},
                {"module": "结构件", "level": "中", "risk": "竞争充分，毛利易被压缩"},
            ],
            "safe_tracks": [
                {"module": "丝杠", "reason": "磨削工艺+设备双重壁垒，短期难被替代，价值量大"},
                {"module": "谐波减速器", "reason": "存量客户验证壁垒高，绑定深度强"},
            ],
        },
        "valuation": [
            {"name": "绿的谐波", "code": "688017", "module": "减速器", "growth": "35%", "irreplaceability": "高",
             "price": 224.12, "pe": 300.4, "pb": 11.5, "mcap": 410.9},
            {"name": "五洲新春", "code": "603667", "module": "丝杠", "growth": "28%", "irreplaceability": "高",
             "price": 32.5, "pe": 45.2, "pb": 4.1, "mcap": 180.3},
            {"name": "步科股份", "code": "688160", "module": "电机", "growth": "40%", "irreplaceability": "中",
             "price": 58.0, "pe": 62.0, "pb": 6.8, "mcap": 90.5},
        ],
    }


# ─────────────────────────── CLI ───────────────────────────

def main():
    parser = argparse.ArgumentParser(description="产业链研报分析 HTML 看板渲染器")
    parser.add_argument("input", nargs="?", help="analysis.json 文件路径")
    parser.add_argument("-o", "--output", default="analysis.html", help="输出 HTML 路径")
    parser.add_argument("--demo", action="store_true", help="渲染内置示例数据预览样式")
    args = parser.parse_args()

    if args.demo or not args.input:
        analysis = demo_analysis()
        print("使用内置示例数据渲染...")
    else:
        analysis = json.loads(Path(args.input).read_text(encoding="utf-8"))

    path = render_dashboard(analysis, args.output)
    print(f"✓ 看板已生成: {path}")


if __name__ == "__main__":
    main()
