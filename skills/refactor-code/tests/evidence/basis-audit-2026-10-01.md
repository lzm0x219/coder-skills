# refactor-code 来源映射独立只读核验

日期：2026-10-01。范围仅该 Skill 的 basis.md、所指执行规则、两份评测记录及必要归档证据；未改仓库，未重跑评估器，未审计其他 Skill。

结论：未发现有影响的来源层级冒充、ISO 合规冒充、精确页码错误、案例等级夸大或失效指针。

## 已核验事实

- basis.md:9–14 定义原文支持、方法推导、项目机制和标准背景，并明确不构成 ISO 合规声明。RF01/RF05 的行为保持与小步检查可由 [Fowler 原文](https://refactoring.com/) 支持；具体动作保留项目解释。RF02/03/04/06/07/10/14 的细化动作标为方法推导，RF08/09/11/12/13 标为项目机制，没有把状态机门槛归给外部标准。
- basis.md:21–23 的支持边界保守且符合可见材料：[Boundary](https://martinfowler.com/bliki/RefactoringBoundary.html) 讨论可观察性及改善目的；[Extract Function](https://refactoring.com/catalog/extractFunction.html)、[Move Function](https://refactoring.com/catalog/moveFunction.html) 为目录示例，不冒充完整 Mechanics；[Preparatory Refactoring 的 Final Thoughts](https://martinfowler.com/articles/preparatory-refactoring-example.html) 支持先改善结构再新增行为的顺序。
- basis.md:25–27 的 ISO 日期分别与官方元数据 2026-04、2022-01、2023-11 一致。[12207 摘要](https://www.iso.org/standard/90219.html) 未指定唯一方法；[14764 摘要](https://www.iso.org/standard/80710.html) 仍以 12207:2017 为依据；[25010 摘要](https://www.iso.org/standard/78176.html) 为产品质量模型背景。文中没有规范性条款映射或合规结论。
- basis.md:35–40 的 [SWEBOK V4.0a](https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf) 章节/纸面页/文件页吻合。网页 PDF 解析页号从零开始，逐项加一得到：3章1.4＝85–86；5章2.2.5＝124；7章2.1.3＝172；7章4.2＝179–180；8章2.1–2.4＝190–191；8章2.6＝192。7章4.2 正式标题是 Software Reengineering，其正文确实包含重构的行为及结构边界，映射未误写其标题。8章2.6 正式标题 Software Libraries，包含测试与源码基线关联及构建对象追踪。basis.md:42 已区分正式配置基线和工作区验证对照。
- basis.md:50–64 的案例等级与两份 evaluations 及 execution/state-v2 报告、rules-v2/boundaries results.json 一致。独立结构案例为受控运行；changed-baseline 为有分阶段提示的真实执行；bad-check 明确是带提示执行；missing-artifact、incomparable、coupling-gap、stale-evidence、resume、revoked 等保留状态走查边界。未把私有集成缺包称通过，未把只读分析称代码改造。
- 用只读 Python 解析 basis.md 全部本地 Markdown 目标并检查实际标题锚点：23 个目标全部有效。外部九个链接（F03 两条）均通过网页工具打开。入口和四份执行参考已读取；rubric 只检查目标文件存在，没有依赖它给出行为通过结论。

## 限制

审查核验公开原文、归档材料和表述是否一致，没有重新运行旧评估、下载依赖或建立生产环境。ISO 仅核验官方公开摘要/元数据，未取得规范性全文；因此不判断正式标准符合性。未证明所有案例输入、第三方消费者或异常组合。SWEBOK 页码核对基于当前公开 V4.0a 文件的页面标记和正文定位，未审阅整本指南。

Jev 根据上述事实选择“未发现有影响的问题，保留审查限制”，置信度 0.77；它没有替代源码、页码和指针核验。
