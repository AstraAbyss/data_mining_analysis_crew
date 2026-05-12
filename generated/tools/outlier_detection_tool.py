"""
异常值检测工具 (Outlier Detection Tool)

功能描述：
    读取 CSV 文件，对指定字段（或所有数值字段）进行异常值检测。
    支持 IQR 和 Z-Score 两种检测方法，返回每个字段的异常值数量、比例及上下界信息。

依赖：
    - pandas
    - numpy
    - scipy (用于 zscore 方法)
    - crewai.tools.BaseTool

用法示例：
    from generated.tools.outlier_detection_tool import OutlierDetectionTool

    tool = OutlierDetectionTool()
    result = tool.run(
        file_path="data.csv",
        columns=["age", "salary"],
        method="iqr",
        threshold=1.5
    )
"""

import json
import warnings
from typing import Any, Optional, Union

import numpy as np
import pandas as pd
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class OutlierDetectionInput(BaseModel):
    """OutlierDetectionTool 的输入参数模型"""

    file_path: str = Field(
        ..., description="CSV 文件路径，例如 './data/dataset.csv'"
    )
    columns: Optional[list] = Field(
        None,
        description="需要检测异常值的字段列表。如果为 None 或空列表，则自动选择所有数值字段。",
    )
    method: str = Field(
        default="iqr",
        description="异常值检测方法。可选值: 'iqr' (四分位距法) 或 'zscore' (Z-Score 法)",
    )
    threshold: float = Field(
        default=1.5,
        description="异常值判定阈值。对于 IQR 方法，默认 1.5；对于 Z-Score 方法，建议 2~3。",
    )


class OutlierDetectionTool(BaseTool):
    """
    异常值检测工具

    读取 CSV 文件并对指定字段（或自动选择数值字段）执行异常值检测。
    支持 IQR（四分位距法）和 Z-Score（标准分数法）两种主流检测方法。

    Attributes:
        name: 工具名称
        description: 工具用途描述
        args_schema: 输入参数 Schema
    """

    name: str = "异常值检测工具"
    description: str = (
        "读取 CSV 文件并对指定字段进行异常值检测。"
        "支持 IQR（四分位距法，threshold=1.5 为中度异常，3 为极度异常）"
        "和 Z-Score（标准分数法，threshold=2 或 3 常用）。"
        "返回 JSON 格式的检测结果，包含每个字段的异常值数量、比例及上下界信息。"
    )
    args_schema: type[BaseModel] = OutlierDetectionInput

    def _run(
        self,
        file_path: str,
        columns: Optional[list] = None,
        method: str = "iqr",
        threshold: float = 1.5,
    ) -> str:
        """
        执行异常值检测的核心方法。

        Args:
            file_path: CSV 文件路径
            columns: 待检测字段列表（可选，为空则自动选择数值字段）
            method: 检测方法，'iqr' 或 'zscore'
            threshold: 异常判定阈值

        Returns:
            JSON 字符串，包含检测结果
        """
        # 1. 参数校验
        method = method.lower().strip()
        if method not in ("iqr", "zscore"):
            raise ValueError(
                f"不支持的检测方法 '{method}'。请使用 'iqr' 或 'zscore'。"
            )

        if threshold <= 0:
            raise ValueError(f"阈值必须为正数，当前值为 {threshold}。")

        # 2. 读取 CSV 文件
        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到文件: {file_path}")
        except Exception as e:
            raise RuntimeError(f"读取 CSV 文件失败: {e}")

        if df.empty:
            return json.dumps(
                {
                    "status": "warning",
                    "message": "CSV 文件内容为空，无数据可检测。",
                    "results": {},
                },
                ensure_ascii=False,
                indent=2,
            )

        # 3. 确定待检测字段
        if columns and len(columns) > 0:
            # 验证用户指定的字段是否存在
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                warnings.warn(
                    f"以下字段在数据集中不存在，将被忽略: {missing_cols}"
                )
            valid_columns = [
                col
                for col in columns
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col])
            ]
            if not valid_columns:
                return json.dumps(
                    {
                        "status": "warning",
                        "message": "指定的字段中无有效的数值字段可供检测。",
                        "results": {},
                    },
                    ensure_ascii=False,
                    indent=2,
                )
        else:
            # 自动选择所有数值字段
            valid_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            if not valid_columns:
                return json.dumps(
                    {
                        "status": "warning",
                        "message": "数据集中不存在数值字段，无法执行异常值检测。",
                        "results": {},
                    },
                    ensure_ascii=False,
                    indent=2,
                )

        # 4. 执行异常值检测
        results = {}
        for col in valid_columns:
            series = df[col].dropna()
            if len(series) < 4:
                results[col] = {
                    "error": f"字段 '{col}' 有效数据不足（{len(series)} 条），无法进行异常值检测（至少需要 4 条）。",
                }
                continue

            if method == "iqr":
                result = self._detect_iqr(series, col, threshold)
            else:
                result = self._detect_zscore(series, col, threshold)

            results[col] = result

        # 5. 汇总并返回
        output = {
            "status": "success",
            "method": method,
            "threshold": threshold,
            "total_records": len(df),
            "detected_fields": valid_columns,
            "results": results,
        }

        return json.dumps(output, ensure_ascii=False, indent=2)

    def _detect_iqr(
        self, series: pd.Series, col_name: str, threshold: float
    ) -> dict[str, Any]:
        """
        使用 IQR（四分位距）法检测异常值。

        IQR = Q3 - Q1
        异常值判定：值 < Q1 - threshold * IQR 或值 > Q3 + threshold * IQR

        Args:
            series: 数值序列
            col_name: 字段名
            threshold: IQR 倍数阈值

        Returns:
            检测结果字典
        """
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr

        outliers = series[(series < lower_bound) | (series > upper_bound)]
        outlier_count = len(outliers)
        total_count = len(series)
        outlier_ratio = round(outlier_count / total_count, 4) if total_count > 0 else 0.0

        return {
            "field": col_name,
            "method": "iqr",
            "threshold": threshold,
            "total_count": total_count,
            "outlier_count": outlier_count,
            "outlier_ratio": outlier_ratio,
            "outlier_ratio_percent": f"{outlier_ratio * 100:.2f}%",
            "q1": round(float(q1), 4),
            "q3": round(float(q3), 4),
            "iqr": round(float(iqr), 4),
            "lower_bound": round(float(lower_bound), 4),
            "upper_bound": round(float(upper_bound), 4),
            "outlier_values": (
                outliers.head(10).tolist()
                if outlier_count > 0
                else []
            ),
            "outlier_preview_count": min(outlier_count, 10),
        }

    def _detect_zscore(
        self, series: pd.Series, col_name: str, threshold: float
    ) -> dict[str, Any]:
        """
        使用 Z-Score（标准分数）法检测异常值。

        Z-Score = (x - mean) / std
        异常值判定：|Z-Score| > threshold

        Args:
            series: 数值序列
            col_name: 字段名
            threshold: Z-Score 阈值

        Returns:
            检测结果字典
        """
        mean = series.mean()
        std = series.std(ddof=0)

        if std == 0:
            return {
                "field": col_name,
                "method": "zscore",
                "threshold": threshold,
                "total_count": len(series),
                "outlier_count": 0,
                "outlier_ratio": 0.0,
                "outlier_ratio_percent": "0.00%",
                "mean": round(float(mean), 4),
                "std": round(float(std), 4),
                "lower_bound": round(float(mean), 4),
                "upper_bound": round(float(mean), 4),
                "warning": "标准差为 0，所有值相同，无异常值。",
                "outlier_values": [],
                "outlier_preview_count": 0,
            }

        z_scores = np.abs((series - mean) / std)
        outliers = series[z_scores > threshold]
        outlier_count = len(outliers)
        total_count = len(series)
        outlier_ratio = round(outlier_count / total_count, 4) if total_count > 0 else 0.0

        return {
            "field": col_name,
            "method": "zscore",
            "threshold": threshold,
            "total_count": total_count,
            "outlier_count": outlier_count,
            "outlier_ratio": outlier_ratio,
            "outlier_ratio_percent": f"{outlier_ratio * 100:.2f}%",
            "mean": round(float(mean), 4),
            "std": round(float(std), 4),
            "lower_bound": round(float(mean - threshold * std), 4),
            "upper_bound": round(float(mean + threshold * std), 4),
            "outlier_values": (
                outliers.head(10).tolist()
                if outlier_count > 0
                else []
            ),
            "outlier_preview_count": min(outlier_count, 10),
        }
