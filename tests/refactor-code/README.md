# refactor-code 测试

[评测协议](methods/capability.md)规定行为兼容、结构收益与状态恢复的验收方法；[案例](cases)是当前可复用输入，[来源页](../../skills/refactor-code/references/basis.md)维护 8 个来源与 15 条 RF 映射。

从仓库根运行：

```sh
rtk proxy python3 tests/refactor-code/checks/verify_basis.py
rtk proxy python3 tests/refactor-code/checks/run_cases.py
```

`verify_basis.py` 检查当前来源与权威规则的关系，不联网验证原文。`run_cases.py` 在临时目录编译并检查 TS 库、订阅时序、重复计费与 ledger；默认自检现有案例，并核实取消回归变体会被拒绝。

核验重构候选时传入包含相同案例的目录：

```sh
rtk proxy python3 tests/refactor-code/checks/run_cases.py /path/to/candidate
```

案例运行与智能体独立重构分别验收。材料通过不证明目录重设计收益、用户编辑保全或实际状态转移已由代理完成；这些按评测协议另行观察。

[首轮独立任务评测](../agent-evals/README.md)记录本 Skill 的一次新上下文任务、首次产物与评估方检查；其通过结论限于该案例。
