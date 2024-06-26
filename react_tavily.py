import os
import pathlib
from typing import Annotated

from tavily import TavilyClient

from autogen import AssistantAgent, UserProxyAgent, register_function
from autogen.cache import Cache
from autogen.coding import DockerCommandLineCodeExecutor

llm_config = {
    "config_list": [
  {
    "model": "gpt-4o",
    "api_type": "azure",
    "api_key": os.environ['AZURE_OPENAI_API_KEY'],
    "base_url": os.environ['AZURE_OPENAI_BASE_URL'],
    "api_version": os.environ['AZURE_OPENAI_API_VERSION'],
    "max_tokens": 4096,
    "cache_seed": None,
  }
]
}

tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def search_tool(query: Annotated[str, "The search query"]) -> Annotated[str, "The search results"]:
    return tavily.get_search_context(query=query, search_depth="advanced")

# 通用的 ReAct 提示
# NOTE: this ReAct prompt is adapted from Langchain's ReAct agent: https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/agents/react/agent.py#L79
ReAct_prompt = """
Answer the following questions as best you can. You have access to tools provided.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take
Action Input: the input to the action
Observation: the result of the action
... (this process can repeat multiple times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!
Question: {input}
"""

# Define the ReAct prompt message. Assuming a "question" field is present in the context
def react_prompt_message(sender, recipient, context):
    return ReAct_prompt.format(input=context["question"])

user_id = "react"
data_dir = pathlib.Path("/data/coding").joinpath(user_id)
code_executor = DockerCommandLineCodeExecutor(
    image="autogen_base_img",
    timeout=60, 
    work_dir=data_dir
    )

user_proxy = UserProxyAgent(
    name="User",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    code_execution_config={"executor": code_executor},
)

assistant = AssistantAgent(
    name="Assistant",
    system_message="Only use the tools you have been provided with. Reply TERMINATE when the task is done. 使用请求的语言作为响应的语言",
    llm_config=llm_config
)

# Register the search tool.
register_function(
    search_tool,
    caller=assistant,
    executor=user_proxy,
    name="search_tool",
    description="Search the web for the given query",
)

# Cache LLM responses. To get different responses, change the cache_seed value.
with Cache.disk(cache_seed=43) as cache:
    user_proxy.initiate_chat(
        assistant,
        message=react_prompt_message,
        question="中国市场的山楂类产品在2023年的市场体量有多少?",
        cache=cache,
    )