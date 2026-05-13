"""
@File: utils/llm.py
@Desc: 创建 CrewAI 原生 LLM，适配路线二 OpenAI-compatible 模型。
"""

import os
from dotenv import load_dotenv
from crewai import LLM


def get_llm(
        model_name: str = os.getenv("OPENAI_MODEL_NAME", "deepseek/deepseek-v4-flash")
) -> LLM:
    load_dotenv()

    return LLM(
        model=model_name,
        api_key=os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
    )


def get_volcengine_llm(
    model_name: str = os.getenv("VOLCENGINE_MODEL_NAME")
) -> LLM:
    load_dotenv()

    return LLM(
        model=model_name,
        api_key=os.getenv("VOLCENGINE_API_KEY"),
        base_url=os.getenv("VOLCENGINE_API_BASE"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
    )



# 测试
if __name__ == "__main__":
    print("OPENAI_API_KEY exists =", bool(os.getenv("OPENAI_API_KEY")))
    print("DEEPSEEK_API_KEY exists =", bool(os.getenv("DEEPSEEK_API_KEY")))
    print("OPENAI_BASE_URL =", os.getenv("OPENAI_BASE_URL"))
    print("OPENAI_API_BASE =", os.getenv("OPENAI_API_BASE"))
    print("OPENAI_MODEL_NAME =", os.getenv("OPENAI_MODEL_NAME"))

    llm = get_llm()

    prompt = "你好，生成一个hello world的python代码"
    print(prompt)
    response = llm.call(prompt)
    print(response)

    print("="*60)
    print("VOLCENGINE_API_KEY exists =", bool(os.getenv("VOLCENGINE_API_KEY")))
    print("VOLCENGINE_API_BASE =", os.getenv("VOLCENGINE_API_BASE"))
    print("VOLCENGINE_MODEL_NAME =", os.getenv("VOLCENGINE_MODEL_NAME"))

    llm = get_volcengine_llm()
    response = llm.call(prompt)
    print(response)