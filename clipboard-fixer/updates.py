from dataclasses import dataclass
import json
import urllib.error
import urllib.request

from packaging.version import InvalidVersion, Version


LATEST_RELEASE_API = "https://api.github.com/repos/MMajor87/Bird-Call/releases/latest"
RELEASES_PAGE = "https://github.com/MMajor87/Bird-Call/releases"


@dataclass(frozen=True)
class Release:
    version: Version
    url: str


def get_latest_release() -> Release | None:
    request = urllib.request.Request(
        LATEST_RELEASE_API,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "BirdCall"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.load(response)
        version = Version(data["tag_name"].lstrip("v"))
    except (KeyError, json.JSONDecodeError, urllib.error.URLError, TimeoutError, InvalidVersion):
        return None

    return Release(version=version, url=data.get("html_url", RELEASES_PAGE))


def is_newer_release(release: Release, current_version: str) -> bool:
    return release.version > Version(current_version)
