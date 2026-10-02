# 资料来源与版本约束

下列官方入口于 2026-10-01 核对，用于定位主题资料。引用须匹配项目声明的版本、配置、平台与适用条款，资料不自动成为项目标准；可变网页的当前内容不能解释所有旧版本。

| 主题 | 一手来源 | 用途及限制 |
| --- | --- | --- |
| 审查范围与尺度 | [Google 审查内容](https://google.github.io/eng-practices/review/reviewer/looking-for.html)、[审查准则](https://google.github.io/eng-practices/review/reviewer/standard.html) | 设计、复杂度、测试、命名和文档；接受有依据的等价方案、区分非阻断偏好，不以完美主义拖延；是工程指南，具体发现仍须本项目证据 |
| 安全审查方法 | [OWASP Secure Code Review](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html) | 风险、信任边界和数据流；按触发变化选用，不把安全专项代替功能审查或完整合规评估 |
| 安全开发框架 | [NIST SP 800-218 / SSDF 1.1](https://csrc.nist.gov/pubs/sp/800/218/final) | PW.7 代码审查与发现/修复记录、PW.8 可执行代码测试；高层框架，不自动成为项目流程或法定义务，不以审查代替测试 |
| Agent 文档 | 用户指定的 [writing-for-agents](../../../../../../../.agents/skills/writing-for-agents/SKILL.md) | 按需披露、指针、完成门槛和单一事实源；本地参考不是安装依赖 |
| 安全控制 | [OWASP ASVS](https://owasp.org/projects/asvs) | 已核对版本为 5.0.0；使用所选版本的实际条款，不声称全 ASVS 审计 |
| Web 可访问性 | [WCAG 2.2 Recommendation](https://www.w3.org/TR/2024/REC-WCAG22-20241212/) | 按项目等级及条款例外核验；自动检查不能证明全面符合性 |
| Web 协议 | [HTTP Semantics](https://httpwg.org/specs/rfc9110.html)、[HTTP Caching](https://httpwg.org/specs/rfc9111.html) | 双端与代理语义；框架实际配置仍须检查 |
| 过载与监测 | [SRE Handling Overload](https://sre.google/sre-book/handling-overload/)、[Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/) | 容量与信号概念；本项目预算/SLO 不由书籍代定 |
| CI 信任 | [GitHub Actions Secure Use](https://docs.github.com/en/actions/reference/security/secure-use) | 不可信输入、执行权限与依赖；其他 CI 查对应官方文档 |
| 制品来源 | [SLSA v1.2](https://slsa.dev/spec/v1.2/) | 固定版本的来源保证参考；文件存在不等于等级验证 |
| 服务生命周期 | [Kubernetes Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) | 就绪、终止与排空；按实际集群版本核实 |
| 数据评估 | [scikit-learn Common Pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) | 数据泄漏、训练/服务变换；规则是通用检查，不要求安装该库 |
| 少数类指标 | [Google ML Imbalanced Datasets](https://developers.google.com/machine-learning/crash-course/overfitting/imbalanced-datasets) | 指标与样本总体；不替代实际业务评估 |
| 日期 | [Python datetime](https://docs.python.org/3/library/datetime.html) | aware/naive 与表示；仅 Python 采用对应实际版本 |
| 内存安全 | [Rust Reference: Undefined Behavior](https://doc.rust-lang.org/reference/behavior-considered-undefined.html) | Rust 安全前提；其他语言用其官方内存模型，不能机械套用 |
| 平台生命周期 | [Android Activity Lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle) | 重建/停止等入口；桌面/iOS 另查实际平台资料 |
| RTOS 接口 | [FreeRTOS Kernel task.h](https://github.com/FreeRTOS/FreeRTOS-Kernel/blob/main/include/task.h) | API 与 ISR 约束的官方源码入口；必须固定项目实际 tag/commit，主分支不证明设备时序 |

语言/框架未列出时，执行 [F1](routing.md#f1) 查实际版本权威资料并登记引用；本表不是支持技术栈白名单。硬件 datasheet、领域安全要求及专有协议必须取项目真实材料。
