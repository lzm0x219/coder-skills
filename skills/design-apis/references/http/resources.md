# HTTP 资源、动作与批量操作

本页只在 API 以资源为主要交互模型时读取。AIP 是 Google API 生态约定；选用其中模式时按该 AIP 完整执行。下列“设计门槛”是本 Skill 对提案的要求，不是 RFC 的 MUST。

## 资源模型

**H13｜资源身份｜设计门槛。** 对每个可被调用方独立读取、修改、删除或引用的概念，定义资源类型、规范 URI、稳定标识、父子归属和可观察表示。集合路径表达资源类型，成员路径表达某一个资源；标识应在资源生命周期内稳定，不能把可变显示名默认为主键。若实体只是计算结果或短期状态，明确它是独立资源还是响应投影，并说明可否单独授权/保留。未建模为资源的动作不得伪装成可读取的持久对象。证据：规范 URI、跨操作同一性、所有权及旧客户端 URL。参考：[AIP-121 resource-oriented design](https://google.aip.dev/121)、[AIP-122 resource names](https://google.aip.dev/122)、[Azure REST API design](https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design)。

**H14｜路径命名｜设计门槛。** 将资源名词放入路径，把筛选/排序/分页表达为查询条件；只在目标生态有约定时采用其复数、父路径、大小写或 `:verb` 格式。避免在同一资源上用路径动词重复 HTTP 方法已经表达的 CRUD 行为。若动作无法表达为标准资源方法，写明为何新资源/标准方法不适用、动作作用对象、可观察结果和重放语义，再选项目既有 custom-action 形式。没有行业统一的 `/v1` 放置方式或冒号动作格式；须评估完整 URL 兼容性。证据：同领域现有路径表、标准方法映射和最终合并后的完整 URL。参考：[AIP-130](https://google.aip.dev/130)、[AIP-136](https://google.aip.dev/136)、[AIP-180](https://google.aip.dev/180)。

**H15｜动作与幂等｜POST custom action 命中时。** 定义动作前置状态、成功后状态、重复调用效果、冲突状态、响应定位及调用方确认未知结果的方法。POST 不因名字叫 `cancel`、`archive` 或 `retry` 就天然可安全重发；若需要安全重试，为请求定义稳定身份/幂等窗口和同键异参处理，或让动作自然满足重放语义。条件不满足时不得让消费者盲目重发。响应丢失时提供可读状态查询或明确“不确定且不可自动恢复”。安全范围/权限按[共享安全规则](../common/security.md)CS01–CS03 逐操作定义。证据：首次、并发重复、同 ID 异参、处理成功但响应丢失。参考：[RFC 9110 §9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2)、[AIP-155](https://google.aip.dev/155)。

**H16｜删除生命周期｜有删除、归档、撤销或恢复时。** 区分从当前 API 视图解除关联、软删除、永久清除、归档和执行取消；逐项定义 GET/LIST 可见性、名称是否可复用、授权检查顺序、恢复窗口及结果/审计记录保留。若声明遵循 Google AIP-164，软删除资源默认从 List 隐藏，Get 仍返回资源，并按该 AIP 定义 undelete/expunge 与错误；其他 API 另行明示自己的这些行为。永久清除须说明副作用范围。取消仅影响任务执行时保留任务资源查询语义。不得从 HTTP DELETE 推断物理擦除；也不得把异步取消写成资源删除。未知保留期和 ID 复用策略标为待产品决策。证据：状态迁移表、重复删除/恢复、权限失败与过期后读取。参考：[RFC 9110 §9.3.5](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.3.5)、Google [AIP-135](https://google.aip.dev/135)、[AIP-164](https://google.aip.dev/164)、[AIP-151](https://google.aip.dev/151)。

## 批量写操作

**H17｜批量语义｜一请求作用于多个成员时。** 在契约中明确原子性是“全成或全败”还是允许逐项部分成功；同时明确是否先验证全部输入、并发冲突如何处理、结果是否按输入索引/稳定 ID 关联、失败项可否安全单独重试。全原子模式失败时不得留下未声明的部分写入；部分成功模式必须返回每项成功/失败及可恢复动作，整体状态不得掩盖成功项。定义最大项数、请求体/处理时限的来源及超限结果；未经过容量验证的上限标为候选。若选择 Google AIP-234 profile，同步 batch update 保持原子；只有异步 Operation 模式才用其 partial-success 形态，并通过原请求索引关联每项错误。不要承诺数据库事务语义，除非边界覆盖所有副作用。证据：混合成功/失败、重复成员、乱序结果、整体失败/重放。参考：Google [AIP-234 Batch Update](https://google.aip.dev/234)、[AIP-235 Batch Delete](https://google.aip.dev/235)；这些规定其 Google API 形态，并非通用 HTTP 标准。
