from openai import OpenAI
from decouple import config

client = OpenAI(api_key=config("DS_API_KEY"), base_url=config("DS_BASE_URL"))

messages = [
        {"role": "system", "content": "你是个乐于助人的助手"},
        {"role": "user", "content": "你好"},
    ]
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    stream=False
)

messages.append(response.choices[0].message)
print(f"响应消息: {messages}")
