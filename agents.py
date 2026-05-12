"""
@File: agents.py
@Desc: 定义数据挖掘分析流程中的 Agent。
"""

from crewai import Agent
from utils.llm import get_llm
from tools import (
    CSVReaderTool,
    DataProfileTool,
    DataQualityTool,
    EDASummaryTool,
    CorrelationAnalysisTool,
    GroupAnalysisTool,
    ReportWriterTool,
)

SKILL_PATH = "./skills/data-mining-analysis"


def create_data_understanding_agent() -> Agent:
    return Agent(
        role="数据理解专家",
        goal="读取数据集并理解字段结构、样例数据和潜在分析方向",
        backstory="你擅长快速理解结构化数据，能从字段、样例和类型中判断数据分析方向。",
        llm=get_llm(),
        skills=[SKILL_PATH],
        tools=[CSVReaderTool(), DataProfileTool()],
        verbose=True,
        allow_delegation=False,
    )


def create_data_quality_agent() -> Agent:
    return Agent(
        role="数据质量检查专家",
        goal="检查缺失值、重复值、常量字段、异常值候选和数据质量风险",
        backstory="你是一名数据治理专家，擅长发现数据质量风险并给出清洗建议。",
        llm=get_llm(),
        skills=[SKILL_PATH],
        tools=[DataQualityTool(), DataProfileTool()],
        verbose=True,
        allow_delegation=False,
    )


def create_data_mining_agent() -> Agent:
    return Agent(
        role="数据挖掘分析专家",
        goal="执行探索性数据分析、相关性分析和分组分析，发现关键特征和业务洞察",
        backstory="你是一名数据挖掘专家，擅长结合统计结果和业务语义形成稳健洞察。",
        llm=get_llm(),
        skills=[SKILL_PATH],
        tools=[EDASummaryTool(), CorrelationAnalysisTool(), GroupAnalysisTool()],
        verbose=True,
        allow_delegation=False,
    )


def create_report_agent() -> Agent:
    return Agent(
        role="数据挖掘报告专家",
        goal="整合各阶段结果，生成结构化 Markdown 数据挖掘分析报告并保存到本地",
        backstory="你擅长将数据事实、分析推断、业务建议和风险限制组织成清晰报告。",
        llm=get_llm(),
        skills=[SKILL_PATH],
        tools=[ReportWriterTool()],
        verbose=True,
        allow_delegation=False,
    )
