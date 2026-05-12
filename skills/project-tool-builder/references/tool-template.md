# Tool Template

```python
import json
import os
from typing import Type, Optional

import pandas as pd
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class XxxInput(BaseModel):
    file_path: str = Field(..., description="CSV 文件路径")


class XxxTool(BaseTool):
    name: str = "xxx_tool"
    description: str = "工具功能描述"
    args_schema: Type[BaseModel] = XxxInput

    def _run(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"

        df = pd.read_csv(file_path)

        result = {}

        return json.dumps(result, ensure_ascii=False, indent=2)
```
