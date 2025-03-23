from openai import OpenAI
from decouple import config

client = OpenAI(api_key=config("DS_API_KEY"), base_url=config("DS_BASE_URL"))

prompt = """
你是一位大模型提示词生成专家，请根据用户的需求编写一个智能助手的提示词，来指导大模型进行内容生成，要求：
1. 以 Markdown 格式输出
2. 贴合用户需求，描述智能助手的定位、能力、知识储备
3. 提示词应清晰、精确、易于理解，在保持质量的同时，尽可能简洁
4. 只输出提示词，不要输出多余解释
"""

messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "请帮我生成一个“nginx 助手”的提示词"},
    ]
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    stream=False
)

messages.append(response.choices[0].message)
print(f"响应消息: {messages}")
