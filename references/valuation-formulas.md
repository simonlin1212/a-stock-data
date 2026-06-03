# 估值公式

使用场景：单票估值、批量估值、成长股 PEG 和 PE 消化时间。

## 函数

| 需求 | 函数 | 公式 |
|---|---|---|
| 前向 PE | `forward_pe(price, eps_forecast)` | 当前股价 / 未来年度一致预期 EPS |
| PE 消化年数 | `pe_digestion(current_pe, cagr, target_pe=30)` | `log(current_pe / target_pe) / log(1 + cagr)` |
| PEG | `calc_peg(pe, cagr)` | `PE / (CAGR * 100)` |

## 口径

- `cagr` 使用小数，例如 30% 输入 `0.3`。
- 默认 `target_pe=30` 是 A 股成长股估值锚点，不适用于所有行业。
- EPS 小于等于 0 时，前向 PE 返回无穷大。
- CAGR 小于等于 0 时，PE 消化和 PEG 返回无穷大。

## 输出要求

估值结论必须同时给出：

- 实时价来源和时间。
- EPS 预测来源和机构覆盖数。
- PE、PEG、消化时间。
- 缺失或覆盖不足 caveat。
