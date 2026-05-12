"""
@File: tools/correlation_analysis_tool.py
@Desc: 数值字段相关性分析工具。
"""

import os
import json
from typing import Type
import pandas as pd
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class CorrelationAnalysisInput(BaseModel):
    """
    相关性分析输入参数模型类
    用于定义相关性分析所需的输入参数及其验证规则
    """
    file_path: str = Field(..., description="CSV 文件路径")  # 必填参数，指定要分析的CSV文件路径
    method: str = Field("pearson", description="相关性方法：pearson、spearman、kendall")  # 可选参数，默认使用pearson方法
    threshold: float = Field(0.5, description="强相关阈值，取绝对值比较")  # 可选参数，默认阈值为0.5，用于判断相关性强度


class CorrelationAnalysisTool(BaseTool):
    name: str = "correlation_analysis_tool"
    description: str = "计算数值字段相关性，返回强相关字段对和相关矩阵摘要。"
    args_schema: Type[BaseModel] = CorrelationAnalysisInput

    def _run(self, file_path: str, method: str = "pearson", threshold: float = 0.5) -> str:
        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"

        df = pd.read_csv(file_path)
        num_df = df.select_dtypes(include="number")
        if num_df.shape[1] < 2:
            return "数值字段少于 2 个，无法计算相关性。"

        corr = num_df.corr(method=method).round(4)
        pairs = []
        cols = corr.columns.tolist()
        for i, c1 in enumerate(cols):
            for c2 in cols[i + 1:]:
                value = corr.loc[c1, c2]
                if pd.notna(value) and abs(value) >= threshold:
                    pairs.append({
                        "field_1": c1,
                        "field_2": c2,
                        "correlation": float(value),
                    })

        result = {
            "file_path": file_path,
            "method": method,
            "threshold": threshold,
            "strong_correlation_pairs": pairs,
            "correlation_matrix": corr.to_dict(),
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
