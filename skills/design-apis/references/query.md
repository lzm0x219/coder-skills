# 声明式查询与数据访问接口

触发：查询/存储过程/schema/DSL本身是公开契约。内部SQL实现细节不自动成为API；GraphQL查询另走其原生类型页。固定dialect/provider/version、参数协议、结果schema、session/事务及旧consumer。以下是综合设计要求；SQLite/PostgreSQL仅提供机制示例，不能声称所有数据库行为相同。

| ID / 条件 | 具体规则 | 消费证据 / 反例 | 一手依据 / 性质 |
| --- | --- | --- | --- |
| Q01 / 命名查询/schema | MUST 记录查询/过程/列身份、参数顺序或名称、默认、类型/null与结果列/别名；`SELECT *` 的新增列影响strict/位置consumer。 | 固定旧结果reader、列增删/重排/类型；空结果仍保留声明schema。 | 设计；[SQLite SELECT](https://www.sqlite.org/lang_select.html)。 |
| Q02 / 动态输入 | MUST 用adopted参数绑定传值，标识符/排序/操作选择走显式allowlist或provider安全构造；参数不是任意SQL片段。 | 注入字串是值；未知列/排序拒绝；不能用字符串转义代替正确绑定。 | [SQLite binding](https://www.sqlite.org/c3ref/bind_blob.html)、[PostgreSQL PREPARE](https://www.postgresql.org/docs/18/sql-prepare.html)。 |
| Q03 / SQL null | MUST 区分NULL、缺失参数、空值、空结果/聚合结果和三值逻辑；接口映射不把未知布尔当False等价。 | `IS NULL`与普通比较、空集合/COUNT/可空结果；用目标engine核对。 | 格式/机制：[SQLite表达式](https://www.sqlite.org/lang_expr.html)；映射为设计。 |
| Q04 / 多行/分页 | MUST 承诺稳定排序时给显式ORDER BY及唯一tie-break；snapshot/并发插删和token/offset影响写清。 | 同键、空页、并发变化、筛选变化；无ORDER BY不声称返回固定顺序。 | [SQLite ORDER BY](https://www.sqlite.org/lang_select.html#orderby)；稳定分页为设计。 |
| Q05 / 写/事务 | MUST 明确事务拥有者、提交点、隔离/锁及失败后session状态；重试范围是语句还是整个事务，写结果未知时先查证。 | 约束失败、锁冲突、提交中断、rollback与部分副作用；目标provider差异明确。 | [SQLite transaction](https://www.sqlite.org/lang_transaction.html)、[PostgreSQL18 isolation](https://www.postgresql.org/docs/18/transaction-iso.html)。 |
| Q06 / 租户/权限 | MUST 定义执行主体、schema/search_path、row/column权限和过程definer/invoker边界；tenant参数不能自行提升授权。 | 跨租户绑定、宽权限连接、关系访问及默认search_path；真实权限配置另验。 | [安全](common/security.md)；provider权限规范采用版本另查。 |
| Q07 / 连接/statement/cursor | MUST 定义session寿命、prepared statement失效、游标关闭、借用连接归还及取消后复用条件；行迭代可能发生I/O。 | 提前退出、异常、DDL后旧statement、池中状态泄漏；只消费一页不代表释放。 | [PostgreSQL PREPARE](https://www.postgresql.org/docs/18/sql-prepare.html)、[程序资源契约](library-sdk/runtime.md)。 |
| Q08 / 可变查询成本 | MUST 记录最大row/时间/内存/递归/执行计划或可用的准入机制，未知上限为候选；`LIMIT`不保证扫描/聚合成本同样受限。 | 合法语法高成本、被取消/超预算、timeout后的事务状态；模型不证明容量。 | [OWASP API4](https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/)；provider planner/cancel机制另查。 |
| Q09 / 时间/数值/排序规则 | MUST 固定数据域、精度/舍入、timezone、collation及宿主映射；区分声明类型、类型亲和性和实际存储类。动态类型引擎须用采用的约束落实公开域，并校验旧/异常存储的输出映射；跨engine文本/数值排序不默认一致。 | 大整数、decimal、offset时间、非ASCII排序与错误存储类往返，actual reader参与；SQLite TEXT声明不代表拒绝BLOB，异常行不能破坏机器错误合同。 | [数据](common/data.md)、[SQLite动态类型/affinity](https://www.sqlite.org/datatype3.html)；STRICT自3.37.0引入，目标floor须核验。 |
| Q10 / schema演进/发布 | MUST 区分旧查询读新schema、新写回滚到旧reader、procedure signature、session缓存与滚动部署；DDL验证不替代旧consumer。 | 原始查询/参数/输出reader对候选schema；兼容策略/发布接受分别标记。 | [演进](common/evolution.md)、[PostgreSQL PREPARE失效机制](https://www.postgresql.org/docs/18/sql-prepare.html)。 |

交付：实际schema/DDL/查询或DSL定义、参数及结果类型、事务/权限/限制说明，加正常/拒绝/空结果/并发或迁移消费者。使用本地engine测试仅证明该dialect和配置；外部数据服务、生产权限、锁与故障场景按实际证据报告。
