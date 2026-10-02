# Webhook 双边契约样例

这里有两份相互独立的契约：GitHub receiver 必须遵守 GitHub 官方定义；自有 provider 示例参考 Standard Webhooks 1.0.0。后者明确标为 “inspired”，不暗示 GitHub、Stripe 或其他供应商遵守该格式。

## GitHub 接收方

GitHub 官方规则用 `X-Hub-Signature-256` 的 HMAC-SHA256 校验发送的 payload 内容。验签输入是请求原始 body 字节；比较必须使用恒定时间算法。官方公开 [secret/payload/signature 向量](github-hmac-vector.json)供脚本直接核对，篡改 body、改变空白/字节、缺失或不匹配的签名均应失败。

`X-GitHub-Delivery`、`X-GitHub-Event` 不在 GitHub 公布的 HMAC 输入内。因此 body HMAC 验证本身**不认证这些头**，更不能只凭这些头做授权。Delivery ID 可作为 GitHub 提供的投递追踪/去重提示；如果 threat model 要求密码学绑定它，需额外采用能覆盖该头的认证 profile，或基于签名 body 中的稳定事件身份做去重。记录该头被替换而签名仍成立的边界测试。接收业务应先验签，再解析 JSON，核对 event/action/schema，再以明确定义的持久确认点响应。GitHub 文档建议在 10 秒内返回 `2xx`，失败投递可人工 redeliver；具体重放仍会产生重复处理窗口。任何确认应和“已可靠接收”一致，不自动代表业务已完成。

## 自有提供方契约

[sender-contract.json](sender-contract.json) 定义了这次设计假设：稳定 event ID、每次 attempt 更新的 Unix timestamp、原始 JSON body，以及 `webhook-id.timestamp.body` 的 HMAC-SHA256 输入；头部身份字段和 body 均被签名。脚本使用固定 current/previous key 向量核对 `v1,<base64>` 签名格式，覆盖 body/id/timestamp 篡改、旧时间戳、信任 keyset 和 key rotation overlap。

该契约将 2xx 视作确认，3xx/不跟随 redirect、410 停用 endpoint、429 读取 `Retry-After`、5xx/超时/断连退避重试；限制为 8 次 / 72 小时，之后告警并提供人工 redelivery。业务需据实调整数值及响应码矩阵。Standard Webhooks 1.0.0 的签名和 header 约定是社区生态规范，不是 RFC 或服务商默认；本样例是签名 profile 的测试模型，不连接发送队列，不证明重试持久性、数据库原子去重或真实 delivery。

## 交付验证边界

运行 `node verify_events_webhooks.cjs <fixture-root>` 可证明：GitHub 发布的 HMAC 测试向量通过、原始 body 篡改失败、GitHub header 未被该 HMAC 覆盖、样例自有签名 profile 对关键修改给出预期结果，CloudEvents 样例符合官方格式 schema 且 payload 旧消费者兼容案例可执行。它不执行 HTTP 服务，不证明 TLS/proxy 配置、持久化原子性、真实供应商消息、发送时序或端到端 retry；这些需要独立集成验证。

权威资料：[GitHub 验签文档和测试向量](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)、[GitHub 投递最佳实践](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks)、[Stripe 签名验证](https://docs.stripe.com/webhooks/signature)、[RFC 9421](https://www.rfc-editor.org/rfc/rfc9421.html)、[Standard Webhooks 1.0.0 社区规范](https://github.com/standard-webhooks/standard-webhooks/blob/main/spec/standard-webhooks.md)。
