# Go 公共 API 映射

适用：目标消费者是 Go module/package。源码兼容按项目声明的 Go 支持政策核验；cgo/共享库 ABI 另读 [原生互操作](../native-interop.md)。

- **包名与导出：** 导出标识符由大写首字母决定；包名进入调用点，通常用简短小写单词，避免 `util`、`common` 等职责空泛名。方法常用 `Read` 而非冗余 `GetRead`，但领域动作名服从既有惯例。来源：[Effective Go: Names](https://go.dev/doc/effective_go#names)、[Go Code Review Comments: Getters](https://go.dev/wiki/CodeReviewComments#getters)。
- **zero value 与构造：** 若类型可安全使用，设计使 zero value 有用；若必须初始化，提供显式构造函数并让未初始化调用返回可检查错误或保持不可导出。不要只靠文档要求调用隐藏 `Init` 顺序。
- **接口与错误：** 通常由消费方定义窄接口；不要为了 mock 预先导出宽接口。用 `%w`/`errors.Is`/`errors.As` 保留稳定分类与根因，避免调用者解析错误字符串。包装错误应提供操作上下文。来源：[Go Code Review Comments: Interfaces](https://go.dev/wiki/CodeReviewComments#interfaces)、[Errors](https://go.dev/blog/go1.13-errors)。
- **context 与并发：** 需要取消/截止时间的 I/O 操作将 `context.Context` 作为首参数传递且不存入结构体；说明同一 client 的并发安全、调用是否尊重 context、返回错误如何区分取消与超时。取消 context 不保证远端操作回滚。
- **兼容：** 若声明 Go 1 Compatibility Commitment，遵循其范围；源码兼容不等于跨 Go 版本编译后二进制兼容。检查 public package 的旧 source consumer 和旧已编译二进制是否属于项目承诺；不能混为一个结果。
- **检查：** 独立 module consumer 运行 `go test`/`go vet`，在最低支持 Go 版本运行；记录 cgo 目标编译与链接状态。

主要依据：[Effective Go](https://go.dev/doc/effective_go)、[Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)、[Go 1 Compatibility](https://go.dev/doc/go1compat)、[Go 1.13 Errors](https://go.dev/blog/go1.13-errors)。前两份是惯例建议，兼容承诺仅适用于 Go 官方声明的范围。
