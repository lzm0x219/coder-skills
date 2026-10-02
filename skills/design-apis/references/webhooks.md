# Webhook API 设计规则

Webhook 同时是 HTTP callback 和至少两方约定的 delivery profile。先识别自有 sender、自有 receiver、第三方 provider、用户可管理 subscription 哪些在 scope 内，再按条件读取分支 reference：

- 原有 WH01–WH11 规则身份和简述 → 下表
- subscription 创建、ownership、endpoint SSRF、pause/delete、delivery receipts → [lifecycle](webhooks/lifecycle.md)
- 自有 provider 发送、重试/receipt/batch/outbox → [sender](webhooks/sender.md)
- 自有 receiver 的 verify→parse→durable intake→ACK、幂等、迟到/毒事件 → [receiver](webhooks/receiver.md)
- raw bytes、HMAC/RFC9421、rotation、freshness/replay → [signatures](webhooks/signatures.md)
- GitHub / Stripe / Standard Webhooks-specific behavior → [profiles](webhooks/profiles.md)

## 原有规则索引

保留 WH01–WH11，避免丢失旧引用；细化的强度、条件、动作、恢复和证据以按需文件为准。

| ID | 规则范围 | 详细分支 |
|---|---|---|
| WH01 | parties、event/delivery/attempt ID、subscription contract | [lifecycle](webhooks/lifecycle.md)、[sender](webhooks/sender.md) |
| WH02–WH06 | exact signed input、profile-specific MAC/signature、freshness/rotation | [signatures](webhooks/signatures.md)、[profiles](webhooks/profiles.md) |
| WH07 | ACK/status-code、retry/backoff/termination | [sender](webhooks/sender.md)、[profiles](webhooks/profiles.md) |
| WH08 | verified → durable accepted → business processed 状态 | [receiver](webhooks/receiver.md) |
| WH09 | key/credential rotate/revoke | [signatures](webhooks/signatures.md)、[lifecycle](webhooks/lifecycle.md) |
| WH10 | user-supplied endpoint SSRF/egress/TLS/redirects | [lifecycle](webhooks/lifecycle.md)、[sender](webhooks/sender.md) |
| WH11 | unknown event/action/schema、untrusted routing header | [receiver](webhooks/receiver.md)、[profiles](webhooks/profiles.md) |

## 规则等级

表内 “协议 MUST” 仅在确切采用标准和版本时生效；“provider MUST” 仅约束对应提供方；“Skill MUST” 是本设计 Skill 的交付门槛，不是外部标准。社区 interoperability profile（如 Standard Webhooks）需注明 pinned version 和兼容性偏离。HTTP 2xx 不是通用 Webhook receipt；contract 必须指定其代表已入队、已接收或业务已完成的哪一个 durable milestone。

## 提交与验证

适用方向须交付 operation/API surface（当自有控制面 scope 内）、subscription state lifecycle、event schema/catalog、URL ownership + SSRF 边界、身份/签名组件表、attempt/delivery/event ID 语义、状态码与恢复矩阵、duplicate/out-of-order/poison policy、receipt 保留和告警。按 C06 记录各规则的证据或不适用原因；数值注明业务 owner/source，依赖外部事实的缺项保持未决，可由设计者决定的值按 C02 给出有界候选。

raw bytes / official vector / policy state simulation 仅证明合同样例或 verifier 对给定向量的局部行为；不证明互联网传输、签名 secret 落盘、订阅租户授权、durable database atomicity 或真实 provider redelivery。声明生产保证须提供其对应系统的集成和故障恢复证据。

既有固定检查：[GitHub receiver 与 self-owned sender](../../../tests/design-apis/cases/webhook-github/contract.md)。一手来源及研究推导：[事件与 Webhook 来源](sources.md#events-webhooks)。HTTP 的通用 method/status 规则见 [HTTP API](http.md)。
