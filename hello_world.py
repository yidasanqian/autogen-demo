import os
from autogen import AssistantAgent, UserProxyAgent

llm_config = {
    "config_list": [
  {
    "model": "gpt-35-turbo-16k",
    "api_type": "azure",
    "api_key": os.environ['AZURE_OPENAI_API_KEY'],
    "base_url": os.environ['AZURE_OPENAI_BASE_URL'],
    "api_version": "2024-02-15-preview",
    "max_tokens": 4096
  }
]
}
assistant = AssistantAgent("assistant", llm_config=llm_config)
user_proxy = UserProxyAgent("user_proxy", code_execution_config=False)

# Start the chat
user_proxy.initiate_chat(
    assistant,
    message="给我讲个关于NVDA和特斯拉股价的笑话.",
)