# 远程服务 SDK 的程序接口

适用：SDK 包装远程服务、传输或长任务时。这里规定宿主语言调用者看到的行为；底层 HTTP/RPC 契约仍按对应 reference 核验。

## W. SDK 包装远程能力时

**W01｜条件｜MUST 定义客户端创建和配置范围。** 凭据、端点、代理、传输、超时、重试和关闭由谁持有；配置修改是否影响已创建客户端。例外/评审：无状态纯本地 SDK 不适用；同一客户端能否并发复用？

**W02｜条件｜MUST 区分本地验证、远端拒绝与传输失败。** SDK 错误模型保留调用方可恢复的信息，同时不把每个服务端字段无条件固定为跨语言接口。例外/评审：原始响应可作为明确标注的低层访问口；消费者如何判断应修正输入还是稍后重试？

**W03｜条件｜MUST 明确自动重试与幂等语义。** 按错误类别和操作副作用列出可重试条件；定义次数是否包含首次请求、退避与服务给出的等待时间、总超时预算，以及同一次逻辑操作的所有尝试是否复用同一幂等键。明确凭据获取、退避和传输分别是否计入尝试及总预算；提供者迟迟不返回时仍须有可观察的停止条件。响应丢失后不得把未知结果描述为失败。例外/评审：不自动重试也应说明；重复调用是否会重复扣费或创建资源？

**W04｜条件｜MUST 定义分页、批量和流的网络边界。** 一次迭代会否发请求、页大小如何控制、继续令牌如何取得与保存、每页失败如何呈现，以及服务支持时如何跨会话恢复，都要清楚；批量部分成功须可识别，流对象须有明确的释放方式。默认收集全部结果不得掩盖无界请求或内存成本。例外/评审：固定小结果可直接返回；调用方能否控制成本与中止？

**W05｜条件｜SHOULD 让各语言 SDK 在语义上一致、形态上地道。** 相同服务能力有一致的错误类别和资源含义，命名、异步、迭代与取消方式按宿主语言惯例表达。例外/评审：某语言缺乏等价机制时应写清差异；是否为追求跨语言外观一致牺牲可用性？

**W06｜条件｜MUST 记录服务版本与 SDK 版本的关系。** 服务存在可选择的 API 版本时，说明 SDK 支持和默认的服务版本、调用方能否选择、预览版与稳定版的边界；服务新增字段、废弃功能或鉴权方式变化时，说明未知值处理和迁移窗口。例外/评审：仅本地功能或服务无版本概念时不适用；新服务响应会否使旧 SDK 崩溃？

**W07｜条件｜MUST 定义长任务句柄的生命周期。** 服务提供异步长任务时，调用方须能获得任务句柄或标识，并获知状态、完成结果和失败；等待或轮询的超时、停止本地等待与取消远端任务须分别定义。服务支持进度、手动轮询、远端取消或断点恢复时，应说明相应入口与限制。例外/评审：服务只提供同步调用时不适用；停止等待后任务是否仍在远端运行？

**W08｜条件｜MUST 定义凭据生命周期与配置优先级。** SDK 接受凭据提供者时，说明过期刷新或轮换由谁负责、已创建客户端何时读取新凭据；取凭据期间取消或超时的信号、错误类别及迟到结果的处理须明确。存在显式参数、环境变量、配置文件和默认值等多个来源时，公开实际覆盖顺序。例外/评审：无需鉴权或只有单一配置来源的 SDK 只需说明适用部分；轮换后是否必须重建客户端？

**W09｜条件｜SHOULD 提供必要的响应元数据访问。** 保持主要调用返回地道的类型化结果；当请求标识、限流信息、ETag、响应头或原始响应影响诊断与后续操作时，提供稳定的访问路径，并定义底层响应或流的所有权与释放责任。例外/评审：无远端元数据需求时不必暴露传输类型；调用方能否在不丢失主要结果的情况下取得必要元数据？

**W10｜条件｜MUST 把中间件纳入公开调用语义。** SDK 提供 middleware/interceptor 时，规定注册顺序、请求/响应方向的执行顺序、短路/重试是否再次经过各层、错误如何变换、每层能否读取或消耗请求体，以及异常中间件是否会改变主请求。逐项说明哪些是受支持扩展点、哪些属于内部实现。证据为两个有序中间件的请求/响应轨迹与短路反例。中间件可组合的顺序不能靠注册代码推测。来源：Azure SDK [General Implementation](https://azure.github.io/azure-sdk/general_implementation.html) 的 HTTP pipeline policy 清单和 [C# implementation](https://azure.github.io/azure-sdk/dotnet_implementation.html) 的自定义 policy 要求；具体层序与重入检查为跨 SDK 综合要求。

**W11｜条件｜SHOULD 将原始响应通道与类型化结果分层。** 若调用者需要未映射字段、传输头或响应体，提供明确标为低层/易变的访问入口或 response wrapper；说明响应体是缓冲、可重复读取还是一次性流，谁负责关闭，读取失败归属于业务调用还是后续消费。不要让默认高层结果依赖内部 HTTP/RPC 客户端具体类型。证据为类型化调用与低层调用各一个消费者，以及读取/关闭反例。来源：Azure SDK [Go Guidelines](https://azure.github.io/azure-sdk/golang_introduction.html) 的 response envelope/streamed response；这是该生态建议，分层与所有权要求是本项目综合建议。

**W12｜条件｜MUST 明确请求管线中凭据、用户中间件、重试和传输的先后关系。** 认证签名要覆盖最终将发送的请求；重试要说明每次 attempt 是否重新取凭据/执行用户中间件、幂等键是否稳定、响应体能否重放。涉及请求压缩/签名/缓存等有序阶段时，给出顺序和可观测失败类别。禁止依赖未文档化的内部管线次序。证据为签名或重放消费者契约；真实网络行为在候选实现中另验。来源：Azure SDK Pipeline、AWS SDK Retry Behavior；具体顺序依产品，不能从来源示例推定为普遍固定顺序。

**W13｜条件｜SHOULD 让分页在不暴露 transport 的情况下可控恢复。** 如 W04 的分页需要持久化 cursor，说明 token 是否不透明、是否绑定过滤/排序/服务版本、过期与跨客户端行为、单页重试和已消费项重复风险；需要应用持久化时提供可序列化 continuation token。每页原始响应句柄与整页类型化结果分开，不能让读取下一页静默吞掉前页失败。证据为中断—保存—恢复消费者及无效/过期 token 反例。来源：Azure SDK General Design「Pagination」与 Google Cloud Client Libraries Best Practices 的分页惯例；这是综合推导。

**W14｜条件｜MUST 使 SDK 客户端配置有可观察的解析结果。** 多来源值（构造参数、环境变量、配置文件、默认值）按属性分别声明优先级、读取时点、缺失/非法值行为及客户端快照还是动态读取；运行中修改配置是否影响并发请求必须明确。各 SDK 对来源优先级没有跨生态统一次序；本条是要求产品自己声明并检查，不预设具体优先级。

这些 SDK 规则是把上面的程序接口规则应用到远程依赖边界的**综合推导**；具体传输语义另以项目协议和对应 API reference 核验。参考：[Azure SDK General API Design](https://azure.github.io/azure-sdk/general_design.html) 的凭据、服务版本、响应、管线、分页与长任务约定，[AWS SDK Retry Behavior](https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html) 的重试分类与次数语义，以及 [Google Cloud Client Libraries Best Practices](https://docs.cloud.google.com/apis/docs/client-libraries-best-practices) 的客户端与凭据复用建议。这些是各生态的权威实例，其具体默认值与机制不直接移植为通用要求。

**落地示例：有创建与列表能力的远程 SDK。** 以下值只是示范如何把规则写成可评审契约，不是所有 SDK 的固定默认值。

```text
client = Client.open(Config(
    credentials: CredentialProvider(...),
    timeout: 10 seconds,
    retries: RetryPolicy(maxAttempts: 2, operations: ReadOnly) // 示例中含首次请求
))

created = client.invoices.create(
    CreateInvoice(customer: CustomerId("c-17"), amount: Money(120, "CNY")),
    requestId: "req-47"   // 仅在服务端承诺按此标识去重时才称为幂等
)

pages = client.invoices.list(pageSize: 50)
failures = []
try:
    for invoice in pages: ...   // 每次取下一页可能发生 I/O 和失败
catch error:
    failures.append(error)
for resource in [pages, client]:
    try:
        resource.close()
    catch error:
        failures.append(error)
if failures.length == 1: raise failures[0]
if failures.length > 1: raise CombinedFailure(failures)
```

`CombinedFailure` 仅表示调用方能取得主操作与各次清理的错误；目标语言可用适合的多错误形式。关闭每个资源都要尝试，不能让前一个关闭失败跳过后一个。

在提案中同时填入：`Client` 是否可并发复用；多来源配置的覆盖顺序与凭据轮换的生效时机；`close()` 重复调用和关闭后调用的结果；`create` 的 `InvalidInput`、`PermissionDenied`、`RateLimited`、`TransportFailure`、`OutcomeUnknown` 如何区分；超时或取消后远端可能已创建时如何凭 `requestId` 查询；重试是否遵守服务等待时间和总预算、凭据提供者不响应时何时停止；`list` 每页失败是否可用游标恢复；类型化结果如何取得必要的请求标识与响应元数据；凭据是否可能出现在日志。若有长任务，还须填入状态、结果、恢复入口，以及停止本地等待与取消远端任务各自的语义。若服务不支持请求去重，删除伪代码中的暗示，并把结果不确定性明确告知调用者。
