# GraphQL API 设计规则

适用于 GraphQL schema、操作和响应契约。先确认服务实现支持的 GraphQL 规范版本、现有 schema、已知查询和客户端；GraphQL 经 HTTP 传输时，HTTP 绑定另按项目采用的规范核对。不要把普通 HTTP API 的错误包裹规则直接套到 GraphQL 执行结果。

## 规范约束

1. 用 `query` 表达读取、`mutation` 表达有副作用的操作；仅在项目实际提供订阅时设计 `subscription`。字段参数与输入对象必须使用输入类型，响应字段使用输出类型。依据：[GraphQL 规范](https://spec.graphql.org/September2025/)。
2. 把 `!` 当作调用者可依赖的承诺：非空输入不可省略或传 `null`，非空输出若发生执行错误会向父级传播 `null`。在可能局部失败的位置谨慎标非空，走查错误传播会影响到哪一层。依据：[GraphQL 规范的 Non-Null 与执行规则](https://spec.graphql.org/September2025/)。
3. 执行阶段可以同时返回部分 `data` 与 `errors`；客户端不能只因收到数据就忽略错误。对规范允许弃用的字段、参数、输入字段或枚举值使用 `@deprecated` 并提供迁移说明；必填且无默认值的输入不能直接标为弃用。确认调用方完成迁移后再考虑删除。依据：[GraphQL 规范](https://spec.graphql.org/September2025/)。

## 设计与验收

4. 从真实查询反推类型、字段和参数，说明身份、权限与成本边界。对列表确定分页、排序和游标有效范围；项目采用 Relay Connections 时遵守其 `edges`、`pageInfo`、`first/after` 等契约，未采用时不要强制套用。依据：[Relay Cursor Connections Specification](https://relay.dev/graphql/connections.htm)。
5. 控制客户端可组合查询带来的资源成本：按项目风险定义深度、复杂度、列表大小或执行时间限制，并明确超过限制的错误表现。限制值须由服务容量与客户端需求确定，不写通用固定值。
6. 对旧查询和新查询分别验证 schema、变量输入、空值传播、局部错误与弃用字段。GraphQL over HTTP 的工作草案仍可能变化；若项目采用它，按项目固定版本核对媒体类型和 HTTP 状态，不把草案中的建议写成所有 GraphQL 服务的强制规则。参考：[GraphQL over HTTP 工作草案](https://http-spec.graphql.org/draft/)。

## 落地时填写

每个新增或变更字段要交付 SDL 或项目等价的 schema 定义，并写清以下值：

| 项 | 必须给出的具体值 |
| --- | --- |
| 字段 | 所属类型、名称、返回类型；`!` 和列表元素是否可空 |
| 参数 | 名称、输入类型、必填性、默认值；省略与显式 `null` 是否不同 |
| 行为 | 查询还是变更、身份与字段级权限、失败时是 `null` 还是业务结果类型 |
| 集合 | 顺序、最大页大小、游标或偏移语义；若采用 Connection，遵守其字段契约 |
| 成本 | 深度、复杂度、列表长度或执行时间中实际采用的限制及超限错误 |

变更已有 schema 时，至少把下列情况与已知查询逐一对照：删除/改名字段、新增无默认值的非空参数、收紧输入类型、改变输出可空性、新增枚举值、改变权限或解析器副作用。先运行旧查询的校验与代表性执行，不用“schema 能编译”替代兼容性判断。

示例：

```graphql
type Query { order(id: ID!): Order }
type Order { id: ID!, note: String }
```

可复查的[GraphQL 查询和错误传播样例](../tests/fixtures/graphql-order/contract.md)同时保留旧查询，并让错误触发 `null` 冒泡。

若 `note` 的解析失败，结果可以保留 `order.id`，令 `note` 为 `null` 并在 `errors` 中给出 `path: ["order", "note"]`。若把 `note` 错设成 `String!`，错误可能继续使 `order` 为 `null`。验收时实际运行两种失败路径，而不只检查 SDL 语法。

```json
{
  "data": { "order": { "id": "42", "note": null } },
  "errors": [{ "message": "note unavailable", "path": ["order", "note"] }]
}
```
