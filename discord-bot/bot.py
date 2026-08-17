import logging
import os
import re
import urllib.parse

import aiohttp
import discord
from dotenv import load_dotenv

from config import load_config
from link_cleaner import (
    TRAILING_PUNCTUATION,
    URL_PATTERN,
    find_cleaned_links,
    is_tiktok_redirect_url,
)
from rules import get_default_rules


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("bird-call-bot")
MAX_DISCORD_MESSAGE_LENGTH = 2000
TIKTOK_REDIRECT_TIMEOUT_SECONDS = 10


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


async def _expand_tiktok_redirects(message_content: str) -> str:
    """Expand TikTok short links before converting them to TNKTOK URLs."""
    candidates: list[tuple[re.Match[str], str, str]] = []
    for match in URL_PATTERN.finditer(message_content):
        url = match.group(0)
        suffix = ""
        while url and url[-1] in TRAILING_PUNCTUATION:
            suffix = url[-1] + suffix
            url = url[:-1]
        if is_tiktok_redirect_url(url):
            candidates.append((match, url, suffix))

    if not candidates:
        return message_content

    timeout = aiohttp.ClientTimeout(total=TIKTOK_REDIRECT_TIMEOUT_SECONDS)
    replacements: dict[tuple[int, int], str] = {}
    headers = {"User-Agent": "Mozilla/5.0 (compatible; BirdCall/1.0)"}
    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        for match, url, suffix in candidates:
            try:
                async with session.get(url, allow_redirects=True, max_redirects=5) as response:
                    resolved = str(response.url)
            except (aiohttp.ClientError, TimeoutError):
                LOGGER.warning("Could not expand TikTok redirect URL: %s", url)
                continue

            parsed = urllib.parse.urlparse(resolved)
            if parsed.netloc.lower() not in ("tiktok.com", "www.tiktok.com"):
                LOGGER.warning("TikTok redirect resolved to an unexpected host: %s", resolved)
                continue
            canonical_url = parsed._replace(query="", fragment="").geturl()
            replacements[(match.start(), match.end())] = canonical_url + suffix

    if not replacements:
        return message_content

    parts: list[str] = []
    cursor = 0
    for (start, end), replacement in replacements.items():
        parts.extend((message_content[cursor:start], replacement))
        cursor = end
    parts.append(message_content[cursor:])
    return "".join(parts)


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
        guild_names = ", ".join(f"{guild.name} ({guild.id})" for guild in self.guilds) or "none"
        LOGGER.info("Connected guilds: %s", guild_names)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if self.watched_channel_ids and message.channel.id not in self.watched_channel_ids:
            LOGGER.info(
                "Ignoring message in channel %s because it is not in watched_channel_ids",
                message.channel.id,
            )
            return

        LOGGER.info("Received message %s in channel %s", message.id, message.channel.id)
        expanded_content = await _expand_tiktok_redirects(message.content)
        cleaned_links = find_cleaned_links(expanded_content, self.rules)
        if not cleaned_links:
            LOGGER.info("No cleanable links found in message %s", message.id)
            return

        LOGGER.info("Found %s cleanable link(s) in message %s", len(cleaned_links), message.id)
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
