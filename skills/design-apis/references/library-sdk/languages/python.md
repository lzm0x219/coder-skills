# Python 公共 API 映射

适用：目标消费者是 Python distribution/package。按最低 Python 版本、同步/异步入口及实际 type checker 核验；扩展模块的 C ABI 另读 [原生互操作](../native-interop.md)。

- **公开边界：** Python 公共/内部主要靠包文档、导入路径及惯例界定；前导下划线不等同访问控制，`__all__` 也不能替代稳定性声明。支持的导入路径从安装后的 distribution 验证。来源：[PEP 8 Public and Internal Interfaces](https://peps.python.org/pep-0008/#public-and-internal-interfaces)。
- **类型与扩展：** 公开 `Protocol` 描述结构化消费契约，ABC 用于需共享实现/运行期注册的场景；加入抽象成员会影响第三方子类。类型标注不是运行时输入校验；跨语言/网络输入仍走 runtime validation。
- **异常：** 使用有意义的异常层次保留根因；文档说明可恢复类别，禁止将异常 message 当稳定机器协议。避免在库中吞掉 `KeyboardInterrupt`/`CancelledError` 等控制流信号。
- **asyncio：** coroutine 必须由调用者 await 或经明确 task owner 调度；谁持有 task、保存强引用、观察异常、取消和等待清理要明确。`Task.cancel()` 注入 `CancelledError`，协程可清理或延迟取消；取消并不保证远端副作用回滚。async generator 的 `aclose`/异步上下文退出和异常传播要可见。
- **检查：** 安装构建后的 wheel/sdist 到干净 consumer；用项目选定的 mypy/pyright 规则检查 `.pyi`/标注，并分别运行 sync/async 关键失败消费者。type check 不证明动态导入和 runtime 行为。

依据：[Python asyncio Tasks](https://docs.python.org/3/library/asyncio-task.html)、[asyncio Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html)、[PEP 8](https://peps.python.org/pep-0008/)、[Python typing Protocols](https://docs.python.org/3/library/typing.html#typing.Protocol)。Python 文档行为依其所标版本；本页不将 typing 建议误作 runtime enforcement。
