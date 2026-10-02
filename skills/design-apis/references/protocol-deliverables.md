# API 契约的设计期交付

适用：具体协议、实时流、自动化或公开查询接口的契约提案；库/SDK/框架使用[声明交付](library-sdk/deliverables.md)。按[共同交付与核验](common.md#delivery-evidence)固定主契约、消费路径和证据，下表补充各类型的载体与消费者。

## 主契约与消费证据

| 接口形态 | 主契约与版本 | 消费证据 |
| --- | --- | --- |
| HTTP / GraphQL | 项目 OpenAPI/等价定义；SDL 与所用 transport profile | 完整 URL 或 named operation、变量、响应及消费者处理。 |
| RPC | 项目 IDL（Proto、Thrift、WSDL 等）或 method/envelope schema；transport/profile | 对应工具生成/解析的消费者与 error/end-of-stream；JSON-RPC notification 无响应，不虚构 ACK。 |
| 事件 / Webhook | 消息 schema、所采用的 CloudEvents/AsyncAPI/broker binding；提供方正式 profile 或自有回调 | 发布/订阅/接收/ACK 的两侧合同和去重恢复；管理接口与数据投递分别验证。 |
| 持续连接 / 流 | 握手与 framing/profile、应用 envelope、状态机、结束/恢复信号 | consumer 解析、慢消费、断线/取消/权限失效；transport frame 不等于业务确认。 |
| CLI / 进程 | argv/options/config、stdin/stdout framing、exit/error 与 signal 合同 | 实际子进程消费者和 pipeline；stdout/stderr/exit 分别断言。 |
| SQL / 查询 / DSL | 固定方言与版本、DDL/公开视图或 query templates、绑定与结果类型、事务/session 合同 | 真实引擎或所采用 DSL parser 的参数与结果消费者，NULL/顺序/失败/旧查询检查。 |

类型/schema 之外的语义按 C05 写入契约说明，用[维度与遗漏检查](coverage.md)及命中分支补齐边界。目标涉及 OS、设备、GPU、宿主 ABI 或专有 profile 时，按其官方版本补充载体与消费检查。

## 核验与状态

按[共同核验](common.md#delivery-evidence)执行与载体版本匹配的解析、编译及语义检查。格式通过仅证明对应格式或类型；HTTP 行为、GraphQL 执行、RPC 调用、broker 投递与 Webhook 来源分别需要对应消费或运行证据。

按[统一交付判据](common.md#delivery-status)报告合同、验证层级与接受状态。示例回归见[协议测试样例](../../../tests/design-apis/README.md)。
