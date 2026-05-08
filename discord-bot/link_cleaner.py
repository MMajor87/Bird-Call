import re
import urllib.parse

from rules import Rule, clean_url


URL_PATTERN = re.compile(r"https?://[^\s<>()]+", re.IGNORECASE)
TRAILING_PUNCTUATION = ".,!?;:"


def _trim_trailing_punctuation(url: str) -> tuple[str, str]:
    suffix = ""
    while url and url[-1] in TRAILING_PUNCTUATION:
        suffix = url[-1] + suffix
        url = url[:-1]
    return url, suffix


def is_link(text: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(text.strip())
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except ValueError:
        return False


def find_cleaned_links(message: str, rules: list[Rule]) -> list[tuple[str, str]]:
    cleaned_links: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for match in URL_PATTERN.finditer(message):
        original, suffix = _trim_trailing_punctuation(match.group(0))
        if not is_link(original):
            continue

        cleaned = clean_url(original, rules)
        if cleaned == original:
            continue

        pair = (original + suffix, cleaned + suffix)
        if pair not in seen:
            seen.add(pair)
            cleaned_links.append(pair)

    return cleaned_links
