# Broker profiles: Kafka、AMQP 1.0、MQTT 5 与 NATS JetStream

本页扩充 [E05–E09](../events.md)。选择哪种 broker 就走相应 profile；相同词（ACK、transaction、ordered、retained）在协议间不构成相同保证。没有指定 broker 时，把值标记为待选/待部署确认，不能虚构默认保证。

## 每个 profile 都要落到合同的字段

| 字段 | 必填决策与恢复路径 |
|---|---|
| 拓扑和路由 | producer/consumer、topic/queue/subject、exchange/binding 或 partition key；绑定/过滤失配后如何发现、补发。 |
| 投递与确认 | 初次发送 ACK、consumer ACK/settlement、处理提交和 checkpoint 各自含义；超时结果未知时去重/重试。 |
| 排序/并发 | key 与 ordering domain（partition/queue/session/subject）；跨 domain 不承诺全序；重复、乱序、缺号、并行冲突处理。 |
| retention / replay | broker retention、expiry、consumer offset/cursor、replay 起点/权限/副作用抑制/边界；到期后恢复源。 |
| 容量和流控 | 单条最大消息、batch/fetch/prefetch/credit、压缩和解压后限额、producer buffer/backpressure；超限拒绝/拆分/隔离。 |
| 隔离和访问 | producer 写、consumer 读、组/队列/subject 权限、schema registry/DLQ 权限、凭据撤销和租户边界。 |
| 毒消息与 DLQ | retry 次数或时间窗、永久错误识别、死信保留/权限、人工修复重放、循环防护和审计。 |

参数值来自目标服务限制、业务 SLO、payload 测量和容量测试；采用 CloudEvents 时同时按[schema:ES09](schema.md)核对 64 KByte 的中介/消费者互操作基线，不能用产品上限覆盖已采用的协议要求。分批发送不得将部分成功当成全批成功；应定义逐项结果或事务边界。压缩须写算法、协商方式、最大压缩/解压大小和不可支持客户端行为；压缩不改变 payload schema。

## Kafka profile

| ID | 适用条件与强度 | 动作、失败路径、证据 | 来源 |
|---|---|---|---|
| EBK01 | Kafka producer。**Skill MUST** | 定义 key、partitioner、partition-count 改变时 ordering 影响、acks、retries、idempotence、delivery timeout、max request/batch/buffer 和压缩 codec。网络超时是结果未知：重试应由 idempotent producer 或事件身份幂等吸收；batch 部分/整批失败需可重放。提交有效配置和目标 broker 上故障注入结果。 | [Kafka producer configs](https://kafka.apache.org/25/configuration/producer-configs/)、[design](https://kafka.apache.org/design/)；配置需匹配实际 client/server 版本。 |
| EBK02 | 同 key 内排序重要。**Skill MUST** | 将同一顺序实体的记录稳定映射到 key；以 partition 为排序边界。扩分区或改变 key/partitioner 前制定迁移或 revision reconciliation；测试不能要求 topic 全局顺序。 | [Kafka introduction](https://kafka.apache.org/documentation/) |
| EBK03 | consumer side-effect + offset。**Skill MUST** | 选择自动/手动提交并写出“处理完成”边界；禁止在副作用前推进 offset。崩溃窗口需以可重试+业务幂等恢复。若要求 Kafka 内部 exactly-once，写 producer transaction + `sendOffsetsToTransaction` 等目标 client 操作、consumer `read_committed` 和 group fencing/rebalance 约束；外部 DB/HTTP 仍需 outbox/inbox、幂等 key 或协调事务。 | [Kafka transactions](https://kafka.apache.org/design/#message-delivery-semantics) |
| EBK04 | Kafka ACL 开启。**Skill MUST** | 以 principal × resource × operation 表证明 producer `WRITE`/必要 `DESCRIBE`；consumer `READ` topic 和 `READ` group；事务 producer 有 `WRITE` transactional-id；schema registry 与 DLQ 单列。未知/拒绝授权要 fail closed 并告警。 | [Kafka authorization and ACLs](https://kafka.apache.org/42/security/authorization-and-acls/) |
| EBK05 | 重放/死信/大消息/批量。**Skill MUST** | 记录 topic retention/compaction、consumer group offset reset 所需权限和回放隔离；DLQ 是否保留原 key/headers/schema/errors 且如何防敏感泄漏。batch 与 max message/compressed/uncompressed sizes 匹配 producer、broker、replica、consumer fetch；超过任一限制的拒绝/隔离与重试终止路径逐项声明。 | Kafka broker/client 配置与组织运行手册；具体限制必须从部署读取，不能由此规则推常数。 |

## AMQP 1.0 profile

| ID | 适用条件与强度 | 动作、失败路径、证据 | 来源 |
|---|---|---|---|
| EBA01 | AMQP 1.0 links。**协议 MUST + Skill MUST 分别应用** | 按协议处理 sender-settle-mode、receiver-settle-mode、delivery state/outcome 与 unsettled/link recovery；`accepted` 表示 receiver 成功处理，不自动代表下游业务终态或外部 DB 提交。Skill MUST 把 accepted/rejected/released/modified 映射到明确的应用确认阶段，说明可靠入队还是业务提交，只有达到所承诺里程碑才发相应接受态。broker receiver 的接受不能冒充业务 consumer 的完成。断链恢复按 broker 支持的 link resume 与未 settle 状态给出失败/恢复合同。 | [AMQP 1.0 Transport §2.6–2.8](https://docs.oasis-open.org/amqp/core/v1.0/amqp-core-transport-v1.0.html)、[Messaging §3.4](https://docs.oasis-open.org/amqp/core/v1.0/amqp-core-messaging-v1.0.html#section-3.4)；可靠性里程碑为应用合同。 |
| EBA02 | 采用 AMQP 1.0 transaction。**协议 MUST + Skill MUST** | 声明 transaction coordinator、事务内 posting/acquisition/retirement 与 discharge/rollback；失败和链接断开后事务状态/未 settle delivery 的恢复步骤要实测。协议事务只覆盖参与的 transactional resource/link；外部 DB/API 的 side effect 需要 outbox/inbox 或协调策略。 | [AMQP Transactions Part 4 §4](https://docs.oasis-open.org/amqp/core/v1.0/amqp-core-transactions-v1.0.html) |
| EBA03 | address/routing/queue/subscription。**Skill MUST** | 在实际 broker mapping 写 exchange/address、queue、binding key/filter、durable/auto-delete、expiry/TTL、max length、dead-letter exchange、consumer credit/prefetch、exclusive/shared 与 authorization。未路由、被过滤或队列满需识别；不能以 send API 返回成功代替路由/持久保存证明。 | [AsyncAPI AMQP 1.0 binding](https://www.asyncapi.com/docs/reference/bindings/amqp1)、目标 broker 官方管理/协议文档。 |

## MQTT 5 profile

| ID | 适用条件与强度 | 动作、失败路径、证据 | 来源 |
|---|---|---|---|
| EBM01 | MQTT publish。**协议 MUST** | 每个消息定义 QoS、RETAIN、Message Expiry Interval、payload format/content type、响应主题/Correlation Data（如使用）及订阅授权。QoS 0/1/2 的协议交换不等价于业务事务或数据库 exactly-once；PUBACK/PUBREC/PUBCOMP reason code 失败须映射到拒绝、重试或 dead-letter policy。 | [OASIS MQTT 5.0 §3.3、§3.4–3.7](https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html) |
| EBM02 | 断连后继续接收。**Skill MUST** | 写 `Clean Start` 与 `Session Expiry Interval`，并说明 subscriptions、未确认 QoS message、expiry 和 broker capacity；离线过期、session 已移除与重连竞态的补偿/状态查询。session expiry=0/缺省及实现限制需从 negotiated properties / broker profile 验证。 | [MQTT 5.0 §3.1.2、§4.1](https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html) |
| EBM03 | retained/state distribution。**Skill MUST** | 说明 retained 是每 topic 最新保留状态而非完整历史事件 log；retain 清除、订阅时 retained delivery 与普通 delivery 的消费差别。历史追溯依赖独立事件存储/回放 API。 | [MQTT 5.0 §3.3.1](https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html) |
| EBM04 | MQTT ACL、shared subscription 或流控。**Skill MUST** | topic filter 授权分别限定 publish/subscribe；用 `$share/{group}/{filter}` 时说明负载分摊、无每组广播保证及重平衡影响；定义 Receive Maximum、Maximum Packet Size、Topic Alias 协商、最大 payload/expiry/backpressure。拒绝/离线积压/超限有可观测 reason 和恢复路径。 | [MQTT 5.0 §3.8、§4.9–4.13、§4.8](https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html) |

## NATS JetStream profile

| ID | 适用条件与强度 | 动作、失败路径、证据 | 来源 |
|---|---|---|---|
| EBN01 | Core NATS 与 JetStream。**Skill MUST** | 明确选择 ephemeral Core pub/sub（无持久保存确认）还是 JetStream stream；JetStream publish 使用 PubAck 时区分被 stream 接收和消费者完成。PubAck 丢失需用 stable message ID / `Nats-Msg-Id` dedup window 控重复，并声明窗口期限。 | [JetStream concepts](https://docs.nats.io/nats-concepts/jetstream)、[message deduplication](https://docs.nats.io/using-nats/developer/develop_jetstream/model_deep_dive#message-deduplication) |
| EBN02 | JetStream consumer。**Skill MUST** | 选择 durable/ephemeral、push/pull、delivery policy、ack policy/ack wait、max deliver/backoff、max ack pending、max waiting 与 filter；明确 ack 是业务完成还是收到，`AckSync`/double ack 是否采用。NAK、in-progress、term、超限重投和 consumer 删除后的恢复分别测试。 | [Consumers](https://docs.nats.io/nats-concepts/jetstream/consumers)、[acknowledgment model](https://docs.nats.io/using-nats/developer/develop_jetstream/model_deep_dive#acknowledgement-model) |
| EBN03 | retention/回放/容量。**Skill MUST** | 在 LimitsPolicy / InterestPolicy / WorkQueuePolicy 中标明实际 policy、max age/bytes/messages/consumers、discard old/new、replicas/storage/rollup、per-message TTL 和 purge/delete 授权。ReplayPolicy original/instant 语义标注；ordered consumer 适合只读遍历而非应用 ACK 处理保证。容量淘汰触发告警/补源，不默默称永久持久。 | [JetStream streams](https://docs.nats.io/nats-concepts/jetstream/streams)、[consumer configuration](https://docs.nats.io/nats-concepts/jetstream/consumers) |
| EBN04 | subject publish/subscribe 安全与流控。**Skill MUST** | 按账号/principal 限定发布与订阅 subject，限制通配符、JetStream `$JS.API` 管理 API 和 reply inbox；列 `MaxPayload`、consumer pending limits、pull batch/bytes/expiry、flow control/heartbeats、discard/retry 路径。对 permission-filtered subscription 做可观测性检查，避免无错误静默漏消息。 | [NATS authorization](https://docs.nats.io/learn/security/authorization)、[JetStream pull consumers](https://docs.nats.io/nats-concepts/jetstream/consumers#pull-consumers) |

## 交付矩阵（适用于各 broker）

下列条目都是设计门槛；标注**适用**或**不适用+原因**，不能跳过。

| 维度 | 交付内容 | 最少可复核用例 |
|---|---|---|
| 投递/确认 | send ack、持久保存、receive ack、业务提交、offset/checkpoint 对照；attempt 与 stable message/event ID；结果未知处理。 | ACK 丢失、consumer 在提交前/后崩溃、重复消息。 |
| retry/poison | transient/permanent 分类、上限/时限、指数退避+jitter、max delivery、park/DLQ、报警和人工修复/再投；retry storm 限速。 | 瞬态恢复、毒消息耗尽、DLQ 再投不循环。 |
| ordering/event-time | key、partition/subject/queue/session scope、sequence/version；event time 和 processing time 区分、迟到 watermark/window/update policy（只有事件时间窗口时适用）。 | 同 key 乱序、duplicate、gap、迟到超过窗口。 |
| replay/offset | 保留/过期、offset/cursor owner/commit boundary、consumer group 生命周期、replay authorization、side-effect guard 和重建说明。 | 从边界 offset 回放，超出 retention 后恢复。 |
| transaction/outbox | DB commit 到 publish 的双写原子性；outbox relay lease/checkpoint/idempotency；inbox 与副作用同事务；目标资源参与事务证明。 | DB commit 成功而 publish 失败、重发同 outbox row。 |
| batch/compress | 批次原子性/部分结果、batch size/count/window、codec negotiation、compressed/uncompressed limits、memory/decompression cap。 | 单项拒绝、超大解压体、不支持 codec。 |
| routing/security | topic/queue/subject/filter、tenant binding、最小 publish/subscribe/admin/schema/DLQ 权限、credential rotation。 | unauthorized publish/subscribe/admin、错误路由、跨租户读写。 |
| observability | publish accepted/failed、consumer lag/oldest age、retry count、DLQ count、replay offset、schema rejects；ID 关联；payload/secret log minimization。 | 掉权限、schema reject、积压和 DLQ 告警路径。 |

**恰好一次边界**：先圈出原子单元。Kafka Kafka→Kafka 可用其事务关联 offset+output；AMQP transaction 只 cover participating links/resources；MQTT QoS、JetStream ack/dedup、进程内去重均不能让任意外部数据库/支付 API 原子化。若外部副作用没有与 inbox/checkpoint 共同原子边界，合同必须承诺 at-least-once/retry + idempotent effect 或说明人工 reconciliation，不称端到端 exactly-once。
