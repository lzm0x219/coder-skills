# Phase A：原始基线与结构方案

当前停在 S2 方案已确定，尚未进入 S3。实施授权已存在，但本轮明确要求仅建立基线与方案；等待 Phase B 消息再修改实现。

范围：仅 `/tmp/coder-refactor-state-v2-20261001`。使用 apply_patch 原样复制 state-transitions 的 index.cjs 与 consumer.cjs，新增本地 baseline-check.cjs。未修改仓库文件，未读取 rubric、评估验证器或评估记录。

## 源码状态与环境

Node.js v26.7.0，无外部安装。SHA256：

- index.cjs：9bb4aeb6ca195557afa0f18d57d4e9669dec35ba36350eb24d1fd7367f2c07bf
- consumer.cjs：f2dc07212bf4145e1ca06e5d4efcf722df451ede5f2facd9998fefad4f762c9d
- baseline-check.cjs：ce6380bd167ad2fa49d29e9bbd65a076c206702ec2983642445774ee6d3fb783

以上指纹绑定当前未重构实现；Phase B 恢复首先核对源码、消费者、检查和环境变化，不能直接沿用记录推定代码仍相同。

## 实际命令与结果

工作目录均为本报告所在目录。

| 命令 | 退出码 | 实际输出 |
| --- | --- | --- |
| `rtk proxy node --version` | 0 | `v26.7.0` |
| `rtk proxy node consumer.cjs` | 0 | `consumer PASS` |
| `rtk proxy node baseline-check.cjs` | 0 | 下列 JSON |
| `rtk proxy shasum -a 256 index.cjs consumer.cjs baseline-check.cjs` | 0 | 上述指纹 |

```json
{"exports":["createLedger"],"events":[[2,3,"Total: 2.00"],[2,4,"Total: 2.00"],["nested",6]],"final":"Total: 9.00","failure":"Total: 10.00","a":"Total: 1.00","b":"Total: 5.00","calls":3}
```

## 兼容账：全部为基线已建立，尚无重构后已验证项

| 观察与契约来源 | 输入/方法与原始结果 | Phase B 检查 |
| --- | --- | --- |
| 公共入口 index.cjs/createLedger 与原 consumer | exports 只有 createLedger，consumer PASS | 原入口复跑两脚本 |
| 实例状态归属：每次 createLedger 私有 amount | a 改动后 b 仍 Total: 5.00 | 两实例反例 |
| 记录先于累计，回调可观察旧值 | 初值2/add3，record 收到2,3，receipt 2.00 | events 对照 |
| 回调重入使用同一实例实时状态 | nested add4 得6，outer add3 最终9；不能提前缓存 next amount | 重入断言 |
| 记录错误同步传播，不执行外层累计 | record-failed 抛出后仍 Total:10.00 | 错误类型/消息与状态断言 |
| 非有限 delta 校验先于记录 | NaN/±Infinity/string/null/undefined 均 RangeError delta，记录次数0 | 错误与副作用断言 |
| 负值和零允许，方法不依赖 this | 负数与0正常累计，脱离对象 add/receipt 正常 | 现有断言 |
| 显示前缀与两位小数 | Total: n.nn，实时读取私有状态 | receipt 对照 |

原有失败：未发现。环境缺口：无。未知第三方消费者未提供，本轮证据限于原入口、给定消费者及所列特征观察；没有宣称穷尽任意 JS 输入。模块无包构建配置，运行入口就是实际 CommonJS 源码制品，TypeScript 声明检查不适用。

## 结构方案与切片

维护变化实例：修改账本显示前缀不应理解记录与累计；调整合法 delta 规则不应修改金额存储；记录回调协议及执行时机集中在一个业务流程中，避免金额状态被模块顶层共享或提前缓存。

目标文件：

- index.cjs：保持 createLedger(initial, record) 公开入口，创建每个实例的状态并组装 add/receipt。
- amount.cjs：createAmount(initial) 封闭每个实例的 amount，提供 read 和 apply(delta)；apply 对当前实时值累计，不接管 record。
- posting.cjs：createPosting(amount, record) 生成 add，拥有有限 delta 校验、record(amount.read(), delta)、随后 amount.apply(delta) 的完整业务顺序。记录异常继续传播，重入后使用实时 amount。
- display.cjs：格式化当前金额为 Total: 加 toFixed(2)，不拥有状态或记录。

依赖：入口组装各职责；posting 通过有界 read/apply 操作使用实例状态，display 只接受当前金额。amount/display 不反向依赖 posting 或公共入口；不存在全局 amount。

切片1：提取显示格式，入口仍读取原状态；复跑 consumer 和 baseline-check，验收显示规则独立。
切片2：提取实例累计与记录业务流程，保留公共组装入口；复跑所有特征检查，重点错误时机、重入实时值、实例隔离；验收状态单一所有者和记录流程唯一位置。
S4：核对最终差异、入口及职责结构，再绑定最后检查与源码指纹。未影响的检查不机械重复。

Jev 已用于判断当前证据是否满足 Phase A 边界，具体结果随执行回报；判断不能替代 Phase B 指令。目前实现仍是原始版本，下一步仅等待 Phase B。
