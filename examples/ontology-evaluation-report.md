# Super Board 本体质量评测报告

## 评测范围

- 输入样例：`tests/fixtures/ontology/pricing_strategy.md`
- Golden：`tests/golden/pricing_strategy.ontology_trace.json`
- 评测命令：`python3 scripts/evaluate_ontology_quality.py`

## 预期命中

| 人物 | 规则 |
|---|---|
| Warren Buffett | `buffett_moat_cashflow_quality` |
| Michael Porter | `porter_competitive_positioning` |
| Roger Martin | `martin_where_to_play_how_to_win` |
| Charlie Munger | `munger_incentive_misalignment` |

## 质量门槛

- 所有 golden 规则必须命中。
- 按需触发专家不得进入核心规则命中。
- 每条命中规则必须带反证实验。
- 命中结果只来自本地材料和本体规则，不联网调用模型。
