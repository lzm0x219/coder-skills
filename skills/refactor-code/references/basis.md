# 来源与规则映射

本文件维护来源与映射；执行规则以指向的入口和参考章节为准。

核验日期：2026-10-01。RF 编号是本项目的追踪编号，不是行业标准条款号。

## 依据层级

- 原文支持：公开原文明确表达对应原则；项目中的执行动作仍按实际环境选取。
- 方法推导：由已核验原则推导具体检查或门槛，原文没有规定同一实现。
- 项目机制：本 Skill 的授权、状态或证据管理设计，不冒充外部标准要求。
- 标准背景：只核验官方版本与摘要，用于组织过程或质量目标；尚无规范性条款映射。

方法依据、规则实施、行为评测及正式标准符合性是不同结论。本映射不构成 ISO 合规声明；拟作正式符合性评估时，需取得适用版本的规范性全文，确认适用条款、裁剪与组织要求，再逐条收集证据。沿用任务授权，不因参考标准自行扩大修改、访问或审批范围。

## 来源登记

| ID | 一手来源与版本 | 已核验的位置 | 支持边界 |
| --- | --- | --- | --- |
| F01 | [Fowler：Refactoring](https://refactoring.com/) | Definition；页首的小步变换与 frequent testing 说明 | 行为保持、结构改善及小步检查方法；不是正式标准 |
| F02 | [Fowler：Refactoring Boundary](https://martinfowler.com/bliki/RefactoringBoundary.html) | 可观察行为与改善目的的讨论 | 行为边界需解释；不推导成所有内部函数签名一律固定 |
| F03 | [Extract Function](https://refactoring.com/catalog/extractFunction.html)、[Move Function](https://refactoring.com/catalog/moveFunction.html) | 作者公开目录的摘要和示例 | 确认操作名称及示意；本次未取得书中完整 Mechanics，不能把本项目步骤称为其逐条原流程 |
| F04 | [Fowler：Preparatory Refactoring](https://martinfowler.com/articles/preparatory-refactoring-example.html) | Final Thoughts 与前文示例 | 先改善结构使后续功能变化容易；不代替新行为验收 |
| W01 | [IEEE SWEBOK Guide V4.0a](https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf) | 下表列出的章节，公开全文 | 工程知识指南；其中引用某个 ISO/IEEE 标准不等于本项目已读取该标准全文 |
| I01 | [ISO/IEC/IEEE 12207:2026](https://www.iso.org/standard/90219.html) | 官方 Abstract，2026-04 发布 | 生命周期框架；摘要明确不指定唯一开发模型或方法 |
| I02 | [ISO/IEC/IEEE 14764:2022](https://www.iso.org/standard/80710.html) | 官方 Abstract，2022-01 发布 | 维护过程指导；摘要引用 12207:2017，本次未核实与 12207:2026 的条款对应 |
| I03 | [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) | 官方 Abstract，2023-11 发布 | 产品质量模型、质量目标和验收框架；未核验细分质量定义或规范性条款 |

## W01 精确定位

纸面页是章节页码；PDF 页为从 1 开始的文件页码，便于打开核验。

| 定位 | 已核验主题 | 纸面页 | PDF 页 |
| --- | --- | --- | --- |
| 第3章 §1.4 | 模块化、信息隐藏、接口与实现分离、耦合与内聚 | 3-3 至 3-4 | 85–86 |
| 第5章 §2.2.5 | 选择性回归及成本与覆盖权衡 | 5-8 | 124 |
| 第7章 §2.1.3 | 维护变更的影响分析 | 7-6 | 172 |
| 第7章 §4.2 | 重构在维护中的定位、结构及行为边界 | 7-13 至 7-14 | 179–180 |
| 第8章 §2.1–2.4 | 配置项、标识、正式配置基线及其属性 | 8-6 至 8-7 | 190–191 |
| 第8章 §2.6 | 测试材料、源码基线与构建制品的关联 | 8-8 | 192 |

W01 的正式配置基线涉及批准与变更控制；本 Skill 的运行前工作区/行为基线是验证对照。二者不能混称，也不因此给普通重构新增配置管理审批。

## 执行映射

证据类型记录现有评测达到的层级；案例标准见 [rubric](../tests/rubric.md)，运行材料与结论见 [初版评测](../tests/evaluations/refactor-code-2026-10-01.md)和[状态修订评测](../tests/evaluations/state-machine-rules-2026-10-01.md)。

| ID | 权威规则位置 | 来源与定位 | 依据层级 | 状态门槛 | 案例 ID | 已有证据类型 |
| --- | --- | --- | --- | --- | --- | --- |
| RF01 | [重构行为边界](../SKILL.md#重构代码) | F01 Definition；W01 第7章 §4.2 | 原文支持 | S0/S1/S4 | library, async, duplicate | 受控运行 |
| RF02 | [公开契约与消费者观察](compatibility.md#观察细则) | F02；W01 第3章 §1.4 | 方法推导 | S1/S4 | library | 受控运行 |
| RF03 | [职责和结构收益](structure.md#从维护摩擦推导职责)及[结构证据](structure.md#结构证据) | F01 改善目的；W01 第3章 §1.4 | 方法推导 | S0/S2/S4 | library, duplicate | 受控运行与结构走查 |
| RF04 | [移动与共享规则](structure.md#目录重设计)及[去重复](structure.md#去重复与抽象) | F03 摘要；W01 第3章 §1.4 | 方法推导 | S2/S3 | library, duplicate | 受控运行与结构走查 |
| RF05 | [小步实施与检查](../SKILL.md#s3-分步实施) | F01 小步变换和 frequent testing | 原文支持 | S3 | changed-baseline | 分阶段运行 |
| RF06 | [影响范围和回归选择](verification.md#验证顺序) | W01 第7章 §2.1.3；第5章 §2.2.5 | 方法推导 | S1/S3/S4 | library, async, missing-artifact | 受控运行与状态走查 |
| RF07 | [基线和证据身份](compatibility.md#兼容账) | W01 第8章 §2.1–2.4、§2.6 | 方法推导 | S0/S1/S4 | changed-baseline, dirty | 分阶段运行与受控运行 |
| RF08 | [证据失效返回](recovery.md#工作区变化与证据失效) | W01 的配置与测试关联是背景；具体返回状态为项目设计 | 项目机制 | S0/S1/S2/S3 | changed-baseline, stale-evidence | 分阶段运行与状态走查 |
| RF09 | [失败分类与隔离边界](recovery.md#检查失败)及[范围收缩](recovery.md#环境缺失与范围收缩) | 项目证据管理设计；W01 影响分析为背景 | 项目机制 | S1/S3/S5 | baseline, unavailable, incomparable, coupling-gap | 受控运行与状态走查 |
| RF10 | [检查预期与行为变化](recovery.md#保护检查的观察)及[混合任务验收](../SKILL.md#s2-选定结构方案) | F01 行为保持；F04 Final Thoughts；具体失败保护为项目设计 | 方法推导 | S1/S2/S4 | bad-check, changed-baseline | 带提示运行与分阶段运行 |
| RF11 | [交付结论](verification.md#完成判断) | I03 官方摘要仅为质量目标背景；具体结论为项目设计 | 项目机制 | S4/S5 | library, unavailable, readonly | 受控运行与结构走查 |
| RF12 | [中断恢复](recovery.md#中断恢复) | 项目状态设计；W01 配置身份为背景 | 项目机制 | S0/S1/S2/S3 | changed-baseline, resume | 分阶段运行与状态走查 |
| RF13 | [用户编辑及授权变化](recovery.md#工作区变化与证据失效) | 当前任务与项目权限约束；不归因于 ISO | 项目机制 | S0/S3/S5 | dirty, readonly, revoked | 受控运行与状态走查 |
| RF14 | [运行制品与消费者](compatibility.md#观察细则)及[验证顺序](verification.md#验证顺序) | W01 第8章 §2.6；平台相关细则为方法推导 | 方法推导 | S3/S4 | library, missing-artifact | 受控运行与状态走查 |
| RF15 | [正式标准声明边界](basis.md#依据层级) | I01 Abstract；I02 Abstract | 标准背景 | S0/S5 | basis | 静态来源核验 |

## 使用与维护

变更规则时核对对应 RF 行的来源是否仍支持它，再更新受影响的状态与案例。新增来源记录版本、可见原文定位与读取范围；新增验证保留原材料和实际结果。仅修改链接、表格或静态校验通过，只能证明映射可用，不证明新增行为或标准符合性。

本表的静态关系校验、来源审查与限制见[追踪评测记录](../tests/evaluations/basis-traceability-2026-10-01.md)。
