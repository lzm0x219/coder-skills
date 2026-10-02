# 长任务、去重写入和分页 HTTP 契约

主契约是 [OpenAPI 3.1.1](openapi.json)，正反消费向量位于 [cases.json](cases.json)。`POST /exports` 接受后返回 `202`、操作表示和 `Location`；客户端轮询 `GET /exports/{operationId}`，状态为 `accepted → running → succeeded | failed | cancelled`。状态请求可重复；仅 `succeeded` 有 `result`，仅 `failed` 有 `error`。取消竞争的胜出状态、操作保留期和下载链接过期后的行为仍需服务负责人确认。

`Idempotency-Key` 按调用主体和操作名隔离，暂定保留 24 小时。同键同规范化请求恢复原 operation；同键不同请求指纹返回 `409 application/problem+json` 且不得创建第二个任务。超时客户端可以安全重发同一请求，但确认窗口外无法据此推断是否重复执行。

分页固定默认 50、最大 100；token 不透明，绑定排序和 `status` 过滤器。中间空页只要带有 `next_page_token` 就必须继续；仅无 token 表示结束。变更过滤器后复用旧 token 返回稳定 `400` Problem Details。错误消费者以 `type` 处理，不能解析 `detail` 文本。

夹具中的样例响应与冲突行为是待评审的服务契约决定。验证器证明 OpenAPI 结构和 JSON 形状可解析；Graph-free 样例不会冒充在线服务或并发存储测试。实现阶段还要验证同键并发、服务重启后状态持久性、任务重复执行、取消竞争、过滤 token 绑定及各终态错误处理。

资料：[RFC 9110 的 202 与 Location 语义](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.3.3)、[Google AIP-151 Long-running operations](https://google.aip.dev/151)、[Google AIP-155 Request identification](https://google.aip.dev/155)、[Google AIP-158 Pagination](https://google.aip.dev/158)、[RFC 9457 Problem Details](https://www.rfc-editor.org/rfc/rfc9457.html)、[OpenAPI 3.1.1](https://spec.openapis.org/oas/v3.1.1.html)。AIP 是 Google API 生态建议，只有项目选择采纳时才作为约束。
