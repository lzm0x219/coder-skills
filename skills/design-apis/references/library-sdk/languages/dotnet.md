# .NET 公共 API 映射

适用：目标消费者使用 .NET library/framework。按目标 TFM、语言版本、运行时及是否承诺 binary compatibility 核验；P/Invoke 另读 [原生互操作](../native-interop.md)。

- **成员与扩展：** 方法名用动作词，属性不隐藏显著工作。公开 interface 难以安全演化，应比较 interface、抽象基类、组合和可选能力；virtual member 会约束后续实现，新增前检查所有可覆盖点、调用前后条件及派生类旧行为。来源建议：[Interface Design](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/interface)、[Virtual Members](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/virtual-members)。
- **异步/TAP：** I/O bound 公开异步方法返回 `Task`/`Task<T>` 或按目标版本使用 `ValueTask`；按生态命名约定核验 `Async` 后缀和同步对应关系。公开 `CancellationToken` 并定义取消传播；取消不代表回滚已发生的服务副作用。事件 handler 需按事件设计指南定义订阅、线程及异常传播。
- **dispose：** 持有 IDisposable/IAsyncDisposable 资源的公开类型说明所有权转移、重复 Dispose 和 dispose 后调用；异步释放如会等待必须暴露异步释放协议。终结器不是一般性的主要资源关闭入口。
- **版本兼容：** 按目标 .NET framework design guidelines 和真实 consumer 检查公共 API；分源码兼容、程序集加载、行为与序列化兼容。不能仅以 API surface diff 证明行为兼容。
- **检查：** 对各承诺 TFM 构建独立消费者；存在继承/接口扩展时加入旧 derived type/implementer；承诺 binary compatibility 时运行 API compatibility 工具及旧程序集加载检查。

主要依据：[Framework Design Guidelines](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/)、[TAP](https://learn.microsoft.com/en-us/dotnet/standard/asynchronous-programming-patterns/task-based-asynchronous-pattern-tap)、[Dispose Pattern](https://learn.microsoft.com/en-us/dotnet/standard/garbage-collection/implementing-dispose)。其中 design guidelines 是 Microsoft 生态建议，不等同 C# 语言规范。
