# 机器调用的 CLI / 进程接口

触发：命令被脚本、其他程序或管道依赖；不是把所有交互式UI改成机器协议。固定平台、shell/直接exec、命令版本、编码和旧调用者。若命令又调用服务，组合相应API规则。POSIX习惯只在目标平台/profile采用时适用；下列严格等级是本 Skill 的交付要求。

## 参数与环境

| ID / 条件 | 具体规则 | 可检查证据 | 一手依据 / 性质 |
| --- | --- | --- | --- |
| CL01 / argv | MUST 写选项、参数、operand、重复/未知选项、`--`、空值/缺失及解析错误；目标POSIX profile按其语法指南，长选项属项目扩展。 | 含空格/非ASCII/前导`-`的operand通过实际exec；缺参/未知/重复有明确失败。 | [POSIX.1-2024 §12](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap12.html)。 |
| CL02 / 接受用户值 | MUST 把值作为独立argv传递，不用shell拼接；必须支持shell表达式的入口明确语法、信任与转义边界。 | `$()`、引号、换行和通配符作为literal或按已采用语法处理，不误执行。 | [POSIX Shell §2](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html)；直接exec为设计。 |
| CL03 / env/config | MUST 决定flag/env/file/default的优先级、作用域、配置读取时点和秘密位置；环境设置错误不得静默忽略。 | 多来源冲突；子进程继承范围；日志/错误/进程参数中无秘密。 | 设计；POSIX environment和[安全](common/security.md)。 |
| CL04 / stdin或文件 | MUST 指明stdin是否被消费、EOF意义、编码、输入格式、最大量及重复`-`规则；重试时不可默认stdin可回放。 | 无stdin/管道EOF、空输入、截断及已消费后重试；明确是否输出副作用。 | [POSIX Utilities §1](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap01.html)；消费边界为设计。 |

## 输出与结束

| ID / 条件 | 具体规则 | 可检查证据 | 依据 / 性质 |
| --- | --- | --- | --- |
| CL05 / machine mode | MUST 固定机器输出schema/版本、stdout数据与stderr诊断、TTY差异及color/progress/交互行为；机器模式不弹交互问答或夹杂非schema文本。 | redirected stdout可由严格consumer解析；提示/诊断只在约定通道。 | 设计；[POSIX stdout/stderr约定](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap01.html)。 |
| CL06 / JSON或record流 | MUST 选择单JSON、JSON-lines或RFC7464等framing、编码、空流、末尾及截断处理；合法单record不证明完整操作成功。 | 逐块读、多字节分割、末record不完整及中途失败；正常结束另有证据。 | JSON：[RFC8259](https://www.rfc-editor.org/rfc/rfc8259)；JSON-seq：[RFC7464](https://www.rfc-editor.org/rfc/rfc7464)。 |
| CL07 / exit | MUST 定义成功/usage/输入/权限/部分失败/内部失败的可识别状态，保留平台signal终止差异；消费者不解析人类错误文案。 | 正反调用同时断言stdout/stderr与退出状态；跨平台不强套同一signal数值。 | [POSIX.1-2024 Utilities §1.4](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap01.html)描述 utility 的 `EXIT STATUS`；本表的错误分类为设计。 |
| CL08 / 管道与取消 | MUST 明确broken pipe、超时/信号、已写部分输出/副作用和子进程清理；停止等待不代表远端或文件操作回滚。 | consumer提前关闭、执行超时、signal后状态；无孤儿或未释放资源承诺另需运行证据。 | 平台机制+内部设计；远端取消按相应类型。 |
| CL09 / 批量或写文件 | MUST 决定逐项/整体原子性、覆盖/append、路径权限、冲突、部分结果和恢复；dry-run的副作用边界具体化。 | 第二项失败、重复调用、目标已存在；不能因进程非零猜所有写入未发生。 | 设计；POSIX文件机制与[共同状态走查](common.md)。 |
| CL10 / 稳定自动化 | MUST 将command/subcommand/flags/env/输出字段/exit变化纳入兼容；版本/help的机器可发现入口写入契约。 | 未修改旧argv/输出reader参与验证，TTY展示变化与机器协议变化分开。 | [演进](common/evolution.md)；POSIX adopted profile。 |

## 交付

主契约采用实际参数定义/机器schema/退出状态表与行为说明；提供直接argv消费者及成功、关键失败、管道/部分结果场景。运行真实本地进程可以验证解析和流通道；合成fixture不证明生产命令或下游服务。不得仅凭README命令行示例称整个自动化契约已验证。
