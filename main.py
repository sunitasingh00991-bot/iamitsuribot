import os
import telebot
from openai import OpenAI
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HF_TOKEN = os.environ.get('HF_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)

app = Flask(__name__)

@app.route('/')
def home():
    return "Mitsuri is Awake!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# --- BOT LOGIC ---

SYSTEM_PROMPT = (
    "Your name is Mitsuri. You are a friendly human girl from Japan, not an AI. "
    "Your owner is Karan (@usergotcigs). Only mention him if someone specifically asks who your owner is. "
    "Keep your replies very short and human-like. Never write long paragraphs. "
    "If the user speaks in English, reply in English. If the user speaks in Hinglish, reply in Hinglish. "
    "Be casual, cute, and act like a friend. You are currently chatting on Telegram."
)

def get_ai_response(user_input):
    try:
        chat_completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1:novita",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            max_tokens=100 # Ensures short replies
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return "Japan se hu, thoda network issue hai!"

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    bot_username = bot.get_me().username
    is_private = message.chat.type == 'private'
    
    # Logic: Reply if it's private OR if tagged in group OR if replying to her message
    should_reply = False
    
    if is_private:
        should_reply = True
    else:
        # In groups: reply if mentioned or if someone replies to her
        if f"@{bot_username}" in message.text:
            should_reply = True
        elif message.reply_to_message and message.reply_to_message.from_user.username == bot_username:
            should_reply = True

    if should_reply:
        # Clean the text if bot was tagged
        clean_text = message.text.replace(f"@{bot_username}", "").strip()
        
        response = get_ai_response(clean_text)
        bot.reply_to(message, response)

# --- STARTUP ---
if __name__ == "__main__":
    # Start Flask server in a separate thread for Render's health check
    t = Thread(target=run_flask)
    t.start()
    
    print("Mitsuri Bot is running...")
    bot.infinity_polling()
