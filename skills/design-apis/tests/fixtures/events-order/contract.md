# 订单创建事件契约样例

主载体是 [事件 schema](event.schema.json)；[有效](valid.json)及[缺少 `id` 的反例](invalid.json)分别验证生产和拒绝路径。该 JSON Schema 是**本样例针对单一事件类型的设计约束**，不宣称覆盖全部 CloudEvents 一致性要求。CloudEvents `id`、`source`、`specversion`、`type` 是必需属性，`time` 可省略。

生产者在订单事务提交后将事实事件写入 outbox；本样例设计为至少一次投递。主题 `orders.created.v1`，以 `orderId` 分区；仅承诺同一订单在单分区中的顺序。`source + id` 对同一事实重投保持不变，新事实使用新 `id`。消费者处理成功并持久化去重记录后确认；处理失败重试最多 5 次，之后入死信队列，人工可在 7 天保留期内补发。去重记录保留 8 天以覆盖该窗口。旧消费者可忽略新增可选字段，但改动 `revision` 语义须另开版本。无真实 broker 或 outbox 实现验证，顺序、重试、保留与原子性均是待实现设计。依据：[CloudEvents 稳定规范](https://github.com/cloudevents/spec/blob/ce@stable/cloudevents/spec.md)。
