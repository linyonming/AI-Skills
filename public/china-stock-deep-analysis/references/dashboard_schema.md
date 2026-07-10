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

---

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
    "evidence": ["is_primary=true", "recent_change=false"],
    "monitor": "基金经理变更公告、管理费/策略说明更新",
    "mitigation": "设置“经理离任即复盘”规则"
  },
  {
    "id": "size",
    "title": "规模约束",
    "level": "中",
    "severity": "medium",
    "summary": "规模偏大，可能影响调仓灵活度。",
    "evidence": ["scale_yi=312.5"],
    "monitor": "季报规模、申赎净流入",
    "mitigation": "若规模继续膨胀且业绩钝化，降低预期"
  },
  {
    "id": "style_drift",
    "title": "风格漂移",
    "level": "低",
    "severity": "medium",
    "summary": "存在轻度漂移，尚未颠覆原叙事。",
    "evidence": ["style_drift.level=轻度"],
    "monitor": "季报行业分布与换手率",
    "mitigation": "漂移升至中度以上时降级动作标签"
  }
]
```

约束：

- `level`：`高` | `中` | `低`
- `severity`：`high` | `medium` | `low`（控制展示排序）
- 完整模式至少 3 条；快速模式至少 2 条
- 高风险卡必须有 `monitor` + `mitigation`

---

## 17. `data_quality`（数据可信度）

```json
{
  "grade": "B",
  "confidence": "medium",
  "sources": [
    {"name": "天天基金", "level": "B", "used_for": ["净值", "收益", "经理"]},
    {"name": "东方财富基金", "level": "B", "used_for": ["净值复核", "持仓", "规模"]},
    {"name": "基金定期报告", "level": "A", "used_for": ["持仓截至日", "规模确认"]}
  ],
  "cross_checks": [
    {
      "field": "return_1y",
      "status": "ok",
      "detail": "天天基金与东财差异 < 0.3pct"
    },
    {
      "field": "nav",
      "status": "ok",
      "detail": "双源净值一致"
    }
  ],
  "missing_fields": ["morningstar_rating", "sortino"],
  "anomalies": [],
  "stale_fields": [
    {"field": "portfolio", "as_of": "2026-03-31", "note": "季报持仓滞后"}
  ],
  "notes": [
    "公开聚合数据可用于快速研究，关键结论已尽量双源校验",
    "不构成投资建议"
  ]
}
```

`grade`：

- `A`：关键字段以公告/报告为主且交叉验证充分
- `B`：聚合源为主，关键项已复核
- `C`：缺失较多或冲突未解
- `D`：不可用，只允许观望结论

渲染：单独“数据可信度”模块，必须展示来源等级、已校验项、待确认项。

---

## 18. `glossary`（术语小抄）

```json
[
  {"term": "最大回撤", "plain": "这段时间从最高点跌下去最深有多疼"},
  {"term": "夏普比率", "plain": "每多承担一点波动，多拿到多少回报"},
  {"term": "Alpha", "plain": "相对基准/市场多出来的本事，不是跟着涨那部分"},
  {"term": "Beta", "plain": "跟市场同涨同跌的敏感度"},
  {"term": "定投", "plain": "固定节奏分批买，减少一次性买在高点的风险"},
  {"term": "风格漂移", "plain": "基金实际持仓风格跟它原本标签越来越不像"}
]
```

建议 5–10 条，短句白话。

---

## 19. `debate`（博弈结果）

与 `references/ai_native_debate.md` 对齐；合并后最小可用集：

```json
{
  "mode": "ai_native",
  "fallback": false,
  "votes": [
    {
      "role_id": "manager_analyst",
      "role_name": "基金经理分析师",
      "direction": "bull",
      "confidence": 0.78,
      "one_liner": "经理稳定，中长期可持有。",
      "reasoning": "……",
      "evidence": ["tenure_years=7.6"],
      "risks": ["经理离任"],
      "invalidators": ["核心经理离任"]
    }
  ],
  "tally": {
    "bull": 4,
    "bear": 1,
    "neutral": 1,
    "bull_pct": 67,
    "bear_pct": 17,
    "neutral_pct": 17
  },
  "direction": "bull",
  "confidence": "medium",
  "bull_pct": 67,
  "bear_pct": 17,
  "summary": "整体偏多，适合持有/定投，不宜追高猛加。",
  "action": "建议定投",
  "key_level": "核心经理离任，或回撤跌破近3年警戒带（约-25%）需复盘",
  "bull_case": ["经理稳定", "中长期业绩仍有优势"],
  "bear_case": ["规模偏大", "回撤中等"],
  "watchpoints": ["经理变更", "风格漂移", "同类替代"],
  "data_gaps": ["晨星评级缺失"]
}
```

验收硬条件：

- `votes` 必须 6 条（跳过博弈除外）
- `summary` / `action` / `key_level` 非空
- `action` 必须落在允许决策标签集合

---

## 20. `charts` / `render`

### `charts`

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
  "quadrant": {
    "x_field": "max_drawdown",
    "y_field": "return_3y",
    "primary_code": "005827"
  }
}
```

### `render`

```json
{
  "theme": "dark_terminal",
  "language": "zh-CN",
  "title": "易方达蓝筹精选混合 · 基金决策看板",
  "sections": [
    "hero",
    "beginner",
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
  "mobile_first": true,
  "show_debate": true,
  "show_peers": true,
  "footer": "公开信息研究，不构成投资建议"
}
```

快速模式可隐藏：`peers` 深表、完整 `portfolio`、部分 `debate` 细节；但 `show_debate` 若为 true，仍需有非空摘要。

---

## 21. 模式差异

| 字段 | quick | deep | compare |
|---|---|---|---|
| `nav_series` | ≥60 日 | ≥180 日 | 主标的完整，对比可简化 |
| `peers` | 可 `[]` | ≥4（含主） | ≥2，强调相对排序 |
| `debate` | 可简化但仍建议有 | 必填完整 6 票 | 可按主标的生成 |
| `portfolio` | 可粗 | 尽量完整 | 可只保留集中度 |
| `better_choices` | 可选 | 建议有 | 重点输出 |

---

## 22. 流水线 IO 约定

`generate_fund_dashboard.py --json` 建议打印：

```json
{
  "ok": true,
  "code": "005827",
  "html": "/root/.openclaw/workspace/outputs/fund_005827_20260511.html",
  "media_line": "MEDIA:/root/.openclaw/workspace/outputs/fund_005827_20260511.html",
  "work_json": "fund_work/005827_dash.json",
  "debate_fallback": false,
  "quick_mode": false,
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

只有 `ok=true` 且 `test -s html` 通过，才允许对外发送 `MEDIA:` 行。

---

## 23. 字段校验伪代码

```python
REQUIRED_TOP = [
    "meta", "summary", "metrics", "scores", "nav_series",
    "risks", "peers", "data_quality", "debate"
]

ALLOWED_ACTIONS = {
    "建议继续持有", "建议定投", "建议减仓",
    "建议止盈", "建议观望", "不建议新增"
}

def validate(dash: dict, quick=False):
    for k in REQUIRED_TOP:
        assert k in dash, f"missing {k}"
    assert dash["summary"].get("one_liner")
    assert dash["summary"].get("decision_tag") in ALLOWED_ACTIONS
    assert dash["metrics"]
    assert isinstance(dash["nav_series"], list) and len(dash["nav_series"]) >= (60 if quick else 180)
    assert isinstance(dash["risks"], list) and len(dash["risks"]) >= (2 if quick else 3)
    if not quick:
        assert len(dash.get("peers") or []) >= 4, "deep mode requires peers"
    debate = dash.get("debate") or {}
    if dash.get("meta", {}).get("debate_enabled", True):
        assert debate.get("votes"), "missing debate.votes"
        assert debate.get("summary") and debate.get("action") and debate.get("key_level")
        assert debate["action"] in ALLOWED_ACTIONS
        if not debate.get("fallback"):
            assert len(debate["votes"]) == 6
    return True
```

---

## 24. 渲染字段映射（给 `render_dashboard.py`）

| 页面区块 | 主字段 |
|---|---|
| Hero 决策区 | `summary` + `scores.total` + `profile.name/code` |
| 小白速读 | `summary.headline/audience/not_for` + 精简 `metrics` |
| 净值走势 | `nav_series` + `drawdown_series` + `charts` |
| 操作地图 | `action_map` |
| 核心数据卡 | `metrics` + `profile` |
| 评分环 | `scores` |
| 业绩风险 | `returns` + `risk` |
| 持仓风格 | `portfolio` + `style_drift` |
| 经理卡 | `manager` |
| 风险热力 | `risks` |
| 同类对比 | `peers` + `better_choices` |
| 博弈裁定 | `debate` |
| 可信度 | `data_quality` |
| 术语小抄 | `glossary` |

---

## 25. Anti-patterns

- 用股票字段名冒充基金字段（如把 `kline` 当主序列）
- 完整模式 `peers=[]` 还输出“深度对比”
- 编造 `morningstar_rating` / `alpha` / 持仓权重
- `decision_tag` 写自由文案（如“可以看看”）
- `nav_series` 倒序或日期重复
- 持仓不写 `as_of` / `lag_note`
- `debate.fallback=true` 当最终深度稿且不标注
- HTML 路径写到临时目录
- 缺 `data_quality` 仍声称“已交叉验证”

---

## 26. Minimal deep-mode skeleton

```json
{
  "meta": {
    "schema_version": "1.0.0",
    "skill": "china-fund-deep-analysis",
    "code": "005827",
    "name": "示例基金",
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
    "one_liner": "综合 80 分，建议继续持有",
    "decision_tag": "建议继续持有",
    "star": 4,
    "score_total": 80,
    "confidence": "medium",
    "disclaimer": "基于公开信息研究，不构成投资建议"
  },
  "profile": {"code": "005827", "name": "示例基金", "share_class": "A"},
  "metrics": {"return_1y": 0, "return_3y": 0, "max_drawdown": 0, "sharpe": null},
  "scores": {
    "total": 80,
    "breakdown": {
      "return": 80, "risk": 80, "manager": 80,
      "stability": 80, "size_liquidity": 80
    }
  },
  "nav_series": [],
  "drawdown_series": [],
  "returns": {},
  "risk": {},
  "portfolio": {},
  "manager": {},
  "style_drift": {},
  "sip": {},
  "action_map": {},
  "peers": [{"code": "005827", "is_primary": true}],
  "better_choices": [],
  "peer_errors": [],
  "risks": [],
  "data_quality": {"grade": "B", "missing_fields": [], "sources": []},
  "glossary": [],
  "debate": {
    "votes": [],
    "summary": "",
    "action": "建议观望",
    "key_level": ""
  },
  "charts": {},
  "render": {"theme": "dark_terminal", "language": "zh-CN"}
}
```

注意：上表是键完整性骨架，不代表可通过业务验收；真正交付前仍需补齐净值序列、同类、风险卡与六角色博弈。
```

---

### 状态

| 文档 | 状态 |
|---|---|
| `SKILL.md` | 已给 |
| `references/scoring-model.md` | 已给 |
| `references/dashboard_schema.md` | **本次完整版** |
| `references/ai_native_debate.md` | 已给 |

---
