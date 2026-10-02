# HTTP 授权、安全与错误

此页适用于所有公开/跨信任边界 HTTP API。协议状态语义是规范责任；访问控制具体策略由产品安全模型决定，不能只在 OpenAPI 中声明而不定义资源级行为。

**H33｜HTTP 资源授权落点｜任何 route 参数/查询/分页/批量项指定资源时。** 对每次访问重新按[共享安全契约](../common/security.md)CS01–CS03 判定 workspace/对象/字段/动作；HTTP 层必须把同一边界应用到 GET、LIST filter、cursor continuation、Range/download URL、批量每项和异步 operation URI，不能因 cursor/签名链接/已知 task ID 而跳过授权。无权与不存在时使用已选隐藏策略，按 H02 映射 401/403/404 并明确缓存/响应差别。证据：同一个对象从成员路由、列表、续页、下载链接和批量引用访问；跨租户拒绝且无副作用。HTTP 状态依据：[RFC 9110 §15.5.2–15.5.4](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.5)。

**H34｜HTTP 字段与外部 URL 边界｜body 或 filter 承载调用者可控字段时。** HTTP/OAS schema 的 `readOnly`/`writeOnly` 标签不构成服务端拒绝或投影机制；为每个 method 声明允许字段，不直接把 body 绑定内部模型，并确定未知字段拒绝/忽略行为。路径中的 tenant/resource identity 是路由对象，不得由 body 中重名字段覆盖。用户 URL 被服务端访问时，按[共享安全契约](../common/security.md)CS07 验证 DNS/redirect/target；HTTP 设计仍需标出 URL 所在字段、发起请求时点和失败如何回报。共用字段许可及消耗上限见 CS02/CS08，字段编码和 unknown-input 策略见[共享数据契约](../common/data.md)CD08/CD13。证据：读写只读字段、路径/body identity 冲突、unknown field、输入链接重定向到私网。参考：[OpenAPI 3.1.1 Schema Object](https://spec.openapis.org/oas/v3.1.1.html#schema-object)、[OWASP API3:2023](https://owasp.org/API-Security/editions/2023/en/0xa3-broken-object-property-level-authorization/)、[OWASP API7:2023](https://api-security.owasp.org/editions/2023/en/0xa7-server-side-request-forgery/)。

**H35｜错误恢复｜所有非成功响应。** 建立稳定错误类型/机器码、请求关联 ID、字段级校验位置、可重试判断和调用方动作；不要让客户端解析自然语言 detail。Problem Details 的 `type` 识别类别，`status` 与 HTTP 状态一致；扩展字段不可覆盖标准成员语义。对部分成功批量错误逐项给出结果。响应不能泄露栈、SQL、凭据、内部主机或未授权资源存在信息；敏感错误可映射为外部稳定类别并在受控日志保留诊断关联。证据：各错误分支 HTTP 状态、机器码、响应 body 与恢复策略一致。依据：[RFC 9457 §§3–5](https://www.rfc-editor.org/rfc/rfc9457.html#section-3)、[OWASP API8:2023](https://owasp.org/API-Security/editions/2023/en/0xa8-security-misconfiguration/)。

**H36｜HTTP 配额响应｜命中 rate/size/concurrency limit 时。** 具体主体、窗口和限额依据[共享安全契约](../common/security.md)CS08；HTTP 提案定义每种超限采用的状态码、problem code 和客户端调整/等待方式。仅在服务能预测等待时间时提供合法 Retry-After；请求体过大与配额超限须分别映射到适当结果，不把每种资源耗尽都塞进 429。证据：每个限额的边界值、超界状态、Retry-After、窗口/预算恢复及重试是否安全。依据：OWASP API4:2023、[RFC 6585 §4](https://www.rfc-editor.org/rfc/rfc6585.html#section-4)。
