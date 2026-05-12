"""
@File: tools/eda_summary_tool.py
@Desc: 基础 EDA 摘要工具。
"""

import os
import json
from typing import Type
import pandas as pd
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class EDASummaryInput(BaseModel):
    file_path: str = Field(..., description="CSV 文件路径")
    max_unique_values: int = Field(10, description="类别字段最多返回多少个频次值")


class EDASummaryTool(BaseTool):
    name: str = "eda_summary_tool"
    description: str = "执行探索性数据分析，返回数值字段统计、类别字段频次和字段分布摘要。"
    args_schema: Type[BaseModel] = EDASummaryInput

    def _run(self, file_path: str, max_unique_values: int = 10) -> str:
        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"

        df = pd.read_csv(file_path)
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

        numeric_distribution = {}
        for col in numeric_cols:
            s = df[col].dropna()
            if s.empty:
                continue
            numeric_distribution[col] = {
                "mean": round(float(s.mean()), 4),
                "median": round(float(s.median()), 4),
                "std": round(float(s.std()), 4) if len(s) > 1 else 0,
                "min": round(float(s.min()), 4),
                "max": round(float(s.max()), 4),
                "skew": round(float(s.skew()), 4) if len(s) > 2 else None,
            }

        categorical_distribution = {}
        for col in categorical_cols:
            categorical_distribution[col] = df[col].value_counts(dropna=False).head(max_unique_values).to_dict()

        result = {
            "file_path": file_path,
            "numeric_distribution": numeric_distribution,
            "categorical_distribution": categorical_distribution,
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
