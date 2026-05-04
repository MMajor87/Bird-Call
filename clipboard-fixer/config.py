import json
import os

_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

_DEFAULTS = {
    "enabled_rules": {
        "strip_utm": True,
        "remove_amp": True,
        "x_to_vxtwitter": True,
        "unwrap_facebook": True,
        "unwrap_google": True,
        "force_https": True,
    }
}


def load_config() -> dict:
    if not os.path.exists(_CONFIG_FILE):
        return dict(_DEFAULTS)
    try:
        with open(_CONFIG_FILE) as f:
            data = json.load(f)
        merged = dict(_DEFAULTS)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(_DEFAULTS)


def save_config(config: dict) -> None:
    with open(_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
