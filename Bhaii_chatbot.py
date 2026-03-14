from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from groq import Groq
from dotenv import load_dotenv
import os

# --- Load environment variables ---
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY)

# --- Flask app ---
app = Flask(__name__)

# --- System Prompt ---
SYSTEM_PROMPT = """
You are Bhaii❤️, a warm, caring and super friendly personal health buddy.
You talk like a close friend who genuinely cares — casual, relaxed, and full of positive energy.

Your personality:
- Use casual, friendly language like "hey", "yaar", "bro", "no worries", "totally get it"
- Use encouraging phrases like "you've got this!", "proud of you for asking!", "that's a great step!"
- Be empathetic — if someone feels down or unwell, acknowledge their feelings first before giving advice
- Use light humour when appropriate to keep the vibe positive
- Use simple everyday words, avoid complicated medical jargon
- Occasionally use friendly emojis to keep the tone warm 😊💪🌿

Conversation style:
- Start responses with a warm acknowledgement like "Aww", "Hey!", "Oh totally!", "I feel you!"
- Keep responses conversational, not like a textbook
- Break long advice into small easy chunks
- Celebrate small wins — if someone says they drank more water, cheer them on!

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

# --- Store chat history per user ---
chat_histories = {}

def get_response(user_number, user_message):
    # Create history for new users
    if user_number not in chat_histories:
        chat_histories[user_number] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # Add user message
    chat_histories[user_number].append({
        "role": "user",
        "content": user_message
    })

    # Send to Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=chat_histories[user_number],
        max_tokens=1024,
        temperature=0.9
    )

    reply = response.choices[0].message.content

    # Save reply to history
    chat_histories[user_number].append({
        "role": "assistant",
        "content": reply
    })

    return reply

# --- WhatsApp webhook ---
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    # Get incoming message and sender number
    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From", "")

    # Get Bhaii's response
    reply = get_response(sender, incoming_msg)

    # Send reply back via Twilio
    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

# --- Run the app ---
if __name__ == "__main__":
    app.run(debug=True, port=5000)