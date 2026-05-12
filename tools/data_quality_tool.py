"""
@File: tools/data_quality_tool.py
@Desc: 检查缺失值、重复值、常量字段、高缺失字段和异常数值候选。
"""

import os
import json
from typing import Type
import pandas as pd
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class DataQualityInput(BaseModel):
    file_path: str = Field(..., description="CSV 文件路径")
    missing_threshold: float = Field(0.3, description="高缺失率阈值")


class DataQualityTool(BaseTool):
    name: str = "data_quality_tool"
    description: str = "检查数据质量，包括缺失值、重复行、常量字段、高缺失字段和可能异常的数值字段。"
    args_schema: Type[BaseModel] = DataQualityInput

    def _run(self, file_path: str, missing_threshold: float = 0.3) -> str:
        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"

        df = pd.read_csv(file_path)
        n_rows = len(df)
        missing_count = df.isna().sum()
        missing_rate = (missing_count / n_rows).round(4) if n_rows else missing_count
        high_missing = missing_rate[missing_rate >= missing_threshold].to_dict()
        duplicate_rows = int(df.duplicated().sum())
        constant_columns = [col for col in df.columns if df[col].nunique(dropna=False) <= 1]

        numeric_cols = df.select_dtypes(include="number").columns
        possible_outliers = {}
        for col in numeric_cols:
            series = df[col].dropna()
            if series.empty:
                continue
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            count = int(((series < lower) | (series > upper)).sum())
            if count > 0:
                possible_outliers[col] = {
                    "count": count,
                    "lower_bound": round(float(lower), 4),
                    "upper_bound": round(float(upper), 4),
                }

        result = {
            "file_path": file_path,
            "row_count": n_rows,
            "missing_count": missing_count.to_dict(),
            "missing_rate": missing_rate.to_dict(),
            "high_missing_columns": high_missing,
            "duplicate_rows": duplicate_rows,
            "constant_columns": constant_columns,
            "possible_outliers_iqr": possible_outliers,
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
