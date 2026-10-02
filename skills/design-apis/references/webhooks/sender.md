# Webhook sender contract

本页扩充 [WH01–WH03、WH07–WH09](../webhooks.md)，用于自建发送端。GitHub/Stripe 等 vendor sender 必须另走 [profiles.md](profiles.md)。

| ID | 条件、强度 | 规则与失败/恢复 | 证据和来源 |
|---|---|---|---|
| WS01 | 接受业务变更并排队发事件。**Skill MUST** | 定义源业务事务和 enqueue 的原子边界。若 DB commit 与网络 publish 不同原子系统，描述 transactional outbox、CDC 或可校准补偿；publisher lease/claim/mark-sent 崩溃后重复发布要由稳定 event/delivery ID + receiver 幂等吸收。 | outbox 记录 schema、双写故障矩阵和实际 DB/broker transaction proof；纯模型只能证明状态流程。 |
| WS02 | 发起一次投递。**Skill MUST** | 把 immutable event/delivery payload 与 attempt 分开：event ID 在重试/人工 redelivery 是否稳定；delivery ID 是每订阅还是每事件；attempt number 单调，started/completed time、签名 timestamp 每次如何变化。签名 id 字段须和 receiver 去重 key 定义一致。 | event→subscription→delivery→attempt ER/state diagram、重复/新订阅案例。 |
| WS03 | HTTP response 控制 retry。**Skill MUST** | 定义 ACK point（仅 durable intake 还是业务完成）。状态码、timeout、TLS/DNS/connect/reset/read failure、redirect、response body/headers 都纳入矩阵；区分可重试、配置永久错、auth、rate-limit。只有采用的 sender profile 才能规定固定 code；未知 code 默认策略也明确。 | response matrix 有每条 retry/terminal/disable 动作及原因；RFC 9110 成功类不是 webhook universal ACK。 |
| WS04 | retry policy。**Skill MUST** | 必填参数：attempt cap 或 retry horizon（可只择一但要推导另一）、初始/上限 delay、指数公式、jitter 算法/比例、`Retry-After` 处理、全局及 endpoint concurrency/rate budget、过期时间、终止原因、人工 redelivery。缺少任何业务值时用 `TBD + owner + measurement`，候选值不能伪装行业常数。 | 可运行时间线：间歇失败、长 429、结果未知、耗尽与人工恢复；provider service limits 引用版本。 |
| WS05 | 允许编辑 destination。**Security MUST** | 每一次 redirect hop 拒绝或完整重做 URL/IP/TLS policy；不转发 Authorization/cookies 到不同 origin；tenant secret 不放 URL；对 endpoint 做 SSRF/egress policy、请求/响应 bytes/timeouts、redirect and retry storm 上限。 | [OWASP API7:2023](https://api-security.owasp.org/editions/2023/en/0xa7-server-side-request-forgery/)，[OWASP SSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)。 |
| WS06 | delivery 可能超时而接收方已完成。**Skill MUST** | 将网络 outcome 标为 unknown 并可重试同一稳定 delivery/event identity；不能把 transport timeout 记录成确定失败/成功。receiver 通过 durable idempotency record 回复约定 ACK；sender receipt 必须记 `outcome unknown/retry pending` 并展示 attempts。 | kill-after-receive-before-response 模型、相同稳定 ID 重发案例、实际 inbox DB transaction 验证。 |
| WS07 | 签名发送。**协议/profile MUST** | 选 GitHub-style HMAC、Standard Webhooks、RFC 9421 或自有 profile 并固定算法/编码/key ID/trust/audience/covered bytes；body 签名需保留 bytes。轮换期间可并列新旧签名并定义验证次序/退役时点；事件 ID、delivery ID、timestamp 究竟绑定哪一个须一致。 | 使用官方向量/双方语言交叉向量；见 [signatures.md](signatures.md)。 |
| WS08 | batch、压缩、大 payload。**Skill MUST** | 定义是否每事件一 request；若 batch，批内逐条结果、原子性、部分重试、各 item identity 与整体 request id 明确。定义 media type/content encoding、body 签名是在压缩前还是传输后、receiver 解压 bytes 限制和事件顺序。大于限制时拆分/外部引用需授权和过期策略。 | 最大 raw/compressed/decompressed size 有 owner 与服务商来源；超限前后边界测试。 |
| WS09 | sender 可查询投递结果。**Skill MUST** | delivery resource 区分 queued、attempting、retrying、succeeded、terminal failed、expired、manually replayed；attempt resource 保存 HTTP status/classified reason、latency、request id、endpoint version，不回显 secret/body 默认脱敏。`succeeded` 意义按 ACK contract 定义，不谎称业务完成。 | GET/list contract 用分页/过滤、tenant ownership、retention 和 polling 不触发重发用例验证。 |
| WS10 | 监控与运维。**Skill MUST** | 暴露 publish accepted/failure、queue age/depth、delivery latency、attempt count、terminal failure、endpoint disabled、retry backlog、DLQ/replay；trace/correlation IDs 不含签名 key / secret /敏感 payload。告警含 owner、runbook、重放权限/审批和 rate cap。 | metric definition 与 on-call recovery procedure；采集实现可另阶段验收。 |

## Sender 状态拆分

`event` 描述业务事实；`delivery` 是该事件面向一个 endpoint/subscription 的逻辑工作项；`attempt` 是一次网络尝试；`receipt` 是 sender 对当前结果的持久记录。这些 ID 的生命周期必须分别写清。TLS 建连成功、HTTP 2xx、队列 ACK、durable receiver intake 和业务完成是不同里程碑。
