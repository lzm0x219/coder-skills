# Rust 审计 SDK：完整设计期案例

状态：**可供设计评审，尚未获设计接受**。这是虚构审计服务，不代表已核实的提供者能力。主契约是 [`src/lib.rs`](src/lib.rs)，调用方是 [`examples/consumer.rs`](examples/consumer.rs)。公开构造器和网络方法中有明确的 `unimplemented!` 占位：它们只用于 Rust 编译期验证，调用即会 panic，**不能当作 SDK 实现运行**。本案例补足 [BlobStore 扩展点小例](../rust-blob-contract/contract.md)无法覆盖的 SDK 客户端设计问题。

## 中性模型与命名

| 中性对象 | 本提案名称 | 依据与排除项 |
| --- | --- | --- |
| E1：持有配置并发起审计读取的客户端 | `AuditClient` | 这是 SDK 对象而非单次请求句柄；`AuditService` 易被误认为远端服务实现。名称是提案选择，非 Rust 规范的唯一要求。 |
| E2：一次读取的一页事件 | `EventPage` | 一次 `list_page` 只请求一页；不能用 `list_all` 暗示遍历完整事件流。 |
| E3：由响应给出的后续读取条件 | `ListEvents` / `next_request` | 继续游标属于原查询上下文，调用方不直接构造游标字符串；末页返回 `None`。 |
| E4：按需提供凭据的用户扩展点 | `CredentialProvider` | 用户可替换静态或轮换提供者；trait 与返回的 boxed future 均允许作 trait object 使用。 |

公开稳定候选仅是 crate 根模块中的类型、trait 和方法；没有已发布旧版。`Event.kind()` 返回开放字符串，调用方不能穷举服务未来新增的种类。`AuditErrorKind` 使用 `#[non_exhaustive]`，因此消费者必须有未知类别分支。Rust 官方 [API Guidelines](https://rust-lang.github.io/api-guidelines/checklist.html)建议检查构造器、常见 trait、错误文档、object safety 与私有字段；这些是设计指导，不是服务事实。

## 构造、状态和所有权

| 入口 | 拟议契约 | 失败与边界 |
| --- | --- | --- |
| `AccessToken::new(String)` | 消费传入字符串；`Debug` 只打印 `[REDACTED]`。提供者在每次请求尝试时返回一个新 token，便于轮换。 | 空值报 `TokenInputError::Empty`；不把凭据或提供者错误文本放进 SDK 错误。 |
| `AuditClient::builder(endpoint, Arc<dyn CredentialProvider>)` | 只保存配置，不读取凭据或发请求；builder 持有凭据提供者。`AuditClient` 可克隆，克隆共享配置与连接。 | `build()` 在网络前验证完整 HTTPS URL 与非零超时；默认整体预算 10 秒。如何选取 URL 解析器属于实现决策，当前占位代码尚未验证此行为。 |
| `PageSize::new(u16)` | 在本地验证 1..=100；`PageSize::DEFAULT` 是 50。`ListEvents::first_page` 要求已验证的大小。 | 0 或大于 100 由 `PageSizeError` 拒绝；不会悄悄截断。 |
| `EventPage::events()` / `next_request()` | 事件只借用本页，不能在页被丢弃后继续借用；下一页请求取得自己的值，保留页大小。 | `None` 唯一表示末页。不能通过公共字段伪造游标；游标过期由 `InvalidCursor` 报告，而非当作首页。 |

这里不开放客户端 `close()`：候选模型由拥有的客户端和运行时连接管理，丢弃最后一个克隆释放本地资源。**这只是拟议释放语义**；如果实际传输需要可观察的关闭失败或后台任务停止确认，就必须在接受设计前加入显式关闭接口，不能让 `Drop` 承载关键错误。`CredentialProvider` 是用户可实现的长期扩展点，正式发布后新增必需方法会破坏下游实现；优先采用新 trait 或默认方法，并检查其行为。Cargo 的[兼容性指南](https://doc.rust-lang.org/cargo/reference/semver.html)明确把向 trait 增加无默认实现的成员列为破坏性变更。

## 单页异步操作

`AuditClient::list_page(ListEvents)` 是异步操作；future 被轮询后依次获取本次凭据、发送最多一个读取请求、接收完整的一页响应。默认**不自动重试**。每次最多返回 100 项；`EventPage` 不保证跨页快照一致，因此遍历时可能出现重复或缺口。客户端可通过共享引用并发发起请求；同一个 `ListEvents` 值被消费，必要时调用方显式克隆。一次请求与另一请求的凭据、页状态和错误不互相覆盖。

整体 10 秒预算（或 builder 指定预算）从首次轮询开始，包含凭据提供者、连接、服务响应和完整页解码。超时返回 `Timeout`；在取得凭据前失败返回 `Credentials`；收到鉴权或限流响应分别为 `Unauthorized`、`RateLimited`；没有可判定响应的 I/O 问题为 `Transport`。服务给出不可接受的游标时为 `InvalidCursor`；其他已分类服务错误为 `Service`。本地 `PageSize` 错误发生在发请求前，不会变成远端错误。若截止时间到达时结果尚未完成，以 `Timeout` 结束；截止前已完成并分类的凭据或服务错误不再被后到的超时覆盖。`request_id()` 只在收到可用响应元数据时返回；`retry_after()` 仅在限流且服务提供合法非负等待时返回。错误文本和 `Debug` 不含 token。实际服务错误映射和竞态下的优先级仍需实现及协议核验。

丢弃 `list_page` future 表示调用方停止等待；不保证已发请求在远端撤销，也不承诺提供者内部工作立即停止。假设该操作只读取事件，重试不会产生写入副作用，但可能读到新的数据；默认重试次数是 0。限流后是否再发请求由调用方决定。消费者示例只读最多两页，并显式处理 `RateLimited`、`Unauthorized` 与未来未知错误，不会暗中无界收集。

## 验证、风险与下一步

`cargo fmt --check`、`cargo check --examples` 与 `cargo clippy --examples -- -D warnings` 可以检查候选声明和调用方的 Rust 语法、类型、trait object 使用、`Send` 约束及基础 lint。它们**不能**验证占位方法的构造行为、网络 I/O、凭据轮换、超时、取消、响应解析或资源回收。项目若要接受或实现本提案，还需确认真实服务术语、API 版本、鉴权权限、游标有效期、是否提供请求 ID、支持的 MSRV/运行时及跨页一致性，再替换占位并运行行为测试。
