import os
import tempfile
import datetime
import tkinter as tk
from PIL import ImageTk, Image
from autogen import ConversableAgent
from autogen.coding import DockerCommandLineCodeExecutor

temp_dir = tempfile.TemporaryDirectory(delete=False)
print(temp_dir.name)
code_executor = DockerCommandLineCodeExecutor(
    image="autogen_base_img",
    timeout=60, 
    work_dir=temp_dir.name # 指向本地文件系统目录，docker容器会挂载这个目录，执行器写入代码文件并输出到其中。
    )

code_executor_agent = ConversableAgent(
    name="code_executor_agent",
    code_execution_config={"executor": code_executor},
    human_input_mode="ALWAYS" # 手动验证正在执行的代码的安全性
)

# When the code executor is no longer used, stop it to release the resources.
# executor.stop()

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

# The code writer agent's system message is to instruct the LLM on how to use
# the code executor in the code executor agent.
code_writer_system_message = """你是一个有用的人工智能助手.
利用你的编码和语言技能解决任务。
在下列情况下，建议用户执行 python 代码（在 python 代码块中）或 shell 脚本（在 sh 代码块中）。
1. 当你需要收集信息时，使用代码输出你需要的信息，例如，浏览或搜索网页、下载/读取文件、打印网页或文件的内容，
获取当前日期/时间，检查操作系统。在打印了足够的信息并准备好根据你的语言技能解决任务后，你就可以自己解决任务了。
pip安装包时，必须指定python包的索引源[https://pypi.tuna.tsinghua.edu.cn/simple]。
2. 当你需要使用代码执行某些任务时，请使用代码执行任务并输出结果。巧妙地完成任务。
如果需要，请逐步解决任务。如果没有提供计划，请先解释你的计划。
要清楚哪一步使用了代码，哪一步使用了你的语言技能。使用代码时，必须在代码块中注明脚本类型。
用户不能提供任何其它反馈或执行你建议的代码之外的任何其他操作。用户不能修改你的代码。因此，不要建议用户修改不完整的代码。
如果用户不打算执行代码块，就不要使用它。如果你希望用户在执行代码之前将其保存在文件中，将#filename:<filename>作为第一行放入代码块中。
不要在一个回复中包含多个代码块。不要要求用户复制和粘贴结果。在相关情况下，请使用 "print" 功能输出结果。
检查用户返回的执行结果。如果结果表明存在错误，请修复错误并再次输出代码。建议使用完整代码，而不是部分代码或更改的代码。
如果错误无法修复，或者代码成功执行后任务仍未解决，分析问题，重新审视自己的假设，收集所需的其它信息，并想出不同的方法进行尝试。
找到答案后，请仔细核实答案。如有可能，请在回答中提供可验证的证据。
一切完成后，最后回复 "TERMINATE"。
"""
code_writer_agent = ConversableAgent(
    "code_writer_agent",
    system_message=code_writer_system_message,
    llm_config=llm_config,
    code_execution_config=False,
)

#message = "请帮我写一个python程序，计算第14个斐波那契数"
today = datetime.datetime.now().strftime("%Y-%m-%d")
message = f"今天是{today}，用python代码绘制出年初至今宁德时代和比亚迪的股价走势图，并保存为“stock_price.png”文件。"
result = code_executor_agent.initiate_chat(code_writer_agent, message=message)
print(result)

# 创建一个新的tkinter窗口
root = tk.Tk()
# 打开图像并转换为tkinter可用的格式
img_path = os.path.join(temp_dir.name, "stock_gains.png")
img = ImageTk.PhotoImage(Image.open(img_path))
# 创建一个标签并将图像添加到标签
panel = tk.Label(root, image=img)
panel.pack(side="bottom", fill="both", expand="yes")
# 显示窗口
root.mainloop()

temp_dir.cleanup()  # Clean up the temporary directory.
code_executor.stop()  # Stop the docker command line code executor.