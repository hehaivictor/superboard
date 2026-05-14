# Super Board 本体董事会 v2 实施计划

## 目标

把 Super Board 从 25 个蒸馏 persona 的松散董事会，升级为 21 个核心本体董事 + 按需触发专家 + 归档蒸馏档案的可验证决策系统。

## 范围

- 保留 7 个常驻委员会，每个委员会 3 个核心本体董事。
- 新增 persona ontology、committee ontology、ontology trace schema。
- 运行器、Web、复盘脚本统一输出 `ontology_trace`、`ontology_rule_hits`、`committee_rule_matrix`。
- 运行器统一输出 `selected_seats`、`seat_viewpoints`、`seat_selection_trace`，建议书只展示本次实际参与席位。
- 增加离线质量评测和 Harness 任务，不联网调用模型。

## 视觉版建议书增量

- 新增 `visual_report` 数据结构，把同一份 `record` 和 `board_memo` 装配成卡片式报告。
- 新增视觉报告模板和导出能力，不替换原董事会建议书。
- Web 中间区域支持“正文建议书 / 视觉版建议书”切换。
- AI 洞察只允许从已有字段提炼，不新增外部事实或第二次模型调用。

## 验证

- `python3 scripts/validate_skill.py`
- `python3 scripts/validate_ontology.py`
- `python3 -m unittest tests/test_validate_skill.py`
- `python3 -m unittest tests/test_validate_ontology.py`
- `python3 scripts/evaluate_ontology_quality.py`
- `python3 -m unittest tests/test_visual_report_builder.py`
- `python3 -m unittest tests/test_seat_view_selector.py`
- `python3 -m unittest tests/test_persona_display_names.py`
- `uv run python .harness/harness_check.py`
- `uv run python .harness/harness_eval.py`
- `cd web && npm run build`
