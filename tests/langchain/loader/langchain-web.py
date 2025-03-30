import asyncio

import bs4
from langchain_community.document_loaders import WebBaseLoader


async def app():
    page_url = "https://python.langchain.com/docs/how_to/chatbots_memory/"

    loader = WebBaseLoader(web_paths=[page_url])
    docs = []
    async for doc in loader.alazy_load():
        docs.append(doc)

    assert len(docs) == 1
    doc = docs[0]

    print(f"{doc.metadata}\n")
    print(doc.page_content[:500].strip())

    loader = WebBaseLoader(
        web_paths=[page_url],
        bs_kwargs={
            "parse_only": bs4.SoupStrainer(class_="theme-doc-markdown markdown"),
        },
        bs_get_text_kwargs={"separator": " | ", "strip": True},
    )

    docs = []
    async for doc in loader.alazy_load():
        docs.append(doc)

    assert len(docs) == 1
    doc = docs[0]

    print(f"{doc.metadata}\n")
    print(doc.page_content[:500])


# Run the agent and stream the messages to the console.
async def main() -> None:
    await app()


# NOTE: if running this inside a Python script you'll need to use asyncio.run(main()).
asyncio.run(main())
