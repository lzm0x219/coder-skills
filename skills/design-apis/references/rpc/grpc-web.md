# gRPC-Web 浏览器传输

仅在浏览器 HTML/JavaScript client 访问 gRPC service 时应用；它是为浏览器限制设计的独立协议，不是原生 gRPC over HTTP/2。必须读取 [gRPC-Web Protocol](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-WEB.md)、[gRPC-Web client README](https://github.com/grpc/grpc-web) 与实际代理/生成器版本。和 [gRPC 运行时契约](grpc.md)、[Proto schema](proto.md)、[HTTP API](../http.md) 组合评审。

**GW01｜传输边界｜Skill MUST。** 明列 browser client → gateway/proxy → native gRPC service 的每一跳、TLS 终止、metadata/trailer 转换、CORS/XSRF、endpoint auth 和错误映射。共享 .proto 不代表 gRPC-Web 与 gRPC wire interchange；用 browser generated client + 实际目标代理做 integration evidence。依据：[PROTOCOL-WEB](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-WEB.md)。

**GW02｜RPC 形态｜生态限制 + Skill MUST。** 按当前官方 grpc-web client 能力，浏览器 unary 可用；server-side streaming 当前只在 `grpcwebtext` mode 支持；client-side 和 bidirectional streaming 当前不支持。不要把 .proto 上 `stream` 的存在等同 browser 可调用。对于上传/双向 UI，选 browser 支持的替代 API、明确代理/专属库支持及部署要求，并测试真实浏览器和版本矩阵。依据：[grpc-web README, Streaming Support](https://github.com/grpc/grpc-web)。

**GW03｜Wire framing｜Skill MUST。** 为 `application/grpc-web+proto` binary 和 `application/grpc-web-text` base64 文本区分 parser/支持形态。响应可能把 trailer/status 封装成 body 最后一帧（flags MSB 表示 trailer），EOF 仅关 body；consumer 必须解析终端 trailers 才可判断 RPC 状态，不能把 HTTP 200/正常 EOF 当 RPC 成功。按锁定协议 revision 和 SDK 版本由官方库解码 framing，并用截断/缺 terminal trailer 负例验证。依据：[gRPC-Web Protocol differences](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-WEB.md#protocol-differences-vs-grpc-over-http2)。

**GW04｜CORS/Auth｜Skill MUST。** 枚举浏览器预检允许的 request headers、暴露给 JS 的 response headers、credentials/cookie 策略、可信 origin、CSRF/XSRF token 与代理追加的 metadata；允许的 origin 与 authenticated principal 不等价。通过浏览器实测 OPTIONS、拒绝跨域和无凭据请求。依据：[official gRPC-Web browser features](https://github.com/grpc/grpc-web/blob/master/doc/browser-features.md)。

**GW05｜生成 client 与工具链｜Skill MUST。** 锁定 protoc、`protoc-gen-grpc-web`、message generator、npm runtime 和输出 mode/import style；生成代码纳入源码 API diff 与实际 TS/JS consumer 编译。代理 capability、transport mode 和 runtime 的版本是互操作矩阵的一部分，不能以 Proto compile 代替。依据：[grpc-web README](https://github.com/grpc/grpc-web)。

**GW06｜Browser stream lifecycle｜使用 server stream 时的 Skill MUST。** 说明 data/status/end/error/cancel 的 callback 顺序、最后 status 可见点、用户取消后的服务端资源停止及已收到部分消息的表现。server streaming failure 之后是否重试、从哪里恢复由应用 cursor/去重协议确定；gRPC-Web stream 不提供 durable resume。依据：官方 README 的 server-streaming client example 与 gRPC cancellation semantics。
