# Persona Skill Adapter

本 adapter 把单人物 skill 转换为 Super Board 可审议的委员会输入。外部 skill 的价值在人物心智模型、决策启发式、反模式和诚实边界；Super Board 的价值在多委员会合议、质询和最终建议书。

## 输入

- 外部 persona skill 的 `SKILL.md`。
- 可用时读取该 skill 的 `references/` 目录，但只提炼结构，不复制长段正文。
- 本地 persona dossier。
- 用户输入材料与第 0 轮审议 brief。

## 输出契约

每个 persona 独立输出以下字段：

- `judgment`：一句话判断。
- `opportunities`：最值得抓住的机会。
- `risks`：最关键失败路径。
- `evidence_requirements`：做判断前必须补的证据。
- `counterfactual_tests`：能推翻当前方案的反证实验。
- `debate_moves`：在组内质询其他 persona 的问题。
- `board_recommendation`：Go / Pivot / No-Go 倾向和条件。

## 适配规则

1. 外部 skill 的“核心心智模型”映射到本项目 `core_models` 和 `decision_rules`。
2. 外部 skill 的“决策启发式”映射到 `deep_diagnostic_questions` 和 `debate_moves`。
3. 外部 skill 的“价值观与反模式”映射到 `red_flags`、`failure_modes` 和 `output_constraints`。
4. 外部 skill 的“诚实边界”映射到 `anti_hallucination_rules`。
5. 外部 skill 的表达风格只保留辨识度，不允许把最终报告写成角色扮演聊天。

## 质量门槛

- 每个 persona 至少提出一个可证伪问题。
- 每个 persona 至少指出一个失败路径。
- 每个委员会至少保留一个组内分歧。
- 最终报告必须能看出 persona 差异，而不是 25 个相似观点。
