# Super Board 人物本体图谱 v3 实施计划

## 目标

把 Super Board 从“人物规则模板 + 席位观点”升级为“人物认知图谱 + 来源证据 + 动作治理 + 反证制衡 + 持续演化”的可验证决策系统。

## 范围

- 覆盖全部 37 个人物：21 个核心席位、10 个按需触发专家、6 个归档人物。
- 新增 `ontology/persona_graphs/*.json`，每个人都具备对象、关系、动作、证据、权限和演化记录。
- 保留 `ontology/personas/*.yaml` 作为兼容索引，不在本轮删除旧结构。
- CLI、Web、record、视觉报告统一消费 persona graph 输出。
- 建议书只展示本次实际参与席位，不展示未启用人物。
- 所有面向用户的人名使用中文展示。

## 人物图谱对象

每个 `persona_graph` 必须包含：

- `person`
- `ontology_contract`
- `sources`
- `claims`
- `mental_models`
- `heuristics`
- `historical_decisions`
- `episodes`
- `expression_patterns`
- `boundaries`
- `contradictions`
- `actions`
- `relations`
- `representative_viewpoints`
- `evidence_graph`
- `model_comparisons`
- `action_audit`
- `eval_cases`
- `ontology_updates`
- `version_log`

## 治理边界

- 不冒充人物本人。
- 不生成伪原话。
- 不编造私人记忆。
- 不让名人效应压过当前材料证据。
- 历史人物必须标注现代适用边界。
- 强反共识或强动员型观点必须触发制衡席位。
- 哲学与人文席位只提供价值、伦理、长期性和边界判断，不替代商业证据。

## 执行顺序

1. 新增 persona graph schema、loader、validator 和对应单测。
2. 全量生成 37 个 `ontology/persona_graphs/*.json`。
3. 重构 ontology matcher 和 seat selector，使命中结果带 `claim_id`、`model_id`、`source_ids`、`boundary_id`、`counter_test_id`、`relation_ids`。
4. 增加 persona actions、action audit 和 prompt compiler。
5. 接入 `super_board_run.py`、decision record、board memo 和 visual report。
6. 接入 Web API 和前端展示。
7. 补充 golden cases、治理测试和 Harness 验收。

## 非目标

- 不联网自动蒸馏新人物。
- 不接外部 SaaS。
- 不做用户个人数字分身。
- 不提交真实 `records/*.json` 或 `.super-board-model.json`。
- 不为了视觉版新增外部模型调用。

## 验证

- `python3 scripts/validate_skill.py`
- `python3 scripts/validate_ontology.py`
- `python3 scripts/validate_persona_graph.py`
- `python3 scripts/evaluate_ontology_quality.py`
- `python3 scripts/evaluate_persona_graph.py`
- `python3 -m unittest tests/test_validate_skill.py`
- `python3 -m unittest tests/test_validate_ontology.py`
- `python3 -m unittest tests/test_persona_display_names.py`
- `python3 -m unittest tests/test_seat_view_selector.py`
- `python3 -m unittest tests/test_visual_report_builder.py`
- `python3 -m unittest tests/test_persona_graph_schema.py`
- `python3 -m unittest tests/test_persona_graph_loader.py`
- `python3 -m unittest tests/test_ontology_matcher_graph.py`
- `python3 -m unittest tests/test_persona_graph_governance.py`
- `python3 -m unittest tests/test_persona_actions.py`
- `python3 -m unittest tests/test_persona_action_audit.py`
- `python3 -m unittest tests/test_compile_persona_prompt.py`
- `uv run python .harness/harness_check.py`
- `uv run python .harness/harness_eval.py`
- `cd web && npm run build`
