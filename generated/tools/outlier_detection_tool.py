import json
import os
from typing import Optional, Type, List

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class OutlierDetectionInput(BaseModel):
    """异常值检测工具的输入参数模型"""
    file_path: str = Field(..., description="CSV 文件路径")
    columns: Optional[List[str]] = Field(
        default=None,
        description="需要检测异常值的字段列表。如果为空，则自动选择所有数值字段。"
    )
    method: str = Field(
        default="iqr",
        description="异常值检测方法，支持 iqr（四分位距法）和 zscore（Z 分数法）。"
    )
    threshold: float = Field(
        default=1.5,
        description="异常值判定阈值。"
        "对于 iqr 方法，表示 IQR 的倍数（默认 1.5）；"
        "对于 zscore 方法，表示 Z 分数的绝对值上限（默认 1.5，建议通常设为 2 或 3）。"
    )


class OutlierDetectionTool(BaseTool):
    """
    异常值检测工具类，用于分析 CSV 文件中数值字段的异常值。
    支持 IQR（四分位距法）和 Z-Score（Z 分数法）两种检测方法。
    继承自 BaseTool，提供异常值检测与分析的功能。
    """
    name: str = "outlier_detection_tool"
    description: str = (
        "检测 CSV 文件中数值字段的异常值。"
        "支持 iqr（四分位距法）和 zscore（Z 分数法）两种方法。"
        "输出每个字段的异常值数量、异常值比例、上下界等信息。"
    )
    args_schema: Type[BaseModel] = OutlierDetectionInput

    def _run(
        self,
        file_path: str,
        columns: Optional[List[str]] = None,
        method: str = "iqr",
        threshold: float = 1.5
    ) -> str:
        """
        执行异常值检测的核心方法

        参数:
            file_path (str): 待检测的 CSV 文件路径
            columns (Optional[List[str]]): 需要检测的字段列表，None 时自动选择所有数值字段
            method (str): 检测方法，可选 "iqr" 或 "zscore"
            threshold (float): 异常值判定阈值

        返回:
            str: JSON 格式的检测结果，包含异常值数量、比例、上下界等信息
        """
        # 1. 检查文件是否存在
        if not os.path.exists(file_path):
            return json.dumps(
                {"error": f"文件不存在: {file_path}"},
                ensure_ascii=False,
                indent=2
            )

        # 2. 校验检测方法
        valid_methods = ["iqr", "zscore"]
        if method not in valid_methods:
            return json.dumps(
                {"error": f"不支持的检测方法: {method}，支持的方法: {', '.join(valid_methods)}"},
                ensure_ascii=False,
                indent=2
            )

        # 3. 读取 CSV 文件
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            return json.dumps(
                {"error": f"读取 CSV 文件失败: {str(e)}"},
                ensure_ascii=False,
                indent=2
            )

        # 4. 确定要检测的字段
        if columns and len(columns) > 0:
            # 检查指定的字段是否在数据集中
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                return json.dumps(
                    {"error": f"数据集中不存在以下字段: {missing_cols}"},
                    ensure_ascii=False,
                    indent=2
                )
            # 过滤出数值字段
            numeric_cols = [col for col in columns if pd.api.types.is_numeric_dtype(df[col])]
            if not numeric_cols:
                return json.dumps(
                    {"error": "指定的字段中不包含数值类型字段，无法进行异常值检测。"},
                    ensure_ascii=False,
                    indent=2
                )
            # 如果有非数值字段被排除，给出提示
            non_numeric = [col for col in columns if col not in numeric_cols]
            if non_numeric:
                print(f"警告: 以下字段不是数值类型，已跳过: {non_numeric}")
        else:
            # 自动选择所有数值字段
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if not numeric_cols:
                return json.dumps(
                    {"error": "数据集中没有数值类型字段，无法进行异常值检测。"},
                    ensure_ascii=False,
                    indent=2
                )

        # 5. 执行异常值检测
        result = {
            "file": file_path,
            "method": method,
            "threshold": threshold,
            "total_rows": len(df),
            "columns_analyzed": len(numeric_cols),
            "fields": {}
        }

        for col in numeric_cols:
            col_data = df[col].dropna()  # 去除缺失值后再检测
            if len(col_data) == 0:
                result["fields"][col] = {
                    "error": "该字段无有效数据（全部为空）"
                }
                continue

            field_result = self._detect_outliers(col_data, method, threshold)
            result["fields"][col] = field_result

        # 6. 汇总统计
        total_outliers = sum(
            info.get("outlier_count", 0)
            for info in result["fields"].values()
            if "outlier_count" in info
        )
        total_values = sum(
            info.get("total_values", 0)
            for info in result["fields"].values()
            if "total_values" in info
        )
        result["summary"] = {
            "total_outliers": total_outliers,
            "total_values_checked": total_values,
            "overall_outlier_ratio": round(total_outliers / total_values, 4) if total_values > 0 else 0
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    def _detect_outliers(
        self,
        data: pd.Series,
        method: str,
        threshold: float
    ) -> dict:
        """
        对单个字段执行异常值检测

        参数:
            data (pd.Series): 待检测的数据序列
            method (str): 检测方法
            threshold (float): 阈值

        返回:
            dict: 该字段的异常值检测结果
        """
        total = len(data)
        stats = {
            "mean": round(float(data.mean()), 4),
            "std": round(float(data.std()), 4),
            "min": round(float(data.min()), 4),
            "max": round(float(data.max()), 4),
            "median": round(float(data.median()), 4),
            "total_values": total
        }

        if method == "iqr":
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR

            outliers = data[(data < lower_bound) | (data > upper_bound)]
            outlier_count = len(outliers)

            stats.update({
                "Q1": round(float(Q1), 4),
                "Q3": round(float(Q3), 4),
                "IQR": round(float(IQR), 4),
                "lower_bound": round(float(lower_bound), 4),
                "upper_bound": round(float(upper_bound), 4),
                "outlier_count": outlier_count,
                "outlier_ratio": round(outlier_count / total, 4),
                "method_description": (
                    f"使用 IQR 方法，阈值={threshold}，"
                    f"下界 = Q1 - {threshold} * IQR = {round(float(lower_bound), 4)}，"
                    f"上界 = Q3 + {threshold} * IQR = {round(float(upper_bound), 4})"
                )
            })

            if outlier_count > 0:
                stats["outlier_values_preview"] = [
                    round(float(v), 4) for v in outliers.head(10).tolist()
                ]
                stats["outlier_indices_preview"] = outliers.index[:10].tolist()

        elif method == "zscore":
            mean_val = data.mean()
            std_val = data.std()

            if std_val == 0:
                stats.update({
                    "outlier_count": 0,
                    "outlier_ratio": 0.0,
                    "lower_bound": round(float(mean_val), 4),
                    "upper_bound": round(float(mean_val), 4),
                    "method_description": "该字段标准差为 0（常量字段），无异常值。"
                })
                return stats

            z_scores = (data - mean_val) / std_val
            outliers = data[z_scores.abs() > threshold]
            outlier_count = len(outliers)

            stats.update({
                "lower_bound": round(float(mean_val - threshold * std_val), 4),
                "upper_bound": round(float(mean_val + threshold * std_val), 4),
                "outlier_count": outlier_count,
                "outlier_ratio": round(outlier_count / total, 4),
                "method_description": (
                    f"使用 Z-Score 方法，阈值={threshold}，"
                    f"|Z| > {threshold} 判定为异常值，"
                    f"下界 = mean - {threshold} * std = {round(float(mean_val - threshold * std_val), 4)}，"
                    f"上界 = mean + {threshold} * std = {round(float(mean_val + threshold * std_val), 4})"
                )
            })

            if outlier_count > 0:
                stats["outlier_values_preview"] = [
                    round(float(v), 4) for v in outliers.head(10).tolist()
                ]
                stats["outlier_indices_preview"] = outliers.index[:10].tolist()

        return stats
