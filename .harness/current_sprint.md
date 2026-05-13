# 当前 Sprint：本体董事会 v2

## 目标

- 落地 15 个核心本体董事。
- 将本体规则命中接入 CLI、Web、record、follow-up。
- 建立可重复的 ontology quality gate。
- 新增视觉版董事会建议书视图和导出。

## 非目标

- 不新增外部 SaaS。
- 不自动联网蒸馏新人物。
- 不提交真实 `records/*.json` 或 `.super-board-model.json`。
- 不为了视觉版新增外部模型调用；AI 洞察只复用现有材料和记录。

## 验收命令

- `python3 scripts/validate_skill.py`
- `python3 scripts/validate_ontology.py`
- `python3 -m unittest tests/test_validate_skill.py`
- `python3 -m unittest tests/test_validate_ontology.py`
- `python3 scripts/evaluate_ontology_quality.py`
- `python3 -m unittest tests/test_visual_report_builder.py`
- `uv run python .harness/harness_check.py`
- `uv run python .harness/harness_eval.py`
- `cd web && npm run build`
