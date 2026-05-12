"""
@File: tools/csv_reader_tool.py
@Desc: 读取 CSV 文件基础信息。
"""

import os
import json
from typing import Type
import pandas as pd
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class CSVReaderInput(BaseModel):
    file_path: str = Field(..., description="CSV 文件路径")
    preview_rows: int = Field(5, description="预览前多少行")


class CSVReaderTool(BaseTool):
    name: str = "csv_reader_tool"
    description: str = "读取 CSV 文件，返回行列数、字段名和样例数据。"
    args_schema: Type[BaseModel] = CSVReaderInput

    def _run(self, file_path: str, preview_rows: int = 5) -> str:
        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"

        df = pd.read_csv(file_path)
        result = {
            "file_path": file_path,
            "shape": list(df.shape),
            "columns": list(df.columns),
            "preview": df.head(preview_rows).to_dict(orient="records"),
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
