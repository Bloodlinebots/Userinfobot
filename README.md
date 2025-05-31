# TeleInfo Bot 🤖

Telegram bot to get user/channel info using forwarded messages, replies, or usernames.

## 🔧 Features:
- Forwarded message → Shows user/channel info
- Reply to someone → Shows profile details
- Send @username or ID → Fetches info
- /stats → Bot usage stats

## 🛠 Deployment

### 🔹 Heroku:
1. Fork this repo
2. Add these Config Vars:
   - `API_ID`
   - `API_HASH`
   - `BOT_TOKEN`
   - `ADMIN_LOG_CHAT_ID` *(optional)*
3. Deploy

### 🔹 Koyeb:
1. Push this to a GitHub repo
2. Create new Koyeb App → Connect to GitHub
3. Buildpack: Python
4. Run Command:
   ```bash
   python bot.py
