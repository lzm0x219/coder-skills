# Server-Sent Events (SSE)

仅用于浏览器 EventSource 或明确实现 WHATWG event-stream parser 的单向服务端推送。SSE 是 UTF-8 文本 HTTP event stream；客户端→服务器命令走单独 HTTP endpoint。标准自动重连/Last-Event-ID 不代表服务保存了事件或可以无损续传。并用[实时总则](../realtime.md)。依据：[WHATWG HTML Server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html)。

**SSE01｜Wire format｜规范 MUST。** 响应为 text/event-stream，按空行分派事件；data: 多行以换行拼接，: comment 不派发，可用于心跳；id 不可含 NUL，retry 仅接受 ASCII digits。每个事件明确 event name、JSON/text payload schema、最大行/事件 bytes；只在事件以空行结束时客户端派发，不把 TCP chunk 当完整事件。反例含 chunk 中间切分、CRLF、多行 data、结尾缺空行。依据：WHATWG §9.2.4–§9.2.6。

**SSE02｜Event ID/重放｜标准机制 + Skill MUST。** id 为 opaque replay cursor，唯一性/排序范围、租户/过滤条件绑定、保留期、重复策略由应用定义。浏览器断线时会发送 Last-Event-ID；服务端必须明确从此 ID 重播、返回 reset/bootstrap，还是无历史时返回显式错误。无持久事件日志/游标存储时如实标记 best-effort，不能声称无损。依据：WHATWG §9.2.3–§9.2.4。

**SSE03｜Reconnect｜规范机制 + Skill MUST。** WHATWG retry: 设置浏览器重连等待毫秒；连接关闭可触发自动重连，HTTP 204 可命令 EventSource 停止重连。另定义鉴权失败、cursor 过期、永久协议错误的 HTTP response；服务端按应用保留期恢复或提示重新 bootstrap。需要更复杂随机 jitter/重连预算时说明使用 fetch/自定义 client，因为标准 EventSource 暴露能力有限。依据：[reconnection](https://html.spec.whatwg.org/multipage/server-sent-events.html#reestablish-the-connection)、[HTTP 204](https://html.spec.whatwg.org/multipage/server-sent-events.html#processing-model-8)。

**SSE04｜缓存/代理｜Skill MUST。** 明确响应缓存禁用策略、反向代理 buffering、idle timeout、压缩、HTTP/1.1 per-origin connection limit 与 HTTP/2 stream 配置；部署检查真实 ingress/CDN 的 flush/timeout。WHATWG user agent 解析规范不保证某代理会实时 flush。心跳 comment 按目标中间层 idle timeout 设定，不固定照搬示例间隔。依据：WHATWG event stream response/authoring notes。

**SSE05｜Backpressure/终态｜Skill MUST。** 规定每客户端排队字节/事件上限、慢 consumer 策略和消费端处理失败语义；断线不代表业务命令撤销。返回结束/权限撤销/订阅不存在/限流时定义连接如何终止、浏览器会否自动重连与客户端如何停用 EventSource，防止永久错误形成 retry storm。

**SSE06｜安全/凭据｜Skill MUST。** 定义 EventSource credentials/CORS 与 cookie 作用域；禁止把长期 bearer secret 放 query string。若浏览器 API 无法设定所需 header，明确使用安全 cookie/短期可撤销 token 或 fetch-stream client；CORS 允许源不得是无边界 wildcard + credentials。Origin 与认证/授权分开判定。
