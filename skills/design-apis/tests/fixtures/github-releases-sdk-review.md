# 真实服务契约复测：GitHub Releases

状态：对 `design-apis` 的小范围设计复测；没有实现或发布新 SDK。输入是 [GitHub Releases 官方接口](https://docs.github.com/en/rest/releases/releases)、[GitHub 分页说明](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api)及可类型检查的 [原始消费者代码](github-releases-consumer.ts)。本次只评审“列出某仓库的一页 Release”，不推断整个 GitHub SDK 的设计。

## 已核验事实与中性模型

- 官方操作名为 **List releases**，路径是 `GET /repos/{owner}/{repo}/releases`。响应中的对象有独立 `id` 和 `tag_name`；官方明确说明列表不包括未关联 Release 的普通 Git tag。这是服务契约证据，不是本项目创造的术语。
- `owner`、`repo` 必填；`per_page` 默认 30、最大 100；`page` 默认 1。官方列出的结果码包括 200 与 404。公开资源可以无凭据读取；草稿 Release 的可见范围不同。
- 中性对象 E1 是返回列表中的一项，E2 是一次请求取回的一页。E2 的页码和 `Link` 响应头说明继续取页的位置；本次没有取得“跨页快照一致”保证。
- 此复测选用 `X-GitHub-Api-Version: 2026-03-10`。版本号来自官方示例；SDK 若要支持多版本，须另定范围与迁移策略。

## 命名准入

| 候选 | 判定 |
| --- | --- |
| `releases` | 通过事实判定：官方资源与操作均使用 Release，E1 具有 Release 身份。 |
| `tags` | 排除：官方明确指出普通 Git tag 不一定是 Release，名称会扩大 E1 的含义。 |
| `listPage` | **本复测的设计决策**：若 SDK 每次只发一个请求、只返回 E2，一页边界应在调用点可见；官方没有要求 SDK 使用这个方法名。 |
| `list` | 也可成立，但应搭配明确的一页返回类型，或用于分页迭代器；不能让调用者误以为一次调用取得全部结果。 |

拟议调用点是 `client.releases.listPage({ owner: "cli", repo: "cli", page: 1, pageSize: 2 })`。`releases` 的结论有外部契约依据；`listPage` 是此候选 SDK 的取舍，两者的证据等级不同。与 FileFlow 的 `jobs` 暂定状态也不同：这里已有服务术语可排除 `tags`。

## 契约与消费者走查

原始消费者 [fetchReleasePage](github-releases-consumer.ts) 使用一次请求、显式页码、固定 API 版本与 `Link` 中的 `next` 关系；`pageSize` 在本地限制为 1..100，示例只投影 `id` 和 `tag_name`。它没有自动收集全部页，也没有把 404 擅自解释成唯一一种业务原因。拟议 SDK 对应地应返回单页内容与继续条件；不能承诺跨页快照或无重复遍历。若加入自动重试，须另写次数、预算与限流处理，不能从 GET 方法本身推出具体策略。

正常路径：2026-09-30 对公开仓库 `cli/cli` 的第 1 页发出无凭据请求，`per_page=2`，响应为 200、2 项，`Link` 有 `next`，服务确认所选版本为 `2026-03-10`。失败路径：空 `owner` 在本地得到 `invalid_input`；请求一个不存在的仓库得到 `GitHub HTTP 404`。这些只验证本次输入与当前服务行为；不证明鉴权、限流、页面变化或其他失败路径。

## 本次复测结论

| 规则 | 证据 | 结论 |
| --- | --- | --- |
| D01、D02 | 官方 Release 术语与“普通 tag 不等于 Release” | `releases` 可由既有事实支持；`tags` 不准确。 |
| D08、W04 | `page`、`per_page` 和 `Link`；单次请求消费者 | `listPage` 可作为明确的设计取舍；没有全量或快照承诺。 |
| W06、S04 | 版本请求头固定；仅测试一个公开资源 | 多版本、鉴权及支持环境仍属候选 SDK 的未决设计，不写作通过。 |

类型检查只验证消费者代码的 TypeScript 形式，单次实时请求只验证已观察的响应。此案例证明规则能区分已有术语、设计取舍与未知契约；它不是完整 SDK 发布验收。
