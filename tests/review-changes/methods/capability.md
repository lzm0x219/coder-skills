# 评测协议

评测者从入口开始，按真实变化选择参考；不用预先指定的规则 ID 引导其发现。每例冻结基线、目标、需求来源、入口/消费者、环境与文件 hash。审查生成物与原作者差异分开登记。

## 两层证据

- 运行见证：证明该夹具的行为或比较语义，不能证明智能体会执行规则。
- 独立前向评测：评测者实际用 Skill 审查，记录发现、反证与缺口。自建自评不是盲测；预期由另一人/Agent 先固定且评测阶段不提供答案时才记为预期隔离评测。

逐例记录预期、实际、规则、来源、工具观察、错误及限制；有缺陷、有成立反证、证据不足三类都要覆盖。已有真实差异可补外部有效性，但本仓库自己改动不是外部真实 PR 样本。

## 成功门槛

确认发现必须符合 S3 五门槛；有效保护不得误报；重要缺失证据必须保留。缺陷/规范/建议分别统计，重复根因只计一次。精度/召回只针对事先定义的金标准集合；未定义样本不纳入分母。

时间、读入参考数与检查次数记录实际值，不能以文件大小推出实际 token 节约或速度。复用同一观察的多条规则不冒充多个独立验证。

## 覆盖记账

规则文件是定义的唯一事实源；[覆盖清单](coverage.json)只记录 ID、路径与证据引用，不复制规则正文。覆盖测试检查 ID/链接/门槛形状；它不评价规则语义或智能体行为。没有逐条运行证据的规则标为“未有逐条运行见证”，不补上推测通过。

本地执行：

```sh
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 tests/review-changes/checks/verify_review_cases.py
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 tests/review-changes/checks/verify_extended_cases.py
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 tests/review-changes/checks/verify_type_replay.py
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 tests/review-changes/checks/verify_coverage.py
```

设备、浏览器/辅助技术、broker、云环境或模型不具备时不绕过宿主限制；明确停在相应证据层。规则扩展需更新清单与独立评测，不能只增加规则数。
