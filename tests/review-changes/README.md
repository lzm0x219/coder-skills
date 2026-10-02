# review-changes 测试

[评测协议](methods/capability.md)与[覆盖清单](methods/coverage.json)维护方法和 95 个公开规则 ID；[固定案例](cases)保存受控输入、反例与预期。

从仓库根运行：

```sh
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/review-changes/checks -p 'verify_*.py'
```

- `verify_coverage.py`：规则清单、触发/动作/完成标记、引用与软件类型。
- `verify_review_cases.py`：边界、授权、反证以及真实 Git 范围。
- `verify_extended_cases.py`：事务、CLI、输入边界等受控见证。
- `verify_type_replay.py`：直接消费 `cases/all-types-source.json` 的可复用多语言输入；宿主 C/Swift 与 plist 检查按工具可用性执行。

这些检查验证规则结构或案例行为，不测量智能体审查正确率，也不证明真实设备、OS 生命周期与生产环境。

[首轮独立任务评测](../agent-evals/README.md)记录本 Skill 的一次新上下文任务、首次产物与评估方检查；其通过结论限于该案例。
