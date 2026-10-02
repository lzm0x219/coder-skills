# 事件 API 设计规则

适用于消息 broker / event bus / stream 的 producer 与 consumer。先判断用户是在设计 domain event、message contract、broker profile、schema registry 还是事件消费状态，并固定协议/产品/版本；HTTP callbacks 走 [Webhook](webhooks.md)。触发具体分支时读取对应 reference：

- payload、identity、CloudEvents、schema evolution / registry → [schema](events/schema.md)
- Kafka、AMQP 1.0、MQTT 5、NATS JetStream、delivery matrix、transactions / outbox → [broker profiles](events/brokers.md)
- 事件处理流程的通用 ACK、排序、回放、DLQ、批量、event-time 和 observability 在 [broker profiles 的交付矩阵](events/brokers.md#交付矩阵适用于各-broker)

## 原有规则索引

保留 E01–E09 标识，供已有消费者和设计记录追踪；以下是简述，具体动作、边界及来源以链接文件为准。

| ID | 持续适用范围 | 详细规则 |
|---|---|---|
| E01 | domain event 语义与发出时点 | [ES01](events/schema.md#规则) |
| E02–E03 | CloudEvents envelope、stable identity、context 类型与 JSON 映射 | [ES02、ES10–ES11](events/schema.md#规则) |
| E04 | schema/事件类型演进和旧 consumer window | [ES04–ES06](events/schema.md#规则) |
| E05–E07 | broker-specific ordering、delivery、retry、replay | [Kafka / AMQP / MQTT / JetStream](events/brokers.md) |
| E08 | AsyncAPI document 和 protocol binding | [AsyncAPI delivery](#asyncapi-交付) |
| E09 | 安全、容量、保留与删除 | [ES07–ES08](events/schema.md#规则)、[broker matrix](events/brokers.md#交付矩阵适用于各-broker) |

## AsyncAPI 交付

采用 AsyncAPI 时锁定文档版本、validator 版本及 protocol binding version。具体接口描述 application operations 的 send/receive 方向、channel/address、message variants、payload schema/contentType、correlation/security 和 broker binding。它是 machine-readable interface contract，不是 broker runtime configuration；协议文档的可选字段不能臆称格式强制，但 Skill 交付需要的具体 contract facts 不能缺失。由对应版本 validator 检查格式，并另外验证 bindings 对目标 broker 的参数是否真实可部署。[AsyncAPI 3.1.0](https://www.asyncapi.com/docs/reference/specification/v3.1.0) 的 MUST 只用于 3.1.0 文档。

## 完成交付检查

每个适用设计分支要么给 evidence artifact，要么标“不适用+业务原因”；缺失需求写明 owner/待决定事实/决策影响。至少提交消息方向、channel/address、payload/schema、producer/consumer principal、event identity、确认与副作用边界、排序 domain、retry/poison/DLQ、retention/replay/offset、limit/batch/compression/backpressure 和监控值。数值只能从业务约束、目标 provider 限制或部署 configuration 推导；不能使用文档里的 example/default 冒充目标项目承诺。

固定 schema/vector 可运行检查证明所校验 bytes/cases 与 schema/profile 一致。它不证明 broker 投递、ACL 实际部署、队列容量、顺序、回放、outbox/inbox DB 原子性或 end-to-end exactly-once。需要这些保证时，必须用目标 broker/DB 的故障注入与恢复演练验收。

固定样例：[原事件演进与乱序 cases](../../../tests/design-apis/cases/events-order/contract.md)。研究来源和规则取舍：[事件与 Webhook 来源](sources.md#events-webhooks)。
