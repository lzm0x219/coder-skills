# JSON-RPC 2.0

仅在使用 JSON-RPC 2.0 envelope 时命中。[官方规范](https://www.jsonrpc.org/specification)定义消息对象语义，不定义 HTTP/WebSocket framing、认证、批次调度顺序、连接恢复或应用业务错误；将这些分别交给实际 transport 和业务契约。

**RJ01｜Request envelope｜规范 MUST。** request 有 jsonrpc=2.0、精确区分大小写的 method、可选 params；params 若存在必须为 array 或 object。定义每个 method 的参数 schema、缺项/多余项和类型 coercion 策略。invalid request 与 method not found 使用规范 error code，不能返回形似正常 result 的错误体。证据：有效、非法 params、未知方法正反例。

**RJ02｜ID correlation｜规范 MUST。** 带 id 的 Request 要用同值在 Response 中关联；客户端对并发请求维护 ID→pending call map，拒绝/隔离未知、重复、已取消 ID 响应。避免 null ID 与小数 ID（规范 discourages），选 string 或整数并定义唯一范围与复用周期。id 缺失表示 notification，不等同 id:null。依据：规范 §4、§4.1。

**RJ03｜Notification｜规范 MUST。** 不含 id 的请求是 notification，服务端不得回 Response；客户端知道自己不会获得成功或失败确认。凡需交付保证、权限错误可见、调用方重试或审计确认的动作，不能设计成 notification，改用有 ID 的 request 或另行定义 durable command/ack。依据：规范 §4.1。

**RJ04｜Response XOR｜规范 MUST。** Response 包含 jsonrpc、相同 id，并且 result 与 error 恰有一个；没有结果值时显式使用 JSON null，不能省略 result。error object 要有 integer code、message，data 如使用必须定义类型和兼容语义。解析器按规范拒绝 result/error 同时存在或同时缺失的对象。依据：规范 §5。

**RJ05｜Batch｜使用 batch 时的 Skill MUST。** 定义最大 batch 长度/bytes、成员是否并发、逐成员错误与 notification 省略响应规则；JSON-RPC 不要求响应数组顺序与请求一致，客户端必须以 ID 关联而不能按数组位置匹配。空 batch 是 invalid request，notification-only batch 返回空 response array。超限和部分成员错误的行为给反例。依据：规范 §6。

**RJ06｜Transport binding｜Skill MUST。** 对 HTTP、WebSocket、stdio 等分别定义 framing、content type、body envelope、一次 connection 可并发的 ID、timeout/cancel 及重连后的 pending call 行为。基础规范不定义可靠投递；断线时未收到 response 的 side effect 可能已执行，使用幂等键/结果查询解决未知结果，不盲目重发。安全/认证和 CORS/Origin 绑定在 transport 专页。依据：[JSON-RPC 2.0](https://www.jsonrpc.org/specification)未规定 transport。

**RJ07｜错误目录｜Skill MUST。** 区分 parse error、invalid request、method not found、invalid params、internal error 与应用自定义错误 code；对每个业务 code 给稳定 data schema、是否可重试、调用方动作和未知 code fallback。message 面向诊断，不供机器解析；data 不暴露堆栈、凭据或内部 SQL。依据：规范 §5.1 及安全设计门槛。

**RJ08｜版本与能力｜Skill MUST。** 保持 method 和参数名的大小写/拼写精确兼容；新增可选参数定义旧服务忽略/拒绝行为，新 result 字段定义旧 client 的 parser strategy。需要协商扩展时使用明示能力方法或 transport subprotocol，不以猜测服务端版本分支。记录 old/new consumer 正反例。
