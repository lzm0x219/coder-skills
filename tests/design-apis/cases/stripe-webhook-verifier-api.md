# SDK API 设计测试：Stripe Webhook 验签

状态：**可供设计评审，尚未获设计接受**；仅为 [design-apis](../../../skills/design-apis/SKILL.md) 的设计测试。主契约是[候选公开声明](stripe-webhook-verifier.api.ts)，[消费者调用](stripe-webhook-verifier.usage.ts)展示接收及失败路径；两者通过 TypeScript 5.6.3 严格静态检查。消费者从候选文件导入，未来包入口尚未设计或验证。没有实现、使用真实密钥或发送请求。依据为 [Stripe Webhook 文档](https://docs.stripe.com/webhooks)与 [Event 对象文档](https://docs.stripe.com/api/events/object)。范围限定为**接收 Stripe snapshot event** 的本地验签和基本信封解析，不包括 thin event、HTTP server、持久队列、业务处理或去重存储。

## 范围与中性模型

E1 是 HTTP 收到的原始请求体字节和 `Stripe-Signature` 头；E2 是一组当前有效的 endpoint signing secret；E3 是通过签名、时间窗口及信封校验的事件；E4 是调用方持久记录的事件处理状态。E3 不意味着 E4 已去重、入队或完成业务处理。Stripe 重试同一 Event 时会重新生成签名和时间戳，事件可能重复、乱序；密钥轮换可有重叠有效期。`api_version` 表示事件数据创建时使用的 API 版本，不能等同于当前 SDK 版本。

## 命名准入

| 候选 | 结论 |
| --- | --- |
| `webhookVerifier` / `webhookProcessor` | 选 `webhookVerifier`：本层只认证并解析，不执行业务；`processor` 会误导调用方把返回值当作处理完成。 |
| `verify` / `parse` | 选 `verify`：成功结果的核心保证是签名和时间窗口通过；`parse` 不足以表达认证语义。 |
| `VerifiedSnapshotEvent` / `StripeEvent` | 选前者：限定 snapshot 格式，并强调信封经验证；`data.object` 仍为 `unknown`，不承诺业务对象已类型检查。 |
| `eventId` / `deliveryId` | 使用事件的 `id`；本层不虚构 Stripe 未提供的独立投递尝试 ID。签名时间戳也不是去重键。 |

## 拟议公共契约

公开形状以 [stripe-webhook-verifier.api.ts](stripe-webhook-verifier.api.ts) 为准，包含 `createWebhookVerifier`、`WebhookVerifier`、`VerifyInput`、`VerifiedSnapshotEvent` 和 `VerifyError`。这些声明只表达候选 API 的类型与签名；下列段落表达验签顺序、密钥范围与处理责任。

构造时验证配置并复制密钥列表；空列表、空密钥、非正容差或非正大小上限抛 `invalid_config`。调用方只提供**同一 endpoint、同一 test/live 环境**的有效密钥；轮换时用包含新旧有效密钥的新 verifier 替换旧实例，不能混入其他 endpoint 的密钥。旧实例不自动读取环境变量或配置文件。实例可并发复用，没有网络、自动重试、`close()` 或凭据刷新。密钥属于调用方配置；本层不记录或返回密钥。`nowSeconds` 必须是有限的 Unix 秒数，生产代码不应传不可信请求时间作为当前时间。Stripe 当前 `v1` 签名以 `t` 的十进制字符串、一个 ASCII 句点和原始 body 字节顺序拼接为输入，用 endpoint secret 计算 HMAC-SHA256，并以常量时间比较候选签名；忽略 `v0`。实现应优先复用 Stripe 官方库的验签能力；若目标版本不能满足本提案的多密钥或时钟注入需求，需要核验版本并调整实现或契约，不能假定现成支持。

`verify` 只接受原始字节，不接受已解析 JSON 或重新序列化的字符串。先检查字节数；再校验头格式、任一有效密钥的 HMAC 和时间窗口；**仅在通过认证后**解析 UTF-8 JSON 与 snapshot event 的最低限度信封字段。大小超过上限为 `payload_too_large`；头缺失、格式错误或全部密钥不匹配为 `invalid_signature`；签名有效但时间超出窗口为 `timestamp_out_of_range`；签名有效但 JSON 或必要信封字段无效为 `invalid_payload`；信封的 `livemode` 与 `expectedLivemode` 不符为 `unexpected_mode`。若多个问题同时出现，按“大小 → 签名 → 时间 → 载荷 → 模式”判定。错误不附带原始 body、签名头或密钥。`verify` 不修改输入，无可见副作用；同一字节、头、密钥和 `nowSeconds` 下结果确定。

成功结果保留 `id`、`type`、`created`、`apiVersion` 和 `livemode`；未知 `type` 合法，`data.object` 保持 `unknown`，由调用方根据 `type` 与 `apiVersion` 再做版本化解码。成功只证明请求在允许时间内由某个配置的 endpoint secret 签署；同一有效请求在容差窗口内仍可能重放。事件 ID 的持久去重、业务对象级去重、乱序处理和回应 Stripe 的 HTTP 状态由接收方负责。`apiVersion: null` 不被擅自当作当前版本。

## 调用点走查

[stripe-webhook-verifier.usage.ts](stripe-webhook-verifier.usage.ts) 从候选声明导入，展示签名头缺失、验签失败、重复事件与持久入队失败的调用方处理。`PersistOnce` 和 `Respond` 是示例应用的边界，不属于 SDK。生产 handler 必须先限制请求体读取量，再把原始字节传入 `verify`；框架若先变更 body，验签可能失败。示例的 1 MiB 是应用配置值，不是 Stripe 通用上限。HTTP 状态码是此示例 handler 的决策，不是 verifier 的返回值。事件 ID 去重保留期需覆盖应用允许的重发／人工补发范围；签名时间戳因重试会变化，不能作为去重键。一个底层业务对象可能产生不同 Event，必要时再按对象 ID 与事件类型制定业务幂等键。

## 设计测试结论与未决

| 检查点 | 结果 |
| --- | --- |
| D01、D05、D07 | 把“认证通过”和“业务完成”分开；`verify` 不冒充处理或去重。 |
| W01、W02、W08 | 纯本地实例的密钥、轮换、错误优先级和并发使用有明确边界。 |
| Webhook 接收规则 | 原始字节、签名时间窗、重叠密钥、重复乱序及可靠接收点均有调用方路径。 |
| 类型边界 | 未知事件类型与 `apiVersion` 被保留，`data.object` 不伪装成已验证业务类型。 |

静态检查只证明候选类型与消费者调用相容；这是契约走查结果，**不是**密码学实现通过声明。实现前仍需用 Stripe 官方测试向量和真实框架的原始 body 行为，验证签名格式、常量时间比较、密钥轮换、时钟偏差和异常优先级；去重与持久入队也需单独验证。
