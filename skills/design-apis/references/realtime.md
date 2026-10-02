# 实时连接与推送 API

适用于连接建立后仍持续收发、推送、订阅、事件流、实时双向消息、断线重连或游标续传；按所选 transport 加载 [WebSocket](realtime/websocket.md)、[SSE](realtime/sse.md) 或 [HTTP streaming](realtime/http-streaming.md)。RPC streaming 是调用内的有界 RPC 生命周期，另按 [RPC 总则](rpc.md) 和对应框架分支设计；只有底层采用连续连接时才加载该连接协议分支。共同规则 RL01–RL12 适用，transport 专属标准不得互相套用。

## 共同设计门槛

**RL01｜生命周期｜Skill MUST。** 说明 bootstrap、身份认证、订阅建立、活跃、暂停、正常结束、服务端终止、客户端取消、过期和重连状态；对每个状态给触发、可见信号、可重试与资源清理动作。正常关闭与异常断开分开描述。

**RL02｜交付语义｜Skill MUST。** 对消息声明 best-effort、至少一次或业务去重后的效果；传输确认、客户端收到、应用处理、持久化提交是不同 checkpoint。需要 ACK 时定义 ACK 的准确含义、超时和重复处理。没有可持久 cursor/ack store 就不能声称断线无损或 exactly-once。

**RL03｜Envelope｜使用一连接承载多操作时的 Skill MUST。** 定义版本化 message envelope：消息种类、correlation/request ID、订阅/stream ID、event ID/cursor、payload type、错误、客户端/服务器终态。验证 request/response 对应、重复 ID 冲突、未知 kind/version、畸形 payload；仅 RFC 已定义的 frame/control 字段不得复用为业务字段。

**RL04｜顺序与并发｜Skill MUST。** 说明同一连接/订阅内排序保证、跨订阅/方向是否可乱序、并发 handler 规则和因重连产生的重复/跳跃处理。若依赖有序 cursor，明确它是单调序列还是不透明 token，不从字典序推断全局顺序。

**RL05｜Bootstrap 与恢复｜需要恢复时的 Skill MUST。** 定义 snapshot/bootstrap 的 watermark、cursor 所属资源与过滤条件、有效期、分页/追赶/live 切换无缝边界。cursor 缺失/过期/未来/过滤器变化时返回显式 reset/bootstrap 结果；客户端从快照 watermark 开始续订，不能静默从最新重开并漏数据。

**RL06｜Reconnect｜自动重连时的 Skill MUST。** 区分协议 transport 自动恢复和业务 subscription 恢复。列首轮随机延时、退避/上限、jitter、最大累计时长或需用户介入的认证/永久协议错误、计数何时重置。把所有阈值放进可达性检查：若单连接时长上限小于稳定计数重置时间，明确选择 connection rotation 后重置或有界总失败次数，防止永远到不了成功阈值。收到服务端 retry-after/关闭理由时定义优先级。

**RL07｜Backpressure｜Skill MUST。** 给每连接和订阅规定最大未消费数量/字节、写队列、最大单消息、慢 consumer 处置（暂停、拒绝、丢弃、合并、断开）的条件和可见原因；在用户端处理速率低于生产速率时给可验证的界限，避免无界内存。无标准统一 limit 时明确来源是服务配置并验证代理/runtime 实际限制，不造统一值。

**RL08｜心跳｜采用 heartbeat 时的 Skill MUST。** 区分 transport ping/pong、SSE comment、应用-level heartbeat 与健康状态；声明谁发、间隔来源、idle timeout、丢失几次判定、移动网络/代理影响。心跳只证明其路径上的连接响应，不能证明业务处理或服务健康。

**RL09｜Authentication/Origin｜Skill MUST。** 为握手/stream 请求说明认证在哪一步发生、凭据更新、会话失效后的 close/error 与恢复方式；浏览器场景按 cookie/Origin/CSRF 约束验证受信任来源。Origin 不是身份认证，非浏览器可伪造；不能仅凭允许 Origin 授权。更新凭据需重新握手时不可假定现存连接自动刷新。

**RL10｜Limits 与 abuse｜Skill MUST。** 定义连接配额、每身份并发订阅、消息帧/重组总消息大小、发送速率、buffer/queue、最大连接年龄/空闲时长、压缩与 CPU 限额的配置来源、拒绝方式及恢复动作。分别检查 client 与 server 限制，不把 RFC 建议或库默认值当所有部署通用值。

**RL11｜Evolution｜Skill MUST。** version subprotocol / endpoint / negotiated capability 中选择明确版本策略；定义新增 optional field、未知消息 type、必需新能力、旧 client 混部和弃用窗口。向未知版本传消息时要求安全忽略还是显式拒绝；协议 envelope/parser 对畸形和过大输入有限资源保护。

**RL12｜Observability｜Skill MUST。** 事件维度包括连接/订阅匿名 correlation ID、建立/关闭原因、恢复次数、cursor reset、队列高水位、ACK 延迟与 dropped/duplicate count；避免 token、完整 payload 和可识别敏感数据。日志和指标能把用户观察的 missing/duplicate 与服务端 retention/queue 行为联系起来。
