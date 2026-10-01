# refactor-code 独立执行报告

完成三个隔离样例的结构重构。未修改仓库 Skill、references、材料或测试；未读取 rubric.md、verify_cases.cjs 或父级评估结论。原始材料复制到 `/tmp/coder-refactor-baseline-20261001` 后保持只读，实现位于本报告所在目录。

## 操作与结构收益

- library：`src/index.ts` 保留稳定公开入口，重导出 Item、total、format、receipt。`billing/amount.ts` 拥有金额、折扣校验、舍入与 Item 契约；`presentation/money.ts` 拥有金额展示；`receipts/receipt.ts` 组合两者与条目名称。收据依赖金额和展示，二者不反向依赖收据或入口。将来修改折扣范围只涉及金额模块，修改小数展示只涉及展示模块，修改收据分隔符只涉及收据模块。
- async：入口组装 `subscriptions.cjs` 与 `publisher.cjs`。前者私有持有 Set 与 closed 状态及订阅/取消/关闭，后者拥有微任务安排、发布时快照与执行时成员判断。调度策略变化不需操作 Set，订阅管理规则不需了解 queueMicrotask。仍保持单个 bus 共享状态、发布后取消、取消后重订阅、回调异常中止当前循环等原语义。
- duplicate：`charge.cjs` 收敛负值校验、求和、记录、乘数、舍入的顺序。入口保留 retail 与 wholesale，只声明渠道和乘数；修改共同负值规则只涉及一处，渠道业务差异仍在入口明确可见。record 在舍入前调用，record 抛错继续传播。

## 基线与检查

环境：Node.js v26.7.0、pnpm v12.3.4、TypeScript 5.6.3。下列命令均通过 rtk proxy 执行。

| 命令与工作目录 | 退出码与结果 |
| --- | --- |
| `pnpm dlx --package typescript@5.6.3 tsc -p tsconfig.json`，baseline/library | 0，原始 strict 类型检查与声明构建通过 |
| 同一命令，execution/library | 0，移动目录后的 strict 类型检查、原消费者与声明构建通过 |
| `node check.cjs /tmp/coder-refactor-baseline-20261001`，execution | 0，基线特征断言通过，输出保存为 baseline-observations.json |
| `node check.cjs`，execution | 0，重构特征断言通过，输出保存为 final-observations.json |
| `diff -u baseline-observations.json final-observations.json`，execution | 0，无差异 |
| `node native-async.cjs /tmp/coder-refactor-baseline-20261001`，execution | 0，实际微任务输出 `[1,2]` |
| `node native-async.cjs`，execution | 0，实际微任务输出 `[1,2]` |
| `node dist/consumer.js`，execution/library | 0，真实构建制品消费输出 `[ '0.95', 'tea:1.05' ]` |

`check.cjs` 覆盖公共运行导出名、折扣范围错误、空条目、负金额、NaN、格式输出、retail/wholesale 渠道和未调整金额记录、负值不记录、记录异常，以及可控微任务的快照、取消重订阅、回调中成员变化、关闭、重复关闭、关闭后订阅错误、回调异常后的下一次发布。native-async.cjs 验证实际微任务延迟、连续发布顺序与关闭抑制待执行事件。

基线生成声明完整保存在 `library/baseline-dist/src/`，重构生成声明保存在 `library/dist/src/`。前后声明文本因 re-export 路径改变而不同；已直接读取对照，Item 字段、readonly Item[] 参数、可选 discount 参数与返回类型一致，原 consumer.ts 从公开 `./src` 导入的类型检查仍通过。原始声明入口为 baseline-dist/src/index.d.ts，新声明入口为 dist/src/index.d.ts。

检查脚本最初错误地以目录 require .cjs 入口，发生 MODULE_NOT_FOUND；修正脚本为显式 index.cjs 后建立基线。该失败属于执行检查脚本，不属于原样例失败。

## 完成判断与限制

Jev 对首轮有限证据返回「证据不足需阻塞」，置信度 0.31、escalate=true，无具体已确认回归。按规则由 Codex 继续调查，补充原生微任务观察、公开导出检查与 NaN 直接断言；据实际基线、构建、消费者、前后观察和结构检查判断完成本任务的有界验证。Jev 低置信度意见未替代实际检查。

这里没有证明全部可能 JS 输入或所有第三方消费者等价；JSON 样例将数值 NaN 序列化为 null，另有直接 NaN 断言避免将这项误当作数值结果证明。可控调度观察回调异常，实际原生调度检查正常路径与关闭；未在子进程验证原生未捕获微任务异常退出行为。未运行评估方隐藏测试，也未宣称已通过它们。
