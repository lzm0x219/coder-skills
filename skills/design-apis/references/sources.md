# 一手资料索引

查规范版本、核验争议或寻找规则出处时读取。本次核验日期：2026-10-01。固定版本指目标契约版本；滚动文档需按项目工具链再次核对。HTTP、GraphQL、Proto、CloudEvents 等规定各自边界，不能拼成一个外部组织颁布的统一 API 标准。本 Skill 的规则是这些资料与调用方设计要求的综合。

| 领域 | 一手资料与版本 | 用途与适用边界 |
| --- | --- | --- |
| HTTP | [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html)（2022） | H01/H02/H05：方法、状态、条件与鉴权 challenge；通用 HTTP 协议。 |
| HTTP | [RFC 9111](https://www.rfc-editor.org/rfc/rfc9111.html)、[RFC 6585](https://www.rfc-editor.org/rfc/rfc6585.html) | H09：缓存与附加状态码；限流窗口仍由服务定义。 |
| HTTP | [RFC 5789](https://www.rfc-editor.org/rfc/rfc5789.html)、[RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html) | H10 的 PATCH；H04 仅在采用 Problem Details 时命中其格式要求。 |
| 契约格式 | [OpenAPI 3.1.1](https://spec.openapis.org/oas/v3.1.1.html) | H03/H11：样例固定 3.1.1，不要求其他项目升级到此版本。 |
| Google API | [AIP-155](https://google.aip.dev/155)、[AIP-158](https://google.aip.dev/158)、[AIP-151](https://google.aip.dev/151)、[AIP-180](https://google.aip.dev/180) | H06/H07/H08/H12/R09：请求身份、分页、长任务、兼容。是 Google API 风格，字段和具体默认值不普遍强制。 |
| Google 取消操作 | [AIP-136](https://google.aip.dev/136)、[long-running Operations 定义](https://github.com/googleapis/googleapis/blob/master/google/longrunning/operations.proto)（滚动） | H08：Custom method 的 POST/冒号风格与 Cancel/Delete 的不同语义；`jobs` 自有资源采用该风格是提案取舍。 |
| Microsoft API | [Azure REST API Guidelines](https://github.com/microsoft/api-guidelines/blob/vNext/azure/Guidelines.md)（滚动） | 可对照一致性、长任务及错误设计；Azure 服务特有约定仅在采用时应用。 |
| GraphQL | [September 2025 规范](https://spec.graphql.org/September2025/) | G01-G05/G08/G09：输入默认、错误传播、串行 mutation、oneOf 与弃用；执行器支持须另核对。 |
| GraphQL | [官方 Security 指南](https://graphql.org/learn/security/)、[Relay Connections](https://relay.dev/graphql/connections.htm) | G06/G07：成本建议；Relay 仅在采用 Connections 时属于约束。 |
| GraphQL HTTP | [工作草案](https://http-spec.graphql.org/draft/)（滚动） | G10：传输绑定；不能宣称它是已批准的通用标准。 |
| gRPC | [Core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/)、[Status](https://grpc.io/docs/guides/status-codes/)、[Error handling](https://grpc.io/docs/guides/error/)、[Deadlines](https://grpc.io/docs/guides/deadlines/)、[Cancellation](https://grpc.io/docs/guides/cancellation/)、[Retry](https://grpc.io/docs/guides/retry/)、[Flow control](https://grpc.io/docs/guides/flow-control/) | R01-R05：框架语义；rich error 依目标语言支持核验；业务幂等、事务与已完成结果仍须项目设计。 |
| Google 重试 | [AIP-194](https://google.aip.dev/194) | R04：自动重试的生态建议，原文针对 unary；不得移植为流收到部分数据后的重放许可。 |
| Proto | [Proto3 Guide](https://protobuf.dev/programming-guides/proto3/)、[Presence](https://protobuf.dev/programming-guides/field_presence/)、[ProtoJSON](https://protobuf.dev/programming-guides/json/) | R06-R08：二进制、JSON、presence；把三种兼容结果独立报告。 |
| Proto | [Best Practices](https://protobuf.dev/best-practices/dos-donts/)、[runtime 保证](https://protobuf.dev/support/cross-version-runtime-guarantee/) | R06/R10：编号与工具链；官方建议不能忽略目标语言差异。 |
| 事件 | [CloudEvents v1.0.2](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md)、[JSON Format v1.0.2](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/formats/json-format.md) | Core 的 Required Context Attributes、Type System、Attribute Naming 与 Extension Context Attributes，以及 JSON §2.2（Type System Mapping）/ §3、§3.1.1–3.1.2（Payload Serialization / Deserialization） 的 null→unset、primary/secondary mapping（含当时 core 其他 event format 的显式映射要求）、data/data_base64、JSON String 解码；不规定 broker 恰好一次效果、顺序或保留期。 |
| 异步文档 | [AsyncAPI 3.1.0](https://www.asyncapi.com/docs/reference/specification/v3.1.0) | channel/message/operation 与 binding；文档格式不证明部署投递保证。 |
| Webhook | [GitHub 验签](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)、[最佳实践](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks)、[Stripe Webhook](https://docs.stripe.com/webhooks) | 接收对应服务商时核对头、原始字节、重投与时限；不同服务商不可互换。 |
| Webhook 签名 | [RFC 9421](https://www.rfc-editor.org/rfc/rfc9421.html)、[Standard Webhooks](https://github.com/standard-webhooks/standard-webhooks/blob/main/spec/standard-webhooks.md)（滚动社区规范） | 新契约可选；RFC 9421 仅在实际采用其签名模型时命中；后者不代表已有服务商都支持。 |
| 摘要/出口 | [RFC 9530](https://www.rfc-editor.org/rfc/rfc9530.html)、[OWASP API7:2023 SSRF](https://api-security.owasp.org/editions/2023/en/0xa7-server-side-request-forgery/) | WH06 的 body 摘要；WH10 的用户配置回调地址及出口边界，配置与实现仍须实际核验。 |
| 程序接口 | [Bloch 原作者](https://research.google/pubs/how-to-design-a-good-api-and-why-it-matters/)、[Swift API Guidelines](https://www.swift.org/documentation/api-design-guidelines/) | 调用点、语义和命名；语言语法不能强加到别的语言。 |
| 程序接口 | [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)、[Kotlin Authors Guidelines](https://kotlinlang.org/docs/api-guidelines-introduction.html)、[.NET Framework Guidelines](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/) | 语言映射、错误、扩展与演化；采用目标语言时读取对应章节。 |
| 远程 SDK | [Azure SDK General Guidelines](https://azure.github.io/azure-sdk/general_introduction.html) | 客户端、调用、配置与可诊断性；Azure 特定包形式不是通用规则。 |
| TypeScript 可变性 | [Object Types / readonly](https://www.typescriptlang.org/docs/handbook/2/objects.html#readonly-properties) | library-sdk/runtime:H01 与语言映射：只读属性、嵌套可变值及别名；运行期复制隔离不能由 tsc 证明。 |

## 扩展专题与具体章节

以下指针仅在命中专题或核验争议时读取。各规则所在文件标出原始章节及来源性质，当前操作依据在规则页；不以来源数量或规则数量证明全面。

| 命中专题 | 一手资料 / 采用边界 | 规则位置 |
| --- | --- | --- |
| JSON 数据/编码 | [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) §§4/6/8；[JSON Schema 2020-12 Validation](https://json-schema.org/draft/2020-12/json-schema-validation) §§6–9（format annotation/assertion）；[Core](https://json-schema.org/draft/2020-12/json-schema-core)；[RFC 7493](https://www.rfc-editor.org/rfc/rfc7493) 是可选 I-JSON profile | [共享数据](common/data.md)；重复键策略、精度、缺失/null 与默认不由示例猜测。 |
| 时间/字节/URI | [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339) §5；[RFC 4648](https://www.rfc-editor.org/rfc/rfc4648) §§3–5；[RFC 3986](https://www.rfc-editor.org/rfc/rfc3986) §§2–3；日期、持续时间及 opaque cursor 另定合同 | [共享数据](common/data.md)。 |
| 安全/权限 | [OWASP API Security 2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) API1/2/3/4/5/6/7/8/9/10 是风险指南；[RFC 6750](https://www.rfc-editor.org/rfc/rfc6750) + [RFC 9700](https://www.rfc-editor.org/rfc/rfc9700)（BCP 240，2025）只约束采用 OAuth 的部分 | [共享安全](common/security.md)；实际部署和业务授权另验。 |
| OAuth 委托与令牌重放 | [RFC 8693（2020）§1.1/§4.1](https://www.rfc-editor.org/rfc/rfc8693.html#section-1.1)；[RFC 9700 / BCP 240（2025）§§2.2/4.10.1/4.14.2](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.2) | [共享安全 CS16/CS17](common/security.md)；delegation/impersonation 条件决策、access-token sender binding 的 SHOULD 与 public-client refresh-token 防重放的 MUST 分开；不要求所有 API 采用 Token Exchange、DPoP 或 mTLS。 |
| 公共演进 | [AIP-180](https://google.aip.dev/180)；[SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)（采用时）；具体语言/格式规则优先于笼统“新增兼容” | [共享演进](common/evolution.md)与目标协议/语言页。 |
| HTTP 资源/批量/异步/表示 | [Google AIP 资源与方法](https://google.aip.dev/general)是具名风格，具体 AIP 章节在规则旁；[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110)、[9111](https://www.rfc-editor.org/rfc/rfc9111)及PATCH/Range/摘要 RFC；[WHATWG Fetch CORS](https://fetch.spec.whatwg.org/#http-cors-protocol)是滚动 living standard | [HTTP 条件路由](http.md)。 |
| GraphQL 扩展能力 | [GraphQL.org](https://graphql.org/learn/)的 pagination/security/serving/performance/file-upload 指南；[Naming design](https://graphql.org/learn/naming-design/)；[Apollo Federation v2.9 指令 SDL](https://specs.apollo.dev/federation/v2.9/federation-v2.9.graphql)（采用才约束）；Relay 与 HTTP 草案同样为独立 profile | [GraphQL 条件路由](graphql.md)；传输/成本/联邦不冒充核心规范。 |
| gRPC 配置与浏览器绑定 | [Service Config](https://grpc.io/docs/guides/service-config/)、[Hedging](https://grpc.io/docs/guides/request-hedging/)、[Metadata](https://grpc.io/docs/guides/metadata/)、[Keepalive](https://grpc.io/docs/guides/keepalive/)；[gRPC-Web official client](https://github.com/grpc/grpc-web)及[protocol delta](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-WEB.md)为滚动项目文档，落地须 pin release | [RPC](rpc.md)。不同语言/浏览器客户端能力不能互推。 |
| 其他 RPC | [JSON-RPC 2.0](https://www.jsonrpc.org/specification)；[Thrift IDL](https://thrift.apache.org/docs/idl)（页面 0.25.0）；[Connect protocol](https://connectrpc.com/docs/protocol/)；[SOAP 1.2](https://www.w3.org/TR/soap12-part1/)与[WSDL 2.0](https://www.w3.org/TR/wsdl20/)；[XML-RPC profile](http://xmlrpc.com/spec.md)是历史 profile | [RPC 路由](rpc.md)；分别固定绑定/生成器/传输/扩展，不共享 gRPC 的保证。 |
| 实时/流 | [RFC 6455](https://www.rfc-editor.org/rfc/rfc6455) §§4–8/10；[RFC 8441](https://www.rfc-editor.org/rfc/rfc8441)（可选 HTTP/2 bootstrap）；[WHATWG SSE §9.2](https://html.spec.whatwg.org/multipage/server-sent-events.html)；[RFC 7464](https://www.rfc-editor.org/rfc/rfc7464) | [实时路由](realtime.md)；durable history 与业务 ACK 由应用决定。 |
| Broker binding / 投递 | [Kafka design](https://kafka.apache.org/documentation/#design)；[AMQP 1.0](https://www.oasis-open.org/standard/amqp/)；[MQTT 5.0](https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html)；[JetStream](https://docs.nats.io/nats-concepts/jetstream) | [事件](events.md)、[投递与来源边界](#events-webhooks)；版本/客户端/broker 配置和原子参与者决定实际保证。 |
| 包/模块/feature | [Node Packages](https://nodejs.org/api/packages.html)（访问页面 v26.10.0）；[TypeScript Publishing](https://www.typescriptlang.org/docs/handbook/declaration-files/publishing.html)；[Cargo Features](https://doc.rust-lang.org/cargo/reference/features.html)/[Targets](https://doc.rust-lang.org/cargo/reference/cargo-targets.html)/[SemVer Compatibility](https://doc.rust-lang.org/cargo/reference/semver.html) | [包与平台](library-sdk/packaging.md)；本机 runtime 版本另报。 |
| 原生/宿主/扩展者 | [Rust Nomicon FFI](https://doc.rust-lang.org/nomicon/ffi.html)；[JNI SE25](https://docs.oracle.com/en/java/javase/25/docs/specs/jni/design.html)；[Wasm Core 2 / CR Draft 2026-09-30](https://www.w3.org/TR/2026/CRD-wasm-core-2-20260930/)；[JLS SE25 §13](https://docs.oracle.com/javase/specs/jls/se25/html/jls-13.html)；[.NET Interface](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/interface)/[Virtual members](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/virtual-members)；[C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)为建议 | [原生](library-sdk/native-interop.md)、[框架扩展](library-sdk/extensions.md)；ABI/回调/旧实现者按目标平台核验。 |
| 目标语言 API | [Swift](https://www.swift.org/documentation/api-design-guidelines/)、[Rust](https://rust-lang.github.io/api-guidelines/)、[Kotlin](https://kotlinlang.org/docs/api-guidelines-introduction.html)、[Go](https://go.dev/wiki/CodeReviewComments)、[Python inspect](https://docs.python.org/3/library/inspect.html)/[asyncio](https://docs.python.org/3/library/asyncio-task.html)、TypeScript 与 .NET 官方指南 | [语言路由](library-sdk/languages.md)及其语言子页；官方指南不是跨语言的统一签名规则。 |
| 远程 SDK 管线 | [Azure general design](https://azure.github.io/azure-sdk/general_design.html)/[implementation](https://azure.github.io/azure-sdk/general_implementation.html)、[AWS retry](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html)、[Google Cloud client best practices](https://docs.cloud.google.com/apis/docs/client-libraries-best-practices) | [远程SDK](library-sdk/remote.md)；产品默认次数/顺序不得当成普遍常数。 |
| 自动化进程 | [POSIX Issue 8 / 2024 Utility Syntax §12](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap12.html)及[Utilities Introduction §1.4](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap01.html)；[Shell Command Language](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html)；JSON framing 另选 | [自动化](automation.md)；POSIX 标准 utility 的要求和项目自有 CLI 合同须区分。 |
| SQL / DSL | [SQLite datatype/affinity](https://www.sqlite.org/datatype3.html)、[SQLite SELECT](https://www.sqlite.org/lang_select.html)、[Expressions](https://www.sqlite.org/lang_expr.html)、[binding](https://www.sqlite.org/c3ref/bind_blob.html)、[transactions](https://www.sqlite.org/lang_transaction.html)；[PostgreSQL 18 PREPARE](https://www.postgresql.org/docs/18/sql-prepare.html)/[Isolation](https://www.postgresql.org/docs/18/transaction-iso.html) | [查询](query.md)；引擎实例的行为不推广为全部 SQL/DSL。 |

采用 C11 的原生消费者还需查 [WG14 N1570（2011-04-12 委员会草案）](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf) §7.1.4、§7.22.3、§7.24.1 的指针、分配和零长度函数语义；公开草案不是 ISO 出版终稿，目标版本/allocator 规则按采用规范核验。对应 Y02 的空 buffer 和释放转换消费，不从 Rust FFI 指南推定 C 库行为。

核验记录应保存来源、采用版本、适用对象和提案位置。协议规定的行为优先于项目偏好；资料冲突时先检查两者是否针对相同协议、版本和调用对象，再作设计判断。资料没有规定的命名、超时或重试数值，用候选决策及验证依据说明。

<a id="events-webhooks"></a>

## 事件与 Webhook 来源边界

事件操作判断由[事件数据](events/schema.md)、[broker profiles](events/brokers.md)及 [Webhook](webhooks.md)各分支维护。来源核对日期仍为 2026-10-01；服务商滚动行为使用时复核。

- AsyncAPI 的 [operations](https://www.asyncapi.com/docs/concepts/asyncapi-document/adding-operations)、[bindings 概念](https://www.asyncapi.com/docs/concepts/asyncapi-document/adding-bindings)与[绑定规范](https://www.asyncapi.com/docs/reference/bindings)补充文档建模；描述文件不证明 broker 配置、ACL 或端到端投递。
- [Stripe 自动重试](https://docs.stripe.com/webhooks#automatic-retries)及当前操作窗口由[提供方 profile](webhooks/profiles.md)维护，不把时间常数套到自建发送端。
- ACK、settlement、消费 checkpoint、数据库提交和外部效果按实际参与者分别验证；CloudEvents、registry 通过、签名向量或局部状态模拟均不证明端到端 exactly-once。
- 当前 broker 分支涵盖 Kafka、AMQP 1.0、MQTT 5 与 JetStream。RabbitMQ/AMQP 0-9-1、Pulsar、SQS/SNS、Pub/Sub、Redis Streams 等按采用版本补专属规则；未选协议不加载。
