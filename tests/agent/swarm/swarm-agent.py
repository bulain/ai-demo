import os
from openai import OpenAI
from swarm import Swarm, Agent
from decouple import config

# 实例化客户端
client = OpenAI(api_key=config("DS_API_KEY"), base_url=config("DS_BASE_URL"))

swarm_client = Swarm(client)

def transfer_to_agent_b():
    return agent_b

agent_a = Agent(
    name="Agent A",
    model="deepseek-chat",
    instructions="你是一个乐于助人的智能体。",
    functions=[transfer_to_agent_b],
)

agent_b = Agent(
    name="Agent B",
    model="deepseek-chat",
    instructions="只用文言文回答。",
)

response = swarm_client.run(
    agent=agent_a,
    messages=[{"role": "user", "content": "我想与智能体B对话，用一句话形容女子的漂亮。"}],
)

print(response.messages[-1])