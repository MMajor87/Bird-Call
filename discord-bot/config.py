import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "reply_prefix": "Cleaned link:",
    "delete_original": False,
    "suppress_original_embeds": True,
    "watched_channel_ids": [],
    "enabled_rules": {
        "strip_utm": True,
        "remove_amp": True,
        "x_to_vxtwitter": True,
        "tiktok_to_tnktok": True,
        "facebook_to_fixacebook": True,
        "unwrap_facebook": True,
        "unwrap_google": True,
        "force_https": True,
    },
}


def _merge_defaults(data: dict[str, Any]) -> dict[str, Any]:
    merged = dict(DEFAULT_CONFIG)
    merged["enabled_rules"] = dict(DEFAULT_CONFIG["enabled_rules"])
    merged.update(data)
    merged["enabled_rules"].update(data.get("enabled_rules", {}))
    return merged


def load_config(path: str | Path = "config.json") -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        return _merge_defaults({})

    try:
        with config_path.open(encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return _merge_defaults({})

    if not isinstance(data, dict):
        return _merge_defaults({})

    return _merge_defaults(data)
