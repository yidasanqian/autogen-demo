import os
from autogen import ConversableAgent

llm_config = {
    "config_list": [
  {
    "model": "gpt-4",
    "api_type": "azure",
    "api_key": os.environ['AZURE_OPENAI_API_KEY'],
    "base_url": os.environ['AZURE_OPENAI_BASE_URL'],
    "api_version": "2024-02-15-preview",
    "max_tokens": 4096
  }
]
}
agent = ConversableAgent("chatbot",
                          llm_config=llm_config,
                         code_execution_config=False,
                         function_map=None,
                         human_input_mode="NEVER",
                         )

messages =[{"role": "user", "content": "给我讲个笑话."}]
reply = agent.generate_reply(messages=messages)
print(reply)