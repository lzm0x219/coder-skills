# Proto 字段演进与 RPC 样例

主契约为 [candidate.proto](candidate.proto)，对照[已发布旧定义](v1.proto)和[错误重用编号的反例](broken.proto)。`ProfileService.GetProfile` 是 unary 读取；`id` 为空返回 `INVALID_ARGUMENT`，找不到返回 `NOT_FOUND`，成功返回 `Profile`。客户端设置 2 秒 deadline；`DEADLINE_EXCEEDED` 后可重试读取，`UNAVAILABLE` 仅重试读取且由客户端限制次数为 2。服务端观察取消，避免继续消耗资源。授权方式与错误详情格式尚待项目决定。

旧字段 `legacy_name = 2` 删除后保留编号与名称；新 `display_name = 3` 可区分缺失和空字符串。旧二进制消息可被新定义读出 `id`，但旧字段值不会自动迁移成 `display_name`。新消息供旧定义读取时旧客户端看不到新字段。反例把编号 `2` 赋给新语义，解析器可编译但违反演化约束，必须由旧新契约对比拒绝。ProtoJSON、生成代码和真实 gRPC 未在此样例验证。依据：[Proto3 字段删除与保留](https://protobuf.dev/programming-guides/proto3/)、[gRPC 状态码](https://grpc.io/docs/guides/status-codes/)、[Deadline](https://grpc.io/docs/guides/deadlines/)。
