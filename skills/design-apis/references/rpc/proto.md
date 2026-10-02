# Protocol Buffers schema 与兼容性

仅在 RPC payload 或跨进程存储使用 Protocol Buffers 时加载。兼容判断必须针对锁定的 protoc、语言 generator/runtime 和实际序列化路径；binary wire、ProtoJSON、TextFormat、生成源码 API 是不同表面，分别给结论。规则依据：[Proto3 Guide](https://protobuf.dev/programming-guides/proto3/)、[Field Presence](https://protobuf.dev/programming-guides/field_presence/)、[ProtoJSON](https://protobuf.dev/programming-guides/json/)、[Best practices](https://protobuf.dev/best-practices/dos-donts/)。

**RP01｜Field tag｜Skill MUST。** 不复用已发布编号；删除时 reserved number，字段名在 JSON/TextFormat/源码暴露场景也 reserved，避免后续误用。用 descriptor 比对并加入故意复用编号的反例；Proto tag 不因字段 rename 改变，但名字兼容另查。规范禁止在声明中再次使用已 reserved 的编号/名称；删除后主动 reserved 及 CI 消费者门禁是官方最佳实践与本 Skill 的演进要求。依据：Proto3 [Reserved Values](https://protobuf.dev/programming-guides/proto3/#reserved-values)。

**RP02｜枚举值｜规范 + Skill。** Proto3 的首个 enum 值 MUST 为零（协议/编译要求）；SHOULD 用 *_UNSPECIFIED 或明确未知含义（官方建议，不是名称语法强制）。删除后保留公开数值/名称、定义 unknown numeric enum 的生成 API 行为并实测是本 Skill 的演进要求。不要把零隐式映射为未经设计的合法业务状态。依据：[Proto3 enum guidance](https://protobuf.dev/programming-guides/proto3/#enum)。

**RP03｜Presence｜Skill MUST。** 对 patch、显式 false/0/空串、清空字段等语义，schema 必须可区分 absent 与显式 default；选择当前 syntax/edition/runtime 支持的 optional、oneof 或 wrapper/operation field mask，并给出 wire roundtrip 证据。必填语义仍由服务验证；presence 本身不证明业务必填。依据：[Field Presence](https://protobuf.dev/programming-guides/field_presence/)。

**RP04｜Oneof｜Skill MUST。** 新增 oneof member 前检查所有旧 reader 的未知字段行为；旧客户端解析后重序列化可能丢失其未知 member，使 oneof 选择消失。不能将新 oneof 成员当作经过旧中间服务无损透传；测试真实旧中继 parse/reserialize。依据：[Proto3 updating a message type](https://protobuf.dev/programming-guides/proto3/#updating)。

**RP05｜ProtoJSON｜Skill MUST。** 针对旧 strict JSON parser、字段 json_name、enum string/name、int64/uint64 字符串映射、未知字段拒绝/忽略分别做消费者测试；忽略未知字段不是保留数据。若仍支持旧 strict consumer，采用旧投影、版本化输出或兼容发布顺序，并验证未修改旧 reader 能读候选响应。JSON numeric precision 必须按真实 parser 处理，禁止经 IEEE-754 number 转换大整数再宣称无损。依据：[ProtoJSON](https://protobuf.dev/programming-guides/json/)。

**RP06｜Wire/生成矩阵｜Skill MUST。** 对 old writer→new reader 与 new writer→old reader 两个方向，分别检查 binary、JSON、源码调用编译；删除/改类型/改语义不可由某一方向成功推断。未知字段在旧 reader 上的保留取决于语言 API 和是否重建消息对象，必须测试消费路径，不只检查 descriptor。依据：[Proto3 guide](https://protobuf.dev/programming-guides/proto3/)、[Cross-version runtime guarantee](https://protobuf.dev/support/cross-version-runtime-guarantee/)。

**RP07｜新字段安全性｜Skill MUST。** 新字段默认不被旧客户端发送，服务器需定义缺失和零值行为；新服务发给旧严格 ProtoJSON client 时按 RP05 处理。不得将“字段可选”本身当作服务语义兼容证明。字段 mask、Any type URL 与 extension 的公开类型稳定性应明确。证据：old/new 生成客户端交叉测试。

**RP08｜IDL 命名/生成 API｜Skill MUST。** package、message、field、enum 与 RPC method 名会映射为多个目标语言符号、JSON 名和 descriptor fully-qualified name；变更前生成受支持语言的 API diff，并对旧源代码消费者编译。generator/runtime 配套版本固定并遵循官方跨版本保证窗口，不以更新 protoc 成功编译作为运行时 ABI 保证。依据：[Cross-version runtime guarantee](https://protobuf.dev/support/cross-version-runtime-guarantee/)。

**RP09｜敏感字段｜Skill MUST。** 不把字段级 deprecated 当作安全擦除；删除敏感数据要说明历史 wire/log/存储/备份中副本的保留和迁移。避免在默认日志、错误 detail 和 debug JSON 暴露秘密；对未知 enum/field 的记录规则覆盖数据最小化。依据：Proto 的格式能力不定义业务安全策略，需结合项目安全要求，作为设计门槛。

**RP10｜Compatibility gate｜Skill MUST。** 运行所选 schema checker 的安全与破坏性演进模式，保存确切工具版本和 breakage class；checker 不能替代旧消费者测试、API 语义评审或迁移方案。交付 compatibility matrix：binary/JSON/source/runtime × old/new reader/writer × pass/fail/未验证及证据路径。
