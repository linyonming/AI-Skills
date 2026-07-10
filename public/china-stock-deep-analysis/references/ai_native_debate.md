```markdown
# AI-Native Debate Spec

`china-fund-deep-analysis` 的六角色博弈规范。  
当外部 `debate_engine.py` 不可用、返回 `fallback: true`，或用户要求“你自己推演”时，由 **OpenClaw 主模型** 基于已核验的 `dash.json` 直接生成博弈 JSON，再合并进看板。

本文件只定义：**角色、输入、输出 JSON、投票规则、质量门禁**。  
不在这里编造净值、回撤、持仓或经理数据。

---

## 1. When to use

优先顺序：

1. `scripts/debate_engine.py` 正常跑通且 `fallback != true` → 直接用其输出  
2. 引擎失败 / `fallback: true` / API 不可用 → **启用本规范做 AI-native 覆盖**  
3. 用户明确说“不要博弈/跳过博弈” → 不生成 `debate`，渲染器跳过  
4. 用户说“你自己推演/多空辩论/六角色分析” → 即使引擎可用，也可用本规范增强

禁止：

- 在无 `dash.json` 关键字段时凭空辩论  
- 把规则兜底稿当最终深度报告默认交付  
- 辩论过程引入未在数据里出现的“内幕/传闻”当证据

---

## 2. File paths

| 用途 | 路径 |
|---|---|
| 输入 dashboard | `fund_work/{code}_dash.json` |
| AI-native 输出 | `fund_work/{code}_ai_debate.json` |
| 引擎输出（对照） | `fund_work/{code}_debate.json` |
| 合并回写 | 用 `scripts/merge_debate.py` 写入 `dash.json` 的 `debate` 字段后重渲染 |

合并命令示例：

```bash
python3 scripts/merge_debate.py \
  --dash fund_work/005827_dash.json \
  --debate fund_work/005827_ai_debate.json \
  --out fund_work/005827_dash.json

python3 scripts/render_dashboard.py \
  --input fund_work/005827_dash.json \
  --out /root/.openclaw/workspace/outputs/fund_005827_20260511.html
```

---

## 3. Input contract

主模型只应阅读 `dash.json` 中的已有事实，最低输入：

必需：

- `meta.code` / `meta.name` / `meta.fund_type`
- `summary`（可先有初稿，辩论后可被覆盖动作标签）
- `metrics`
- `scores.breakdown`
- `risk` 或等价回撤/波动字段
- `manager`
- `peers`（快速模式可空，但完整模式应有）
- `portfolio`（可部分缺失，缺失必须在 reasoning 里承认）

建议附加：

- `style_drift`
- `sip`
- `action_map`
- `data_quality`
- `better_choices`
- `returns`

输入降级规则：

- 缺回撤/同类/经理任一关键项 → 最终 `confidence` 不得超过 `medium`
- 缺两项以上关键项 → `confidence=low`，`action` 优先 `建议观望`
- 不得用假设数据补齐后假装高置信

---

## 4. Six roles

固定 6 个角色，ID 不可改，顺序建议保持如下（便于前端展示）：

### 4.1 `manager_analyst` 基金经理分析师

关注：

- 任职时间、任职回报、是否近期更换
- 风格是否清晰、能力圈是否匹配基金类型
- 经理项对中长期可信度的支撑

偏多条件：任期长、任职业绩稳定、风格一致  
偏空条件：频繁更换、任职短、风格漂移与经理叙事冲突

### 4.2 `risk_analyst` 风险分析师

关注：

- 最大回撤、当前回撤、波动、修复时间
- 下行风险是否被收益补偿
- 规模、流动性、结构复杂度带来的额外风险

偏多条件：回撤可控、修复尚可、风险收益比健康  
偏空条件：深回撤未修、波动畸高、风险指标恶化

### 4.3 `quant_analyst` 量化分析师

关注：

- 1Y/3Y 收益、年化、Sharpe、Alpha/Beta
- 同类百分位、收益是否只靠短窗口脉冲
- 统计证据是否支持“真超额”而非行情贝塔

偏多条件：多窗口稳健、Sharpe 友好、同类持续靠前  
偏空条件：短强长弱、指标依赖单一区间、同类口径不稳

### 4.4 `allocator_analyst` 资产配置分析师

关注：

- 在组合中的角色：核心底仓 / 卫星 / 主题弹性 / 防守
- 与用户可能风险偏好的匹配
- 同类替代是否更优（`peers` / `better_choices`）

偏多条件：定位清晰、可承担配置功能、替代优势不明显  
偏空条件：定位模糊、更优同类明确、拥挤或重复暴露

### 4.5 `longterm_analyst` 长期投资分析师

关注：

- 3Y+ 逻辑是否仍成立
- 定投适配、费率摩擦、持有体验
- 是否值得用时间换空间

偏多条件：适合定投/长期持有，过程回撤可解释  
偏空条件：长期逻辑松动，持有性价比下降

### 4.6 `contrarian_analyst` 反方分析师

硬性要求：

- **必须挑主要风险**，不能和多头复读
- 即使总分高，也要给出“什么情况下会错”
- 重点攻击：规模过大、风格漂移、经理依赖、同类更优、数据缺失、阶段性拥挤

偏空是默认姿态；若数据实在强，可给出“有条件中性”，但仍需列失效条件。

---

## 5. Output JSON schema

顶层结构：

```json
{
  "schema_version": "1.0.0",
  "mode": "ai_native",
  "code": "005827",
  "name": "易方达蓝筹精选混合",
  "as_of": "2026-05-11",
  "generated_at": "2026-05-11T12:10:00+08:00",
  "source_dash": "fund_work/005827_dash.json",
  "fallback": false,
  "votes": [],
  "tally": {
    "bull": 3,
    "bear": 2,
    "neutral": 1,
    "bull_pct": 50,
    "bear_pct": 33,
    "neutral_pct": 17
  },
  "direction": "bull",
  "confidence": "medium",
  "summary": "中长期逻辑仍在，回撤中等，更适合持有/定投而非追高猛加。",
  "action": "建议定投",
  "key_level": "核心经理离任，或回撤跌破近3年警戒带（约-25%）需复盘",
  "bull_case": [],
  "bear_case": [],
  "watchpoints": [],
  "data_gaps": [],
  "decision_tags": ["建议继续持有", "建议定投"]
}
```

### 5.1 `votes[]` 单角色结构

```json
{
  "role_id": "risk_analyst",
  "role_name": "风险分析师",
  "direction": "neutral",
  "confidence": 0.66,
  "score_hint": 76,
  "one_liner": "回撤中等可持有，但波动决定它不是稳钱工具。",
  "reasoning": "近3年最大回撤约22%，修复月份尚可；波动不低，说明收益来自风险暴露而非纯稳健。",
  "evidence": [
    "max_drawdown=-22.4",
    "volatility=18.6",
    "recovery_months=10"
  ],
  "risks": [
    "若市场进入长熊，持有体验会明显变差"
  ],
  "invalidators": [
    "回撤显著超过历史中枢且迟迟不修复"
  ]
}
```

字段约束：

| 字段 | 类型 | 说明 |
|---|---|---|
| `role_id` | string | 固定枚举，见下 |
| `role_name` | string | 中文名 |
| `direction` | string | `bull` / `bear` / `neutral` |
| `confidence` | number | 0–1，角色自身把握 |
| `score_hint` | number/null | 可选，0–100，角色视角分 |
| `one_liner` | string | ≤40字为佳 |
| `reasoning` | string | 2–5 句，必须引用数据 |
| `evidence` | string[] | 可追溯字段/事实，至少 2 条 |
| `risks` | string[] | 至少 1 条 |
| `invalidators` | string[] | 至少 1 条 |

`role_id` 枚举：

- `manager_analyst`
- `risk_analyst`
- `quant_analyst`
- `allocator_analyst`
- `longterm_analyst`
- `contrarian_analyst`

必须 6 票齐全；缺角色视为不合格输出。

---

## 6. Direction & action mapping

### 6.1 角色 `direction`

- `bull`：支持继续持有 / 定投 / 谨慎新增  
- `bear`：倾向减仓 / 止盈 / 不建议新增  
- `neutral`：信息不足或多空平衡，观察为主  

### 6.2 全局 `direction`

由 6 票统计：

```text
bull_pct   = bull / 6
bear_pct   = bear / 6
neutral_pct = neutral / 6
```

判定：

| 条件 | `direction` |
|---|---|
| `bull >= 4` 且 `bear <= 1` | `bull` |
| `bear >= 4` 且 `bull <= 1` | `bear` |
| 其余 | `neutral` |

补充：

- 反方 `contrarian_analyst` 若为 `bear`，不自动否决多头，但最终 `confidence` 通常不超过 `high`
- 若 `data_gaps` 含回撤/经理/同类等关键缺失，`direction` 再乐观也要降级置信度

### 6.3 最终 `action`（决策标签）

只能输出 SKILL 允许标签之一：

- `建议继续持有`
- `建议定投`
- `建议减仓`
- `建议止盈`
- `建议观望`
- `不建议新增`

推荐映射（可被风险一票降级）：

| 局面 | action |
|---|---|
| 偏多 + 波动可接受 + 适合长期积累 | `建议定投` |
| 偏多 + 已持有 + 无需再强调建仓 | `建议继续持有` |
| 多空胶着 / 数据不足 | `建议观望` |
| 偏空 + 已有较大涨幅 | `建议减仓` 或 `建议止盈` |
| 偏空 + 长期落后 / 经理不稳 | `不建议新增` |

可同时给 `decision_tags` 数组（最多 2 个），例如：

```json
"action": "建议定投",
"decision_tags": ["建议继续持有", "建议定投"]
```

但 `action` 必须是唯一主标签，供 Hero 与 Telegram 一句话使用。

### 6.4 全局 `confidence`

- `high`：关键数据齐全，票型清晰（≥4 票同向），无明显口径冲突  
- `medium`：缺 1 个非致命字段，或 3:2:1 / 3:3 胶着  
- `low`：缺关键字段，或证据冲突大，或快速模式信息过薄  

规则：

- `confidence=low` 时，禁止“强烈推荐”叙事  
- `confidence=low` 时，`action` 优先 `建议观望`  
- 即使 `scores.total` 很高，数据缺口也可把辩论置信度压到 medium/low  

---

## 7. Writing rules for each vote

每票必须遵守：

1. **先数据后观点**：`evidence` 里出现的数字/事实必须能在 `dash.json` 找到或由其直接推导  
2. **不跨角色复读**：六段 `one_liner` 不能六句同义反复  
3. **反方必须真反**：`contrarian_analyst.direction` 默认为 `bear` 或带强风险的 `neutral`；只有在空方实在打不动时才可 `neutral`，且仍要列失效条件  
4. **基金口径**：禁止 PE/PB/K 线买卖点话术；改用回撤、同类、经理、规模、风格漂移、定投适配  
5. **条件化表达**：用“若…则…”，避免“必然大涨/必亏”  
6. **承认局限**：持仓滞后、评级缺失、区间不同要在 `data_gaps` 或角色 `risks` 写明  

`reasoning` 推荐模板：

```text
1) 关键事实（1–2个指标）
2) 该事实对持有/定投意味着什么
3) 主要反证或前提
```

---

## 8. Aggregator requirements

裁定者（主模型最后综合）必须输出：

### `summary`

- 2–4 句中文  
- 覆盖：总判断 + 主要支撑 + 主要风险  
- 不要堆指标表，要决策语言  

### `action` + `key_level`

- `action`：唯一主标签  
- `key_level`：基金语境下的关键线，不是股价支撑位  

`key_level` 可写：

- 回撤警戒带（如“跌破近3年最大回撤警戒带约-25%需复盘”）  
- 经理事件（如“核心经理离任即重启评估”）  
- 定投条件（如“仅在可持有3年+且能承受中等波动时定投”）  
- 止盈条件（如“达到目标收益或主题拥挤后减仓”）  

### `bull_case` / `bear_case` / `watchpoints`

```json
{
  "bull_case": [
    "3Y 收益与同类排名仍有优势",
    "经理稳定，风格未崩"
  ],
  "bear_case": [
    "规模偏大可能影响灵活度",
    "回撤中等，弱市体验一般"
  ],
  "watchpoints": [
    "下季报持仓是否继续漂移",
    "规模变化与经理是否变更",
    "同类替代基金的收益-回撤比"
  ]
}
```

每项 2–4 条，短句。

### `data_gaps`

```json
"data_gaps": [
  "晨星评级缺失",
  "持仓截至上季度，非实时"
]
```

无缺口写 `[]`，不要省略键。

---

## 9. Worked example（结构示例）

```json
{
  "schema_version": "1.0.0",
  "mode": "ai_native",
  "code": "005827",
  "name": "易方达蓝筹精选混合",
  "as_of": "2026-05-11",
  "generated_at": "2026-05-11T12:10:00+08:00",
  "source_dash": "fund_work/005827_dash.json",
  "fallback": false,
  "votes": [
    {
      "role_id": "manager_analyst",
      "role_name": "基金经理分析师",
      "direction": "bull",
      "confidence": 0.78,
      "score_hint": 84,
      "one_liner": "经理任期与风格匹配，是中长期持有的重要加分项。",
      "reasoning": "主经理任职年限较长，任职回报与基金中长期业绩匹配，未见近12个月核心更换。",
      "evidence": ["tenure_years=7.6", "recent_change=false", "manager.score=84"],
      "risks": ["能力圈若转向不擅长赛道，叙事会削弱"],
      "invalidators": ["核心经理离任或管理职责显著稀释"]
    },
    {
      "role_id": "risk_analyst",
      "role_name": "风险分析师",
      "direction": "neutral",
      "confidence": 0.7,
      "score_hint": 76,
      "one_liner": "回撤中等可持有，但绝非低波动工具。",
      "reasoning": "最大回撤与波动说明需承受权益风险；尚可修复，故不直接看空，也不能当稳钱。",
      "evidence": ["max_drawdown=-22.4", "volatility=18.6", "current_drawdown=-6.3"],
      "risks": ["弱市连续回撤会打击定投坚持度"],
      "invalidators": ["回撤显著恶化且修复时间明显拉长"]
    },
    {
      "role_id": "quant_analyst",
      "role_name": "量化分析师",
      "direction": "bull",
      "confidence": 0.74,
      "score_hint": 88,
      "one_liner": "1Y/3Y 与 Sharpe 支持其有统计优势，不是纯短脉冲。",
      "reasoning": "多窗口收益与同类百分位较一致，Sharpe 可接受，短窗口没有单独劫持总分。",
      "evidence": ["return_1y=18.2", "return_3y=42.5", "sharpe=1.42", "peer_rank_1y_pct=18"],
      "risks": ["若未来 Beta 上升而 Alpha 消失，排名会回吐"],
      "invalidators": ["连续多个窗口跌出同类前50%"]
    },
    {
      "role_id": "allocator_analyst",
      "role_name": "资产配置分析师",
      "direction": "bull",
      "confidence": 0.69,
      "score_hint": 82,
      "one_liner": "更适合作为主动权益核心仓，而不是主题博弈仓。",
      "reasoning": "定位清晰，可承担组合成长仓；是否“更优”取决于用户已有暴露，当前替代优势未压倒性。",
      "evidence": ["suggested_position_role=核心底仓", "peers>=4", "score_total=86"],
      "risks": ["若组合已堆满同类风格，再增加会造成拥挤"],
      "invalidators": ["better_choices 出现显著更优且相关性高的替代"]
    },
    {
      "role_id": "longterm_analyst",
      "role_name": "长期投资分析师",
      "direction": "bull",
      "confidence": 0.73,
      "score_hint": 85,
      "one_liner": "3年视角下可持有，定投比一次性追高更合适。",
      "reasoning": "长期业绩与定投适配分不低；关键是投资者能否穿越中等回撤。",
      "evidence": ["sip.suitable=true", "sip.score=84", "return_ann_3y=12.5"],
      "risks": ["高位大额一次性买入会放大回撤体感"],
      "invalidators": ["投资期限被缩短到1年以内"]
    },
    {
      "role_id": "contrarian_analyst",
      "role_name": "反方分析师",
      "direction": "bear",
      "confidence": 0.67,
      "score_hint": 62,
      "one_liner": "规模与拥挤是隐患，且持仓披露滞后会让人过度自信。",
      "reasoning": "高分不等于低风险；规模偏大、风格轻度漂移、持仓非实时，都可能让“过去有效”在未来打折。",
      "evidence": ["scale_yi=312.5", "style_drift.level=轻度", "portfolio.lag_note=持仓截至季报"],
      "risks": ["投资者可能在回撤中误判为风格失效而错误操作"],
      "invalidators": ["若后续规模回落到更优区间且风格重新收敛，空方论据减弱"]
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
  "summary": "六角色整体偏多：经理与中长期业绩支撑持有，但回撤与规模问题限制了激进加仓。更合理的动作是继续持有并分批定投，而不是追高重仓。",
  "action": "建议定投",
  "key_level": "核心经理离任，或回撤跌破近3年警戒带（约-25%）时停止加仓并复盘",
  "bull_case": [
    "经理稳定且中长期业绩仍具同类优势",
    "定投适配较好，适合3年+资金"
  ],
  "bear_case": [
    "规模偏大，灵活度存疑",
    "波动与回撤决定持有体验一般"
  ],
  "watchpoints": [
    "经理是否变更",
    "风格漂移是否升温",
    "同类替代的收益-回撤是否反超"
  ],
  "data_gaps": [
    "晨星评级缺失",
    "持仓截至季报"
  ],
  "decision_tags": ["建议继续持有", "建议定投"]
}
```

---

## 10. Merge contract

`merge_debate.py` 合并后，`dash.json.debate` 至少应有：

```json
{
  "mode": "ai_native",
  "fallback": false,
  "votes": [],
  "direction": "bull",
  "confidence": "medium",
  "bull_pct": 67,
  "bear_pct": 17,
  "summary": "...",
  "action": "建议定投",
  "key_level": "...",
  "tally": {},
  "bull_case": [],
  "bear_case": [],
  "watchpoints": [],
  "data_gaps": []
}
```

并同步：

- `meta.debate_enabled = true`
- `meta.debate_fallback = false`（AI-native 成功覆盖后）
- 如需统一对外结论：可用辩论结果回写  
  - `summary.decision_tag = debate.action`  
  - `summary.one_liner`（若一句话结论过时）  
  - `summary.confidence` 取 `min(原置信度, 辩论置信度)` 更保守的一档  

不得：

- 合并后仍留空 `votes`
- 把 `fallback: true` 的规则稿与 AI-native 稿混装且不标注
- 渲染成功但 `debate.action` 不在允许标签集合内

---

## 11. Prompt skeleton（主模型用）

```text
你是中国基金深度分析的裁定者。请基于给定 dash.json 事实，生成六角色博弈 JSON。

硬规则：
1. 只使用输入数据，不编造净值/回撤/持仓/评级
2. 角色固定为 6 个：manager_analyst, risk_analyst, quant_analyst, allocator_analyst, longterm_analyst, contrarian_analyst
3. 反方必须给主要风险与失效条件
4. 禁止股票 PE/PB/K线话术
5. action 只能是：建议继续持有 / 建议定投 / 建议减仓 / 建议止盈 / 建议观望 / 不建议新增
6. 输出严格 JSON，不要 Markdown 包裹

请输出符合 references/ai_native_debate.md 的完整对象。
```

输入时附上：

- 压缩后的 `meta/summary/metrics/scores/risk/manager/portfolio/style_drift/sip/peers/better_choices/data_quality`
- 不要整份超长原始抓取日志

---

## 12. Quality gate

AI-native 辩论通过条件：

```python
assert len(debate["votes"]) == 6
roles = {v["role_id"] for v in debate["votes"]}
assert roles == {
    "manager_analyst", "risk_analyst", "quant_analyst",
    "allocator_analyst", "longterm_analyst", "contrarian_analyst"
}
assert debate["action"] in {
    "建议继续持有", "建议定投", "建议减仓",
    "建议止盈", "建议观望", "不建议新增"
}
assert debate.get("summary") and debate.get("key_level")
assert debate.get("fallback") is False
contrarian = next(v for v in debate["votes"] if v["role_id"] == "contrarian_analyst")
assert contrarian.get("risks") and contrarian.get("invalidators")
for v in debate["votes"]:
    assert v["direction"] in {"bull", "bear", "neutral"}
    assert len(v.get("evidence") or []) >= 2
```

验收失败则重生成，不得把半成品写入最终 HTML。

---

## 13. Anti-patterns

- 六角色假辩论、真复读（one_liner 高度同义）  
- 反方变成“温和补充多头”  
- 用新闻情绪替代回撤/同类/经理证据  
- 把缺失数据脑补成精确 Alpha/Beta  
- 输出 `强烈买入` 等非标准标签  
- 快速模式信息不足却给 `confidence=high`  
- 只给长文不给结构化 `votes`  
- 合并后 HTML 无「多智能体博弈裁定」区块所需字段  

---

## 14. Minimal valid stub

仅用于接口打通测试，**不可作为最终用户交付**：

```json
{
  "schema_version": "1.0.0",
  "mode": "ai_native",
  "code": "000000",
  "name": "示例基金",
  "as_of": "2026-05-11",
  "generated_at": "2026-05-11T00:00:00+08:00",
  "source_dash": "fund_work/000000_dash.json",
  "fallback": false,
  "votes": [
    {
      "role_id": "manager_analyst",
      "role_name": "基金经理分析师",
      "direction": "neutral",
      "confidence": 0.5,
      "score_hint": 70,
      "one_liner": "经理信息有限，暂不增强结论。",
      "reasoning": "示例占位。",
      "evidence": ["manager.score=70", "recent_change=false"],
      "risks": ["样本不足"],
      "invalidators": ["出现经理更换"]
    },
    {
      "role_id": "risk_analyst",
      "role_name": "风险分析师",
      "direction": "neutral",
      "confidence": 0.5,
      "score_hint": 70,
      "one_liner": "风险信号不足，保持观察。",
      "reasoning": "示例占位。",
      "evidence": ["max_drawdown=null", "volatility=null"],
      "risks": ["回撤未知"],
      "invalidators": ["回撤数据补齐后需重估"]
    },
    {
      "role_id": "quant_analyst",
      "role_name": "量化分析师",
      "direction": "neutral",
      "confidence": 0.5,
      "score_hint": 70,
      "one_liner": "量化证据不足。",
      "reasoning": "示例占位。",
      "evidence": ["return_1y=null", "sharpe=null"],
      "risks": ["指标缺失"],
      "invalidators": ["补齐1Y/3Y后重算"]
    },
    {
      "role_id": "allocator_analyst",
      "role_name": "资产配置分析师",
      "direction": "neutral",
      "confidence": 0.5,
      "score_hint": 70,
      "one_liner": "配置角色不清。",
      "reasoning": "示例占位。",
      "evidence": ["peers=[]", "fund_type=other"],
      "risks": ["定位不明"],
      "invalidators": ["明确组合目标后重估"]
    },
    {
      "role_id": "longterm_analyst",
      "role_name": "长期投资分析师",
      "direction": "neutral",
      "confidence": 0.5,
      "score_hint": 70,
      "one_liner": "长期结论暂不可给。",
      "reasoning": "示例占位。",
      "evidence": ["sip.suitable=null", "return_3y=null"],
      "risks": ["期限不匹配"],
      "invalidators": ["明确3Y资金后再评估"]
    },
    {
      "role_id": "contrarian_analyst",
      "role_name": "反方分析师",
      "direction": "bear",
      "confidence": 0.6,
      "score_hint": 55,
      "one_liner": "信息不足时不应新增。",
      "reasoning": "示例占位；缺数据时默认保守。",
      "evidence": ["confidence=low", "missing_critical_fields=true"],
      "risks": ["盲目确认偏误"],
      "invalidators": ["关键数据补齐且多窗
口验证通过"]
    }
  ],
  "tally": {
    "bull": 0,
    "bear": 1,
    "neutral": 5,
    "bull_pct": 0,
    "bear_pct": 17,
    "neutral_pct": 83
  },
  "direction": "neutral",
  "confidence": "low",
  "summary": "示例占位：数据不足，默认观望。",
  "action": "建议观望",
  "key_level": "关键数据补齐前不新增",
  "bull_case": [],
  "bear_case": ["关键指标缺失"],
  "watchpoints": ["补齐回撤/经理/同类数据"],
  "data_gaps": ["示例缺口"],
  "decision_tags": ["建议观望"]
}
```

---

## 15. Alignment checklist

与周边文档对齐：

| 项目 | 对齐对象 |
|---|---|
| 五维评分不在辩论里重算权重 | `references/scoring-model.md` |
| `action` 标签集合 | `SKILL.md` Decision tags |
| `dash.debate` 字段 | `references/dashboard_schema.md` |
| 缺数据降置信度 | Data Trust / Completion Gate |
| 反方强制风险 | SKILL 六角色要求 |

完成标准一句话：

> 有 6 票、有主动作、有关键失效线、有真实证据、能合并进 HTML，并且不编造基金数据。
```

可直接保存为：

`public/china-fund-deep-analysis/references/ai_native_debate.md`

---

### 和当前基金版的衔接

- 引擎失败或 `fallback: true` → 按本文生成 `fund_work/{code}_ai_debate.json`
- `merge_debate.py` 写回 `dash.debate`
- 重渲染 HTML，确认有「多智能体博弈裁定」
- 再跑 SKILL 里的 Completion Gate
