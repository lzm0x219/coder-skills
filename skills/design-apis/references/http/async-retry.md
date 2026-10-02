# HTTP 异步操作与重试

触发：请求在单个交互时限内不能可靠完成、结果可独立查询、调用方需要取消，或请求/响应丢失可能造成重复副作用。仅返回 `202` 不构成可消费的异步契约。

**H23｜接受后的定位｜普通 HTTP 业务长任务需观察终态或恢复未知结果时。** 返回可持久查询的操作 URI（通常通过 `Location` 或明确响应字段）及稳定 operation ID；定义初始状态、查询方法、授权范围、状态新鲜度与未知/过期 URI 行为。操作状态应至少区分进行中、成功、失败和已取消；每个终态定义结果/错误形态和结果资源链接。若只提供轮询，给建议间隔/退避与 Retry-After 的规则；数值由服务容量与用户体验确定。响应丢失时，客户必须能用请求标识或已知资源找到既有操作，不能盲目重新创建。证据：202、Location、轮询状态迁移、完成资源读取、未知 ID。操作 URI、可查询状态与恢复路径是本 Skill 的长任务设计门槛；202 的 HTTP 语义不强制通用查询 URI。采用通知或其他协议绑定时先按 C03/C04 和其 profile 处理，不能制造未定义的 RPC 响应。参考：状态语义 [RFC 9110 §15.3.3](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.3.3)；生态 [AIP-151](https://google.aip.dev/151)、[Azure async request-reply](https://learn.microsoft.com/en-us/azure/architecture/patterns/async-request-reply)。

**H24｜取消竞态｜操作可取消时。** 定义取消的授权、可取消状态、取消请求接受与真正停止的差别、与成功/失败竞态时的胜者及终态、已产生副作用是否补偿。取消响应若表示“已请求”则不能伪装为“已停止”；轮询结果必须让客户端分辨取消待处理与已取消。取消后操作记录/结果保留遵守 H16 生命周期。不可取消阶段要返回确定的冲突/前置条件错误和当前状态。证据：运行中、刚完成、已失败、重复取消、取消后查询。参考：[AIP-136](https://google.aip.dev/136)、Google [Operations proto](https://github.com/googleapis/googleapis/blob/master/google/longrunning/operations.proto)；其中 Cancel 与 Delete 分别是取消和移除操作记录。

**H25｜重试分类｜客户端可能重发时。** 对每个状态码/错误码声明 retryable 与否、是否确定没有副作用、退避/抖动及停止条件；429/503 的 Retry-After 若给出需定义可解析形式。只对幂等请求或具备请求去重契约的操作自动重试；传输超时发生在服务端是否收到请求未知时，先查操作/请求身份再重放。不得仅凭“5xx”一概重试，也不得将长时间轮询的操作 deadline 与单次 HTTP 连接 timeout 混为一值。证据：连接前失败、服务已提交但响应丢失、限流、可重试服务故障、永久验证错误。参考：[RFC 9110 §9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2)、[AIP-194](https://google.aip.dev/194)。

**H26｜请求去重｜创建/动作非天然幂等且需安全恢复时。** 定义 key 在调用方/操作/资源范围中的唯一性、有效期、输入摘要绑定、同 key 同参的原响应或当前状态、同 key 异参冲突、并发首请求仲裁、失败时是否记录，以及窗口过期后客户端如何避免重复副作用。服务若不提供此能力，明确调用方如何安全确认结果或标注无法自动重试。不要臆造统一 `Idempotency-Key` header 要求或保留期限。证据：并发重复、成功后响应丢失、同 key 异参、过期边界。参考：[AIP-155](https://google.aip.dev/155)；该 AIP 的 request_id 是生态模式，不是 HTTP 标准。

**H27｜资源预算｜有轮询、批量或长流时。** 分别设置连接/单次请求/总操作的超时边界，说明服务的最大接受时限、客户端 deadline 取消传播、轮询退避、单租户并发/速率预算及超限恢复。各数值由运行容量和服务等级证据决定；资料没给数值时保留待定值与验证方法。证据：慢处理、慢消费者、deadline 越界、取消传播、重复轮询与限额恢复。参考：Azure [LRO guidance](https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design#implement-asynchronous-methods)、[AIP-151](https://google.aip.dev/151)。
