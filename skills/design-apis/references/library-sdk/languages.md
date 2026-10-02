# 程序接口原则的语言映射

目标语言已定时，从下表读取相应分支；比较不同语言表达时再看后面的机制表。语法、ABI 和工具行为均按项目实际版本核验，语言示例不成为跨语言要求。

## 选定目标后的具体映射

目标语言已定且正在设计签名、错误、扩展或兼容边界时，只读该语言的专属页；涉及 FFI 时再读 [原生互操作](native-interop.md)，包解析再读 [包与平台产物](packaging.md)。将目标语言惯例转成候选签名和消费者检查。

| 目标语言 | 条件读取 |
| --- | --- |
| Rust | [Rust APIs](languages/rust.md)：可见性、错误/缺失、trait 与枚举演化、feature、借用/所有权。 |
| Swift | [Swift APIs](languages/swift.md)：调用点标签、初始化、错误与异步、resilience。 |
| Go | [Go APIs](languages/go.md)：包边界、zero value、接口消费、errors/context 与兼容承诺。 |
| Java / Kotlin | [JVM APIs](languages/jvm.md)：Java binary compatibility、Kotlin 默认参数/属性与多平台公开 API。 |
| .NET | [.NET APIs](languages/dotnet.md)：成员可见性、interface/virtual 成员、TAP 与框架兼容。 |
| TypeScript / JavaScript | [TypeScript / JavaScript APIs](languages/typescript.md)：声明/运行时同构、module resolution、类型公开和 async iterator。 |
| Python | [Python APIs](languages/python.md)：公开模块、异常、Protocol/ABC、asyncio cancellation/task lifetime。 |

## 具体提案的可检查载体

主契约与静态检查按[设计期交付](deliverables.md)。采用项目工具链：TS 导出类型/`declare` 或 JS JSDoc，Python `.pyi`/Protocol，Go 导出类型/接口，Rust `pub` 类型/trait，JVM/.NET 公开 interface/数据类型，Swift protocol 或 C++ 头文件/模块接口；各自配独立消费者。需要函数体的 Go/Rust 入口采用隔离的编译占位，或保持未验证，不能删掉需要的构造器。

具体检查命令和条件在语言子页；Swift/C++ 使用项目 typecheck/编译命令。编译、类型检查与真实包导出、ABI、链接及运行分别报告；没有工具链标未验证，不另造构建项目。

## 比较语言表达时

以下机制帮助比较候选形态，不表示某一种机制跨语言更优；选定后以该语言分支和实际版本为准。

| 普遍目标 | 可能的语言级表达 |
| --- | --- |
| 结构化失败 | Rust `Result<T, E>`；Go `(T, error)`；Java/C# 异常或结果类型；Swift `throws`/`Result`；Kotlin 异常或 sealed result；Python 异常；TypeScript 判别联合或 Promise rejection。 |
| 区分正常缺失与失败 | Rust `Option`/`Result`；Swift/Kotlin 可选类型或 sealed 状态；Go 显式 `ok`/`error`；Python `None` 加明确异常或专用结果；TypeScript 判别联合。 |
| 资源寿命 | C++ RAII、`unique_ptr`；Rust 所有权与 `Drop`；C# `IDisposable`；Java `AutoCloseable`；Python context manager；Go 显式 `Close`；JS/TS 显式关闭或适用环境的 disposal 机制。 |
| 防止相同底层值混传 | Rust newtype、Swift struct、Kotlin value class、Java/C# 值对象、C++ 强类型包装、Go 定义类型、Python `NewType`/运行时包装、TypeScript 品牌类型或对象。 |
| 公共/内部边界 | Rust `pub`、Go 大写导出、Python `__all__`/下划线、Kotlin explicit API、TypeScript 包 `exports`/声明文件；所有语言还需文档稳定性标签。 |
| 扩展点 | Java/C# 接口或抽象类、Rust trait、Swift protocol、Kotlin interface、Go 小接口、Python protocol/ABC、TypeScript interface/structural type；C++ 抽象基类或模板约束。 |
| 异步与取消 | 宿主语言 Future/Promise、协程或回调；取消令牌、上下文或任务取消机制必须映射到一致的可观察语义。 |
