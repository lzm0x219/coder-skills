# GraphQL 执行、权限与需求控制

适用：GraphQL server 执行任意/第一方 operation。核心规范定义解析、验证和执行；以下授权、需求控制和错误遮蔽是针对部署威胁模型的设计门槛/官方安全建议。

**G19｜GraphQL 授权执行路径｜schema 可通过任一路径返回受保护数据时。** 共用主体/租户/字段许可按[共享安全契约](../common/security.md)CS01–CS03 定义；GraphQL execution context 传递认证身份，field resolver 委托共享 business/data-access 授权层判定，不能只在根 query 验权。nested fields、node/global ID、alias、fragment、mutation、subscription event 都必须经过相同授权策略。batch/DataLoader 缓存至少按身份/租户隔离，避免一次授权结果跨主体复用。证据：对象经 root/nested/node/alias/batch 路径访问、两租户缓存隔离、越权 mutation 无副作用、撤权后订阅停止。参考：GraphQL.org [Authorization](https://graphql.org/learn/authorization/)、[Security](https://graphql.org/learn/security/)。

**G20｜未受信 operation 的需求控制｜客户端可提交任意文档时。** 选择并组合适用措施：每列表字段分页和最大页数、query/list depth、字段/alias breadth、同请求 operation batch 数、加权 complexity、速率或可信文档 allowlist。每条限制定义测量算法（含 fragment 展开、alias 单独计费、变量控制的 list size）、阈值来源、在何阶段拒绝、稳定错误码及用户恢复办法。拒绝发生在 resolver/副作用前；可信文档仅适用于能控制所有客户端发布流程的一方，不作为公开第三方 API 唯一保护。限额数值须由压力/成本数据支持并标注测量环境；官方指南没有普遍安全阈值。证据：超深、超宽、alias 重复、fragment 重用、变量最大 list、超复杂组合及边界合法操作。参考：GraphQL.org [Security: Demand Control](https://graphql.org/learn/security/#demand-control)、[trusted documents](https://graphql.org/learn/security/#trusted-documents)。

**G21｜resolver 成本与 N+1｜字段可能扇出查询或调用下游时。** 为字段标出数据源、预计 fan-out/单项代价、可批处理边界与缓存授权键；避免每个 list item 独立调用下游，并限制嵌套列表的乘积结果。把成本计入 G20 模型并观测真实 resolver 时间/下游调用数；只用 query depth 不足以代表实际成本。昂贵字段可独立限流或拆为显式分页/异步资源。证据：N 项输入时下游调用量有界、扩展 alias/list 后成本受预算拒绝、缓存不跨权限主体复用。参考：GraphQL.org [Performance](https://graphql.org/learn/performance/)、[Security](https://graphql.org/learn/security/#query-complexity-analysis)。

**G22｜GraphQL 错误呈现｜向调用方返回 request/execution error 时。** 敏感信息遮蔽和资源存在性政策按[共享安全契约](../common/security.md)CS05/CS10；保留 GraphQL 可定位的 `path` 与稳定 extensions code/trace ID，对部分 `data` 说明哪些字段失败。Parse/validation/coercion 错误与 resolver execution errors 分阶段呈现；不得把所有业务/系统失败映射为 HTTP 状态码，因为同一 execution result 可同时含 data 与 errors。内部栈/下游细节进入受控诊断而非公开错误。证据：无 data 的请求错误、带部分 data 的执行错误、跨环境敏感 detail 遮蔽与客户端恢复。参考：[GraphQL Security: Error messages](https://graphql.org/learn/security/#error-messages)、GraphQL [Response](https://spec.graphql.org/September2025/#sec-Response)。

**G23｜Introspection｜按运行环境/消费者约束控制 schema 探索时。** 明确内省策略按身份、网络边界或环境执行，并让授权保护 schema 中的敏感字段及数据。若选择关闭生产内省，说明目的仅为降低自动发现面；同时保留受控的 schema 发布/客户端生成途径，不声称此举隐藏 API 或替代授权、输入验证和需求控制。不得破坏 Federation router 所需的专用 subgraph schema endpoint。证据：匿名/认证/内部身份的 introspection 操作，普通字段错误提示，以及部署时 Federation 组合测试。参考：GraphQL.org [Security: Introspection](https://graphql.org/learn/security/#introspection)。
