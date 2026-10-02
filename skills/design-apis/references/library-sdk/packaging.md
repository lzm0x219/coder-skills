# 包、模块与平台产物

适用：公共包通过一个或多个模块系统、平台目标、feature 或运行时形态交付。此处只定义消费者实际解析、安装和加载的契约；类型声明正确不代表包入口或产物正确。

## X. 包装与平台边界

**X01｜条件｜MUST 逐个列出支持的消费者入口。** 对每个受支持的模块系统/加载方式，记录包名、公开子路径、运行时入口、类型入口及导出限制；用该入口编写消费者导入。Node `exports` 存在时限制通过包名解析的未声明子路径，不能以仓库文件可达推断包路径可导入；绝对文件路径可绕过包名导出限制，`exports` 不是文件访问控制或机密保护边界。例外：纯源码交付且无包解析承诺时按实际导入路径核验。证据为导出清单及对每个承诺入口的消费者检查。来源事实：Node.js Packages 的 `exports` / subpath exports；本条跨生态要求为综合设计建议。

**X02｜条件｜MUST 保持运行时实现与类型/声明入口同一公开形状。** TypeScript 声明、Python stub、Java/Kotlin 元数据或 C/C++ header 必须指向实际交付的 API；至少让消费者经安装/打包后的产物导入并调用一个代表性签名。实际交付归档时，MUST 核对完整文件清单：声明必需入口/声明/header/资源、允许的可选内容及禁止内容，确认目标文件存在，机密配置或凭据未混入；源码、测试、文档或 source map 是否分发按项目政策判断，不一律禁止。检查真实 tarball/wheel/JAR/crate 等产物，不能仅凭仓库配置或入口导入成功称打包内容正确。尚无产物时只设计清单/排除政策并标未验证，不制造归档通过。只对孤立 `.d.ts`、`.pyi` 或源目录执行静态检查时，明确标记包解析未验证。例外：尚无产物的提案仅能标为候选声明检查。证据为构建包后的消费者调用、实际归档清单与项目内容政策的核对结果及导出列表。来源：TypeScript Declaration Files 的 Publishing；Node.js Packages 的 Dual CommonJS/ESM 与 conditional exports；[npm v11 `files`](https://docs.npmjs.com/cli/v11/configuring-npm/package-json#files) 与 [`npm pack`](https://docs.npmjs.com/cli/v11/commands/npm-pack) 提供归档机制，`files` 可省略且不是全生态强制白名单；内容核对是 Skill 交付要求。

**X03｜条件｜MUST 对条件入口检查解析一致性。** 同时发布 ESM/CJS、平台专用入口、开发/生产条件或子路径时，写出每个条件选择的目标文件、互操作限制及类型解析关系；对声称支持的解析模式分别执行最小导入检查。避免同一包名在不同入口暴露语义不兼容的类型或状态单例。某模式未检查时将该格标为未验证，不从另一模式推定通过。来源事实：Node.js Packages `Conditional exports`、`Dual CommonJS/ES module packages`；本条的逐格验收为综合建议。

**X04｜条件｜MUST 把 feature / optional dependency 作为 API 维度声明。** 对 Rust Cargo features、平台标记依赖或可选组件，记录 feature 名、互斥/组合约束、默认集合、公开项是否随配置出现及最低支持工具链；在文档承诺的 feature 组合上编译消费者。不要把一个 feature 下可见误写成默认可见。项目尚未定矩阵时，列出待决组合并标记未验证。来源事实：Cargo Book 的 Features 与 package targets；兼容性影响参考 Cargo SemVer Compatibility。

**X05｜条件｜MUST 定义最低运行时/工具链与目标平台支持范围。** 公开契约涉及原生库、语言运行时、架构、操作系统或编译器 ABI 时，声明实际承诺的组合和降级行为，并分别验证组合；不声称“跨平台”而不给出矩阵。选择新 API、语法或二进制格式时，以支持矩阵内最低版本的一手规范为准。证据是构建/导入矩阵；缺失的真实设备、架构或运行时结果保持未知。来源：Rust Target features / Cargo targets、Node.js Packages 条件导出、项目目标平台的官方支持文档。此条是本项目的交付要求，不代表任一语言官方强制矩阵。

**X06｜条件｜SHOULD 让默认安装仅包含默认承诺能力。** 可选原生库、外部工具、平台资源及大体积组件应能从包清单识别；缺失可选能力时，导入或调用给出稳定的能力/安装错误，并说明补装或禁用入口。只有所有消费者都需要且目标平台已限定时，才把依赖设为强制。证据为干净环境安装/导入及缺依赖反例。来源：Cargo Book Optional dependencies / features、Node.js package entry points；属于综合生态建议。

## 资料边界

Node 的 `exports`、Cargo feature/target 语义是各自工具的规范事实；X01–X06 是跨生态检查要求，不能替代各包管理器的具体配置规则。版本/解析行为应按项目实际最低 Node、TypeScript、Cargo/Rust 或其他目标版本核验。
