# Bird Call

Bird Call cleans up social-media links in two ways:

- **Discord bot** — watches Discord messages and replies with cleaned, embed-friendly URLs.
- **Clipboard fixer** — a Windows system-tray app that cleans a copied URL before you paste it elsewhere.

Both components share the same cleanup rules, including UTM removal, AMP cleanup, HTTPS upgrades, and embed-friendly replacements for X, TikTok, and Facebook links.

## Discord bot setup

### 1. Create the Discord bot

1. Open the [Discord Developer Portal](https://discord.com/developers/applications) and create an application.
2. Open **Bot**, then create a bot user and copy its token.
3. Under **Privileged Gateway Intents**, enable **Message Content Intent**. The bot cannot read message URLs without it.
4. Use **OAuth2 → URL Generator** to invite the bot with the `bot` scope.

Grant these server/channel permissions:

- View Channels
- Send Messages
- Embed Links
- Read Message History

**Manage Messages** is optional, but required when `suppress_original_embeds` is enabled or when `delete_original` is enabled in the bot configuration.

Never commit the bot token. Treat it like a password.

### 2. Configure it

From the repository root:

```powershell
cd discord-bot
Copy-Item .env.example .env
Copy-Item config.example.json config.json
```

Set the bot token in `.env`:

```text
DISCORD_BOT_TOKEN=replace-with-your-bot-token
```

Use `config.json` to control replies:

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

Leave `watched_channel_ids` empty to monitor every channel the bot can access. To limit it to specific channels, enable Discord Developer Mode, right-click a channel, choose **Copy Channel ID**, and add the IDs to that array.

### 3. Run with Docker (recommended)

With Docker Desktop running, from `discord-bot` run:

```powershell
docker compose up -d --build
```

Check that it connected successfully:

```powershell
docker compose logs -f bird-call-bot
```

Stop the bot:

```powershell
docker compose down
```

The Compose configuration restarts the bot automatically unless it is explicitly stopped and rotates its container logs.

### Run from source

```powershell
cd discord-bot
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python bot.py
```

Run the bot tests with `python -m unittest` from `discord-bot`.

## Clipboard fixer

Download the current Windows executable from [GitHub Releases](https://github.com/MMajor87/Bird-Call/releases), or build it from source:

```powershell
cd clipboard-fixer
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\build.ps1
```

The versioned executable is written to `clipboard-fixer\dist`.

## TikTok share links

TikTok short links such as `vm.tiktok.com`, `vt.tiktok.com`, and `tiktok.com/t/...` are expanded to their canonical TikTok video URLs before they are converted to TNKTOK. This avoids TNKTOK short-link routes that can return an internal-server error.

## Configuration and security

- `.env` and `config.json` are local runtime files and should not be committed.
- Keep `delete_original` disabled unless the bot is intended to moderate messages.
- Enable only the cleanup rules you want under `enabled_rules`.
