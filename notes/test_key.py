from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

response = client.responses.create(
    model = "gpt-4.1-mini",
    input = "Say hello to ShopEasy customers in one line."
)
print(response.output_text)
