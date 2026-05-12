from crewai import Agent
from crewai_tools import DirectoryReadTool, FileReadTool, FileWriterTool

from utils.llm import get_llm


def create_project_code_builder_agent() -> Agent:
    """
    创建一个用于构建项目代码的 Agent
    该函数初始化并返回一个专门用于生成 CrewAI 项目代码的 Agent。
    Agent 具备读取目录和文件的能力，可以根据样例代码生成符合规范的新代码。
    Returns:
        Agent: 配置好的 Agent 实例，用于项目代码生成
    """
    # 获取语言模型实例
    llm = get_llm()

    # 定义 Agent 可使用的工具列表
    tools = [
        # 用于读取 examples 目录的内容
        DirectoryReadTool(directory="examples"),
        # 用于读取项目构建工具技能目录
        DirectoryReadTool(directory="skills/project-tool-builder"),
        # 用于读取已生成代码的目录
        DirectoryReadTool(directory="generated"),
        # 用于读取单个文件内容
        FileReadTool(),
        # 用于写入文件
        FileWriterTool(),
    ]

    # 返回配置好的 Agent 实例
    return Agent(
        # Agent 的角色定义
        role="CrewAI 项目代码生成专家",
        # Agent 的目标描述
        goal=(
            "根据用户需求和项目样例，生成符合当前数据挖掘项目规范的 "
            "Tool、Agent、Task 和 Crew 集成代码。"
        ),
        # Agent 的背景故事和专长描述
        backstory=(
            "你熟悉 CrewAI 的 Agent、Task、Crew、Tool 和 Skill 机制。"
            "你擅长根据已有项目结构和代码风格生成可维护的项目代码。"
            "你必须先读取样例代码，再生成新代码。"
        ),
        # 使用的语言模型
        llm=llm,
        # 可用的工具列表
        tools=tools,
        # Agent 使用的技能路径
        skills=[
            "./skills/project-tool-builder"
        ],
        # 是否输出详细日志
        verbose=True,
        # 是否允许委托任务给其他 Agent
        allow_delegation=False,
    )