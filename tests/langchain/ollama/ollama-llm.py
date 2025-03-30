from decouple import config
from openai import OpenAI

client = OpenAI(api_key=config("OLA_API_KEY"), base_url=config("OLA_BASE_URL"))

messages = [
        {"role": "system", "content": "你是个乐于助人的助手"},
        {"role": "user", "content": "介绍下长江"},
    ]
response = client.chat.completions.create(
    model="deepseek-r1:1.5b",
    messages=messages,
    stream=False
)

messages.append(response.choices[0].message)
print(f"响应消息: {messages}")
