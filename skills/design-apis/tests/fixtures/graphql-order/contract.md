# 部分失败 GraphQL 契约样例

主契约是 [schema.graphql](schema.graphql)。`order(id: ID!)` 是读取；不存在时返回 `null`，无权限时解析器返回 `null` 和 `errors`，具体权限策略仍须项目决定。正常查询为 `query { order(id: "42") { id note legacyNote } }`；`legacyNote` 供旧查询迁移，不能在客户端仍使用时删除。`note` 解析失败时应返回 `order.id`、`note: null` 和指向 `order.note` 的错误路径。调用方读取 `errors` 后按业务决定是否补查 `note`。

[broken.graphql](broken.graphql) 是故意的反例：删除旧字段会使旧查询校验失败，且将 `note` 改为 `String!` 会让解析错误向上冒泡、使整个 `order` 为 `null`。本样例用实际 GraphQL 执行验证传播；真实解析器、授权和查询成本限制尚未验证。依据：[GraphQL September 2025 规范](https://spec.graphql.org/September2025/)。
