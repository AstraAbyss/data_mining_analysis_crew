"""
@File: tools/group_analysis_tool.py
@Desc: 分组统计分析工具。
"""

import os
import json
from typing import Type
import pandas as pd
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class GroupAnalysisInput(BaseModel):
    file_path: str = Field(..., description="CSV 文件路径")
    group_by_column: str = Field(..., description="分组字段")
    target_column: str = Field(..., description="目标统计字段")
    agg_method: str = Field("mean", description="聚合方法：mean、sum、count、min、max、median")


class GroupAnalysisTool(BaseTool):
    name: str = "group_analysis_tool"
    description: str = "按指定字段分组，对目标字段执行聚合统计，辅助发现群体差异。"
    args_schema: Type[BaseModel] = GroupAnalysisInput

    def _run(self, file_path: str, group_by_column: str, target_column: str, agg_method: str = "mean") -> str:
        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"

        df = pd.read_csv(file_path)
        if group_by_column not in df.columns:
            return f"分组字段不存在: {group_by_column}"
        if target_column not in df.columns:
            return f"目标字段不存在: {target_column}"
        if agg_method not in ["mean", "sum", "count", "min", "max", "median"]:
            return f"不支持的聚合方法: {agg_method}"

        grouped = getattr(df.groupby(group_by_column)[target_column], agg_method)().reset_index()
        result = {
            "file_path": file_path,
            "group_by_column": group_by_column,
            "target_column": target_column,
            "agg_method": agg_method,
            "result": grouped.to_dict(orient="records"),
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
