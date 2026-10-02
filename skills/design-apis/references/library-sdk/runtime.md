# Library / SDK 运行契约

适用：公开对象存在状态、资源所有权、异步/并发、显著成本、诊断或外部依赖时。只应用命中的条件规则；每个判断落为调用者可验证的行为。

## H. 状态与可变性

**H01｜通用｜SHOULD 先选择明确的可变性模型。** 公开对象是值快照、可变句柄还是共享视图，构造后哪些字段可变要写清。声称不可变或独立快照时，MUST 说明嵌套可变值、别名与复制/借用边界；异步入口说明在首次挂起前还是之后捕获输入，调用者在此期间可否修改或复用缓冲区。输出说明是否共享内部缓存以及调用者修改是否影响其他对象。只读属性声明不能证明深度不可变或运行期隔离；设计期将复制等实现承诺列为待运行核验。例外/评审：性能敏感类型可提供有明确寿命的共享视图；调用方持有的旧引用会观察到变化吗？

**H02｜通用｜MUST 声明可观察副作用。** I/O、缓存写入、回调、事件发送和惰性计算不能完全依赖调用者猜测。例外/评审：实现内部且不可观察的缓存无需承诺；只读方法是否可能触发外部操作？

**H03｜条件｜SHOULD 把状态迁移变成可验证操作。** 对启动、关闭、提交、重置等写出允许的前后状态及非法调用结果。例外/评审：无状态纯函数不适用；重复调用和失败后重试落在哪个状态？

依据：[Kotlin Library Authors’ Guidelines](https://kotlinlang.org/docs/api-guidelines-introduction.html)、[C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)。

## I. 资源、所有权与寿命

**I01｜条件｜MUST 声明资源归属与释放责任。** 文件、连接、线程、订阅和缓冲区由谁创建、持有、转移及关闭必须明确。例外/评审：无显式资源的纯值类型不适用；调用者能否仅凭文档避免泄漏？

**I02｜条件｜MUST 定义关闭与失败语义。** 重复关闭、关闭后调用、初始化一半失败以及关闭自身失败要有确定结果；不得默默丢失关键错误。例外/评审：析构/终结器无法安全报告失败时提供显式关闭路径；能否测试这些路径？

**I03｜条件｜SHOULD 区分借用、复制和共享视图。** 返回对象的有效期、别名修改和跨线程使用限制要可见。例外/评审：运行时自动管理内存仍可能有缓冲区借用；原对象关闭后返回视图是否有效？

依据：[C++ Core Guidelines Resource Management](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)、[Rust API Guidelines Dependability](https://rust-lang.github.io/api-guidelines/dependability.html)。

## N. 异步与并发

**N01｜条件｜MUST 说明操作的同步/异步完成点。** 返回时是已完成、已排队还是仅获得句柄；回调可能同步触发还是始终异步，不能模糊。例外/评审：纯同步 API 不需异步条款；调用者何时可观察副作用？

**N02｜条件｜MUST 定义取消与超时。** 说明取消是否保证停止、是否可能已产生副作用、超时归属及清理责任。例外/评审：不可取消操作应明确说明；取消后是否仍收到回调或结果？

**N03｜条件｜MUST 写明并发安全与执行上下文。** 客户端/对象是否可跨线程共享，回调在哪个线程/调度器执行，是否可重入。例外/评审：单线程运行时仍可能有异步重入；并发调用同一对象会怎样？

**N04｜条件｜SHOULD 指定事件、回调和异步结果顺序。** 若无顺序保证应明确说；若有顺序保证，界定同一对象还是全局。例外/评审：顺序对调用者无意义时无需额外排序成本；竞态下结果是否可预测？

依据：[Kotlin Informative Documentation](https://kotlinlang.org/docs/api-guidelines-informative-documentation.html)、[.NET Event Design](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/event)、[C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)。

## O. 性能契约

**O01｜通用｜MUST 使显著成本可发现。** 可能做网络/磁盘 I/O、大量分配或全表扫描的操作要用名称、类型或文档显露；不要让属性读取意外阻塞。例外/评审：实现可能缓存时仍须说明最坏的可见行为；一次调用最坏会做多少工作？

**O02｜条件｜SHOULD 对大结果提供有界消费方式。** 分页、迭代或流式接口要说明何时拉取、何时关闭、失败发生在何处。例外/评审：结果明确小且固定时直接返回集合更简单；调用方能否避免一次载入全部数据？

**O03｜条件｜MAY 提供批量接口降低跨边界开销。** 批量失败要能定位每项结果，并说明原子性、顺序及上限。例外/评审：无实际跨边界成本时不必添加；批量与单项调用的语义是否一致？

依据：[Rust API Guidelines Flexibility](https://rust-lang.github.io/api-guidelines/flexibility.html)、[Kotlin Library Authors’ Guidelines](https://kotlinlang.org/docs/api-guidelines-introduction.html)。

## P. 可诊断性与可观测性

**P01｜通用｜SHOULD 提供可理解的诊断表示。** 错误、状态和对象身份应足以定位调用问题，但不得打印凭据；调试表示不等于稳定机器格式。例外/评审：敏感对象可只给安全摘要；日志是否能关联操作与结果？

**P02｜条件｜SHOULD 提供可选的观测挂钩。** 对长任务/远程 SDK 可暴露请求标识、耗时、追踪或事件监听；挂钩失败不得暗中改变主操作结果，除非明确契约。例外/评审：小型纯计算库无需日志框架；调用者能否诊断生产故障？

依据：[Rust API Guidelines Debuggability](https://rust-lang.github.io/api-guidelines/debuggability.html)、[Go Effective Go Errors](https://go.dev/doc/effective_go#errors)。

## Q. 可测试性

**Q01｜通用｜SHOULD 隔离时间、随机、网络和文件系统等外部依赖。** 用构造参数、接口或配置注入必要的替身，不强迫所有测试触碰真实外部系统。例外/评审：纯函数无需注入；用户能否离线复现一个失败场景？

**Q02｜通用｜SHOULD 让相同公开输入在约定环境下得到可预测结果。** 对时间、并发和缓存的非确定性写清边界；不要为了测试暴露内部私有状态。例外/评审：随机/采样库可按统计契约测试；测试是否依赖未承诺顺序？

依据：[Kotlin Informative Documentation](https://kotlinlang.org/docs/api-guidelines-informative-documentation.html)、[Go Effective Go](https://go.dev/doc/effective_go)。
