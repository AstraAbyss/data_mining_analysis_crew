# Agent Template

```python
def create_xxx_agent(llm, tools):
    return Agent(
        role="...",
        goal="...",
        backstory="...",
        llm=llm,
        tools=tools,
        skills=["./skills/data-mining-analysis"],
        verbose=True,
        allow_delegation=False,
    )
```
