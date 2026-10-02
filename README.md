# Coder

面向软件开发的 Skill 插件。从 [master](skills/master/SKILL.md)开始，或直接指定专业 Skill。

| Skill | 目标 |
| --- | --- |
| [master](skills/master/SKILL.md) | 按目标选择能力并完成任务 |
| [design-apis](skills/design-apis/SKILL.md) | 设计、演进与评审 API 契约 |
| [fix-bugs](skills/fix-bugs/SKILL.md) | 复现、定位、修复与验证缺陷 |
| [review-changes](skills/review-changes/SKILL.md) | 审查固定差异与需求符合性 |
| [refactor-code](skills/refactor-code/SKILL.md) | 改善结构并核验行为兼容 |

执行规则从各 Skill 入口沿条件指针读取；检查命令与案例见[测试入口](tests/README.md)。`plugin.json` 维护插件身份。仓库只维护当前 Skill、测试及其必要输入和配置。
