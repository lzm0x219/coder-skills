# RPC API 设计规则

先确认 RPC 框架、序列化格式及版本。下列 gRPC 与 Protocol Buffers 规则只在项目采用相应技术时生效；其他 RPC 框架使用其官方契约文档。

## gRPC 调用语义

1. 根据交互形态选 unary、服务端流、客户端流或双向流。为流定义何时结束、取消后如何处理、消息上限及背压；gRPC 只保证单次 RPC 内各方向消息的顺序，不保证跨 RPC 全局顺序。依据：[gRPC Core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/)、[Flow Control](https://grpc.io/docs/guides/flow-control/)。
2. 为调用方区分错误的下一步：`UNAVAILABLE` 可考虑重试当前调用，`ABORTED` 可能要求重试更大事务，`FAILED_PRECONDITION` 需先修正状态。不要把业务失败统一写成 `UNKNOWN`，也不要让客户端解析人类可读错误文案。依据：[gRPC Status Codes](https://grpc.io/docs/guides/status-codes/)。
3. 约定 deadline、取消、重试和超时后如何查询操作结果。deadline 到期不能证明服务端没有执行；重试策略仍需核对操作幂等性。gRPC 的透明重试或配置重试不替业务契约作保证。依据：[Deadlines](https://grpc.io/docs/guides/deadlines/)、[Retry](https://grpc.io/docs/guides/retry/)。

## Protocol Buffers 演进

4. 已发布字段不能改用旧编号或随意更换类型。删除字段时保留编号，并考虑保留名称；删除枚举值时保留其编号。服务端与客户端可能混用新旧版本，也可能读取历史序列化数据。依据：[Proto Best Practices](https://protobuf.dev/best-practices/dos-donts/)。
5. 设计字段时明确“未提供”与零值是否必须可区分；若必须区分，选择项目所用 Proto 版本支持的 presence 表达。枚举的零值用于未指定状态，不让它承担真实业务含义；新增枚举值时检查旧客户端对未知值的处理。依据：[Proto3 Language Guide](https://protobuf.dev/programming-guides/proto3/)。
6. 分别检查二进制 wire、ProtoJSON 和生成代码的兼容性；二进制可解析不代表 JSON 字段名、枚举文本或调用方源码兼容。对 `oneof`、字段类型和默认行为的调整，先在项目的具体语言与编码链上验证。依据：[ProtoJSON Format](https://protobuf.dev/programming-guides/json/)、[Proto3 Language Guide](https://protobuf.dev/programming-guides/proto3/)。

## 落地时填写

每个 RPC 方法在 `.proto` 或项目等价 IDL 中落实以下契约：

| 项 | 必须给出的具体值 |
| --- | --- |
| 方法 | 完整服务/方法名；unary、客户端流、服务端流或双向流 |
| 消息 | 请求与响应类型；字段编号、是否可区分缺失与零值、取值约束 |
| 结果 | 正常完成条件；业务失败对应的状态码及可机读详情（若框架支持） |
| 时间 | 客户端 deadline、服务端取消处理、超时后查询结果的方式 |
| 重试 | 可重试的状态与方法、最大尝试或由谁决定；写入的去重方式 |
| 流 | 结束条件、消息大小、背压与中途失败时已处理消息的语义 |

状态码不能只列名称：`UNAVAILABLE` 要说明重试是否可能重复写入；`ABORTED` 要说明需要重做哪一段读改写事务；`FAILED_PRECONDITION` 要指出先修正什么状态。若无法安全重试，明确写“不自动重试”。

Proto 演进示例（仅在字段 `2` 曾发布、现已删除时使用）：

```proto
message Account {
  string id = 1;
  reserved 2;
  reserved "legacy_name";
  optional string display_name = 3;
}
```

字段 `2` 不得再分配；`display_name` 的 presence 能区分未传与空字符串。验收时用旧客户端与新服务端、新客户端与旧服务端各走一条消息路径，并按项目实际编码分别验证二进制、ProtoJSON 与生成代码；不能只跑 `protoc` 语法检查。

可复查的[Proto 演进与编号重用反例](../tests/fixtures/rpc-profile/contract.md)检查二进制读取与字段编号；它没有覆盖 ProtoJSON、生成代码和真实 gRPC。
