import asyncio

from langchain_community.document_loaders import UnstructuredExcelLoader


async def app():
    file_path = "./xlsx-demo.xlsx"
    loader = UnstructuredExcelLoader(
        file_path=file_path
    )
    docs = []
    for doc in loader.lazy_load():
        docs.append(doc)
    print("----------------------------------------------------")
    print(docs)

# Run the agent and stream the messages to the console.
async def main() -> None:
    await app()


# NOTE: if running this inside a Python script you'll need to use asyncio.run(main()).
asyncio.run(main())
