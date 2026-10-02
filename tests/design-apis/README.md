# design-apis 测试

[规则准则](methods/rules.md)检查覆盖、准确性、可执行性与出处；[能力准则](methods/capability.md)检查设计交付和独立使用。当前固定案例直接由检查器消费。

| 检查 | 输入与范围 |
| --- | --- |
| [HTTP / GraphQL](checks/verify_http_graphql.cjs) | [HTTP 条件更新](cases/http-profile/contract.md)、[分页与导出](cases/http-exports/contract.md)、[GraphQL](cases/graphql-order/contract.md)；schema、错误、消费者和局部执行 |
| [事件 / Webhook](checks/verify_events_webhooks.cjs) | [事件](cases/events-order/contract.md)、[Webhook](cases/webhook-github/contract.md)；消息 schema、演进、HMAC 和投递模型 |
| [RPC](checks/verify_rpc.py) | [Proto 与 loopback](cases/rpc-profile/contract.md)；生成、wire、旧消费者、重试、deadline、流终态和取消 |
| [程序接口](checks/verify_library_sdk.py) | [TS 演进](cases/typescript-sdk-evolution/contract.md)、[Python](cases/python-audit-sdk/contract.md)、[Rust](cases/rust-audit-sdk/contract.md)及其他 SDK 调用点；声明和消费者 |
| [规则报告](checks/review_rules.py) | 调用方提供的报告；核实当前规则路径、SHA、原文和证据字段，不裁定规范语义 |

从仓库根运行：

```sh
rtk proxy python3 tests/design-apis/checks/verify_protocols.py
rtk proxy python3 tests/design-apis/checks/verify_library_sdk.py
rtk proxy python3 tests/design-apis/checks/review_rules.py <规则专项报告.json>
```

protocols 包含 HTTP/GraphQL、事件/Webhook 与 RPC；依赖和生成物隔离在临时目录。固定输入与消费者通过不表示生产服务、真实 broker、第三方投递、正式包发布或智能体独立使用通过。

[首轮独立任务评测](../agent-evals/README.md)记录本 Skill 的一次新上下文任务、首次产物与评估方检查；其通过结论限于该案例。
