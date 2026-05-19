# Bird Call Discord Bot

A Discord bot that watches server messages for dirty URLs and replies with cleaned versions.

This is separate from the `clipboard-fixer` desktop app. It has its own entry point, config, dependencies, and tests.

## What It Cleans

- UTM tracking parameters
- AMP suffixes and `amp` query params
- `x.com` links to `vxtwitter.com`
- `tiktok.com` links to `tnktok.com`
- `facebook.com` links to `fixacebook.com`
- Facebook redirect wrappers
- Google redirect wrappers
- `http://` links to `https://`

## Discord Setup

1. Create a Discord application and bot in the Discord Developer Portal.
2. Enable the **Message Content Intent** for the bot.
3. Invite the bot to your server with permissions to:
   - View Channels
   - Read Message History
   - Send Messages
   - Use External Emojis is not required
   - Manage Messages is optional, only needed for embed suppression or deleting original messages

## Local Setup

```powershell
cd discord-bot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
Copy-Item config.example.json config.json
```

Edit `.env` and set:

```text
DISCORD_BOT_TOKEN=your-token-here
```

Then run:

```powershell
python bot.py
```

## Docker Setup

From `discord-bot`:

```powershell
Copy-Item .env.example .env
Copy-Item config.example.json config.json
```

Edit `.env` and set:

```text
DISCORD_BOT_TOKEN=your-token-here
```

Build and run with Docker:

```powershell
docker build -t bird-call-bot .
docker run --rm --name bird-call-bot --env-file .env -v ${PWD}/config.json:/app/config.json:ro bird-call-bot
```

Or with Docker Compose:

```powershell
docker compose up -d --build
```

To stop:

```powershell
docker compose down
```

## Config

`config.json` controls the bot:

```json
{
  "reply_prefix": "Cleaned link:",
  "delete_original": false,
  "suppress_original_embeds": true,
  "watched_channel_ids": [],
  "enabled_rules": {
    "strip_utm": true,
    "remove_amp": true,
    "x_to_vxtwitter": true,
    "tiktok_to_tnktok": true,
    "facebook_to_fixacebook": true,
    "unwrap_facebook": true,
    "unwrap_google": true,
    "force_https": true
  }
}
```

Leave `watched_channel_ids` empty to watch every channel the bot can read. Add channel IDs to limit where it replies.

`suppress_original_embeds` tries to hide embeds on the original dirty-link message. It needs Manage Messages permission.

`delete_original` deletes the original message after replying. Keep this off unless you really want moderation-style behavior.

## Tests

```powershell
python -m unittest
```
