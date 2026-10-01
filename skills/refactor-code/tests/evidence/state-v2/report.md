# Phase B 执行报告

完成账本职责拆分，保留暂停期间用户的 `User total: ` 前缀和 consumer.cjs 编辑。范围仅当前隔离目录，未修改仓库或读取评估方验证器。Phase A 文档与旧检查保持不变。

## 真实状态转移

Phase A 停在 S2，未进入实施。Phase B 恢复核对文件和环境：index/consumer SHA 均变化，baseline-check.cjs SHA 保持 ce6380bd167ad2fa49d29e9bbd65a076c206702ec2983642445774ee6d3fb783。当前 consumer 通过，但旧检查因预期 Total: 与当前 User total: 冲突退出1。

根据 recovery.md 的「基线或环境变化影响兼容观察 → S1，失效对应兼容项」，返回 S1 刷新显示兼容项。未把它归为重构引入失败，也未回滚用户编辑。用户授权的前缀变化是更新断言的依据，不是以重构输出自动刷新 golden。

将用户编辑后的原始实现保存到 user-baseline/index.cjs，原始消费者保存到 user-baseline/consumer.cjs。旧检查在根目录原样保留，并在 user-baseline/baseline-check.cjs 保存副本；对用户基线复跑旧检查的完整真实失败输出保存在 old-check-failure.txt。新 current-check.cjs 明确使用 User total: 契约，对独立用户基线与当前未重构实现均通过，再返回 S2 核对原方案仍适用。

S3 切片1仅提取显示，consumer/current-check 均通过；切片2提取私有实例累计和记录流程，再验证当前全部兼容项。S4 读取最终源码、核对消费者与旧检查 SHA、比较独立基线输出，全部必要项已验证；S5 完成交付。

## 最终结构和收益

- index.cjs：createLedger 稳定入口与实例组装。
- amount.cjs：createAmount 私有持有每实例 amount，read/apply 是有限状态操作；没有模块顶层共享状态。
- posting.cjs：createPosting 集中有限 delta 校验、record 当前值、随后实时 apply 的顺序与异常传播。记录抛错不执行 apply，重入后不会覆盖嵌套累计结果。
- display.cjs：formatTotal 负责用户前缀与两位小数。

显示前缀变化只修改 display；合法 delta 规则只修改 posting；累计规则只修改 amount。入口不再混合这些知识。依赖从入口组装向内，posting 依赖传入状态操作，显示只接受当前值，不持有状态、不依赖 posting。保留 createLedger(initial, record) 与返回 add/receipt，脱离对象调用仍正常。

## 命令与实际结果

Node.js v26.7.0，无依赖安装。默认 cwd 为本报告目录。

| 命令/阶段 | 退出码与输出 |
| --- | --- |
| 恢复：`rtk proxy node consumer.cjs` | 0，consumer PASS |
| 恢复：`rtk proxy node baseline-check.cjs` | 1，AssertionError：actual User total: 2.00，expected Total: 2.00，baseline-check.cjs:11 |
| S1：`rtk proxy node current-check.cjs ./user-baseline/index.cjs > user-baseline-observations.json` | 0，独立新基线输出保存 |
| S1：`rtk proxy node current-check.cjs` | 0，新检查对未重构实现通过 |
| S3切片1：`rtk proxy node consumer.cjs`、`rtk proxy node current-check.cjs` | 均0，consumer PASS 与下列JSON |
| S3切片2：`rtk proxy node consumer.cjs` | 0，consumer PASS |
| S4：`rtk proxy node current-check.cjs > final-observations.json` | 0，最终输出保存 |
| S4：`rtk proxy diff -u user-baseline-observations.json final-observations.json` | 0，无差异 |
| 历史复现：user-baseline 中 `rtk proxy node baseline-check.cjs > ../old-check-failure.txt 2>&1` | 1，完整输出保存，旧契约失败可由未重构新基线复现 |
| 独立消费者：user-baseline 中 `rtk proxy node consumer.cjs` | 0，consumer PASS |

当前基线和最终输出完全相同：

```json
{"exports":["createLedger"],"events":[[2,3,"User total: 2.00"],[2,4,"User total: 2.00"],["nested",6]],"final":"User total: 9.00","failure":"User total: 10.00","a":"User total: 1.00","b":"User total: 5.00","calls":3}
```

兼容项全部已验证：公开导出与原入口消费者、显示前缀/格式、记录旧值和记录次数、非法 delta 先抛错、记录失败不累计、回调重入最终9、实例隔离、负值零、脱离对象调用。CommonJS 源码即本材料的实际制品，无包构建/TS 声明路径。

## 最终状态指纹

`rtk proxy shasum -a 256 index.cjs amount.cjs posting.cjs display.cjs consumer.cjs baseline-check.cjs current-check.cjs`，退出0：

```text
c1abb1ea0b606e3c0bd0a4f0db65d47621dc2e03a2d03b9cfc52bde29340ce11  index.cjs
41a0f80b41d3b31f2e12277c9df714c1a731af923e0972e07b32ad8ba18e37a7  amount.cjs
4aa269b51d327ff3cdd5dd5f1a5eb1f8c3ab468c6768721d6d4c2391da662042  posting.cjs
bee595753c48cd7b7429d8229002c3a40ca8185dbff33ee946ed4a9c17644ec1  display.cjs
2f55827b5a3735c71d8e6f37a3c77b38310ca029176a6275fbd2e5bdc26847d5  consumer.cjs
ce6380bd167ad2fa49d29e9bbd65a076c206702ec2983642445774ee6d3fb783  baseline-check.cjs
0f703e0225cc2e1ba462de261ecb6e0ae24e73dec7a387c07856058166711799  current-check.cjs
```

consumer 指纹与暂停期间用户版本一致；旧检查指纹与 Phase A 一致。基线副本与实际输出可独立复验，未删除旧失败证据。

Jev 对恢复路径选择 S1 刷新基线（0.97），最终判定完成且保留历史旧检查失败与有限输入限制（0.93）；判断依据为上述实际检查和结构证据，不能替代实际测试。未穷尽所有第三方消费者或恶意 JS 输入，未运行评估方隐藏检查；这些不被本报告冒充为已验证。
