import dspy
from decouple import config

lm = dspy.LM('openai/deepseek-chat', api_key=config("DS_API_KEY"), base_url=config("DS_BASE_URL"))
dspy.configure(lm=lm)

math = dspy.ChainOfThought("question -> answer: float")
response = math(question="Two dice are tossed. What is the probability that the sum equals two?")

print(response)
