# Proto / gRPC 可执行设计样例

主契约为 [candidate.proto](candidate.proto)，对照[已发布旧定义](v1.proto)和[错误重用编号的反例](broken.proto)。验证器使用固定版本 `grpcio-tools==1.84.0`、`grpcio==1.84.0`、`protobuf==7.36.2` 生成并编译 Python 客户端/服务端；不修改全局环境或项目依赖。

## RPC 行为契约

| 方法 | 形态 | 输入与结果 | 错误/恢复 | deadline、取消与重试 |
| --- | --- | --- | --- | --- |
| `GetProfile` | unary | `id` 必填；返回 Profile | 空值 `INVALID_ARGUMENT`；不存在 `NOT_FOUND`。`UNAVAILABLE` 仅读操作按服务配置最多 2 次；其他状态不自动重试 | 客户端给出调用 deadline；deadline 到期为 `DEADLINE_EXCEEDED`，服务端停止工作。真实写操作须另行定义幂等键/状态查询，因为超时结果可能未知 |
| `WatchProfiles` | server streaming | `id` 必填；按单调 `sequence` 发更新；正常结束表示服务端已完成本次快照 | 任意终态状态必须在已交付消息后仍可观察；消费端不能把已收到部分消息误判为完整成功 | 客户端取消后服务端停止生产。首个消息到达后流已提交，本例不会从头自动重放；恢复须用 sequence 游标重新订阅并去重 |

认证/授权、TLS 身份、生产错误详情 schema、流缓冲上限、业务数据保留期及重连游标的持久化均依服务环境确定，本 fixture 不虚构其实现。测试的 `127.0.0.1` loopback 仅验证代表性语义，不证明生产网络、安全或负载行为。

## 消息演进契约

旧字段 `legacy_name = 2` 删除后保留编号与名称；新 `display_name = 3` 使用显式 presence，可区分缺失和显式空字符串。`reputation = 4` 同样显式 presence。旧二进制消息被新定义读取时，旧字段不会自动迁移到 `display_name`；候选消息被旧定义读取时，旧消费者保留已知字段，但不能读取新字段。二进制未知字段保留行为由生成运行时决定，需独立断言。

ProtoJSON 单独评估：字段名进入 JSON，因此删除/改名可能破坏解析；新字段默认不被旧 JSON parser 接受，除非明确启用 ignore-unknown（并接受丢失字段）；int64/uint64 在 JSON 中按规范使用字符串映射；有 presence 的显式零值应序列化并可往返。`broken.proto` 把旧编号 2 分给 `display_name`，Protobuf 编译器允许它编译；跨版本 descriptor 检查必须拒绝它，不能把“可编译”误当兼容。

可执行验证覆盖：真实 `protoc` 生成、隔离的 v1 生成消费者编译并调用 candidate loopback 服务、正反向 binary 与 ProtoJSON 消费、presence 和 unknown-field 行为、错误编号反例、loopback unary 重试、deadline/服务端取消、stream 中途 `UNAVAILABLE` 最终状态，以及收到首条消息后没有错误地从头重放。运行：

```sh
rtk proxy python3 tests/design-apis/checks/verify_rpc.py
```

必要时将 fixture 目录作为参数传入：`rtk proxy python3 tests/design-apis/checks/verify_rpc.py --fixtures path/to/rpc-profile`。

规则依据：gRPC [Core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/)、[Status codes](https://grpc.io/docs/guides/status-codes/)、[Deadlines](https://grpc.io/docs/guides/deadlines/)、[Cancellation](https://grpc.io/docs/guides/cancellation/)、[Retry](https://grpc.io/docs/guides/retry/)、[Flow control](https://grpc.io/docs/guides/flow-control/)；Protobuf [Best practices](https://protobuf.dev/best-practices/dos-donts/)、[Field presence](https://protobuf.dev/programming-guides/field_presence/)、[ProtoJSON](https://protobuf.dev/programming-guides/json/)、[Cross-version runtime guarantee](https://protobuf.dev/support/cross-version-runtime-guarantee/)；需遵循 Google API 设计时另核对 [AIP-194](https://google.aip.dev/194)（自动重试）与 [AIP-158](https://google.aip.dev/158)（分页）。这些 AIP 只对采纳该 API 设计指南的项目构成约束。
