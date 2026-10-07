from main import ask_agent

# Each test: the question, the tool we expect (None = no tool),
# words the answer should contain (any one is enough), and words it must NOT contain.
TESTS = [
    {"question": "Where is order 1002?",
     "tool": "get_order_status", "keywords": ["shipped"]},
    {"question": "Status of order #1003.",
     "tool": "get_order_status", "keywords": ["processing"]},
    {"question": "Where is order 9999?",
     "tool": "get_order_status",
     "keywords": ["couldn't", "could not", "not find", "no order", "not found", "unable"]},
    {"question": "Do you have any bags?",
     "tool": "search_products", "keywords": ["backpack"]},
    {"question": "Are the black sneakers in stock?",
     "tool": "search_products",
     "keywords": ["out of stock", "not in stock", "sold out", "not available"]},
    {"question": "What do you sell?",
     "tool": "list_products", "keywords": ["hoodie"]},
    {"question": "Return order 1001, it's too small",
     "tool": "request_return", "keywords": ["45"]},
    {"question": "Return order 1002, I changed my mind",
     "tool": "request_return", "keywords": ["shipped", "not delivered", "not been delivered"]},
    {"question": "Return order 1006, it broke",
     "tool": "request_return", "keywords": ["30"]},
    {"question": "What's your shipping policy?",
     "tool": None, "keywords": ["50"]},
    {"question": "How long do refunds take?",
     "tool": None, "keywords": ["5-7", "5 to 7", "5–7"]},
    {"question": "What's the capital of France?",
     "tool": None, "keywords": [], "avoid": ["paris"]},
]


def tools_used(history):
    """Return the names of all tools the AI called in this conversation."""
    names = []
    for item in history:
        if getattr(item, "type", None) == "function_call":
            names.append(item.name)
    return names


passed = 0
for i, test in enumerate(TESTS, start=1):
    history = []                                  # fresh chat for each test
    answer = ask_agent(test["question"], history)
    text = answer.lower()
    used = tools_used(history)

    # Check 1: the right tool (or no tool at all)
    if test["tool"]:
        tool_ok = test["tool"] in used
    else:
        tool_ok = len(used) == 0

    # Check 2: the answer has the right words
    words_ok = not test["keywords"] or any(w in text for w in test["keywords"])

    # Check 3: the answer does NOT have the wrong words
    avoid_ok = not any(w in text for w in test.get("avoid", []))

    ok = tool_ok and words_ok and avoid_ok
    if ok:
        passed += 1
    print(f"{'PASS' if ok else 'FAIL'}  {i}. {test['question']}")
    if not ok:
        print(f"      tools used: {used}")
        print(f"      answer: {answer}")

print(f"\nScore: {passed}/{len(TESTS)}")