# Webhook interoperability profiles

本页扩充 [WH03、WH05–WH07、WH11](../webhooks.md)。服务商行为有版本漂移，使用时检查当天的官方文档和 API version，并把检索日期/版本写入设计交付。下表不是统一标准。

## GitHub receiver

| 分支 | 适用规则与可执行动作 | 一手来源 |
|---|---|---|
| Signature | `X-Hub-Signature-256` 用 endpoint secret 对原始 payload HMAC-SHA256；常数时间比较。成功只证明 body 在共享 secret 下完整且来自持有者，不认证 `X-GitHub-Delivery`、`X-GitHub-Event` header。固定官方 `Hello, World!` vector。 | [Validate deliveries](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries) |
| Receiver ACK | 目标是 10 秒内 2XX；耗时工作放到先持久化的内部 queue 再响应。超时记为 sender failed，不能假定自动重投。 | [Best practices](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks) |
| Duplicate/order | `X-GitHub-Delivery` 对 redelivery 保留相同值，可作 delivery dedup key；它未被 body HMAC 覆盖。event header 决定类型、body `action` 再决定细分动作；未来新增 type/action 应安全忽略副作用并观测。事件可能乱序，按 resource revision/latest API reconcile。 | [Best practices](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks)、[Troubleshooting](https://docs.github.com/en/enterprise-cloud%40latest/webhooks/testing-and-troubleshooting-webhooks/troubleshooting-webhooks) |
| Recovery | GitHub 不自动 redeliver failed deliveries；支持人/程序通过 delivery API 对 past 3 days 的 delivery 发 redelivery 请求，需具有 webhook write/admin 权限。请求 API accepted 不代表 callback 已成功；检查 attempt receipt 并按相同 delivery ID 去重。 | [Handling failed deliveries](https://docs.github.com/en/enterprise-cloud%40latest/webhooks/using-webhooks/handling-failed-webhook-deliveries)、[Redelivering](https://docs.github.com/en/webhooks/testing-and-troubleshooting-webhooks/redelivering-webhooks)、[REST API](https://docs.github.com/en/rest/repos/webhooks#redeliver-a-delivery-for-a-repository-webhook) |
| Ownership/network | secret 置于受控 secret store；HTTPS/TLS 验证保持开启；IP allowlist 是需定期同步的附加边界，不代替 signature。只订阅所需 event types。 | [Best practices](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks) |

## Stripe receiver

| 分支 | 适用规则与动作 | 一手来源 |
|---|---|---|
| Signature | 用 Stripe 官方 verifier/endpoint signing secret 和未修改原始 body；若 body 已解析/变换会验签失败。不要将 test secret/API version 混入 live endpoint。每 endpoint 独立配置 signing secret。 | [Signature verification](https://docs.stripe.com/webhooks/signature)、[webhook endpoints](https://docs.stripe.com/webhooks) |
| ACK and retry | 返回 2xx 表示接收成功；快速 ACK，慢处理先异步入队。入队持久提交前不要 ACK。当前官方 retry 窗口详见下方 Operational recovery；这是 Stripe profile，不是自有 sender 参数。 | [Receive Stripe events](https://docs.stripe.com/webhooks) |
| Duplicate/reconcile | 同一 Event 可能重复；使用 `event.id` 幂等。不同 Event 也可能代表同一对象/事件语义；有必要时按 object ID + event type 做业务去重。Stripe 明确不保证顺序，`created` 以秒计可能相同，不得用作排序/去重；需要时 fetch canonical object。snapshot event 与 thin event 是不同 payload/destination profile，固定 endpoint API version 和 handler/SDK 支持范围。 | [Webhook delivery behaviors, API versioning, duplicate and ordering](https://docs.stripe.com/webhooks) |
| Operational recovery | 当前官方页面称 live automatic retries 最多 3 天 exponential backoff；sandbox 3 次/数小时。Dashboard resend 窗口 15 天，CLI resend 窗口 30 天；manual resend 成功不自动取消原 automatic retry schedule。禁用/删除 endpoint 时，发生 retry 检查会停止后续 retries；禁用后在下一 retry 前重新启用则仍会继续。收到重复时仍按 Event ID 幂等。 | [Webhook event delivery behaviors](https://docs.stripe.com/webhooks)；文档可能变化，使用时复核。 |
| Secret rotation | Endpoint 可轮换 signing secret；当前官方页面支持旧 secret 最长额外 active 24 小时并在窗口内为每个请求生成多个签名。receiver overlap 验证要采用官方 SDK/profile，不把 24h 当自有服务通用值。 | [Stripe best practices, rotate secrets](https://docs.stripe.com/webhooks) |
| HTTP response profile | Stripe 将 3xx 视为 delivery failure、不跟随 redirect；其他状态/timeout 按 Stripe 失败分类，不可泛化为自有 sender。接收端长期 URL 采用最终 URL，避免重定向。 | [Stripe webhook delivery behaviors](https://docs.stripe.com/webhooks) |

## Standard Webhooks v1.0.0 (community profile)

| 分支 | profile contract | 依据 |
|---|---|---|
| Headers/signature | `webhook-id`、`webhook-timestamp`、`webhook-signature`；HMAC v1 signing input 为 UTF-8 `id.timestamp.raw_payload`，secret 按其 encoding 解码。签名头可带多个版本 signature 以支持 overlap；constant-time compare。header value grammar 与 parser 完全跟 pinned version。 | [Spec §Webhook Message Headers, §Signature Scheme](https://github.com/standard-webhooks/standard-webhooks/blob/v1.0.0/spec/standard-webhooks.md) |
| Freshness/idempotency | 以 timestamp tolerance 拒绝 stale replay；以 `webhook-id` 持久去重。Tolerance 是 profile/config；样例中的 300 秒不能推广为所有服务商安全数值。timestamp 接受窗口和 dedup retention 应协调。 | 同上，§Security Considerations |
| Delivery behavior | sender 2xx success、3xx no automatic redirect、retry classification/backoff、delivery attempts/timeout/replay 按 v1.0.0 operational rules 实现。保存每次 attempt，manual redrive 不覆盖过去结果。 | 同上，§Sending Webhooks / §Best Practices |
| Compatibility | 发布兼容性承诺需明确 profile revision；不可只写 “Standard Webhooks compatible” 后另改 header grammar、timestamp tolerance、canonical bytes 或 status policy。社区 profile 不代替法律/行业标准。 | 以上为 Standard Webhooks project authored community spec；不是 IETF RFC。 |

## Profile 对比交付矩阵

| 项 | GitHub | Stripe | Standard Webhooks | 自建协议 |
|---|---|---|---|---|
| body signing | HMAC body bytes | 官方 signature verifier/raw body | ID + timestamp + body | 选成熟 profile / RFC9421 |
| header binding | delivery/event headers 不随 body HMAC 自动认证 | 依 Stripe verifier contract | ID/timestamp 纳入 signing input | 明列完整 signed components |
| duplicate key | delivery ID 在 redelivery 稳定；与 event identity区分 | Event ID；可追加 object semantic key | webhook-id | stable delivery/event ID |
| retry | GitHub 不自动重试；管理面 redelivery | Stripe 自动+手动 retries | 依据 pinned spec | 显式状态码和时间策略 |
| ACK | 2XX <10s | 2xx before slow work | profile response code | durable receiver intake ACK |
| source recovery | failed delivery dashboard/API, finite window | Dashboard/CLI/service | sender-specific API | receipt + redrive endpoint |

表内字段按服务商当前合同变更而变更；实际设计至少附入实际 endpoint API version、测试向量、当前状态码矩阵、retry/redelivery 权限和保留窗证据。
