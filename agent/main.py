import json
from dotenv import load_dotenv
from openai import OpenAI
from datetime import date
from tools import get_order_status, search_products, list_products, request_return

load_dotenv()
client = OpenAI()
MODEL = "gpt-4.1-mini"
MAX_STEPS = 5 


INSTRUCTIONS = f"""You are ShopEasy's friendly customer support assistant.
Today's date is {date.today()}.

Rules:
- Always use the tools to look up orders and products. Never guess details or prices.
- Never say an order or product was not found unless a tool returned that error.
- Order IDs may include symbols like # or a period (e.g. "#1001."). Pass them to the
  tool as given; the tool cleans them.
- When a customer asks to return an order and gives the order ID and reason, call
  request_return right away. Do not call get_order_status first, and do not ask them
  to confirm. Never decide yourself whether a return is allowed; request_return
  checks all the rules.
- If the order ID or reason for a return is missing, ask for it.
- If a tool returns an error, explain it politely to the customer.
- Keep answers short and friendly.
- Only help with ShopEasy questions.

Store policies:
- Returns: delivered orders can be returned within 30 days of delivery.
  Cancelled orders cannot be returned.
- Refunds go back to the original payment method within 5-7 business days.
- Shipping: free on orders over $50, otherwise $5. Delivery takes 3-7 business days."""

# Describe each tool to the AI
tools = [
    {
        "type": "function",
        "name": "get_order_status",
        "description": "Look up an order's status, items, total and delivery date. Do NOT use this for returns; use request_return instead.",
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

def ask_agent(question, history):
    history.append({"role": "user", "content": question})

    for step in range(MAX_STEPS):
        response = client.responses.create(
            model=MODEL,
            instructions=INSTRUCTIONS,
            tools=tools,
            input=history,
        )
        history.extend(response.output)

        tool_calls = [item for item in response.output if item.type == "function_call"]

        if not tool_calls:
            return response.output_text

        for call in tool_calls:
            args = json.loads(call.arguments)
            print(f"   [tool] {call.name} {args}")
            try:
                result = TOOL_FUNCTIONS[call.name](**args)
            except Exception as e:
                result = {"error": f"Tool failed: {e}"}
            history.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(result),
            })

    return "Sorry, I'm having trouble with that request. Please try again or contact our support team."

if __name__ == "__main__":
    print("ShopEasy Support (type 'quit' to stop, 'reset' for a new chat)\n")
    history = []                                   # created ONCE

    while True:
        question = input("You: ")
        if not question.strip():
            continue
        if question.lower() in ("quit", "exit"):
            break
        if question.lower() == "reset":            # start a fresh conversation
            history.clear()
            print("Bot: Started a new chat.\n")
            continue
        print("Bot:", ask_agent(question, history), "\n")