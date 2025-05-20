from agents import Agent, Runner, set_tracing_disabled, OpenAIChatCompletionsModel
from agents.mcp import MCPServerSse, MCPServerSseParams
from decouple import config
from openai import AsyncOpenAI

external_client = AsyncOpenAI(api_key=config("DS_API_KEY"), base_url=config("DS_BASE_URL"))
set_tracing_disabled(True)

async def mcp_run():
    # Initialize MCP server
    mcp_sserver = MCPServerSse(
        MCPServerSseParams(url="https://mcp.amap.com/sse?key="+config("AMAP_API_KEY")),
        cache_tools_list=True
    )

    async with mcp_sserver:
        # Create agent with mcp server
        agent = Agent(
            name="代理工具",
            instructions="使用可用工具完成任务",
            model=OpenAIChatCompletionsModel(model="deepseek-chat", openai_client=external_client),
            mcp_servers=[mcp_sserver]
        )

        # Get all tools
        tools = await agent.get_all_tools()
        print(tools)

        # Run the agent
        messages = [
            {"role": "system", "content": "你是个天气助手,只能调用MCP工具进行回答"},
            {"role": "user", "content": "上海的天气"},
        ]

        result = await Runner.run(agent, input=messages)
        print(result.final_output)


if __name__ == "__main__":
    import asyncio

    asyncio.run(mcp_run())
