# SDK API 设计测试：S3 分段上传

状态：**可供设计评审，尚未获设计接受**；仅为 [design-apis](../../../skills/design-apis/SKILL.md) 的设计测试。主契约是[候选公开声明](s3-multipart-sdk.api.ts)，[消费者调用](s3-multipart-sdk.usage.ts)展示正常与失败路径；两者通过 TypeScript 5.6.3 的严格静态检查（临时检查环境使用 `@aws-sdk/client-s3@3.1142.0` 与 `@types/node@24`）。消费者从候选文件导入，未来包入口尚未设计或验证。没有实现、连接 AWS 或运行集成测试。依据为 [S3 分段上传流程](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)、[完成上传接口](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CompleteMultipartUpload.html)和[条件写入](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html)。

## 范围与中性模型

假设调用方已有配置好的 AWS SDK for JavaScript v3 `S3Client`。本层只封装**通用型、未启用版本控制的 bucket** 的 `CreateMultipartUpload`、`UploadPart`、`CompleteMultipartUpload` 和 `AbortMultipartUpload`；不提供目录 bucket、`UploadPartCopy`、对象元数据、自定义校验和算法或整个文件的自动切片。底层客户端的凭据、区域、端点、代理、请求超时、网络重试和关闭均由调用方配置与持有。本层不增加重试，也不关闭注入的客户端；调用方应清楚底层重试配置，不能据此提案推断网络请求恰好发送一次。

先不命名，列出对象：E1 是目标 `bucket` + `key`；E2 是由服务端 `uploadId` 标识、完成前可计费的暂存过程；E3 是一次成功上传某编号片段后获得的 `number` + 不透明 `ETag` 回执；E4 是完成后可访问的对象。E2 与 E4 的身份不同，E3 不是整个对象的校验和。S3 官方契约支持这些关系；本层的调用形态和安全默认值是设计决策。

## 命名准入

| 候选 | 结论 |
| --- | --- |
| `multipartUploads` / `uploadJobs` | 选 `multipartUploads`：前者对应 S3 已有 `MultipartUpload` 术语及 E2；`jobs` 会引入服务并未承诺的任务资源概念。 |
| `create` / `start` | 选 `create`：与 `CreateMultipartUpload` 对应，Promise 只表示取得 E2 的 `uploadId`，不表示对象已经上传。`start` 也可成立，但不增加信息。 |
| `uploadPart` / `put` | 选 `uploadPart`：调用点直接表明上传一个片段，成功结果是 E3。 |
| `complete` / `finish` | 选 `complete`：对应 S3 的显式提交操作；Promise 成功才表示 E4 已创建。 |
| `abort` / `cancel` | 选 `abort`：这是删除远端未完成上传的请求，不能与仅停止本地等待的 `AbortSignal` 混同。 |
| `fromCheckpoint` / `resume` | 选 `fromCheckpoint`：只恢复本地句柄和回执，不查询远端状态，不暗示自动补齐缺失片段。 |
| `createMultipartUploads` / `useMultipartUploads` | 选 `createMultipartUploads`：只构造本地包装层；TypeScript 中 `use...` 容易被读成 React Hook。它不等同于远端会话的 `uploads.create(...)`。 |

## 拟议公共契约

公开形状以 [s3-multipart-sdk.api.ts](s3-multipart-sdk.api.ts) 为准，包含 `MultipartUploads`、`MultipartUploadSession`、`UploadCheckpoint`、`PartReceipt`、`CompletedObject`、`UploadError` 与 `createMultipartUploads(s3)`。这些声明仅表达候选 API 的类型与签名；下列段落表达类型无法单独保证的运行行为。

`createMultipartUploads` 不持有 `s3` 的关闭权；同一实例可并发处理不同上传。`create` 至少要求非空 `bucket`、非空 `key`，服务端最终验证名称、权限和区域；结果是尚未产生对象的 E2。`fromCheckpoint` 只验证形状与 E3 的 `uploadId` 一致性，不证明远端仍存在。公开接口不读取环境变量或配置文件，也不覆盖底层 `S3Client` 配置；服务版本随调用方提供的 S3 客户端及服务端演进，本层不提供独立的版本选择。

`uploadPart` 要求会话仍可写、编号 1..10_000、非空字节；同一会话同一编号的并发调用本地拒绝为 `part_in_flight`，不同编号可并发。调用期间借用 `bytes`，Promise settle 前调用方不得修改。成功后用新回执替换该编号旧回执，并返回 E3；覆盖同编号远端片段是可见副作用。调用方必须把最新 `checkpoint()` **原子持久化**，否则进程崩溃后需用原字节重传未记录的片段。响应丢失时抛 `outcome_unknown`，该编号回执未知；只在持有相同原字节且没有该编号并发写入时，调用方可重传该编号并采用新的回执。不能用 `ListParts` 的输出构造 `complete` 输入。`fromCheckpoint` 不加跨进程锁；同一 upload 不能由两个进程同时变更，协调由调用方负责。

`complete` 要求至少一个已确认的回执、没有进行中的 `uploadPart`，且按升序提交无重复编号；除最后一个片段外，每段至少 5 MiB。此调用进行期间禁止新的片段写入及并发 `complete`/`abort`。`overwrite: "forbid"` 在完成请求使用 `If-None-Match: *`，现有对象对应 `object_exists`（HTTP 412）；`overwrite: "allow"` 是明确的覆盖授权。条件完成遇 HTTP 409 时为 `completion_conflict`，该 upload 不继续重试完成，调用方需重新创建上传。注入的 AWS SDK 客户端必须完整接收并识别嵌入在 HTTP 200 中的 S3 错误；本层仅在客户端确认成功后返回 E4。成功后 E2 失效。对明确的 412，保留 `abort` 能力以清理片段；对 409，不允许在原 upload 上再 `complete`，仍应尝试清理。`InvalidPart` 映射 `invalid_part`，调用结束后允许调用方核对或重传片段；其他明确拒绝依错误类型决定修正片段后再完成或中止。`complete` 返回 `NoSuchUpload` 或结果未知时，因远端终态不能仅由该响应判定，冻结会话直到调用方核对远端状态。

`abort` 要求没有进行中的片段或完成请求；请求成功后 E2 不可再用。已开始但尚未完成的片段不能靠一次 abort 保证清理。`AbortSignal` 仅停止本地等待／请求，不等于远端已停止。任何远端操作在请求可能到达远端但未收到可判定结果时抛 `outcome_unknown`；此时不能把 E2 判作已完成或已清理，也不能盲目重复 `complete` 或 `abort`。`uploadPart` 结果未知时只允许前述同号原字节的受控重传；`complete`/`abort` 结果未知时应冻结会话并核对远端状态。保留 checkpoint、对象键和请求诊断信息；`NoSuchUpload` 单独不足以证明成功完成。

本层错误优先级：本地输入和会话状态错误先于网络；收到可解析的 S3 错误时优先映射明确拒绝（`object_exists`、`completion_conflict`、`invalid_part`、`permission_denied`、`remote_rejected`），但 `complete` 的 `NoSuchUpload` 映射 `outcome_unknown`；请求确定未发出才用 `transport_failure`，发送状态不明或提交响应不明用 `outcome_unknown`。错误不包含凭据、请求体或原始签名。`requestId` 仅作为可选诊断字段。S3 对已上传片段收费，生产使用应配置 bucket 生命周期规则清理长期未完成的上传。

## 调用点走查

[s3-multipart-sdk.usage.ts](s3-multipart-sdk.usage.ts) 从候选声明导入，先保存 `uploadId`，待并行片段全部 settle 后保存回执，再用显式覆盖策略完成。结果未知时交给调用方核对；明确失败时尝试清理并保留主错误与清理错误。`saveCheckpoint`、`flagForReconciliation` 等持久化与诊断函数均为调用方职责，不属于 SDK。若 `create` 本身结果未知且未取得 `uploadId`，调用方无法用本 API 定位孤儿上传，生命周期清理是必要的后备措施。若 `complete` 报 `object_exists`，应在无片段进行中时显式 `abort`，不能默认覆盖现有对象。`clearCheckpoint` 失败属于调用方本地清理错误，不能据此逆转已确认的远端完成。

## 设计测试结论与未决

| 检查点 | 结果 |
| --- | --- |
| D01、D05、D07 | 资源身份和完成阶段已区分；`abort` 与本地 `AbortSignal` 不混用。 |
| W01、W03、W08 | 客户端及凭据生命周期归调用方；本层不重试。底层 S3 客户端的具体重试和超时配置须在实际集成时核验。 |
| W02、W07、W09 | 回执、错误类别、未知结果及可选请求 ID 有调用方处理路径；没有声称 200 即成功。 |
| 关键失败 | 412 不覆盖、409 重新开始、完成结果未知进入人工／后台核对。 |

静态检查只证明候选类型与消费者调用相容；这是契约走查结果，**不是**可用 SDK 的测试通过声明。实现前仍需确认注入客户端的实际重试配置、校验和与签名行为，补充 `NoSuchUpload`、嵌入错误、跨进程并发和网络中断的服务端集成测试。
