from pathlib import Path
from autogen import UserProxyAgent
from autogen.coding import DockerCommandLineCodeExecutor

work_dir = Path("coding")
work_dir.mkdir(exist_ok=True)

with DockerCommandLineCodeExecutor(work_dir=work_dir) as code_executor:
    user_proxy = UserProxyAgent(
        name="user_proxy",
        code_execution_config={"executor": code_executor},
    )