# HTTP API 设计规则

适用：普通 HTTP 请求/响应。固定项目版本；GraphQL 执行另按 [GraphQL](graphql.md)，投递另按 [Webhook](webhooks.md)。等级见主 Skill。「设计」是本项目交付要求，「生态」是指定组织建议，均不冒充 IETF 强制条款。

子页等级与来源性质统一按[共享规则](common.md#规则等级)解释。

## 方法、结果与失败

**H01｜所有操作｜MUST 按可见效果选方法。** GET/HEAD 不承载请求者要求的写入；PUT 表达目标资源状态的创建/替换，DELETE 表达解除目标资源与当前功能的关联，不要求物理擦除所有历史信息。PUT/DELETE 和安全方法保持幂等的预期效果，响应无需相同。POST/PATCH 安全重试另有契约。业务取消、归档等动作须说明实际意图，不能仅凭“幂等”选 DELETE。证据：方法、资源关联、副作用、重复请求。依据：协议，[RFC 9110 §9](https://www.rfc-editor.org/rfc/rfc9110.html#section-9)。

**H02｜所有响应｜MUST 使状态与 HTTP 语义一致。** 201 说明新资源定位；202 表示已接受但处理尚未完成，不保证最终执行，不能作为业务完成或持久提交的证明；204 无响应内容。401 包含适用的 WWW-Authenticate challenge；已认证但权限不足可用 403，隐藏资源按项目策略可用 404。证据：成功/失败、实际 HTTP 响应和错误优先级。依据：协议，[RFC 9110 §15](https://www.rfc-editor.org/rfc/rfc9110.html#section-15)。

**H02 的异步观察门槛｜普通 HTTP 长任务设计。** 当调用者需要获知业务终态或恢复未知结果时，Skill MUST 定义查询、回调或其他可消费的观察方式，按 H08 给出终态与失败恢复合同。RFC 9110 §15.3.3 建议 202 的表示描述当前状态并指向或包含状态监视器，这不是每个 202 必须携带业务结果或观察入口的协议强制。绑定到其他协议时先按 C03/C04 核对该 profile：例如 [MCP Streamable HTTP 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports#sending-messages-to-the-server) 对已接受的 JSON-RPC notification/response 要求 `202` 且无主体；不得为满足普通长任务设计添加其未定义的 RPC 响应或强加任务查询入口。通知接受与业务完成分别判断。依据：HTTP 状态语义与采用的协议绑定；观察/恢复门槛是 Skill 设计要求。

**H03｜所有输入｜MUST 明确 HTTP 载体和边界。** 路径、查询、主体、头各有职责；明确媒体类型、编码、序列化和实际采用的 400/415/422。字段缺失/null/精度/单位/未知值按[共享数据契约](common/data.md)CD02–CD15 分析。证据：OpenAPI schema 与正反输入；schema 校验不证明业务/授权行为。依据：设计；格式，[OpenAPI 3.1.1](https://spec.openapis.org/oas/v3.1.1.html)。

**H04｜错误｜MUST 给稳定类别和恢复动作。** 可重试、修输入、权限、结果未知可区分。采用 RFC 9457 时用 application/problem+json，status 若出现与实际状态一致，以 type 识别类别，不解析 detail。证据：错误 schema 与消费代码。依据：设计；采用时的格式，[RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html)。

## 状态与成本

**H05｜条件请求｜MUST 落实比较与优先级。** If-Match 强比较；条件失败不覆盖写入，按契约返回 412 或规范允许且已确认操作成功的响应。正常权限/输入检查优先于前置条件。条件 GET 的 If-None-Match 弱比较，命中为无内容的 304。缺少必要条件另定策略。证据：旧版本、弱 ETag、缺头、组合错误。依据：协议，[RFC 9110 §13](https://www.rfc-editor.org/rfc/rfc9110.html#section-13)。

**H06｜重试写入｜MUST 定义去重与未知结果恢复。** 键作用域、同键不同输入、并发重复、保留期、失败缓存和响应丢失的查询方式明确。仅加 Idempotency-Key 不足。证据：首次/重发/冲突/过期。依据：设计；生态参考 [AIP-155](https://google.aip.dev/155)，字段沿用项目。

**H07｜分页｜MUST 定义遍历承诺。** 默认/最大页大小、排序、cursor 与筛选绑定、过期、终止标志、并发变更保证具体。空页不必是终点；cursor 不替代授权。证据：普通/空中间页/结束/变筛选/旧消费者。依据：设计；生态参考 [AIP-158](https://google.aip.dev/158)，不强制未采用的字段名。

**H08｜长任务｜MUST 定义状态机。** 接受、执行、成功、失败、取消竞争、查询入口、终态结果/错误、保留期和轮询间隔可消费。超时不自动等于失败；取消不自动回滚。分别说明停止执行、删除查询记录和回收结果的效果与时间；项目若将这些动作绑定须明确，不由方法名互相推断。仅改变执行状态并保留任务资源时 SHOULD 采用明确的取消操作。采用 Google long-running Operations 时，Cancel 与 Delete 按其不同语义处理；自有 `/jobs/{jobId}:cancel` 是可选 Google 风格，不是 HTTP 标准唯一路径。证据：202/终态/未知结果/取消竞争、取消后能否查询及结果保留。依据：设计；生态参考 [AIP-151](https://google.aip.dev/151)。

**H09｜缓存/限流｜MUST 给实际策略。** 缓存列新鲜度、验证器、Vary 和共享范围，private/no-store 按不同语义选；429 列限制范围，能给等待时间时才提供 Retry-After。证据：私有响应、缓存验证与恢复。依据：协议，[RFC 9111](https://www.rfc-editor.org/rfc/rfc9111.html)、[RFC 6585](https://www.rfc-editor.org/rfc/rfc6585.html)。

**H10｜PATCH｜MUST 定补丁格式与原子性。** 媒体类型、缺失/null/删除明确；整份补丁成功或不应用，重试/并发保护另定。证据：多项补丁的关键失败。依据：协议，[RFC 5789 §2](https://www.rfc-editor.org/rfc/rfc5789.html#section-2)。

## 契约与演进

**H11｜OpenAPI｜MUST 校验主契约和样例。** 固定版本、路径参数、operationId、请求/响应、安全和头字段；schema 校验正反样例，另查执行语义。证据：文件和工具版本/输出。依据：格式，[OpenAPI](https://spec.openapis.org/oas/v3.1.1.html)。

**H12｜HTTP 公开演进｜修改已有入口、schema、行为或安全策略时。** 按[共享演进契约](common/evolution.md)CE01–CE07 核对旧消费者的输入/响应、错误/重试、权限与默认行为；HTTP 额外将 server/base URL 与 operation path 合并为最终 URL，逐项比对完整入口。未授权的 `/v1` 等前缀也是入口变更。兼容结论依据原始请求/消费者和迁移证据，不能仅由 schema diff 或作者声明推出。名称 SHOULD 沿用项目领域约定。依据：设计；生态，[AIP-180](https://google.aip.dev/180)。

## 按分支读取的规则

H01–H12 保持原规则身份。以下材料按触发条件读取；没有触发的 API 形态不要求套用对应生态约定。

| 触发条件 | 阅读 | 原规则扩展 |
| --- | --- | --- |
| 需要建模资源、集合、生命周期、软删除、恢复、批量或自定义动作 | [资源与动作](http/resources.md) | H01、H08、H12 |
| 有集合查询、过滤、排序、字段投影或分页 | [集合查询](http/collections.md) | H03、H07 |
| 操作异步执行、取消、重试、去重或响应可能丢失 | [异步与重试](http/async-retry.md) | H02、H06、H08 |
| 传输文件/大表示、支持 Range、内容协商或缓存 | [表示与传输](http/representations.md) | H03、H05、H09 |
| 接受凭据、租户/对象标识、用户定义字段，或有公开错误体 | [安全与错误](http/security-errors.md) | H02、H03、H04、H09 |
| 浏览器需从跨源 origin 调用 API | [浏览器跨源策略](http/browser-security.md) | H02、H03 |
| 输出 OpenAPI、多个版本或生命周期/弃用承诺 | [契约描述与演进](http/contract-evolution.md) | H11、H12 |

规则用 RFC 的 MUST/SHOULD 描述协议责任；AIP/Azure 属于仅在明确采用相应配置时生效的生态建议；“本设计要求”是本 Skill 的评审门槛，不声称行业统一字段、路径或数值。

按[协议交付](protocol-deliverables.md)提供规则证据。[条件更新样例](../../../tests/design-apis/cases/http-profile/contract.md)及扩展场景见[测试索引](../../../tests/design-apis/README.md)。
