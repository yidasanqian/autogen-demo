import os
import tempfile
from autogen import ConversableAgent
from autogen.coding import LocalCommandLineCodeExecutor

temp_dir = tempfile.TemporaryDirectory()
work_dir_path = temp_dir.name
print(temp_dir)
code_executor = LocalCommandLineCodeExecutor(timeout=10, work_dir=work_dir_path)
code_executor_agent = ConversableAgent(
    name="code_executor_agent",
    code_execution_config={"executor": code_executor},
    human_input_mode="ALWAYS" # 手动验证正在执行的代码的安全性
)

message_with_code_block = """This is a message with code block.
The code block is below:
```python
import numpy as np
import matplotlib.pyplot as plt
x = np.random.randint(0, 100, 100)
y = np.random.randint(0, 100, 100)
plt.scatter(x, y)
plt.savefig('scatter.png')
print('Scatter plot saved to scatter.png')
```
This is the end of the message.
"""
messages = [{
    "role": "user",
    "content": message_with_code_block
}]
# Generate a reply for the given code.
reply = code_executor_agent.generate_reply(messages=messages)
print(reply)


print(os.listdir(temp_dir.name))