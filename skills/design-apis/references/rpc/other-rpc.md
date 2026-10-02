# 其他 RPC 协议分支

按项目真实选用的协议只应用对应小节；不要把 gRPC status、JSON-RPC envelope 或 HTTP resource semantics 移植成所有 RPC 的规则。未列出的框架回到其官方协议/实现文档，确定实际版本、消息封装、传输 binding、客户端库与服务端互操作组合后再设计。

## 选择协议分支

| 项目选择 | 本页规则 | 官方依据 | 需另加载 |
| --- | --- | --- | --- |
| Connect RPC | C01–C05 | [Connect Protocol](https://connectrpc.com/docs/protocol/) | [Proto](proto.md)，HTTP 传输按需读 http references |
| SOAP 1.2 + WSDL 2.0 | S01–S06 | [SOAP Part 1](https://www.w3.org/TR/soap12-part1/)、[Part 2](https://www.w3.org/TR/soap12-part2/)、[WSDL 2.0 Part 1](https://www.w3.org/TR/wsdl20/)、[Part 2](https://www.w3.org/TR/wsdl20/part2/) | 实际 SOAP binding、security/reliability module |
| XML-RPC | X01–X05 | 项目所用 XML-RPC profile 与其实现文档；起点：[XML-RPC Specification](https://xmlrpc.com/spec.md) | XML parser/runtime、安全配置、HTTP binding |
| Apache Thrift | RT01–RT08 | [Thrift 分支](thrift.md) | 目标语言能力矩阵 |

## Connect RPC

Connect 是独立的 HTTP RPC protocol，不是“gRPC 换一个 content-type”。锁定官方 protocol revision/SDK 版本、HTTP 版本和已启用的 gRPC/gRPC-Web/Connect transports。双向 streaming 能力受实现及 HTTP version 限制；不要由 Proto 服务声明直接推断所有传输端支持全部形态。

**C01｜Content type/framing｜Skill MUST。** unary 用 application/proto 或 application/json payload，streaming 用 application/connect+proto 或 application/connect+json 的 envelope framing；响应中 streaming failure 位于最终 EndStreamResponse，HTTP status 可能仍是 200。consumer 必须检查终态 envelope 才判定业务成功。unsupported content-type/encoding 按官方状态处理。用官方 Connect client 解析 success、error 和截断 stream 各一例。依据：[Protocol Reference](https://connectrpc.com/docs/protocol/)。

**C02｜Method 与 GET｜Skill MUST。** 默认 POST 与 Protobuf fully qualified service/method 路径；仅标为 `NO_SIDE_EFFECTS` 且符合目标 Connect profile 的 unary RPC 才考虑 GET，单纯幂等不等于安全。GET query encoding、缓存、隐私和 URL 长度进入契约；GET 不是因为“只读名字”就天然无副作用。依据：Connect protocol 的 safe GET 条件。

**C03｜协议协商｜Skill MUST。** 记录 Connect-Protocol-Version、codec、compression negotiation、HTTP status 和 client compatibility；明确 server/proxy 缺版本 header 的策略。面向浏览器时检查 CORS 和 gRPC-Web/Connect 传输具体实现，不把跨浏览器能力当协议保证。依据：Connect Protocol Reference。

**C04｜Streaming｜Skill MUST。** 按 Connect envelope flag 与长度解码 message；请求 stream 可零条或多条，响应 stream 必须有最终 EndStreamResponse，且不得提前出现。定义 HTTP/2 要求、half/full duplex、客户端读取 terminal errors/trailers 的处理。采用二进制或 JSON 分开生成真实 wire fixture 并用目标 SDK 解码正反例。依据：Connect protocol 的 Streaming Request/Response 章节。

**C05｜协议互操作｜Skill MUST。** 对每个 endpoint 声明是否接受 Connect、gRPC、gRPC-Web；为每个开关分别验证 status、错误 detail、metadata、压缩、streaming 和 ProtoJSON 行为。共享 Proto schema 不证明 protocol wire互通。依据：Connect Protocol 与对应 gRPC protocol spec。

## SOAP 1.2 与 WSDL 2.0

SOAP 1.2 是 extensible messaging framework；核心规范没有默认提供 reliability、security、correlation、routing 或完整 MEP。WSDL 是抽象 interface + binding/endpoint 描述，不会仅凭 abstract operation 规定所有 runtime 重试/安全语义。必须锁定 SOAP 1.1 或 1.2、WSDL 1.1 或 2.0、binding/WS-* profile 与客户端代码生成器；不要把各代混称“SOAP 标准”。

**S01｜WSDL contract｜Skill MUST。** 审查 interface/operation、input/output/fault、message element/type、binding、endpoint 与 style/use 的完整映射；附真实 WSDL/XSD 和目标工具生成后的公开方法签名。每个 endpoint-binding-operation 都有正例与 schema/binding 反例。依据：[WSDL 2.0 Core](https://www.w3.org/TR/wsdl20/) 和 [SOAP binding Part 2](https://www.w3.org/TR/wsdl20/part2/)。

**S02｜Version/namespace｜规范 MUST。** SOAP 1.2 Envelope namespace 为 http://www.w3.org/2003/05/soap-envelope；version mismatch 依规范 fault 处理。XML element identity 使用 namespace URI + local name，不依靠 prefix 拼写。WSDL target namespace 与 SOAP envelope namespace 分别管理；破坏 contract 时给新 namespace/versioning strategy 与旧/新生成客户端测试。依据：[SOAP Part 1 §5.1, §5.4.7](https://www.w3.org/TR/soap12-part1/)。

**S03｜Header extensions｜规范 MUST + Skill MUST。** 每个 SOAP header block 指定 QName、target role、mustUnderstand、relay 和模块版本。接收节点对指向自身角色且 mustUnderstand=true 的未知/不支持 header 不能静默忽略；定义 NotUnderstood/MustUnderstand fault 及中介者 relay 行为。不得未经协商占用其他 namespace 扩展。依据：[SOAP Part 1 §2.3–2.7, §5.2.1–5.2.4](https://www.w3.org/TR/soap12-part1/)。

**S04｜Fault｜Skill MUST。** 为各 SOAP Fault code/subcode/detail QName 给稳定 machine-readable 语义、调用方动作、是否重试和是否结果未知；Reason 文本为人读信息，不当协议字段。区分 Sender/Receiver 与版本/必理解 fault；SOAP 1.2 HTTP binding 的 status/fault mapping 按选定 binding 核验。依据：[SOAP Part 1 §5.4](https://www.w3.org/TR/soap12-part1/)；[SOAP HTTP binding](https://www.w3.org/TR/soap12-part2/)。

**S05｜Binding/MEP｜Skill MUST。** 单独定义 SOAP abstract MEP 和 transport binding 如何实现 request-response/one-way、HTTP status/headers、重定向、timeout 和连接复用；SOAP core 自身不承诺重试、消息相关性或持久交付。WS-Security、WS-ReliableMessaging 等扩展需精确 profile/版本和互操作测试，不能仅写“支持 WS-*”。依据：[SOAP Part 1 §1.3、§3.2、§4](https://www.w3.org/TR/soap12-part1/)。

**S06｜互操作与 XML 安全｜Skill MUST。** 对确定的 WSDL/XSD、binding、SOAP 版本与工具矩阵做 cross-stack roundtrip 和 faults test；固定 parser 的 DTD/external entity、扩展实体、总 document size、深度和处理时间限制，并对 schema imports 使用允许列表。规范有效不等于 parser 安全。依据：W3C SOAP/WSDL 定义的 XML 载体；安全限额按实际 XML parser 官方配置。

## XML-RPC（profile-dependent）

XML-RPC 资料/实现存在不同年代与扩展；除通用 methodCall/methodResponse/fault 形状外，将被采用的规格/profile 与服务器/client版本一并纳入 contract。不能把 XML-RPC 的整数范围、nil、日期或扩展类型假设为跨实现一致。

**X01｜Method 与参数｜Skill MUST。** 登记稳定 method name、大小写、参数顺序/类型、必选数目、返回类型与 version profile；标准 struct member order 不作业务依赖。对未知方法、参数个数/类型不合、未知 struct member 给出确定 fault 行为并用目标 parser 检查。依据：[XML-RPC profile](http://xmlrpc.com/spec.md)及目标实现文档。

**X02｜Fault｜规范 MUST + Skill MUST。** `methodResponse` 包含 `params` 或 `fault` 之一，不能同时存在；定义 faultCode 到稳定业务类别、faultString 诊断边界、重试性和调用方动作。faultString 不参与 machine branching，不包含堆栈/秘密。列出 malformed XML、未知 method、业务错误、transport timeout；写操作 response 丢失仍视为结果未知。依据：[XML-RPC Response Format](https://xmlrpc.com/spec.md)。

**X03｜Profile interop｜Skill MUST。** 对每种数据类型（integer、boolean、string、double、dateTime、base64、array、struct、nil/extensions）标出基础规格或双方共同扩展；为边界数字、时区、binary、空值和未知扩展跑目标双方实际序列化 roundtrip。服务器不能因一个实现接受扩展就宣称标准允许。

**X04｜XML/HTTP transport｜profile MUST + Skill MUST。** 固定 HTTP method/headers/charset/auth/TLS、XML parser safe configuration、request/response byte limits、timeout、HTTP status 与 RPC fault 的优先级；遵循基础 HTTP profile 时请求使用 POST、`text/xml`、正确的 `Content-Length` 和 `Host`，除低层 HTTP 错误外 XML-RPC response 是 HTTP 200 + 单个 `methodResponse`。禁用不需要的 XML external entities。客户端必须区分收到 XML fault、无法解析的响应与没有响应；后者不能证明服务未执行。依据：[XML-RPC header and response requirements](https://xmlrpc.com/spec.md)；安全限制按具体 parser 文档验证。

**X05｜基础类型与日期｜规范/profile MUST。** 若声明遵循 UserLand 基础规格，`i4`/`int` 是有符号 32 位值，boolean 只能表示 `0`/`1`，日期字段未定义默认时区，服务文档必须明说时间解释。`i8`、`nil` 等若被目标实现扩展，先证明双方 profile 一致再使用；不得默默升级基础类型。依据：[XML-RPC Specification](https://xmlrpc.com/spec.md)，其原始 profile 更新时间为 2003-06-30。
