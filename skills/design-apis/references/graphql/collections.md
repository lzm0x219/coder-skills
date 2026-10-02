# GraphQL 集合与游标

仅在字段返回可变或可能长大的集合时读取。GraphQL core 允许 list，但不规定分页模型；Relay cursor connection 是可选生态规范。

**G33｜有界集合｜集合可能无界或读取会产生可观成本时。** 不返回无界 list；设计字段参数与结果形状，使调用方每次只能获得有限页。给默认/最大条数、排序稳定性、下一页/上一页可达性、游标范围与失效策略。上限数值来自负载/成本与客户端需求测试，标注候选时说明压测场景；超限参数是 GraphQL request/coercion error 还是业务结果须固定。小型稳定枚举或配置表可用简单 list，但必须给出有界理由。证据：默认响应数受界、最大合法边界和声明阶段的超限拒绝；输入/准入错误不运行 resolver，业务拒绝可以由 resolver 返回，但须在昂贵读取和副作用前生效。参考：GraphQL.org [Security: Paginated fields](https://graphql.org/learn/security/#paginated-fields)、[Pagination](https://graphql.org/learn/pagination/)。

**G34｜Relay Connection｜选择 Relay cursor connections 时。** 按 Relay Cursor Connections Specification 定义 `{Name}Connection` 的 `edges` 与 `pageInfo`，edge 至少含 `node` 和 `cursor`，pageInfo 提供 `hasNextPage`/`hasPreviousPage`；参数使用选定 forward (`first/after`) 与/或 backward (`last/before`) 模式，并逐项定义是否可同时组合。游标不透明且绑定到排序和过滤上下文；cursor 失效、伪造或改筛选后复用时返回稳定的客户端错误/明确重启指引，不把游标作为授权。定义默认和最大 `first/last`、负数/零及超限行为。`totalCount` 是可选字段，须定义精确/估算及过滤口径；不能假定 Relay 要求它。证据：第一页、cursor 边界续读、反向页、空中间页、结束页、过滤变更/失效 cursor。依据：[Relay Cursor Connections Specification](https://relay.dev/graphql/connections.htm)；只在声明 Relay 风格时作为生态约束。
