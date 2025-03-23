from langchain.chat_models import init_chat_model
from decouple import config

# 初始化模型
llm = init_chat_model(model="deepseek-chat", model_provider="deepseek", api_key=config("DS_API_KEY"))

# 调用大模型
response = llm.invoke("你好")
print(response.content)

