"""
@File: demo_generate_tool.py
@Desc: 使用 project-tool-builder Skill 生成新 Tool 示例
"""

import os

from code_builder_crew import create_code_builder_crew


def ensure_generated_dirs():
    os.makedirs("generated/tools", exist_ok=True)
    os.makedirs("generated/agents", exist_ok=True)
    os.makedirs("generated/tasks", exist_ok=True)
    os.makedirs("generated/docs", exist_ok=True)


def main():
    # 确保生成必要的目录结构
    ensure_generated_dirs()

    # 定义数据挖掘项目需求字符串，包含异常值检测工具的详细规格
    requirement = """
    请为当前数据挖掘项目生成一个异常值检测工具。
    
    工具需求：
    1. 工具名称为 outlier_detection_tool。
    2. 输入参数包括：
       - file_path: CSV 文件路径
       - columns: 可选，需要检测异常值的字段列表
       - method: 异常值检测方法，支持 iqr 和 zscore
       - threshold: 阈值，默认 1.5
    3. 工具需要读取 CSV 文件。
    4. 如果 columns 为空，则自动选择所有数值字段。
    5. 输出每个字段的异常值数量、异常值比例、上下界信息。
    6. 返回 JSON 字符串。
    7. 同时给出 Agent 挂载示例、Task 示例和 Crew 集成说明。
    8. 请将 Tool 代码写入 generated/tools/outlier_detection_tool.py。
    9. 请将集成说明写入 generated/docs/outlier_detection_tool_usage.md。
    """

    # 创建代码构建器团队，用于处理上述需求
    crew = create_code_builder_crew(requirement)

    # 启动团队执行任务，获取生成结果
    result = crew.kickoff()

    # 打印代码生成结果，使用分隔线增强可读性
    print("\n========== 代码生成结果 ==========\n")
    print(result.raw)


if __name__ == "__main__":
    main()
