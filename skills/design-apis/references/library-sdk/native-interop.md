# 原生互操作与 FFI

适用：公开 API 穿越进程内外语言 ABI，包括 C/C++ FFI、JNI、P/Invoke、Swift/C bridge、Rust `extern`、Wasm host/import/export 或平台原生句柄。先明确真实目标 ABI 与版本；不得把一种平台声明成全部平台契约。

## Y. ABI 与跨边界语义

**Y01｜条件｜MUST 固定 ABI 身份与布局。** 记录调用约定、符号导出/名称修饰、整数宽度、对齐、结构体/枚举布局、字符串编码、空指针表示及版本化策略，并按每个承诺的 OS/架构/工具链生成或编译消费者。语言默认布局不可自动视为 C ABI；Rust 仅在 `repr(C)` 等适用条件下承诺相应布局。来源事实：Rustonomicon FFI「Interoperability with foreign code」「Foreign calling conventions」；本条的 ABI 清单是综合建议。

**Y02｜条件｜MUST 为每个指针、缓冲区和句柄写出所有权协议。** 逐入口说明借用是否仅在调用期间有效、异步持有多久、是否可空、长度/容量单位、谁分配谁释放、释放函数/allocator 配对、重复释放及错误后部分初始化处理。输入不满足有效范围时在安全包装层拒绝，或把调用明确标为 unsafe 并列出调用者必须维持的不变量。证据为生命周期/释放配对调用样例及空值、截断、重复释放反例。来源事实：Rustonomicon「Calling foreign functions」「Creating a safe interface」「Destructors」；本条跨语言推导。

采用 C11 时，公开 API 允许 `NULL, 0` 不代表内部 libc 调用也允许：按 [WG14 N1570（C11 委员会草案）§7.1.4、§7.24.1](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)核对零长度仍需有效指针的函数；§7.22.3 的零大小分配行为依实现。包装层须避免非法零长度 copy、统一处理空缓冲区释放与保存指针，不能保留 allocator 已释放的旧指针。消费者至少覆盖空输入、部分输入后完成记录、失败后重试、关闭后释放；只测完整记录会遗漏所有权转换。其他 C 版本、语言和 allocator 另查其规范。

**Y03｜条件｜MUST 阻止语言异常、恐慌或非局部退出跨越不支持的 ABI 边界。** 定义边界如何捕获并映射为错误/状态码，资源处于何种状态，以及调用者如何取回诊断；不得假定两种语言的栈展开、析构和异常 ABI 兼容。证据为错误路径消费者及目标编译器检查。按使用语言与 ABI 版本核对官方规定；Rust FFI 参考 `extern` unwind 属性与 panic 行为，JNI 参考异常 pending 状态规则。

**Y04｜条件｜MUST 定义回调注销与对象销毁之间的竞态。** 若外部代码可能在注册函数返回后调用回调，规定注册成功点、同步/异步执行线程、重入、在途回调计数、注销完成是否保证不再调用、对象何时可释放，以及回调错误如何传回。若底层不提供“注销后静默”的保证，适配层须维持 trampoline/context 至安全屏障，或拒绝销毁并返回可观察状态。仅写“调用者应小心”不构成契约。证据为注册—触发—注销—并发销毁的反例/消费者流程。来源事实：Rustonomicon FFI「Asynchronous callbacks」明确要求销毁后不得继续回调，并指出线程同步要求；本项目动作是据此综合。

**Y05｜条件｜MUST 定义原生线程进入托管运行时的附着与局部引用寿命。** JNI 或相似运行时时，不把局部引用当作普通 GC 引用跨线程/回调保留；说明线程附着/分离、局部/全局引用创建与释放、异常 pending 时允许的 JNI 操作、临界数组/字符串区释放以及 daemon 生命周期。为每一处长期保存的引用选择合法引用类型和删除时点。证据为本地线程回调、重复调用和异常分支检查。来源事实：JNI Specification Java 25「Design Overview」的 Threads、Global and Local References、Exceptions 与 Critical Regions；语义仅适用于 JNI。

**Y06｜条件｜MUST 为 Wasm 定义模块边界与宿主能力版本。** 记录导入/导出函数、线性内存/表共享约定、资源句柄编码、内存增长/视图失效行为、异常/陷阱和宿主能力最低版本；区分 Core Wasm 与 WASI/浏览器宿主扩展。若 API 不需要 Wasm，不读取或套用本条。来源：Wasm Core 的 Imports/Exports/Memories 与所采用 WASI 版本；本次核验 [Core 2 / 2026-09-30](https://www.w3.org/TR/2026/CRD-wasm-core-2-20260930/)为 Candidate Recommendation Draft，不能称已获 W3C Recommendation 批准，目标实现支持另核验。具体 ABI 依目标工具链，不由本规则代替。

**Y07｜条件｜SHOULD 隔离低层原始绑定与安全高层包装。** 原始入口保留与上游 ABI 对照关系并显式标识不安全/平台限定；惯用高层 API 在验证长度、空值、所有权与线程条件后再开放安全调用。绑定声明应由头文件/IDL 生成或通过签名对照维护，避免手抄类型漂移。若库本来就是低层 binding，可把原始入口作为产品面，但必须保留调用前置条件与目标 ABI 证据。来源事实：Rustonomicon「Creating a safe interface」示例将 raw FFI 包装为安全 slice API；综合建议。

## 最低消费者证据

对所声明目标至少编译一个跨边界成功调用和一个失败/释放路径；涉及 ABI 布局时对头文件与绑定签名做可重复对照；涉及回调时有生命周期顺序反例。静态编译不能证明目标运行时加载、线程竞态、异常行为或全部平台 ABI；这些未实际执行的维度单独标为未验证。
