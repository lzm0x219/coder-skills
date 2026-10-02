# RPC API 设计规则

固定框架、IDL、编码和生成器版本。以下 gRPC/Proto 规则仅在采用时命中；其他框架用其一手契约。等级与来源性质见主 Skill。

本页保留既有 gRPC/Proto R01–R10 规则；这些规则仅在其协议和语义适用时命中，不是 JSON-RPC、Thrift、SOAP/WSDL 或其他 RPC 的通用要求。按项目实际选用的框架/schema 加载：[gRPC 运行时](rpc/grpc.md)、[Protocol Buffers](rpc/proto.md)、浏览器 [gRPC-Web](rpc/grpc-web.md)、[JSON-RPC 2.0](rpc/json-rpc.md)，以及 Thrift、Connect、SOAP/WSDL、XML-RPC profile 的[其他 RPC 协议](rpc/other-rpc.md)。采用连续连接、服务推送、实时双向流或断线续传时，再加载[实时传输总则](realtime.md)及匹配的 WebSocket、SSE 或 HTTP 流分支；不要因使用 gRPC streaming 就套用 WebSocket 帧规则。

规则等级按[共享规则](common.md#规则等级)解释。未声明实现细节时，按服务预算给出大小、并发、重试或超时的候选值，或指出提供实际限额的部署配置与待确认项。

## gRPC 调用语义（R01–R05）

**R01｜gRPC 方法｜MUST 明确交互形态。** unary、服务端流、客户端流、双向流按需求选；服务名、消息类型、成功完成条件具体。证据：IDL 与序列。依据：协议，[Core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/)。

**R02｜失败｜MUST 为每种公开失败定义稳定状态与调用方动作。** `INVALID_ARGUMENT` 修请求；`FAILED_PRECONDITION` 等待状态改变；`ABORTED` 在更高层重试整个事务/序列；`UNAVAILABLE` 仅在操作可安全重放且策略允许时重试。`DEADLINE_EXCEEDED` 和 `CANCELLED` 必须向调用方可见；有副作用的操作超时后用查询/幂等键恢复未知结果。

采用 Google richer error model 时，必须读取并核验 [R02：结构化错误](rpc/rich-errors.md)，包括 wire 编码、消费端校验及正负例。证据：每种失败的状态与恢复样例；依据：[gRPC Error handling](https://grpc.io/docs/guides/error/)。详细分类/重试属于 API 设计要求；AIP-194 只在项目采纳 Google AIP 时作为强制规则。

**R03｜远程调用｜MUST 定义调用预算和取消传播。** 为方法规定有限 deadline 或由调用方传入的剩余预算；跨服务调用传播剩余时间，不能每跳重置完整预算。规定取消后服务端如何停止计算、下游调用与流生产并清理资源。写操作超时可能已提交，须提供查询、幂等键或可安全重复的恢复语义。证据：短 deadline、客户端取消、下游 deadline 传播及副作用未知结果样例。依据：设计；官方机制，[Deadlines](https://grpc.io/docs/guides/deadlines/)、[Cancellation](https://grpc.io/docs/guides/cancellation/)。

**R04｜自动重试｜MUST 给每个自动重试方法写明可重放依据和完整策略。** 声明 method、retryable status、最大总尝试次数、退避与抖动、总 deadline/重试预算、请求历史缓冲上限及服务端副作用约束；收到 response headers 后 gRPC 将调用视为 committed，不再自动重试。默认不自动重试有副作用或事务 RPC；`ABORTED` 应在事务边界重做。不要把 unary 的策略套到客户端流或双向流：客户端消息重放、缓冲耗尽、部分副作用与断点续传均须单独设计；server stream 提交后也不能从头重放。证据：固定 Service Config + 真实生成客户端，覆盖提交前一次重试、提交后流终态和调用次数。依据：gRPC 官方机制，[Retry](https://grpc.io/docs/guides/retry/)；若项目采纳 Google AIP，再执行 [AIP-194](https://google.aip.dev/194)，该 AIP 明确只推荐无非预期副作用、非事务、unary 请求的自动重试，并不覆盖 client/bidi streaming。

**R05｜流｜MUST 定义顺序、背压、完成和中途失败。** 单次 RPC 各方向内消息有序；写出/收到消息不代表对端业务已处理。规定每个方向的结束条件、半关闭、取消、允许的并发写入/在途消息、缓冲或窗口上限、慢消费者时生产者行为。client/server stream 最后仍有 RPC status；消费端必须耗尽/检查终态才能区分正常完成与部分结果后失败。定义重连游标、重复消息去重和确认语义，不能把重连误认为透明续传。显式重连策略另写次数、退避、计数重置条件；将阈值与单流 deadline 一起代入，确保重置前提可达，覆盖正常 EOF 和快速反复失败。证据：正常终结、部分消息后非 OK 终态、慢消费者/取消、断点恢复及重连预算样例。依据：gRPC 顺序与流控制机制，[Core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/)、[Flow control](https://grpc.io/docs/guides/flow-control/)；应用层重连预算与可达性检查是 Skill 设计门槛。

## Protocol Buffers 消息与演进（R06–R08）

**R06｜Proto 演进｜MUST 保持字段与枚举编号身份。** 永不复用已发布的 tag/value number；删除时 `reserved` 原编号，并保留名称（尤其消息经过 JSON/TextFormat/日志或名称在源码 API 中暴露时）。新语义分配新编号。字段改名分别判断 binary wire、ProtoJSON、生成源码 API，不能以 binary 可解析推断整体兼容。证据：旧/新 descriptor 自动比较，候选安全演进通过，复用编号反例被拒绝。依据：[Proto Best Practices](https://protobuf.dev/best-practices/dos-donts/)。

**R07｜presence/默认｜MUST 区分缺失与零值。** 用采用版本支持的 optional/oneof/edition presence；proto3 枚举首值编号为 0，SHOULD 表示 unspecified。业务必填另校验。证据：HasField、显式零值、未知枚举。依据：格式，[Field Presence](https://protobuf.dev/programming-guides/field_presence/)。

**R08｜跨版本｜MUST 分验 binary wire、ProtoJSON 与生成源码 API。** 对每个受支持的 old/new 读写方向分别检查未知字段保留/丢失、`oneof`、显式默认值、JSON 字段名与未知字段策略、int64/uint64 精度，以及真实生成调用点。ProtoJSON 不携带未知字段；解析器默认拒绝未知字段，启用忽略时需记录数据丢失风险。仍须支持旧严格客户端时，新增字段不能默认出现在其 JSON 输出中；提出旧投影或明确的新输出通道等候选策略，用未修改的旧 reader 检查实际候选输出，同时保留新 JSON 被旧 reader 拒绝的反例。不能以要求旧客户端改成忽略未知字段代替兼容方案；没有可确认的输出隔离策略时保留为发布阻断，不称兼容已解决。int64/uint64 JSON 映射为字符串，禁止把经过 IEEE-754 number 的精度当作无损。证据：固定版本的旧/新生成消费者做双向二进制与 ProtoJSON 往返，并分别报告兼容结论及策略的实现/接受状态。依据：[ProtoJSON](https://protobuf.dev/programming-guides/json/)、[Field Presence](https://protobuf.dev/programming-guides/field_presence/)。

## 集合、长任务与生成（R09–R10）

**R09｜集合/长任务｜MUST 定消费生命周期。** 分页不因空页终止；长任务有查询、终态、保留与取消。采用 AIP 才强制其消息模式。证据：终止、错误和恢复。依据：设计；生态，[AIP-158](https://google.aip.dev/158)、[AIP-151](https://google.aip.dev/151)。

**R10｜生成/发布｜MUST 固定工具链和入口。** IDL/目标语言编译；生成器/runtime 兼容；包/服务路径、大小上限及安全配置可定位。源码变更用旧客户端接入候选。证据：编译/消费者/配置。依据：设计；[runtime 保证](https://protobuf.dev/support/cross-version-runtime-guarantee/)。

按[协议交付](protocol-deliverables.md)给请求、结果、错误、时间、重试和流表。[字段演进样例](../../../tests/design-apis/cases/rpc-profile/contract.md)及扩展验证见[测试索引](../../../tests/design-apis/README.md)。
