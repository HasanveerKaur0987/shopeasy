# ShopEasy: AI Customer Support Agent

An AI agent that handles customer support for an online store. It looks up orders, searches products, explains store policies, and processes returns, using **OpenAI tool calling** with business rules enforced in Python code.

> **Status:** Week 1 of 3 done. The agent works in the terminal.
> Coming next: SQLite database, FastAPI backend, web chat page, user login, Docker and CI.

## Example

```
You: Do you have any bags?
   [tool] search_products {'query': 'bag'}
Bot: We have a backpack available. It's a 25 litre backpack with a laptop pocket,
     priced at $60. There are 5 in stock.

You: Return order #1006, it broke
   [tool] request_return {'order_id': '1006', 'reason': 'it broke'}
Bot: I'm sorry, but the return window for order 1006 has passed. It has been
     52 days since delivery, and returns are only accepted within 30 days.
```

## How it works

```
Customer message
      |
      v
  AI model (gpt-4.1-mini) --- decides which tool it needs
      |
      v
  Python tool runs (looks up data, checks rules)
      |
      v
  Result goes back to the AI --- AI writes a friendly reply
```

The agent loops until the AI has everything it needs (max 5 steps), so one question can use several tools.

## Tools

| Tool | What it does |
| --- | --- |
| `get_order_status` | Looks up an order's status, items, total and delivery date |
| `search_products` | Finds products by name, description or tags ("bag" finds the backpack) |
| `list_products` | Lists everything the store sells, with price and stock |
| `request_return` | Starts a return, but only if the rules allow it |

## Design decisions

- **Business rules live in code, not in the AI.** `request_return` checks that the order exists, is delivered, is within 30 days, and has no open return. The AI only reports the result. Early tests showed the AI sometimes "decided" on its own, so the rules were moved fully into code.
- **Fewer, clearer tools.** An early `get_product_info` tool overlapped with `search_products`, so they were merged. Each tool has one clear job, which helps the AI pick the right one.
- **Messy input is cleaned in code.** Order IDs like `#1001.` are cleaned to `1001` before lookup.
- **Today's date is given to the AI.** Without it, the AI treated future delivery dates as past ones.
- **Chat memory.** The full conversation is sent on each turn, so follow-ups like "it's too small" work.
- **Safe failure.** A tool error is passed back to the AI as a message instead of crashing the chat, and the agent loop stops after 5 steps.

## Testing

`agent/test_agent.py` runs 12 test questions automatically. For each one it checks:

1. The AI called the right tool (or no tool, for policy and off-topic questions)
2. The answer contains the expected facts
3. The answer avoids wrong content (for example, answering off-topic questions)

**Current score: 12/12**

## Run it locally

```bash
git clone https://github.com/<your-username>/shopeasy.git
cd shopeasy
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the `shopeasy` folder:

```
OPENAI_API_KEY=your-key-here
```

Then:

```bash
cd agent
python main.py          # chat with the agent
python test_agent.py    # run the tests
```

## Project structure

```
shopeasy/
├── agent/
│   ├── data.py         # fake store data (products and orders)
│   ├── tools.py        # tool functions with business rules
│   ├── main.py         # agent loop, instructions and chat
│   └── test_agent.py   # automated test questions with a score
├── requirements.txt
└── README.md
```

## Roadmap

- [x] Agent with 4 tools, chat memory and return rules
- [x] Automated tests
- [ ] SQLite database
- [ ] FastAPI backend with chat history per user
- [ ] Web chat page (HTML, CSS, JavaScript)
- [ ] Deploy online
- [ ] User login (users only see their own orders)
- [ ] Streaming replies and safety rules
- [ ] Human handoff tickets and a larger evaluation (30-50 questions)
- [ ] Docker and GitHub Actions CI

## Tech

Python, OpenAI Responses API (tool calling), python-dotenv
