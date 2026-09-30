# 程序接口原则的语言映射

适用：把跨语言规则落实到目标语言、运行时与发布工具链。这里的语言机制只是示例；版本敏感语法与 ABI 以目标版本的一手资料核验。

## 同一原则的语言映射

下表仅用于选取宿主语言的惯用机制；不表示某一种机制跨语言更优。每项仍须查项目所用语言版本与官方文档。

| 普遍目标 | 可能的语言级表达 |
| --- | --- |
| 结构化失败 | Rust `Result<T, E>`；Go `(T, error)`；Java/C# 异常或结果类型；Swift `throws`/`Result`；Kotlin 异常或 sealed result；Python 异常；TypeScript 判别联合或 Promise rejection。 |
| 区分正常缺失与失败 | Rust `Option`/`Result`；Swift/Kotlin 可选类型或 sealed 状态；Go 显式 `ok`/`error`；Python `None` 加明确异常或专用结果；TypeScript 判别联合。 |
| 资源寿命 | C++ RAII、`unique_ptr`；Rust 所有权与 `Drop`；C# `IDisposable`；Java `AutoCloseable`；Python context manager；Go 显式 `Close`；JS/TS 显式关闭或适用环境的 disposal 机制。 |
| 防止相同底层值混传 | Rust newtype、Swift struct、Kotlin value class、Java/C# 值对象、C++ 强类型包装、Go 定义类型、Python `NewType`/运行时包装、TypeScript 品牌类型或对象。 |
| 公共/内部边界 | Rust `pub`、Go 大写导出、Python `__all__`/下划线、Kotlin explicit API、TypeScript 包 `exports`/声明文件；所有语言还需文档稳定性标签。 |
| 扩展点 | Java/C# 接口或抽象类、Rust trait、Swift protocol、Kotlin interface、Go 小接口、Python protocol/ABC、TypeScript interface/structural type；C++ 抽象基类或模板约束。 |
| 异步与取消 | 宿主语言 Future/Promise、协程或回调；取消令牌、上下文或任务取消机制必须映射到一致的可观察语义。 |

## 具体提案的可检查载体

下表给出[设计期交付](deliverables.md)的常见落点，不要求项目改用表中的构建工具。优先使用项目已经采用的包结构、语言版本与检查命令；尚无工具链时标记静态检查未验证。声明只需足以描述公开表面，消费者只需编译/静态检查，不需要伪造运行时实现。

| 目标语言 | 候选公开契约与消费者 | 设计期检查示例 |
| --- | --- | --- |
| TypeScript / JavaScript | 导出类型与 `declare` 签名或 JSDoc 类型，加独立消费者文件；包 `exports` 已确定时验证该导入。 | 使用项目配置运行 `tsc --noEmit`；仅检查相对候选文件时，不声称包导出已验证。 |
| Python | `.pyi`、Protocol 或带类型注解的公开模块，加消费者文件。 | 使用项目选定的 mypy/pyright 配置检查；运行时导入与动态行为另验。 |
| Go | 导出类型/接口与消费者，维持真实包路径；若拟议构造器或函数需要函数体，按[设计期交付](deliverables.md)使用隔离的编译占位或标为未验证。 | `go test` 或项目构建命令编译候选包与消费者；编译占位不证明运行行为。 |
| Rust | `pub` 类型/trait 与消费者模块，遵守 crate 的 feature 和可见性边界；需要实现体的入口同样隔离占位或标为未验证。 | `cargo check` 对应 feature 组合；未构建的 feature 标为未验证。 |
| Java / Kotlin / C# | 公开 interface、数据类型和消费者编译单元。 | 使用项目构建任务编译目标模块与消费者；二进制兼容仍须另验。 |
| Swift / C++ | 公开 protocol、头文件或模块接口，加调用侧编译单元。 | 使用项目的 typecheck/编译命令检查目标平台；ABI 与链接结果另验。 |

语言机制的细节需核验相应一手资料：[Rust](https://rust-lang.github.io/api-guidelines/checklist.html)、[Swift](https://www.swift.org/documentation/api-design-guidelines/)、[Kotlin](https://kotlinlang.org/docs/api-guidelines-introduction.html)、[.NET](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/)、[C++](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)、[Go](https://go.dev/doc/effective_go)、[Python](https://peps.python.org/pep-0008/#public-and-internal-interfaces)、[TypeScript](https://www.typescriptlang.org/docs/handbook/declaration-files/library-structures.html)。
