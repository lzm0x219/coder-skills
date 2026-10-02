# Universal Library / Code API Design Guidelines — 基础契约

适用于公开的库、SDK、框架、包与可复用模块的**程序接口**。这是本项目综合多种语言官方指南形成的内部设计标准草案，不是某个语言组织颁布的跨语言规范。HTTP、RPC 等传输层设计另读对应 reference。等级与来源性质见[共享规则](../common.md#规则等级)；具体语言机制只是实现示例。

## 摘要与适用边界

调用者可依赖的不只是名称和签名，还包括参数顺序与缺省、返回值、错误、状态、副作用、所有权与生命周期、线程/协程语义、性能边界、扩展点、运行环境和已公开的序列化形式。一个实现细节只有被导出、文档承诺或成为可靠的可观察行为时，才可能进入公共契约；是否承诺需要在发布前明确。

**规则分层。** `通用`规则适用于几乎所有公共程序接口；`条件`规则只有在相应机制存在时触发。继承与第三方实现的 L01–L03 统一放在[扩展点](extensions.md)；资源、异步和并发按[运行契约](runtime.md)读取；跨原生边界按[原生互操作](native-interop.md)读取。语言特定技术见[语言映射](languages.md)，不作为通用规则。每条规则都应在所选语言和项目约定下落地。本文件及关联 reference 的规则是跨资料**综合原则**；每组末尾给出主要一手依据，未声称来源逐字规定了本标准的措辞。

## 核心设计方法

整体流程按[Skill 入口](../../SKILL.md)执行；程序接口评审的模型、调用点和取舍步骤见[评审流程](review.md#api-评审流程)。以下伪代码只说明可读性与结果建模，具体提案使用目标语言的可检查载体。

### 语言中立的示例记法

以下为伪代码，仅表达调用契约，不是某门语言的推荐语法。

```text
差：client.send("user-7", true, false, 30)
好：client.send(Message(to: UserId("user-7"), delivery: Confirmed,
                      timeout: Duration.seconds(30)))

差：record = store.get(key)  // null 可能表示不存在、失败或未加载
好：result = store.find(key) // Found(record) | Missing | Failed(error)
```

## 基础契约规则

每条规则采用相同读法：**要求**说明具体动作；**原因/落地**给出调用者可见的结果；**例外/评审**说明何时可以偏离及评审问题。`MUST` 只用于明确契约、安全或发布承诺；其余主要为 `SHOULD`。

### A. API 哲学与调用点

**A01｜通用｜SHOULD 从代表性用例推导接口。** 在提案中写出普通、边界和失败调用，注明调用者目标与成功标准。原因：接口声明在实现侧只写一次，调用点会出现无数次。例外/评审：底层原语可以先做概念证明；调用代码是否无需内部知识？常见任务是否可直接表达？

**A02｜通用｜SHOULD 优化调用点可读性而非最短字符数。** 检查参数、返回值与副作用在上下文中是否自明；必要时用标签、语义类型或配置对象。例外/评审：高频数学原语可用社区惯例的短名；读者能否不查声明理解布尔值与单位？

**A03｜通用｜MUST 写出稳定接口的可观察语义。** 前置条件、成功结果、失败、状态变化和承诺边界要可测试。原因：仅签名兼容仍可能行为破坏。例外/评审：未承诺的内部细节不要写成保证；旧调用得到的结果是否改变？

依据：[Bloch 原作者资料](https://research.google/pubs/how-to-design-a-good-api-and-why-it-matters/)、[Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/)、[Kotlin Library Authors’ Guidelines](https://kotlinlang.org/docs/api-guidelines-introduction.html)。

### B. 公共表面

**B01｜通用｜MUST 标出公共、实验和内部边界。** 列出包入口、重导出、公开类型与扩展点，并说明稳定性承诺。原因：未声明边界会造成意外依赖。例外/评审：动态语言也可用文档、命名及导出清单标注；调用者能否识别可依赖的入口？

**B02｜通用｜SHOULD 仅导出调用者确实需要的概念。** 把内部帮助类、存储模型、配置过程留在实现内；评审新增导出是否能完成独立任务。例外/评审：调试或互操作确需低层入口时可设独立命名空间及稳定性级别；可否通过既有入口完成？

**B03｜通用｜SHOULD 控制再导出与默认可见性。** 公开第三方类型或默认 public 成员前检查兼容成本。原因：依赖升级、命名冲突和成员新增可能破坏消费者。例外/评审：生态原生类型可显著改善互操作时可公开；其版本与所有权由谁承担？

依据：[Rust API Guidelines](https://rust-lang.github.io/api-guidelines/checklist.html)、[Kotlin Simplicity](https://kotlinlang.org/docs/api-guidelines-simplicity.html)、[Python PEP 8 公共接口](https://peps.python.org/pep-0008/#public-and-internal-interfaces)。

### C. 领域模型与抽象

**C01｜通用｜SHOULD 公开调用者的领域概念。** 先画出对象、操作和关系，再决定类、函数或模块；不要直接照搬数据库表或传输消息。例外/评审：低层数据访问库本身可能以存储概念为领域；名称是否反映调用者任务？

**C02｜通用｜MUST 保持公开对象的不变量。** 构造完成后的可见状态应满足文档约束；若有阶段性状态，使用明确状态类型或转换。原因：调用者不能靠隐藏顺序修复半有效对象。例外/评审：性能敏感的可变缓冲区可允许受控中间态；何时可用、何时不可用？

**C03｜通用｜SHOULD 拒绝无职责的 `Manager`、`Helper`、`Service`。** 若一个类型承载多个无关流程，应拆回领域操作或正交能力。例外/评审：命名来自明确领域术语时可保留；新增方法是否总落在同一个抽象上？

依据：[Kotlin Simplicity](https://kotlinlang.org/docs/api-guidelines-simplicity.html)、[.NET Type Design Guidelines](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/type)。

### D. 命名与词汇

新增、修改或评审公开名称时，读取[命名规范](naming.md)。该文件集中定义领域词汇、调用点、操作动词、阶段/成本、类型角色与语言惯例；本节不另设重复规则。

### E. 类型设计

**E01｜通用｜SHOULD 为高风险混淆值提供语义区分。** 金额/币种、标识符、时长/时间点、路径/URL 等相同底层表示不能仅靠参数位置区分。例外/评审：仅局部且低风险的简单运算无需包装；误传相同原始类型能否被发现？

**E02｜条件｜SHOULD 明确集合是封闭还是可扩展。** 若调用者可穷举分支，新增成员可能破坏编译或行为；若要演化，预留未知值处理并记录语义。例外/评审：受控内部枚举可封闭；消费者遇到新值会怎样？

**E03｜通用｜SHOULD 使非法组合难以构造。** 用有效构造函数、独立状态或互斥选项代替多个可冲突标志。例外/评审：兼容旧接口时可保留旧形态并提供新入口；是否能构造 `closed=true` 且 `active=true`？

**E04｜条件｜MUST 说明公开值的相等、排序和身份语义。** 当对象可比较、作键或缓存时，明确值相等/实体身份、稳定性与哈希的一致性。例外/评审：不可比较对象应显式拒绝或不提供比较；同一对象跨版本是否仍可作为键？

依据：[Rust API Guidelines Type Safety](https://rust-lang.github.io/api-guidelines/type-safety.html)、[.NET Type Design Guidelines](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/type)。

### F. 函数与方法

**F01｜通用｜SHOULD 以调用点解释参数顺序。** 将核心对象/必需输入置前，相关参数成组；相邻同类型参数要用标签或语义类型消歧。例外/评审：遵循已有生态固定签名更重要时可沿用；交换参数后是否仍能编译却做错事？

**F02｜通用｜SHOULD 用明确选择代替含糊布尔开关。** `send(x, true)` 要换成命名选项或描述性操作；布尔本身就是领域事实时可保留。评审：调用处不查声明能否读懂 `true`？新增第三状态会怎样？

**F03｜通用｜MUST 定义默认值和可选参数的行为。** 默认超时、重试、权限、编码与排序要明确；改变默认值按行为变更评审。例外/评审：由系统环境决定时说明解析规则；升级后旧调用是否改变？

**F04｜通用｜SHOULD 让返回值承载可用结果。** 避免要求调用者再读全局状态、输出参数或含糊布尔值；正常缺失要有可识别表示。例外/评审：底层零拷贝或 ABI 约束可使用输出参数；结果是否含足够信息用于下一步？

**F05｜条件｜SHOULD 按操作复杂度选择参数对象、构建器或重载。** 当组合选项增长时，使互斥关系与默认值清楚；不要为每个排列新增方法。例外/评审：少量固定参数维持简单签名即可；新选项会产生组合爆炸吗？

依据：[Rust API Guidelines](https://rust-lang.github.io/api-guidelines/checklist.html)、[.NET Member Design Guidelines](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/member)、[Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/)。

### G. 空值、缺失与未知

**G01｜通用｜MUST 区分正常缺失、未知、未加载、不适用与失败。** 一个 `null`/`nil`/`None` 不应同时表示这些状态；用文档、类型或错误分支明确表示。例外/评审：只存在一种缺失语义时可用单一空值；调用者能否决定重试还是展示“无结果”？

**G02｜通用｜MUST 写明可空性与集合空值约定。** 每个公开输入、输出和成员的缺省/空值含义一致；不让空集合和未加载相互替代。例外/评审：语言无静态空值机制也必须文档化；消费者是否需要猜测空值来源？

依据：[Kotlin Backward Compatibility](https://kotlinlang.org/docs/api-guidelines-backward-compatibility.html)、[.NET Parameter Design](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/parameter-design)。

### J. 错误模型

**J01｜通用｜MUST 区分调用者错误、领域拒绝、外部失败与正常缺失。** 定义稳定的可程序化类别；不要让调用方匹配人类文案。例外/评审：极小纯函数可能仅有参数错误；每类错误能否触发不同处理？

**J02｜通用｜MUST 写出失败后的状态和副作用。** 尤其是部分成功、原子性、可恢复性及重复执行风险。例外/评审：纯函数失败没有副作用可直接声明；调用方可否安全修正后重试？

**J03｜条件｜SHOULD 暴露有限且稳定的重试判断信息。** 超时、限流、暂时不可用与永久错误可分，但不能把所有内部细节固定为公共错误码。例外/评审：无远程/外部依赖时不适用；分类变化会不会破坏自动化处理？

**J04｜通用｜MUST 提供有用且安全的错误上下文。** 包含操作与相关安全标识，不泄漏密钥、凭据或敏感载荷；可在适用语言中保留根因。例外/评审：面向终端用户的显示文案可另设层；日志中能定位问题又不泄密吗？

依据：[Go Effective Go Errors](https://go.dev/doc/effective_go#errors)、[.NET 异常最佳实践](https://learn.microsoft.com/en-us/dotnet/standard/exceptions/best-practices-for-exceptions)、[Rust API Guidelines](https://rust-lang.github.io/api-guidelines/checklist.html)。

### K. 组合与便捷性

**K01｜通用｜SHOULD 提供少量正交原语。** 每个原语解决一种独立能力，输入输出能连接；避免一个万能方法承载全部选项。例外/评审：单一完整工作流本身是领域原语时可保留；新需求是否要复制现有方法？

**K02｜通用｜MAY 为高频任务提供便捷入口。** 便捷入口应组合既有原语且行为相同，避免双套语义。例外/评审：性能优化需要专用实现时应保证外部语义一致；调用方何时该选哪个？

**K03｜条件｜SHOULD 允许结果进入宿主生态的组合机制。** 集合、流、迭代器、回调或 Promise 等采用目标语言可互操作形式。例外/评审：特殊性能约束可用专用类型并提供转换；结果是否被困在私有框架中？

依据：[Rust API Guidelines Interoperability](https://rust-lang.github.io/api-guidelines/checklist.html)、[Kotlin Consistency](https://kotlinlang.org/docs/api-guidelines-consistency.html)。

### L. 继承与扩展点

允许第三方继承、实现、注册插件或接收框架回调时，读[扩展点的 L01–L03 与 Z01–Z08](extensions.md)。规则正文、依据和消费者要求统一在该页；不提供这些机制时不用加载。

### M. 依赖边界

**M01｜通用｜SHOULD 审核公共签名中的第三方类型。** 只有其生态价值高于版本耦合时才公开；记录依赖最低/最高支持范围及升级影响。例外/评审：插件标准类型或宿主语言标准类型通常值得复用；依赖大版本变化会迫使本库破坏兼容吗？

**M02｜通用｜SHOULD 让实现替换不要求调用者重写。** 不泄漏内部存储、网络库、线程池或数据库实现特有的配置。例外/评审：库本来就是某产品或某数据库的绑定时可公开其概念；替换实现会改变哪些公开类型？

依据：[Rust API Guidelines Future Proofing](https://rust-lang.github.io/api-guidelines/checklist.html)、[TypeScript Declaration Files: Library Structures](https://www.typescriptlang.org/docs/handbook/declaration-files/library-structures.html)。

### R. 文档与示例

**R01｜通用｜MUST 文档化稳定接口的语义。** 至少覆盖用途、前后条件、参数单位、结果、失败、副作用、资源及适用的并发/性能边界；不要复述签名。例外/评审：无对应机制的条目可略；新人只读文档能否正确调用？

**R02｜通用｜SHOULD 提供可检查的常见与失败示例。** 已发布接口的示例使用当前版本实际入口；设计提案的示例引用同一提案中的候选公开声明，并标明尚未发布。展示关闭、错误或取消处理；目标语言与工具链可用的具体提案按[设计期交付](deliverables.md)执行静态检查。例外/评审：极小纯函数可只给简短调用例；示例能否在所声明的导入路径和目标版本下通过检查？

**R03｜通用｜SHOULD 用文档写作反向检验设计。** 若解释一个入口需要大量例外、调用顺序或隐藏约定，先简化模型或改名，再增补文档。例外/评审：领域本身复杂时文档不可避免；困难来自业务还是接口组织？

依据：[Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/)、[Kotlin Informative Documentation](https://kotlinlang.org/docs/api-guidelines-informative-documentation.html)、[Rust API Guidelines](https://rust-lang.github.io/api-guidelines/checklist.html)。

### U. 安全与防误用

以下说明安全要求在程序调用点、类型和调试表示中的落地。跨信任边界、身份、外部目标或成本保护按[共享安全契约](../common/security.md)读取；共享页负责通用安全边界，本节补充程序接口的表现方式。

**U01｜通用｜MUST 为有代价或破坏性的操作选择安全默认值。** 删除、覆盖、广权限、无限重试或无界读取要显式启用，并在调用点可见。例外/评审：明确就是底层危险原语时以名称和边界表示；误用是否会造成不可逆结果？

**U02｜通用｜MUST 在可信边界验证输入并明确失败。** 类型可约束的先用类型，运行时才能判断的在边界拒绝；不要静默截断或修正危险值。例外/评审：宽松解析器可提供独立容错模式；非法值何时被发现？

**U03｜通用｜MUST 保护秘密与权限边界。** 凭据不出现在默认调试表示、错误消息或日志中；操作所需权限应在配置或文档可见。例外/评审：特权调试工具可受控暴露必要信息；一个普通异常会不会泄密？

依据：[Rust API Guidelines Dependability](https://rust-lang.github.io/api-guidelines/dependability.html)、[C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)。

## 资料边界

各组末尾的一手资料支持其主题，语言适用边界由[语言分支](languages.md)维护，规范/生态与 Skill 综合要求按[共享等级](../common.md#规则等级)区分。版本争议查[一手索引](../sources.md)，不把跨资料归纳冒充共同强制条文。
