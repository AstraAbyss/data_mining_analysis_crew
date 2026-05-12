"""
@File: tools/report_writer_tool.py
@Desc: 将最终 Markdown 报告写入本地文件。
"""

import os
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class ReportWriterInput(BaseModel):
    output_path: str = Field(..., description="报告输出路径，例如 outputs/final_report.md")
    content: str = Field(..., description="Markdown 报告正文内容")


class ReportWriterTool(BaseTool):
    name: str = "report_writer_tool"
    description: str = "将 Markdown 报告内容写入指定本地文件。"
    args_schema: Type[BaseModel] = ReportWriterInput

    def _run(self, output_path: str, content: str) -> str:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"报告写入成功: {output_path}"
