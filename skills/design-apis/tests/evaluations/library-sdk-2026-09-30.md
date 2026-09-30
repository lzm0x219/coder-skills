# `library-sdk` 设计期能力复核（2026-09-30）

**限定范围评分：10/10。** 评分对象是 `coder:design-apis` 对具体 Library / SDK / Framework API 的**设计期规则与可检查交付**，不是 SDK 实现、真实服务行为、发布包质量或代理调用成功率。每项按可观察证据给 0、1、2 分；只有规则可执行且至少有对应样例或检查时给 2 分。

| 维度 | 分数 | 证据 |
| --- | ---: | --- |
| 路由与适用边界 | 2/2 | [主 Skill](../../SKILL.md)按 API 类型分流；[程序接口入口](../../references/library-sdk.md)再按命名、运行、远程、演化和交付任务选规则。 |
| 语义与命名 | 2/2 | [命名准入](../../references/library-sdk/naming.md)要求先识别对象、走查相反解释和信息不足情形；[设计规则](../../references/library-sdk/design.md)与[评审规则](../../references/library-sdk/review.md)要求在调用点写出缺省、错误、资源与取舍。FileFlow、Stripe Webhook 和 S3 三个设计例有不同领域压力。 |
| 语言级交付 | 2/2 | [交付要求](../../references/library-sdk/deliverables.md)规定候选公开声明、正常及关键失败消费者、语义说明和分层验证；[语言映射](../../references/library-sdk/languages.md)指明载体。TypeScript、Python `.pyi`、Rust 框架 trait 和[更完整的 Rust 审计 SDK 候选](../fixtures/rust-audit-sdk/contract.md)均有可检查调用点。 |
| 演化与负对照 | 2/2 | [演化规则](../../references/library-sdk/evolution.md)分源码、运行、数据、环境等维度与阶段；[TypeScript 演化例](../fixtures/typescript-sdk-evolution/contract.md)保持同一旧消费者在 v1、候选 v2 都可编译，删除 `limit` 后仅因 `TS2353` 失败。无完整弃用计划时不标记 `@deprecated`。 |
| 可复现验证与结论边界 | 2/2 | [回归脚本](../verify_library_sdk.py)用精确版本依赖在临时目录检查多语言样例和文档；设计稿明确静态检查、语义走查与运行验证的差别。Skill 元数据验证通过。 |

## 本轮复现

在项目根目录运行 `rtk proxy python3 skills/design-apis/tests/verify_library_sdk.py`，检查 Markdown 相对链接与围栏、临时 TypeScript 依赖、TypeScript v1 与候选消费者、精确的破坏性反例、FileFlow 与 Stripe、S3、Python 审计 SDK、Rust BlobStore，以及 Rust 审计 SDK 的格式、消费者编译和严格 Clippy。脚本安装固定版本 TypeScript 5.6.3、`@aws-sdk/client-s3` 3.1142.0、`@types/node` 24.19.0，调用 Pyright 1.1.414 和本机 Cargo；需要 `rtk`、`pnpm`、`cargo` 及可用的包缓存或网络。

补充复核：最初的 Rust BlobStore 例子只验证小型框架扩展点，作为“Rust SDK 设计已充分覆盖”的证据过窄。新增审计 SDK 候选后，构造、凭据、异步、分页、错误、保密诊断和并发调用点才有独立可检查样例；10 分仅按本页定义的设计期静态范围重新成立。

另用 `skill-creator/scripts/quick_validate.py` 验证 `skills/design-apis`，结果为 `Skill is valid!`。该工具位于本机 Codex Skill 安装目录，不是本项目自带的检查程序。

## 评分边界

- 这些例子中的 FileFlow、审计服务、搜索服务与 BlobStore 是设计测试对象，不证明其真实服务或实现存在。GitHub Releases 的[真实服务局部复测](../fixtures/github-releases-sdk-review.md)只覆盖该文档写明的范围。
- 类型检查和编译未验证运行行为、候选包真实导出、发布兼容、外部服务、ABI、资源释放或安全实现。设计接受仍需项目决策者确认。
- Go 工具链在本机是未配置版本的 mise shim，因此没有 Go 样例编译证据；语言映射表不等于所有语言都已验收。
- 本轮没有独立代理按 Skill 从零完成任务的对照试验；10/10 不代表触发准确率或执行成功率已达 100%。

后续若扩大评分对象到真实 SDK 实现或代理使用效果，必须另建基准并重新评分，不能沿用这里的 10 分。
