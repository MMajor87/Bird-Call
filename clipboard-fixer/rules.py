from dataclasses import dataclass, field
from typing import Callable
import re
import urllib.parse


@dataclass
class Rule:
    name: str
    enabled: bool
    apply: Callable[[str], str] = field(repr=False)


def _strip_utm(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    utm_keys = [k for k in params if k.startswith("utm_")]
    for k in utm_keys:
        del params[k]
    new_query = urllib.parse.urlencode(params, doseq=True)
    return parsed._replace(query=new_query).geturl()


def _remove_amp(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    path = re.sub(r"/amp/?$", "", parsed.path)
    params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    params.pop("amp", None)
    new_query = urllib.parse.urlencode(params, doseq=True)
    return parsed._replace(path=path, query=new_query).geturl()


def _x_to_vxtwitter(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower()
    if host == "x.com" or host == "www.x.com":
        new_host = "vxtwitter.com"
        return parsed._replace(netloc=new_host).geturl()
    return url


def _unwrap_facebook(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc in ("l.facebook.com",) and parsed.path == "/l.php":
        params = urllib.parse.parse_qs(parsed.query)
        inner = params.get("u", [None])[0]
        if inner:
            return urllib.parse.unquote(inner)
    return url


def _unwrap_google(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if "google." in parsed.netloc and parsed.path == "/url":
        params = urllib.parse.parse_qs(parsed.query)
        inner = params.get("q", [None])[0]
        if inner:
            return inner
    return url


def _force_https(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme == "http":
        return parsed._replace(scheme="https").geturl()
    return url


def get_default_rules(config: dict) -> list[Rule]:
    enabled = config.get("enabled_rules", {})
    return [
        Rule("strip_utm", enabled.get("strip_utm", True), _strip_utm),
        Rule("remove_amp", enabled.get("remove_amp", True), _remove_amp),
        Rule("x_to_vxtwitter", enabled.get("x_to_vxtwitter", True), _x_to_vxtwitter),
        Rule("unwrap_facebook", enabled.get("unwrap_facebook", True), _unwrap_facebook),
        Rule("unwrap_google", enabled.get("unwrap_google", True), _unwrap_google),
        Rule("force_https", enabled.get("force_https", True), _force_https),
    ]


def clean_url(url: str, rules: list[Rule]) -> str:
    for rule in rules:
        if rule.enabled:
            url = rule.apply(url)
    return url
