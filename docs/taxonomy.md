# Skill 分类与命名

`coder` 是插件名，`master` 是已实现的总入口。专业 Skill 按用户要完成的目标划分；语言、框架、工具和职位作为任务上下文。[覆盖设计](coverage-plan.md)列出 43 项工程任务的英文工作名，其中 2 项已实现、8 项为优先候选、33 项为覆盖项；它们不是 43 个待创建的 Skill。

## 命名规则

- 英文工作名用于覆盖追踪和讨论；只有证明任务具备独立的触发条件、工作方法和验收结果，才把工作名确定为正式 Skill 名。
- 专业 Skill 使用小写英文、数字和连字符，动词在前、对象在后；优先使用两个常见词，例如 `design-apis`。不重复插件名 `coder`。
- 名称只说主要目标。范围、技术栈和近义触发词写进 `description`，不堆进名称；例如 `design-algorithms` 的描述应明确包含数据结构选择。
- 同一对象若有不同动作，名称与说明要能区分产物；例如 `design-security` 与 `audit-security` 的产物不同。
- 完整身份 `coder:<skill-name>` 不超过 64 个字符。目录与 frontmatter 的 `name` 一致：`skills/<skill-name>/SKILL.md`。

## 已实现与优先评审的名称

`design-apis` 和 `fix-bugs` 已创建 Skill 文件。`fix-bugs` 已完成[限定范围的独立评测](../skills/fix-bugs/tests/evaluations/fix-bugs-2026-09-30.md)，`design-apis` 仍待完整真实任务验证。其余名称便于优先评审，并不代表专业 Skill 已实现或边界已经通过真实任务验证。另有 33 项英文工作名仅承担覆盖追踪，不计划立即创建 Skill。

| 名称 | 状态 | 用户目标与主要产物 |
| --- | --- | --- |
| `define-requirements` | 优先候选 | 明确需求、范围与验收条件。 |
| `model-domain` | 优先候选 | 梳理业务概念、规则与不变量。 |
| `design-architecture` | 优先候选 | 设计系统或模块职责与依赖。 |
| `design-apis` | 已实现 | 设计调用方可见的接口契约。 |
| `design-storage` | 优先候选 | 设计持久化结构、约束与查询。 |
| `design-algorithms` | 优先候选 | 选择数据结构与算法，核验资源约束。 |
| `design-ui` | 优先候选 | 设计用户流程、交互与界面状态。 |
| `design-security` | 优先候选 | 设计信任边界与安全控制。 |
| `fix-bugs` | 已实现 | 复现并修复缺陷，验证回归。 |
| `review-changes` | 优先候选 | 针对固定差异审查实现与需求。 |

新增实体 Skill 时，先用自然表达、直接点名、信息不足和不应触发的请求测试路由，再确定 `name` 与 `description`。没有独立工作方法的任务交给 `master` 的常规能力，或作为已实现 Skill 的按需参考。
