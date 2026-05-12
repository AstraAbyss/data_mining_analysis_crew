"""
@File: crew.py
@Desc: 创建数据挖掘分析 Crew。
"""

from crewai import Crew, Process
from agents import (
    create_data_understanding_agent,
    create_data_quality_agent,
    create_data_mining_agent,
    create_report_agent,
)
from tasks import (
    create_data_understanding_task,
    create_data_quality_task,
    create_eda_task,
    create_relation_task,
    create_final_report_task,
)


def create_data_mining_crew(file_path: str) -> Crew:
    """
    创建一个数据挖掘团队，包含多个专业代理和任务
    参数:
        file_path (str): 数据文件的路径
    返回:
        Crew: 包含所有代理和任务的团队对象
    """
    # 创建数据理解代理
    understanding_agent = create_data_understanding_agent()
    # 创建数据质量检查代理
    quality_agent = create_data_quality_agent()
    # 创建数据挖掘代理
    mining_agent = create_data_mining_agent()
    # 创建报告生成代理
    report_agent = create_report_agent()

    # 创建数据理解任务，需要数据理解代理和文件路径
    understanding_task = create_data_understanding_task(understanding_agent, file_path)
    # 创建数据质量任务，需要质量检查代理、文件路径和数据理解任务作为前置任务
    quality_task = create_data_quality_task(quality_agent, file_path, [understanding_task])
    # 创建探索性数据分析任务，需要挖掘代理、文件路径以及之前的数据理解任务和质量任务作为前置
    eda_task = create_eda_task(mining_agent, file_path, [understanding_task, quality_task])
    # 创建关系分析任务，需要挖掘代理、文件路径以及之前的所有任务作为前置
    relation_task = create_relation_task(mining_agent, file_path, [understanding_task, quality_task, eda_task])
    # 创建最终报告任务，需要报告代理、输出路径和所有之前的任务作为上下文
    final_report_task = create_final_report_task(
        report_agent,
        output_path="outputs/final_report.md",
        context_tasks=[understanding_task, quality_task, eda_task, relation_task],
    )

    # 返回一个包含所有代理和任务的团队，使用顺序执行流程
    return Crew(
        agents=[understanding_agent, quality_agent, mining_agent, report_agent],
        tasks=[understanding_task, quality_task, eda_task, relation_task, final_report_task],
        process=Process.sequential,
        verbose=True,
    )
