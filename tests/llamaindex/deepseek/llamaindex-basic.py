import asyncio

from decouple import config
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.deepseek import DeepSeek


# Define a simple calculator tool
def multiply(a: float, b: float) -> float:
    """Useful for multiplying two numbers."""
    return a * b


# Create an agent workflow with our calculator tool
agent = FunctionAgent(
    tools=[multiply],
    llm=DeepSeek(model="deepseek-chat", api_key=config("DS_API_KEY"), base_url=config("DS_BASE_URL")),
    system_prompt="You are a helpful assistant that can multiply two numbers.",
)


async def main():
    # Run the agent
    response = await agent.run("What is 1234 * 4567?")
    print(str(response))


# Run the agent
if __name__ == "__main__":
    asyncio.run(main())