"""
@File: tools/data_profile_tool.py
@Desc: 生成字段画像和基础统计信息。
"""

import os
import json
from typing import Type
import pandas as pd
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class DataProfileInput(BaseModel):
    file_path: str = Field(..., description="CSV 文件路径")
    top_n: int = Field(5, description="类别字段返回前多少个高频值")


class DataProfileTool(BaseTool):
    name: str = "data_profile_tool"
    description: str = "生成数据字段画像，包括类型、非空数量、唯一值数量、数值统计和类别高频值。"
    args_schema: Type[BaseModel] = DataProfileInput

    def _run(self, file_path: str, top_n: int = 5) -> str:
        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"

        df = pd.read_csv(file_path)
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        object_cols = df.select_dtypes(exclude="number").columns.tolist()

        numeric_summary = df[numeric_cols].describe().round(4).to_dict() if numeric_cols else {}
        categorical_summary = {}
        for col in object_cols:
            categorical_summary[col] = df[col].value_counts(dropna=False).head(top_n).to_dict()

        result = {
            "file_path": file_path,
            "shape": list(df.shape),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "non_null_count": df.notna().sum().to_dict(),
            "unique_count": df.nunique(dropna=False).to_dict(),
            "numeric_columns": numeric_cols,
            "categorical_columns": object_cols,
            "numeric_summary": numeric_summary,
            "categorical_top_values": categorical_summary,
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
