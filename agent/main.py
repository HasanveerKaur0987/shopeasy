import json
from dotenv import load_dotenv
from openai import OpenAI
from datetime import date
from tools import get_order_status, search_products, list_products, request_return

load_dotenv()
client = OpenAI()
MODEL = "gpt-4.1-mini"



INSTRUCTIONS = f"""You are ShopEasy's friendly customer support assistant.
Today's date is {date.today()}.

- Always use the tools to look up orders and products. Never guess details or prices.
- If a tool returns an error, explain it politely to the customer.
- Never decide yourself whether an order can be returned. Always call request_return;
  it checks the return rules. Only tell the customer the result it gives you.
- Before calling request_return, make sure you have the order ID and the reason.
  If either is missing, ask the customer for it.
- Keep answers short and friendly.
- Only help with ShopEasy questions.

Store policies:
- Returns: - When a customer asks to return an order and gives the order ID and reason,
    call request_return right away. Do not call get_order_status first, and do not
    ask them to confirm. request_return checks all the rules.
    - If the order ID or reason is missing, ask for it.
- Shipping: free on orders over $50, otherwise $5. Delivery takes 3-7 business days.
- Cancelled orders cannot be returned."""

# Describe each tool to the AI
tools = [
    {
        "type": "function",
        "name": "get_order_status",
        "description": "Look up an order by its order ID to get status, items, total and delivery date.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID e.g. 1002",
                },
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "search_products",
        "description": "Search products by name or keyword, e.g. 'hoodie' or 'bag'. Use a short keyword. Returns price, stock and description.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "A short keyword, e.g. hoodie"}
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "list_products",
        "description": "List all products the store sells, with price and whether they are in stock",
        "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "request_return",
        "description": "Start a return and refund for a delivered order. Only call this after the customer has given the order ID and a reason.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The order ID, e.g. 1001"},
                "reason": {"type": "string", "description": "Why the customer wants to return it"}
            },
            "required": ["order_id", "reason"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

# Match tool names to our real Python functions
TOOL_FUNCTIONS = {
    "get_order_status": get_order_status,
    "search_products": search_products,
    "list_products": list_products,
    "request_return": request_return,

}

def ask_agent(question):
    messages = [{"role": "user", "content": question}]

    while True:
        response = client.responses.create(
            model=MODEL,
            instructions=INSTRUCTIONS,
            tools=tools,
            input=messages,
        )
        messages+=response.output

        tool_calls = [item for item in response.output if item.type == "function_call"]

        if not tool_calls:
            return response.output_text

        for call in tool_calls:

            args = json.loads(call.arguments)

            print(f"   [tool] {call.name} {args}")
            result = TOOL_FUNCTIONS[call.name](**args)

            messages.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(result),
            })


# Chat in the terminal
print("ShopEasy Support (type 'quit' to stop)\n")
while True:
    question = input("You: ")
    if question.lower() in ("quit", "exit"):
        break
    print("Bot:", ask_agent(question), "\n")
