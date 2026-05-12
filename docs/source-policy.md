# 来源与版权边界

Super Board 的 persona 档案是自有结构化提炼，不复制外部 skill、文章、书籍或访谈原文。

## 允许

- 使用公开材料中反复出现的思想框架、决策模型和分析角度。
- 使用 license 已审计的上游 persona skill 作为结构和方法来源，并在 `sources/` 中保留来源记录。
- 使用 `nuwa-skill` 的多源采集、三重验证、框架提炼和诚实边界方法来蒸馏缺失人物。
- 对未直接命中的人物，先在 `nuwa_distillations/<persona-id>/` 保存完整女娲产物，再压缩适配到 `personas/<persona-id>.md`。
- 记录来源类型，例如书籍、公开演讲、访谈、股东信、博客、产品发布材料。
- 用自己的语言总结人物在某类问题上的常见关注点。
- 在不确定时说明“材料不足”或“这是基于公开材料的框架化推断”。

## 禁止

- 复制 GitHub 上其他 persona skill 的正文作为本项目资产。
- 使用未审计 license 的外部正文作为本项目资产。
- 编造人物原话、引用、私人观点、实时立场或未公开信息。
- 把模型对人物的印象当成事实来源。
- 输出可能让读者误以为本人参与审议或背书的表述。

## 写作边界

- 可以写“从其公开材料中常见的长期主义框架看”。
- 不要写“他会说”或“他一定认为”。
- 可以提炼“关注现金流、护城河、资本配置”。
- 不要伪造具体页码、访谈日期或演讲标题。

## 维护要求

- 新增 persona 时必须包含 `source_basis` 和 `anti_hallucination_rules`。
- 新增上游 persona 时必须更新 `sources/awesome-persona-skills.yaml` 和 `sources/license-audit.md`。
- 新增非直接命中 persona 时必须同时包含 `nuwa_distillations/<persona-id>/SKILL.md`、6 个 `references/research/*.md` 文件和 `references/sources/source-index.md`。
- 如果引用具体来源，必须确认来源存在，并避免长段摘录。
- 如果材料来源薄弱，档案中要明确适用边界。
