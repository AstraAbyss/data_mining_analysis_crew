"""
异常值检测工具 - Outlier Detection Tool

该工具用于检测CSV数据中的异常值，支持 IQR 和 Z-Score 两种方法。
输出每个字段的异常值数量、比例和上下界信息。

Author: CrewAI Data Mining Project
"""

import json
import warnings
from typing import Optional, List, Dict, Any

import pandas as pd
import numpy as np
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class OutlierDetectionInput(BaseModel):
    """异常值检测工具的输入参数模型"""
    file_path: str = Field(..., description="CSV 文件路径")
    columns: Optional[List[str]] = Field(
        default=None,
        description="需要检测异常值的字段列表，若为空则自动选择所有数值字段"
    )
    method: str = Field(
        default="iqr",
        description="异常值检测方法，支持 'iqr' (四分位距法) 和 'zscore' (Z分数法)"
    )
    threshold: float = Field(
        default=1.5,
        description="异常值检测阈值。IQR方法默认为1.5，Z-Score方法建议使用2~3"
    )


class OutlierDetectionTool(BaseTool):
    """
    异常值检测工具

    读取CSV文件，对指定字段（或所有数值字段）进行异常值检测，
    返回每个字段的异常值数量、异常值比例、上下界信息。

    支持两种检测方法：
    - iqr: 使用四分位距法，异常定义为 Q1 - threshold*IQR 或 Q3 + threshold*IQR
    - zscore: 使用Z分数法，异常定义为 |Z| > threshold
    """
    name: str = "异常值检测工具"
    description: str = (
        "读取CSV文件并检测数值字段中的异常值。"
        "支持IQR(四分位距)法和Z-Score(Z分数)法。"
        "输入参数包括：file_path(CSV文件路径)、columns(可选字段列表)、"
        "method(检测方法：iqr或zscore)、threshold(阈值，默认1.5)。"
        "返回每个字段的异常值统计信息。"
    )
    args_schema: type = OutlierDetectionInput

    def _detect_outliers_iqr(
        self, series: pd.Series, threshold: float
    ) -> Dict[str, Any]:
        """
        使用 IQR 方法检测异常值

        Args:
            series: 数据序列
            threshold: IQR 倍数阈值

        Returns:
            包含异常值统计信息的字典
        """
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr

        outliers = series[(series < lower_bound) | (series > upper_bound)]
        total = len(series)

        return {
            "field": series.name,
            "total_count": total,
            "outlier_count": len(outliers),
            "outlier_ratio": round(len(outliers) / total * 100, 4) if total > 0 else 0.0,
            "method": "iqr",
            "threshold": threshold,
            "lower_bound": round(float(lower_bound), 6),
            "upper_bound": round(float(upper_bound), 6),
            "q1": round(float(q1), 6),
            "q3": round(float(q3), 6),
            "iqr": round(float(iqr), 6),
            "outlier_indices": outliers.index.tolist() if len(outliers) > 0 else [],
        }

    def _detect_outliers_zscore(
        self, series: pd.Series, threshold: float
    ) -> Dict[str, Any]:
        """
        使用 Z-Score 方法检测异常值

        Args:
            series: 数据序列
            threshold: Z-Score 阈值

        Returns:
            包含异常值统计信息的字典
        """
        mean = series.mean()
        std = series.std()

        if std == 0:
            return {
                "field": series.name,
                "total_count": len(series),
                "outlier_count": 0,
                "outlier_ratio": 0.0,
                "method": "zscore",
                "threshold": threshold,
                "mean": round(float(mean), 6),
                "std": round(float(std), 6),
                "lower_bound": round(float(mean), 6),
                "upper_bound": round(float(mean), 6),
                "warning": "标准差为0，无法检测异常值",
                "outlier_indices": [],
            }

        z_scores = np.abs((series - mean) / std)
        outliers = series[z_scores > threshold]
        total = len(series)

        return {
            "field": series.name,
            "total_count": total,
            "outlier_count": len(outliers),
            "outlier_ratio": round(len(outliers) / total * 100, 4) if total > 0 else 0.0,
            "method": "zscore",
            "threshold": threshold,
            "mean": round(float(mean), 6),
            "std": round(float(std), 6),
            "lower_bound": round(float(mean - threshold * std), 6),
            "upper_bound": round(float(mean + threshold * std), 6),
            "outlier_indices": outliers.index.tolist() if len(outliers) > 0 else [],
        }

    def _run(
        self,
        file_path: str,
        columns: Optional[List[str]] = None,
        method: str = "iqr",
        threshold: float = 1.5,
    ) -> str:
        """
        执行异常值检测

        Args:
            file_path: CSV 文件路径
            columns: 需要检测的字段列表，为None时自动选择所有数值字段
            method: 检测方法 (iqr/zscore)
            threshold: 阈值

        Returns:
            JSON 格式的异常值检测结果字符串
        """
        # 参数校验
        if method not in ["iqr", "zscore"]:
            raise ValueError(
                f"不支持的检测方法: '{method}'。仅支持 'iqr' 和 'zscore'。"
            )

        if threshold <= 0:
            raise ValueError(f"阈值必须大于0，当前值: {threshold}")

        # 读取 CSV 文件
        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            return json.dumps({
                "status": "error",
                "message": f"文件未找到: {file_path}",
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"读取文件失败: {str(e)}",
            }, ensure_ascii=False, indent=2)

        if df.empty:
            return json.dumps({
                "status": "warning",
                "message": "CSV文件为空，无数据可检测",
                "file_path": file_path,
            }, ensure_ascii=False, indent=2)

        # 确定要检测的字段
        if columns is not None and len(columns) > 0:
            # 验证指定的字段是否存在
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                return json.dumps({
                    "status": "error",
                    "message": f"指定的字段不存在: {missing_cols}",
                    "available_columns": df.columns.tolist(),
                }, ensure_ascii=False, indent=2)

            numeric_cols = [
                col for col in columns
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col])
            ]
            non_numeric_cols = [
                col for col in columns if col not in numeric_cols
            ]
            if non_numeric_cols:
                warnings.warn(
                    f"以下字段不是数值类型，已自动跳过: {non_numeric_cols}"
                )
        else:
            # 自动选择所有数值字段
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_cols:
            return json.dumps({
                "status": "warning",
                "message": "未找到数值字段，无法进行异常值检测",
                "file_path": file_path,
            }, ensure_ascii=False, indent=2)

        # 执行检测
        results = []
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) < 4:
                # 数据点太少无法进行有效检测
                results.append({
                    "field": col,
                    "total_count": len(df[col]),
                    "valid_count": len(series),
                    "outlier_count": 0,
                    "outlier_ratio": 0.0,
                    "method": method,
                    "threshold": threshold,
                    "warning": f"有效数据点不足 ({len(series)} < 4)，无法进行异常值检测",
                })
                continue

            if method == "iqr":
                result = self._detect_outliers_iqr(series, threshold)
            else:
                result = self._detect_outliers_zscore(series, threshold)

            results.append(result)

        # 汇总信息
        total_outliers = sum(r["outlier_count"] for r in results)
        total_fields = len(results)

        output = {
            "status": "success",
            "file_path": file_path,
            "detection_summary": {
                "total_fields_analyzed": total_fields,
                "total_outliers_found": total_outliers,
                "method": method,
                "threshold": threshold,
                "fields_with_outliers": sum(
                    1 for r in results if r["outlier_count"] > 0
                ),
                "fields_clean": sum(
                    1 for r in results if r["outlier_count"] == 0
                ),
            },
            "field_results": results,
        }

        return json.dumps(output, ensure_ascii=False, indent=2)
