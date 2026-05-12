# Data Mining Analysis CrewAI Demo

本项目是一个数据挖掘与分析类 CrewAI Demo，重点展示：

- CrewAI Agent 分工
- Skill 方法论注入
- Tool 可控调用
- Task 分阶段执行
- Crew 顺序编排
- Markdown 数据分析报告生成

## 项目结构

```text
data_mining_analysis_crew/
├── main.py
├── crew.py
├── agents.py
├── tasks.py
├── tools/
├── skills/
├── data/
├── outputs/
├── configs/
├── prompts/
└── utils/
```

## Skill + Tool 设计

Skill：`skills/data-mining-analysis/SKILL.md`

它负责注入数据挖掘方法论，包括数据理解、质量检查、EDA、相关性分析、分组分析和报告结构。

Tools：

- `csv_reader_tool`：读取 CSV 基础信息
- `data_profile_tool`：生成字段画像
- `data_quality_tool`：检查数据质量
- `eda_summary_tool`：执行探索性数据分析
- `correlation_analysis_tool`：执行相关性分析
- `group_analysis_tool`：执行分组统计
- `report_writer_tool`：写入 Markdown 报告

## 运行准备

安装依赖：

```bash
pip install crewai python-dotenv pandas pydantic
```

根据你的模型配置修改 `.env`。

## 运行

```bash
python main.py
```

成功后会生成：

```text
outputs/final_report.md
```

## 执行流程

```text
数据读取与理解
↓
数据质量检查
↓
探索性数据分析
↓
相关性与分组分析
↓
最终报告生成
```

## 注意事项

1. 如果使用 `deepseek/...` 模型前缀，部分 CrewAI 版本需要设置 `DEEPSEEK_API_KEY`。
2. 如果使用内网 OpenAI-compatible 模型，请设置 `OPENAI_BASE_URL=http://your-host/v1`。
3. 所有分析必须基于工具返回结果，Skill 中已经明确禁止编造统计结论。
