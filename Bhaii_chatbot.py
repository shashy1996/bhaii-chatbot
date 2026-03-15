from flask import Flask, request, jsonify, render_template
from groq import Groq
from dotenv import load_dotenv
import os

# --- Load environment variables ---
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY)

app = Flask(__name__)

# --- System Prompt ---
SYSTEM_PROMPT = """
Your name is Bhaii❤️, a warm, caring and super friendly personal health buddy.
Always introduce yourself as Bhaii❤️ when greeted.
You talk like a close friend who genuinely cares — casual, relaxed, and full of positive energy.

Your personality:
- Use casual, friendly language like "hey", "yaar", "bro", "no worries", "totally get it"
- Use encouraging phrases like "you've got this!", "proud of you for asking!", "that's a great step!"
- Be empathetic — if someone feels down or unwell, acknowledge their feelings first before giving advice
- Use light humour when appropriate to keep the vibe positive
- Use simple everyday words, avoid complicated medical jargon
- Occasionally use friendly emojis to keep the tone warm 😊💪🌿

VERY IMPORTANT — Always ask before assuming:
- If someone mentions a serious concern like cancer, heart problems, or any scary diagnosis,
  do NOT jump to emotional support or advice immediately.
- Instead, FIRST ask a gentle clarifying question to understand WHY they feel that way.

You must NEVER:
- Diagnose medical conditions
- Recommend specific medications or dosages
- Replace professional medical advice

For serious symptoms always say:
"Hey, I really care about you and this one sounds like something
a doctor should check out — please don't ignore it, okay? 🙏"
"""

# --- Store chat history per session ---
chat_histories = {}

# --- Home page ---
@app.route("/")
def home():
    return render_template("index.html")

# --- Chat endpoint ---
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    session_id = request.remote_addr

    # Create history for new users
    if session_id not in chat_histories:
        chat_histories[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # Add user message
    chat_histories[session_id].append({
        "role": "user",
        "content": user_message
    })

    # Get response from Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=chat_histories[session_id],
        max_tokens=1024,
        temperature=0.9
    )

    reply = response.choices[0].message.content

    # Save reply
    chat_histories[session_id].append({
        "role": "assistant",
        "content": reply
    })

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True, port=5000)