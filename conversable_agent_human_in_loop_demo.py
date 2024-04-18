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

generate_number_agent = ConversableAgent("生成数字agent",
                                          system_message="您正在玩 `猜数字` 游戏。"
                                      "首次游戏时，你脑海中有53这个数字，我要试着猜出来。"
                                       "如果我猜得太高，就说'太高'，如果我猜得太低，就说'太低'。",
                                       llm_config=llm_config,
                                       max_consecutive_auto_reply=1, # 在要求人工输入之前连续自动回复的最多次数
                                        is_termination_msg=lambda msg: "53" in msg["content"],
                                        human_input_mode="TERMINATE"
)

guess_number_agent = ConversableAgent("猜数字agent",
                                      system_message="我脑子里有一个数字，你可以试着猜出来。"
                                       "如果我说'太高'，你应该猜一个更低的数字，如果我说'太低'，你应该猜一个更高的数字。",
                                       llm_config=llm_config,                                     
                                        human_input_mode="NEVER",
                                      )
result = generate_number_agent.initiate_chat(guess_number_agent, message="我有一个在1~100之间的数字，你猜猜看。")