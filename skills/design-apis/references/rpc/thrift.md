# Apache Thrift

仅在 Apache Thrift IDL/runtime/transport 被选用时命中。固定 compiler 与各语言 runtime 版本、协议（binary/compact/JSON 等）、transport 和服务端调用栈；不同语言支持矩阵可能不同。Thrift 官方 IDL 页面当前标记 version 0.25.0，项目应记录实际工具版本而不是默认跟随文档版本。依据：[IDL](https://thrift.apache.org/docs/idl)、[Types](https://thrift.apache.org/docs/types)、[Concepts](https://thrift.apache.org/docs/concepts.html)、[Language/Feature Matrix](https://thrift.apache.org/docs/Languages.html)。

**RT01｜字段 ID｜Skill MUST。** 对 struct/exception/args/result 固定字段 ID；发布后不复用删除 ID。改名、改类型、改 requiredness、default 或语义，按各协议编码和各语言映射逐项检查。仓库用 compiler parse 并与基线 AST/descriptor 比较，重用 ID 负例必须被拒。IDL 编译通过不等于 wire compatibility。

**RT02｜Requiredness｜Skill MUST。** 对每字段写明 required、optional 或 implicit default 的读写规则。官方 IDL 明确 required 缺失读会失败，且 required 字段不能安全删除/弃用；除必须兼容的遗留场景外，新字段优先采用可演进的默认 requiredness 或 optional，并实测目标语言的 isset/默认行为。禁止把关键业务校验只寄托在 schema requiredness。依据：[IDL Field Requiredness](https://thrift.apache.org/docs/idl#field)。

**RT03｜Default 值｜Skill MUST。** Thrift 默认值可能由语言实现初始化、可能不在 wire 写出；默认值变更会影响未写字段解读。给字段记录 unset、explicit default、wire omitted 三态的业务含义；需要区分缺失与默认值时用 optional/isset 并在目标 runtime 做 roundtrip，而不是只看 IDL。依据：[IDL Semantics of Default Values](https://thrift.apache.org/docs/idl#semantics-of-default-values)。

**RT04｜Service 方法｜Skill MUST。** 每个方法固定参数 ID、返回类型、异常列表、oneway 与同步响应行为；调用方区分业务异常、TApplicationException/transport failure 和超时。oneway 不返回应用级结果，不能用来表达需确认或需重试的持久命令；服务端可能已经处理但响应丢失时按未知副作用处置。需一手校验具体行为时对目标语言的生成代码与协议实现执行 loopback。

**RT05｜协议/传输组合｜Skill MUST。** 明确 TCP/HTTP/自定义 transport、framed/unframed、binary/compact/JSON 编码、消息长度/资源上限和连接复用；不能以 Thrift IDL 描述推断每一语言组合互通。通过官方语言功能矩阵选择实际支持组合，跨语言 golden bytes/loopback 证明编码兼容。

**RT06｜演进矩阵｜Skill MUST。** 生成旧/新客户端与服务端，分别测试旧写→新读、新写→旧读，并覆盖缺字段、未知字段、enum 未知值、optional isset、默认值与 exception。兼容结论限定到确切 serializer/runtime/transport 版本和方向；未支持目标语言列为限制而非假定相同。

**RT07｜异常与错误语义｜Skill MUST。** 声明每个业务 exception 的稳定 wire field ID/schema、触发条件、客户端处理动作和可重试性；未声明异常按 transport/runtime 错误处理时，将副作用未知显式暴露。不要仅用异常 class 名或本地字符串假设跨语言通用。

**RT08｜IDL 代码生成｜Skill MUST。** 将 compiler、生成器选项、include 路径、language namespace 和 runtime 配置纳入可重现构建；提交生成源代码消费者示例或生成 API diff。检查生成后 public symbols、async/sync 形态和 mapping exceptions；不得仅凭 .thrift 文本评审 SDK/ABI。
