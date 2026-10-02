# GraphQL API 设计规则

适用：schema、操作和响应。固定规范与执行器版本；HTTP 绑定按采用版本另查。等级和来源性质见主 Skill。

子页等级与来源性质统一按[共享规则](common.md#规则等级)解释。

## 类型、输入与执行

**G01｜schema｜MUST 使用正确类型位置与副作用边界。** 参数/输入字段用输入类型，输出字段用输出类型。读取用 query；副作用只在顶层 mutation 字段发生，其串行执行不代表整个 mutation 自动原子。证据：SDL、调用及事务边界。依据：协议，[GraphQL September 2025](https://spec.graphql.org/September2025/)。

**G02｜输入｜MUST 区分省略、null 与默认值。** 非空且无默认值才不可省略；非空有默认值可省略，显式 null 仍拒绝。可空字段省略和 null 可有不同业务含义。变量转换失败不执行解析器。跨协议的默认/精度/单位约束见[共享数据契约](common/data.md)CD02/CD04/CD06；GraphQL resolver 对输入对象只获得成功 coercion 后存在的字段。证据：省略/null/缺省/非法变量。依据：协议，[输入对象](https://spec.graphql.org/September2025/#sec-Input-Objects)。

**G03｜输出/列表｜MUST 走查 null 传播。** 对象、列表和元素分别决定可空；非空错误向最近可空父级传播，可能令全部 data 为 null。证据：实际 data 与 errors.path。依据：协议，[执行错误](https://spec.graphql.org/September2025/#sec-Handling-Execution-Errors)。

**G04｜错误｜MUST 区分请求错误与执行错误。** 校验/变量转换失败（包括未知输入字段、变量提供的非法 null）不执行解析器，响应没有 data；执行错误可与部分 data 共存。文档中的错误阶段、错误类别和副作用与实际输入/执行测试对齐。业务错误可用结果类型或安全的 extensions.code，提供处理动作。证据：执行次数、部分结果与消费者。依据：协议加设计，[响应](https://spec.graphql.org/September2025/#sec-Response)。

**G05｜scalar/oneOf｜MUST 固定可消费行为。** 自定 scalar 说明序列化、输入转换、精度和格式；specifiedBy 指向实际规范。执行器支持才采用 oneOf，其字段可空且无默认值，输入恰有一个非空字段。证据：正反输入。依据：协议，[类型系统](https://spec.graphql.org/September2025/#sec-Type-System)。

## 成本与演进

**G06｜集合｜MUST 定义分页与上限。** 排序、默认/最大页大小、cursor 范围和失效明确；采用 Relay 时遵守 edges/pageInfo 及分页参数规则。证据：首/续/尾页和非法页大小。依据：设计；采用时的生态，[Relay Connections](https://relay.dev/graphql/connections.htm)。

**G07｜可组合查询｜MUST 落实成本与权限策略。** 选深度、复杂度、列表长度、时间预算或可信文档，写出配置、超限错误与字段权限；alias/批量请求计入成本。无容量证据的数值标为候选。证据：普通/超限/重复 alias。依据：设计；官方建议，[Security](https://graphql.org/learn/security/)。

**G08｜演进｜MUST 用旧操作复查。** 删除字段、增加必填参数、收紧输入、输出可空性与枚举变更逐项评估。若新字段声明为旧字段的同义替代，明确同来源、单位、值与 null 语义；局部 resolver 样例也要在更新后同次选择新旧字段核对一致性，不能只证明旧 operation 仍可解析。非空且无默认值输入不能直接 deprecated；删除前核实迁移。弃用说明 SHOULD 指向替代调用。证据：旧查询、新消费者和可执行的同义字段不变量。依据：协议加设计，[弃用](https://spec.graphql.org/September2025/#sec--deprecated)。

**G09｜订阅｜MUST 定义消费生命周期。** 顺序范围、重连位点、断线事件、授权失效、取消和背压落实到传输；schema 不自动提供持久投递保证。证据：重连/重复/取消。依据：设计；[订阅执行](https://spec.graphql.org/September2025/#sec-Subscription)。

**G10｜HTTP 绑定｜MUST 按采用版本核验。** GraphQL over HTTP 是工作草案；核对媒体类型和请求错误/执行结果状态。普通 HTTP 错误封装不能替代执行结果。证据：HTTP 请求/响应。依据：采用时的草案，[GraphQL over HTTP](https://http-spec.graphql.org/draft/)。

## 按分支读取的规则

G01–G10 保持原规则身份。按 API 所采用的能力读取分支：

| 触发条件 | 阅读 | 原规则扩展 |
| --- | --- | --- |
| 新增/修改公共类型、列表/连接、输入、标识或自定义 scalar | [Schema 与输入建模](graphql/schema-input.md) | G01–G05、G08 |
| GraphQL 字段返回可变或可能长大的集合 | [集合与游标](graphql/collections.md) | G06 |
| 有多层查询、可重复字段、列表、批量操作或不可信客户端 | [执行、权限与需求控制](graphql/execution-security.md) | G03、G04、G07 |
| 向浏览器/移动端交付 HTTP、订阅、文件、缓存或增量响应 | [传输与订阅](graphql/transport-subscriptions.md) | G06、G09、G10 |
| 采用 Apollo Federation v2.9 | [Federation 与组合](graphql/federation.md) | G01、G07、G08；其他组合技术只套用该技术自己的固定版本规范 |
| 变更已有 schema、弃用或发布多个 schema 版本 | [Schema 与输入建模](graphql/schema-input.md) §演进 | G08 |

GraphQL 规范只约束 GraphQL 语言/schema/执行语义；传输、授权、成本门槛和 Federation 的具体要求分别来自被采用的传输规范、服务安全策略或明确选用的 Federation 版本。本 Skill 的设计门槛不冒充 GraphQL 核心规范。

按[协议交付](protocol-deliverables.md)给 SDL、操作、变量、响应与规则证据。[部分失败样例](../../../tests/design-apis/cases/graphql-order/contract.md)及扩展场景见[测试索引](../../../tests/design-apis/README.md)。
