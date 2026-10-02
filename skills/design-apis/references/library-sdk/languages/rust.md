# Rust 公共 API 映射

适用：目标消费者是 Rust crate API。先按目标 `rustc`、MSRV、Cargo features 和 crate 类型核验；C ABI 另读 [原生互操作](../native-interop.md)。

- **结果与缺失：** 用 `Result<T, E>` 表达调用者可处理的失败，用 `Option<T>` 表达单一正常缺失；两者组合时写清错误和 `None` 的差异。若 API 可被 `?` 组合，错误应保留可观察来源且避免字符串匹配成为唯一机器契约。来源建议：[Rust API Guidelines, Interoperability / Dependability](https://rust-lang.github.io/api-guidelines/checklist.html)。
- **可见性与默认配置：** 检查每个 `pub` 项是否确属稳定 API；列出默认与非默认 feature 下可见项，不能把 feature-gated API 当成 crate 默认表面。为公共类型考虑稳定构造/访问器而非公开字段，前提是类型需要维持不变量。来源：[Rust API Guidelines, Future Proofing](https://rust-lang.github.io/api-guidelines/future-proofing.html)、[Cargo Features](https://doc.rust-lang.org/cargo/reference/features.html)。
- **枚举与 trait 演化：** 调用者可能穷举 `enum` 时新增 variant 可能破坏下游编译；需决定封闭匹配还是使用 `#[non_exhaustive]` 等目标版本机制。公开 trait 新增必需方法会影响第三方实现者，应拆 trait、适配器或有意识地给安全默认实现；检查 Cargo SemVer 分类并编译旧 consumer。
- **所有权与转换：** API 名称/签名要区分借用、分配和消费所有权；按惯例使用 `as_`（廉价借用/视图）、`to_`（转换/通常可能分配）、`into_`（消费 self）仅在与实际行为一致时。迭代器的惰性、副作用和借用期应由类型签名及文档共同表达。
- **异步与取消：** Rust `Future` 通常通过 drop 停止本地轮询；这不自动撤销已发出的远端副作用。明确 drop/cancel 对远端状态的影响；返回 stream 时写出终止错误与释放要求。
- **检查：** 从外部 crate consumer 分别 `cargo check` 默认 feature、被承诺的 feature 组合及 MSRV；旧消费者用前版 crate 源码/锁定依赖编译。检查通过不证明 ABI、运行时语义或未构建 feature。

主要依据：[Rust API Guidelines Checklist](https://rust-lang.github.io/api-guidelines/checklist.html)、[Cargo SemVer Compatibility](https://doc.rust-lang.org/cargo/reference/semver.html)、[Cargo Features](https://doc.rust-lang.org/cargo/reference/features.html)、[Async Book](https://rust-lang.github.io/async-book/)。这些 API Guidelines 是建议，不是 Rust 语言强制规则。
