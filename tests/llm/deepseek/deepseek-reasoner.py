from openai import OpenAI
from decouple import config

client = OpenAI(api_key=config("DS_API_KEY"), base_url=config("DS_BASE_URL"))

messages = [
        {"role": "system", "content": "你是个地理专家"},
        {"role": "user", "content": "世界上最深的海洋在哪里？"},
    ]
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages,
    stream=False
)

messages.append(response.choices[0].message)
print(f"响应消息: {messages}")
