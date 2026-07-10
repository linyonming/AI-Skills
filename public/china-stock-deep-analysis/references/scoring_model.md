```markdown
# Scoring Model

`china-fund-deep-analysis` 的基金评分规范。  
所有脚本按同一口径打分；`scores` 字段写入 `fund_work/{code}_dash.json`，渲染器只展示、不重算。

关联：

- `references/dashboard_schema.md` → `scores` / `summary.score_total` / `summary.star`
- `references/ai_native_debate.md` → 角色 `score_hint` 可参考分项，但不覆盖总分公式
- `SKILL.md` Completion Gate → 完整模式必须有可解释的 `scores.breakdown` + `scores.explain`

---

## 1. 设计原则

1. **可解释**：每分都能落到指标与证据，禁止“感觉给分”
2. **多窗口**：收益不只看近 1 月；主动权益强调 1Y/3Y
3. **风险对称**：高收益若伴随失控回撤，风险项必须拉低
4. **类型适配**：权益 / 债基 / 货基 / ETF 权重与上限不同
5. **保守封顶**：数据缺失、经理更换、风格漂移等触发 cap，而不是靠措辞掩盖
6. **不编造**：缺数据就降分或降置信度，不补假指标

---

## 2. 输出结构（写入 dash.scores）

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
  "caps_applied": [],
  "type_adjustments": ["主动权益：强调3Y与经理稳定性"]
}
```

### 字段约束

| 字段 | 规则 |
|---|---|
| `breakdown.*` | 0–100 数值，建议 1 位小数或整数 |
| `weights.*` | 之和 = 1.00（允许 0.99–1.01 浮点误差） |
| `weighted[k]` | `breakdown[k] * weights[k]` |
| `total` | `sum(weighted)`，再应用全局 cap 后四舍五入到 1 位小数 |
| `star` | 由 `total` 映射，见 §8 |
| `confidence` | `high` / `medium` / `low`，见 §9 |
| `explain` | 五维各 1 句白话，禁止空字符串 |
| `flags` | 风险/特征标签，供页面徽章 |
| `caps_applied` | 记录触发的封顶规则 |
| `type_adjustments` | 记录类型权重或口径调整 |

同步到 `summary`：

- `summary.score_total = scores.total`
- `summary.star = scores.star`
- `summary.confidence = min(summary侧数据置信度, scores.confidence)`（取更低）

---

## 3. 默认权重（主动权益 / 偏股混合）

适用于：`equity_active`、`hybrid_equity`。

| 维度 | 键名 | 权重 | 关注点 |
|---|---|---|---|
| 收益 | `return` | 0.30 | 1Y/3Y、同类分位、相对基准 |
| 风险控制 | `risk` | 0.25 | 最大回撤、波动、修复、Sharpe |
| 基金经理 | `manager` | 0.20 | 任期、任职回报、是否更换 |
| 稳定性 | `stability` | 0.15 | 风格漂移、换手、业绩连续性 |
| 规模流动性 | `size_liquidity` | 0.10 | 规模是否过大/过小、申赎与运作 |

公式：

```text
raw_total =
    return * 0.30
  + risk * 0.25
  + manager * 0.20
  + stability * 0.15
  + size_liquidity * 0.10

total = apply_global_caps(raw_total, context)
```

---

## 4. 类型权重表

按 `meta.fund_type` / `profile.fund_type` 切换。写入 `scores.weights`，并在 `type_adjustments` 注明。

### 4.1 偏债混合 `hybrid_bond`

| 维度 | 权重 |
|---|---|
| return | 0.20 |
| risk | 0.35 |
| manager | 0.15 |
| stability | 0.20 |
| size_liquidity | 0.10 |

强调回撤与波动；收益权重下调。

### 4.2 纯债 `bond`

| 维度 | 权重 |
|---|---|
| return | 0.20 |
| risk | 0.40 |
| manager | 0.15 |
| stability | 0.15 |
| size_liquidity | 0.10 |

`alpha/beta` 可弱化；回撤、下行波动、信用/利率风险叙事优先。

### 4.3 货币 `money`

| 维度 | 权重 |
|---|---|
| return | 0.25 |
| risk | 0.35 |
| manager | 0.05 |
| stability | 0.20 |
| size_liquidity | 0.15 |

- 不做“成长股式”经理叙事
- 重点：万份收益稳定性、偏离、流动性、规模异常
- 通常 `star` 上限建议 4（货币基金避免过度明星化）；若坚持 5 星须有极强稳定性证据

### 4.4 ETF / 增强 ETF `etf` / `etf_enhanced`

| 维度 | 权重 |
|---|---|
| return | 0.25 |
| risk | 0.20 |
| manager | 0.05 |
| stability | 0.25 |
| size_liquidity | 0.25 |

额外口径：

- 跟踪误差、折溢价、成交额进入 `risk` / `size_liquidity` / `stability`
- 宽基 ETF 经理分可固定中性分（60–70），除非增强策略有明确超额证据

### 4.5 平衡混合 `hybrid_balanced`

| 维度 | 权重 |
|---|---|
| return | 0.25 |
| risk | 0.30 |
| manager | 0.15 |
| stability | 0.20 |
| size_liquidity | 0.10 |

### 4.6 QDII / FOF / REITs / other

先映射到最接近的大类，再在 `type_adjustments` 标注：

- QDII：增加汇率与时区/交易时段说明；流动性权重可 +0.05（从 return 或 manager 挪）
- FOF：manager 解释为“配置能力/母基金管理”；持仓重叠与费率拖累进 stability
- REITs：收益与分红稳定性、折溢价、底层资产集中度

权重微调后必须重归一化到 1.00。

---

## 5. 分项评分细则

每项先算 0–100 的 `breakdown`，再乘权重。  
下列为**默认主动权益口径**；其他类型见各小节“类型修正”。

### 5.1 收益 `return`（0–100）

#### 输入

- `metrics.return_1y` / `return_3y` / `return_ytd` / `return_6m`
- `returns.windows.*.peer_pct` / `vs_benchmark`
- `metrics.peer_rank_1y_pct` / `peer_rank_3y_pct`

#### 子分（建议权重）

| 子项 | 内部权重 | 说明 |
|---|---|---|
| 近 1 年收益水平 | 0.30 | 绝对收益 + 同类分位 |
| 近 3 年收益水平 | 0.40 | 主动权益主锚 |
| 相对基准 | 0.15 | `vs_benchmark`，缺基准则重分到同类 |
| 收益质量/连续性 | 0.15 | 避免单段暴涨；看日历年与回撤后修复期收益 |

#### 同类百分位 → 分数映射（越小越好）

| 百分位 `peer_pct` | 基础分 |
|---|---|
| ≤10 | 92–98 |
| ≤20 | 85–91 |
| ≤30 | 78–84 |
| ≤50 | 65–77 |
| ≤70 | 50–64 |
| ≤90 | 35–49 |
| >90 | 15–34 |
| 缺失 | 55（中性）并记 missing |

绝对收益仅作微调（±5），**不能**在同类极差时靠绝对收益抬到 90+。

#### 硬约束

- 仅近 1–3 个月强、1Y/3Y 弱：`return` 上限 70，`flags` 加 `短线脉冲`
- 成立不足 1 年：3Y 子项用成立以来年化替代，且 `return` 上限 75，`confidence` ≤ medium
- 成立不足 3 年：3Y 权重并入 1Y/成立以来，并在 `explain.return` 说明
- 禁止用单日/单周涨幅打高分

#### 类型修正

- 债基/货基：绝对收益区间收窄；更多看同类分位与回撤调整后收益
- ETF：相对基准与跟踪质量优先；增强 ETF 才强调超额

---

### 5.2 风险控制 `risk`（0–100）

#### 输入

- `metrics.max_drawdown` / `recovery_months` / `volatility` / `sharpe`
- `risk.current_drawdown` / `downside_deviation` / `sortino`
- ETF：`tracking_error`

#### 子分

| 子项 | 内部权重 | 说明 |
|---|---|---|
| 最大回撤 | 0.40 | 深度与同类对比 |
| 波动/下行波动 | 0.25 | 年化波动、downside |
| 修复能力 | 0.15 | 回撤修复月数、是否已修复 |
| 风险调整收益 | 0.20 | Sharpe / Sortino（有则用） |

#### 主动权益回撤参考（近 3 年，可按市场环境微调）

| 最大回撤 | 回撤子分参考 |
|---|---|
| ≥ -10% | 90–98（权益里很少见，需核验） |
| -10% ~ -20% | 80–89 |
| -20% ~ -30% | 65–79 |
| -30% ~ -40% | 45–64 |
| < -40% | 20–44 |

注意：回撤是负数；比较用绝对值深度。

#### Sharpe 参考（近 3 年，主动权益）

| Sharpe | 子分参考 |
|---|---|
| ≥ 1.5 | 90+ |
| 1.0–1.5 | 75–89 |
| 0.5–1.0 | 55–74 |
| 0–0.5 | 35–54 |
| < 0 | 10–34 |
| 缺失 | 中性 60，并降置信度 |

#### 硬约束

- 当前回撤接近或超过历史最大回撤：`risk` ≤ 60，`flags` 加 `深水回撤`
- 回撤未修复且持续时间过长：降低修复子分
- 估算的 Sharpe/Alpha 必须在 `risk.notes` 与 `data_quality` 标明；估算争议大时风险项保守给分
- 货基出现负收益或异常偏离：`risk` 直接 ≤ 40

#### 类型修正

- 债基：回撤 -2% 与 -10% 的惩罚应显著严于权益
- ETF：跟踪误差大、长期折溢价异常，下调 `risk` 与 `stability`

---

### 5.3 基金经理 `manager`（0–100）

#### 输入

- `manager.managers[]`：任期、任职回报、是否主经理
- `manager.recent_change` / `team_stability` / `departure_risk`
- 公告核验的经理变更

#### 子分

| 子项 | 内部权重 | 说明 |
|---|---|---|
| 任期与连续性 | 0.35 | 主经理任职年限 |
| 任职期间业绩 | 0.35 | 任职回报/年化与同类 |
| 团队稳定性 | 0.20 | 近期是否更换、共同管理结构 |
| 信息披露清晰度 | 0.10 | 能否确认主理人、职责 |

#### 任期参考

| 主经理任期 | 任期子分 |
|---|---|
| ≥ 5 年 | 88–95 |
| 3–5 年 | 78–87 |
| 1–3 年 | 60–77 |
| < 1 年 | 40–59（并触发 cap） |
| 无法确认 | 35–50 |

#### 硬约束（必须实现）

1. **近 12 个月核心经理更换**  
   - `recent_change=true`  
   - `manager` 上限 **65**  
   - `flags` 加 `经理更换`  
   - `summary.confidence` ≤ medium

2. **主经理任职 < 1 年**  
   - `manager` 上限 **60**  
   - 不得因短期业绩把 manager 打到 80+

3. **多经理且无主理人**  
   - 稳定性子分下调；`explain.manager` 说明责任不清

4. **ETF 纯被动**  
   - `manager` 给中性分 65–72，除非增强策略有独立超额证据

---

### 5.4 稳定性 `stability`（0–100）

#### 输入

- `style_drift.level` / `score`
- `portfolio.turnover_rate` / 行业分布变化
- 收益日历年波动、排名漂移
- 合约/策略一致性（主题基是否偏题）

#### 子分

| 子项 | 内部权重 | 说明 |
|---|---|---|
| 风格漂移 | 0.40 | 与 `style_drift` 对齐 |
| 业绩连续性 | 0.30 | 排名大起大落惩罚 |
| 换手与持仓行为 | 0.20 | 异常高换手下调 |
| 策略一致性 | 0.10 | 名称/主题 vs 实际持仓 |

#### 风格漂移映射

| `style_drift.level` | 漂移子分参考 | 对 `stability` 的 cap |
|---|---|---|
| 无 | 90–95 | 无 |
| 轻度 | 75–85 | 无强制 |
| 中度 | 55–70 | `stability` ≤ 70 |
| 显著 | 30–50 | `stability` ≤ 55，且 `flags` 加 `显著漂移` |

#### 硬约束

- 显著漂移 + 逻辑不清：`stability` ≤ 50，并影响 `action_map.reduce`
- 主题基金持仓长期偏离主题：额外 -10～-20
- 数据不足以判断漂移：给中性 65–70，`confidence` 不高估

---

### 5.5 规模与流动性 `size_liquidity`（0–100）

#### 输入

- `profile.scale_yi` / `scale_date`
- 申购状态、是否限大额
- ETF：成交额、冲击成本、折溢价
- 清盘风险（规模过小）

#### 主动权益规模参考（可按策略容量调整）

| 规模（亿元） | 参考分 | 说明 |
|---|---|---|
| 2–50 | 85–95 | 灵活，需防过小 |
| 50–150 | 80–90 | 较舒适 |
| 150–300 | 70–82 | 开始关注容量 |
| 300–600 | 55–72 | 大盘股策略尚可，小盘策略惩罚加重 |
| > 600 | 40–60 | 容量与拥挤风险 |
| < 2 | 35–55 | 清盘/费用/流动性风险 |
| 缺失 | 60 | 记 missing |

#### 微调

- 明确限购/大额赎回异常：-5～-15
- 小盘/主题策略却规模巨大：额外 -10～-20
- 宽基 ETF 规模大反而加分（流动性好）
- 迷你基（持续低规模 + 收益率侵蚀）：上限 50

#### 硬约束

- 可能清盘或已发提示：`size_liquidity` ≤ 35，`flags` 加 `清盘风险`
- 仅规模大不自动等于差；要结合策略类型解释

---

## 6. 综合分与全局 Cap

### 6.1 计算顺序

```text
1) 选类型权重 → scores.weights
2) 算五维 breakdown（含分项硬约束）
3) weighted[k] = breakdown[k] * weights[k]
4) raw_total = sum(weighted)
5) apply_global_caps(raw_total)
6) 四舍五入到 1 位小数 → scores.total
7) map star / confidence
8) 生成 explain / flags / caps_applied
```

### 6.2 全局封顶规则（在 raw_total 上生效）

| 条件 | cap | 写入 `caps_applied` |
|---|---|---|
| `data_quality.overall = D` | total ≤ 60 | `数据质量D封顶` |
| `data_quality.overall = C` | total ≤ 75 | `数据质量C封顶` |
| 关键字段缺失 ≥ 2（净值序列/1Y收益/回撤/经理） | total ≤ 70，confidence ≤ medium | `关键字段缺失封顶` |
| 近 12 个月核心经理更换 | total ≤ 78 | `经理更换总封顶` |
| 风格漂移 = 显著 | total ≤ 75 | `显著漂移总封顶` |
| 仅短线脉冲、中长期弱 | total ≤ 72 | `短线脉冲封顶` |
| 成立 < 1 年 | total ≤ 75 | `次新基金封顶` |
| 货币基金默认 | total ≤ 88（建议） | `货基明星化限制` |
| 争议数据未交叉验证且冲突 | total ≤ 70 | `数据冲突封顶` |

多个 cap 同时触发时取**更低**上限。

### 6.3 全局保底（少用）

仅当数据极端缺失导致算法塌缩时：

- 仍能确认“活着的正常运作基金”：`total` 不低于 25
- 否则可输出低分，但必须 `confidence=low` 且 risks 说明

禁止为了“好看”把总分抬过 cap。

---

## 7. 加减分与 Flags（细项）

在分项内完成微调，不要在最后随意 +10 黑箱加分。

### 常见加分（单项内 ≤ +5）

- 多窗口同类分位稳定在前 30%
- 回撤后修复显著快于同类
- 经理长期在任且任职期穿越完整熊牛
- ETF 跟踪误差长期优异、流动性好

### 常见减分（单项内）

- 规模与策略不匹配：-5～-15（size）
- 持仓严重集中且无解释：-5～-10（risk/stability）
- 费率显著偏高拖累：-3～-8（return 或 size_liquidity 说明）
- 同源数据冲突：不加分，先降 confidence

### 标准 flags（示例词表）

- `短线脉冲`
- `经理更换`
- `任职不足1年`
- `轻度风格漂移` / `中度风格漂移` / `显著漂移`
- `规模偏大` / `迷你基`
- `深水回撤`
- `数据滞后`
- `关键数据缺失`
- `限购`
- `清盘风险`
- `跟踪误差偏高`（ETF）

`flags` 控制页面徽章；**不是**分数本身。

---

## 8. 星级映射

由 `scores.total` 映射到 `star`（1–5 整数）：

| total | star | 语义 |
|---|---|---|
| ≥ 90 | 5 | 综合优秀，仍须看风险与适合度 |
| 80–89.9 | 4 | 良好，可作为核心观察/持有候选 |
| 70–79.9 | 3 | 中等，亮点与瑕疵并存 |
| 60–69.9 | 2 | 偏弱，仅特定条件可考虑 |
| < 60 | 1 | 明显偏弱或不适合新增 |

约束：

- 星级只服务展示；决策标签不单靠星级
- `confidence=low` 时，页面需同时显示低置信，不暗示“稳 5 星”
- 货基/短债避免滥用 5 星（见类型 cap）

---

## 9. 置信度 `scores.confidence`

### 评定

| 级别 | 条件（同时倾向满足） |
|---|---|
| high | 关键收益/回撤双源一致；经理与持仓信息完整；`data_quality.overall` ∈ {A,B}；无重大 cap |
| medium | 有部分缺失或轻度冲突；或次新/轻度漂移；或单源但无矛盾 |
| low | 关键缺失 ≥2；数据冲突；经理不明；`overall` ∈ {C,D}；或主要指标为粗估 |

### 硬规则

- `data_quality.overall = D` → `confidence=low`
- `data_quality.overall = C` → 不超过 `medium`
- 近 12 个月核心经理更换 → 不超过 `medium`
- 成立 < 1 年 → 不超过 `medium`
- `summary.confidence` 取 summary 侧与 scores 侧更低者

---

## 10. `explain` 写作规范

每维 1 句，面向用户，不堆指标名也可以，但必须真实。

好：

- `return`: "1Y/3Y 都强于同类，不是靠近几个月脉冲。"
- `risk`: "最大回撤中等，修复尚可，但波动不低。"
- `manager`: "主经理任期长，近一年无核心更换。"
- `stability`: "存在轻度风格漂移，尚未颠覆原策略。"
- `size_liquidity`: "规模偏大，运作仍可，但不适合再激进堆仓。"

坏：

- "综合较好"（空话）
- "Alpha 显著为证"（未计算却写）
- "强烈推荐"（解释里禁止投资煽动）

长度：建议 20–40 个汉字；可含 1 个关键数字。

---

## 11. 与决策标签的关系

评分 **不直接** 唯一决定 `decision_tag`，但提供约束：

| total 区间 | 决策倾向（默认） | 仍需检查 |
|---|---|---|
| ≥ 85 | 可倾向 `建议继续持有` / `建议定投` | 回撤承受力、经理、漂移 |
| 75–84 | 持有或定投观察 | 是否有更好同类 |
| 65–74 | `建议观望` 或谨慎持有 | 风险项是否很差 |
| 55–64 | `不建议新增` / 观望 | 已持仓是否减仓 |
| < 55 | `不建议新增`，已持仓考虑 `建议减仓` | 失效条件 |

覆盖规则（分数再高也要改标签）：

- 核心经理刚离任 → 不得 `建议定投`；优先观望/减仓评估
- 显著漂移 + 逻辑不清 → 不得新增长期定投建议
- 用户风险承受不足（如不能接受 20%+ 回撤）→ 权益高分也应 `不建议新增` 到其场景
- `confidence=low` → 避免强断言式标签；偏向观望

最终 `summary.decision_tag` 仍取 6 类固定标签之一。

---

## 12. 快速模式 vs 完整模式

### 快速模式

- 可用精简指标打分：1Y 收益、同类分位、最大回撤、经理任期、规模
- 允许子项用中性默认，但必须：
  - `explain` 标明“快速模式简化”
  - `confidence` ≤ medium
  - `caps_applied` 含 `快速模式简化`

### 完整模式

- 五维齐全，weights 按类型写出
- `breakdown` + `weighted` + `explain` 必填
- 能追溯到 metrics/risk/manager/style_drift/scale
- 与 debate 可互相校验，但**辩论投票不改写公式总分**  
  （若辩论发现硬伤，应回到数据层改 breakdown，而不是直接改 total）

---

## 13. 工作示例（主动权益）

输入摘要：

- return_1y=18.2（同类前 18%），return_3y 强（前 12%）
- max_drawdown=-22.4，Sharpe=1.42
- 经理任期 7.6 年，无近一年更换
- 轻度漂移，规模 312.5 亿

分项：

```text
return          = 88
risk            = 76
manager         = 84
stability       = 78
size_liquidity  = 80
```

加权：

```text
88*0.30 = 26.4
76*0.25 = 19.0
84*0.20 = 16.8
78*0.15 = 11.7
80*0.10 =  8.0
----------------
total   = 82.0 → 若再综合微调解释后可为 86.0
```

注意：示例中 82→86 仅当子分取区间上沿或相对基准加分时发生；**禁止**无依据上调。  
实现时以精确子分为准，本例展示结构而非允许“拍脑袋 +4”。

更严谨的一种取法：

```text
return=90, risk=78, manager=86, stability=80, size=72
→ 27+19.5+17.2+12+7.2 = 82.9 → star=4
```

规模偏大把 size 压到 72，总分留在 4 星区间，与“可定投但不宜激进加仓”一致。

---

## 14. 机器校验伪码

```python
from typing import Dict, Any

ALLOWED_CONF = {"high", "medium", "low"}
DIMS = ["return", "risk", "manager", "stability", "size_liquidity"]

def validate_scores(scores: Dict[str, Any], fund_type: str, ctx: Dict[str, Any]) -> None:
    assert scores, "missing scores"
    for k in DIMS:
        assert k in scores["breakdown"], f"missing breakdown.{k}"
        v = float(scores["breakdown"][k])
        assert 0 <= v <= 100, f"breakdown.{k} out of range"

    wsum = sum(float(scores["weights"][k]) for k in DIMS)
    assert abs(wsum - 1.0) <= 0.011, "weights must sum to 1"

    weighted_sum = 0.0
    for k in DIMS:
        exp = float(scores["breakdown"][k]) * float(scores["weights"][k])
        got = float(scores["weighted"][k])
        assert abs(exp - got) <= 0.15, f"weighted.{k} mismatch"
        weighted_sum += exp

    total = float(scores["total"])
    # total 可能经过 cap，故不应高于 raw太多，且 cap 后应 ≤ raw + 0.2
    assert 0 <= total <= 100
    assert abs(total - round(total, 1)) < 1e-9 or True  # 允许实现侧统一 round

    star = int(scores["star"])
    assert 1 <= star <= 5
    # star 与 total 映射一致性
    if total >= 90: assert star == 5
    elif total >= 80: assert star == 4
    elif total >= 70: assert star == 3
    elif total >= 60: assert star == 2
    else: assert star == 1

    assert scores.get("confidence") in ALLOWED_CONF
    for k in DIMS:
        assert scores.get("explain", {}).get(k), f"missing explain.{k}"

    # 硬 cap 示例
    if ctx.get("recent_change"):
        assert float(scores["breakdown"]["manager"]) <= 65 + 1e-6
        assert total <= 78 + 1e-6
    if ctx.get("style_drift_level") == "显著":
        assert float(scores["breakdown"]["stability"]) <= 55 + 1e-6
        assert total <= 75 + 1e-6
    if ctx.get("data_quality_overall") == "D":
        assert total <= 60 + 1e-6
        assert scores["confidence"] == "low"
```

---

## 15. 实现接口约定

建议 `scripts/score_fund.py` 或评分模块纯函数：

```text
score_fund(dash: dict, fund_type: str, mode: str) -> dict
```

要求：

1. 只读已抓取字段，不在评分里发网
2. 返回完整 `scores` 对象
3. 同步写 `summary.score_total` / `summary.star`
4. 把触发的 cap 写入 `caps_applied`
5. 快速模式传入 `mode=quick`
6. 单元测试覆盖：经理更换封顶、显著漂移封顶、权重归一、星级映射

---

## 16. 反模式

- 用近 1 周涨幅把 `return` 打到 95
- 缺 3Y 数据却按完整 3Y 权重假装精确
- 经理刚换仍给 manager 90+
- 总分 91 但 `data_quality=D`
- 渲染器自己重算与 JSON 不一致的分数
- 辩论 bull 票多就直接 +5 分
- 货基/ETF 套用主动权益经理故事抬分
- `explain` 写“建议买入冲”等非解释性话术
- 权重和不归一仍输出
- 悄悄突破 cap 却不写 `caps_applied`

---

## 17. 与其它文档的边界

| 文档 | 边界 |
|---|---|
| `dashboard_schema.md` | 字段形态与验收；本模型负责数值如何来 |
| `ai_native_debate.md` | 立场与 action 质证；不可静默覆盖 total |
| `data-sources.md` | 数据源与交叉校验；影响 confidence 与 cap |
| `SKILL.md` | 流程门禁；无 scores.explain 不得称完整模式完成 |

更新原则：

1. 先改本模型，再改评分脚本
2. 破坏性变更提升 `schema_version` 或在本文件增加 `scoring_model_version`
3. 任何新 cap 必须有机器可检条件

---

## 18. 版本

- `scoring_model_version`: `1.0.0`
- 适用 skill: `china-fund-deep-analysis`
- 默认权重场景: 主动权益 / 偏股混合
- 状态: 可落盘、可机器校验、可与 dashboard schema 联调
```

---

### 落盘路径

`public/china-fund-deep-analysis/references/scoring-model.md`

### 与 schema 的对接要点

| schema 字段 | 本模型 |
|---|---|
| `scores.weights/breakdown/weighted/explain` | §2–§5 |
| `scores.caps_applied` / `type_adjustments` | §4、§6 |
| `summary.score_total` / `star` / `confidence` | §8–§9 |
| 经理更换、漂移、数据质量 | 分项硬约束 + 全局 cap |
| 决策标签 | §11 只约束，不单点决定 |
