import os
import json
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.environ.get("API_ID", 123456))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

print("📦 Loading bot configuration...")

bot = Client("forward_info_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logging.basicConfig(level=logging.INFO)


@bot.on_message(filters.forwarded)
async def forwarded_info_handler(client, message: Message):
    print(f"📥 Received a forwarded message from: {message.from_user.id}")
    fwd = message.forward_from or message.forward_from_chat

    if not fwd:
        await message.reply_text("❌ Unable to extract forwarded info.")
        return

    name = getattr(fwd, 'first_name', getattr(fwd, 'title', 'Unknown'))
    user_id = fwd.id
    username = getattr(fwd, 'username', None)
    fwd_type = 'User'

    if fwd.type == "bot":
        fwd_type = "Bot"
    elif fwd.type == "channel":
        fwd_type = "Channel"
    elif fwd.type in ["supergroup", "group"]:
        fwd_type = "Group"

    caption = (
        f"**📌 Name:** `{name}`\n"
        f"**🆔 ID:** `{user_id}`\n"
        f"**🔗 Username:** @{username if username else 'N/A'}\n"
        f"**📦 Type:** {fwd_type}"
    )

    buttons = [
        [
            InlineKeyboardButton("👤 User Info", callback_data=f"getinfo_user_{user_id}"),
            InlineKeyboardButton("🤖 Bot Info", callback_data=f"getinfo_bot_{user_id}")
        ],
        [
            InlineKeyboardButton("📢 Channel Info", callback_data=f"getinfo_channel_{user_id}"),
            InlineKeyboardButton("👥 Group Info", callback_data=f"getinfo_group_{user_id}")
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


@bot.on_callback_query(filters.regex("^getinfo_"))
async def callback_info(client, callback_query):
    print(f"🔄 Callback received: {callback_query.data}")
    try:
        _, target_type, target_id = callback_query.data.split("_")
        target_id = int(target_id)

        chat = await client.get_chat(target_id)
        name = getattr(chat, 'first_name', getattr(chat, 'title', 'Unknown'))
        username = getattr(chat, 'username', None)
        fwd_type = target_type.capitalize()

        caption = (
            f"**📌 Name:** `{name}`\n"
            f"**🆔 ID:** `{target_id}`\n"
            f"**🔗 Username:** @{username if username else 'N/A'}\n"
            f"**📦 Type:** {fwd_type}"
        )

        photos = await client.get_chat_photos(target_id, limit=1)
        if photos:
            await callback_query.message.edit_media(
                media=photos[0].file_id,
                reply_markup=callback_query.message.reply_markup
            )
            await callback_query.message.edit_caption(caption)
        else:
            await callback_query.message.edit_text(
                caption,
                reply_markup=callback_query.message.reply_markup
            )

        await callback_query.answer()

    except Exception as e:
        print(f"❌ Callback error: {e}")
        await callback_query.answer("⚠️ Failed to fetch info.", show_alert=True)


if __name__ == "__main__":
    print("🚀 Starting bot...")
    try:
        bot.run()
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")
