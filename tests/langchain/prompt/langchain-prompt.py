from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from decouple import config

# 初始化模型
llm = init_chat_model(model="deepseek-chat", model_provider="deepseek", api_key=config("DS_API_KEY"))

# 结合 LangChain 的 Chain 使用
template = """
你是一个科技记者。根据以下主题写一篇简短的科普文章：
主题: {topic}
文章:
"""
prompt = PromptTemplate.from_template(template)

chain = prompt | llm

response = chain.invoke({"topic":"人工智能在医疗诊断中的应用"})
print(response.content)

# 提示词模板
prompt_template = ChatPromptTemplate([
    ("system", "你是个乐于助人的助手"),
    ("user", "给我讲一个关于{topic}的笑话")
])
messages = prompt_template.invoke({"topic": "加菲猫"})
print(messages)

response = llm.invoke(messages)
print(response.content)
