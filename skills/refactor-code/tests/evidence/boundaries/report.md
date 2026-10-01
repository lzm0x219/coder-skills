# 独立边界与路由实测

读取 refactor-code/SKILL.md、三个 references 和 master/SKILL.md；未读取 tests/rubric.md、verify_cases.cjs，未改仓库。原始材料在 originals/，用户未提交差异在 user-edits/user-baseline.diff。before.json、after.json 为 SHA-256 指纹；versions.txt 记录实际 Node 版本。

## 实施与证据

原始计价与收据合在 index.cjs。实际拆为 pricing.cjs（税率及计价）、receipt.cjs（显示格式），原 index.cjs 保持 total/receipt 公共入口。依赖方向 index → receipt → pricing；税率变更只涉及 pricing，格式变更只涉及 receipt。没有更换算法或业务错误约定。

1. old-failure：前后 consumer 均退出 0，四组输入的公共入口 differential 退出 0。unrelated.cjs 的既有 assert 1===2 失败前后均退出 1，文件指纹相同。未修复无关失败。目标切片完成，不能宣称全套检查通过。
2. user-edits：实际创建 Git 基线提交，随后留下未提交 USER Total: 前缀改动。重构后前缀保留，consumer 与 original 对照均退出 0。保留的是工作区原始材料中的用户改动，没有恢复 HEAD。
3. readonly：仅一个纯 add(a,b) 函数，无独立变化策略、共享状态或职责摩擦。交付无需拆分判断；没有修改 index.cjs，指纹相同。consumer 退出 0。Jev 此项置信度 0.39、escalate=true，却建议拆分；Codex 根据明确只读边界及无收益事实拒绝该建议。
4. missing-private：不安装、不替换 @private/billing-engine。纯模块已拆分，consumer 与原始入口四组对照退出 0；runtime.cjs 前后均 MODULE_NOT_FOUND、退出 1。私有引擎集成行为没有验证，只能称纯模块切片部分交付，不能宣称生产运行兼容。

实际命令：python3 build-fixtures.py；node --version；各目录 node consumer.cjs（前后）；node unrelated.cjs（前后）；node runtime.cjs（前后）；git diff；python3 verify.py（运行 Node 公共入口差分并记录退出码）。均通过 rtk proxy 执行。日志保存各目录 before.log/after.log、differential.log 及失败日志；results.json 汇总退出码。

Jev 对缺包选择“实施纯模块切片并限定验证范围”（0.96），对旧失败选择“保留失败，独立验证目标切片”（0.74）。这些判断未替代实际运行证据。

## master 自然请求路由

首次读取 master 未含 refactor-code 的显式路由，已通知父任务。父任务更新通知后重新读取，当前实际文本已包含该路由。以下按更新文本判定：

| 自然请求 | 主路由 | 理由 |
| --- | --- | --- |
| 整理目录保持 API | refactor-code | 既定行为、兼容约束下调整目录与模块 |
| 修复取消失效 | fix-bugs | 修复已有可观察行为的缺陷 |
| 审查 PR | review-changes | 固定差异的正确性与回归审查 |
| 设计新 API | design-apis | 调用者可见契约本身的设计 |
| 只分析全仓改善机会 | 常规只读分析，先交付有依据的候选 | master 明文要求先交付候选，不能自动推进结构修改；无具体重构范围 |

评价边界：这些是小型 CommonJS 人工项目的真实执行。没有 TS 类型、发布包或私有运行环境证据，不能扩张为所有语言和环境均验证。
