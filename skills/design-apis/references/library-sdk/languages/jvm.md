# Java 与 Kotlin 公共 API 映射

适用：目标消费者使用 Java/JVM 或 Kotlin/JVM。二者源码表面相似但生成签名、默认参数、空值和二进制兼容不同；逐目标语言编译消费者。Native/JNI 另读 [原生互操作](../native-interop.md)。

## Java

- 用构造器或静态工厂表达创建策略；公开类/方法按使用场景避免过多重载造成解析或演进问题。接口一旦公开，视为第三方实现者契约。
- 异常类型、受检/非受检及可恢复语义是源码契约；二进制兼容按 JLS §13 逐项评估，接口方法/类层级变化不能凭“只新增”推断兼容。
- 使用 `CompletionStage`/`CompletableFuture` 时明确取消、完成线程、异常包装和 executor；`Future.cancel` 不证明远端副作用被撤回。
- 核验 [JLS SE 25 §13](https://docs.oracle.com/javase/specs/jls/se25/html/jls-13.html)，并按项目实际 JDK 版本对照。JLS 是语言规范，生态 API 设计建议另标。

## Kotlin

- 公开可空类型明确用 `T?`；不要把 `null` 同时用作未加载、缺失和错误。Java interop 还需检查平台类型的实际注解与生成签名。
- 默认参数会生成面向 Kotlin 的调用语法，但 Java 可见调用形式需核查；若改变/暴露二进制签名，检查 `@JvmOverloads`、桥接方法及 JVM descriptor，不将其当无代价语法糖。
- `suspend`、Flow、属性和 extension function 的 Kotlin 形态需与 Java consumer 可访问性分别检查；不要以 Kotlin 源码编译证明 Java API 可用。
- public `sealed` hierarchies、enum 和 interface 的演化影响 exhaustive `when`、第三方实现者及二进制消费者；按发布策略核验。多平台 API 只承诺各 target 实际共有的类型/行为。
- 依据：[Kotlin API Guidelines](https://kotlinlang.org/docs/api-guidelines-introduction.html)、[Backward Compatibility](https://kotlinlang.org/docs/api-guidelines-backward-compatibility.html)、[Java Interop](https://kotlinlang.org/docs/java-interop.html)。这些是 Kotlin 官方作者建议，JVM 二进制兼容还须以目标编译器/API 检查实测。

## 消费者证据

对公开 library 分别编译 Java 与 Kotlin 调用者；演化检查保留旧编译 consumer，并在项目承诺时运行 ABI 工具和旧二进制。源码通过不代表二进制兼容。
