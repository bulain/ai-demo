from agents import Agent, Runner, set_default_openai_client, set_tracing_disabled
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams
from decouple import config
from openai import AsyncOpenAI

external_client = AsyncOpenAI(api_key=config("DS_API_KEY"), base_url=config("DS_BASE_URL"))
set_default_openai_client(external_client)
set_tracing_disabled(True)

async def run_agent_with_mcp_servers():
    # Initialize remote SSE MCP server (if needed)
    remote_server = MCPServerStreamableHttp(
        MCPServerStreamableHttpParams(url="http://127.0.0.1:8000/mcp"),
        cache_tools_list=True
    )

    async with remote_server:
        # Create agent with both servers
        agent = Agent(
            name="MultiToolAgent",
            instructions="Use the available tools to accomplish tasks.",
            model="deepseek-chat",
            mcp_servers=[remote_server]
        )

        # Run the agent
        result = await Runner.run(agent, input="上海的天气怎么样")
        print(result.final_output)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_agent_with_mcp_servers())
