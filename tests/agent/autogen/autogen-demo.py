import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from decouple import config


async def main() -> None:
    model_client = OpenAIChatCompletionClient(model="deepseek-chat",
                                              api_key=config("DS_API_KEY"),
                                              base_url=config("DS_BASE_URL"),
                                              model_info={
                                                  "vision": True,
                                                  "function_calling": True,
                                                  "json_output": True,
                                                  "family": "o1",
                                              })
    agent = AssistantAgent("assistant", model_client=model_client)
    print(await agent.run(task="Say 'Hello World!'"))
    await model_client.close()


asyncio.run(main())
