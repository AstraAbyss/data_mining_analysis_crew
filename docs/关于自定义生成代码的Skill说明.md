# Project Tool Builder Skill Demo

用于给数据挖掘 CrewAI 项目增加一个 `project-tool-builder` Skill，让 Agent 能参考项目样例，生成符合项目规范的 Tool、Agent、Task 和 Crew 集成代码。

## 目录结构

```text
data_mining_analysis_crew/
├── skills/project-tool-builder/
│   ├── SKILL.md
│   └── references/
├── examples/sample_tool_example.py
├── generated/
├── utils/llm.py
├── code_builder_agents.py
├── code_builder_tasks.py
├── code_builder_crew.py
├── demo_generate_tool.py
└── .env
```

## 使用方式

1. 安装依赖：

```bash
pip install crewai crewai-tools python-dotenv pandas pydantic
```

2. 运行示例：

```bash
python demo_generate_tool.py
```

## 运行目标

默认 Demo 会要求 Agent 生成一个异常值检测工具：

```text
generated/tools/outlier_detection_tool.py
generated/docs/outlier_detection_tool_usage.md
```

## 设计说明

- Skill 负责规定“如何写符合项目规范的 Tool/Agent/Task/Crew”。
- DirectoryReadTool 负责读取项目结构。
- FileReadTool 负责读取样例代码。
- FileWriterTool 负责写入生成文件。
- Agent 根据 Skill + 示例 + 用户需求生成代码。
