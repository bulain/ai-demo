import asyncio

from decouple import config
from llama_index.core import SimpleDirectoryReader
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.indices.managed.dashscope import DashScopeCloudIndex
from llama_index.llms.deepseek import DeepSeek

# Create a RAG tool using LlamaIndex
# wget https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt -O data/paul_graham_essay.txt
documents = SimpleDirectoryReader("data").load_data()
index = DashScopeCloudIndex.from_documents(documents=documents, name="first_index", api_key=config("ALI_API_KEY"),
                                           base_url=config("ALI_BASE_URL"), verbose=True)
query_engine = index.as_query_engine()


def multiply(a: float, b: float) -> float:
    """Useful for multiplying two numbers."""
    return a * b


async def search_documents(query: str) -> str:
    """Useful for answering natural language questions about an personal essay written by Paul Graham."""
    response = await query_engine.aquery(query)
    return str(response)


# Create an enhanced workflow with both tools
agent = FunctionAgent(
    tools=[multiply, search_documents],
    llm=DeepSeek(model="deepseek-chat", api_key=config("DS_API_KEY"), base_url=config("DS_BASE_URL")),
    system_prompt="""You are a helpful assistant that can perform calculations and search through documents to answer questions.""",
)


# Now we can ask questions about the documents or do calculations
async def main():
    response = await agent.run(
        "What did the author do in college? Also, what's 7 * 8?"
    )
    print(response)


# Run the agent
if __name__ == "__main__":
    asyncio.run(main())
