import asyncio

from decouple import config
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.workflow import Context
from llama_index.llms.deepseek import DeepSeek

# Create an agent workflow
agent = FunctionAgent(
    llm=DeepSeek(model="deepseek-chat", api_key=config("DS_API_KEY"), base_url=config("DS_BASE_URL")),
    system_prompt="You are a helpful assistant.",
)

agentWf = AgentWorkflow(agents=[agent])
ctx = Context(agentWf)

async def main():
    # run agent with context
    response = await agent.run("My name is Jack", ctx=ctx)
    response = await agent.run("What is my name?", ctx=ctx)
    print(str(response))


# Run the agent
if __name__ == "__main__":
    asyncio.run(main())