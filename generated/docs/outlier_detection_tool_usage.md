# 异常值检测工具 (OutlierDetectionTool) 使用指南

## 一、工具简介

`OutlierDetectionTool` 是一个基于 CrewAI 框架的异常值检测工具，用于从 CSV 文件中读取数据并对指定字段（或所有数值字段）进行异常值检测分析。

### 支持的方法

| 方法 | 说明 | 适用场景 | 常用阈值 |
|------|------|----------|----------|
| `iqr` | 四分位距法 (Interquartile Range) | 数据分布偏态较强，含极端值时 | 1.5（中度异常）/ 3（极度异常） |
| `zscore` | Z-Score 标准分数法 | 数据近似正态分布时 | 2（宽松）/ 3（严格） |

---

## 二、安装依赖

确保已安装所需依赖：

```bash
pip install pandas numpy scipy crewai
```

---

## 三、Tool 代码文件

**文件位置：** `generated/tools/outlier_detection_tool.py`

---

## 四、独立使用示例

```python
from generated.tools.outlier_detection_tool import OutlierDetectionTool

# 初始化工具
tool = OutlierDetectionTool()

# 示例 1：使用 IQR 方法检测所有数值字段
result = tool.run(
    file_path="./data/dataset.csv",
    method="iqr",
    threshold=1.5
)
print(result)

# 示例 2：使用 Z-Score 方法检测指定字段
result = tool.run(
    file_path="./data/dataset.csv",
    columns=["age", "salary", "score"],
    method="zscore",
    threshold=3.0
)
print(result)

# 示例 3：仅检测单个字段
result = tool.run(
    file_path="./data/dataset.csv",
    columns=["price"],
    method="iqr",
    threshold=3.0
)
print(result)
```

---

## 五、Agent 挂载示例

将工具挂载到 Agent 上，使 Agent 具备异常值检测能力：

```python
from crewai import Agent
from generated.tools.outlier_detection_tool import OutlierDetectionTool

def create_data_quality_agent(llm):
    """创建数据质量分析 Agent"""
    return Agent(
        role="数据质量分析师",
        goal="对数据集进行全面的质量检测，包括异常值识别、缺失值分析和数据分布评估",
        backstory=(
            "你是一名资深的数据质量分析师，擅长从数据中发现异常模式。"
            "你精通统计学方法，能够准确识别数据集中的异常值，"
            "并为后续的数据清洗和预处理提供专业建议。"
        ),
        llm=llm,
        tools=[OutlierDetectionTool()],
        skills=["./skills/data-mining-analysis"],
        verbose=True,
        allow_delegation=False,
    )
```

---

## 六、Task 挂载示例

在 Task 中使用工具进行异常值检测：

### 示例 1：基础异常值检测任务

```python
from crewai import Task
from generated.tools.outlier_detection_tool import OutlierDetectionTool

outlier_detection_task = Task(
    description=(
        "对数据集 {file_path} 进行异常值检测。\n"
        "1. 使用 IQR 方法，阈值为 1.5，检测所有数值字段的异常值。\n"
        "2. 对于异常值比例超过 5% 的字段，使用 Z-Score 方法（阈值=3）进行交叉验证。\n"
        "3. 输出每个字段的异常值数量、比例、上下界以及异常值的具体取值。\n"
        "4. 根据检测结果给出数据清洗建议。"
    ),
    expected_output=(
        "一个结构化的 JSON 报告，包含：\n"
        "- 每个字段的异常值检测结果（数量、比例、上下界）\n"
        "- 异常值具体取值预览（最多前 10 个）\n"
        "- 基于异常值分析的数据清洗建议"
    ),
    tools=[OutlierDetectionTool()],
    agent=data_quality_agent,  # 对应上面创建的 Agent
)
```

### 示例 2：高级异常值分析任务

```python
advanced_outlier_task = Task(
    description=(
        "对数据集 {file_path} 进行深度异常值分析：\n"
        "1. 使用 IQR 方法（threshold=1.5）检测所有数值字段的异常值。\n"
        "2. 针对字段 {columns}，使用 Z-Score 方法（threshold=3）进行精确检测。\n"
        "3. 对比两种方法的检测结果差异。\n"
        "4. 统计每个字段异常值的占比，判断数据质量等级。\n"
        "5. 给出是否删除异常值、替换或保留的建议。"
    ),
    expected_output=(
        "包含 IQR 和 Z-Score 两种方法对比的异常值检测报告，"
        "以及数据质量评估和处理建议。"
    ),
    tools=[OutlierDetectionTool()],
    agent=data_quality_agent,
)
```

---

## 七、Crew 集成说明

将 Agent、Task 和 Tool 集成到 Crew 中：

### 完整集成示例

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""异常值检测 Crew 集成示例"""

import os
from crewai import Agent, Crew, Task, Process
from crewai.llm import LLM

from generated.tools.outlier_detection_tool import OutlierDetectionTool


def create_crew(file_path: str, columns: list = None):
    """
    创建并运行异常值检测 Crew。

    Args:
        file_path: CSV 数据集路径
        columns: 待检测字段列表（可选）
    """
    # 1. 初始化 LLM
    llm = LLM(
        model=os.getenv("LLM_MODEL", "gpt-4"),
        api_key=os.getenv("LLM_API_KEY"),
        temperature=0.1,
    )

    # 2. 创建工具实例
    outlier_tool = OutlierDetectionTool()

    # 3. 创建 Agent
    data_quality_agent = Agent(
        role="数据质量分析师",
        goal="对数据集进行全面的异常值检测分析，确保数据质量",
        backstory=(
            "你是一名经验丰富的数据质量分析师，精通统计学和数据分析。"
            "你擅长使用 IQR 和 Z-Score 等方法精准识别异常值，"
            "并能为数据清洗提供专业建议。"
        ),
        llm=llm,
        tools=[outlier_tool],
        skills=["./skills/data-mining-analysis"],
        verbose=True,
        allow_delegation=False,
    )

    # 4. 创建 Task
    outlier_detection_task = Task(
        description=(
            f"对数据集 {file_path} 进行全面的异常值检测：\n"
            f"1. 使用 IQR 方法（threshold=1.5）检测所有数值字段。\n"
            f"{'2. 重点关注字段: ' + str(columns) if columns else '2. 自动检测所有数值字段。'}\n"
            f"3. 输出每个字段的异常值数量、比例、上下界信息。\n"
            f"4. 对异常值比例超过 5% 的字段进行重点分析。\n"
            f"5. 给出数据清洗和处理的建议。"
        ),
        expected_output=(
            "一个完整的异常值检测报告，包含：\n"
            "- 数据集基本信息（总记录数、字段数）\n"
            "- 每个数值字段的异常值检测结果\n"
            "- 异常值取值预览\n"
            "- 数据质量评估结论和清洗建议"
        ),
        tools=[outlier_tool],
        agent=data_quality_agent,
    )

    # 5. 创建 Crew
    crew = Crew(
        agents=[data_quality_agent],
        tasks=[outlier_detection_task],
        process=Process.sequential,
        verbose=True,
    )

    return crew


# ===== 运行入口 =====
if __name__ == "__main__":
    crew = create_crew(
        file_path="./data/sample_dataset.csv",
        columns=["age", "salary", "experience_years"],
    )
    result = crew.kickoff()
    print("=" * 60)
    print("异常值检测完成！")
    print("=" * 60)
    print(result)
```

---

## 八、返回结果格式说明

工具返回的 JSON 结果结构如下：

```json
{
  "status": "success",
  "method": "iqr",
  "threshold": 1.5,
  "total_records": 1000,
  "detected_fields": ["age", "salary", "score"],
  "results": {
    "age": {
      "field": "age",
      "method": "iqr",
      "threshold": 1.5,
      "total_count": 1000,
      "outlier_count": 12,
      "outlier_ratio": 0.012,
      "outlier_ratio_percent": "1.20%",
      "q1": 25.0,
      "q3": 45.0,
      "iqr": 20.0,
      "lower_bound": -5.0,
      "upper_bound": 75.0,
      "outlier_values": [82, 85, 90, 2, 3, ...],
      "outlier_preview_count": 10
    },
    "salary": {
      "field": "salary",
      "method": "iqr",
      "threshold": 1.5,
      "total_count": 998,
      "outlier_count": 5,
      "outlier_ratio": 0.005,
      "outlier_ratio_percent": "0.50%",
      "q1": 35000.0,
      "q3": 85000.0,
      "iqr": 50000.0,
      "lower_bound": -40000.0,
      "upper_bound": 160000.0,
      "outlier_values": [250000, 300000, ...],
      "outlier_preview_count": 3
    }
  }
}
```

### 结果字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 执行状态: `success` / `warning` / `error` |
| `method` | string | 使用的检测方法 |
| `threshold` | float | 设定的阈值 |
| `total_records` | int | CSV 文件总记录数 |
| `detected_fields` | list | 实际检测的字段列表 |
| `results` | object | 每个字段的检测结果 |
| `field` | string | 字段名称 |
| `outlier_count` | int | 异常值数量 |
| `outlier_ratio` | float | 异常值比例（小数） |
| `outlier_ratio_percent` | string | 异常值比例（百分比） |
| `lower_bound` | float | 下界（低于此值为异常） |
| `upper_bound` | float | 上界（高于此值为异常） |
| `outlier_values` | list | 异常值取值预览（最多 10 个） |

---

## 九、注意事项

1. **数据量要求**：每个字段至少需要 4 条有效数据才能进行异常值检测。
2. **缺失值处理**：工具自动忽略缺失值（NaN），不会将其视为异常值。
3. **非数值字段**：工具会自动跳过非数值字段，不会报错。
4. **阈值选择建议**：
   - IQR 方法：`threshold=1.5` 适用于常规检测，`threshold=3` 适用于严格检测。
   - Z-Score 方法：`threshold=2` 较为宽松，`threshold=3` 较为严格。
5. **性能考虑**：对于超大文件（百万级以上），建议先进行数据采样。
6. **异常值预览**：仅展示前 10 个异常值，完整列表需自行从数据中提取。
