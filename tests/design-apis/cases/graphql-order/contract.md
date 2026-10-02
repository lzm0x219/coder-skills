# 部分失败 GraphQL 契约样例

主契约是 [schema.graphql](schema.graphql)，操作与变量向量在 [operations.graphql](operations.graphql) 和 [variables.json](variables.json)。`order(id: ID!)` 是读取；不存在时返回 `null`。`legacyNote` 仍可供旧查询使用，必须先检查旧消费者并完成迁移再删除。`note` 解析失败时，字段可空，因此响应保留 `order.id`，返回 `note: null` 和指向 `order.note` 的错误路径。调用方必须检查 `errors`，然后决定是否补查 `note`。

`UpdateOrderInput.note` 和 `priority` 都有默认值：省略 `note` 得到 `"default note"`，省略 `priority` 得到 `1`；显式传 `null` 对可空 `note` / `displayLabel` 保留为 null，对 `priority: Int! = 1` 则报变量/输入错误。变量转换失败属于 request error，响应不得包含 `data`，且 mutation resolver 不得执行。规则为 GraphQL 强制语义，由真实 `graphql-js` schema 构造、校验和执行验证。

此夹具定义候选容量预算：一个操作最多包含两个顶层 `order` 查询；别名仍分别计数。两别名查询有效，三别名查询由显式 GraphQL validation rule 拒绝。该局部预算只是待容量测试确认的设计提案；`graphql-js` 不自动限制成本，也不等于服务端已启用该规则。生产环境还应按实际 schema / resolver 成本核算嵌套列表、分页上限、batching 和主体速率限制。不得直接把这个单一根字段上限当成完整的查询复杂度模型。

[broken.graphql](broken.graphql) 是故意的反例：删除旧字段会使 `OldConsumer` 校验失败；将 `note` 改为 `String!` 后，解析错误会越过 `Order` 并使整个 `order` 为 `null`。这些结果由 GraphQL 官方参考实现 `graphql-js` 实际 schema/validator/executor 验证。真实解析器、授权、在线容量预算和生产查询限制未验证。

依据：[GraphQL September 2025 规范—Input Objects](https://spec.graphql.org/September2025/#sec-Input-Objects)、[Non-Null](https://spec.graphql.org/September2025/#sec-Non-Null)、[Response](https://spec.graphql.org/September2025/#sec-Response)、[Deprecation](https://spec.graphql.org/September2025/#sec--deprecated)、[GraphQL 官方 Security 指南](https://graphql.org/learn/security/)。该安全指南提出的复杂度、查询深度与速率限制属于实现建议，不是 GraphQL wire 协议自动提供的保证。
