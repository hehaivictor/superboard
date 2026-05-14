# 当前 Sprint：人物本体图谱 v3

## 目标

- 覆盖 37 个本体人物，新增 `ontology/persona_graphs/*.json`。
- 将人物本体从规则列表升级为对象、关系、动作、证据、边界和演化记录。
- 让规则命中、席位选择、建议书、视觉报告和 Web API 统一消费 persona graph。
- 建立人物图谱校验、治理校验、动作审计和 prompt compiler 测试。

## 非目标

- 不联网自动蒸馏新人物。
- 不做用户个人数字分身。
- 不提交真实 `records/*.json` 或 `.super-board-model.json`。
- 不生成伪原话、私人记忆或人物本人背书。
- 不展示未参与席位。

## 执行纪律

- 使用 Superpowers：`executing-plans`、`test-driven-development`、`verification-before-completion`。
- 新行为先写失败测试，再写实现。
- 每个阶段完成后跑对应验证命令。
- 关键事件追加 `logs/execution_stream.log`。

## 验收命令

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
