# FileFlow SDK API 设计演练

状态：**草案 / 待验证，未实现、未发布**；`jobs` 与 `extractions` 的命名取舍尚未完成。这是用于检验 `design-apis` 的虚构服务，以下服务能力均为测试假设，不代表已有后端承诺。公开类型草案见 [fileflow-sdk.api.ts](fileflow-sdk.api.ts)，可类型检查的调用点见 [fileflow-sdk.usage.ts](fileflow-sdk.usage.ts)。

## 目标与边界

- 调用者：在 Node.js 24 中使用 TypeScript 5.6 及以上版本的服务端开发者；拟议包入口为 `@example/fileflow`，使用 ESM。最低 TypeScript 版本是本提案的支持决策，发布前仍须用真实安装包验证。
- 任务：上传一份 PDF 或文本文件，启动文本提取任务，等待或稍后恢复查询，并流式下载结果；另可按页查看历史任务。
- 此轮只设计 **TypeScript 程序接口**。底层 HTTP 路径、消息格式和鉴权协议应另立契约；没有后端时不得把下面的假设写成已验证事实。
- 公共表面拟包含客户端、文件与处理记录操作、输入与结果类型、ID 解析函数和错误类型；名称见下文走查。没有继承点、插件系统、自动全量收集或浏览器构建。提案获批并发布 v1 后才承诺稳定。

## 演练输入：服务行为与概念模型

以下是为了演练而预设的行为，不是已验证的服务事实。先以中性代号区分：**处理记录 E1** 有独立 ID、状态、取消和失败信息；一次源文件可以发起多个 E1，同一幂等键的重试指向原 E1。**文件 E2** 有独立 ID 和保留期限，成功后的文本以 E2 提供。现有输入没有给出真实调用方对 E1 使用的英文名，也没有说明既有服务契约把 E1 称为什么。

| 能力 | 本次设计所依赖的服务行为 |
| --- | --- |
| 文件 | 接受 `application/pdf`、`text/plain`，单份 1..16 MiB；上传和生成文件均保留 7 天，并返回 `expiresAt`。文本提取结果是 UTF-8 文本文件。 |
| 重复请求 | 文件上传和发起处理都接受幂等键，服务保存 24 小时；同键同请求返回同一资源，同键不同请求返回冲突。重复请求不得重复处理或计费。 |
| 处理记录 | 不同的逻辑启动可针对同一源文件创建多个 E1；同一幂等键的重试返回原 E1。v1 仅执行文本提取；可查询 E1 状态，终态后的记录保留 7 天。远端取消是尽力请求，可与完成竞争，重复请求安全；状态含未知未来值。输出 E2 有独立 ID 和保留期限。 |
| 列表 | 服务提供按创建时间倒序、再按 ID 倒序的快照分页；继续令牌绑定过滤条件，1 小时内可跨进程继续，新任务不进入旧快照。 |
| 诊断与节流 | 每个成功响应含请求标识；部分响应含剩余额度，限流响应可能含建议等待时间。 |
| 版本 | SDK 固定使用服务稳定版 `2026-01-01`；本轮没有预览服务版本，也没有调用方版本选择入口。此版本只返回文本提取类处理记录；新增处理种类需要新服务版本。 |

任何一项无法由后端兑现，都需要先修改相应公开契约，尤其是幂等重试、分页恢复与取消语义。

## 命名走查

按[命名规范](../../../skills/design-apis/references/library-sdk/naming.md)对上述中性模型比较候选。E1 的 ID 与 E2 分开，只能证明处理记录与输出文件是两个概念，不能单独排除 `Extraction` 作为 E1 的领域名称。

| 候选名 | 需要补足的术语依据 | 当前结论 |
| --- | --- | --- |
| `jobs` | 服务公开契约或目标调用者把 E1 视为一次处理任务。 | 与模型相容；尚无独立术语证据。 |
| `extractions` | 服务公开契约或目标调用者把 E1 视为一次文本提取请求。 | 也与模型相容；尚无独立术语证据。 |

**命名评审：未通过，`jobs` 仅为可类型检查的暂定草案。** 发布前须核对真实服务契约、调用方用语及同产品已有 SDK；证据仍无法区分时，把 `jobs`/`extractions` 作为明确的产品设计取舍记录，不能宣称任一名称由行业规范唯一推出。暂用 `jobs.startTextExtraction` 表明动作。`FileRecord` 改为表示远端资源的 `StoredFile`；`name` 改为明确的 `filename`；分页过滤条件与模型统一用 `state`。`waitForCompletion` 表示等待终态，`openDownload` 表示取得尚需消费并关闭的流句柄。`listPage` 保留，因为该操作只发一次请求并返回一页。

## 正常调用点

```ts
import { FileFlowClient } from "@example/fileflow";

async function extractText(
  pdf: Uint8Array,
  uploadKey: string,
  startKey: string,
  currentToken: () => Promise<string>,
  writeOutput: (chunk: Uint8Array) => Promise<void>,
) {
  const client = new FileFlowClient({
    endpoint: "https://api.fileflow.example",
    credential: { getToken: () => currentToken() },
  });

  const uploaded = await client.files.upload({
    filename: "report.pdf",
    mediaType: "application/pdf",
    bytes: pdf,
    idempotencyKey: uploadKey,
  });
  const started = await client.jobs.startTextExtraction({
    sourceFileId: uploaded.data.id,
    idempotencyKey: startKey,
  });
  const finished = await client.jobs.waitForCompletion(started.data.id, { timeoutMs: 120_000 });

  if (finished.data.state === "failed") throw new Error(finished.data.failure.message);
  if (finished.data.state === "cancelled") throw new Error("任务已取消");

  const response = await client.files.openDownload(finished.data.outputFileId);
  let transferFailed = false;
  let transferError: unknown;
  try {
    for await (const chunk of response.data.chunks) await writeOutput(chunk);
  } catch (error) {
    transferFailed = true;
    transferError = error;
  }
  try {
    await response.data.close();
  } catch (closeError) {
    if (transferFailed) throw new AggregateError([transferError, closeError], "传输与关闭均失败");
    throw closeError;
  }
  if (transferFailed) throw transferError;
  return { jobId: finished.data.id, requestId: finished.meta.requestId };
}
```

调用方应在调用本函数**之前**生成并持久化 `uploadKey` 和 `startKey`，直到各自操作结果确定；未知结果后的补偿重试必须使用相同输入和原键。上传恢复还需要保留原文件字节。`writeOutput` 应对部分写入自行回滚或覆盖。

## 失败与恢复调用点

```ts
import { FileFlowError } from "@example/fileflow";

const startInput = {
  sourceFileId: uploaded.data.id,
  idempotencyKey: savedKey,
};

try {
  await client.jobs.startTextExtraction(startInput);
} catch (error) {
  if (error instanceof FileFlowError && error.code === "outcome_unknown") {
    // 24 小时去重窗口内，用相同输入和相同键再次调用；服务返回原任务。
    const recovered = await client.jobs.startTextExtraction(startInput);
    persistJobId(recovered.data.id);
  } else {
    throw error;
  }
}
```

恢复示例假设 `uploaded`、`client`、`savedKey` 和 `persistJobId` 来自调用方上下文。若已超过 24 小时窗口，SDK 不承诺重复调用安全；调用方需人工核对服务端资源或接受结果未知。

## 操作契约

| 操作 | 前置条件、结果与副作用 | 关键失败与成本 |
| --- | --- | --- |
| `files.upload` | `filename` 为 1..255 个 UTF-8 字节；`bytes` 为 1..16 MiB；`idempotencyKey` 为 1..128 个可打印 ASCII 字符。SDK 调用时复制字节，之后调用方可修改原数组。成功返回 `StoredFile`。 | 创建远端文件，可能计费；本地非法输入在发请求前拒绝。响应丢失时可能已创建，按原键重试。复制最多额外占用 16 MiB。 |
| `files.openDownload` | 文件存在且未过期；成功返回文件元数据和单次消费的 `chunks`。 | 建立一次网络流，读取中可失败并留下部分输出；交付首字节后不自动重试。迭代完成、提前退出或失败后均由调用方调用 `close()`；传输与关闭同时失败时保留两项错误。 |
| `jobs.startTextExtraction` | 源文件存在且类型可处理；`idempotencyKey` 满足同上约束。成功返回任务，可能已处于任一已知状态。 | 创建远端任务，可能计费；未知结果按原键重试；不同输入复用键为 `conflict`。 |
| `jobs.get` | 接受 `JobId`；每次调用都发网络请求，返回包括未来未知状态在内的任务快照。 | 不存在或无权查看均可为 `not_found`；明确的操作权限拒绝为 `permission_denied`。 |
| `jobs.waitForCompletion` | 轮询直到 `succeeded`、`failed` 或 `cancelled`，返回 `TerminalJob`；任务失败作为数据返回。 | 默认本地等待 60 秒；超时或 `AbortSignal` 仅停止本地等待，远端任务继续。未知服务状态抛 `unsupported_service_state`，可用 `get` 查看原状态。 |
| `jobs.cancel` | 向远端请求取消，返回服务此刻报告的状态；调用方应再 `get` 或 `waitForCompletion` 判定最终结果。 | 可能与任务完成竞争，成功响应也不保证最终为 `cancelled`。只有此操作请求远端取消。 |
| `jobs.listPage` | `pageSize` 默认 50，范围 1..200；每次调用取一页，`nextCursor` 缺失表示结束。 | 令牌不透明且绑定状态过滤条件；过期或错配为 `invalid_input`，不得静默从第一页重来。无自动全量收集。 |

`parseFileId` 和 `parseJobId` 将持久化字符串恢复为不同的 ID 类型；仅检查服务承诺的 `file_` / `job_` 前缀与非空主体，不解析主体含义。构造器验证 HTTPS 端点、凭据提供者和数值配置；失败时同步抛 `FileFlowError(invalid_input)`。其余异步方法统一以 Promise rejection 报告请求级失败。可选字段用缺失表示未提供，公开结果不以 `null` 混用未知和缺失。时间字段为 RFC 3339 UTC 字符串。

## 客户端、凭据与并发

- `endpoint` 和 `credential` 必须显式提供；SDK 不读取环境变量、配置文件或全局单例，因此没有隐含优先级。构造后配置为快照，不支持原地修改。
- 每次尝试开始时调用 `credential.getToken`。刷新、缓存与轮换由提供者负责；下一次尝试即可取得新凭据。提供者须可并发调用。SDK 向提供者传入同时受调用方取消和尝试超时控制的 `signal`。请求发出前若调用方取消，SDK 立即停止等待并报告 `aborted`；若尝试或总预算先耗尽，则报告 `credential_unavailable`。即使提供者忽略 `signal`，SDK 也按预算停止等待，忽略迟到的令牌或失败，绝不在此后发请求。提供者自身失败且未取消时同样报告 `credential_unavailable`；发送前已发生的调用方取消优先于凭据失败或超时。
- `FileFlowClient` 无后台线程或自有持久连接，可并发复用，无需 `close()`。替代 `fetch` 由调用方持有并可看到凭据，只应传入可信实现；默认使用 Node.js 的 `fetch`。下载句柄由调用方显式关闭：迭代完成、提前退出或失败都不免除 `close()` 责任。`close()` 在首次调用时开始一次清理；并发或后续调用复用同一次关闭结果，清理失败时均拒绝且不重复清理。关闭开始后的读取以 `download_closed` 失败；关闭失败通过 `close()` 的 Promise rejection 报告。消费与关闭同时失败时，示例使用 `AggregateError` 保留两项原因。
- 对上传/下载/任务调用，`signal` 取消本地请求。发送前取消为 `aborted`，包括取凭据期间；在上传、启动或远端取消请求已发送后中止可能是 `outcome_unknown`。上传/启动可在去重窗口内按原键恢复，取消后应查询任务状态。`jobs.waitForCompletion` 的中止始终只停止轮询；远端取消必须调用 `jobs.cancel`。

## 重试、错误与元数据

- 默认 `maxAttempts=3`，**包含首次请求**；单次尝试默认超时 10 秒，单次服务调用的重试预算默认 20 秒。配置范围：尝试 1..5、单次超时 1..60 秒、总预算 1..120 秒。尝试预算从取凭据开始，到收到普通响应或下载流句柄结束；总预算包含各次取凭据、网络请求和退避。下载句柄交付后的流消费不计入尝试预算，由调用方的 `signal` 和 `close()` 控制。`jobs.waitForCompletion` 每次轮询分别计算重试预算，同时受 `WaitOptions.timeoutMs` 的整体等待预算约束，该整体预算也包含取凭据时间。等待采用 200 毫秒起、2 秒封顶的指数随机退避；服务建议等待时间优先，但超过剩余预算时不再重试。
- 仅对 `rate_limited`、`service_unavailable` 和可恢复传输失败自动重试。读取操作可重试；`upload` 与 `start` 仅在服务保证幂等且**同一次逻辑操作的所有尝试复用同一键**时重试；`cancel` 仅在服务保证重复请求安全时重试；`download` 在开始交付流后不重试。`invalid_input`、鉴权/权限错误、`conflict` 和任务处理失败不自动重试。
- `FileFlowError.code` 是稳定处理分支；`message` 仅供人阅读。远端任务的 `failed` 状态通过 `JobFailure` 返回，不混作传输异常。请求标识在已收到服务响应时提供；未收到响应时可缺失。`rate_limited` 可附 `retryAfterMs`。未知服务状态和任务失败码保留原值，不使旧 SDK 在解析时崩溃。
- 成功调用返回 `ApiResponse<T>`，其中 `data` 是类型化结果，`meta.requestId` 可用于诊断，`rateLimitRemaining` 仅在服务提供时出现。`jobs.waitForCompletion` 返回最后一次成功轮询的响应元数据，`listPage` 返回本页的响应元数据。SDK 不在默认日志、错误消息或调试表示中输出令牌、文件内容和文件名；公开 API 不暴露原始 HTTP 响应对象。

## 分页与长任务的恢复边界

调用方可以保存 `nextCursor`，在 1 小时内用相同的 `state` 过滤条件跨进程继续 `listPage`。旧快照中的排序固定，新建任务需从新列表查询；不得依赖全局实时顺序。每页网络失败由本次 `listPage` 的 Promise 拒绝表示，已取得的页保持有效；可用同一令牌重试当前页。

```ts
const page = await client.jobs.listPage({ state: "failed", pageSize: 50, cursor: savedCursor });
await persistItems(page.data.items);
await saveCursor(page.data.nextCursor); // 缺失表示列表结束
```

调用方可以持久化 `JobId`，稍后用 `jobs.get` 或 `jobs.waitForCompletion` 恢复观察，无须保存 SDK 对象。`waitForCompletion` 采用服务建议轮询间隔；无建议时每 1 秒轮询一次。`waitForCompletion` 的总预算包含轮询请求及其重试。远端 `cancel` 只是请求，不是同步终止承诺；`succeeded`、`failed`、`cancelled` 都是可观察终态。

## 版本与兼容

此提案没有已发布消费者，因此无需旧消费者兼容验收。拟议支持范围为 Node.js 24、TypeScript 5.6 及以上版本和 ESM；本轮仅对 TypeScript 5.6.3 的声明与调用点做类型检查，真实包的 ESM 导出和安装后导入仍待验证。拟议 v1 发布后，方法签名、错误代码、默认超时/重试、任务状态映射和文件保留语义均应作为可观察契约评审。SDK 版本与服务版本独立；本版只请求服务 `2026-01-01`，暂定 `Job.kind` 恒为 `text-extraction`，并以前述“同版不新增处理种类”为前提。遇到额外响应字段时忽略，未知状态或失败码映射到显式 `unknown` 分支。预览服务版本不通过隐藏开关启用。

## 设计测试与待核验事实

| 走查 | 预期可观察结果 | 对应规则 |
| --- | --- | --- |
| 同键同内容上传两次；同键不同内容再传 | 前两次同一 `FileId`，第三次 `conflict` | W03、J02 |
| 启动请求响应丢失后按原键重试 | 仅一个 `JobId`，无重复计费 | W03、W02 |
| `waitForCompletion` 中止后读取任务，再显式 `cancel` | 中止不改变远端状态；取消结果需再次观察 | W07、N02 |
| 保存分页令牌并在新进程继续；令牌过期 | 旧快照继续；过期显式失败 | W04、O02 |
| 下载到一半停止迭代或网络断开后调用 `close()` | 资源关闭；网络断开报告错误且不隐藏部分输出 | W04、I01、I02 |
| 传输或写入失败且 `close()` 也失败 | `AggregateError` 同时保留原失败与关闭失败 | I02、J04 |
| 流完成后两个调用方并发调用 `close()`，首次清理失败 | 只执行一次清理；两个调用均收到同一次失败 | I02、N03 |
| 凭据提供者轮换令牌，并发调用 | 后续尝试取新令牌；无凭据泄漏 | W08、N03、U03 |
| 取凭据期间 `signal` 取消，同时提供者失败或迟到成功 | `aborted`，不发送请求；提供者独立失败且未取消才是 `credential_unavailable` | N02、W02、W08 |
| `getToken` 长期不返回且调用方未提供 `signal` | 在尝试或总预算到期时返回 `credential_unavailable`；迟到令牌不能触发请求 | W03、W08、N02 |
| 服务增加未知任务状态 | `get` 返回 `unknown`；`waitForCompletion` 明确失败 | W06、E02 |

这些是**拟议验收用例，尚未运行**。实施前须向后端核验：幂等键 24 小时窗口及计费语义、快照令牌寿命和跨进程能力、取消竞争结果、文件保留时间、请求标识与轮询等待提示。任一假设不成立，应先调整类型、重试策略和示例。

本设计把项目的 [程序接口规则](../../../skills/design-apis/references/library-sdk.md) 与远程 SDK 条件规则落实到具体调用。Node.js 24 的运行时选择参考 [Node.js 官方版本表](https://nodejs.org/en/about/previous-releases)；`AbortSignal`、`fetch` 及流能力按 [Node.js 24 官方文档](https://nodejs.org/download/release/latest-v24.x/docs/api/globals.html) 使用。分页、长任务和重试设计分别参考 [Azure SDK 设计指南](https://azure.github.io/azure-sdk/general_design.html) 与 [AWS SDK 重试指南](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html)；具体数值和服务保证是本演练的选择，**不是**这些来源的通用规定。
