import json
import os
from typing import Type

import pandas as pd
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class DataQualityInput(BaseModel):
    file_path: str = Field(..., description="CSV 文件路径")


class DataQualityTool(BaseTool):

    """
    数据质量检查工具类，用于分析CSV文件的质量问题。
    继承自BaseTool，提供数据质量检查的功能。
    """
    name: str = "data_quality_tool"  # 工具名称
    description: str = "检查 CSV 数据质量，包括缺失值、重复值和常量字段。"  # 工具描述
    args_schema: Type[BaseModel] = DataQualityInput  # 参数模式定义

    def _run(self, file_path: str) -> str:

        """
        执行数据质量检查的核心方法

        参数:
            file_path (str): 待检查的CSV文件路径

        返回:
            str: JSON格式的检查结果，包含数据形状、缺失值、重复行和常量列信息
        """
        if not os.path.exists(file_path):  # 检查文件是否存在
            return f"文件不存在: {file_path}"

        df = pd.read_csv(file_path)  # 读取CSV文件

        # 构建包含各类质量检查结果的字典
        result = {
            "shape": df.shape,  # 数据集的维度(行数,列数)
            "missing_values": df.isna().sum().to_dict(),  # 每列的缺失值统计
            "duplicate_rows": int(df.duplicated().sum()),  # 重复行的数量
            "constant_columns": [  # 常量列(所有值相同的列)的列表
                col for col in df.columns if df[col].nunique(dropna=False) <= 1
            ],
        }

        return json.dumps(result, ensure_ascii=False, indent=2)  # 返回格式化的JSON结果
