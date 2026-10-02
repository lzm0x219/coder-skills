# TypeScript / JavaScript 公共 API 映射

适用：目标消费者使用 npm package、Node.js 或声明文件；具体 Node/browser/其他 runtime 和 TS `moduleResolution` 是契约条件。包入口另读 [包与平台产物](../packaging.md)。

- **声明与实现：** `.d.ts` 描述真实 JS 运行时能力；不要用 overload、泛型或 `readonly` 承诺实现并未满足的行为。结构化对象只读属性不是深冻结；运行期深度变更按 runtime contract 说明。对外声明应由发布 package consumer 验证，而非仅检查仓库内部相对路径。
- **错误与异步：** Promise rejection 的错误类型和同步抛出边界都属于调用语义；不要让同一参数错误有时同步抛、有时 reject，除非明确选择该契约。异步 iterator 的 `return()`、取消、下一页 I/O 与错误发生位置都须定义；AbortSignal 的传播不代表远端事务已撤销。
- **module resolution：** 显式测试项目所承诺的 ESM `import` 与 CommonJS `require` 入口、子路径、types 条件和最低 Node/TypeScript 解析器。双入口若分别创建 singleton，消费者可能观察到两份状态；以真实发布包检查。Node `exports` 的封闭子路径及条件键顺序是 Node 语义，不能泛化为浏览器 bundler 规则。
- **兼容演化：** `.d.ts` 可检查源码类型兼容；运行时导出、默认值、对象枚举行为及 JS 消费者是独立维度。新增必选属性、窄化参数或改 Promise 行为可能破坏纯 JavaScript 调用者。
- **检查：** `tsc --noEmit` 配合每个导入模式的消费者；打包后通过 Node 解析入口并执行最小调用。未发布实际包时标记模块解析未验证。

依据：[TypeScript Declaration Files: Publishing](https://www.typescriptlang.org/docs/handbook/declaration-files/publishing.html)、[Modules: Theory](https://www.typescriptlang.org/docs/handbook/modules/theory.html)、[Object Types: readonly](https://www.typescriptlang.org/docs/handbook/2/objects.html#readonly-properties)、[Node.js Packages](https://nodejs.org/api/packages.html)。TypeScript 文档约束类型声明工具行为；Node 条件导出结论只适用于相应 Node 版本。
