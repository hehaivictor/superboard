# 上游 License 审计

审计日期：2026-05-12

## 结论

`awesome-persona-skills` 是目录索引，不能用根仓库授权覆盖所有子仓库。已逐一检查本轮直接使用的上游仓库，直接命中的 8 个人物 skill、`nuwa-skill` 和 `curator-skill` 均带 `MIT License`。

## 直接命中人物

| Persona | 上游仓库 | License | 使用方式 |
|---|---|---:|---|
| Warren Buffett | `will2025btc/buffett-perspective` | MIT | 适配为董事会审议字段，保留来源 |
| Steve Jobs | `alchaincyf/steve-jobs-skill` | MIT | 适配为董事会审议字段，保留来源 |
| Elon Musk | `alchaincyf/elon-musk-skill` | MIT | 适配为董事会审议字段，保留来源 |
| Charlie Munger | `alchaincyf/munger-skill` | MIT | 适配为董事会审议字段，保留来源 |
| Richard Feynman | `alchaincyf/feynman-skill` | MIT | 适配为董事会审议字段，保留来源 |
| Naval Ravikant | `alchaincyf/naval-skill` | MIT | 适配为董事会审议字段，保留来源 |
| Nassim Taleb | `alchaincyf/taleb-skill` | MIT | 适配为董事会审议字段，保留来源 |
| 张一鸣 | `alchaincyf/zhang-yiming-skill` | MIT | 适配为董事会审议字段，保留来源 |

## 方法来源

| 仓库 | License | 作用 |
|---|---:|---|
| `alchaincyf/nuwa-skill` | MIT | 使用其“多源信息采集、三重验证、框架提炼、诚实边界”的方法论 |
| `Aar0nPB/curator-skill` | MIT | 使用其“persona router / adapter / 不抢位”的调度思想 |

## Nuwa 全流程补蒸馏人物

以下人物没有在 `awesome-persona-skills` 索引中直接命中单人物 skill。本项目按 `nuwa-skill` 的多源采集、心智模型三重验证、案例提炼、诚实边界方法，使用具体公开来源重新蒸馏。每个人先生成完整本地产物 `nuwa_distillations/<persona-id>/`，再压缩适配为 `personas/<persona-id>.md` 的董事会档案：

| Persona | 主要具体来源 |
|---|---|
| Jeff Bezos | Amazon 1997 shareholder letter、Amazon shareholder letters、Working Backwards、AWS/Prime/Marketplace 公开案例 |
| Lou Gerstner | Who Says Elephants Can't Dance?、Forbes IBM turnaround article、IBM 转型公开资料 |
| Paul Graham | Do Things that Don't Scale、How to Get Startup Ideas、How to Start a Startup、Be Good |
| Sam Altman | Startup Advice、Hard Startups、Startup Advice Briefly、YC 公开创业课程材料 |
| Reid Hoffman | Blitzscaling、The Alliance、LinkedIn/PayPal 公开案例 |
| Marc Andreessen | Why Software Is Eating the World、a16z 公开文章、技术产业访谈 |
| Peter Thiel | Zero to One、Stanford CS183 notes、PayPal/Palantir 公开案例 |
| George Soros | The Alchemy of Finance、reflexivity academic discussions、SSRN reflexivity paper |
| Ray Dalio | Principles、How the Economic Machine Works、Principles for Navigating Big Debt Crises |
| Michael Porter | HBS Five Forces materials、Competitive Strategy、Competitive Advantage |
| Clayton Christensen | Christensen Institute disruptive innovation theory、HBS disruptive innovation / JTBD materials、The Innovator's Dilemma |
| Marvin Bower | McKinsey mission and values、McKinsey's Marvin Bower、McKinsey code and values materials |
| Bruce Henderson | BCG The Experience Curve、BCG Rule of Three and Four、Growth-share matrix history |
| Orit Gadiesh | Bain profile、HBR Transforming Corner-Office Strategy into Frontline Action、Bain Strategic Leader / strategy articles |
| Don Norman | The Design of Everyday Things、IxDF affordances topic、NN/g and design psychology materials |
| Marty Cagan | SVPG Four Big Risks、Inspired、Empowered、SVPG product discovery materials |
| Julie Zhuo | The Making of a Manager official page、book materials、public product/design leadership writings |

## 约束

- 本项目不直接复制外部 skill 正文作为主资产。
- 直接命中人物使用 `adapted-with-attribution`：吸收结构、模型名称和适配思路，落到 Super Board 的审议字段。
- 未直接命中的 17 人使用 `nuwa-method-full artifact -> super-board compressed dossier`：先保留完整女娲产物，再压缩进董事会字段。
- 如未来直接 vendoring 外部仓库全文，必须同时保留原 LICENSE 和来源说明。
