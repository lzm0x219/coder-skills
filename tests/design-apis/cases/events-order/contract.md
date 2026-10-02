# CloudEvents 事件契约与消费者演进样例

状态：固定契约样例，可用于事件设计评审；没有连接真实 broker 或数据库。事件封装使用 CloudEvents JSON structured mode 1.0，类型为 `com.example.order.created.v1`。封装字段包含必需身份字段和 `datacontenttype: application/json`；`source` 是绝对 HTTPS URI，`dataschema` 标识 payload contract。省略 `time` 合法，因为 CloudEvents 将其定义为可选。

## Schema 与兼容窗口

- [CloudEvents v1.0.2 官方 JSON Schema](cloudevents-v1.0.2.schema.json) 原样固定在 fixture 中，来源是 CloudEvents `v1.0.2` tag，运行时由 Ajv draft-07 校验。
- [项目事件封装 schema](event.schema.json) 固定 CloudEvents version/type 与 `source` 的 URI-reference 格式，并引用 v1 载荷规则；[旧消费者 schema](consumer-v1.schema.json) 代表兼容窗口里的使用方。
- [合法事件](valid.json) 通过官方格式 schema 和项目 profile；[负例](invalid.json) 使用非法 `source`，两层校验都拒绝。
- [候选可兼容事件](candidate-additive.json) 新增可选载荷字段，旧消费者接受；[破坏候选](candidate-breaking.json) 删除旧消费者必需的 `revision`，旧消费者拒绝。生产规则据此要求：任何必填/语义/枚举/触发条件变化先评估兼容性；发布破坏变化时使用新的 `type` 或 `dataschema` URI，并给出旧消费者退出窗口。

## 投递模型与消费者预期

[delivery-cases.json](delivery-cases.json) 是本示例自定义的**设计假设**，不是 CloudEvents 或 AsyncAPI 自动保证：at-least-once、按 order key 分区、瞬态故障最多 5 次指数退避加 jitter，耗尽后 DLQ 告警；永久错误不重试；30 天可回放，由 consumer group 管 offset。

revision 处理案例分别覆盖正常递增、重复/乱序和缺号。消费者将过期 revision 视为陈旧、忽略；缺号先停放并对账，不越过缺失 revision。代码中的纯函数只验证这套状态转移示例，不证明并发去重、事务原子性、持久性或 exactly-once。上线前要用目标 broker 的 partition、ack、retention、redelivery、DLQ 与数据库事务配置做集成验证；如果业务副作用与 checkpoint 无共同原子边界，文档只能称 at-least-once/idempotent behavior，不能承诺恰好一次。

## 来源

- [CloudEvents Core 1.0.2](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md)
- [CloudEvents JSON event format schema 1.0.2](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/formats/cloudevents.json)
- [AsyncAPI 3.1.0](https://www.asyncapi.com/docs/reference/specification/v3.1.0)
- 执行 `node verify_events_webhooks.cjs <fixture-root>` 的 CloudEvents JSON Schema 校验只覆盖样例格式与示例 payload 兼容；不会测试 broker 的运行语义。
