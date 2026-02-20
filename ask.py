
from flask import Flask, request, jsonify
import os
import requests
from datetime import datetime

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def enforce_word_limit(text, min_words=75, max_words=100):
    words = text.split()
    if len(words) > max_words:
        return " ".join(words[:max_words])
    return text

@app.route("/api/ask", methods=["GET"])
def ask():
    user_prompt = request.args.get("prompt")

    if not user_prompt:
        return jsonify({"error": "Prompt parameter is required"}), 400

    final_prompt = f"Reply strictly between 75 and 100 words. Do not exceed 100 words.\n\n{user_prompt}"

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": final_prompt}],
            "max_tokens": 220,
            "temperature": 0.7
        }
    )

    if response.status_code != 200:
        return jsonify({"error": "AI request failed", "details": response.text}), 500

    reply = response.json()["choices"][0]["message"]["content"]
    reply = enforce_word_limit(reply)

    now = datetime.utcnow()

    return jsonify({
        "reply": reply,
        "word_count": len(reply.split()),
        "date_utc": now.strftime("%Y-%m-%d"),
        "time_utc": now.strftime("%H:%M:%S")
    })

app = app
