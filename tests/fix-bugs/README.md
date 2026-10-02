# fix-bugs 测试

[工作流](../../skills/fix-bugs/SKILL.md)采用 S0–S7；[工具测试](../../skills/fix-bugs/scripts/tests)检查人工复现反馈与发生率采样。

```sh
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/fix-bugs/scripts/tests
```

独立使用评测分别观察原症状红灯、定位证据、旧红新绿、回退与有限交付。工具测试不证明代理诊断效果；原场景缺失或仅修复替代症状时，按工作流保留相应限制。

[首轮独立任务评测](../agent-evals/README.md)记录本 Skill 的一次新上下文任务、首次产物与评估方检查；其通过结论限于该案例。
