# Super Board 人工 Smoke 记录

此文件记录用三类样例输入检查 skill 行为的人工验收点。它不是自动化测试结果，也不伪造完整模型运行日志。

## 产品需求样例

输入：`examples/product-requirement.md`

必须覆盖：

- 用户价值：是否真正节省产品经理整理会议的时间。
- 差异化：与普通会议纪要、转写总结工具的区别。
- 产品风险：上传动作是否形成使用阻力，转写质量是否影响可靠性。
- 下一步实验：用少量真实会议文本验证行动项提取准确率和节省时间。

检查结论：`SKILL.md`、`protocols/board-review.md` 和 `templates/board-memo.md` 已要求输出用户价值、风险、行动建议和验证问题，可支撑此类审议。

## 项目计划样例

输入：`examples/project-plan.md`

必须覆盖：

- 里程碑：8 周迁移节奏是否有足够缓冲。
- 依赖：部门配合、权限盘点、旧入口回滚。
- 资源风险：1 名项目经理和 2 名兼职运营是否足够。
- 执行建议：先迁移高价值低风险文档，建立回滚和灰度机制。

检查结论：默认 board 中的咨询委员会、商业委员会和产品委员会分别覆盖执行节奏、组织责任和用户访问风险。

## 商业计划样例

输入：`examples/business-plan.md`

必须覆盖：

- 市场：中小企业客服效率提升是否是强需求。
- 商业模式：按坐席订阅是否与价值和成本匹配。
- 护城河：知识库接入、数据反馈和工作流嵌入是否形成防御。
- 可投性判断：渠道获客、合规风险和数据安全是关键验证项。

检查结论：投资委员会、创业委员会和咨询委员会分别覆盖现金流、防御性、增长路径、市场结构和风险验证。

## 审议模式样例

输入：`examples/output-quick-triage-board-memo.md`、`examples/output-red-team-board-memo.md`、`examples/output-product-discovery-board-memo.md`

必须覆盖：

- `quick_triage` 能在短材料下快速给出 Go / Pivot / No-Go 和下一步验证。
- `red_team` 优先输出失败路径、停止条件和反证实验。
- `product_discovery` 聚焦用户任务、价值风险、可用性风险和发现问题。

检查结论：`boards/modes/*.yaml` 已把启用委员会、输出深度、必选章节和 persona appendix 行为显式化。

## 证据包样例

必须覆盖：

- 每条核心判断区分 fact、inference 或 assumption。
- 每条判断包含证据来源、置信度、反向证据和反证实验。
- 低置信假设不能写成事实。

检查结论：`templates/board-memo.md`、深度输出样例和 validator 已要求 `证据包` 与 `假设账本`。

## 决策记录样例

必须覆盖：

- CLI dry-run 能生成 prompt bundle 和 `records/<decision-id>.json` 骨架。
- 真实 record 默认被 `.gitignore` 忽略，只保留 `records/.gitkeep`。
- follow-up 脚本能读取 record 并生成 30 / 60 / 90 天复盘 prompt。

检查结论：第一版运行器只装配本地结构，不调用模型、不联网、不写全局配置。
