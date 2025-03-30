import asyncio

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.embeddings import FakeEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore


async def app():
    file_path = "./pdf-demo.pdf"
    loader = PyPDFLoader(file_path)
    pages = []
    async for page in loader.alazy_load():
        pages.append(page)

    for page in pages:
        print(f"{page.metadata}\n")
        print(page.page_content)

    vector_store = InMemoryVectorStore.from_documents(pages, FakeEmbeddings(size=1024))
    docs = vector_store.similarity_search("What is LangChain?", k=2)
    for doc in docs:
        print("----------------------------------------------------")
        print(f'Page {doc.metadata["page"]}: {doc.page_content[:300]}\n')

# Run the agent and stream the messages to the console.
async def main() -> None:
    await app()

# NOTE: if running this inside a Python script you'll need to use asyncio.run(main()).
asyncio.run(main())
