from openai import OpenAI
from decouple import config

client = OpenAI(
    api_key=config("ALI_API_KEY"),
    base_url=config("ALI_BASE_URL") + "/compatible-mode/v1"
)

completion = client.embeddings.create(
    model="text-embedding-v3",
    input='The clothes are of good quality and look good, definitely worth the wait. I love them.',
    dimensions=1024,
    encoding_format="float"
)

print(completion.model_dump_json())
