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
    """
    创建一个数据理解专家智能体
    该函数用于初始化并返回一个专门用于数据理解和分析的智能体。
    智能体具有读取数据集、理解字段结构、分析样例数据和确定潜在分析方向的能力。
    Returns:
        Agent: 返回一个配置好的数据理解专家智能体实例
    """
    return Agent(
        role="数据理解专家",  # 智能体的角色定位，负责数据理解任务
        goal="读取数据集并理解字段结构、样例数据和潜在分析方向",  # 智能体的主要目标
        backstory="你擅长快速理解结构化数据，能从字段、样例和类型中判断数据分析方向。",  # 智能体的背景描述和特性
        llm=get_llm(),  # 为智能体配置语言模型
        skills=[SKILL_PATH],  # 智能体具备的技能路径
        tools=[CSVReaderTool(), DataProfileTool()],  # 智能体可使用的工具，包括CSV读取和数据概览工具
        verbose=True,  # 启用详细输出模式，便于调试和观察智能体行为
        allow_delegation=False,  # 禁止任务委派，确保智能体独立完成数据理解任务
    )


def create_data_quality_agent() -> Agent:
    """
    创建一个数据质量检查专家智能体
    该函数用于初始化并返回一个专门用于数据质量检查的Agent实例。
    这个Agent将具备检查数据质量问题并提供清洗建议的能力。
    Returns:
        Agent: 配置好的数据质量检查专家智能体实例
    """
    return Agent(
        role="数据质量检查专家",  # Agent的角色定位
        goal="检查缺失值、重复值、常量字段、异常值候选和数据质量风险",  # Agent的主要目标
        backstory="你是一名数据治理专家，擅长发现数据质量风险并给出清洗建议。",  # Agent的背景设定
        llm=get_llm(),  # 配置语言模型
        skills=[SKILL_PATH],  # 设置技能路径
        tools=[DataQualityTool(), DataProfileTool()],  # 配置可使用的工具
        verbose=True,  # 启用详细输出模式
        allow_delegation=False,  # 禁止任务委托
    )


def create_data_mining_agent() -> Agent:
    # 创建并返回一个数据挖掘分析智能体
    return Agent(
        # 定义智能体的角色为数据挖掘分析专家
        role="数据挖掘分析专家",
        # 智能体的目标是执行探索性数据分析、相关性分析和分组分析，发现关键特征和业务洞察
        goal="执行探索性数据分析、相关性分析和分组分析，发现关键特征和业务洞察",
        # 智能体的背景描述：结合统计结果和业务语义形成稳健洞察的数据挖掘专家
        backstory="你是一名数据挖掘专家，擅长结合统计结果和业务语义形成稳健洞察。",
        # 获取并设置语言模型
        llm=get_llm(),
        # 设置智能体的技能路径
        skills=[SKILL_PATH],
        # 配置智能体可用的工具：摘要分析工具、相关性分析工具和分组分析工具
        tools=[EDASummaryTool(), CorrelationAnalysisTool(), GroupAnalysisTool()],
        # 启用详细输出模式
        verbose=True,
        # 禁止任务委托给其他智能体
        allow_delegation=False,
    )


def create_report_agent() -> Agent:
    # 创建并返回一个报告代理函数
    # 该代理负责整合数据挖掘各阶段的结果，并生成结构化的Markdown报告
    return Agent(
        role="数据挖掘报告专家",  # 定义代理的角色为数据挖掘报告专家
        goal="整合各阶段结果，生成结构化 Markdown 数据挖掘分析报告并保存到本地",  # 设定代理的主要目标
        backstory="你擅长将数据事实、分析推断、业务建议和风险限制组织成清晰报告。",  # 提供代理的背景描述，展示其专长
        llm=get_llm(),  # 获取语言模型实例
        skills=[SKILL_PATH],  # 设置代理所需的技能路径
        tools=[ReportWriterTool()],  # 配置代理可用的工具，特别是报告写入工具
        verbose=True,  # 启用详细输出模式
        allow_delegation=False,  # 禁止任务委派，确保由该代理独立完成报告生成
    )
