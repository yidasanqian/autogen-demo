import os
from autogen import ConversableAgent

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

# 创建孙悟空agent
sun_monkey = ConversableAgent("孙悟空",
                              llm_config=llm_config,
                                system_message="你是孙悟空，是西游记里的齐天大圣",
                                human_input_mode="NEVER", # 创建完全自主的代理
                               )
# 创建唐僧agent
tang_monk = ConversableAgent("唐僧",
                              llm_config=llm_config,
                                system_message="你是唐僧，是西游记里的唐僧",
                                human_input_mode="NEVER",
                                is_termination_msg=lambda msg: "妖怪已被打败" in msg["content"],
                               )
#result = sun_monkey.initiate_chat(tang_monk, message="师傅，我们又遇到妖怪了", max_turns=3)

# 当human_input_mode模式为 NEVER 时，上述终止条件将结束对话
result = tang_monk.initiate_chat(sun_monkey, message="悟空，我们又遇到妖怪了，快去打败他，如果被打败了，就说妖怪已被打败")