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
    "max_tokens": 4096,
    "temperature": 0.5,
  }
]
}

# 创建猜数字游戏的agent，该agent会自动给出1-100之间的随机数，然后根据玩家的猜测给出提示
generate_number_agent = ConversableAgent("生成数字agent",
                                         system_message="您正在玩 `猜数字` 游戏。"
                                         "你的脑海中有有 53 这个数字,而我要试着猜出来."
                                        "如果我猜得太高，就说'太高'，如果我猜得太低，就说'太低'。",
                                        llm_config=llm_config,
                                        human_input_mode="NEVER",
                                        is_termination_msg=lambda msg: "53" in msg["content"]
)

# create a human agent
human_agent = ConversableAgent("human agent",                            
                               human_input_mode="ALWAYS",
                               llm_config=False,      
)            

result = human_agent.initiate_chat(generate_number_agent, message="10")