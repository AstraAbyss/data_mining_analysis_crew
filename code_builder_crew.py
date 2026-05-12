"""
@File: code_builder_crew.py
@Desc: 定义代码生成 Crew
"""

from crewai import Crew, Process

from code_builder_agents import create_project_code_builder_agent
from code_builder_tasks import create_generate_tool_task


def create_code_builder_crew(requirement: str) -> Crew:
    """
    创建一个代码构建团队，用于根据需求生成代码
    参数:
        requirement (str): 用户的需求描述，将作为输入传递给团队
    返回:
        Crew: 一个包含代理和任务的团队对象，设置为顺序处理模式并启用详细输出
    """
    # 创建项目代码构建代理
    agent = create_project_code_builder_agent()

    # 创建生成工具任务，使用指定的代理和需求
    task = create_generate_tool_task(
        agent=agent,
        requirement=requirement,
    )

    # 返回配置好的团队对象
    return Crew(
        agents=[agent],  # 团队包含的代理列表
        tasks=[task],    # 团队需要执行的任务列表
        process=Process.sequential,  # 设置为顺序处理模式
        verbose=True,    # 启用详细输出模式
    )
