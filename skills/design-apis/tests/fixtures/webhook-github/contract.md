# GitHub Webhook 接收契约样例

本项目是接收方，GitHub 是提供方。采用 GitHub 的 `POST` JSON 投递、`X-Hub-Signature-256` 和 `X-GitHub-Delivery`，不是自定这些头。[原始载荷](payload.json)与签名头一起输入验签；本地临时测试密钥仅在回归进程内创建。先对原始字节验证 HMAC-SHA256，再解析 JSON、按 delivery ID 去重并持久接收。签名缺失或错误返回 `401`；合法首次投递持久接收后返回 `202`；重复 delivery 不再产生第二次业务效果，返回 `200`。处理失败由接收方记录并补偿，不把“已接收”说成业务完成。

测试模型覆盖有效签名、载荷篡改、缺失签名和重复 delivery；它不证明 GitHub 实际发送或本地数据库已经保证原子去重。实际部署需核对密钥存储、轮换、队列持久化、处理时限和 GitHub 重投记录。GitHub 要求在 10 秒内返回 `2xx`；本样例设置本地 8 秒处理预算，超时前只在已持久接收时确认。依据：[GitHub 验签](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)、[最佳实践](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks)。
