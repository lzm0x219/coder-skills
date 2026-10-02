# HTTP streaming

适用于以 HTTP response/request body 长时间分块传输但未采用 WebSocket 或 SSE 专属 parser 的接口，包括 chunked response、NDJSON/JSON Text Sequences 等应用 framing。HTTP transport 不自动提供 record boundary、可靠 event replay、acknowledgement 或双向实时性。复用[HTTP API](../http.md)请求/响应规则和[实时总则](../realtime.md)。

**HS01｜Framing｜Skill MUST。** 选择媒体类型和 record delimiter（NDJSON、RFC 7464 JSON Text Sequences 或 binary length-prefix），定义 UTF-8/CRLF、空行、跨 chunk 拼接、末尾 partial record 和 malformed record 处置。parser 增量读取并限制单条 record 大小；不得依赖一次 socket read 等于一条记录。若用 RFC 7464，按其 RS 开始与可检测截断语义实现，不把它误读为事务完整性。依据：[RFC 7464](https://www.rfc-editor.org/rfc/rfc7464)、HTTP message framing in [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110)。

**HS02｜Flush 与中间件｜Skill MUST。** 列部署路径上的 proxy/load balancer/CDN buffering、content encoding、idle timeout 和最大 response 时长；通过目标 ingress 的实际测试测首条与后续事件到达，不将服务器 write/flush 调用等同网络交付。断流后声明已收 records 与未完成 record 的边界。

**HS03｜终态/错误｜Skill MUST。** 流已开始后若 HTTP status/trailer 无法再修改，定义应用末尾 terminal record（success/error、cursor、trace correlation）及 EOF 无 terminal record 代表的中断状态。消费者只有读到定义的 terminal record 才能认为业务完成；最后一个不完整 JSON record 必须丢弃并报告 truncated，而非解析为成功。

**HS04｜Backpressure/limits｜Skill MUST。** 对单条 record、累计 stream bytes、时间/事件数、队列和每主体并发制定配置值、上游暂停/取消与超限可见错误。HTTP 协议与各 runtime 没有本 API 的统一 application record 最大值；由服务容量及代理约束推导并记录来源。

**HS05｜Recovery｜启用续传时的 Skill MUST。** 使用应用 cursor/Last-Event-ID 或 range/token 时说明包含/不包含边界、filter/schema/version 绑定、保留期和重复处理；cursor invalid/expired 必须有 bootstrap 响应。TCP/HTTP 重试从头重放不等于从已确认位置续传；对产生副作用的 request body 采用幂等 key 或客户端 resume protocol。

**HS06｜半关闭与 duplex｜采用 request/response 双向流时的 Skill MUST。** 说明目标 HTTP 版本、服务器/库是否支持 full duplex request 与 response 同时读写、各半流关闭信号和 proxy 行为。HTTP/1.1、HTTP/2、HTTP/3 及浏览器 Fetch 能力不同；没有目标栈 loopback/浏览器验证就列为兼容未决，不称通用 duplex。
