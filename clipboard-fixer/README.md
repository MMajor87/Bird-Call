# Clipboard Link Corrector

A lightweight system-tray app that watches your clipboard and automatically cleans up URLs as you copy them.

## What it does

Every time you copy a link, the app silently fixes common annoyances:

| Rule | Example |
|------|---------|
| Strip UTM tracking params | `example.com?utm_source=twitter` → `example.com` |
| Remove AMP suffixes | `example.com/article/amp` → `example.com/article` |
| Replace `x.com` with `vxtwitter.com` | `x.com/user/status/123` → `vxtwitter.com/user/status/123` |
| Replace `facebook.com` with `facebed.com` | `facebook.com/reel/123` → `facebed.com/reel/123` |
| Unwrap Facebook redirects | `l.facebook.com/l.php?u=https://...` → the real URL |
| Unwrap Google redirects | `google.com/url?q=https://...` → the real URL |
| Force HTTPS | `http://example.com` → `https://example.com` |

A tray notification appears each time a correction is made. Right-click the tray icon to pause, review recent corrections, or adjust settings.

## Requirements

- Windows 10 / 11
- Python 3.10+ (run from source only)

---

## Option A — Use the binary (recommended)

Download `ClipboardLinkCorrector.exe` from the `dist/` folder and run it directly. No Python or dependencies required.

To start it automatically on login, open **Settings** from the tray icon and check **Start on login**.

---

## Option B — Run from source

```bat
:: 1. Clone / download this folder
cd clipboard-fixer

:: 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

:: 3. Install runtime dependencies
pip install PyQt6

:: 4. Launch
python main.py
```

The app runs silently in the background. Look for its icon in your system tray.

---

## Building the binary yourself

```bat
:: Inside the activated venv
pip install pyinstaller pillow
pyinstaller --onefile --windowed --icon=BlueJay.png --add-data "BlueJay.png;." --name ClipboardLinkCorrector main.py
```

The binary is written to `dist\ClipboardLinkCorrector.exe`.

---

## Configuration

Rules can be toggled on/off through the **Settings** dialog in the tray menu. Settings are saved to:

```
%LOCALAPPDATA%\clipboard-fixer\clipboard-fixer\config.json
```

You can also edit the file directly:

```json
{
  "enabled_rules": {
    "strip_utm": true,
    "remove_amp": true,
    "x_to_vxtwitter": true,
    "facebook_to_facebed": true,
    "unwrap_facebook": true,
    "unwrap_google": true,
    "force_https": true
  }
}
```
