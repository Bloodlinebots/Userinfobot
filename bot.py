import os
import logging
from pyrogram import Client, filters
from pyrogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    KeyboardButtonRequestUser, KeyboardButtonRequestChat
)

API_ID = int(os.environ.get("API_ID", 123456))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

print("📦 Loading bot configuration...")

bot = Client("forward_info_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logging.basicConfig(level=logging.INFO)

@bot.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    user = message.from_user

    # Menu reply keyboard with user/chat request buttons
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📱 User",
                    request_user=KeyboardButtonRequestUser(request_id=1, user_is_bot=False)
                ),
                KeyboardButton(
                    text="🤖 Bot",
                    request_user=KeyboardButtonRequestUser(request_id=2, user_is_bot=True)
                )
            ],
            [
                KeyboardButton(
                    text="📣 Channel",
                    request_chat=KeyboardButtonRequestChat(
                        request_id=3,
                        chat_is_channel=True,
                        bot_is_member=False
                    )
                ),
                KeyboardButton(
                    text="👥 Chat",
                    request_chat=KeyboardButtonRequestChat(
                        request_id=4,
                        chat_is_channel=False,
                        bot_is_member=False
                    )
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    await message.reply_text(
        f"👋 Welcome {user.first_name}!\n"
        f"🆔 ID: `{user.id}`\n"
        f"🔗 Username: @{user.username if user.username else 'N/A'}\n"
        f"📦 Type: User",
        reply_markup=keyboard
    )

    await message.reply_text("🛠 Support: @botmine_tech")

@bot.on_message(filters.forwarded)
async def forwarded_info_handler(client, message: Message):
    fwd = message.forward_from or message.forward_from_chat
    if not fwd:
        await message.reply_text("❌ Unable to extract forwarded info.")
        return

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

    try:
        photos = await client.get_chat_photos(user_id, limit=1)
        if photos:
            await message.reply_photo(
                photo=photos[0].file_id,
                caption=caption
            )
        else:
            await message.reply_text(caption)
    except Exception as e:
        print(f"⚠️ Error sending profile photo: {e}")
        await message.reply_text(caption)

@bot.on_user_shared()
async def handle_user_shared(client, message: Message):
    user_id = message.user_shared.user_id
    try:
        user = await client.get_users(user_id)
        name = user.first_name
        username = user.username
        caption = (
            f"**📌 Name:** `{name}`\n"
            f"**🆔 ID:** `{user.id}`\n"
            f"**🔗 Username:** @{username if username else 'N/A'}\n"
            f"**📦 Type:** Bot" if user.is_bot else "**📦 Type:** User"
        )

        photos = await client.get_chat_photos(user.id, limit=1)
        if photos:
            await message.reply_photo(photos[0].file_id, caption=caption)
        else:
            await message.reply_text(caption)
    except Exception as e:
        await message.reply_text(f"❌ Failed to fetch user.\n`{e}`")

@bot.on_chat_shared()
async def handle_chat_shared(client, message: Message):
    chat_id = message.chat_shared.chat_id
    try:
        chat = await client.get_chat(chat_id)
        name = chat.title
        username = chat.username
        chat_type = chat.type.capitalize()

        caption = (
            f"**📌 Name:** `{name}`\n"
            f"**🆔 ID:** `{chat.id}`\n"
            f"**🔗 Username:** @{username if username else 'N/A'}\n"
            f"**📦 Type:** {chat_type}"
        )

        photos = await client.get_chat_photos(chat.id, limit=1)
        if photos:
            await message.reply_photo(photos[0].file_id, caption=caption)
        else:
            await message.reply_text(caption)
    except Exception as e:
        await message.reply_text(f"❌ Failed to fetch chat.\n`{e}`")

if __name__ == "__main__":
    print("🚀 Starting bot...")
    try:
        bot.run()
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")
