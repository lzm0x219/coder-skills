# refactor-code 实施与限定评测

日期：2026-10-01。用户确认规划后实施；本地入口、三份按需参考和 master 路由已完成。未安装或发布。

这是初版记录；后续按 writing-for-agents 完善状态机及四份规则，当前增量证据见[状态机与规则修订](state-machine-rules-2026-10-01.md)。

## 已运行的证据

| 层级 | 结果与证据 |
| --- | --- |
| 格式 | bundled Python 执行 skill-creator/quick_validate.py，Skill is valid |
| 材料自检 | `rtk proxy python3 skills/refactor-code/tests/run_cases.py`：TS 5.6.3 strict 构建、公共消费者、运行契约、异步与计费检查通过；取消回归变体被拒绝 |
| 独立实施 | 执行代理读取 Skill 和原材料，未读 rubric 或评估验证器；重设计 TS 业务目录、拆分订阅与调度、收敛计费规则。见[执行报告](../evidence/execution/report.md)及该目录源码、前后观察与声明 |
| 评估方复验 | `rtk proxy python3 skills/refactor-code/tests/run_cases.py /tmp/coder-refactor-execution-20261001` 通过；另读取前后声明，签名、Item 字段、readonly 参数和 discount 可选性保持，重导出路径变化有消费者检查支持 |
| 边界执行 | 第二代理运行旧失败、用户改动、只读和缺私有依赖四组人工项目。见[边界报告](../evidence/boundaries/report.md)、原始源码、指纹和退出码 |
| 边界复验 | 父级重跑保存的四个 consumer，均退出 0；旧失败与缺包 runtime 均按预期退出 1。原只读源码与无关失败指纹保持，USER Total: 前缀保留；代理的公共入口四组差分退出 0 |
| 路由 | 接入后独立代理读取 master，对目录重构、取消故障、PR 审查、新 API、只读机会分析五个自然目标进行语义走查，路由分别对应 refactor-code、fix-bugs、review-changes、design-apis、常规只读分析 |

## 收益与兼容

TS 库稳定入口下，金额规则、金额展示、收据组合拥有独立职责和单向依赖。异步模块的订阅集合与关闭状态有单一所有者，调度通过内部操作读取状态；计费共同验证与求和只维护一处，渠道与倍率保持可见。变化实例与实际源码见执行报告；这些是小案例中的结构收益，不是生产维护效率测量。

原消费者、生成制品、前后特征断言与原生微任务观察通过。边界项目保留已有失败和用户编辑；私有依赖缺失案例仅验证纯模块，集成仍未验证。

Jev 最终选择“本地实施与限定案例评测完成”，报告置信度 1.0；路由选择“独立代理规则语义走查”，置信度 1.0。其依据是以上核验事实，不替代实际运行或用户授权。执行代理首轮低置信度结果及边界代理只读判断的升级，由 Codex 补证或依明确授权处理，详见原报告。

## 复验方式与限制

从仓库根运行 `rtk proxy python3 skills/refactor-code/tests/run_cases.py skills/refactor-code/tests/evidence/execution`，会重建保存的 TS 执行制品并运行评估方检查；未保存 node_modules，需要可用的 pnpm/TypeScript 下载或缓存。原始材料自检使用临时目录。

证据目录的 `.d.ts` 是评测时的生成声明快照，运行构建可能重生成 execution/library/dist；原始声明保存在 baseline-dist。边界 verify.py 会更新日志与指纹，若需重跑请在隔离副本运行；build-fixtures.py 是代理的原始材料构建记录，不应覆盖已保存的执行结果。

八类规划场景均有对应材料或评测记录，其中自然路由只达到语义走查层。未验证插件安装后自动发现、生产服务、任意第三方消费者、所有 JS 输入、其他语言及私有集成环境；原生未捕获微任务异常退出行为未做子进程验证。不得将本记录解释为全类型生产验证或满分。
