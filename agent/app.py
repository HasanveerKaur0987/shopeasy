from flask import Flask, request, render_template
from main import ask_agent


app = Flask(__name__)

from db import init_db, get_connection
init_db()

histories = {}

@app.route("/")
def home():
    # Store page: load the products so Jinja can show one card per product
    conn = get_connection()
    rows = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    products = [dict(row) for row in rows]
    return render_template("store.html", products=products)


@app.route("/support")
def support():
    # The old full-page chat
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    # 1. Read the JSON the page sent (or an empty dict if it sent nothing useful)
    data = request.get_json(silent=True) or {}

    # 2. Get the two values we need
    message = (data.get("message") or "").strip()
    session_id = data.get("session_id")

    # 3. If either is missing, it's the caller's mistake -> 400
    if not message or not session_id:
        return {"error": "Both 'message' and 'session_id' are required."}, 400

    # 4. Find this session's history (create it if this is a new session)
    if session_id not in histories:
        histories[session_id] = []
    history = histories[session_id]

    # 5. Ask the agent. If anything fails (OpenAI down, bad key), don't crash -> 500
    try:
        reply = ask_agent(message, history)
    except Exception as e:
        print("Error in /chat:", e)          # shows in your terminal for debugging
        return {"error": "Something went wrong. Please try again."}, 500

    # 6. Send the reply back as JSON
    return {"reply": reply}


if __name__ == "__main__":
    app.run(debug=True, port=5001)