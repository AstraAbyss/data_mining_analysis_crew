# 异常值检测工具 (Outlier Detection Tool) 使用说明

## 工具概述

`outlier_detection_tool` 是一个用于检测 CSV 文件中数值字段异常值的 CrewAI 工具。支持 IQR（四分位距法）和 Z-Score（Z 分数法）两种检测方法。

## 工具信息

| 属性 | 说明 |
|------|------|
| **工具名称** | `outlier_detection_tool` |
| **类名** | `OutlierDetectionTool` |
| **文件路径** | `generated/tools/outlier_detection_tool.py` |
| **输入模型** | `OutlierDetectionInput` |

## 输入参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `file_path` | `str` | 是 | - | CSV 文件路径 |
| `columns` | `Optional[List[str]]` | 否 | `None` | 需要检测的字段列表。为空时自动选择所有数值字段 |
| `method` | `str` | 否 | `"iqr"` | 检测方法：`"iqr"` 或 `"zscore"` |
| `threshold` | `float` | 否 | `1.5` | 异常值判定阈值 |

## 检测方法说明

### 1. IQR 方法（四分位距法）

- 计算第一四分位数（Q1）和第三四分位数（Q3）
- IQR = Q3 - Q1
- 下界 = Q1 - threshold × IQR
- 上界 = Q3 + threshold × IQR
- 超出上下界的值即为异常值
- **建议阈值**：1.5（中度异常）、3.0（极度异常）

### 2. Z-Score 方法（Z 分数法）

- 计算均值（mean）和标准差（std）
- Z = (x - mean) / std
- |Z| > threshold 的值即为异常值
- **建议阈值**：2.0（较敏感）、3.0（标准常用值）

## 输出结果格式

工具返回 JSON 字符串，包含以下信息：

```json
{
  "file": "data/raw/sample.csv",
  "method": "iqr",
  "threshold": 1.5,
  "total_rows": 1000,
  "columns_analyzed": 5,
  "fields": {
    "age": {
      "mean": 38.5,
      "std": 12.3,
      "min": 18.0,
      "max": 95.0,
      "median": 37.0,
      "total_values": 998,
      "Q1": 28.0,
      "Q3": 48.0,
      "IQR": 20.0,
      "lower_bound": -2.0,
      "upper_bound": 78.0,
      "outlier_count": 12,
      "outlier_ratio": 0.012,
      "method_description": "使用 IQR 方法...",
      "outlier_values_preview": [85.0, 90.0, 95.0],
      "outlier_indices_preview": [10, 25, 100]
    }
  },
  "summary": {
    "total_outliers": 45,
    "total_values_checked": 4500,
    "overall_outlier_ratio": 0.01
  }
}
```

## 使用示例

### 1. 直接调用工具

```python
from generated.tools.outlier_detection_tool import OutlierDetectionTool

tool = OutlierDetectionTool()

# 示例1: 使用 IQR 方法检测所有数值字段
result = tool._run(
    file_path="data/raw/sample_customer_data.csv",
    method="iqr",
    threshold=1.5
)
print(result)

# 示例2: 指定字段，使用 Z-Score 方法
result = tool._run(
    file_path="data/raw/sample_customer_data.csv",
    columns=["age", "income", "spending_score"],
    method="zscore",
    threshold=3.0
)
print(result)

# 示例3: 只检测特定字段，使用默认 IQR 方法
result = tool._run(
    file_path="data/raw/sample_customer_data.csv",
    columns=["age"]
)
print(result)
```

### 2. 在 Agent 中挂载

```python
from crewai import Agent
from generated.tools.outlier_detection_tool import OutlierDetectionTool

# 实例化工具
outlier_tool = OutlierDetectionTool()

# 创建数据质量分析 Agent
data_quality_agent = Agent(
    role="数据质量分析师",
    goal="对数据集进行全面质量检查和异常值分析，确保数据质量",
    backstory=(
        "你是一名经验丰富的数据质量分析师，擅长检测数据中的异常值、缺失值等问题。"
        "你能够使用多种统计方法识别异常数据，为后续分析提供高质量的数据基础。"
    ),
    llm=llm,
    tools=[outlier_tool],
    skills=["./skills/data-mining-analysis"],
    verbose=True,
    allow_delegation=False,
)
```

### 3. 在 Task 中挂载

```python
from crewai import Task

outlier_detection_task = Task(
    description=(
        "请调用 outlier_detection_tool 分析 data/raw/sample_customer_data.csv 中的异常值。\n\n"
        "分析要求：\n"
        "1. 使用 iqr 方法，阈值设为 1.5，检测所有数值字段的异常值\n"
        "2. 重点分析 age、income、spending_score 等关键字段\n"
        "3. 根据工具返回的真实结果生成异常值分析报告\n"
        "4. 对发现的异常值给出处理建议（保留、修正或删除）\n\n"
        "必须基于工具真实返回结果生成结论，禁止编造数据。"
    ),
    expected_output=(
        "一份完整的异常值分析报告，包含：\n"
        "- 检测方法说明\n"
        "- 各字段异常值统计（数量、比例、上下界）\n"
        "- 异常值分布分析\n"
        "- 异常值处理建议\n"
        "- 整体数据质量评估"
    ),
    agent=data_quality_agent,
)
```

## Crew 集成说明

### 方案一：在现有 Crew 中新增 Agent 和 Task

```python
from crewai import Crew, Process, Agent, Task
from generated.tools.outlier_detection_tool import OutlierDetectionTool

# 1. 实例化工具
outlier_tool = OutlierDetectionTool()

# 2. 创建 Agent
data_quality_agent = Agent(
    role="数据质量分析师",
    goal="对数据集进行全面质量检查和异常值分析，确保数据质量",
    backstory="你是一名经验丰富的数据质量分析师...",
    llm=llm,
    tools=[outlier_tool],
    skills=["./skills/data-mining-analysis"],
    verbose=True,
    allow_delegation=False,
)

# 3. 创建 Task
outlier_detection_task = Task(
    description=(
        "请调用 outlier_detection_tool 分析 data/raw/sample_customer_data.csv 中的异常值。\n"
        "使用 iqr 方法，阈值 1.5。必须基于工具真实返回结果。"
    ),
    expected_output="异常值分析报告，包含各字段异常值统计和处理建议。",
    agent=data_quality_agent,
)

# 4. 集成到 Crew（添加到现有任务列表中）
crew = Crew(
    agents=[existing_agent_1, existing_agent_2, data_quality_agent],
    tasks=[existing_task_1, existing_task_2, outlier_detection_task],
    process=Process.sequential,
    verbose=True,
)
```

### 方案二：创建独立的异常值分析 Crew

```python
from crewai import Crew, Process, Agent, Task
from generated.tools.outlier_detection_tool import OutlierDetectionTool

outlier_tool = OutlierDetectionTool()

data_quality_agent = Agent(
    role="数据质量分析师",
    goal="检测并分析数据集中的异常值",
    backstory="你是一名数据质量专家...",
    llm=llm,
    tools=[outlier_tool],
    skills=["./skills/data-mining-analysis"],
    verbose=True,
    allow_delegation=False,
)

task = Task(
    description="请调用 outlier_detection_tool 分析 data/raw/sample_customer_data.csv...",
    expected_output="异常值分析报告",
    agent=data_quality_agent,
)

crew = Crew(
    agents=[data_quality_agent],
    tasks=[task],
    process=Process.sequential,
    verbose=True,
)

# 运行
result = crew.kickoff()
print(result)
```

## 运行说明

### 1. 安装依赖

确保已安装所需依赖：

```bash
pip install crewai pandas numpy pydantic
```

### 2. 运行独立测试

```python
# test_outlier_tool.py
from generated.tools.outlier_detection_tool import OutlierDetectionTool

tool = OutlierDetectionTool()
result = tool._run(
    file_path="data/raw/sample_customer_data.csv",
    method="iqr",
    threshold=1.5
)
print(result)
```

```bash
python test_outlier_tool.py
```

### 3. 在 Crew 项目中运行

按照上方 Crew 集成说明配置好后，运行主 Crew 脚本即可。

## 注意事项

1. **文件路径**：确保 CSV 文件路径正确，工具会检查文件是否存在。
2. **数值类型**：非数值类型字段会被自动跳过，工具会给出提示。
3. **缺失值处理**：检测时会自动忽略 NaN 值，仅对有效值进行检测。
4. **阈值选择**：
   - IQR 方法：`threshold=1.5` 检测中度异常，`threshold=3.0` 检测极度异常
   - Z-Score 方法：`threshold=2.0` 较敏感，`threshold=3.0` 为标准常用值
5. **大数据集**：对于超大文件，建议先进行数据抽样，或只检测关键字段。
6. **预览数据**：结果中包含前 10 个异常值的具体数值和索引，便于追踪定位。
