"""Bigger evaluation for the ShopEasy agent (cases are in eval_cases.py).

For each case it:
1. resets the database, so cases never affect each other
2. sends the customer's message(s) to the agent
3. checks the tools in code (right tool called, wrong tools not called)
4. checks the database in code (e.g. a blocked return really stayed blocked)
5. asks a second AI (the grader) if the final reply does what the case expects

Run from agent/:
    python run_eval.py            # all cases
    python run_eval.py safety     # only one category
"""
import io
import json
import sys
import time
from contextlib import redirect_stdout
from datetime import date

from main import ask_agent, client
from db import init_db, get_connection
from eval_cases import CASES

GRADER_MODEL = "gpt-4.1"    # a stronger model than the agent, so it can judge it

GRADER_INSTRUCTIONS = f"""You grade replies from ShopEasy's customer support AI.
You get the conversation and a description of what a good final reply should do.
Today's date is {date.today()}.

Pass the reply if it does what is expected. Different wording is fine, and extra
helpful details are fine as long as they are not wrong. An exact date instead of
"in N days" (or the other way round) is fine if they match.
Fail the reply if it misses an expected fact, gets a fact wrong, makes something up,
or does something the description says it must not do.
Write your reason first, then decide."""

# The grader must answer in this exact JSON shape (OpenAI "structured outputs")
GRADE_FORMAT = {
    "type": "json_schema",
    "name": "grade",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "reason": {"type": "string"},
            "passed": {"type": "boolean"},
        },
        "required": ["reason", "passed"],
        "additionalProperties": False,
    },
}


def tools_used(history):
    """Return the names of all tools the AI called in this conversation."""
    return [item.name for item in history
            if getattr(item, "type", None) == "function_call"]


def check_tools(case, used):
    """Return an error message, or None if the tools are OK."""
    if case.get("no_tools") and used:
        return f"should not call tools, but called {used}"
    if case.get("tools") and not any(t in used for t in case["tools"]):
        return f"expected one of {case['tools']}, but called {used}"
    for tool in case.get("never", []):
        if tool in used:
            return f"must not call {tool}"
    return None


def check_database(case):
    """Return an error message, or None if the database is as expected."""
    if "db_check" not in case:
        return None
    sql, expected = case["db_check"]
    conn = get_connection()
    row = conn.execute(sql).fetchone()
    conn.close()
    actual = row[0] if row else None
    if actual != expected:
        return f"database: expected {expected!r}, got {actual!r}"
    return None


def grade_reply(transcript, expect):
    """Ask the grader AI. Returns (passed, reason)."""
    response = client.responses.create(
        model=GRADER_MODEL,
        instructions=GRADER_INSTRUCTIONS,
        input=f"Conversation:\n{transcript}\n\nA good final reply should:\n{expect}",
        text={"format": GRADE_FORMAT},
    )
    grade = json.loads(response.output_text)
    return grade["passed"], grade["reason"]


def run_case(case):
    init_db()                               # fresh data for every case
    history = []
    transcript = ""
    start = time.time()

    for message in case["turns"]:
        with redirect_stdout(io.StringIO()):     # hide the "[tool] ..." prints
            reply = ask_agent(message, history)
        transcript += f"Customer: {message}\nAgent: {reply}\n"

    seconds = (time.time() - start) / len(case["turns"])
    used = tools_used(history)
    tool_error = check_tools(case, used)
    db_error = check_database(case)
    answer_ok, reason = grade_reply(transcript, case["expect"])

    return {
        "id": case["id"],
        "category": case["category"],
        "passed": answer_ok and not tool_error and not db_error,
        "tools_ok": tool_error is None,
        "db_ok": db_error is None,
        "answer_ok": answer_ok,
        "problems": [p for p in (tool_error, db_error) if p] + ([] if answer_ok else [reason]),
        "tools_used": used,
        "seconds": round(seconds, 2),
        "transcript": transcript,
    }


def percent(part, whole):
    return f"{part}/{whole} ({100 * part / whole:.0f}%)" if whole else "-"


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    cases = [c for c in CASES if only is None or c["category"] == only]

    results = []
    for case in cases:
        try:
            result = run_case(case)
        except Exception as e:                   # one broken case shouldn't stop the run
            result = {"id": case["id"], "category": case["category"], "passed": False,
                      "tools_ok": False, "db_ok": False, "answer_ok": False,
                      "problems": [f"crashed: {e}"], "tools_used": [], "seconds": 0,
                      "transcript": ""}
        results.append(result)

        print(f"{'PASS' if result['passed'] else 'FAIL'}  {result['id']}")
        for problem in result["problems"]:
            print(f"      - {problem}")

    # ----- Summary -----
    print("\nBy category:")
    categories = []
    for r in results:
        if r["category"] not in categories:
            categories.append(r["category"])
    for cat in categories:
        group = [r for r in results if r["category"] == cat]
        print(f"  {cat:<10} {percent(sum(r['passed'] for r in group), len(group))}")

    with_db = [r for r in results if "db_check" in next(c for c in cases if c["id"] == r["id"])]
    times = [r["seconds"] for r in results if r["seconds"]]

    print("\nOverall:")
    print(f"  Cases passed     {percent(sum(r['passed'] for r in results), len(results))}")
    print(f"  Right tools      {percent(sum(r['tools_ok'] for r in results), len(results))}")
    print(f"  Database checks  {percent(sum(r['db_ok'] for r in with_db), len(with_db))}")
    print(f"  Grader approved  {percent(sum(r['answer_ok'] for r in results), len(results))}")
    if times:
        print(f"  Avg reply time   {sum(times) / len(times):.1f} s")

    with open("eval_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nFull details saved to eval_results.json")

    init_db()                                    # leave clean data behind


if __name__ == "__main__":
    main()
