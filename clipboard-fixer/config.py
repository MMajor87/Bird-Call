import json
import os

from PyQt6.QtCore import QStandardPaths

_DEFAULTS = {
    "enabled_rules": {
        "strip_utm": True,
        "remove_amp": True,
        "x_to_vxtwitter": True,
        "tiktok_to_tnktok": True,
        "facebook_to_fixacebook": True,
        "unwrap_facebook": True,
        "unwrap_google": True,
        "force_https": True,
    }
}


def _config_path() -> str:
    config_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "config.json")


def _merge_defaults(data: dict) -> dict:
    merged = dict(_DEFAULTS)
    merged["enabled_rules"] = dict(_DEFAULTS["enabled_rules"])
    merged.update({k: v for k, v in data.items() if k != "enabled_rules"})
    merged["enabled_rules"].update(data.get("enabled_rules", {}))
    return merged


def load_config() -> dict:
    path = _config_path()
    if not os.path.exists(path):
        return _merge_defaults({})
    try:
        with open(path) as f:
            data = json.load(f)
        return _merge_defaults(data)
    except (json.JSONDecodeError, OSError):
        return _merge_defaults({})


def save_config(config: dict) -> None:
    with open(_config_path(), "w") as f:
        json.dump(config, f, indent=2)
