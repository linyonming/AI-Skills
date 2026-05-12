# Screener Dashboard JSON Schema

## Top-level

```json
{
  "title": "AI应用潜力股筛选",
  "date": "2026-05-11",
  "market": "A股",
  "theme": "AI应用",
  "universe": "候选池来源和覆盖范围",
  "verdict": "一句话结论",
  "opportunity_level": "低/中/高/极高",
  "risk_level": "低/中/高/极高",
  "top3": [],
  "top10": [],
  "funnel": [],
  "matrix": [],
  "factor_summary": [],
  "deep_cards": [],
  "risk_heatmap": [],
  "excluded": [],
  "tracking_plan": [],
  "data_sources": [],
  "blind_spots": [],
  "glossary": []
}
```

## Candidate Item

```json
{
  "rank": 1,
  "name": "公司名",
  "code": "000001",
  "price": "10.20",
  "score": 8.1,
  "style": "核心观察/进攻弹性/低估修复/困境反转/防守配置",
  "industry": "行业",
  "reason": "入选理由",
  "risk": "主要风险",
  "trigger": "触发/确认条件",
  "invalid": "失效/剔除条件",
  "metrics": {"pe":"15", "pb":"1.2", "roe":"12%", "profit_growth":"30%"},
  "factors": [
    {"name":"基本面质量", "score":7.6, "note":"现金流稳定"}
  ]
}
```

## Funnel Item

```json
{"stage":"原始股票池", "count":80, "note":"AI应用相关A股"}
```

## Matrix Item

```json
{"name":"公司名", "code":"000001", "x":7.2, "y":8.1, "size":420, "style":"核心观察"}
```

x 通常为估值性价比，y 通常为成长/弹性，size 可用市值或成交额。
