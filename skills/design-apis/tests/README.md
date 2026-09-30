# design-apis 测试样例

`fixtures/` 存放设计提案的主契约、消费样例和故意错误的反例；它不是正式产品文档。各样例用 `contract.md` 标明设计决策、来源和未验证行为。

| 分支 | 样例 | 可执行检查 |
| --- | --- | --- |
| HTTP | [条件更新](fixtures/http-profile/contract.md) | OpenAPI 解析、必需前置条件、正反请求与响应形状 |
| GraphQL | [部分失败与迁移](fixtures/graphql-order/contract.md) | SDL/旧查询校验、执行错误传播与反例 |
| gRPC/Proto | [字段演进](fixtures/rpc-profile/contract.md) | Proto 解析、二进制新旧读取、编号重用反例 |
| 事件 | [订单创建](fixtures/events-order/contract.md) | 事件 schema 正反样例及去重键模型 |
| Webhook | [GitHub 接收](fixtures/webhook-github/contract.md) | 原始字节验签、篡改和重复 delivery 模型 |
| 库/SDK | [设计期记录](evaluations/library-sdk-2026-09-30.md) | TypeScript、Python、Rust 类型及兼容性反例 |

运行 `rtk proxy python3 skills/design-apis/tests/verify_protocols.py` 检查五种协议样例；运行 `rtk proxy python3 skills/design-apis/tests/verify_library_sdk.py` 检查 SDK 样例。脚本在临时目录安装固定版本的校验依赖，不修改仓库依赖。通过表示这些**固定样例**在覆盖范围内得到验证；服务、broker、第三方投递与独立代理从零执行仍须另行验证。

本轮结果与未覆盖项见[协议样例回归记录](evaluations/protocol-design-2026-09-30.md)。
