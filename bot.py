import os
import json
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message

# Load environment variables from config.py or os.getenv
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_LOG_CHAT_ID

app = Client(
    "teleinfo_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

STATS_FILE = "stats.json"

# Load or initialize stats
try:
    with open(STATS_FILE, "r") as f:
        stats = json.load(f)
except FileNotFoundError:
    stats = {
        "total_users": 0,
        "users_set": [],
        "daily_users": {},
        "total_lookups": 0,
    }

def save_stats():
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)

def increment_user(user_id):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    user_id_str = str(user_id)
    if user_id_str not in stats["users_set"]:
        stats["users_set"].append(user_id_str)
        stats["total_users"] += 1
    stats["daily_users"].setdefault(today, 0)
    stats["daily_users"][today] += 1

def increment_lookups():
    stats["total_lookups"] += 1

def format_user(user):
    return f"""👤 User Info:
• ID: {user.id}
• First Name: {user.first_name or 'N/A'}
• Last Name: {user.last_name or 'N/A'}
• Username: @{user.username or 'N/A'}
• Is Bot: {user.is_bot}"""

def format_chat(chat):
    return f"""📢 Channel/Group Info:
• ID: {chat.id}
• Title: {chat.title}
• Username: @{chat.username or 'N/A'}
• Type: {chat.type}"""

async def log_event(text):
    try:
        if ADMIN_LOG_CHAT_ID:
            await app.send_message(ADMIN_LOG_CHAT_ID, text)
    except Exception:
        pass  # Prevent crash if logging fails

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Message):
    user = message.from_user

    increment_user(user.id)
    increment_lookups()
    save_stats()

    await log_event(f"🚀 /start used by {user.first_name} (`{user.id}`)")

    bot = await client.get_me()
    bot_name = bot.first_name

    welcome_text = f"""👋 **Welcome, {user.first_name or 'User'}!**

I'm **{bot_name}** 🤖 — your personal Telegram ID & Info assistant.

📌 **What I can do:**
• Forward a message or reply to someone — I'll fetch full info
• Send a user ID or @username — I'll find their info

🔐 Your data is never stored .
📮 Use me freely & securely!"""

    await message.reply_text(welcome_text)

@app.on_message(filters.private & ~filters.command("start"))
async def handle_message(client, message: Message):
    user = message.from_user

    increment_user(user.id)
    increment_lookups()
    save_stats()

    await log_event(f"ℹ️ Used by {user.first_name} (`{user.id}`) - Text: {message.text or 'No text'}")

    if message.reply_to_message and message.reply_to_message.from_user:
        await message.reply_text(format_user(message.reply_to_message.from_user))
        return

    if message.forward_from:
        await message.reply_text(format_user(message.forward_from))
        return

    if message.forward_from_chat:
        await message.reply_text(format_chat(message.forward_from_chat))
        return

    if not message.text:
        return

    text = message.text.strip()

    if text.isdigit():
        try:
            target_user = await client.get_users(int(text))
            await message.reply_text(format_user(target_user))
        except Exception:
            await message.reply_text(f"❌ User not found for ID `{text}`")
        return

    if not text.startswith("@"):  # username search
        text = "@" + text

    try:
        target_user = await client.get_users(text)
        await message.reply_text(format_user(target_user))
    except Exception:
        await message.reply_text(f"❌ User not found for username `{text}`")

@app.on_message(filters.command("stats") & filters.private)
async def stats_handler(client, message: Message):
    total_users = stats.get("total_users", 0)
    total_lookups = stats.get("total_lookups", 0)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    daily_users = stats.get("daily_users", {}).get(today, 0)

    await message.reply_text(
        f"""📊 **Bot Stats:**
• Total Unique Users: {total_users}
• Total Lookups: {total_lookups}
• Today’s Users: {daily_users}"""
    )

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
