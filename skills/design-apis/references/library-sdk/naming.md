# Library / SDK 公共 API 命名规范

适用：新增、重命名或评审公开包、类型、方法、参数、结果和状态名称。先确定公开对象，再写目标语言中的真实调用点，最后判断名称。这里的 `MUST` / `SHOULD` 是**本项目的设计要求**，不是引用资料共同颁布的跨语言标准；既有已发布名称还受兼容承诺约束。传输协议中的资源、字段或 RPC 命名应另按该协议的规范处理。

## 依据与边界

| 一手资料 | 可借鉴的原则 | 不能直接移植的部分 |
| --- | --- | --- |
| [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/) | 以调用点的清晰度判断名称；保留消歧所需的词，删去上下文已表达的词。 | Swift 参数标签与语法不是各语言的统一写法。 |
| [Google AIP-121](https://google.aip.dev/121) 与 [AIP-151](https://google.aip.dev/151) | 先确定资源及其关系，再确定操作；长任务的执行句柄可以与最终结果分开建模。 | 它们分别约束 Google 风格的资源 API 和长任务模式，并未规定 SDK 必须选用 `Job` 或 `Extraction`。 |
| [Google AIP-190](https://google.aip.dev/190) | 简单、直观、一致的词汇；同一概念同名，不同概念避免重名。 | `VerbNoun` 和大小写要求针对 Google 的 RPC/Proto API，不能直接套到 SDK 子客户端。 |
| [Azure TypeScript SDK 指南](https://azure.github.io/azure-sdk/typescript_design.html) | 操作动词应对应真实行为；子客户端上下文可省略重复名词；分页与长任务有明确的命名和返回形态。 | `begin`、`list` 返回迭代器、`Client` 后缀是 Azure TypeScript 的生态约定，并非所有 SDK 的强制形式。 |
| [Kotlin Library Authors’ Guidelines](https://kotlinlang.org/docs/api-guidelines-consistency.html) 与 [Kotlin 命名约定](https://kotlinlang.org/docs/coding-conventions.html) | 同一库的参数顺序、词汇和命名形式保持一致；类通常用名词，方法通常用动词。 | Kotlin 的大小写、工厂函数和属性惯例只在相应语言中适用。 |
| [.NET Naming Guidelines](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/names-of-type-members) 与 [General Naming Conventions](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/general-naming-conventions) | 方法用动词，属性用名词/形容词；可读性优先；避免难懂缩写。 | 文档部分来自较早版 Framework Design Guidelines，大小写和 `Async` 习惯需按当前 .NET 目标核验。 |
| [Effective Go](https://go.dev/doc/effective_go#names) 与 [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/naming.html) | 在包/类型上下文中去冗余；名称应符合语言惯用形态，并在转换时表达成本与所有权。 | Go 的 getter 命名和 Rust 的 `as_`/`to_`/`into_` 不应变成跨语言前缀要求。 |

## 命名规则

**D01｜通用｜MUST 先确认概念，再给概念命名。** 在比较候选词之前，以中性代号列出调用者可见的对象、执行与结果；对有 ID 的对象写明 ID 所指、生命周期、状态、可用操作及它们之间的关系。逐项区分**已验证的既有契约或调用方用语**、**已确定的设计决策**和**待验证的提案假设**，注明来源。假设可用于演练或草案，但不能作为排除另一个同样符合假设的候选名的证据。最后才选资源、动作、状态和结果的主词：既有事实或调用方用语足以区分时，记录证据；多个词都准确且没有决定性既有事实时，由设计负责人在完整调用点上作明确取舍，记录备选、理由与代价。尚未作出取舍则记为暂定或未决。仅有一种操作、对象有状态、结果另有 ID 或内部队列叫 `job`，都不足以单独决定 `Job` 与 `Extraction`。评审：不看候选名，能否说清 ID 指向什么？另一候选词违反了哪条已确认事实；若没有这样的事实，是否诚实地把选择标为设计决策？依据：Google AIP-121、AIP-151、AIP-190；判定门槛为本项目规则。

**D02｜通用｜MUST 保持同一概念同名、不同概念异名。** 参数、过滤条件、结果属性、错误、示例和文档使用同一词；若 `state` 与 `status` 是不同概念，写清差别，否则统一。仅大小写或单复数变化不算新概念。评审：调用者能否从一个名称预测其余入口？依据：Google AIP-190、Kotlin Consistency。

**D03｜通用｜SHOULD 在完整调用点上保留必要词、删除重复词。** 连同包名、对象名、方法名和参数名一起读；`client.files.upload(...)` 的 `files` 已提供对象语境，顶层 `client.upload(...)` 则可能需要 `uploadFile`。不要为了最短字符数删除消歧词，也不要重复 `files.uploadFile` 这类已知语境。评审：脱离声明，只看调用代码能否读出对象和动作？依据：Swift、Effective Go、Azure TypeScript。

**D04｜通用｜SHOULD 使用调用者熟悉的具体词。** 优先选能指认资源或动作的普通领域词；`Manager`、`Helper`、`Info`、`Record` 等宽词只有在确实表达角色时使用。缩写只用于目标开发者普遍认识且不会与另一概念冲突的词；避免把内部术语、营销词或协议实现细节带进公共名称。评审：把名称单独列在自动补全中，调用者知道它是什么吗？依据：Google AIP-190、.NET General Naming、Kotlin Naming。

**D05｜通用｜MUST 让名称的词性与可观察行为一致。** 类型和资源属性指向事物或状态，执行动作的方法使用动词；属性读取若可能发网络请求或改变外部状态，应改成显式操作入口或在目标语言已有明确惯例下标出成本。布尔状态用肯定且可回答真假的词，如 `isClosed`、`canRetry`。评审：名称是否让调用者误判为廉价属性、纯函数或已经完成的动作？依据：.NET Names of Type Members、Kotlin Naming。

**D06｜通用｜SHOULD 让操作动词对应实际语义；语义不符时选更具体的领域动词。** 下表是候选词的典型含义，不是要求所有 SDK 提供这些操作。不要靠一个通用 `process`、`handle`、`execute` 掩盖不同副作用，也不要仅因底层 HTTP/RPC 方法这样命名就照搬。依据：Azure TypeScript 的服务操作动词表、Google AIP-190 的词汇一致原则；文件传输和容器动作是本项目的归纳。

| 动词 | 适用的可观察行为 |
| --- | --- |
| `get` / `list` | 取一个已知资源 / 枚举一组资源；列表是否分页另按 D08 命名。 |
| `create` / `update` / `replace` / `upsert` | 新建 / 局部修改 / 整体替换 / 新建或修改；不承诺相应语义时换词。 |
| `upload` / `download` | 向远端发送本地内容 / 从远端取得内容；只打开待消费流时按 D07 表达阶段。 |
| `delete` / `remove` / `clear` | 销毁资源 / 从集合移除 / 清空容器；服务已有不同领域惯例时记录并保持一致。 |

**D07｜条件｜MUST 在异步、流和资源句柄中标出阶段。** `start`/`begin` 只表示启动并返回任务或句柄；等待终态的入口应明确等待目标，如 `waitForCompletion`；`cancel` 是请求取消远端任务时，不可同时表示“只停止本地轮询”。若 `download` 返回尚未读取的流句柄而非完整内容，使用 `openDownload` 等能体现获取句柄的名称，或让返回类型与文档在调用点同样清楚。`open`/`close` 成对入口的所有权应一致。依据：Azure General Design 的长任务语义、Swift 的调用点原则；具体动词是本项目的推导。

**D08｜条件｜MUST 让集合调用点和返回类型共同说明取数边界。** 返回可持续取页的迭代器可用 `list`；只发一次请求并返回一页时，优先用 `listPage` 或目标语言中同样明确的形态。`Page<T>`、`nextCursor` 等名称应让调用者识别继续条件，不把“读完所有项”的成本藏在 `list` 或 `toArray` 的默认行为中。评审：只看调用点和返回类型，能否分辨一次请求、一页和全部结果？依据：Azure TypeScript Pagination、Azure General Design Pagination；本规则并不强制 Azure 的迭代器形式。

**D09｜通用｜SHOULD 按公开角色命名类型、参数和结果。** 资源模型用领域名；必要时用限定词区分 `StoredFile` 与上传内容、`UploadInput` 与可选的 `RequestOptions`、`FileDownload` 与已下载的文件。`Response`/`Result`/`Options` 等后缀只有确有不同角色时才保留，不能用 `Data`、`Info` 或 `Record` 代替语义建模。评审：类型名离开声明位置仍能对应调用者持有的是什么吗？依据：Azure TypeScript Model Types、Swift 的省词规则。

**D10｜条件｜SHOULD 遵循目标语言的公开 API 惯例，并记录跨语言语义映射。** TypeScript/Kotlin 常用 `PascalCase` 类型与 `camelCase` 方法；Go 用包名参与调用点并避免无意义的 `Get` getter 前缀；Rust 用 `snake_case`，转换可按 `as_`/`to_`/`into_` 表达借用与所有权；.NET TAP 的可等待方法通常带 `Async` 后缀。不要把其中一个生态的拼写规则升级为其他语言的通用要求。依据：各语言官方指南，.NET 异步命名见 [TAP](https://learn.microsoft.com/en-us/dotnet/standard/asynchronous-programming-patterns/task-based-asynchronous-pattern-tap)。

**D11｜条件｜MUST 把已发布名称的修改作为兼容变更评审。** 同时检查源码导入、类型引用、序列化名、文档示例和旧消费者；过渡别名要有主名、弃用与移除计划。新提案未发布时直接改成最清晰的名称，避免为了草案历史保留别名。按[兼容与演化](evolution.md)验证。

## 命名评审的完成条件

1. 在写候选名之前，留下不含候选词的对象、执行和结果模型，并为每项标注既有事实、已定决策或待验证假设及来源。对象身份和关系不足以区分公开概念时，命名评审**未通过**，交付未决项；只有调用方词汇缺失时，仍可走明确的产品设计决策路径。
2. 为可能混淆的名称写出至少两个候选及各自成立的条件。若已确认事实能排除其中之一，列出该事实及来源；若两者都符合已知事实，由设计负责人记录选择、完整调用点、理由和被放弃方案的代价，并标为**设计决策**，不声称行业规范唯一要求此词。尚无负责人取舍时保留暂定或未决状态。功能数量、内部实现名和更短的拼写都不能代替语义证据或正式取舍。
3. 写出普通、失败、分页/长任务或资源释放等命中场景的**完整调用点**，再逐一核对新增/改名的公开类型、方法、参数、属性和状态：同一概念是否同名，动词是否承诺真实副作用，名称是否暗示错误的完成点或成本。
4. 用目标语言的官方惯例检查大小写、前后缀与导出形态；协议层和 SDK 层名称可映射，不能机械同形。变更已发布名称时再运行旧消费者验证。

以下预设案例用于检查 D01 的判定边界；案例前提不能从候选名倒推：

| 预先给定的契约与调用方用语 | 合格的命名结论 |
| --- | --- |
| 已有公开契约和调用方都把可独立追踪的处理记录称为 `job`，结果另有身份。 | `jobs` 有直接依据；具体动作可叫 `startTextExtraction`。不推导其他服务也应使用 `Job`。 |
| 已有公开契约和调用方都把可持久引用的提取请求称为 `extraction`，一次请求可有多次执行尝试。 | `extractions` 有直接依据；执行尝试若公开，另建模其身份。 |
| 只知道“提交文件后返回 ID，可查状态并下载输出”，没有资源定义或调用方词汇。 | 保持未决；`jobs` 和 `extractions` 都不能从这些行为中唯一推出。 |
| 已明确资源身份、生命周期及调用点，但新产品没有既有英文术语；设计负责人比较两个可行名称后正式选定一个。 | 标为设计决策并记录理由、备选与代价；不称为由既有事实或行业规范唯一推出。 |

即使执行有独立 ID、输出文件也有独立 ID，`Extraction` 仍可能是该执行请求的领域名称。[Amazon Textract 异步文本检测](https://docs.aws.amazon.com/textract/latest/dg/api-async.html)使用 `JobId` 是行业实例，不是所有 SDK 的命名要求。`listPage` 与 `list` 的选择取决于返回的是单页还是可迭代集合。
