# Task Template

```python
def create_xxx_task(agent, file_path: str):
    return Task(
        description=(
            f"请调用 xxx_tool 分析 {file_path}。"
            "必须基于工具真实返回结果生成结论。"
        ),
        expected_output="...",
        agent=agent,
    )
```
