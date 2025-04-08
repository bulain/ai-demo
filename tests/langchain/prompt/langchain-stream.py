from decouple import config
from langchain.chat_models import init_chat_model
import asyncio

# 初始化模型
llm = init_chat_model(model="deepseek-chat", model_provider="deepseek", api_key=config("DS_API_KEY"))

for chunk in llm.stream("写一首形容春天的七言绝句的诗。"):
    print(chunk.content, end="", flush=True)

async def main() -> None:
    async for chk in llm.astream("写一首形容夏天的七言绝句的诗。"):
        print(chk.content, end="", flush=True)

asyncio.run(main())