# 协议分支设计样例回归（2026-09-30）

范围：`coder:design-apis` 的 HTTP、GraphQL、RPC/Proto、事件和 Webhook **固定设计样例**。这是样例和规则的回归证据，不是任意 API 的合规认证，也不是独立代理从零调用 Skill 的评估。

## 已执行

- `rtk proxy python3 skills/design-apis/tests/verify_protocols.py`：5 个分支均通过。脚本在临时目录安装固定版本的 `@apidevtools/swagger-parser 13.1.0`、`graphql 16.14.2`、`protobufjs 7.6.6`、`ajv 8.20.0`、`ajv-formats 3.0.1`。
- `rtk proxy python3 skills/design-apis/tests/verify_library_sdk.py`：Markdown 链接/代码围栏及既有 10 项 SDK 检查通过。
- `quick_validate.py skills/design-apis`：`Skill is valid!`。

| 分支 | 正例与可复查结果 | 反例与拒绝点 | 验证边界 |
| --- | --- | --- | --- |
| HTTP | OpenAPI 3.1.1 可解析；带 `If-Match` 的更新样例与 `204` 定义一致 | 缺少前置条件、无效主体、旧版本和无权且版本过期的组合在本地模型中分别进入 `400`、`400`、`412`、`403` | 未向真实服务发请求，无法证明旧版本不写入 |
| GraphQL | SDL、旧查询校验及普通查询执行通过；解析器错误保留 `order.id` | 删除旧字段导致旧查询校验失败；错误字段改为非空后 `order` 变 `null` | 授权、查询成本及实际解析器未验证 |
| RPC/Proto | 新旧定义能解析；二进制交叉读取保留 `id`；新字段有 presence | 旧字段编号 `2` 赋予新语义，被旧新字段表比较拒绝 | 使用 `protobufjs`，未跑 `protoc`、ProtoJSON、生成客户端和 gRPC 服务 |
| 事件 | JSON Schema 接受有效封装；同 `source + id` 去重模型可复查 | 缺少 `id` 被 schema 拒绝 | 项目 schema 只覆盖样例事件；broker 顺序、重试与保留未验证 |
| Webhook | 原始字节 HMAC 验证和 delivery 去重模型通过 | 载荷篡改及缺失签名被拒绝 | 无真实 GitHub 投递、数据库原子性、密钥轮换或超时测量 |

## 结论

这五个分支达到**可供设计评审**的样例层级：有可定位的契约源、正常路径、关键反例和分层验证结论。不能据此称具体接口“设计通过”；项目设计决策者尚未接受这些候选设计，也未验证运行期行为。独立代理读取 Skill 后能否稳定产出同等级契约仍未测试。
