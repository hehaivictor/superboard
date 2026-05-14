# Super Board 本体论优化讨论 Q&A

> 本文整理自围绕「用本体论思想优化 Super Board」的一轮产品与工程讨论。
> 目标是尽量保留原始讨论中的问题、判断、名单、边界和实施计划，不刻意删除信息。
> 文中「建议书」指 Super Board 生成的董事会建议书；「本体」指基于公开资料抽象出的人物概念、规则、证据门槛、反证实验和误用边界。

## Q1：我听说有一个本体论的概念，可以把一个人真正做成数字人，比单纯蒸馏的强很多。这个内容存在吗？如果落地在这个项目中，董事会建议书会更好吗？

存在，但需要澄清边界。

这里说的「本体论」不是简单把一个人的文章、访谈、书籍蒸馏成风格 prompt，而是把一个人的思想系统拆成结构化对象：

- 核心概念。
- 判断规则。
- 适用场景。
- 不适用场景。
- 证据要求。
- 反证方式。
- 经典案例。
- 误用边界。
- 与其他人物观点的冲突关系。

它比单纯蒸馏强的地方在于：

- 蒸馏更像「模仿说话方式」。
- 本体更像「约束这个人物视角如何判断」。
- 蒸馏容易产生风格化幻觉。
- 本体可以让判断更可追踪、可校准、可复盘。

落地到 Super Board 后，董事会建议书会更好，尤其体现在：

- 建议不再只是「某某风格怎么看」。
- 每条观点能追溯到规则和证据。
- 可以区分事实、推断和假设。
- 可以告诉用户：这个判断为什么成立，什么情况下会被推翻。
- 可以跨人物比较：分歧来自事实假设、时间尺度，还是价值排序。

但有一个边界要说清楚：它不会自动让建议书变成真理。如果本体里的来源薄、规则错、案例不充分，反而会制造「结构化幻觉」。所以它应该作为「决策本体 + 证据约束」，不是「数字本人」。

## Q2：现在已经蒸馏的 25 个人，如果做成本体，哪些人会出现来源薄、规则错、案例不充分的问题？

需要分层看。

有些人物适合升级成本体，因为公开资料厚、方法论稳定、案例丰富。

有些人物不适合作为核心本体，因为资料不足、观点过度泛化，或很容易被误用。

### 较适合升级为核心本体的人物

这些人物的公开资料、方法论和案例相对扎实：

- 沃伦·巴菲特。
- 查理·芒格。
- 彼得·德鲁克。
- 迈克尔·波特。
- 克莱顿·克里斯坦森。
- 史蒂夫·乔布斯。
- 杰夫·贝索斯。
- 纳西姆·塔勒布。
- 瑞·达利欧。
- 唐·诺曼。
- 保罗·格雷厄姆。
- 马蒂·卡根。
- 理查德·鲁梅尔特。
- 罗杰·马丁。
- 丽塔·麦格拉思。

### 需要谨慎处理的人物

这些人物不是没有价值，而是如果直接变成本体，容易出现来源薄、规则错、案例不充分或误用风险：

- Peter Thiel：来源和框架足够，但「垄断、秘密、逆向判断」容易诱导过度反共识。需要强制绑定证据门槛，否则本体会鼓励聪明但不可证伪的判断。
- Elon Musk：素材很多，但容易把「第一性原理、极限工程、硬压强」误用到不适合高压组织和硬科技的场景。
- Sam Altman：适合 AI、平台、资本和生态议题，但不适合泛化成所有创业问题的普适规则。
- Naval Ravikant：适合杠杆、复利、个人创造力，但不适合直接判断企业组织执行。
- George Soros：反身性有价值，但不能泛化成所有市场和商业判断。
- Richard Feynman：适合科学思维和解释复杂问题，但不适合直接替代商业判断。
- Peter Thiel、Marc Andreessen 等高表达密度人物，需要尤其防止语录化、口号化。

### 不宜继续作为核心本体的人物

如果公开资料不足、案例难复盘、或方法论主要来自二手归纳，就不宜作为核心本体。可以作为归档蒸馏档案，除非补齐来源、案例和规则。

核心原则：

> 可以有强观点，但必须能说明：这个观点在什么证据下成立，在什么证据下失效。

## Q3：如果中间有不适合的人物，有没有高质量且有代表性的同类人物可以替换？

有。

替换不是简单找更有名的人，而是找：

- 资料更厚的人。
- 方法论更稳定的人。
- 案例更可复盘的人。
- 代表性更强的人。
- 更适合 Super Board 常见议题的人。

### 可替换方向

如果某些咨询类 persona 来源薄，可以替换为：

- 理查德·鲁梅尔特：战略诊断、关键问题、连贯行动。
- 罗杰·马丁：战略选择、Where to Play / How to Win。
- 丽塔·麦格拉思：不确定性、发现驱动规划、竞争优势衰减。

如果某些产品类 persona 过弱，可以替换为：

- 唐·诺曼：人因、可用性、体验。
- 马蒂·卡根：产品发现、产品团队、风险验证。
- 张小龙：用户心智、克制、关系链、产品感。

如果某些投资类 persona 资料不足，可以替换为：

- 查理·芒格：误判心理、激励、反向思考。
- 纳西姆·塔勒布：脆弱性、黑天鹅、反脆弱。
- 瑞·达利欧：周期、系统、原则、分歧机制。

如果想强化中国语境，可以加入：

- 任正非：组织韧性、长期投入、客户中心、危机管理。
- 张一鸣：信息效率、组织机制、产品增长。
- 稻盛和夫：经营责任、长期主义、组织心性。

如果想强化哲学和人文，可以加入：

- 老子：顺势、无为、系统平衡、反过度干预。
- 孔子：责任、秩序、关系伦理、长期信任。
- 王阳明：知行合一、行动校验、内在责任。

## Q4：如果按照推荐替换，5 个委员会还是 25 人吗，还是有所减少？还是有的是本体，有的是蒸馏？

当时的阶段性建议是：

- 不建议继续维持「25 个蒸馏 persona 全部平铺」。
- 推荐先做「15 个核心本体董事 + 按需触发专家 + 归档蒸馏档案」。

原因：

- 25 人全参与会让建议书过长。
- 模型会更容易泛泛而谈。
- 每个人的观点会变薄。
- 可信度会被稀释。

更稳的结构是：

- 核心本体董事：完整本体，默认参与候选。
- 触发专家：完整本体，命中特定场景才参与。
- 归档蒸馏档案：保留历史资料，但不进入用户可见建议书，除非补成本体。

后来讨论进一步升级为新版结构：

- 7 个常驻委员会。
- 21 个核心本体席位。
- 若干按需触发专家。
- 所有用户可见人物都必须本体化。

## Q5：下一步本体论人物优化如果落地，详细实施计划是什么？预期效果是什么？

初始计划是：

1. 扩展 ontology schema。
2. 为核心人物建立结构化本体。
3. 接入 `ontology_trace`。
4. 把本体规则命中接入 CLI、Web 和 record。
5. 在建议书中展示本体规则、证据缺口和反证实验。
6. 增加质量门禁和离线评测。

预期效果：

- 董事会建议不再只是「名人风格」。
- 每个观点都有证据、规则和边界。
- 能区分强证据、弱证据、缺失证据。
- 能追踪某个人物规则为什么被触发。
- 能避免「名人说了算」。
- 能让建议书更可复盘、更可信。

## Q6：一次做好 15 个。基于这个目标，详细计划是什么？市面上有没有同类型董事会类决策产品？

当时的建议是：

- 15 个核心人物可以一次做好，但必须走分阶段验证。
- 不建议只靠 prompt 一口气生成 15 个。
- 每个人都要有本体文件、来源、规则、证据门槛和误用边界。

市面上有一些相近产品或可参考方向：

- AI persona panel。
- AI boardroom。
- Multi-agent decision support。
- 投资委员会 memo 工具。
- 红队审查工具。
- 战略咨询类 AI 工作流。

但大多数产品停留在：

- 多 persona 对话。
- 几个专家角色轮流发言。
- 生成建议报告。
- 会议纪要或战略建议。

Super Board 的差异化应该是：

- 本体化人物。
- 证据链约束。
- 反证实验。
- 决策记录。
- 30 / 60 / 90 天复盘。
- 可校准的委员会机制。

## Q7：需要增加测试验证阶段吗？

需要，而且必须增加。

原因：

- 本体人物越多，越容易出现规则漂移。
- 模型越强，越容易把不完整的规则讲得很像真的。
- 建议书越像正式报告，越需要结构与事实门禁。

测试应该覆盖：

- ontology schema 校验。
- 人物本体字段完整性。
- 触发规则是否命中预期场景。
- 不适用场景是否不会误触发。
- 建议书是否包含证据和反证。
- 视觉版是否没有引入新事实。
- 未配置人物不能进入建议书。
- 用户可见内容不能出现英文展示名。
- 本次参与席位和席位观点必须一致。

## Q8：这次改造会依据 Harness 和 Superpowers 来实现吗？

应该依据。

Harness 负责：

- 明确 sprint 边界。
- 维护验证命令。
- 添加 `.harness/tasks`。
- 跑 `harness_check.py` 和 `harness_eval.py`。
- 把关键事件写入 `logs/execution_stream.log`。

Superpowers 负责：

- 需求和设计阶段使用 `brainstorming`。
- 实施计划使用 `writing-plans`。
- 功能实现使用 `test-driven-development`。
- 异常和 bug 使用 `systematic-debugging`。
- 完成前使用 `verification-before-completion`。
- 收口提交使用 `finishing-a-development-branch`。

原则是：

> 本体论优化不是一次 prompt 修改，而是一套数据、生成、展示、验证、复盘链路的升级。

## Q9：建议书或报告是否可以做成彩色卡片 + 结构化文字的样式？AI 洞察需要新增内容还是复用已有内容？

可以做，而且建议做成「新增视觉版输出，不替换原建议书」。

核心原则：

> 同一份董事会建议书数据，生成两种呈现形态。

原 Markdown 保持严谨；视觉报告负责第一页摘要、卡片化洞察和可转发观感。

### 目标形态

- Web 端新增一个视图：`视觉版建议书`。
- 导出新增按钮：`导出视觉报告`。
- 输出内容仍来自现有 `record`、`board_memo`、`ontology_rule_hits`、`evidence_packets`、`assumptions`。
- 不新增模型调用，不让 AI 重新编造内容，只做结构提炼和视觉排版。

### 可放进卡片的内容

- 最终建议。
- 最大机会。
- 最大风险。
- 关键反证。
- 委员会摘要。
- 本体人物规则命中。
- 证据强度。
- AI 洞察。
- 30 / 60 / 90 天行动。

### 适合结构化正文的内容

- 输入材料拆解。
- 核心判断依据。
- 各委员会详细意见。
- 跨委员会共识与关键分歧。
- 证据包。
- 假设账本。
- 决策记录。
- 附录。

### AI 洞察规则

AI 洞察不新增事实，采用「复用 + 压缩」：

- 复用一句话结论。
- 复用最大机会 / 最大风险。
- 复用关键分歧。
- 复用本体规则中的证据缺口。
- 复用反证实验。

示例：

- 当前核心问题不是是否做，而是定价权是否能被客户证据支撑。
- 最大风险集中在证据强度不足，而不是产品方向本身。
- 下一步优先级应是验证付费意愿、复用频率和销售激励。

## Q10：Peter Thiel 之前被排除，但历史中很多正确决定早期并不可证伪，否则如何突破和创新？

这个质疑成立。

之前把 Peter Thiel 排除，并不代表「反共识人物不该进董事会」。更准确的说法应该是：

> 反共识人物不能以无限制本体规则进入主审议链路。

很多正确决策在早期确实不能被充分证伪，比如新市场、新品类、技术范式变化。但它们通常不是「不可证伪」，而是「短期证据弱、验证周期长、验证方式不传统」。

所以 Peter Thiel 不应该简单排除，而应该被放进更合适的位置：

- 不是普通商业委员会成员。
- 更适合做「反共识与秘密委员会」或「战略非共识观察员」。
- 输出必须标注为：反共识假设、非主流判断、需要延迟验证。
- 每条判断必须绑定「未来如何知道自己错了」。

Peter Thiel 的价值不是直接给 Go / No-Go，而是提出：

- 这里是否存在别人没看到的秘密？
- 这个市场有没有机会形成垄断性优势？
- 当前共识是否只是平庸安全答案？
- 如果要赌，最小可验证赌注是什么？

这样既不会压制创新，也不会让系统变成「聪明但不可验证的判断机器」。

## Q11：董事会建议书最大的效果是名人效应。人选是否应该选国际上或中国有极高知名度、且有丰富素材的人？

是。

董事会建议书的效果不只是理性分析，还有「谁在审议」的心理影响。

如果报告里出现的是高度知名、资料丰富、观点鲜明的人物，用户会更愿意读，也更容易产生共鸣。这个产品天然有一部分「思想品牌」价值。

但选人不能只按名气。建议用三层标准：

- 高知名度：用户一看就知道这个人代表什么。
- 高资料密度：书、访谈、演讲、股东信、公开决策案例足够多。
- 高方法论稳定性：能抽象成规则，而不是只剩个性或金句。

因此可以引入更多高知名度人物，但要分层：

- 核心本体董事：资料厚、规则稳定、可长期复用。
- 名人观察员：观点强、吸引力高，但不直接决定结论。
- 特定模式专家：只在某类问题触发，比如定价、品牌、组织、投资、产品。

## Q12：是否可以增加哲学委员会？哲学或人文因素辅助商业决策，会不会更有说服力？

可以，而且值得加入。

商业决策很多时候不是纯 ROI 问题，还涉及：

- 这个决定服务什么样的人？
- 它是否尊重真实需求，而不是操纵欲望？
- 长期会塑造什么组织性格？
- 它会不会为了增长牺牲信任？
- 这个选择是否符合创始人想建立的世界？

哲学委员会可以承担三个任务：

- 价值判断：这件事是否值得做。
- 长期主义：这件事五年后会不会变成组织负债。
- 人文风险：用户、员工、社会信任是否被透支。

但哲学委员会不能写成玄学。它也要有输出模板：

- 价值冲突是什么？
- 哪个群体会受益，哪个群体会受损？
- 这个选择强化了什么组织习惯？
- 有没有更体面的替代方案？
- 如果必须做，边界条件是什么？

可选人物包括：

- 苏格拉底：追问概念是否成立。
- 亚里士多德：目的论、德性、实践智慧。
- 康德：是否把人当工具。
- 尼采：是否只是从众道德。
- 汉娜·阿伦特：组织责任与平庸之恶。
- 维特根斯坦：语言和概念是否混乱。
- 王阳明：知行合一，判断是否落到行动。
- 孔子：秩序、责任、关系伦理。
- 老子：系统平衡、顺势、反过度干预。

## Q13：基于哲学委员会，还可以有其他新委员会吗？

可以。

未来董事会可以演进成「常设委员会 + 特殊委员会」：

- 商业委员会：市场、商业模式、竞争优势。
- 产品委员会：用户、体验、场景、PMF。
- 投资委员会：风险收益、资本效率、现金流。
- 组织委员会：人才、激励、执行、组织负债。
- 反共识委员会：Peter Thiel 这类，专门挑战共识。
- 哲学与人文委员会：价值、伦理、长期信任。
- 中国商业实践委员会：任正非、张一鸣、稻盛和夫这类，更贴近中国语境。
- 品牌传播委员会：乔布斯、马斯克、奥格威这类，判断叙事、传播和心智占位。

不建议一下子把人堆到 50 个。更好的结构是：

- 核心 21 人。
- 可触发专家席位。
- 每次报告展示实际参与的 7-10 个席位。

## Q14：毛泽东、老子这样的人物该如何归类？

可以纳入，但不要放进普通商业委员会。

### 毛泽东

更适合归到：

- 战略与组织动员委员会。
- 复杂斗争与阶段性策略席位。
- 中国实践思想观察员。

适合处理的问题：

- 弱势方如何对抗强势方。
- 如何判断主要矛盾和次要矛盾。
- 如何做阶段性战略：保存实力、集中突破、形成根据地。
- 如何组织群众、统一认知、建立纪律和执行体系。
- 如何在资源不足时打运动战、游击战、持久战。

不适合直接处理的问题：

- 用户体验细节。
- 现代合规、资本市场、SaaS 定价。
- 高度依赖现代数据、财务模型和产品指标的问题。

使用边界：

- 他的价值是战略判断、组织动员、矛盾分析。
- 不能照搬历史政治语境。
- 必须转译成商业语言。

可转译成：

- 主要矛盾是什么？
- 当前阶段该集中优势资源打哪个点？
- 哪些资源必须先建立根据地？
- 哪些打法是持久战，哪些是速决战？
- 有没有把次要矛盾误当主要矛盾？

### 老子

更适合归到：

- 哲学与人文委员会。
- 反过度设计席位。
- 系统平衡与无为治理席位。

适合处理的问题：

- 是否过度干预、过度管理、过度设计。
- 产品是否违背用户自然行为。
- 组织是否靠强控制制造短期效率但长期失衡。
- 商业策略是否太用力，反而损害信任。
- 是否应该通过「降低动作」获得更大系统收益。

不适合直接处理的问题：

- 市场规模测算。
- 销售漏斗优化。
- 具体产品路线排期。
- 技术实现方案。

老子的价值不是「消极不作为」，而是提醒系统设计里哪些动作会破坏自组织能力。

可转译成：

- 哪些控制是多余的？
- 哪些流程应该顺势而不是强推？
- 是否可以通过减少功能、减少承诺、减少干预来提升结果？
- 当前策略有没有「过犹不及」？
- 哪个地方应该让用户或组织自己形成秩序？

## Q15：我希望在建议书中放每个席位代表人物的观点，这样可以增加用户对于建议书的信任。是否应该做？

应该做，而且这是 Super Board 下一阶段最应该强化的点之一。

但不建议写成「某某本人说」。更合适的写法是：

> 某某视角：基于其公开思想框架，本席位会如何审议这个问题。

这样既保留名人效应，又避免伪造背书。

### 当前缺口

现在建议书里已有：

- 委员会意见。
- 本体规则命中。
- 证据缺口。
- 反证实验。
- Persona 附录。

但它还不够「有脸」。用户看到的是规则和委员会，而不是「巴菲特怎么看、乔布斯怎么看、德鲁克怎么看」。所以信任感和传播感会弱一些。

### 推荐新增章节：席位代表观点

位置建议放在「五个委员会意见」之后，「跨委员会共识与关键分歧」之前。

示例：

```markdown
## 席位代表观点

### 商业委员会：巴菲特视角

- 核心关注：这是不是一门能长期产生现金流、具备护城河的生意。
- 对本次决策的判断：当前机会成立，但需要证明客户愿意持续付费，而不是一次性咨询需求。
- 证据要求：续费率、毛利率、客户获取成本、客户留存周期。
- 反证信号：客户只愿试用，不愿签长期合同。

### 产品委员会：乔布斯视角

- 核心关注：产品是否足够简单、明确、能让用户一眼理解价值。
- 对本次决策的判断：当前方案有价值，但叙事和体验还不够锋利。
- 证据要求：用户是否能在 30 秒内说清楚产品解决什么问题。
- 反证信号：用户觉得这是「又一个 AI 工具」，而不是必须使用的工作流。
```

### 每个席位观点不宜太长

每个人控制在 4 行以内：

- 他的审议镜头是什么。
- 他会支持什么。
- 他会质疑什么。
- 他要求什么证据。

这样既有名人感，又不会把建议书变成名人语录合集。

## Q16：建议书中哪些人参与了讨论，是否也应该把名字列进来，增加用户对于建议书的信任？

应该列，而且这是必要改造，不只是锦上添花。

建议书里要明确「本次参与审议席位」。

推荐放在「一页结论」之后：

```markdown
## 本次审议席位

本次建议书启用了 7 个代表席位，覆盖商业、产品、投资、反共识和哲学人文视角。以下观点均为基于公开材料抽象出的决策本体视角，不代表人物本人实时观点或背书。

| 委员会 | 参与席位 | 本次角色 | 触发原因 |
|---|---|---|---|
| 商业委员会 | 巴菲特 | 长期商业质量 | 判断现金流与护城河 |
| 产品委员会 | 乔布斯 | 核心体验 | 判断产品是否足够锋利 |
| 投资委员会 | 芒格 | 误判与激励 | 识别激励错配和下行风险 |
| 反共识委员会 | Peter Thiel | 非共识机会 | 判断是否存在被忽视的秘密 |
| 哲学与人文委员会 | 老子 | 系统平衡 | 识别过度设计和过度控制 |
```

后来进一步修正为：面向中国用户时，人物名应显示中文译名。

固定边界说明：

> 本报告中的人物观点是基于公开资料抽象出的决策本体视角，不代表人物本人参与、授权、实时观点或背书。

## Q17：未启用的席位要不要展示给用户？

不用。

未启用席位不应该展示给用户。用户只需要知道「这次建议书由哪些席位参与审议」，不需要看到「哪些没参与」。

原因：

- 未启用席位对用户没有直接价值。
- 会增加噪音。
- 会削弱报告的确定感。
- 会让用户误以为系统遗漏了某些人。

调整后的规则：

- 正文只展示「本次参与审议席位」。
- 视觉版只展示「本次参与席位 badge / 卡片」。
- `record` 内部可以保留 `available_seats` 供调试和复盘。
- 面向用户的建议书不输出未启用席位列表。

## Q18：按照头脑风暴后的优化，全新的委员会名单是什么？现在的名单已经是过去式。

推荐升级为：

> 7 个委员会，21 个核心本体席位 + 按需触发专家席位。

### 新版常驻委员会名单

| 委员会 | 核心成员 | 主要价值 |
|---|---|---|
| 商业与长期价值委员会 | 沃伦·巴菲特、杰夫·贝索斯、彼得·德鲁克 | 长期商业质量、客户价值、现金流、管理责任 |
| 创业与非共识机会委员会 | 史蒂夫·乔布斯、彼得·蒂尔、保罗·格雷厄姆 | 产品直觉、非共识机会、创业切口、秘密与垄断潜力 |
| 投资与风险委员会 | 查理·芒格、纳西姆·塔勒布、瑞·达利欧 | 误判、激励、尾部风险、周期与系统风险 |
| 战略与竞争委员会 | 迈克尔·波特、理查德·鲁梅尔特、孙子 | 竞争结构、战略诊断、取舍、避实击虚 |
| 产品与用户委员会 | 马蒂·卡根、唐·诺曼、张小龙 | 产品发现、人因体验、用户心智、端到端体验 |
| 组织与中国商业实践委员会 | 任正非、张一鸣、稻盛和夫 | 组织韧性、长期投入、信息效率、经营哲学 |
| 哲学与人文委员会 | 老子、孔子、王阳明 | 价值判断、系统平衡、责任伦理、知行合一 |

### 为什么不是继续 25 人

不建议一上来扩到 25 或 30 个常驻成员。原因是：

- 建议书会变长。
- 模型生成稳定性下降。
- 每个人物观点的可信度会被稀释。

21 人比较合理：

- 每个委员会 3 人，结构整齐。
- 名字足够有识别度。
- 覆盖商业、创业、投资、战略、产品、组织、哲学。
- 每次报告仍然只展示实际参与的 7-10 个席位观点。

## Q19：按需触发专家有哪些？

推荐如下：

| 触发场景 | 人物 |
|---|---|
| AI 平台与模型产业 | 萨姆·奥尔特曼 |
| 极限工程与第一性原理 | 埃隆·马斯克 |
| 杠杆、财富与个人创造力 | 纳瓦尔·拉维坎特 |
| 平台增长与网络效应 | 里德·霍夫曼 |
| 反身性与市场预期 | 乔治·索罗斯 |
| 企业转型 | 郭士纳 |
| 经验曲线与组合战略 | 布鲁斯·亨德森 |
| 科学思维与复杂问题解释 | 理查德·费曼 |
| 品牌传播与叙事 | 大卫·奥格威 |
| 主要矛盾、弱势突破、组织动员 | 毛泽东 |

几个关键调整：

- 史蒂夫·乔布斯从原来的产品委员会调整到「创业与非共识机会委员会」。他当然懂产品，但在 Super Board 里更有价值的是「产品即战略、极致体验、聚焦、叙事和品类创造」。
- 彼得·蒂尔应该从归档中回归，但不是无约束回归。他进入「创业与非共识机会委员会」，每条观点必须带证据门槛和反证路径。
- 孙子比克劳塞维茨更适合作为第一版战略委员会成员，因为中文用户更熟悉，传播性更强，也更容易和「竞争态势、避实击虚、胜算判断」结合。
- 毛泽东建议先不放进 21 个常驻核心，而是作为「战略与组织动员」触发专家。原因不是能力问题，而是语境太强，容易让建议书风格政治化。等系统稳定后，可以考虑纳入「战略与组织动员委员会」。
- 老子、孔子、王阳明作为哲学与人文委员会，比放亚里士多德、康德更适合第一版中文产品。它们文化识别度高，且可以转译为系统平衡、责任伦理、知行合一。

## Q20：如果名字是英文，不要展示英文，要展示中文译文，因为用户是中国人。

同意。

面向中国用户，建议书和 Web 端所有人物名都应该展示中文译名，英文名只作为内部 `persona_id` 或数据字段保留。

### 展示规则

- 正文建议书：只显示中文名。
- 视觉版卡片：只显示中文名。
- 参与席位名单：只显示中文名。
- 附录：可以显示 `中文名（英文名）`，但默认不建议，除非做来源审计。
- 内部配置、文件名、`persona_id`：继续使用英文 kebab-case，避免破坏代码和 schema。

### 新版 21 人中文展示名单

| 委员会 | 展示成员 |
|---|---|
| 商业与长期价值委员会 | 沃伦·巴菲特、杰夫·贝索斯、彼得·德鲁克 |
| 创业与非共识机会委员会 | 史蒂夫·乔布斯、彼得·蒂尔、保罗·格雷厄姆 |
| 投资与风险委员会 | 查理·芒格、纳西姆·塔勒布、瑞·达利欧 |
| 战略与竞争委员会 | 迈克尔·波特、理查德·鲁梅尔特、孙子 |
| 产品与用户委员会 | 马蒂·卡根、唐·诺曼、张小龙 |
| 组织与中国商业实践委员会 | 任正非、张一鸣、稻盛和夫 |
| 哲学与人文委员会 | 老子、孔子、王阳明 |

### 按需触发专家中文展示名

| 内部人物 | 中文展示 |
|---|---|
| Sam Altman | 萨姆·奥尔特曼 |
| Elon Musk | 埃隆·马斯克 |
| Naval Ravikant | 纳瓦尔·拉维坎特 |
| Reid Hoffman | 里德·霍夫曼 |
| George Soros | 乔治·索罗斯 |
| Lou Gerstner | 郭士纳 |
| Bruce Henderson | 布鲁斯·亨德森 |
| Richard Feynman | 理查德·费曼 |
| David Ogilvy | 大卫·奥格威 |
| Mao Zedong | 毛泽东 |

### 统一映射层

建议在每个人物本体里增加：

```yaml
name: 彼得·蒂尔
english_name: Peter Thiel
display_name: 彼得·蒂尔
```

报告生成时统一使用 `display_name`，不要直接用 `persona_id` 或英文 `name`。

质量门禁：

- 建议书正文不得出现 `Warren Buffett`、`Peter Thiel` 这类英文展示名。
- 视觉卡片不得出现英文展示名。
- `persona_id` 可以继续是 `warren-buffett`。
- 来源审计和内部 schema 可以保留英文名。

## Q21：以上这些人是否都会按照本体论要求实现？

是。

如果按这版方案落地，所有会进入用户可见建议书的人都必须按本体论要求实现，不能再新增「只蒸馏、不结构化」的人物。

### 常驻核心 21 人：完整本体

这 21 人全部要有完整 ontology：

- 中文展示名。
- 英文名。
- 所属委员会。
- 核心概念。
- 决策规则。
- 代表观点模板。
- 证据门槛。
- 反证实验。
- 误用边界。
- 适用场景。
- 不适用场景。
- 来源映射。
- 案例映射。
- 校准备注。

报告里出现「彼得·蒂尔视角」「老子视角」「张小龙视角」时，背后不是一句 prompt，而是结构化本体规则触发。

### 按需触发专家：也是本体

按需专家也必须是 ontology，只是 `ontology_level` 不同：

```yaml
ontology_level: triggered_specialist
```

他们不会每次都参与建议书，只在议题命中特定条件时触发。

### 明确不再使用的方式

不建议再有这种人物进入用户可见建议书：

```yaml
ontology_level: distilled_archive
```

除非只是历史兼容，不进入新建议书。

新建议书里的所有「参与席位」必须来自：

- `core`
- `triggered_specialist`

不能来自：

- 单纯 persona markdown。
- 旧蒸馏档案。
- 未结构化名人素材。
- 临时 prompt 生成的人物观点。

建议写死 validator：

> 如果人物会出现在建议书正文、视觉卡片或参与席位名单中，就必须存在对应 `ontology/personas/<persona-id>.yaml`，且通过 schema 校验。

## Q22：委员会是否常驻？和触发专家的关系是怎样的？

建议设计为：

> 委员会常驻，人物席位按需参与。

也就是说，报告结构中委员会一直存在，但不是每个委员会里的每个人都每次发言。

### 委员会常驻

新版 7 个委员会建议全部常驻：

- 商业与长期价值委员会。
- 创业与非共识机会委员会。
- 投资与风险委员会。
- 战略与竞争委员会。
- 产品与用户委员会。
- 组织与中国商业实践委员会。
- 哲学与人文委员会。

好处：

- 建议书结构稳定。
- 用户每次都知道董事会从哪些维度审议。
- 不会因为触发逻辑不同导致报告结构忽长忽短。
- 哲学、人文、战略这类维度会持续给决策增加深度。

### 委员会内人物不是全量常驻发言

每个委员会有 3 个核心人物，但每次建议书不一定全展开 21 个人观点。

建议规则：

- 每个委员会至少选 1 个代表席位发言。
- 对高度相关的委员会，可选 2 个席位。
- 每份建议书正文展示 7-10 个席位观点。
- 附录可列更多规则命中，但正文不堆人名。

### 触发专家不是委员会外散兵

触发专家应该挂靠到某个委员会或特殊议题席位下。

| 触发专家 | 挂靠委员会 | 触发场景 |
|---|---|---|
| 萨姆·奥尔特曼 | 创业与非共识机会委员会 / 产品与用户委员会 | AI 平台、模型生态、智能体 |
| 埃隆·马斯克 | 战略与竞争委员会 / 组织委员会 | 第一性原理、极限工程、硬科技 |
| 纳瓦尔·拉维坎特 | 创业与非共识机会委员会 | 杠杆、复利、个人创造力 |
| 里德·霍夫曼 | 创业与非共识机会委员会 | 平台增长、网络效应 |
| 乔治·索罗斯 | 投资与风险委员会 | 反身性、市场预期 |
| 郭士纳 | 组织与中国商业实践委员会 | 企业转型 |
| 布鲁斯·亨德森 | 战略与竞争委员会 | 经验曲线、组合战略 |
| 理查德·费曼 | 产品与用户委员会 / 哲学委员会 | 第一性原理、解释复杂问题 |
| 大卫·奥格威 | 商业与长期价值委员会 | 品牌、传播、心智定位 |
| 毛泽东 | 战略与竞争委员会 / 组织委员会 | 主要矛盾、弱势突破、组织动员 |

### 触发专家和核心人物的关系

触发专家不是替代核心人物，而是增强某个委员会在特定问题上的判断力。

有三种关系：

- 补充型：核心人物覆盖基础判断，专家补一个特殊视角。
- 挑战型：专家提出反向判断，挑战核心委员会共识。
- 放大型：专家把某个维度展开到更深。

示例：

- 产品委员会已有唐·诺曼，AI 产品触发萨姆·奥尔特曼。
- 巴菲特偏保守，彼得·蒂尔提醒非共识机会。
- 战略委员会判断竞争结构，毛泽东进一步判断主要矛盾和阶段打法。

## Q23：委员会中代表的选择和专家触发是基于什么逻辑确定的？

建议基于：

> 议题适配度 + 证据命中度 + 观点差异度 + 报告容量约束。

不是随机选，也不是固定轮流选。

### 委员会代表选择逻辑

每个常驻委员会都有 3 个核心人物。生成建议书时，每个委员会至少选 1 个代表，最多选 2 个。

选择公式：

```text
席位得分 =
议题适配度
+ 本体规则命中度
+ 当前材料证据覆盖度
+ 与其他席位观点差异度
- 重复度惩罚
- 证据不足惩罚
```

简单说：

- 谁最适合这个议题，谁优先。
- 谁的本体规则被材料触发，谁优先。
- 谁能提供不同视角，谁优先。
- 如果两个人说的差不多，只保留更强的一个。
- 如果观点很有名但材料证据不足，可以进附录或不参与正文。

### 专家触发逻辑

触发专家不是常驻发言，而是材料中出现特定问题类型时才加入。

触发公式：

```text
专家触发 =
关键词 / 语义主题命中
+ 本体规则命中
+ 当前材料存在对应证据或风险
+ 该专家能补足常驻委员会缺口
```

### 触发示例

| 材料特征 | 触发专家 |
|---|---|
| AI 平台、模型生态、智能体、算力、agent | 萨姆·奥尔特曼 |
| 第一性原理、硬科技、极限工程、成本压缩 | 埃隆·马斯克 |
| 非共识机会、垄断、秘密、品类创造 | 彼得·蒂尔 |
| 弱势突破、主要矛盾、组织动员、阶段打法 | 毛泽东 |
| 品牌定位、广告传播、心智占位 | 大卫·奥格威 |
| 平台、网络效应、增长飞轮 | 里德·霍夫曼 |
| 反身性、市场预期、金融反馈循环 | 乔治·索罗斯 |
| 组织转型、大企业变革 | 郭士纳 |
| 经验曲线、成本优势、组合战略 | 布鲁斯·亨德森 |
| 过度设计、过度控制、系统失衡 | 老子或费曼，视语境 |

### 为什么不是全部人都参与

全部参与会有三个问题：

- 建议书太长。
- 名字越多，每个人的观点越薄。
- 模型更容易生成泛泛而谈的名人观点。

所以要限制正文容量：

- 每个委员会至少 1 人。
- 特别相关委员会最多 2 人。
- 触发专家最多 2-3 人。
- 整份建议书正文建议 7-10 个席位观点。

### 怎么保证不是拍脑袋

要把每个人的触发条件写进 ontology，而不是写死在 prompt 里。

每个人物本体里要有：

```yaml
activation:
  topics:
    - 非共识机会
    - 垄断
    - 秘密
  material_signals:
    - 新品类
    - 市场共识错误
    - 高不确定性但潜在独占优势
  negative_signals:
    - 纯执行优化
    - 成熟市场常规降本
  min_evidence:
    - 至少一个客户或市场证据
    - 至少一个可验证反证实验
```

系统根据这些字段计算，而不是靠模型自由发挥。

## Q24：基于这些内容，完整落地实施计划是什么？

### 目标

把 Super Board 升级为：

> 7 个常驻委员会 + 21 个核心本体席位 + 按需触发专家 + 本次参与席位观点 + 证据与反证约束。

建议书不再只写「委员会意见」，而是明确展示：

- 本次哪些代表人物参与了审议。
- 他们基于什么视角判断。
- 证据是什么。
- 如何反证。

### 数据结构改造

修改：

- `boards/default-board.yaml`
- `ontology/schemas/persona_ontology.schema.json`
- `ontology/schemas/committee_ontology.schema.json`
- `schemas/decision_record.schema.json`
- `schemas/visual_report.schema.json`

新增或扩展字段：

```yaml
display_name: 中文展示名
english_name: 英文名
committee:
ontology_level: core | triggered_specialist
activation:
  topics:
  material_signals:
  negative_signals:
  min_evidence:
representative_viewpoints:
evidence_thresholds:
counter_tests:
misuse_guardrails:
not_for:
source_map:
case_map:
calibration_notes:
```

新增 record 字段：

```json
{
  "selected_seats": [],
  "seat_viewpoints": [],
  "triggered_specialists": [],
  "seat_selection_trace": []
}
```

`available_seats` 可内部保留，但不进入用户可见建议书。

### 席位选择逻辑

新增：

- `scripts/seat_view_selector.py`

输入：

- `material_pack`
- `ontology_rule_hits`
- `committee_rule_matrix`
- `mode_id`
- `board_config`

输出：

- `selected_seats`
- `selection_reason`
- `triggered_rules`
- `evidence_basis`
- `counter_signal`
- `viewpoint_summary`

容量规则：

- 每个常驻委员会至少 1 人。
- 高相关委员会最多 2 人。
- 触发专家最多 2-3 人。
- 正文展示 7-10 个参与席位。
- 不展示未启用席位。

### 建议书模板改造

修改：

- `templates/board-memo.md`

新增章节，放在「一页结论」后：

```markdown
## 本次审议席位

本次建议书启用了 {{seat_count}} 个代表席位。以下观点均为基于公开材料抽象出的决策本体视角，不代表人物本人实时观点或背书。

| 委员会 | 参与席位 | 本次角色 | 触发原因 |
```

新增章节，放在「五个委员会意见」后：

```markdown
## 席位代表观点

### {{display_name}} 视角

- 审议镜头：
- 当前判断：
- 支持证据：
- 缺失证据：
- 反证信号：
```

质量门禁：

- 有 `selected_seats`，必须有对应观点。
- 有观点，必须出现在参与席位名单里。
- 用户可见正文不得出现英文人物名。
- 不展示未启用席位。

### 视觉版改造

修改：

- `scripts/visual_report_builder.py`
- `templates/visual-board-report.md`
- `web/src/components/VisualReport.tsx`
- `web/src/App.tsx`

新增视觉模块：

- 顶部「本次参与席位」中文 badge。
- `seat_view_cards` 人物观点卡。
- 每张卡包含人物、委员会、审议镜头、一句话判断、证据、反证信号。

### Prompt 与生成链路

修改：

- `scripts/super_board_run.py`
- `web/server.py`

生成约束：

- 只使用中文展示名。
- 不得写「某某本人认为」。
- 必须写「某某视角下」。
- 不得生成未经来源支持的直接引语。
- 每个席位观点必须绑定证据和反证。
- 哲学、战略人物必须转译为商业决策语言。

### 测试与验证

新增：

- `tests/test_seat_view_selector.py`
- `tests/test_persona_display_names.py`

扩展：

- `tests/test_validate_ontology.py`
- `tests/test_validate_skill.py`
- `tests/test_visual_report_builder.py`

重点测试：

- 新进人物没有 ontology 文件则失败。
- 用户可见报告不得出现英文人物名。
- `selected_seats` 与 `seat_viewpoints` 一致。
- 未启用席位不出现在建议书正文和视觉版。
- 彼得·蒂尔、老子、毛泽东等只在对应触发条件下参与。
- 视觉报告能展示参与席位卡片。

### Harness 与 Superpowers

必须更新：

- `PLANS.md`
- `.harness/current_sprint.md`

新增 Harness task：

- `.harness/tasks/seat_view_schema.yaml`
- `.harness/tasks/seat_view_selector.yaml`
- `.harness/tasks/persona_display_name.yaml`
- `.harness/tasks/board_memo_selected_seats.yaml`
- `.harness/tasks/visual_report_seat_cards.yaml`

Superpowers 执行顺序：

1. `writing-plans`：固化计划。
2. `test-driven-development`：先写失败测试。
3. `systematic-debugging`：处理触发错误、内容缺失、英文名泄漏。
4. `verification-before-completion`：完成前跑全量验证。
5. `finishing-a-development-branch`：提交、推送、合并。

## Q25：按照真正执行顺序，每一步应该干什么？

### 第 0 步：建立执行边界

目标：先把本轮改造定义成一个独立 sprint，避免和旧的本体 v2 混在一起。

要做：

- 更新 `PLANS.md`：新增「席位代表观点与新版委员会」实施范围。
- 更新 `.harness/current_sprint.md`：写明目标、非目标、验证命令。
- 追加 `logs/execution_stream.log`：记录本轮改造开始。

不做：

- 不先改人物内容。
- 不先改 Web。
- 不先调用模型验证。

验证：

```bash
uv run python .harness/harness_check.py
```

产出：清晰的 sprint 边界。

### 第 1 步：先定数据契约

目标：让后续所有功能都有统一数据结构。

要改：

- `ontology/schemas/persona_ontology.schema.json`
- `ontology/schemas/committee_ontology.schema.json`
- `schemas/decision_record.schema.json`
- `schemas/visual_report.schema.json`

新增字段：

- `display_name`
- `english_name`
- `activation`
- `representative_viewpoints`
- `evidence_thresholds`
- `counter_tests`
- `misuse_guardrails`
- `selected_seats`
- `seat_viewpoints`
- `seat_selection_trace`

同时写失败测试：

- `tests/test_validate_ontology.py`
- `tests/test_persona_display_names.py`

验证目标：

- 没有中文展示名的人物必须失败。
- 会出现在建议书中的人物必须有 ontology。
- `persona_id` 可英文，用户可见名必须中文。

### 第 2 步：更新新版委员会配置

目标：把董事会结构从旧 5 委员会升级为新版 7 委员会。

要改：

- `boards/default-board.yaml`
- `ontology/committees/*.yaml`

新版 7 个常驻委员会：

- 商业与长期价值委员会。
- 创业与非共识机会委员会。
- 投资与风险委员会。
- 战略与竞争委员会。
- 产品与用户委员会。
- 组织与中国商业实践委员会。
- 哲学与人文委员会。

产出：

- 21 个核心席位配置完成。
- 触发专家挂靠关系配置完成。
- 不再把未启用席位作为用户可见内容。

验证：

```bash
python3 scripts/validate_ontology.py
```

### 第 3 步：补齐 21 个核心人物本体

目标：所有核心人物都必须是完整 ontology。

要做：

- 已有 ontology 的人物：补 `display_name`、`activation`、`representative_viewpoints`、`evidence_thresholds`、`counter_tests`。
- 新核心人物：新增完整 `ontology/personas/<persona-id>.yaml`。

核心 21 人：

- 沃伦·巴菲特。
- 杰夫·贝索斯。
- 彼得·德鲁克。
- 史蒂夫·乔布斯。
- 彼得·蒂尔。
- 保罗·格雷厄姆。
- 查理·芒格。
- 纳西姆·塔勒布。
- 瑞·达利欧。
- 迈克尔·波特。
- 理查德·鲁梅尔特。
- 孙子。
- 马蒂·卡根。
- 唐·诺曼。
- 张小龙。
- 任正非。
- 张一鸣。
- 稻盛和夫。
- 老子。
- 孔子。
- 王阳明。

验证：

```bash
python3 scripts/validate_ontology.py
python3 -m unittest tests/test_validate_ontology.py
```

### 第 4 步：补齐触发专家本体

目标：触发专家也必须是 ontology，不能临时 prompt 造人。

新增或升级：

- 萨姆·奥尔特曼。
- 埃隆·马斯克。
- 纳瓦尔·拉维坎特。
- 里德·霍夫曼。
- 乔治·索罗斯。
- 郭士纳。
- 布鲁斯·亨德森。
- 理查德·费曼。
- 大卫·奥格威。
- 毛泽东。

每个人必须有：

- 触发条件。
- 反触发条件。
- 证据门槛。
- 反证信号。
- 误用边界。

验证：

```bash
python3 scripts/validate_ontology.py
python3 scripts/evaluate_ontology_quality.py
```

### 第 5 步：实现席位选择器

目标：决定本次建议书中谁参与审议。

新增：

- `scripts/seat_view_selector.py`
- `tests/test_seat_view_selector.py`

输入：

- `material_pack`
- `ontology_rule_hits`
- `committee_rule_matrix`
- `mode_id`
- `board_config`

输出：

- `selected_seats`
- `seat_viewpoints`
- `seat_selection_trace`

选择规则：

- 每个常驻委员会至少 1 人。
- 高相关委员会最多 2 人。
- 触发专家最多 2-3 人。
- 正文总数控制在 7-10 人。
- 不输出未启用席位。

验证：

```bash
python3 -m unittest tests/test_seat_view_selector.py
```

### 第 6 步：接入 CLI 和 record

目标：让本地运行器生成统一的席位数据。

修改：

- `scripts/super_board_run.py`
- `schemas/decision_record.schema.json`

要求：

- `record` 中写入 `selected_seats`。
- `record` 中写入 `seat_viewpoints`。
- `record` 中写入 `seat_selection_trace`。
- prompt bundle 中带入本次参与席位。

验证：

```bash
python3 scripts/super_board_run.py --input examples/product-requirement.md --mode deep_board_review --dry-run
python3 -m unittest tests/test_validate_skill.py
```

### 第 7 步：改造建议书模板

目标：让正文建议书展示「谁参与了审议」和「他们怎么看」。

修改：

- `templates/board-memo.md`
- `scripts/board_memo_structure.py`
- `tests/test_validate_skill.py`

新增章节：

- `本次审议席位`
- `席位代表观点`

质量门禁：

- 有 `selected_seats`，必须有对应观点。
- 有观点，必须出现在参与席位名单里。
- 用户可见正文不得出现英文人物名。
- 不展示未启用席位。

验证：

```bash
python3 -m unittest tests/test_validate_skill.py
python3 scripts/validate_skill.py
```

### 第 8 步：改造 Web 模型生成链路

目标：Web 端调用模型时也使用新版席位结构。

修改：

- `web/server.py`

要求：

- `/api/preview` 返回 `selected_seats`。
- `/api/preview` 返回 `seat_viewpoints`。
- 模型 prompt 使用中文展示名。
- 模型不得生成「某某本人认为」。
- 模型必须写「某某视角下」。
- 模型输出缺少席位观点时判定失败。

验证：

```bash
python3 -m unittest tests/test_validate_skill.py
```

### 第 9 步：改造视觉版报告

目标：视觉版展示人物观点卡片。

修改：

- `scripts/visual_report_builder.py`
- `templates/visual-board-report.md`
- `web/src/components/VisualReport.tsx`
- `web/src/App.tsx`

新增：

- 顶部参与席位 badge。
- `seat_view_cards`。
- 每张卡包含人物、委员会、审议镜头、当前判断、证据、反证信号。

验证：

```bash
python3 -m unittest tests/test_visual_report_builder.py
cd web && npm run build
```

### 第 10 步：新增 Harness 任务

目标：把新能力纳入持续验证。

新增：

- `.harness/tasks/seat_view_schema.yaml`
- `.harness/tasks/seat_view_selector.yaml`
- `.harness/tasks/persona_display_name.yaml`
- `.harness/tasks/board_memo_selected_seats.yaml`
- `.harness/tasks/visual_report_seat_cards.yaml`

修改：

- `.harness/harness_check.py`
- `.harness/harness_eval.py`

验证：

```bash
uv run python .harness/harness_check.py
uv run python .harness/harness_eval.py
```

### 第 11 步：浏览器 smoke

目标：确认 Web 端真实可用。

步骤：

1. 启动服务。
2. 打开 `http://127.0.0.1:8766/`。
3. 上传材料。
4. 生成建议书。
5. 检查正文版：
   - 有本次审议席位。
   - 有席位代表观点。
   - 没有英文展示名。
6. 检查视觉版：
   - 有参与席位 badge。
   - 有人物观点卡。
   - 导出可用。

验证：

```bash
cd web && npm run build
SUPER_BOARD_WEB_PORT=8766 python3 web/server.py
```

### 第 12 步：全量验证与提交

最终验证命令：

```bash
python3 scripts/validate_skill.py
python3 scripts/validate_ontology.py
python3 -m unittest tests/test_validate_skill.py
python3 -m unittest tests/test_validate_ontology.py
python3 -m unittest tests/test_visual_report_builder.py
python3 -m unittest tests/test_seat_view_selector.py
python3 -m unittest tests/test_persona_display_names.py
python3 scripts/evaluate_ontology_quality.py
uv run python .harness/harness_check.py
uv run python .harness/harness_eval.py
cd web && npm run build
```

提交建议拆成 4 个 commit：

1. `扩展席位本体数据契约`
2. `升级新版委员会与人物本体`
3. `接入本次审议席位选择`
4. `新增席位观点建议书与视觉卡片`

## Q26：执行原则是什么？

- 先 schema，再数据。
- 先测试，再实现。
- 先 CLI / record，再 Web。
- 先正文建议书，再视觉版。
- 每一步都能独立验证。
- 不展示未启用席位。
- 不允许非本体人物进入用户可见建议书。
- 用户可见人物名只用中文展示名。
- Harness 与 Superpowers 验证链必须完整。

## Q27：分析 `qa-palantir-ontology-digital-twin.md` 这个文档，Super Board 中的本体论人物是否可以进化？

可以，而且非常适合进化。

但要先说边界：Super Board 不应该把人物做成「数字本人」，而应该做成「决策本体人物」。

参考文档里真正有价值的地方，不是「让 AI 模仿一个人说话」，而是把一个人拆成可运行的对象系统：

- 对象。
- 关系。
- 动作。
- 权限。
- 审计。
- 持续更新。

Super Board 现在已经有第一层本体雏形：

- `concepts`。
- `decision_rules`。
- `activation`。
- `representative_viewpoints`。
- `evidence_thresholds`。
- `counter_tests`。
- `misuse_guardrails`。

这些字段已经比简单 persona prompt 强很多，但它仍然偏「结构化规则 YAML」，不是完整的 Palantir-style 人物认知图谱。

如果参考 Palantir Ontology 的思想，Super Board 的人物本体可以继续进化成 4 层：

### 第一层：人物从规则表升级为认知对象图

每个人不再只是一个 YAML 文件，而是一个 `persona_graph`。

这个图谱里应该有：

- 人物身份边界。
- 核心概念。
- 判断规则。
- 心智模型。
- 历史案例。
- 适用条件。
- 不适用条件。
- 误用边界。
- 反证实验。
- 与其他人物的分歧关系。

这样，系统不是在问「某某会怎么说」，而是在问：

> 当前问题触发了这个人物本体中的哪些概念、规则、证据门槛和边界？

### 第二层：证据图谱

人物观点必须绑定证据，而不是只绑定名人标签。

每条人物观点都应该能追溯到：

- `source_id`：来自哪类公开来源。
- `claim_id`：抽象出的主张是什么。
- `rule_id`：命中了哪条判断规则。
- `boundary_id`：这个观点有什么边界。
- `counter_test_id`：什么实验可以推翻它。

否则名人效应会变成伪权威。

### 第三层：Action 层

参考 Palantir AIP 的做法，本体不只描述世界，还应该能触发动作。

在 Super Board 里，这些动作可以是：

- 要求补证据。
- 要求反证实验。
- 要求降级建议强度。
- 要求标注高风险判断。
- 要求进入观察而不是 Go。
- 要求把某个观点转译成 30 / 60 / 90 天检查点。

这比「输出一段观点」更有价值，因为它能影响建议书的结构和决策质量。

### 第四层：持续进化与校准

本体人物不能一次写死。

每次建议书之后，都应该能沉淀：

- 哪些人物视角被触发。
- 哪些规则反复有效。
- 哪些规则经常误判。
- 哪些来源不足。
- 哪些案例需要补充。
- 哪些人物不适合某类问题。

这就是从「静态蒸馏」走向「可校准本体」。

## Q28：不要一点点进化，我希望所有人都有脱胎换骨的变化。基于这个目标，详细实施计划是什么？

如果目标不是试点，而是所有人都脱胎换骨，那么应该按一次性重构做。

核心判断是：

> 不再把人物本体当成 `ontology/personas/*.yaml` 的增强字段，而是把所有人物统一升级为 `persona_graph`。

旧 YAML 可以保留兼容，但不再是核心能力。

### 总目标

把 Super Board 的所有人物从「静态人物规则」升级为：

> 人物认知图谱 + 来源证据 + 动作治理 + 反证校准 + 决策复盘。

落地后应该达到：

- 所有人物都有独立 `persona_graph`。
- 每个人都有来源、主张、心智模型、启发式、边界、反证、误用风险、代表观点、评估用例。
- 建议书中的人物观点能追溯到 `claim_id`、`model_id`、`source_id`、`boundary_id`。
- Web、CLI、视觉报告、validator、Harness 都消费同一套新本体。
- 仍然不声称「数字本人」，只说「某某视角下」「基于公开材料抽象出的本体视角」。

### 实施阶段

#### 阶段 0：计划和边界

要做：

- 更新 `PLANS.md`。
- 更新 `.harness/current_sprint.md`。
- 追加 `logs/execution_stream.log`。
- 明确本轮目标是「全量人物图谱化」，不是局部 patch。

非目标：

- 不做真人数字分身。
- 不做语音、头像、聊天人格。
- 不新增外部模型调用。
- 不把来源薄的人硬说成权威。

#### 阶段 1：新增人物图谱 schema

新增：

- `ontology/schemas/persona_graph.schema.json`
- `ontology/schemas/persona_source.schema.json`
- `ontology/schemas/persona_eval_case.schema.json`
- `ontology/schemas/persona_relation.schema.json`

核心字段包括：

```json
{
  "person": {},
  "ontology_contract": {},
  "sources": [],
  "claims": [],
  "mental_models": [],
  "heuristics": [],
  "historical_decisions": [],
  "episodes": [],
  "expression_patterns": [],
  "boundaries": [],
  "contradictions": [],
  "actions": [],
  "relations": [],
  "representative_viewpoints": [],
  "evidence_graph": {},
  "model_comparisons": [],
  "action_audit": {},
  "eval_cases": [],
  "ontology_updates": [],
  "version_log": []
}
```

#### 阶段 2：全量人物图谱生成

所有人物都要有 `ontology/persona_graphs/<person-id>.json`。

每个文件必须包含：

- 中文展示名。
- 英文名只作为内部字段。
- 所属委员会。
- 是否常驻。
- 是否触发专家。
- 激活条件。
- 证据门槛。
- 核心主张。
- 心智模型。
- 决策规则。
- 历史案例。
- 误用边界。
- 反证实验。
- 可触发动作。
- 评估用例。
- 版本日志。

人物观点不能再只是一句「某某会认为」。

必须是：

> 当前材料命中了哪些概念、哪条规则、哪个证据缺口、哪个反证实验，所以某某视角下会给出什么有限判断。

#### 阶段 3：loader 和 validator

新增：

- `scripts/persona_graph_loader.py`
- `scripts/validate_persona_graph.py`
- `scripts/evaluate_persona_graph.py`

校验规则：

- 每个人必须有 `persona_graph`。
- 中文展示名必填。
- 用户可见字段不得依赖英文名。
- 每个核心主张必须有来源。
- 每个心智模型必须有边界。
- 每个动作必须有触发条件和审计字段。
- 每个常驻席位必须有 eval case。
- 误用边界不能为空。

#### 阶段 4：重构匹配与触发逻辑

修改：

- `scripts/ontology_matcher.py`

从旧逻辑：

> material signal -> persona yaml -> rule hit

升级为：

> material signal -> persona graph -> claim/model/boundary/action/relation hits

输出里要包含：

- `persona_graph_refs`
- `claim_hits`
- `mental_model_hits`
- `boundary_hits`
- `counter_test_hits`
- `action_triggers`
- `relation_conflicts`
- `selection_trace`

#### 阶段 5：建议书生成链路

修改：

- `scripts/super_board_run.py`
- `templates/board-memo.md`
- `web/server.py`

建议书必须展示：

- 本次参与席位。
- 每个席位的中文名。
- 每个席位的代表观点。
- 观点来源于哪个规则或心智模型。
- 支持证据。
- 证据缺口。
- 反证实验。
- 本体边界提示。

禁止输出：

- 「某某本人认为」。
- 未触发人物。
- 英文展示名。
- 没有证据绑定的人物观点。
- 把哲学人物直接套成商业结论。

#### 阶段 6：视觉报告升级

修改：

- `scripts/visual_report_builder.py`
- `schemas/visual_report.schema.json`
- `web/src/App.tsx`

视觉报告新增：

- 人物观点卡。
- 图谱命中卡。
- 模型比较卡。
- 动作审计卡。
- 本体边界卡。

卡片不新增事实，只复用建议书和 record 中已有的结构化字段。

#### 阶段 7：测试与 Harness

新增测试：

- `tests/test_persona_graph_schema.py`
- `tests/test_persona_graph_loader.py`
- `tests/test_ontology_matcher_graph.py`
- `tests/test_persona_graph_governance.py`
- `tests/test_persona_actions.py`
- `tests/test_persona_action_audit.py`
- `tests/test_compile_persona_prompt.py`

新增 golden cases：

- `tests/golden/product_decision.persona_graph.json`
- `tests/golden/business_strategy.persona_graph.json`
- `tests/golden/misuse_guardrail.persona_graph.json`
- `tests/golden/philosophy_boundary.persona_graph.json`

新增 Harness task：

- `.harness/tasks/persona_graph_validation.yaml`
- `.harness/tasks/persona_graph_quality.yaml`

验证命令：

```bash
python3 scripts/validate_skill.py
python3 scripts/validate_ontology.py
python3 scripts/validate_persona_graph.py
python3 scripts/evaluate_ontology_quality.py
python3 scripts/evaluate_persona_graph.py
uv run python .harness/harness_check.py
uv run python .harness/harness_eval.py
cd web && npm run build
```

## Q29：针对这份计划和参考文件，结合市面上的成功经验，接下来的实施计划还有没有需要补充的想法或建议？

有，需要补充 8 个方向。

### 1. 来源优先，而不是人物优先

NotebookLM、Perplexity 这类产品给人的启发是：用户信任不是来自「AI 很会说」，而是来自「我能看到依据」。

所以 Super Board 不能只展示名人观点。

应该优先展示：

- 这个观点来自哪类公开材料。
- 证据强度如何。
- 哪些内容只是推断。
- 哪些是假设。
- 哪些需要验证。

人物本体只是透镜，证据链才是信任基础。

### 2. 增加身份治理层

Delphi 这类数字分身产品的方向是把人做成可对话的 digital twin。

但 Super Board 不应该走这个方向。

原因：

- 我们没有人物授权。
- 我们不是在复制一个人。
- 我们做的是公开材料抽象出的决策框架。

所以必须有 `ontology_contract`：

- 不声称代表人物本人。
- 不生成直接引语。
- 不使用未授权口吻。
- 只输出「某某视角下」。
- 所有观点必须是抽象判断，不是人格扮演。

### 3. 增加 Action 层

Palantir AIP 的经验是：本体不是信息展示，而是驱动动作。

Super Board 里的人物本体也应该能触发动作。

例如：

- 张小龙视角触发「删减功能」动作。
- 巴菲特视角触发「现金流与护城河证据」动作。
- 孙子视角触发「先胜后战条件检查」动作。
- 老子视角触发「降低干预强度」动作。
- 毛泽东视角触发「主要矛盾与群众路线验证」动作。

这些动作要进入建议书，而不是只停留在人物卡片里。

### 4. 增加董事会周期

Board Intelligence 这类董事会产品的启发是：董事会不是一次性报告，而是一整套 board cycle。

Super Board 也应该从「生成建议书」进化为：

- 会前材料。
- 审议建议书。
- 决策记录。
- 30 / 60 / 90 天复盘。
- 假设校准。
- 下次审议继承。

这会让本体人物有机会被校准，而不是每次重新开始。

### 5. 人物质量等级

每个人物应该有 `quality_level`。

不是所有人物都同等适合所有问题。

建议分为：

- `core`：资料厚、框架稳定、案例丰富。
- `limited`：适合特定主题，但不能泛化。
- `contextual`：只在特定议题触发。
- `experimental`：需要更多验证。

建议书默认只展示已触发且质量等级足够的人。

### 6. 反共识保护

Peter Thiel 这类人物不应被排除，而应被严格约束。

正确处理方式不是「不用」，而是：

- 只在非共识机会、平台垄断、秘密发现、品类重构等问题触发。
- 必须绑定客户证据、市场证据或结构性优势证据。
- 必须有可执行反证实验。
- 不允许输出不可证伪的聪明判断。

也就是说，保留反共识能力，但不给它无限权力。

### 7. 建议书可解释层

用户不只想看结论，还想知道：

- 哪些人参与了讨论。
- 他们为什么被触发。
- 他们基于什么证据说话。
- 他们之间哪里冲突。
- 最终建议为什么选择这一边。

所以建议书里应该有：

- 本次参与席位。
- 人物观点。
- 关键分歧。
- 分歧解决原则。
- 证据缺口。
- 反证路径。

### 8. 专门评测集

不要只测 schema。

还要有业务评测：

- 产品决策。
- 商业策略。
- 组织与执行。
- 哲学边界。
- 误用防护。

每个评测都要看：

- 是否触发正确人物。
- 是否没有触发不相关人物。
- 是否输出中文名。
- 是否引用证据。
- 是否给出反证实验。
- 是否避免伪装本人。

## Q30：结合这些建议，重新整理后的详细落地实施计划是什么？

重新整理后的计划是：

> Super Board 人物本体 v3：人物认知图谱 + 来源证据 + 动作治理 + 反证校准 + 决策复盘。

### 阶段 0：计划边界

明确：

- 本轮不是补字段，而是重构人物本体层。
- 本轮不是新增名人，而是把现有人物全部升级为本体图谱。
- 本轮不是数字人产品，而是决策审议系统。
- 本轮不新增外部模型调用。
- 本轮不上传敏感材料。

产物：

- `PLANS.md`
- `.harness/current_sprint.md`
- `logs/execution_stream.log`

### 阶段 1：schema 层

新增：

- `persona_graph.schema.json`
- `persona_source.schema.json`
- `persona_eval_case.schema.json`
- `persona_relation.schema.json`

目标：

- 先定义契约，再填数据。
- 所有后续脚本、Web、建议书都不能各自发明格式。

### 阶段 2：全量人物图谱

为全部人物生成 `ontology/persona_graphs/*.json`。

每个人至少具备：

- 身份边界。
- 来源摘要。
- 核心主张。
- 心智模型。
- 启发式。
- 历史案例。
- 行动建议。
- 反证实验。
- 误用防护。
- 评估用例。

### 阶段 3：治理层

加入：

- `ontology_contract`
- `quality_level`
- `source_strength`
- `misuse_guardrails`
- `action_audit`
- `version_log`

目的：

- 防止名人效应变成伪权威。
- 防止哲学人物被乱用。
- 防止反共识人物输出不可证伪判断。

### 阶段 4：匹配层

重构：

- `scripts/ontology_matcher.py`

输出从旧的 rule hits 升级成 graph hits：

- 人物命中。
- 主张命中。
- 心智模型命中。
- 边界命中。
- 反证命中。
- 动作命中。
- 人物关系和分歧命中。

### 阶段 5：建议书层

建议书必须能回答：

- 谁参与了讨论。
- 为什么是这些人。
- 每个人说了什么。
- 哪些观点互相冲突。
- 哪些证据支持。
- 哪些证据不足。
- 如何反证。
- 最终建议如何权衡。

### 阶段 6：视觉报告层

视觉报告不重新生成事实，只把同一份 record 变成卡片：

- 决策摘要卡。
- 委员会卡。
- 人物观点卡。
- 本体规则卡。
- 证据卡。
- 假设卡。
- 行动审计卡。
- 30 / 60 / 90 天时间线。

### 阶段 7：Web API

接口要返回：

- `persona_graph_refs`
- `selected_seats`
- `seat_viewpoints`
- `graph_rule_hits`
- `action_triggers`
- `visual_report`

前端只展示本次触发内容，不展示未启用席位。

### 阶段 8：测试

测试不仅验证能不能跑，还要验证质量：

- 人物图谱 schema 合法。
- 中文展示名完整。
- 英文名不进入用户可见报告。
- 所有人物都有来源、边界、反证。
- 人物观点必须绑定证据。
- 视觉报告不新增事实。
- 误用场景能被挡住。

### 阶段 9：Golden Cases

用固定材料测试：

- 产品决策。
- 商业策略。
- 误用防护。
- 哲学边界。

每个 case 都要求：

- 触发正确人物。
- 不触发无关人物。
- 输出结构完整。
- 证据与反证完整。

### 阶段 10：全量验收

验收命令：

```bash
python3 scripts/validate_skill.py
python3 scripts/validate_ontology.py
python3 scripts/validate_persona_graph.py
python3 scripts/evaluate_ontology_quality.py
python3 scripts/evaluate_persona_graph.py
python3 -m unittest tests/test_validate_skill.py tests/test_validate_ontology.py tests/test_persona_display_names.py tests/test_seat_view_selector.py tests/test_visual_report_builder.py
python3 -m unittest tests/test_persona_graph_schema.py tests/test_persona_graph_loader.py tests/test_ontology_matcher_graph.py tests/test_persona_graph_governance.py tests/test_persona_actions.py tests/test_persona_action_audit.py tests/test_compile_persona_prompt.py
uv run python .harness/harness_check.py
uv run python .harness/harness_eval.py
cd web && npm run build
```

## Q31：基于这个计划，如何开发落地？每一步干什么，如何达到最终目标？不要遗忘 Harness 和 Superpowers。

开发顺序应该是从底层契约往上做。

### 第 1 步：冻结现状

先看：

- `PLANS.md`
- `ARCHITECTURE.md`
- `README.md`
- `docs/harness-summary.md`
- `docs/harness-superpowers.md`
- 现有 ontology 文件。
- 现有建议书生成链路。
- 现有 Web API。

目的：

- 不凭印象改。
- 不破坏当前能生成建议书的链路。
- 明确哪些文件是旧本体、哪些文件是新图谱。

### 第 2 步：写计划

更新：

- `PLANS.md`
- `.harness/current_sprint.md`

使用 Superpowers：

- `writing-plans`

目的：

- 把目标、非目标、验证命令写清楚。
- 防止实施中途发散。

### 第 3 步：先写 schema 和失败测试

新增 schema 后，先写测试：

- schema 必填字段缺失会失败。
- 来源为空会失败。
- 没有误用边界会失败。
- 没有 eval case 会失败。
- 用户可见展示名不是中文会失败。

使用 Superpowers：

- `test-driven-development`

目的：

- 先让质量门槛变成程序约束。
- 再填数据。

### 第 4 步：生成全量人物图谱

为全部人物补齐：

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
- `eval_cases`

这里不是写漂亮介绍，而是写可运行字段。

### 第 5 步：loader 与 validator

新增：

- `persona_graph_loader.py`
- `validate_persona_graph.py`
- `evaluate_persona_graph.py`

目的：

- 所有后续逻辑只通过 loader 读取人物图谱。
- validator 负责结构正确。
- evaluator 负责质量最低门槛。

### 第 6 步：接入 matcher

修改：

- `ontology_matcher.py`

做到：

- 材料能触发人物图谱。
- 输出人物命中理由。
- 输出 claim/model/boundary/action。
- 输出人物之间的分歧关系。
- 输出不能直接下结论的证据缺口。

### 第 7 步：接入 CLI / record

修改：

- `super_board_run.py`
- `schemas/decision_record.schema.json`

record 中新增：

- `persona_graph_refs`
- `persona_claim_hits`
- `persona_action_triggers`
- `persona_model_comparisons`
- `persona_action_audit`

目的：

- Web、视觉报告、复盘都从 record 读取。
- 不让前端重新推断。

### 第 8 步：接入建议书

建议书新增或增强：

- 本次参与席位。
- 人物代表观点。
- 本体规则命中。
- 证据缺口。
- 人物分歧。
- 分歧解决原则。
- 反证实验。
- 动作建议。

质量要求：

- 只展示本次启用人物。
- 只展示中文名。
- 不把人物写成实时发言。
- 不新增没有来源的名人观点。

### 第 9 步：接入视觉报告

视觉报告显示：

- 人物观点卡。
- 本体规则卡。
- 模型比较卡。
- 动作审计卡。
- 证据卡。
- 假设卡。

目的：

- 管理层扫读。
- 一眼看到谁参与、观点是什么、证据在哪里、下一步做什么。

### 第 10 步：Web 接入

修改：

- `web/server.py`
- `web/src/App.tsx`

Web 要做到：

- 生成建议书时带出人物图谱命中。
- 视觉版展示人物卡。
- 正文版展示完整内容。
- 未配置模型时给清晰状态。
- 生成中有明确状态。

### 第 11 步：Harness 验证

新增或扩展 Harness task：

- 人物图谱合法性。
- 人物图谱质量。
- 建议书完整性。
- Web 视觉报告完整性。

执行：

```bash
uv run python .harness/harness_check.py
uv run python .harness/harness_eval.py
```

### 第 12 步：完成前验证

使用 Superpowers：

- `verification-before-completion`

必须重新跑：

- validator。
- Python 单测。
- Harness。
- Web build。
- 浏览器 smoke。

没有跑过的不能说完成。

## Q32：特别是人物本体论这块，基于参考文件，优化部分还有遗漏吗？

有几个遗漏需要补上。

已经覆盖的部分包括：

- 人物从 YAML 规则升级为 `persona_graph`。
- 观点绑定 `claim_id`、`model_id`、`source_id`、`boundary_id`、`counter_test_id`。
- 增加身份边界，避免声称数字本人。
- 增加动作层。
- 增加 eval 与版本。
- 建议书只展示本次参与人物。
- 用户可见只展示中文名。
- Harness 与 TDD。

但参考 Palantir 式本体数字分身文档后，还应该补这些：

### 1. Decision / Episode 层

人物本体不能只有抽象观点，还应该有历史情境。

需要补：

- `historical_decisions`
- `episodes`

目的：

- 让观点有具体场景。
- 防止把抽象原则无限泛化。

### 2. Expression Pattern

可以记录表达模式，但只能受限使用。

原因：

- 表达模式有助于把观点写得更有辨识度。
- 但不能变成模仿本人。

所以要加约束：

- 不生成直接引语。
- 不声称本人说过。
- 只作为结构化表达的参考。

### 3. Relation 图谱层

人物之间不是孤立的。

要写出：

- 谁与谁互补。
- 谁与谁冲突。
- 谁适合反证谁。
- 谁适合做长期视角。
- 谁适合做执行视角。

这样建议书才能写出「分歧解决」，而不是把观点平铺。

### 4. Ontology Contract 独立层

需要把人物使用边界独立成契约。

例如：

- 不是本人。
- 不是授权代理。
- 不输出私人信息。
- 不输出直接引语。
- 不在证据不足时输出强判断。

### 5. 增量更新状态

人物本体应该有：

- `ontology_updates`
- `version_log`
- `last_reviewed_at`
- `quality_notes`

这方便后续持续进化。

### 6. Skill Compiler 对应物

需要一个把人物图谱编译成 prompt 片段的脚本。

新增：

- `scripts/compile_persona_prompt.py`

目的：

- 避免每个调用链自己拼 prompt。
- 统一人物观点、边界、动作、反证格式。

### 7. 动作审计

如果人物本体触发了动作，必须能审计：

- 触发原因。
- 输入证据。
- 输出动作。
- 风险等级。
- 是否进入建议书。

新增：

- `scripts/persona_action_audit.py`

### 8. 人物之间模型比较

建议书不应只显示「A 认为、B 认为」。

还要显示：

- 哪些模型支持 Go。
- 哪些模型要求 Pivot。
- 哪些模型要求 No-Go。
- 分歧点是什么。
- 需要什么证据裁决。

### 9. 未来数字分身边界

参考文档讨论的是数字分身，但 Super Board 当前不做这个。

可以保留未来边界：

- 如果未来要做某个真实人物的授权数字分身，必须另走授权、来源、人格边界、审计、撤回机制。
- 不能混进当前 Super Board。

## Q33：补充遗漏后，重新生成的详细步骤落地实施计划是什么？

最终计划按 14 个阶段执行。

### 阶段 0：计划与基线

- 读取 `README.md`、`ARCHITECTURE.md`、`PLANS.md`、Harness 文档。
- 更新 `PLANS.md`。
- 更新 `.harness/current_sprint.md`。
- 记录执行开始。

目标：

- 明确「全量人物图谱重构」。
- 保护原有建议书生成链路。
- 保证每一步可验证。

### 阶段 1：schema 契约

新增：

- `persona_graph.schema.json`
- `persona_source.schema.json`
- `persona_eval_case.schema.json`
- `persona_relation.schema.json`

覆盖：

- 人物。
- 来源。
- 主张。
- 心智模型。
- 历史决策。
- 情境片段。
- 表达模式。
- 边界。
- 动作。
- 关系。
- 评估用例。

### 阶段 2：加载器与校验器

新增：

- `persona_graph_loader.py`
- `validate_persona_graph.py`
- `evaluate_persona_graph.py`

目标：

- 结构合法。
- 质量达标。
- 业务字段完整。

### 阶段 3：全量人物图谱

生成所有人物的图谱文件。

每个人都要有：

- 中文名。
- 内部英文名。
- 常驻或触发类型。
- 委员会归属。
- 来源摘要。
- 核心主张。
- 心智模型。
- 启发式。
- 历史案例。
- 边界。
- 反证。
- 动作。
- 关系。
- eval case。

### 阶段 4：动作层与审计

新增：

- `persona_actions.py`
- `persona_action_audit.py`

动作包括：

- 补证据。
- 降级建议。
- 要求反证。
- 进入观察。
- 转成检查点。
- 提醒误用风险。

### 阶段 5：匹配器升级

修改：

- `ontology_matcher.py`

输出：

- `persona_graph_refs`
- `claim_hits`
- `mental_model_hits`
- `boundary_hits`
- `counter_test_hits`
- `action_triggers`
- `model_comparisons`
- `selection_trace`

### 阶段 6：Prompt Compiler

新增：

- `compile_persona_prompt.py`

功能：

- 把人物图谱编译成模型可用的 prompt 片段。
- 统一格式。
- 强制中文展示名。
- 强制身份边界。
- 强制证据与反证。

### 阶段 7：record 与 CLI

修改：

- `schemas/decision_record.schema.json`
- `scripts/super_board_run.py`

record 需要保存：

- 参与人物。
- 图谱引用。
- 规则命中。
- 动作命中。
- 人物分歧。
- 证据缺口。
- 反证实验。

### 阶段 8：建议书模板

修改：

- `templates/board-memo.md`

新增或强化：

- 本次审议席位。
- 席位代表观点。
- 人物本体规则命中。
- 跨委员会分歧。
- 分歧解决原则。
- 反证路径。
- 本体边界提示。

### 阶段 9：视觉报告

修改：

- `scripts/visual_report_builder.py`
- `schemas/visual_report.schema.json`
- `web/src/App.tsx`

新增：

- 人物观点卡。
- 图谱规则卡。
- 模型比较卡。
- 动作审计卡。

### 阶段 10：Web API

修改：

- `web/server.py`

接口输出：

- 正文建议书。
- 视觉报告。
- 人物图谱命中。
- 动作审计。
- 本体规则卡。

### 阶段 11：Golden Cases

新增：

- 产品决策 case。
- 商业策略 case。
- 误用防护 case。
- 哲学边界 case。

目标：

- 验证触发是否合理。
- 验证哲学人物是否被商业化转译。
- 验证反共识人物是否被证据门槛约束。

### 阶段 12：Harness

新增：

- `persona_graph_validation.yaml`
- `persona_graph_quality.yaml`

运行：

```bash
uv run python .harness/harness_check.py
uv run python .harness/harness_eval.py
```

### 阶段 13：浏览器 smoke

验证：

- 上传材料。
- 生成建议书。
- 正文版完整。
- 视觉版完整。
- 人物观点出现。
- 不展示未启用人物。
- 不展示英文名。
- 导出可用。

### 阶段 14：提交策略

建议拆分：

1. schema 与 graph loader。
2. 全量人物图谱。
3. matcher / CLI / record。
4. 建议书与视觉报告。
5. Web 与 Harness。

每个 commit 前都跑对应测试。

## Q34：批准，开始执行后，实际完成了哪些改动？

已按上述计划执行落地。

### 已新增的人物图谱

新增：

- `ontology/persona_graphs/*.json`

覆盖 37 个人物图谱。

每个人物图谱包含：

- 中文展示名。
- 内部英文名。
- 委员会归属。
- 常驻或触发专家属性。
- 来源摘要。
- 核心主张。
- 心智模型。
- 历史案例。
- 情境片段。
- 表达模式约束。
- 误用边界。
- 反证实验。
- 行动触发。
- 人物关系。
- 评估用例。
- 版本记录。

### 已新增 schema

新增：

- `ontology/schemas/persona_graph.schema.json`
- `ontology/schemas/persona_source.schema.json`
- `ontology/schemas/persona_eval_case.schema.json`
- `ontology/schemas/persona_relation.schema.json`

扩展：

- `schemas/decision_record.schema.json`
- `schemas/visual_report.schema.json`

### 已新增脚本

新增：

- `scripts/persona_graph_loader.py`
- `scripts/validate_persona_graph.py`
- `scripts/evaluate_persona_graph.py`
- `scripts/generate_persona_graphs.py`
- `scripts/persona_actions.py`
- `scripts/persona_action_audit.py`
- `scripts/compile_persona_prompt.py`
- `scripts/suggest_ontology_updates.py`

### 已修改生成链路

修改：

- `scripts/ontology_matcher.py`
- `scripts/super_board_run.py`
- `scripts/visual_report_builder.py`
- `scripts/validate_skill.py`
- `web/server.py`
- `web/src/App.tsx`

接入内容包括：

- `persona_graph_refs`
- 人物图谱命中。
- 动作触发。
- 行动审计。
- 模型比较。
- 视觉报告人物卡片。
- record 结构扩展。

### 已新增测试

新增：

- `tests/test_persona_graph_schema.py`
- `tests/test_persona_graph_loader.py`
- `tests/test_ontology_matcher_graph.py`
- `tests/test_persona_graph_governance.py`
- `tests/test_persona_actions.py`
- `tests/test_persona_action_audit.py`
- `tests/test_compile_persona_prompt.py`

新增 golden：

- `tests/golden/product_decision.persona_graph.json`
- `tests/golden/business_strategy.persona_graph.json`
- `tests/golden/misuse_guardrail.persona_graph.json`
- `tests/golden/philosophy_boundary.persona_graph.json`

扩展：

- `tests/test_visual_report_builder.py`

### 已新增 Harness 任务

新增：

- `.harness/tasks/persona_graph_validation.yaml`
- `.harness/tasks/persona_graph_quality.yaml`

### 已完成验证

已通过：

```bash
python3 scripts/validate_skill.py
python3 scripts/validate_ontology.py
python3 scripts/validate_persona_graph.py
python3 scripts/evaluate_ontology_quality.py
python3 scripts/evaluate_persona_graph.py
python3 -m unittest tests/test_validate_skill.py tests/test_validate_ontology.py tests/test_persona_display_names.py tests/test_seat_view_selector.py tests/test_visual_report_builder.py
python3 -m unittest tests/test_persona_graph_schema.py tests/test_persona_graph_loader.py tests/test_ontology_matcher_graph.py tests/test_persona_graph_governance.py tests/test_persona_actions.py tests/test_persona_action_audit.py tests/test_compile_persona_prompt.py
uv run python .harness/harness_check.py
uv run python .harness/harness_eval.py
cd web && npm run build
```

浏览器 smoke 也完成过验证：

- `/api/preview` 返回 `ok: true`。
- `visual_report` 存在。
- `selectedSeats` 为 10。
- `personaGraphRefs` 为 25。
- `visualGraphCards` 为 8。
- `modelComparisonCards` 为 8。
- `actionAuditCards` 为 8。
- `markdownHasGraph` 为 true。

### 当前仍需注意的边界

- 这仍然不是「数字本人」。
- 人物观点只能写成「某某视角下」。
- 不展示未启用人物。
- 用户可见名称必须是中文名。
- 视觉报告只做结构提炼，不新增事实。
- 真实 records 仍不应提交。
