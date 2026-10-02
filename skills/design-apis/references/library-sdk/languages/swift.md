# Swift 公共 API 映射

适用：目标消费者是 Swift module/package。按最低 Swift 编译器、平台和 library evolution 设置核验；C/Objective-C 边界另读 [原生互操作](../native-interop.md)。

- **调用点：** 在真实调用表达式中审查 external argument labels。参数标签应让表达式读作清晰语句；省略标签仅在惯例明确且不损失语义时使用。初始化器标签同样是调用契约。来源规范建议：[Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/) 的 “Promote Clear Usage”“Strive for Fluent Usage”。
- **命名/成员角色：** 方法名表达动作；属性表示稳定、低成本的值或状态。会 I/O 或显著计算的操作用方法表达；mutating/nonmutating 与值/引用语义应让调用者能预测修改对象。
- **错误与异步：** 采用 `throws` 表达失败；将可恢复类别建为稳定错误值，文案不作为机器接口。用 `async` 表达挂起；取消检查与任务结构不会自动保证底层 I/O/服务副作用停止，须说明取消映射。
- **值类型与协议扩展：** 值类型的复制/共享引用嵌套需分清。公开 protocol 是第三方实现契约；添加 requirement 前评估下游 conformer、默认实现和 ABI/source compatibility。使用 `@available`、availability annotations 和弃用消息时对目标平台逐项检查。
- **Resilience：** Swift library evolution 模式会影响跨模块可见的布局/穷举保证。公开 enum、struct 布局与 ABI 承诺按发布模式及 Swift 版本核验，不从“编译成 framework”推断稳定 ABI。
- **检查：** 用独立 Swift module consumer 编译调用点；若承诺 binary compatibility，使用目标发布配置的 ABI/API diff 工具及旧编译二进制加载检查。

主要依据：[Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/)、[Swift Library Evolution](https://www.swift.org/blog/library-evolution/)、[Swift Package Manager Documentation](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/)。第一份是语言生态设计建议；ABI 行为以目标 Swift 版本和构建模式核验。
