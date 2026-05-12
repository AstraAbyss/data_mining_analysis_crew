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
    understanding_agent = create_data_understanding_agent()
    quality_agent = create_data_quality_agent()
    mining_agent = create_data_mining_agent()
    report_agent = create_report_agent()

    understanding_task = create_data_understanding_task(understanding_agent, file_path)
    quality_task = create_data_quality_task(quality_agent, file_path, [understanding_task])
    eda_task = create_eda_task(mining_agent, file_path, [understanding_task, quality_task])
    relation_task = create_relation_task(mining_agent, file_path, [understanding_task, quality_task, eda_task])
    final_report_task = create_final_report_task(
        report_agent,
        output_path="outputs/final_report.md",
        context_tasks=[understanding_task, quality_task, eda_task, relation_task],
    )

    return Crew(
        agents=[understanding_agent, quality_agent, mining_agent, report_agent],
        tasks=[understanding_task, quality_task, eda_task, relation_task, final_report_task],
        process=Process.sequential,
        verbose=True,
    )
