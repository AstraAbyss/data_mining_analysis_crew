"""
@File: code_builder_tasks.py
@Desc: 定义代码生成任务
"""

from crewai import Task


def create_generate_tool_task(agent, requirement: str) -> Task:
    return Task(
        description=(
            "请根据以下需求，为当前数据挖掘项目生成新的 CrewAI Tool 及相关集成代码。\n\n"
            f"用户需求：\n{requirement}\n\n"
            "执行要求：\n"
            "1. 只能使用 DirectoryReadTool 查看以下目录：examples、skills/project-tool-builder、generated。\n"
            "2. 不允许扫描项目根目录，不允许扫描 .venv、site-packages、__pycache__。\n"
            "3. 必须调用 FileReadTool 读取 examples/sample_tool_example.py。\n"
            "4. 必须调用 FileReadTool 读取 skills/project-tool-builder/SKILL.md。\n"
            "5. 必须参考 project-tool-builder Skill 中的规范。\n"
            "6. 必须生成符合本项目风格的 Tool 代码。\n"
            "7. 必须给出 Agent 挂载示例。\n"
            "8. 必须给出 Task 挂载示例。\n"
            "9. 必须给出 Crew 集成说明。\n"
            "10. 请将 Tool 代码写入 generated/tools/ 目录。\n"
            "11. 请将集成说明写入 generated/docs/ 目录。\n"
        ),
        expected_output=(
            "完整代码生成结果，包括 Tool 文件代码、Agent 示例、Task 示例、"
            "Crew 集成说明和运行说明。"
        ),
        agent=agent,
    )
