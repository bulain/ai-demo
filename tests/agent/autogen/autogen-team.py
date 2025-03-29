import asyncio
from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from autogen_core.models import ModelInfo
from decouple import config


async def main() -> None:
    model_info = ModelInfo(vision=False, function_calling=True, json_output=True, family="r1")
    model_client = OpenAIChatCompletionClient(model="deepseek-chat",
                                              api_key=config("DS_API_KEY"),
                                              base_url=config("DS_BASE_URL"),
                                              model_info=model_info)
    # The web surfer will open a Chromium browser window to perform web browsing tasks.
    web_surfer = MultimodalWebSurfer("web_surfer", model_client, headless=True, animate_actions=True)
    # The user proxy agent is used to get user input after each step of the web surfer.
    # NOTE: you can skip input by pressing Enter.
    user_proxy = UserProxyAgent("user_proxy")
    # The termination condition is set to end the conversation when the user types 'exit'.
    termination = TextMentionTermination("exit", sources=["user_proxy"])
    # Web surfer and user proxy take turns in a round-robin fashion.
    team = RoundRobinGroupChat([web_surfer, user_proxy], termination_condition=termination)
    try:
        # Start the team and wait for it to terminate.
        await Console(team.run_stream(task="查询AutoGen资料，并写一段简短描述。"))
    finally:
        await web_surfer.close()
        await model_client.close()


asyncio.run(main())
