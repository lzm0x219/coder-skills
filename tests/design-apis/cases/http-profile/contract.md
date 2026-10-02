# 条件更新 HTTP 契约样例

主契约是 [OpenAPI 3.1.1](openapi.json)，[消费样例](cases.json)含成功、旧 ETag、缺少前置条件、无效主体、未认证和已认证但无权限。`PUT` 完整替换资料；调用方持有最近读取的强 `ETag`，通过 `If-Match` 防止覆盖并发修改。成功为 `204`、新 `ETag`、无响应体；旧值为 `412` 且不写入；缺少头为本提案定义的 `400`，不能静默覆盖。无效主体 `400`。没有或无效凭据时返回 `401`，带适用的 `WWW-Authenticate` challenge；身份有效但仅有只读权限时返回 `403`。本提案先检查身份与输入，再评估 `If-Match`，故未认证且版本已过期仍返回 `401`。若用 Problem Details，消费者按稳定的 `type` 分流，`detail` 只作说明。

此处的响应及检查顺序是**候选设计决策**，尚无服务实现证据。静态检查只能证明 OpenAPI 和样例契约一致；不能证明服务器真的返回 `412` 或不写入。依据：[RFC 9110 条件请求和认证语义](https://www.rfc-editor.org/rfc/rfc9110.html#section-13)、[RFC 9457 Problem Details](https://www.rfc-editor.org/rfc/rfc9457.html)、[OpenAPI 3.1.1](https://spec.openapis.org/oas/v3.1.1.html)。
