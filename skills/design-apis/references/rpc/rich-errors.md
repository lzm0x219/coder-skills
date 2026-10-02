# R02：gRPC 结构化错误

仅在采用 Google richer error model 时读取。此页是 [R02](../rpc.md) 的条件细则，追踪时使用 `rpc:R02` 并保留本页位置。

## Wire 契约

错误 detail MUST 以 protobuf `google.rpc.Status` 封装：标准 trailing metadata key `grpc-status-details-bin` 携带序列化 Status，各细节放在 `Status.details` 的 `google.protobuf.Any` 中。自定义 trailer key 或裸 `ErrorInfo` 属于不同契约，不能作为该模型的实现证据。

定义稳定的 detail schema 与 reason/domain/metadata 版本语义。

## 消费与核验

调用者 MUST 用目标语言 rich-status helper 或等价实现读取：

1. 检查外层 gRPC status code/message 与嵌入 `Status.code/message` 一致。
2. 对 `Any` 做类型化 `Unpack`。
3. 仅在 detail 存在、类型正确且 code/message 一致时执行特定恢复动作；其余路径按已定义的普通状态处理。

Python 可用 `grpc_status.rpc_status.from_call`，由 `grpcio-status` 支持；该 helper 对 code/message 不一致抛 `ValueError`。

完成条件：规范编码/解析的 loopback 正例与错误封装负例均有证据，缺 detail、错误类型和 code/message 不一致的消费路径已核验。

## 来源

[gRPC Error handling richer model](https://grpc.io/docs/guides/error/) 规定 protobuf binary trailing metadata 机制；Python 行为依据官方 [`grpcio-status` v1.84.0 helper 实现](https://github.com/grpc/grpc/blob/v1.84.0/src/python/grpcio_status/grpc_status/rpc_status.py)。使用其他版本时核验对应实现。
