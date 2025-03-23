from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate
from decouple import config

# 初始化模型
llm = init_chat_model(model="deepseek-chat", model_provider="deepseek", api_key=config("DS_API_KEY"))

# 提示模板 1 ：这个提示将接受产品并返回最佳名称来描述该公司
prompt1 = PromptTemplate.from_template("描述制造{product}的一个公司的最好的名称是什么?")

# 提示模板 2 ：接受公司名称，然后输出该公司的长为20个单词的描述
prompt2 = PromptTemplate.from_template("写一个50字的描述对于下面这个公司：{company_name}")

# 创建模型链
chain1 = prompt1 | llm
chain2 = prompt2 | llm

# 实际上会调用两次API
chain = chain1 | chain2

response = chain.invoke({"product":"保温杯"})
print(response.content)