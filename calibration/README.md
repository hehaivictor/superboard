# Super Board 校准说明

校准用于记录委员会在不同类型决策上的长期表现，帮助后续复盘改进审议质量。

## 原则

- 只记录已复盘的真实结果，不凭感觉给 persona 排名。
- 不自动改变最终建议权重；第一版只展示校准信号。
- 不声称统计显著，不把少量样本包装成预测能力。
- 不记录敏感原文，只记录脱敏后的判断类型、假设命中情况和复盘结论。
- 以规则级校准为主：记录 `persona_id + rule_id` 在某类问题上是否反复有效，不评价人物“对错”。

## 建议字段

- `decision_id`：对应 `records/<decision-id>.json`。
- `input_type`：产品需求、项目计划或商业计划。
- `mode_id`：使用的审议模式。
- `committee_id`：委员会 ID。
- `persona_id`：本体人物 ID。
- `rule_id`：触发的本体规则。
- `judgment_type`：机会、风险、反证、执行建议。
- `outcome_status`：hit、miss、partial、unknown。
- `evidence_note`：复盘依据的简短说明。
- `counter_test_result`：当时反证实验是否真的执行，以及结果如何。
- `updated_at`：复盘更新时间。

## 使用边界

校准记录只能帮助维护者发现重复有效或重复失效的审议模式，不能替代真实用户研究、财务尽调、法律意见或专业风险评估。
