# Super Board 本体董事会 v2 实施计划

## 目标

把 Super Board 从 25 个蒸馏 persona 的松散董事会，升级为 15 个核心本体董事 + 按需触发专家 + 归档蒸馏档案的可验证决策系统。

## 范围

- 保留 5 个委员会，每个委员会 3 个核心本体董事。
- 新增 persona ontology、committee ontology、ontology trace schema。
- 运行器、Web、复盘脚本统一输出 `ontology_trace`、`ontology_rule_hits`、`committee_rule_matrix`。
- 增加离线质量评测和 Harness 任务，不联网调用模型。

## 验证

- `python3 scripts/validate_skill.py`
- `python3 scripts/validate_ontology.py`
- `python3 -m unittest tests/test_validate_skill.py`
- `python3 -m unittest tests/test_validate_ontology.py`
- `python3 scripts/evaluate_ontology_quality.py`
- `uv run python .harness/harness_check.py`
- `uv run python .harness/harness_eval.py`
- `cd web && npm run build`
