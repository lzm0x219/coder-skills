# gRPC 调用契约

仅在选择 gRPC 时应用。先固定 gRPC 语言实现及版本、传输（通常 HTTP/2）、IDL、客户端生成器、Service Config 来源和目标代理；gRPC 机制跨语言不代表每种语言实现都支持相同能力。共同方法/消息演进回到 [RPC 总则](../rpc.md) 与 [Proto 分支](proto.md)；浏览器访问加载 [gRPC-Web](grpc-web.md)。规范 MUST/SHOULD 是 gRPC 协议约束；生态 SHOULD 是 gRPC 官方建议；Skill MUST 是设计交付要求。

## 方法、终态与错误

**RG01｜完成状态｜Skill MUST。** 每个 unary/server-stream/client-stream/bidi 方法写清请求与响应数目、谁先发、每个方向的结束方式、终态 status 从何处读取，以及部分消息后失败如何呈现。gRPC stream 的发送方向相互独立；双向双方可按各自协议任意读写顺序。消费者不得把“收到最后一条业务消息”当作 RPC 成功，必须读取最终 status/trailers。证据：每种形态一个成功与“已有消息后非 OK”调用示例；依据：[Core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/)。

**RG02｜状态分类｜Skill MUST。** 为可恢复的公开失败映射稳定 gRPC status 和下一步动作：参数错误修改请求；`FAILED_PRECONDITION` 改变前置状态后再调用；`ABORTED` 在事务/序列边界重试；`UNAVAILABLE` 只有可安全重放时重试；`RESOURCE_EXHAUSTED` 按配额/资源说明退让；`PERMISSION_DENIED` 不应盲目重试；`UNAUTHENTICATED` 走凭据更新流程。业务错误不得塞进状态文本供消费者解析。列出 status 到动作的表并覆盖未知 code 的安全默认。依据：[Status codes](https://grpc.io/docs/guides/status-codes/)、[Error handling](https://grpc.io/docs/guides/error/)。

**RG03｜丰富错误｜采用 protobuf rich error 时的 Skill MUST。** 只使用官方 `google.rpc.Status` wire contract：二进制序列化放入 `grpc-status-details-bin` trailer，typed detail 放 `Status.details` 的 `Any`；客户端用语言 helper 或等价解析，校验外层与嵌入的 code/message 一致并按 type URL 解包。detail 缺失、损坏、未知类型或不一致时退回稳定外层 status 的通用处理，不触发细粒度自动恢复。先验证目标语言/代理链支持；否则定义另一种有版本的应用协议，不能声称互通 rich error。依据：[gRPC richer error model](https://grpc.io/docs/guides/error/)。

**RG04｜Metadata｜Skill MUST。** 为每个 metadata key 记方向（initial request/header 或 response trailer）、ASCII/binary、重复值合并、大小预算、敏感性、跨代理可见性和消费者动作。保留 `grpc-` 前缀及实现定义字段；认证优先使用 gRPC credentials/安全传输机制，不把 bearer token 写进业务消息、URL 或日志。元数据不得承载需要可靠持久化的大型结果。gRPC 官方建议请求头默认总量上限为 8 KiB，但具体服务可不同；设计应读取服务端真实配置而不是把建议值写成协议常量。依据：[Metadata](https://grpc.io/docs/guides/metadata/)、[Authentication](https://grpc.io/docs/guides/auth/)。

## 预算、重试和流控

**RG05｜Deadline｜生态 SHOULD + Skill MUST。** gRPC 调用默认没有 deadline；客户端为每次请求设合理有限预算，服务器向下游传播剩余预算而非重新给满额，并记录哪些语言库会自动传播。写操作超时必须按“结果可能已提交”处理，提供幂等键、状态查询或可证明的安全重复语义。选择 timeout 必须来自延迟/SLO预算和负载验证；不得用无来源的统一常数。依据：[Deadlines](https://grpc.io/docs/guides/deadlines/)。

**RG06｜取消｜Skill MUST。** 规定用户取消、deadline 超时和客户端断连分别可见的终态；服务处理器必须监听取消并停止本地计算、下游 RPC、流生产与持有资源的任务。取消不等于事务回滚或撤销已提交副作用，契约说明结果不确定时怎样查询。依据：[Cancellation](https://grpc.io/docs/guides/cancellation/)。

**RG07｜自动 retry｜Skill MUST。** 每个方法声明可重试 status、最大尝试数（含首次调用）、指数退避上下限/抖动、总 deadline、重试节流和 request buffer 上限；说明幂等或服务端去重证据。gRPC 收到 response headers 后调用已 committed，不再自动 retry。未声明安全重放的有副作用 RPC 不配置 retry。Google AIP-194 只针对 unary 且仅建议无意外副作用、非事务方法；不得套在流式调用。依据：[Retry](https://grpc.io/docs/guides/retry/)、[AIP-194](https://google.aip.dev/194)。

**RG08｜Hedging｜使用 hedging 时的 Skill MUST。** 列出重复并发请求数、发出间隔、可容忍的失败 status、取消其他副本的行为、总 deadline 和服务端幂等/副作用保证，并把放大流量纳入容量预算。hedging 对同一请求发多份副本，首个成功响应获胜；它只适用于服务能承受并发副本且副作用有安全约束的操作。不要把默认 `maxAttempts` 或 gRPC 实现硬上限当服务目标。依据：[Request hedging](https://grpc.io/docs/guides/request-hedging/)、[Service Config](https://grpc.io/docs/guides/service-config/)。

**RG09｜Flow control｜采用 gRPC streaming 时的 Skill MUST。** 指明自动或手动流控模式、读写并发模型、缓冲容量、最大单条消息、慢消费者时暂停/拒绝/丢弃/合并哪一种，以及应用层 ACK 何时表示已处理。gRPC transport 的 write 成功仅说明框架接管数据，不表示网络送达或业务提交。若双方同步写满而不读，协议可能死锁；样例要覆盖慢读端和双向同时写。实际大小/窗口按目标库、代理和部署限制列证据，不发明统一值。依据：[Flow control](https://grpc.io/docs/guides/flow-control/)。

**RG10｜Keepalive 与 health｜配置长连接时的 Skill MUST。** 分别描述 transport PING、health-check RPC 和应用 heartbeat 的目的，选定空闲间隔、超时、允许无活动 RPC 的策略和服务端限制；不可用 keepalive 推断服务健康。与服务所有者协调参数，覆盖代理/LB idle timeout，避免紧密 PING 造成拒连或负载。连接丢失会令进行中的流失败，未发送数据可能丢失，故仍需流恢复契约。依据：[Keepalive](https://grpc.io/docs/guides/keepalive/)、[Health checking](https://grpc.io/docs/guides/health-checking/)。

**RG11｜Service Config｜使用客户端服务配置时的 Skill MUST。** 把配置绑定到具体 target 与 method；标注解析来源、默认/覆盖顺序、未知字段行为和未支持客户端的 fallback。retry、hedging、timeout、wait-for-ready、load balancing、health check 彼此组合后仍须受一个端到端 deadline 和负载预算约束；用实际客户端解析配置并断言 effective config。依据：[Service Config](https://grpc.io/docs/guides/service-config/)。

**RG12｜传输安全｜Skill MUST。** 写清 TLS/mTLS、凭据来源与轮换、身份映射、每个方法的授权、metadata/log redaction、传输目标及代理信任边界。gRPC 官方提供 TLS/credential APIs，不替 API 设计者决定主体、权限和秘密生命周期。认证失败与授权拒绝分别建模；证据至少包含未认证与越权拒绝契约。依据：[Authentication](https://grpc.io/docs/guides/auth/)。

**RG13｜限额｜Skill MUST。** 对 request headers、单条消息、整次调用累计 bytes、并行流、每主体速率、服务器最大连接/时长分别给配置来源、超限 status/close 行为、重试提示和观测项。不要把官方某语言/服务的默认值推广到所有实现；无服务端或代理配置证据时列为发布前置未决。依据：[Metadata](https://grpc.io/docs/guides/metadata/)、[Keepalive](https://grpc.io/docs/guides/keepalive/)、目标运行库文档。
