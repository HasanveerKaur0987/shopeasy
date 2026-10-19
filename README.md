# ShopEasy: AI Customer Support Agent

An AI support agent for an online store. Customers chat on a web page, and the agent looks up orders, searches products, explains store policies, and processes returns. It uses **OpenAI tool calling**, with all business rules enforced in Python code and data stored in **SQLite**.

**Live demo:** https://shopeasy-ggve.onrender.com
Hosted on Render's free plan, so the first visit after a quiet period can take about a minute to wake up. Try order IDs 1001 to 1006.

## What it can do

- **Track orders:** status, items, and delivery dates
- **Find products:** by name, description or tags ("bag" finds the backpack)
- **Start returns:** only when the store's rules allow it
- **Answer policy questions:** shipping, returns and refunds
- **Remember the conversation:** follow-ups like "what items are in it?" work
- **Stay on topic:** politely refuses questions that aren't about the store

## Example

```
You: Where is order 1002?
Bot: Your order 1002 has shipped and should arrive in 3 days.

You: What items are in it?
Bot: Order 1002 includes a Backpack and a Water Bottle.

You: Return order 1006, it broke
Bot: The return window for order 1006 has passed. It was delivered 60 days ago,
     and returns are accepted within 30 days.
```

## How it works

```
Chat page (HTML, CSS, JavaScript)
      |   fetch() sends {"session_id", "message"} as JSON
      v
Flask backend (app.py)
      |   finds this session's chat history
      v
AI agent (main.py)
      |   the model decides which tool to call (max 5 steps)
      v
Tools (tools.py)  --->  SQLite database
      |   look up data, check business rules
      v
The AI writes a reply  --->  Flask returns {"reply"}  --->  shown on the page
```

### Tools

| Tool | What it does |
| --- | --- |
| `get_order_status` | Looks up an order's status, items, total and delivery dates |
| `search_products` | Searches products by name, description or tags |
| `list_products` | Lists everything the store sells, with price and stock |
| `request_return` | Starts a return, only if the order is delivered, within 30 days, and has no open return |

### Database

| Table | Holds |
| --- | --- |
| `products` | Name, price, stock, description, tags |
| `orders` | Customer, total, status, order date, delivery dates |
| `order_items` | One row per item in an order (linked to `orders` with a foreign key) |

## Design decisions

- **Business rules live in code, not in the AI.** During testing, the AI sometimes "decided" on returns by itself, and once said an order wasn't found without checking. Now `request_return` enforces every rule in Python, and the AI only reports the result.
- **Two layers of safety.** The instructions control *whether* the AI calls a tool. The code controls *what happens* when it does, which is always reliable.
- **Fewer, clearer tools.** An early `get_product_info` tool overlapped with `search_products`, so they were merged. Each tool has one clear job, which helps the AI pick the right one.
- **Safe database queries.** All SQL uses `?` placeholders, never string formatting, so text from customers can't change a query (SQL injection).
- **Messy input is cleaned in code.** Order IDs like `#1001.` become `1001` before lookup.
- **Today's date is given to the AI.** Without it, the AI treated future delivery dates as past ones.
- **A separate chat history for each browser session,** so two people using the demo never see each other's conversation.
- **Test data uses relative dates** (`date('now', '-11 days')`), so the demo and tests never go stale.
- **Safe failure.** Tool errors are passed back to the AI instead of crashing, the agent loop stops after 5 steps, and the page shows a friendly message if the server can't be reached.
- **Safe page updates.** Messages are added with `textContent`, never `innerHTML`, so text can't inject code into the page (XSS).

## Testing

`agent/test_agent.py` runs 12 test questions through the agent. For each one, it checks that:

1. The AI called the right tool (or no tool, for policy and off-topic questions)
2. The answer contains the expected facts
3. The answer avoids wrong content (for example, answering off-topic questions)

A lesson from testing: AI wording changes from run to run, so the tests accept several correct phrasings.

## Tech

Python · OpenAI Responses API (tool calling, `gpt-4.1-mini`) · Flask · SQLite · HTML · CSS · JavaScript (`fetch`, async/await)

## Project structure

```
shopeasy/
├── agent/
│   ├── app.py            # Flask: chat page + POST /chat
│   ├── main.py           # agent loop, instructions, tool descriptions
│   ├── tools.py          # tool functions with business rules
│   ├── db.py             # database connection
│   ├── test_agent.py     # automated test questions
│   ├── templates/
│   │   └── index.html    # chat page
│   └── static/
│       ├── style.css
│       └── script.js     # sends messages, shows replies
├── database/
│   ├── schema.sql        # tables
│   └── seed.sql          # sample store data
├── requirements.txt
└── README.md
```

## Run it locally

**1. Install**

```bash
git clone https://github.com/<your-username>/shopeasy.git
cd shopeasy
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Add your OpenAI key.** Create a `.env` file in the `shopeasy` folder:

```
OPENAI_API_KEY=your-key-here
```

**3. Build the database**

```bash
cd database
sqlite3 shopeasy.db < schema.sql
sqlite3 shopeasy.db < seed.sql
```

**4. Start the app**

```bash
cd ../agent
python app.py
```

Open **http://127.0.0.1:5001/** and start chatting.

**Run the tests** (rebuild the database first, since a test makes a return):

```bash
python test_agent.py
```

## Roadmap

- [x] AI agent with 4 tools, chat memory and return rules
- [x] Automated tests
- [x] SQLite database
- [x] Flask backend with a separate chat history per session
- [x] Chat page (HTML, CSS, JavaScript)
- [ ] Deploy online
- [ ] Human handoff: create a support ticket when the agent can't help
- [ ] User login (customers only see their own orders)
- [ ] Streaming replies
- [ ] Storefront page with the chat as a bubble in the corner
