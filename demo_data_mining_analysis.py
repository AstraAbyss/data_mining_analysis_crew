"""
@File: main.py
@Desc: 数据挖掘与分析 CrewAI Demo 入口。
"""

from utils.file_utils import ensure_dirs
from utils.data_utils import create_sample_customer_data
from crew import create_data_mining_crew


def main() -> None:
    """
    主函数，执行数据挖掘分析流程
    包括创建必要目录、生成示例数据、创建数据挖掘团队并执行分析任务
    """
    ensure_dirs()  # 确保所需的输出目录存在
    file_path = create_sample_customer_data("data/raw/sample_customer_data.csv")
    crew = create_data_mining_crew(file_path)
    result = crew.kickoff()

    print("\n========== 数据挖掘分析最终结果 ==========")
    print(result.raw)
    print("\n[OK] 如果 report_writer_tool 调用成功，报告已保存到 outputs/final_report.md")


if __name__ == "__main__":
    main()
