# 来源与规则映射

核对出处、修改规则或评估标准符合性时读取。本页只维护来源；执行要求以所指章节为准。来源核验日期为 2026-10-01，RF 是项目追踪编号。

## 依据层级

- 原文支持：公开原文明确表达对应原则；项目中的执行动作仍按实际环境选取。
- 方法推导：由已核验原则推导具体检查或门槛，原文没有规定同一实现。
- 项目机制：本 Skill 的授权、状态或证据管理设计，不冒充外部标准要求。
- 标准背景：只核验官方版本与摘要，用于组织过程或质量目标；尚无规范性条款映射。

正式符合性评估须取得适用版本规范性全文，确认条款、裁剪与组织要求，再逐条取证。此映射只证明方法出处，不构成 ISO 合规声明；执行仍沿用任务授权。

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

案例与运行证据由[评测协议](../../../tests/refactor-code/methods/capability.md)及[测试入口](../../../tests/refactor-code/README.md)维护；此表只回答规则从何而来。

| ID | 权威规则位置 | 来源与定位 | 依据层级 |
| --- | --- | --- | --- |
| RF01 | [行为边界](../SKILL.md#重构代码) | F01 Definition；W01 第7章 §4.2 | 原文支持 |
| RF02 | [消费者观察](compatibility.md#观察细则) | F02；W01 第3章 §1.4 | 方法推导 |
| RF03 | [职责](structure.md#从维护摩擦推导职责)与[收益](structure.md#结构证据) | F01 改善目的；W01 第3章 §1.4 | 方法推导 |
| RF04 | [移动](structure.md#目录重设计)与[去重复](structure.md#去重复与抽象) | F03 摘要；W01 第3章 §1.4 | 方法推导 |
| RF05 | [小步实施](../SKILL.md#s3-分步实施) | F01 小步变换与 frequent testing | 原文支持 |
| RF06 | [回归选择](verification.md#验证顺序) | W01 第7章 §2.1.3；第5章 §2.2.5 | 方法推导 |
| RF07 | [基线身份](compatibility.md#兼容账) | W01 第8章 §2.1–2.4、§2.6 | 方法推导 |
| RF08 | [证据失效](recovery.md#工作区变化与证据失效) | W01 配置/测试关联为背景；返回状态为项目设计 | 项目机制 |
| RF09 | [失败分类](recovery.md#检查失败)与[范围收缩](recovery.md#环境缺失与范围收缩) | 项目证据设计；W01 影响分析为背景 | 项目机制 |
| RF10 | [检查预期](recovery.md#保护检查的观察)与[混合验收](../SKILL.md#s2-选定结构方案) | F01 行为保持；F04 Final Thoughts；失败保护为项目设计 | 方法推导 |
| RF11 | [交付](verification.md#完成判断) | I03 摘要为质量目标背景；具体结论为项目设计 | 项目机制 |
| RF12 | [中断恢复](recovery.md#中断恢复) | 项目状态设计；W01 配置身份为背景 | 项目机制 |
| RF13 | [用户编辑/授权](recovery.md#工作区变化与证据失效) | 当前任务与项目权限约束 | 项目机制 |
| RF14 | [制品观察](compatibility.md#观察细则)与[验证](verification.md#验证顺序) | W01 第8章 §2.6；平台细则为方法推导 | 方法推导 |
| RF15 | [标准声明边界](basis.md#依据层级) | I01/I02 Abstract | 标准背景 |

## 使用与维护

变更规则先核对 RF 来源仍适用，再更新受影响状态与案例；新增来源注明版本、定位与读取范围，新增验证保留原材料和结果。静态关系核验使用[关系检查器](../../../tests/refactor-code/checks/verify_basis.py)，仅证明来源登记与当前规则指针完整。
