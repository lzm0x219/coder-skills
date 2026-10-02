# 兼容与发布演进

触发：已发布入口、持久消息、跨版本客户端、包/ABI或提供方能力变更。每一方向都需自己的证据；局部 reader 成功不能证明整体发布兼容。以下为综合设计要求，协议及语言强制由该分支规范决定。

| ID / 条件 | 要求 | 完成证据 / 反例 | 一手依据 |
| --- | --- | --- | --- |
| CE01 / 已有调用方 | MUST 列出 source/binary/ABI/wire/行为/性能成本/权限各维度和稳定承诺；公开身份、完整入口及序列化身份分别保留或迁移。 | 固定旧入口/消费者；未知消费者明确范围，不能凭新增字段称全兼容。 | [AIP-180](https://google.aip.dev/180)；各语言API演进规则。 |
| CE02 / 新旧收发并存 | MUST 给旧读新、新读旧及新/旧写入后再次转发的方向矩阵；保留/丢弃unknown与字段省略/null分别判断。 | 每方向实际parser/consumer；失败方向和数据丢失有明确隔离。 | [ProtoJSON wire safety](https://protobuf.dev/programming-guides/json/#protojson-wire-safety)；格式差异另查。 |
| CE03 / 改输入/输出 | MUST 审查必填、新默认、可空性/范围/枚举/未知属性/字段名/单位；request和response方向相反的兼容风险分别列。 | 旧合法输入不能静默失效；旧输出解析、穷举与patch含义参与检查。 | [AIP-180](https://google.aip.dev/180)、[Kotlin兼容指南](https://kotlinlang.org/docs/api-guidelines-backward-compatibility.html)。 |
| CE04 / 改错误/副作用 | MUST 审查机器错误、错误阶段/优先级、重试类别、幂等作用域、重复处理与取消/删除语义。 | 旧恢复代码仍有正确下一步；错误文案不充当兼容标识。 | [AIP-180](https://google.aip.dev/180)；具体协议错误页。 |
| CE05 / 新接口或扩展点 | MUST 分开“旧client调用”和“旧第三方实现被新host调用”；default method或fallback是否真适配目标runtime另验。 | 未修改旧插件/trait/interface实现参与编译/链接/调用；无实现只标假设。 | [Java JLS13](https://docs.oracle.com/javase/specs/jls/se25/html/jls-13.html)、[.NET Interface Design](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/interface)。 |
| CE06 / 版本控制 | MUST 明确版本属于包/服务/schema/消息/能力或工具链，选择版本的通道和缺省；版本号变化本身不隔离不兼容输出。 | 无新header的旧caller、显式新profile、错版本/能力未知；兼容隔离有具体提案与实现状态。 | [SemVer](https://semver.org/spec/v2.0.0.html)为版本政策；协议输出隔离属设计。 |
| CE07 / 弃用/移除 | MUST 列替代入口、迁移动作、受影响主体、接受政策和退出依据；SHOULD 采用调用侧证据验证迁移，不以文档发布代替消费者变更。 | 固定旧调用+替代调用、可观察弃用信息；未知使用者仍记风险。 | [AIP-180](https://google.aip.dev/180)；采用HTTP弃用机制时查其RFC。 |
| CE08 / 数据持久化/回放 | MUST 覆盖存储旧记录、延迟消息、恢复游标/任务句柄和回滚读取；producer发布与consumer部署顺序有决定。 | 旧数据回放、滚动版本窗口与失败后回滚；不得只验在线最新payload。 | Proto未知字段机制、事件/schema profile；此部署矩阵为内部设计。 |
| CE09 / 工具链/产物改变 | MUST 分开声明检查、实际import、链接、运行和发布包；生成器/runtime版本与entry/feature/平台支持范围有可定位依据。 | 旧消费者接候选实际载体；声明相对导入不能称真实包exports已通过。 | [Node packages](https://nodejs.org/api/packages.html)、[protobuf runtime保证](https://protobuf.dev/support/cross-version-runtime-guarantee/)。 |
| CE10 / 兼容承诺有例外 | MUST 写出被接受的破坏、理由、安全/成本影响、降级/迁移及决策人状态；实验标记不能事后抹掉既有稳定承诺。 | 例外可追踪；未采纳的迁移策略标待决，不能称发布已兼容。 | [AIP-180](https://google.aip.dev/180)、[SemVer](https://semver.org/spec/v2.0.0.html)；项目政策优先。 |

协议变更的具体检测按类型页，程序接口的source/ABI和包工具按[SDK演进](../library-sdk/evolution.md)；这张矩阵要求组合证据，不重复每种格式的兼容机制。
