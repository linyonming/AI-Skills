```markdown
# Dashboard Schema

`china-fund-deep-analysis` 的 HTML 看板 JSON 规范。  
所有脚本读写同一结构；渲染器只消费本 schema，不自行猜字段。

---

## 1. 文件约定

| 用途 | 路径 |
|---|---|
| 工作 JSON | `fund_work/{code}_dash.json` |
| 博弈 JSON | `fund_work/{code}_debate.json` 或 `fund_work/{code}_ai_debate.json` |
| 最终 HTML | `/root/.openclaw/workspace/outputs/fund_{code}_{YYYYMMDD}.html` |
| 流水线输出 | `generate_fund_dashboard.py --json` 打印含 `html` / `media_line` / `ok` |

规则：

- `{code}` 用基金主代码数字，如 `005827`
- 日期用分析日 `YYYYMMDD`
- 最终附件禁止写入 `/tmp` 或会话临时目录
- 字段缺失用 `null` / `[]` / `{}`，禁止省略关键键后静默通过验收

---

## 2. Top-level object

```json
{
  "meta": {},
  "summary": {},
  "profile": {},
  "metrics": {},
  "scores": {},
  "nav_series": [],
  "drawdown_series": [],
  "returns": {},
  "risk": {},
  "portfolio": {},
  "manager": {},
  "style_drift": {},
  "sip": {},
  "action_map": {},
  "peers": [],
  "better_choices": [],
  "peer_errors": [],
  "risks": [],
  "data_quality": {},
  "glossary": [],
  "debate": {},
  "charts": {},
  "render": {}
}
```

验收最低集（与 SKILL Completion Gate 对齐）：

- `summary`
- `metrics`
- `nav_series`
- `risks`
- `peers`（快速模式可空数组，但键必须存在；完整模式不得为空）
- `debate.votes` / `debate.summary` / `debate.action` / `debate.key_level`

---

## 3. `meta`

```json
{
  "schema_version": "1.0.0",
  "skill": "china-fund-deep-analysis",
  "code": "005827",
  "name": "易方达蓝筹精选混合",
  "share_class": "A",
  "market": "cn_fund",
  "fund_type": "hybrid_equity",
  "theme": "蓝筹/消费",
  "mode": "deep",
  "as_of": "2026-05-11",
  "generated_at": "2026-05-11T12:00:00+08:00",
  "timezone": "Asia/Shanghai",
  "currency": "CNY",
  "quick_mode": false,
  "debate_enabled": true,
  "debate_fallback": false,
  "html_path": "/root/.openclaw/workspace/outputs/fund_005827_20260511.html",
  "work_json_path": "fund_work/005827_dash.json"
}
```

### 枚举

`fund_type`：

- `equity_active`
- `hybrid_equity`
- `hybrid_balanced`
- `hybrid_bond`
- `bond`
- `money`
- `etf`
- `etf_enhanced`
- `lof`
- `qdii`
- `fof`
- `reits`
- `other`

`mode`：

- `quick`
- `deep`
- `compare`

`share_class`：

- `A` / `C` / `OTHER` / `UNKNOWN`

---

## 4. `summary`（Hero + 一句话结论）

```json
{
  "headline": "易方达蓝筹精选：中长期仍可持有，回撤中等，适合分批定投",
  "one_liner": "综合 86 分，建议继续持有，可分批定投",
  "decision_tag": "建议定投",
  "decision_tags": ["建议继续持有", "建议定投"],
  "star": 4,
  "score_total": 86.0,
  "confidence": "medium",
  "risk_level": "中",
  "return_level": "良",
  "drawdown_level": "中",
  "stability_level": "良",
  "manager_level": "优",
  "traffic_lights": {
    "return": "green",
    "risk": "amber",
    "drawdown": "amber",
    "stability": "green",
    "manager": "green"
  },
  "audience": "适合能承受中等波动、准备 1–3 年持有或定投的投资者",
  "not_for": "追求极致稳健或不能接受 20%+ 回撤的用户",
  "disclaimer": "基于公开信息研究，不构成投资建议"
}
```

### 约束

- `decision_tag` 主标签只能是：
  - `建议继续持有`
  - `建议定投`
  - `建议减仓`
  - `建议止盈`
  - `建议观望`
  - `不建议新增`
- `star`：1–5 整数
- `confidence`：`high` | `medium` | `low`
- `traffic_lights` 颜色：`green` | `amber` | `red` | `gray`
- Telegram 最终一句话优先用 `one_liner`

---

## 5. `profile`（基金画像）

```json
{
  "code": "005827",
  "name": "易方达蓝筹精选混合",
  "full_name": "易方达蓝筹精选混合型证券投资基金",
  "share_class": "A",
  "fund_type": "hybrid_equity",
  "fund_type_label": "偏股混合",
  "company": "易方达基金",
  "custodian": "xx银行",
  "inception_date": "2018-09-05",
  "manager_names": ["张坤"],
  "scale_yi": 312.5,
  "scale_date": "2026-03-31",
  "risk_rating_official": "R3",
  "morningstar_rating": null,
  "morningstar_date": null,
  "benchmark": "沪深300指数收益率×80% + 中证全债指数收益率×20%",
  "purchase_status": "开放申购/赎回",
  "min_purchase": 10,
  "fees": {
    "management_fee": 1.5,
    "custody_fee": 0.25,
    "purchase_fee": "前端申购费，可折扣",
    "redemption_fee": "持有期限阶梯费率",
    "sales_service_fee": 0.0,
    "fee_notes": "A类无销售服务费；C类需另计"
  },
  "tags": ["主动权益", "蓝筹", "消费医药仓位可能偏高"]
}
```

说明：

- `scale_yi` 单位：亿元
- 费率未知时用 `null`，并在 `data_quality.missing_fields` 记录
- `morningstar_rating` 禁止编造

---

## 6. `metrics`（核心数据卡）

首屏卡片统一读这里，避免渲染器东拼西凑。

```json
{
  "nav": 1.2345,
  "nav_date": "2026-05-10",
  "acc_nav": 2.3456,
  "return_1m": 2.1,
  "return_3m": 5.4,
  "return_6m": 8.7,
  "return_1y": 18.2,
  "return_3y": 42.5,
  "return_ytd": 9.3,
  "return_inception": 120.4,
  "return_ann_3y": 12.5,
  "max_drawdown": -22.4,
  "max_drawdown_start": "2024-01-01",
  "max_drawdown_end": "2024-08-15",
  "recovery_months": 10,
  "volatility": 18.6,
  "std_dev": 18.6,
  "sharpe": 1.42,
  "alpha": 3.1,
  "beta": 0.96,
  "peer_rank_1y_pct": 18,
  "peer_rank_3y_pct": 12,
  "peer_size": 320,
  "turnover_rate": 120.5,
  "concentration_top10": 48.6,
  "equity_ratio": 86.2,
  "bond_ratio": 5.1,
  "cash_ratio": 8.7
}
```

### 口径

- 所有收益/回撤/波动类字段：百分比数值，保留 1 位小数（如 `18.2` 表示 18.2%）
- `peer_rank_*_pct`：百分位，**数字越小越好**（Top 18% → `18`）
- `recovery_months`：最大回撤修复月数；未修复用 `null`
- `sharpe/alpha/beta` 必须与 `risk.window` / `risk.benchmark` 一致

---

## 7. `scores`（评分拆解）

与 `references/scoring-model.md` 对齐。

```json
{
  "total": 86.0,
  "star": 4,
  "confidence": "medium",
  "weights": {
    "return": 0.30,
    "risk": 0.25,
    "manager": 0.20,
    "stability": 0.15,
    "size_liquidity": 0.10
  },
  "breakdown": {
    "return": 88,
    "risk": 76,
    "manager": 84,
    "stability": 78,
    "size_liquidity": 80
  },
  "weighted": {
    "return": 26.4,
    "risk": 19.0,
    "manager": 16.8,
    "stability": 11.7,
    "size_liquidity": 8.0
  },
  "explain": {
    "return": "1Y/3Y 均强于同类，不只靠近几个月脉冲。",
    "risk": "回撤中等，修复尚可，但波动不低。",
    "manager": "经理任期较长，任职回报稳定。",
    "stability": "风格大体稳定，存在轻度漂移。",
    "size_liquidity": "规模偏大但尚可运作，流动性无重大障碍。"
  },
  "flags": ["轻度风格漂移", "规模偏大"],
  "caps_applied": ["无近1月暴涨加成上限"],
  "type_adjustments": ["主动权益：强调3Y与经理稳定性"]
}
```

渲染：

- Hero 大环用 `total`
- 五维小环用 `breakdown`
- 白话解释用 `explain`

---

## 8. `nav_series` / `drawdown_series`

### `nav_series[]`

```json
[
  {"date": "2025-05-12", "nav": 1.1012, "acc_nav": 2.0011, "volume": null},
  {"date": "2025-05-13", "nav": 1.1098, "acc_nav": 2.0097, "volume": null}
]
```

要求：

- 完整模式建议 180–800 个交易日；快速模式至少 60 日
- 按日期升序
- ETF/LOF 可把成交额放 `volume`；开放式主动基金可为 `null`

### `drawdown_series[]`

```json
[
  {"date": "2025-05-12", "drawdown": 0.0},
  {"date": "2025-05-13", "drawdown": -1.2}
]
```

- `drawdown` 为相对阶段峰值的回撤百分比（0 到负值）
- 用于回撤色块与当前回撤位置

---

## 9. `returns` / `risk`

### `returns`

```json
{
  "windows": {
    "1m": {"value": 2.1, "peer_pct": 40, "vs_benchmark": 0.5},
    "3m": {"value": 5.4, "peer_pct": 33, "vs_benchmark": 1.2},
    "6m": {"value": 8.7, "peer_pct": 25, "vs_benchmark": 1.8},
    "1y": {"value": 18.2, "peer_pct": 18, "vs_benchmark": 3.4},
    "3y": {"value": 42.5, "peer_pct": 12, "vs_benchmark": 8.1},
    "ytd": {"value": 9.3, "peer_pct": 22, "vs_benchmark": 2.0},
    "inception": {"value": 120.4, "peer_pct": null, "vs_benchmark": null}
  },
  "annualized": {
    "3y": 12.5,
    "inception": 14.8
  },
  "calendar_years": [
    {"year": 2023, "value": -8.2},
    {"year": 2024, "value": 12.4},
    {"year": 2025, "value": 21.0}
  ]
}
```

### `risk`

```json
{
  "window": "3y",
  "benchmark": "沪深300",
  "max_drawdown": -22.4,
  "max_drawdown_start": "2024-01-01",
  "max_drawdown_end": "2024-08-15",
  "current_drawdown": -6.3,
  "recovery_months": 10,
  "recovered": true,
  "volatility": 18.6,
  "downside_deviation": 12.4,
  "sharpe": 1.42,
  "sortino": 1.75,
  "alpha": 3.1,
  "beta": 0.96,
  "tracking_error": null,
  "info_ratio": null,
  "var_95": null,
  "notes": ["Sharpe/Alpha/Beta 按近3年周频估算", "未计申购赎回费"]
}
```

类型适配：

- ETF：优先填 `tracking_error`
- 债基/货基：`alpha/beta` 可空，但回撤/波动必填
- 估算值必须在 `notes` 与 `data_quality` 标明

---

## 10. `portfolio`（持仓与结构）

```json
{
  "as_of": "2026-03-31",
  "lag_note": "持仓截至季报，非实时",
  "asset_allocation": [
    {"name": "股票", "weight": 86.2},
    {"name": "债券", "weight": 5.1},
    {"name": "现金", "weight": 8.7}
  ],
  "industry_allocation": [
    {"name": "食品饮料", "weight": 22.5},
    {"name": "医药生物", "weight": 14.2},
    {"name": "电子", "weight": 9.8}
  ],
  "top_holdings": [
    {
      "rank": 1,
      "name": "贵州茅台",
      "code": "600519",
      "weight": 9.6,
      "type": "stock",
      "change": "增持"
    }
  ],
  "concentration_top5": 32.1,
  "concentration_top10": 48.6,
  "turnover_rate": 120.5,
  "holding_count": 42,
  "style_labels": ["大盘", "价值/质量", "消费偏向"]
}
```

约束：

- 权重之和允许 98–102（四舍五入误差）；明显异常要进 `data_quality.anomalies`
- 债基/货基 `top_holdings.type` 可用 `bond` / `cash` / `other`
- 无持仓数据时：`top_holdings=[]`，并降置信度

---

## 11. `manager`

```json
{
  "managers": [
    {
      "name": "张坤",
      "role": "主基金经理",
      "start_date": "2018-09-05",
      "tenure_years": 7.6,
      "return_since_takeover": 120.4,
      "ann_return_since_takeover": 14.8,
      "peer_rank_pct": 15,
      "background": "长期管理主动权益，风格偏质量蓝筹",
      "other_funds": ["示例基金A"],
      "is_primary": true
    }
  ],
  "team_stability": "高",
  "recent_change": false,
  "recent_change_note": null,
  "departure_risk": "低",
  "score": 84,
  "summary": "任期长、风格清晰，经理项支撑较强"
}
```

硬规则映射：

- 近 12 个月更换核心经理：`recent_change=true`，并影响 `scores.breakdown.manager`
- 任职未满 1 年：`tenure_years < 1`，经理分设上限，`summary.confidence` 不超过 medium

---

## 12. `style_drift`

```json
{
  "score": 28,
  "level": "轻度",
  "detected": true,
  "from_style": ["消费", "医药"],
  "to_style": ["消费", "科技"],
  "evidence": [
    "行业前三大中科技权重上升",
    "换手率高于自身近3年中枢"
  ],
  "impact": "对原消费蓝筹叙事有轻微扰动，尚未完全改方向",
  "as_of": "2026-03-31"
}
```

`level`：`无` | `轻度` | `中度` | `显著`  
`score`：0–100，越高漂移越强。

---

## 13. `sip`（定投适配）

```json
{
  "suitable": true,
  "score": 84,
  "star": 5,
  "period_suggest": "每月",
  "period_options": ["每周", "每月"],
  "reasons": [
    "波动适中，适合分批摊薄成本",
    "历史回撤后有修复能力",
    "费率对长期定投可接受"
  ],
  "cautions": [
    "不适合作为现金替代",
    "若经理离任需重新评估"
  ],
  "horizon_years": "3+",
  "suggested_position_role": "核心底仓或卫星中的稳定成长仓"
}
```

---

## 14. `action_map`（操作观察地图）

```json
{
  "hold": {
    "title": "继续持有条件",
    "items": [
      "核心经理未离任",
      "近3年同类排名未跌出前50%",
      "最大回撤未系统性恶化"
    ]
  },
  "sip": {
    "title": "定投观察区",
    "items": [
      "计划投资期限 ≥ 3 年",
      "能接受约 20% 级别回撤",
      "当前无明显策略失效信号"
    ]
  },
  "reduce": {
    "title": "减仓警戒区",
    "items": [
      "风格漂移转为中度以上且逻辑不清",
      "同类连续4个季度落后",
      "组合内同类暴露过高"
    ]
  },
  "take_profit": {
    "title": "止盈条件",
    "items": [
      "达到个人目标收益率",
      "估值拥挤或主题退潮导致风险收益比下降"
    ]
  },
  "invalidate": {
    "title": "失效 / 赎回警戒",
    "items": [
      "核心经理离任",
      "策略实质性漂移",
      "规模极端恶化或出现重大风险公告"
    ],
    "key_level": "回撤跌破近3年最大回撤警戒带（约-25%）需复盘"
  }
}
```

`debate.key_level` 可直接复用 `action_map.invalidate.key_level` 或更短的关键线文案。

---

## 15. `peers` / `better_choices` / `peer_errors`

### `peers[]`

```json
[
  {
    "code": "005827",
    "name": "易方达蓝筹精选混合",
    "is_primary": true,
    "fund_type": "hybrid_equity",
    "manager": "张坤",
    "score_total": 86.0,
    "star": 4,
    "return_1y": 18.2,
    "return_3y": 42.5,
    "max_drawdown": -22.4,
    "sharpe": 1.42,
    "peer_rank_1y_pct": 18,
    "scale_yi": 312.5,
    "decision_tag": "建议定投",
    "one_liner": "质量蓝筹代表，回撤中等",
    "pros": ["经理稳定", "中长期业绩较好"],
    "cons": ["规模偏大", "阶段拥挤"]
  }
]
```

要求：

- 完整模式至少 1 主 + 3 同类（建议 4–6）
- 主标的 `is_primary=true`，排序可置顶
- 字段口径与主基金一致

### `better_choices[]`

```json
[
  {
    "code": "260108",
    "name": "景顺长城新兴成长混合",
    "why": "同类中收益-回撤更均衡，适合作为替代观察",
    "score_total": 88.0,
    "relation": "同类主动权益"
  }
]
```

### `peer_errors[]`

```json
[
  {
    "code": "xxxxxx",
    "name": "某基金",
    "error": "净值接口超时",
    "stage": "fetch"
  }
]
```
## 16. `risks[]`（风险热力卡）

```json
[
  {
    "id": "drawdown",
    "title": "回撤风险",
    "level": "中",
    "severity": "high",
    "summary": "历史最大回撤约 22%，波动不低。",
    "evidence": ["max_drawdown=-22.4", "volatility=18.6"],
    "monitor": "跟踪当前回撤、修复速度、同类回撤分位",
    "mitigation": "控制仓位；用定投代替一次性重仓"
  },
  {
    "id": "manager_keyperson",
    "title": "经理依赖",
    "level": "中",
    "severity": "high",
    "summary": "策略辨识度与主经理绑定较深。",
    "evidence": ["is_primary=true", "recent_change=false", "tenure_years=7.6"],
    "monitor": "公告、经理页、基金公司人事变动",
    "mitigation": "经理离任即冻结加仓并重评"
  },
  {
    "id": "style_drift",
    "title": "风格漂移",
    "level": "低",
    "severity": "medium",
    "summary": "存在轻度漂移，尚未颠覆原叙事。",
    "evidence": ["style_drift.level=轻度", "turnover_rate=120.5"],
    "monitor": "季报行业分布、换手率、前十大变化",
    "mitigation": "漂移升至中度以上时降为观察"
  },
  {
    "id": "size",
    "title": "规模风险",
    "level": "中",
    "severity": "medium",
    "summary": "规模偏大，可能影响调仓灵活度。",
    "evidence": ["scale_yi=312.5"],
    "monitor": "季末规模、净申赎、流动性环境",
    "mitigation": "避免在拥挤阶段大幅加仓"
  },
  {
    "id": "data_lag",
    "title": "持仓滞后",
    "level": "低",
    "severity": "medium",
    "summary": "持仓为季报口径，不是实时仓位。",
    "evidence": ["portfolio.as_of=2026-03-31", "lag_note=持仓截至季报"],
    "monitor": "最新季报/年报披露日",
    "mitigation": "结论标注时效；重大判断等新持仓验证"
  }
]
```

### 字段说明

| 字段 | 说明 |
|---|---|
| `id` | 稳定英文键，便于去重与前端图标映射 |
| `title` | 中文短标题 |
| `level` | `高` / `中` / `低` |
| `severity` | 展示优先级：`high` / `medium` / `low`（高风险红卡优先） |
| `summary` | ≤2 句 |
| `evidence` | 可追溯事实/指标 |
| `monitor` | 怎么跟踪 |
| `mitigation` | 怎么缓释 |

规则：

- 完整模式至少 3 条；快速模式至少 2 条
- 高风险必须排在数组前面
- 禁止空 `risks` 仍声称深度分析

---

## 17. `data_quality`（数据可信度）

```json
{
  "overall": "B",
  "confidence": "medium",
  "sources": [
    {
      "name": "天天基金",
      "level": "B",
      "fields": ["nav", "returns", "manager", "scale"],
      "checked_at": "2026-05-11T11:50:00+08:00"
    },
    {
      "name": "东方财富基金",
      "level": "B",
      "fields": ["nav", "returns", "portfolio"],
      "checked_at": "2026-05-11T11:51:00+08:00"
    },
    {
      "name": "基金季报/公告",
      "level": "A",
      "fields": ["portfolio", "scale", "manager_change"],
      "checked_at": "2026-05-11T11:52:00+08:00"
    }
  ],
  "cross_checks": [
    {
      "field": "return_1y",
      "sources": ["天天基金", "东方财富基金"],
      "status": "ok",
      "diff": 0.2,
      "note": "差异小于阈值"
    },
    {
      "field": "nav",
      "sources": ["天天基金", "东方财富基金"],
      "status": "ok",
      "diff": 0.0,
      "note": null
    }
  ],
  "verified": ["nav双源", "1Y收益双源", "经理任期与公告一致"],
  "pending": ["晨星评级未取到", "Alpha/Beta 为估算"],
  "missing_fields": ["morningstar_rating", "risk.var_95"],
  "anomalies": [],
  "stale_fields": [
    {
      "field": "portfolio",
      "as_of": "2026-03-31",
      "note": "持仓披露滞后"
    }
  ],
  "notes": [
    "公开信息研究，不构成投资建议",
    "风险指标按近3年窗口估算，未扣申购赎回费"
  ]
}
```

### 约束

- `overall`：`A` | `B` | `C` | `D`（与 SKILL Data Trust Model 一致）
- 净值/关键收益尽量有双源 `cross_checks`
- 有异常时 `anomalies` 必填，例如：

```json
{
  "field": "return_1y",
  "severity": "high",
  "message": "两源相差超过阈值，已采用东财并降置信度",
  "values": {"天天基金": 18.2, "东方财富基金": 21.0}
}
```

- `missing_fields` 与页面“数据局限”同步
- `overall=C/D` 或关键缺失 ≥2 时，`summary.confidence` 不得为 `high`

---

## 18. `glossary`（术语小抄）

```json
[
  {
    "term": "最大回撤",
    "plain": "从阶段最高点跌到最低点最多亏多少，衡量最疼的一段。"
  },
  {
    "term": "夏普比率",
    "plain": "多承担一单位波动，大概换来多少超额回报；越高通常越好。"
  },
  {
    "term": "Alpha",
    "plain": "剔除市场涨跌后，基金经理可能创造的超额部分。"
  },
  {
    "term": "Beta",
    "plain": "相对市场的敏感度；接近1表示跟市场起伏差不多。"
  },
  {
    "term": "定投",
    "plain": "按固定节奏分批买入，用来摊薄成本，不保证盈利。"
  },
  {
    "term": "风格漂移",
    "plain": "基金实际持仓风格偏离既有标签或历史习惯。"
  },
  {
    "term": "同类排名百分位",
    "plain": "数字越小越好；18 表示大约排在前 18%。"
  }
]
```

要求：

- 8–12 条足够
- 每条必须有白话 `plain`
- 按基金类型可增删（ETF 加“跟踪误差/折溢价”；货基弱化 Alpha）

---

## 19. `debate`（多智能体博弈）

与 `references/ai_native_debate.md` 对齐；渲染器读此字段。

```json
{
  "mode": "ai_native",
  "fallback": false,
  "direction": "bull",
  "confidence": "medium",
  "bull_pct": 67,
  "bear_pct": 17,
  "neutral_pct": 17,
  "summary": "整体偏多，适合持有/定投，但回撤与规模限制激进加仓。",
  "action": "建议定投",
  "key_level": "核心经理离任，或回撤跌破近3年警戒带（约-25%）时停止加仓并复盘",
  "tally": {
    "bull": 4,
    "bear": 1,
    "neutral": 1,
    "bull_pct": 67,
    "bear_pct": 17,
    "neutral_pct": 17
  },
  "votes": [
    {
      "role_id": "manager_analyst",
      "role_name": "基金经理分析师",
      "direction": "bull",
      "confidence": 0.78,
      "score_hint": 84,
      "one_liner": "经理稳定，是中长期持有加分项。",
      "reasoning": "任期长、未见近期核心更换。",
      "evidence": ["tenure_years=7.6", "recent_change=false"],
      "risks": ["能力圈切换可能削弱叙事"],
      "invalidators": ["核心经理离任"]
    }
  ],
  "bull_case": [
    "中长期业绩与经理稳定性仍在",
    "定投适配较好"
  ],
  "bear_case": [
    "规模偏大",
    "回撤中等，弱市体验一般"
  ],
  "watchpoints": [
    "经理是否变更",
    "风格漂移是否升温",
    "同类替代是否反超"
  ],
  "data_gaps": [
    "晨星评级缺失",
    "持仓截至季报"
  ],
  "decision_tags": ["建议继续持有", "建议定投"]
}
```

### 验收

完整模式（未 `--no-debate`）必须：

- `votes` 长度为 6
- `summary` / `action` / `key_level` 非空
- `action` ∈ 允许决策标签
- `fallback=true` 时，`meta.debate_fallback=true`；默认还应尝试 AI-native 覆盖

快速模式：

- 可简化 votes，但若开启博弈，仍建议保留 `summary/action/key_level`
- 用户明确跳过博弈：`debate` 可为 `{}`，渲染器隐藏区块

---

## 20. `charts`（图辅助层）

```json
{
  "nav_marks": [
    {"date": "2024-01-01", "label": "最大回撤起点", "type": "dd_start"},
    {"date": "2024-08-15", "label": "最大回撤终点", "type": "dd_end"}
  ],
  "reference_lines": [
    {"y": 1.05, "label": "定投参考成本示意", "type": "sip"},
    {"y_pct": -20, "label": "警戒回撤线", "type": "risk"}
  ],
  "score_radar": {
    "labels": ["收益", "风险控制", "经理", "稳定性", "规模流动性"],
    "values": [88, 76, 84, 78, 80]
  },
  "peer_scatter": {
    "x_label": "最大回撤(%)",
    "y_label": "近1年收益(%)",
    "points": [
      {"code": "005827", "x": -22.4, "y": 18.2, "is_primary": true},
      {"code": "260108", "x": -19.0, "y": 16.5, "is_primary": false}
    ]
  }
}
```

说明：

- 无图数据时键可空，但推荐完整模式给 `score_radar`
- `peer_scatter` 用于收益-回撤象限
- 渲染器不得因缺可选图表而失败

---

## 21. `render`（渲染与交付控制）

```json
{
  "theme": "dark_terminal",
  "lang": "zh-CN",
  "title": "易方达蓝筹精选混合（005827）基金决策看板",
  "html_path": "/root/.openclaw/workspace/outputs/fund_005827_20260511.html",
  "pdf_path": null,
  "media_line": "MEDIA:/root/.openclaw/workspace/outputs/fund_005827_20260511.html",
  "sections": [
    "hero",
    "plain_summary",
    "nav",
    "action_map",
    "metrics",
    "scores",
    "returns_risk",
    "portfolio",
    "manager",
    "risks",
    "peers",
    "debate",
    "data_quality",
    "glossary"
  ],
  "highlight_code": "005827",
  "mobile_first": true,
  "show_disclaimer": true,
  "generated_by": "generate_fund_dashboard.py"
}
```

规则：

- `html_path` 必须与最终附件一致
- 发 Telegram 前：`test -s html_path`
- `media_line` 仅用于流水线返回值；聊天里附件指令单独成行
- `pdf_path` 仅用户明确要求 PDF 时生成

---

## 22. 模式差异

### 快速模式 `meta.quick_mode=true`

必填：

- `summary` / `profile`（可简） / `metrics` / `scores`
- `nav_series`（≥60 日）
- `risks`（≥2）
- `data_quality`
- `peers` 键存在，值可 `[]`
- `debate` 可跳过或极简

可省略深挖：

- 完整 `portfolio.top_holdings` 解析
- 完整同类 4–6 只
- 完整六角色长 reasoning

### 完整模式

必填：最低验收集 + 非空 `peers` + 完整 `debate`（除非用户关闭）

### 多基对比模式 `meta.mode=compare`

- 主对象仍写 top-level
- 其余全部进 `peers`
- `better_choices` 给出首选/备选
- `charts.peer_scatter` 与对比表必须可用

---

## 23. 流水线 I/O 约定

`generate_fund_dashboard.py --json` 成功示例：

```json
{
  "ok": true,
  "code": "005827",
  "html": "/root/.openclaw/workspace/outputs/fund_005827_20260511.html",
  "work_json": "fund_work/005827_dash.json",
  "media_line": "MEDIA:/root/.openclaw/workspace/outputs/fund_005827_20260511.html",
  "decision_tag": "建议定投",
  "score_total": 86.0,
  "debate_fallback": false,
  "warnings": []
}
```

失败时：

```json
{
  "ok": false,
  "code": "005827",
  "error": "missing peers in deep mode",
  "stage": "validate",
  "html": null,
  "media_line": null
}
```

禁止：`ok=false` 仍输出可发送的 `MEDIA:` 行。

---

## 24. Completion Gate（机器校验伪码）

```python
import json
from pathlib import Path

ALLOWED_ACTIONS = {
    "建议继续持有", "建议定投", "建议减仓",
    "建议止盈", "建议观望", "不建议新增"
}

def validate_dash(path, html_path, quick=False, debate_required=True):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    assert d.get("summary"), "missing summary"
    assert d.get("metrics"), "missing metrics"
    assert d.get("nav_series"), "missing nav_series"
    assert d.get("risks"), "missing risks"
    assert "peers" in d, "missing peers key"
    if not quick:
        assert d["peers"], "empty peers in deep mode"

    s = d["summary"]
    assert s.get("one_liner") and s.get("decision_tag") in ALLOWED_ACTIONS
    assert 1 <= int(s.get("star", 0)) <= 5
    assert s.get("confidence") in {"high", "medium", "low"}

    if debate_required and not d.get("meta", {}).get("quick_mode"):
        debate = d.get("debate") or {}
        assert debate.get("votes"), "missing debate.votes"
        assert debate.get("summary"), "missing debate.summary"
        assert debate.get("action") in ALLOWED_ACTIONS
        assert debate.get("key_level"), "missing debate.key_level"
        if debate.get("mode") == "ai_native" or not debate.get("fallback", False):
            assert len(debate["votes"]) == 6

    hp = Path(html_path)
    assert hp.exists() and hp.stat().st_size > 0, "html missing or empty"
    return True
```

---

## 25. 字段类型速查

| 字段 | 类型 | 单位/枚举 |
|---|---|---|
| 收益/回撤/波动 | number | 百分比，1 位小数 |
| 净值 | number | 元，4 位小数常用 |
| 规模 `scale_yi` | number | 亿元 |
| 百分位 `peer_rank_*_pct` | number | 越小越好 |
| 评分 | number | 0–100 |
| 星级 | int | 1–5 |
| 置信度 | string | high/medium/low |
| 决策标签 | string | 6 个固定中文标签 |
| 日期 | string | `YYYY-MM-DD` |
| 时间戳 | string | ISO8601 + 时区 |

---

## 26. 反模式

- 用股票字段（PE/PB/K线买卖点）冒充基金看板
- 完整模式 `peers=[]` 还显示“同类对比完成”
- 编造 `morningstar_rating` / Alpha / 持仓
- 持仓不写 `as_of` / `lag_note`
- `decision_tag` 自造“强烈买入”“核心推荐”
- `debate.votes` 不足 6 个却当终稿
- HTML 写到 `/tmp/...` 仍发 `MEDIA:`
- 关键收益单源且与另一源冲突时不降级 `data_quality`
- 快速模式与完整模式字段混用却不标 `meta.mode`

---

## 27. 最小合法样例（deep，删减展示）

```json
{
  "meta": {
    "schema_version": "1.0.0",
    "skill": "china-fund-deep-analysis",
    "code": "005827",
    "name": "易方达蓝筹精选混合",
    "share_class": "A",
    "fund_type": "hybrid_equity",
    "mode": "deep",
    "as_of": "2026-05-11",
    "quick_mode": false,
    "debate_enabled": true,
    "debate_fallback": false,
    "html_path": "/root/.openclaw/workspace/outputs/fund_005827_20260511.html"
  },
  "summary": {
    "headline": "中长期可持有，回撤中等，适合分批定投",
    "one_liner": "易方达蓝筹精选综合86分，建议定投",
    "decision_tag": "建议定投",
    "star": 4,
    "score_total": 86.0,
    "confidence": "medium",
    "disclaimer": "基于公开信息研究，不构成投资建议"
  },
  "profile": {"code": "005827", "name": "易方达蓝筹精选混合", "fund_type": "hybrid_equity"},
  "metrics": {"nav": 1.2345, "return_1y": 18.2, "return_3y": 42.5, "max_drawdown": -22.4, "sharpe": 1.42},
  "scores": {
    "total": 86.0,
    "breakdown": {"return": 88, "risk": 76, "manager": 84, "stability": 78, "size_liquidity": 80},
    "explain": {"return": "中长期收益较好", "risk": "回撤中等", "manager": "经理稳定", "stability": "轻度漂移", "size_liquidity": "规模偏大"}
  },
  "nav_series": [{"date": "2025-05-12", "nav": 1.10, "acc_nav": 2.00}],
  "drawdown_series": [{"date": "2025-05-12", "drawdown": 0.0}],
  "returns": {},
  "risk": {"window": "3y", "max_drawdown": -22.4, "sharpe": 1.42},
  "portfolio": {"as_of": "2026-03-31", "top_holdings": [], "lag_note": "持仓截至季报"},
  "manager": {"managers": [], "recent_change": false, "score": 84},
  "style_drift": {"level": "轻度", "score": 28},
  "sip": {"suitable": true, "score": 84},
  "action_map": {
    "hold": {"title": "继续持有条件", "items": ["经理未离任"]},
    "sip": {"title": "定投观察区", "items": ["期限≥3年"]},
    "reduce": {"title": "减仓警戒区", "items": ["漂移升温"]},
    "take_profit": {"title": "止盈条件", "items": ["达到目标收益"]},
    "invalidate": {"title": "失效警戒", "items": ["经理离任"], "key_level": "回撤跌破警戒带需复盘"}
  },
  "peers": [
    {"code": "005827", "name": "易方达蓝筹精选混合", "is_primary": true, "score_total": 86.0}
  ],
  "better_choices": [],
  "peer_errors": [],
  "risks": [
    {
      "id": "drawdown",
      "title": "回撤风险",
      "level": "中",
      "severity": "high",
      "summary": "回撤中等",
      "evidence": ["max_drawdown=-22.4"],
      "monitor": "跟踪当前回撤",
      "mitigation": "控制仓位"
    }
  ],
  "data_quality": {
    "overall": "B",
    "confidence": "medium",
    "sources": [],
    "cross_checks": [],
    "verified": ["nav双源"],
    "pending": ["晨星评级缺失"],
    "missing_fields": ["morningstar_rating"],
    "anomalies": [],
    "notes": ["不构成投资建议"]
  },
  "glossary": [
    {"term": "最大回撤", "plain": "从高点到低点最多跌了多少"}
  ],
  "debate": {
    "mode": "ai_native",
    "fallback": false,
    "direction": "bull",
    "confidence": "medium",
    "bull_pct": 67,
    "bear_pct": 17,
    "summary": "偏多，适合定投",
    "action": "建议定投",
    "key_level": "经理离任或回撤破警戒带需复盘",
    "votes": [
      {"role_id": "manager_analyst", "role_name": "基金经理分析师", "direction": "bull", "confidence": 0.7, "one_liner": "经理稳定", "reasoning": "任期长", "evidence": ["tenure"], "risks": ["离任"], "invalidators": ["离任"]},
      {"role_id": "risk_analyst", "role_name": "风险分析师", "direction": "neutral", "confidence": 0.7, "one_liner": "回撤中等", "reasoning": "波动不低", "evidence": ["dd"], "risks": ["弱市"], "invalidators": ["回撤恶化"]},
      {"role_id": "quant_analyst", "role_name": "量化分析师", "direction": "bull", "confidence": 0.7, "one_liner": "中长期统计不弱", "reasoning": "1Y/3Y尚可", "evidence": ["ret"], "risks": ["回吐"], "invalidators": ["排名滑坡"]},
      {"role_id": "allocator_analyst", "role_name": "资产配置分析师", "direction": "bull", "confidence": 0.7, "one_liner": "可作主动权益仓", "reasoning": "定位清晰", "evidence": ["role"], "risks": ["拥挤"], "invalidators": ["更优替代"]},
      {"role_id": "longterm_analyst", "role_name": "长期投资分析师", "direction": "bull", "confidence": 0.7, "one_liner": "适合3年+定投", "reasoning": "定投适配高", "evidence": ["sip"], "risks": ["短持有"], "invalidators": ["期限过短"]},
      {"role_id": "contrarian_analyst", "role_name": "反方分析师", "direction": "bear", "confidence": 0.7, "one_liner": "规模与滞后是隐患", "reasoning": "高分不等于低风险", "evidence": ["scale"], "risks": ["误判"], "invalidators": ["规模优化"]}
    ]
  },
  "charts": {},
  "render": {
    "theme": "dark_terminal",
    "html_path": "/root/.openclaw/workspace/outputs/fund_005827_20260511.html",
    "media_line": "MEDIA:/root/.openclaw/workspace/outputs/fund_005827_20260511.html"
  }
}
```

> 注意：上例为“结构最小合法样例”，真实深度分析需补全净值序列、同类多只、经理与持仓等，不可拿空壳直接对用户交付。

---

## 28. 与脚本的字段所有权

| 脚本 | 主要写入 |
|---|---|
| `fetch_fund_data.py` | `profile` `metrics` `nav_series` `returns` `risk` `portfolio` `manager` 初值 |
| `scoring_model.py` | `scores` `summary` 初稿 `sip` 初稿 |
| `detect_style_drift.py` | `style_drift` |
| `auto_peers.py` | `peers` `better_choices` `peer_errors` |
| `debate_engine.py` / AI-native | `debate` |
| `merge_debate.py` | 合并 `debate`，可回写 `summary.decision_tag` |
| `render_dashboard.py` | 只读；写 HTML；可回填 `render.html_path` |
| `generate_fund_dashboard.py` | 串联全部并做验收 |

冲突处理：

1. 公告/A 级源 > 聚合 B 级源  
2. 辩论可改 `decision_tag`，但不得改原始净值与持仓事实  
3. 任何回写后必须重跑 validate + `test -s html`

---

## 29. 版本

- `schema_version`: `1.0.0`
- 兼容策略：新增可选字段不升主版本；删除/改名关键键必须升主版本并同步 SKILL Completion Gate
```
---

