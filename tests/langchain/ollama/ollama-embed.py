from openai import OpenAI
from decouple import config

client = OpenAI(
    api_key=config("OLA_API_KEY"),
    base_url=config("OLA_BASE_URL")
)

completion = client.embeddings.create(
    model="nomic-embed-text:v1.5",
    input='The clothes are of good quality and look good, definitely worth the wait. I love them.',
    dimensions=1024,
    encoding_format="float"
)

print(completion.model_dump_json())
