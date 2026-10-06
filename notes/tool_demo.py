import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = "gpt-4.1-mini"

def get_weather(city):
    fake_weather = {"Calgary": "5°C and windy", "Toronto": "12°C and rainy"}
    return fake_weather.get(city, "No weather data for that city")

tools = [
    {
    "type": "function",
    "name": "get_weather",
    "description": "Get the current weather for a city.",
    "parameters":{
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name, e.g. Calgary"}
            },
        "required": ["city"],
        "additionalProperties": False,
        },
        "strict": True
    }
]

messages = [{"role": "user", "content": "What's the weather in Calgary?"}]
response = client.responses.create(model=MODEL, tools=tools, input=messages)

messages+= response.output

for item in response.output:
    if item.type == "function_call":
        print(f"AI wants to call: {item.name} with {item.arguments}")

        args = json.loads(item.arguments)
        result = get_weather(**args)           
        print(f"Our function returned: {result}")

        messages.append({
            "type": "function_call_output",
            "call_id": item.call_id,           # links the result to the request
            "output": result,
        })

final = client.responses.create(model=MODEL, tools=tools, input=messages)
print("AI answer:", final.output_text)