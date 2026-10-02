# 数据、编码与 schema

触发：接口交换结构化数据，或其类型/序列化会影响调用者。固定采用的格式/dialect、读写方向与解析器；以下 `MUST` 是设计交付要求，具体外部强制见依据列。适用协议的原生机制优先，不把 JSON 限制强加给二进制或内存类型。

| ID / 条件 | 要求与具体规则 | 消费证据 / 关键反例 | 依据与性质 |
| --- | --- | --- | --- |
| CD01 / 使用 schema | MUST 声明 dialect、引用解析基准、外部 `$ref` 的取得方式与固定版本；区分结构校验和业务约束。 | 脱离作者机器解析；引用缺失/错 dialect 不默认为通过。 | 格式：[JSON Schema Core](https://json-schema.org/draft/2020-12/json-schema-core#section-8)；载体按类型选择。 |
| CD02 / 可选或可空字段 | MUST 分别写缺失、null、空字符串/容器、显式零值、默认及 patch 清除效果。默认由谁何时应用；schema 的 `default` 标注不等于自动赋值。 | 省略、null、零、空集合各用实际 reader 验证；修改后状态与规则一致。 | 格式：[Validation §9.2](https://json-schema.org/draft/2020-12/json-schema-validation#section-9.2)；协议专有 presence 另查。 |
| CD03 / JSON 对象 | SHOULD 使用唯一成员名；MUST 决定重复 key 的接收策略，并在鉴权/签名/验证/业务解析链保持一致。不能以最后值覆盖掩盖边界差异。 | 重复身份或金额字段，验证前后解释相同；若采用严格 profile 则拒绝。 | JSON 的唯一名为 SHOULD：[RFC 8259 §4](https://www.rfc-editor.org/rfc/rfc8259#section-4)；拒绝策略属设计。 |
| CD04 / 有数值 | MUST 明确数学域、合法范围、精度、舍入及溢出行为；跨 IEEE-754 reader 的大整数/金额不能先转 number 再称无损。格式不允许 NaN/Infinity 时拒绝。 | 边界整数、超界、非有限值和十进制往返；货币比例/单位必须能解释。 | 格式：[RFC 8259 §6](https://www.rfc-editor.org/rfc/rfc8259#section-6)、[ProtoJSON](https://protobuf.dev/programming-guides/json/#format-description)；业务金额表示属设计。 |
| CD05 / 字符串跨边界 | MUST 确定字符编码、非法序列处理、长度计量是字节/代码点/字素，以及是否正规化。标识符正规化/大小写规则与原始签名字节分开。 | 多字节、组合字符、非法 UTF-8 与长度边界；相似字符不能绕过身份规则。 | 格式：[RFC 8259 §8](https://www.rfc-editor.org/rfc/rfc8259#section-8)；正规化决定属设计。 |
| CD06 / 时间或时长 | MUST 区分时刻、当地日期、时区、持续时间和 deadline；写单位/精度、UTC offset、闰秒支持及越界规则。持续预算使用单调时钟概念，不用可跳变墙钟作等价替代。 | 相同时刻不同 offset、毫秒/秒混淆、夏令转换和预算耗尽。 | 时间格式：[RFC 3339 §5](https://www.rfc-editor.org/rfc/rfc3339#section-5)；deadline 设计按类型。 |
| CD07 / 枚举或状态扩展 | MUST 定义未知值是保留、映射 unknown、拒绝还是触发升级；开放枚举与闭集分别声明。旧客户端穷举分支参与变更检查。 | 新值到旧 reader；未知不变成既有业务状态，不触发错误副作用。 | 设计；格式差异见[ProtoJSON](https://protobuf.dev/programming-guides/json/#protojson-wire-safety)。 |
| CD08 / 未知属性 | MUST 分开请求与响应、生产者与消费者的未知字段政策；严格请求防误用不等于严格响应利于演进。保留/丢弃/转发策略写明。 | 新字段到旧 reader、误拼字段、转发后数据是否丢失。 | 格式：[JSON Schema additionalProperties](https://json-schema.org/draft/2020-12/json-schema-core#section-10.3.2.3)；兼容属于设计。 |
| CD09 / 联合或多态 | MUST 明确判别方式、互斥条件、未知 variant 与新增分支影响。验证所有分支及非法组合，不能仅靠文档标签或工具未执行的 discriminator。 | 正常每分支、同时命中/均不命中、旧消费者读新增 variant。 | 格式：[JSON Schema applicators](https://json-schema.org/draft/2020-12/json-schema-core#section-10.2.1)；OAS/RPC native union 另查。 |
| CD10 / 数据含 bytes | MUST 指定原始 bytes/编码文本、base64 alphabet/padding、长度计量、是否流式及完整性含义。解码成功不证明内容安全或签名正确。 | 空、非 ASCII、损坏编码、截断；原始体签名必须仍用指定原字节。 | 格式：[RFC 4648](https://www.rfc-editor.org/rfc/rfc4648)；传输/签名 profile 决定。 |
| CD11 / URI/ID/游标 | MUST 分开可解析 URI、opaque ID、分页 token 与恢复 cursor，定义作用域/可比较性/编码与过期。未承诺结构的值由调用者原样保存。 | 把一种 token 用于另一通道应拒绝；跨租户/筛选/版本恢复按所选契约。 | URI格式：[RFC 3986](https://www.rfc-editor.org/rfc/rfc3986)；[AIP-158](https://google.aip.dev/158)为生态。 |
| CD12 / 采用 format | MUST 记录校验器的 format-annotation/assertion 支持和配置；URI、时间等需要拒绝非法值时给实际失败证据，不能以 `format` 字段存在称已验证。 | 合法/非法同类型字符串；工具缺格式支持时报告语义检查缺口。 | 格式：[Validation §7](https://json-schema.org/draft/2020-12/json-schema-validation#section-7)。 |
| CD13 / 只读/写入专用字段 | MUST 明确请求/响应中的字段许可，包含系统生成 ID、秘密与计算字段；schema 注释不替代实施校验和响应投影。 | 试写只读字段、读取 write-only 秘密；拒绝/忽略须是具体决定。 | 格式：[Validation §9.4](https://json-schema.org/draft/2020-12/json-schema-validation#section-9.4)；权限决策属设计。 |
| CD14 / 字段集合/顺序有含义 | MUST 明确集合/多重集/有序序列、重复元素、相等键顺序和空结果；对象成员顺序不承载未声明的语义。 | 重排、重复、空页非终态及排序并列；按类型页处理分页。 | 格式：[RFC 8259 §4–5](https://www.rfc-editor.org/rfc/rfc8259#section-4)；集合契约属设计。 |
| CD15 / 变更单位或含义 | MUST 保留稳定字段的原单位/语义；新语义使用明确新字段/variant及迁移，不能同名解释随版本暗变。 | 旧/新 payload 在相同消费者得到相同既有含义；同义替代更新后值一致。 | 生态：[AIP-180](https://google.aip.dev/180)；内部兼容要求。 |
| CD16 / 嵌入内容或链接内容 | MUST 区分容器/schema valid 与嵌入媒体、压缩内容、引用文件是否已验证，明确扩展上限和外部内容取得边界。 | 恶意内容/巨大解压比/外部引用不可访问不算业务消费成功。 | 格式：[Validation §8](https://json-schema.org/draft/2020-12/json-schema-validation#section-8)；成本和信任策略属设计。 |

内存别名/借用/可变输出按[程序接口所有权](../library-sdk/runtime.md)；网络分块与终止按[实时流](../realtime.md)。这两种机制不由 schema 或 JSON roundtrip 证明。
