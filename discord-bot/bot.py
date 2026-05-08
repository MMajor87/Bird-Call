import logging
import os

import discord
from dotenv import load_dotenv

from config import load_config
from link_cleaner import find_cleaned_links
from rules import get_default_rules


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("bird-call-bot")
MAX_DISCORD_MESSAGE_LENGTH = 2000


def _normalize_channel_ids(raw_channel_ids: list[object]) -> set[int]:
    channel_ids: set[int] = set()
    for channel_id in raw_channel_ids:
        try:
            channel_ids.add(int(channel_id))
        except (TypeError, ValueError):
            LOGGER.warning("Ignoring invalid channel id in config: %r", channel_id)
    return channel_ids


def _format_reply(prefix: str, cleaned_links: list[tuple[str, str]]) -> str:
    lines = [prefix]
    lines.extend(cleaned for _, cleaned in cleaned_links)
    reply = "\n".join(lines)
    if len(reply) <= MAX_DISCORD_MESSAGE_LENGTH:
        return reply
    return reply[: MAX_DISCORD_MESSAGE_LENGTH - 3] + "..."


class BirdCallBot(discord.Client):
    def __init__(self, config: dict):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.config = config
        self.rules = get_default_rules(config)
        self.watched_channel_ids = _normalize_channel_ids(config.get("watched_channel_ids", []))

    async def on_ready(self) -> None:
        assert self.user is not None
        LOGGER.info("Logged in as %s (%s)", self.user, self.user.id)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if self.watched_channel_ids and message.channel.id not in self.watched_channel_ids:
            return

        cleaned_links = find_cleaned_links(message.content, self.rules)
        if not cleaned_links:
            return

        if self.config.get("suppress_original_embeds", True):
            try:
                await message.edit(suppress=True)
            except discord.Forbidden:
                LOGGER.info("Missing permission to suppress embeds in channel %s", message.channel.id)
            except discord.HTTPException:
                LOGGER.exception("Failed to suppress embeds for message %s", message.id)

        reply = _format_reply(self.config.get("reply_prefix", "Cleaned link:"), cleaned_links)
        await message.reply(reply, mention_author=False, allowed_mentions=discord.AllowedMentions.none())

        if self.config.get("delete_original", False):
            try:
                await message.delete()
            except discord.Forbidden:
                LOGGER.info("Missing permission to delete messages in channel %s", message.channel.id)
            except discord.HTTPException:
                LOGGER.exception("Failed to delete message %s", message.id)


def main() -> None:
    load_dotenv()
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_BOT_TOKEN is not set. Add it to .env or your environment.")

    bot = BirdCallBot(load_config())
    bot.run(token)


if __name__ == "__main__":
    main()
