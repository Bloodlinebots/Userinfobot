import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.environ.get("API_ID", 123456))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

print("📦 Loading bot configuration...")

bot = Client("forward_info_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logging.basicConfig(level=logging.INFO)

# Store recent chats/entities
recent_entities = []
MAX_RECENTS = 10

def add_recent(entity):
    global recent_entities
    if entity not in recent_entities:
        recent_entities.insert(0, entity)
        if len(recent_entities) > MAX_RECENTS:
            recent_entities.pop()

@bot.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    user = message.from_user
    add_recent(user)
    caption = (
        f"👋 Welcome {user.first_name}!\n"
        f"🆔 ID: `{user.id}`\n"
        f"🔗 Username: @{user.username if user.username else 'N/A'}\n"
        f"📦 Type: User"
    )
    buttons = [
        [
            InlineKeyboardButton("👤 User", callback_data="pick_user"),
            InlineKeyboardButton("🤖 Bot", callback_data="pick_bot")
        ],
        [
            InlineKeyboardButton("📢 Channel", callback_data="pick_channel"),
            InlineKeyboardButton("👥 Chat", callback_data="pick_chat")
        ],
        [
            InlineKeyboardButton("🛠 Support", url="https://t.me/botmine_tech")
        ]
    ]
    await message.reply_text(caption, reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_message(filters.forwarded)
async def forwarded_info_handler(client, message: Message):
    fwd = message.forward_from or message.forward_from_chat
    if not fwd:
        await message.reply_text("❌ Unable to extract forwarded info.")
        return

    add_recent(fwd)
    name = getattr(fwd, 'first_name', getattr(fwd, 'title', 'Unknown'))
    user_id = fwd.id
    username = getattr(fwd, 'username', None)
    fwd_type = getattr(fwd, 'type', 'user').capitalize()

    caption = (
        f"**📌 Name:** `{name}`\n"
        f"**🆔 ID:** `{user_id}`\n"
        f"**🔗 Username:** @{username if username else 'N/A'}\n"
        f"**📦 Type:** {fwd_type}"
    )

    buttons = [
        [
            InlineKeyboardButton("👤 User", callback_data="pick_user"),
            InlineKeyboardButton("🤖 Bot", callback_data="pick_bot")
        ],
        [
            InlineKeyboardButton("📢 Channel", callback_data="pick_channel"),
            InlineKeyboardButton("👥 Chat", callback_data="pick_chat")
        ]
    ]

    try:
        photos = await client.get_chat_photos(user_id, limit=1)
        if photos:
            await message.reply_photo(
                photo=photos[0].file_id,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await message.reply_text(caption, reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        print(f"⚠️ Error sending profile photo: {e}")
        await message.reply_text(caption, reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_callback_query(filters.regex("^pick_"))
async def handle_pick_callback(client, callback_query):
    _, typ = callback_query.data.split("_")
    types_map = {
        "user": ["private"],
        "bot": ["bot"],
        "channel": ["channel"],
        "chat": ["group", "supergroup"]
    }

    matched = None
    for e in recent_entities:
        if hasattr(e, 'type') and (e.type in types_map.get(typ, [])):
            matched = e
            break

    if not matched:
        await callback_query.answer("No recent match found.", show_alert=True)
        return

    name = getattr(matched, 'first_name', getattr(matched, 'title', 'Unknown'))
    user_id = matched.id
    username = getattr(matched, 'username', None)
    fwd_type = matched.type.capitalize()

    caption = (
        f"**📌 Name:** `{name}`\n"
        f"**🆔 ID:** `{user_id}`\n"
        f"**🔗 Username:** @{username if username else 'N/A'}\n"
        f"**📦 Type:** {fwd_type}"
    )

    try:
        photos = await client.get_chat_photos(user_id, limit=1)
        if photos:
            await callback_query.message.reply_photo(
                photo=photos[0].file_id,
                caption=caption
            )
        else:
            await callback_query.message.reply_text(caption)
        await callback_query.answer()
    except Exception as e:
        print(f"❌ Error during callback: {e}")
        await callback_query.answer("Failed to fetch.", show_alert=True)

if __name__ == "__main__":
    print("🚀 Starting bot...")
    try:
        bot.run()
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")
