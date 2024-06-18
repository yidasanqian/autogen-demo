import os
from autogen import ConversableAgent, register_function
from typing import Annotated, Literal

llm_config = {
    "config_list": [
  {
    "model": "gpt-4",
    "api_type": "azure",
    "api_key": os.environ['AZURE_OPENAI_API_KEY'],
    "base_url": os.environ['AZURE_OPENAI_BASE_URL'],
    "api_version": os.environ['AZURE_OPENAI_API_VERSION'],
    "max_tokens": 4096,
    "temperature": 0.5,
  }
]
}

Operator = Literal["+", "-", "*", "/"]

def calculator(a: int, b: int, operator: Annotated[Operator, "operator"]) -> int:
    if operator == "+":
        return a + b
    elif operator == "-":
        return a - b
    elif operator == "*":
        return a * b
    elif operator == "/":
        return int(a / b)
    else:
        raise ValueError("Invalid operator")
    
assistant = ConversableAgent(
    name = "Assistant",
    system_message="你是一个有用的ai助手。你可以帮助进行简单的计算。任务完成后返回“TERMINATE”。",
    llm_config=llm_config,
)

user_proxy = ConversableAgent(
    name = "User",
    llm_config=False,
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
)

# 同时向两个代理注册工具
register_function(
    calculator,
    caller=assistant,
    executor=user_proxy,
    name="calculator",
    description="一个简单的计算器",
)

chat_result = user_proxy.initiate_chat(assistant, message="(44232 + 13312 / (232 - 32)) * 5的结果是多少？")
print(chat_result.summary)