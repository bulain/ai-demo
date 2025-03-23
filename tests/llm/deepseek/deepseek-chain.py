from openai import OpenAI
from decouple import config

client = OpenAI(api_key=config("DS_API_KEY"), base_url=config("DS_BASE_URL"))

# Round 1
messages = [
    {"role": "system", "content": "你是个地理专家"},
    {"role": "user", "content": "世界上最高的山是什么？"}
]
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    stream=False
)

messages.append(response.choices[0].message)
print(f"第1轮消息: {messages}")

# Round 2
messages.append({"role": "user", "content": "第二高的呢？"})
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    stream=False
)

messages.append(response.choices[0].message)
print(f"第2轮消息: {messages}")