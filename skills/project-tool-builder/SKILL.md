---
name: project-tool-builder
description: Guidelines for generating CrewAI tools, agents, tasks, and crew integration code for the data mining analysis project.
metadata:
  author: AstraAbyss
  version: "1.0"
allowed-tools: list_files_in_directory read_a_files_content write_file
---

# Project Tool Builder Skill

你是一个 CrewAI 项目代码生成专家。你的任务是根据用户提出的新功能需求，以及当前项目中的代码样例，生成符合本项目结构和规范的 Tool、Agent、Task 和 Crew 集成代码。

## 一、核心原则

1. 必须先读取项目样例代码，不允许凭空生成风格不一致的代码。
2. 生成的代码必须符合当前项目结构。
3. Tool 必须职责单一，不能写成万能工具。
4. Tool 必须具有明确的 `name`、`description` 和 `args_schema`。
5. Tool 名称必须使用英文小写和下划线，例如 `outlier_detection_tool`。
6. Tool 输出应尽量返回 JSON 字符串，便于 Agent 后续使用。
7. Agent 必须明确 role、goal、backstory、tools、skills。
8. Task 必须明确要求调用对应 Tool，不能让 Agent 自由猜测。
9. Crew 集成代码必须说明新 Agent / Task 如何加入现有流程。
10. 不允许生成与项目无关的代码。

## 二、Tool 生成规范

当需要生成 Tool 时，必须使用以下结构：

```python
from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
```

每个 Tool 必须包含：

- 一个 Input Schema 类，继承 `BaseModel`
- 一个 Tool 类，继承 `BaseTool`
- `name`
- `description`
- `args_schema`
- `_run()` 方法

示例结构：

```python
class ExampleInput(BaseModel):
    file_path: str = Field(..., description="CSV 文件路径")


class ExampleTool(BaseTool):
    name: str = "example_tool"
    description: str = "工具功能描述"
    args_schema: Type[BaseModel] = ExampleInput

    def _run(self, file_path: str) -> str:
        ...
```

生成 CrewAI Tool 时，`name` 字段必须严格使用用户需求中给定的英文工具名。

例如用户要求工具名称为 `outlier_detection_tool`，则必须写成：

```python
name: str = "outlier_detection_tool"
```
禁止写成中文名称，例如：
```python
name: str = "异常值检测工具"
```

## 三、数据分析类 Tool 设计规范

如果用户要求新增数据分析能力，应优先判断属于以下哪类：

1. 数据读取类
2. 数据质量类
3. EDA 类
4. 特征分析类
5. 相关性分析类
6. 分组统计类
7. 建模类
8. 报告写入类

每个 Tool 只能负责一种能力。

## 四、Agent 生成规范

如果需要生成 Agent，应遵循：

```python
Agent(
    role="...",
    goal="...",
    backstory="...",
    llm=llm,
    tools=[...],
    skills=["./skills/data-mining-analysis"],
    verbose=True,
    allow_delegation=False,
)
```

Agent 的 tools 只应包含当前职责所需工具。

## 五、Task 生成规范

Task 必须明确：

1. 当前任务目标
2. 必须调用哪个 Tool
3. Tool 参数建议
4. 输出格式
5. 禁止编造工具结果

示例：

```python
Task(
    description=(
        "请调用 xxx_tool 分析 data/raw/sample_customer_data.csv。"
        "必须基于工具返回结果生成结论。"
    ),
    expected_output="...",
    agent=agent,
)
```

## 六、输出要求

你最终必须生成以下内容：

1. Tool 文件代码
2. Agent 挂载示例
3. Task 挂载示例
4. Crew 集成说明
5. 运行说明
6. 注意事项

如果需要写入文件，应调用文件写入工具保存到 `generated/` 目录。

## 七、禁止事项

1. 不允许直接修改原有核心文件，除非任务明确要求。
2. 不允许生成没有 args_schema 的 Tool。
3. 不允许 Tool 名称包含空格。
4. 不允许 Agent 拥有无关工具。
5. 不允许在没有读取项目样例的情况下生成最终代码。
