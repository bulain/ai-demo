import asyncio

from langchain_unstructured import UnstructuredLoader


async def app():
    """
     https://api.unstructuredapp.io/general/v0/general
    """
    file_path = "./pdf-demo.pdf"
    loader = UnstructuredLoader(
        file_path=file_path,
        strategy="hi_res",
        partition_via_api=True,
        coordinates=True,
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
