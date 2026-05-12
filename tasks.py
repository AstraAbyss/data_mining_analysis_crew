"""
@File: tasks.py
@Desc: 定义数据挖掘分析任务链。
"""

from crewai import Task


def create_data_understanding_task(agent, file_path: str) -> Task:
    return Task(
        description=(
            f"请分析数据文件：{file_path}\n"
            "必须调用 csv_reader_tool 获取行列数、字段名和样例数据；"
            "必须调用 data_profile_tool 获取字段画像。"
            "基于工具真实返回结果，说明数据规模、字段类型、字段含义推测和潜在分析方向。"
        ),
        expected_output="数据理解报告，包括数据规模、字段清单、字段类型、样例解读和潜在分析方向。",
        agent=agent,
    )


def create_data_quality_task(agent, file_path: str, context_tasks=None) -> Task:
    return Task(
        description=(
            f"请对数据文件进行质量检查：{file_path}\n"
            "必须调用 data_quality_tool 检查缺失值、重复行、常量字段和异常值候选；"
            "必要时调用 data_profile_tool 辅助解释字段质量。"
            "请基于工具结果输出数据质量问题清单和清洗建议。"
        ),
        expected_output="数据质量报告，包括缺失值、重复值、常量字段、异常值候选、风险等级和清洗建议。",
        agent=agent,
        context=context_tasks or [],
    )


def create_eda_task(agent, file_path: str, context_tasks=None) -> Task:
    return Task(
        description=(
            f"请对数据文件执行探索性数据分析：{file_path}\n"
            "必须调用 eda_summary_tool 分析数值字段和类别字段分布。"
            "请输出关键字段的分布特征、可能异常模式和初步业务洞察。"
        ),
        expected_output="探索性数据分析报告，包括数值字段分布、类别字段频次、异常模式和初步洞察。",
        agent=agent,
        context=context_tasks or [],
    )


def create_relation_task(agent, file_path: str, context_tasks=None) -> Task:
    return Task(
        description=(
            f"请对数据文件执行相关性和分组分析：{file_path}\n"
            "必须调用 correlation_analysis_tool，method='pearson', threshold=0.5。"
            "必须至少调用一次 group_analysis_tool，优先分析 membership_level 对 churn 或 monthly_spend 的差异；"
            "如果字段不适合，请选择更合适的分组字段和目标字段。"
            "请注意相关性不等于因果关系。"
        ),
        expected_output="相关性与分组分析报告，包括强相关字段对、关键分组差异、业务解释和限制说明。",
        agent=agent,
        context=context_tasks or [],
    )


def create_final_report_task(agent, output_path: str = "outputs/final_report.md", context_tasks=None) -> Task:
    return Task(
        description=(
            "请整合前面所有任务结果，生成完整 Markdown 数据挖掘分析报告。"
            f"必须调用 report_writer_tool 将最终报告写入：{output_path}。"
            "报告必须遵循 data-mining-analysis skill 中的报告结构，"
            "并明确区分数据事实、分析推断、业务建议和风险限制。"
        ),
        expected_output="最终 Markdown 数据挖掘分析报告，并确认已写入 outputs/final_report.md。",
        agent=agent,
        context=context_tasks or [],
    )
