import os
import pathlib
import time
import pandas as pd
import tkinter as tk
from PIL import ImageTk, Image
from autogen import AssistantAgent, UserProxyAgent
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
    "stream": True
  }
]
}

user_id = "123"
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
assistant = AssistantAgent(
    name="assistant",
    system_message=DEFAULT_SYSTEM_MESSAGE,
    llm_config=llm_config
)

user_agent = UserProxyAgent(
    name="user_agent",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"executor": code_executor}
)


def analysis_data_and_plot(filename: list, few_shot, task: str) -> None:
    start_time = time.time()
    message = f"""
    ## Excel Files
    {filename}
    ### Data Frame Examples
    {few_shot}
    ## Task
    {task}    
    """
    print(f"Task:【{task}】的描述：\n{message}")
    try:
      chat_res = user_agent.initiate_chat(
        recipient=assistant,
        message=message,
        summary_method="last_msg"
      )
    except RuntimeError as e:
      print(f"Error: {e}")
      return
    print(f"Task:【{task}】\n摘要：\n", chat_res.summary)
    # print(f"Task:【{task}】的历史会话：\n{chat_res.chat_history}")
    print(f"成本：\n{chat_res.cost}")
    # messages = user_agent.chat_messages[assistant]
    # response = {
    #         "messages": messages[1:],
    #         "usage": chat_res.cost,
    #         "duration": time.time() - start_time,
    #     }
    # print(f"Task:【{task}】的响应：\n{response}")

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

def read_excel_with_determined_header(file_path, index_col=0, max_header_rows=3):
    header_format = determine_header_format(file_path, max_header_rows)
    df = pd.read_excel(file_path, header=header_format, index_col=index_col)
    return df
    
def show_image(img_path):
  if img_path is None and len(img_path) > 0:
    # 创建一个新的tkinter窗口
    root = tk.Tk()
    # 打开图像并转换为tkinter可用的格式
    img = ImageTk.PhotoImage(Image.open(img_path))
    # 创建一个标签并将图像添加到标签
    panel = tk.Label(root, image=img)
    panel.pack(side="bottom", fill="both", expand="yes")
    # 显示窗口
    root.mainloop()
  
if __name__ == "__main__":
  filename = ["类目报表周表-品类细项.xlsx"]
  few_shot = """
  ```csv
  日期,	平台,	一级类目,	二级类目,	三级类目,	四级类目,	销售额,	销量
  20240513-20240519,	阿里全部,	保健食品/膳食营养补充食品,	海外膳食营养补充食品,	蛋白粉/氨基酸/胶原蛋白,	氨基酸,	268046,	1792
  20240513-20240519,	阿里全部,	保健食品/膳食营养补充食品,	海外膳食营养补充食品,	蛋白粉/氨基酸/胶原蛋白,	混合蛋白,	7685,	15
  ```
  """
  # task1 = "分析文件数据，绘制平台对应的销售额、销量的图表，保存数据到 platform_sales.xlsx 文件中，并且保存绘图到 platform_sales.png，确保正常保存了对应文件。"
  # analysis_data_and_plot(filename, few_shot, task1)
  
  # task2 = "分析文件数据，统计淘宝平台5月的销售额和销量，保存数据到 platform_sales(5月).xlsx 文件中，并且保存绘图到 platform_sales(5月).png，确保正常保存了对应文件。"
  # analysis_data_and_plot(filename, few_shot, task2)
  
  # task3 = "分析文件数据，统计淘宝平台氨基酸的销售额和销量。"
  # analysis_data_and_plot(filename, few_shot, task3)
  
  # ====
  filename = ["行业分析-食品_保健-宝贝.xlsx"]
  few_shot = """
  ```csv
column names：时间,	排名,	宝贝名称,	宝贝链接,	宝贝图片链接,	上架月份,	商品类别,	参考价格,	成交均价,	销量,	销售额,	份额占比（销量),	上轮排名,	品牌,	掌柜,	掌柜链接,	地域,
row1: 2024-03-01,	1,	蒙牛特仑苏纯牛奶250ml*16盒家庭分享【最早生产日期12月】,	http://item.taobao.com/item.htm?id=534465655558,	https://img.alicdn.com/imgextra/i4/6000000003039/O1CN01AtJ4nK1YJua8G1fS9_!!6000000003039-0-sm.jpg,	2016-07,	咖啡/麦片/冲饮 » 液态奶/常温乳制品 » 纯牛奶,	86.9,	42.6,	352615,	15014405,	0.4%,	2,	特仑苏,	天猫超市,	http://shop67597230.taobao.com,	上海
row2: 2024-03-01,	2,	蒙牛纯牛奶全脂灭菌乳250ml*24盒/箱【最早生产日期11月】,	http://item.taobao.com/item.htm?id=597610168994,	https://img.alicdn.com/imgextra/i3/6000000001494/O1CN01uf0vfD1MuIerIduOF_!!6000000001494-0-sm.jpg,	2019-08,	咖啡/麦片/冲饮 » 液态奶/常温乳制品 » 纯牛奶,	74.4,	40.8,	198444,	8095749,	0.23%, 4,	蒙牛,	天猫超市,	http://shop67597230.taobao.com,	湖北武汉
  ```
  """

  # task4 = "哪个宝贝的销量最高？"
  # analysis_data_and_plot(filename, few_shot, task4)
  
  # task5 = "成交均价最高的宝贝是什么？"
  # analysis_data_and_plot(filename, few_shot, task5)
  
  # task6 = "份额占比（销量）最高的宝贝是什么？"
  # analysis_data_and_plot(filename, few_shot, task6)
  
  # task7 = "品牌最多的商品类别是什么？"
  # analysis_data_and_plot(filename, few_shot, task7)
  
  # task8 = "商品上架时间最早的宝贝是什么？"
  # analysis_data_and_plot(filename, few_shot, task8)
  
  # task9 = "销量前五的宝贝及其销售额是多少？"
  # analysis_data_and_plot(filename, few_shot, task9)
  
  # task10 = "排名前五的宝贝所属的品牌分别是什么？"
  # analysis_data_and_plot(filename, few_shot, task10)
  
  # === 多级表头 ===
  filename = ["行业分析-食品_保健-品牌.xlsx"]
  file_path = data_dir.joinpath(filename[0])
  df = read_excel_with_determined_header(file_path)
  filename1 = filename[0]
  few_shot = f"""
  {filename1}: 
  Columns in the dataframe:
  {df.columns}
  Values in the dataframe:
  {df.values[:2]}
  """
  # task11 = "农夫山泉5月份销售额是多少？"
  # analysis_data_and_plot(filename, few_shot, task11)
  # task12 = "农夫山泉3月份销售额是多少？"
  # analysis_data_and_plot(filename, few_shot, task12)
  # task13 = "农夫山泉5月份销售额比3月份多多少？"
  # analysis_data_and_plot(filename, few_shot, task13)
  
  # task14 = "农夫山泉3、4、5月份销售额是多少？5月份销售额比3月份多多少？"
  # analysis_data_and_plot(filename, few_shot, task14)
  
  # === 多表关联 ===
  # 行业分析-食品_保健-店铺.xlsx和行业分析-食品_保健-宝贝.xlsx通过掌柜名关联
  filename1 = "行业分析-食品_保健-店铺.xlsx"
  filename2 = "行业分析-食品_保健-宝贝.xlsx"
  filename.append(filename1)
  filename.append(filename2)
  
  few_shot = ""
  for item in filename:    
    file_path = data_dir.joinpath(item)
    df = read_excel_with_determined_header(file_path)
    few_shot1 = f"""
    {item}: 
    Columns in the dataframe:
    {df.columns}
    Values in the dataframe:
    {df.values[:2]}
    """
    few_shot += few_shot1

  # task15 = "销量排名前5的宝贝名称、掌柜名、店铺名、店铺类别是什么？"
  # analysis_data_and_plot(filename, few_shot, task15)
  
  # task16 = "按月份、商品类别分组统计销售额和销量，输出4月的商品类别、销售额和销量。"
  # analysis_data_and_plot(filename, few_shot, task16)
  
  task17 = "上海地区成交均价排名前10的宝贝名称、销量、销售额是什么？"
  analysis_data_and_plot(filename, few_shot, task17)
  


  