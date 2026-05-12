"""
@File: main.py
@Desc: 数据挖掘与分析 CrewAI Demo 入口。
"""

from utils.file_utils import ensure_dirs
from utils.data_utils import create_sample_customer_data
from crew import create_data_mining_crew


def main() -> None:
    ensure_dirs()
    file_path = create_sample_customer_data("data/raw/sample_customer_data.csv")
    crew = create_data_mining_crew(file_path)
    result = crew.kickoff()

    print("\n========== 数据挖掘分析最终结果 ==========")
    print(result.raw)
    print("\n[OK] 如果 report_writer_tool 调用成功，报告已保存到 outputs/final_report.md")


if __name__ == "__main__":
    main()
