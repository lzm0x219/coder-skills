# 测试

各套件维护当前检查命令与范围：[master](master/README.md)、[design-apis](design-apis/README.md)、[fix-bugs](fix-bugs/README.md)、[review-changes](review-changes/README.md)、[refactor-code](refactor-code/README.md)。

`methods/` 保存评测准则，`cases/` 保存可复用输入与消费者，`checks/` 保存检查器。JSON、schema、Proto、GraphQL、类型声明及依赖配置是测试输入，随对应案例维护。

从仓库根运行：

```sh
rtk proxy python3 tests/check-layout.py
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/fix-bugs/scripts/tests
rtk proxy env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/review-changes/checks -p 'verify_*.py'
rtk proxy python3 tests/refactor-code/checks/verify_basis.py
rtk proxy python3 tests/refactor-code/checks/run_cases.py
rtk proxy python3 tests/design-apis/checks/verify_protocols.py
rtk proxy python3 tests/design-apis/checks/verify_library_sdk.py
```

Python、Git 与相应平台工具按检查需要使用；API/重构检查器将依赖和生成物放入临时目录。部分命令安装固定版本 Node/Python 依赖，SDK 检查还需 Rust。缺少平台工具时，测试的 skip 只表示未覆盖。

检查结果限于实际导航、格式、类型、输入向量、模型或本地执行。材料自检与智能体独立使用分别记录；当前检查通过不表示所有协议、生产环境或代理行为通过。[独立任务评测](agent-evals/README.md)保存首轮输入、首次产物和版本指纹；产物复核在临时目录进行，不代替重新启动代理。
