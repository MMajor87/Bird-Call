# Clipboard Link Corrector

A lightweight system-tray app that watches your clipboard and automatically cleans up URLs as you copy them.

## What it does

Every time you copy a link, the app silently fixes common annoyances:

| Rule | Example |
|------|---------|
| Strip UTM tracking params | `example.com?utm_source=twitter` → `example.com` |
| Remove AMP suffixes | `example.com/article/amp` → `example.com/article` |
| Replace `x.com` with `vxtwitter.com` | `x.com/user/status/123` → `vxtwitter.com/user/status/123` |
| Unwrap Facebook redirects | `l.facebook.com/l.php?u=https://...` → the real URL |
| Unwrap Google redirects | `google.com/url?q=https://...` → the real URL |
| Force HTTPS | `http://example.com` → `https://example.com` |

## Requirements

- Python 3.10+
- PyQt6

## Run from source

```bash
# 1. Clone / download this folder
cd clipboard-fixer

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install PyQt6

# 4. Launch
python main.py
```

The app runs silently in the background. Look for its icon in your system tray.

## Configuration

Rules can be toggled on/off in `config.json` (created automatically on first run) or through the Settings dialog in the tray menu (available in a later phase).

```json
{
  "enabled_rules": {
    "strip_utm": true,
    "remove_amp": true,
    "x_to_vxtwitter": true,
    "unwrap_facebook": true,
    "unwrap_google": true,
    "force_https": true
  }
}
```
