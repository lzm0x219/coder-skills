# Coder

`coder` 是面向软件开发的 Skill 插件。`master` 是总入口，负责在实际可用的专业 Skill 中选择适合当前任务的能力，并继续完成任务。

## 当前状态

- 插件标识：`coder`
- 已实现的 Skill：`coder:master`、`coder:design-apis`、`coder:fix-bugs`、`coder:refactor-code`
- 其余专业 Skill：[命名规则与优先候选](docs/taxonomy.md)及[43 项英文工作名与覆盖状态](docs/coverage-plan.md)已记录，尚未实现
- 尚未安装或发布；已用 [GitHub Releases 真实服务契约](skills/design-apis/tests/fixtures/github-releases-sdk-review.md)做局部复测，完整 SDK 发布行为验收仍未进行
- `design-apis` 的 `library-sdk` 设计期规则已有[限定范围评分与验证记录](skills/design-apis/tests/evaluations/library-sdk-2026-09-30.md)；运行 `rtk proxy python3 skills/design-apis/tests/verify_library_sdk.py` 可复查 TypeScript、Python、Rust 样例及兼容性反例
- `fix-bugs` 已有[限定范围的独立评测与评分](skills/fix-bugs/tests/evaluations/fix-bugs-2026-09-30.md)，包含真实项目、受控缺陷、无提示路由和未复现场景
- `refactor-code` 已完成[整体优化与限定复验](skills/refactor-code/tests/evaluations/overall-optimization-2026-10-01.md)：六状态门槛、按分支加载、兼容账、异常恢复与交付结论；[来源映射](skills/refactor-code/references/basis.md)连接 8 项来源、15 组规则和 16 个案例。已归档的 TS、异步、去重复及状态恢复实现复验通过；本次分支检查与既有自然路由证据均属语义走查，未新增代理从零执行、安装自动发现或生产环境验证。ISO 摘要只作背景，未进行条款符合性审计
- `design-apis` 的 HTTP、GraphQL、RPC/Proto、事件及 Webhook 设计案例见[协议样例与验证说明](skills/design-apis/tests/README.md)；运行 `rtk proxy python3 skills/design-apis/tests/verify_protocols.py` 可复查静态与模型测试，真实服务行为另行验证

## 项目结构

```text
plugin.json             插件身份与版本
skills/master/SKILL.md  总入口
skills/design-apis/SKILL.md  API 契约设计
skills/design-apis/references/  按 API 类型分开的规则；库/SDK 规则继续按任务分支拆分
skills/design-apis/tests/  该 Skill 的测试样例、验证记录与回归脚本
skills/fix-bugs/SKILL.md  缺陷复现、定位、修复与回归验证
skills/refactor-code/SKILL.md  结构重构、分步实施与兼容核验
skills/refactor-code/references/  模块目录设计、兼容基线、恢复规则、验证交付与来源映射
skills/refactor-code/tests/  隔离材料、行为验证器与评测协议
docs/taxonomy.md        分类与命名规则
docs/coverage-plan.md   软件工程任务覆盖与职责
```

专业 Skill 在实现时直接放入 `skills/<skill-name>/SKILL.md`。不为尚未实现的能力建立占位 Skill。

## 命名

插件名为 `coder`，总入口名为 `master`。专业 Skill 使用小写英文、连字符和“动词-对象”形式，例如 `design-apis`。作为插件安装后，完整身份由插件名和 Skill 名组成，例如 `coder:design-apis`。
