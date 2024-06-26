import os
import pathlib
import pandas as pd
from autogen import filter_config, AssistantAgent, UserProxyAgent
from autogen.coding import DockerCommandLineCodeExecutor

config_list = [
  {
    "model": "gpt-4o",
    "api_type": "azure",
    "api_key": os.environ['AZURE_OPENAI_API_KEY'],
    "base_url": os.environ['AZURE_OPENAI_BASE_URL'],
    "api_version": os.environ['AZURE_OPENAI_API_VERSION'],
    "max_tokens": 4096
  },
  {
    "model": "gpt-35-turbo-16k",
    "api_type": "azure",
    "api_key": os.environ['AZURE_OPENAI_API_KEY'],
    "base_url": os.environ['AZURE_OPENAI_BASE_URL'],
    "api_version": os.environ['AZURE_OPENAI_API_VERSION'],
    "max_tokens": 4096,
    "stream": True
  }
]


user_id = "321"
# 创建Path=/data/coding/目录
data_dir = pathlib.Path("/data/coding").joinpath(user_id)
code_executor = DockerCommandLineCodeExecutor(
    image="autogen_base_img",
    timeout=60, 
    work_dir=data_dir # 指向本地文件系统目录，docker容器会挂载这个目录，执行器写入代码文件并输出到其中。
    )

DEFAULT_SYSTEM_MESSAGE = """You are a Python expert.
Solve tasks using your coding and language skills.
In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute.
    1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.
    2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly.           
Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.
When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible. 
Reply "TERMINATE" in the end when all plan is done. 
The final results were answered in Chinese.
## 生成的代码和脚本须参考以下要求：
  - 系统环境已安装python3.12、NotoSansCJK字体路径:['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc']
  - 当在python代码中用到绘制图表时，手动指定NotoSansCJK字体路径；解决负号显示问题；确保布局完整，使得子图适合于图形区域。 
  - 当需要分析多张Excel/csv文件时，需根据任务判断多张表的关联关系，合理分析数据。
  - Ensure the shell script has only Unix line endings and doesn't have any hidden characters.
  - Ensure the Python script separately without embedding it in the shell script.   
    """

filter_dict = {"model": ["gpt-4o"]}
llm_config = {
    "config_list": filter_config(config_list, filter_dict)
}
assistant_agent = AssistantAgent(
    name="ai_assistant_agent",
    system_message=DEFAULT_SYSTEM_MESSAGE,
    llm_config=llm_config,
)

code_interpreter_agent = UserProxyAgent(
    name="code_interpreter_agent",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"executor": code_executor}
)


filter_dict = {"model": ["gpt-35-turbo-16k"]}
llm_config = {
    "config_list": filter_config(config_list, filter_dict)
}
user_agent = UserProxyAgent(
    name="user_agent",
    human_input_mode="TERMINATE",
    llm_config=llm_config,  
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),  
    code_execution_config=False
)

nested_chat_queue = [
  {"recipient": assistant_agent, "summary_method": "last_msg"},
  {"recipient": user_agent, "summary_method": "last_msg"},
]

code_interpreter_agent.register_nested_chats(
  nested_chat_queue,
  trigger=lambda sender: sender not in [assistant_agent, user_agent],
)

def read_excel_with_determined_header(file_path, index_col=0, max_header_rows=3):
    header_format = determine_header_format(file_path, max_header_rows)
    df = pd.read_excel(file_path, header=header_format, index_col=index_col)
    return df
   
def determine_header_format(file_path, max_header_rows=3):
    for i in range(1, max_header_rows + 1):
        try:
            data = pd.read_excel(file_path, header=list(range(i)), nrows=max_header_rows)
            # 检查列名是否为多级索引
            if isinstance(data.columns, pd.MultiIndex):
                # 检查多级索引的每一层是否包含重复的列名
                unique_levels = [len(set(data.columns.get_level_values(level))) for level in range(data.columns.nlevels)]
                total_unique = len(set(data.columns.get_level_values(0)))  # 第一层的唯一列名数量
                if all(unique == total_unique for unique in unique_levels):
                    continue  # 如果所有层的列名完全相同，则继续尝试下一个表头行数
                return list(range(i))
        except Exception as e:
            print(f"Error reading with header {list(range(i))}: {e}")
            continue
    return [0]  # 如果没有找到多级表头，返回单级表头格式

def analysis_data_and_plot(filename: list, few_shot, task: str) -> None:
    content = f"""
    ## Excel/CSV Files
    {filename}
    ### Data Frame Examples
    {few_shot}
    ## Task
    {task}    
    """
    print(f"Task:【{task}】的描述：\n{content}")
    user_message = [
      {
        "role": "user",
        "content": content
      }
    ]
    try:
      response = code_interpreter_agent.generate_reply(
        messages=user_message
      )
    except RuntimeError as e:
      print(f"Error: {e}")
      return
    #print(f"Task:【{task}】\n摘要：\n", chat_res.summary)
    # print(f"Task:【{task}】的历史会话：\n{chat_res.chat_history}")
    #print(f"成本：\n{chat_res.cost}")
    # messages = user_agent.chat_messages[assistant]
    # response = {
    #         "messages": messages[1:],
    #         "usage": chat_res.cost,
    #         "duration": time.time() - start_time,
    #     }
    print(f"Task:【{task}】的响应：\n{response}")
   
if __name__ == "__main__":
  filename = ["行业分析-食品_保健-宝贝.xlsx"]
  file_path = data_dir.joinpath(filename[0])
  try:
    df = read_excel_with_determined_header(file_path)
  except FileNotFoundError as e:
    print(f"Error: {e}")
    exit(1)
  
  filename1 = filename[0]
  few_shot = f"""
  {filename1}: 
  Columns in the dataframe:
  {df.columns}
  Values in the dataframe:
  {df.values[:2]}
  """

  task = "哪个宝贝的销量最高？"
  analysis_data_and_plot(filename, few_shot, task)