import json
import os

from PyQt6.QtCore import QStandardPaths

_DEFAULTS = {
    "enabled_rules": {
        "strip_utm": True,
        "remove_amp": True,
        "x_to_vxtwitter": True,
        "tiktok_to_tnktok": True,
        "facebook_to_facebed": True,
        "unwrap_facebook": True,
        "unwrap_google": True,
        "force_https": True,
    }
}


def _config_path() -> str:
    config_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "config.json")


def load_config() -> dict:
    path = _config_path()
    if not os.path.exists(path):
        return dict(_DEFAULTS)
    try:
        with open(path) as f:
            data = json.load(f)
        merged = dict(_DEFAULTS)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(_DEFAULTS)


def save_config(config: dict) -> None:
    with open(_config_path(), "w") as f:
        json.dump(config, f, indent=2)
