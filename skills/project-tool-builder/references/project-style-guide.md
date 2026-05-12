# Project Style Guide

## 命名规范

- Tool 文件名：`xxx_tool.py`
- Tool 类名：`XxxTool`
- Tool 输入类名：`XxxInput`
- Tool name：英文小写下划线，例如 `outlier_detection_tool`

## Tool 规范

- 继承 `BaseTool`
- 使用 Pydantic `BaseModel` 定义输入 schema
- `_run()` 返回字符串，推荐 JSON 字符串
- 所有文件路径参数必须检查是否存在
- 不要在 Tool 中执行和职责无关的逻辑

## Agent 规范

- 每个 Agent 只绑定职责相关的工具
- 必须挂载对应 Skill
- `allow_delegation=False`

## Task 规范

- 明确要求调用哪个 Tool
- 明确输入文件路径和关键参数
- 强调必须基于工具真实返回结果
