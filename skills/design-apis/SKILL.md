---
name: design-apis
description: 设计、演进或评审调用者可见的 API 契约：服务协议、库/SDK/框架、消息、实时流、机器调用 CLI 和公开查询接口。
---

# 设计 API 契约

设计调用者可以依赖的输入、结果、失败和恢复行为。内部存储不直接成为外部契约；按下面流程交付可实现、可评审的候选。

## 1. 固定范围与事实

读取[共享工作规则](references/common.md)，确认调用者、场景、稳定性承诺、完整入口和采用版本。已有接口对照契约源、实现、真实调用方与相关测试；事实、候选和未知分别记录。

出口 → 既有依赖可定位，候选不冒充事实；关键缺项注明阻断的结论，可设计的行为有有界候选。

## 2. 按接口类型读取规则

类型路由以本表为准。复合接口按控制面、数据面及各侧消费者分别匹配，读取命中顶页，再沿条件指针读取分支。

| 公开调用形态 | 读取 |
| --- | --- |
| HTTP 请求/响应 | [HTTP](references/http.md) |
| GraphQL schema、查询、变更 | [GraphQL](references/graphql.md)；有 HTTP 绑定再读适用 HTTP 规则 |
| RPC 方法和消息 | [RPC](references/rpc.md)；IDL、编码、框架按实际采用分支 |
| 库、SDK、框架程序接口 | [程序接口](references/library-sdk.md) |
| broker/event bus 的事件 | [事件](references/events.md) |
| 发送或接收 HTTP callback | [Webhook](references/webhooks.md)与适用 HTTP 规则 |
| 长连接、持续流、订阅恢复 | [实时与流](references/realtime.md)；GraphQL subscription、streaming RPC 同时读原生执行规则 |
| 脚本/其他进程依赖的命令 | [自动化](references/automation.md) |
| 对外承诺的 SQL、视图、查询模板或 DSL | [声明式查询](references/query.md)；纯内部 SQL 不因此成为公开 API |

按共享页的触发条件读取数据、安全与演进；用[维度与遗漏检查](references/coverage.md)核对边界。未收录协议查其权威版本并补差异。规则等级由[共享规则](references/common.md#规则等级)解释，版本争议用[一手索引](references/sources.md)定位原条款。

出口 → 每条公开边界有适用分支；不适用有理由，缺规范或关键决定保持未决。

## 3. 形成可观察契约

按 C05 写每个操作的输入、结果、副作用、失败和恢复，再核对跨操作的身份、状态、并发、限额及生命周期。用正常与关键失败/边界消费路径对照需求；已有接口加入旧消费者，响应丢失、重投、并发、部分成功与权限撤销检查恢复。

出口 → 消费者能判断已发生效果、未知结果和下一步；字段、授权和兼容行为具体，样例遵守同一契约。

## 4. 核对规则与证据

按 [C06](references/common.md#tracking)逐条关联需求、触发规则、契约与消费证据。跨页同名 ID 标明文件 scope；核对命中 MUST，记录 SHOULD 的实质偏离，先修与规则冲突的样例。

出口 → 每个适用要求都有行为与证据状态，无法核实的事实或行为保持未决。

## 5. 交付与核验

具体协议、实时、CLI、查询提案按[协议交付](references/protocol-deliverables.md)，程序接口按[声明与消费者交付](references/library-sdk/deliverables.md)，沿用项目主契约。概念讨论、现状评审或语言未定时交付对应模型与结论；用户明确要求只输出文档时遵守该范围。

用户要求实现时继续完成代码和适当验证；设计任务交付可评审契约。按[统一状态判据](references/common.md#delivery-status)分别报告设计完整性、证据层级与项目接受，不把拟议合同或静态通过写成上线事实。

出口 → 主契约、消费者和报告一致，交付符合任务范围，结论不超出证据。
