# Clipboard Link Corrector — Build Checklist

## Phase 1: Project Setup

- [ ] Create a project folder, e.g. `clipboard-fixer/`
- [ ] Create and activate a Python virtual environment inside it: `python -m venv .venv && source .venv/bin/activate`
- [ ] Install dependencies: `pip install PyQt6`
- [ ] Create the main entry point file: `main.py`
- [ ] Create a `rules.py` file where link correction logic will live
- [ ] Create a `config.py` file to hold user preferences (e.g. which rules are enabled)
- [ ] Create a `README.md` describing what the app does and how to run it

---

## Phase 2: Core Application Shell

- [ ] In `main.py`, import `QApplication`, `QSystemTrayIcon`, `QMenu`, and `QClipboard` from PyQt6
- [ ] Instantiate `QApplication` with `sys.argv` and set `app.setQuitOnLastWindowClosed(False)` so the app stays alive with no visible windows
- [ ] Create a `ClipboardWatcher` class that inherits from `QObject`
- [ ] In `ClipboardWatcher.__init__`, grab the clipboard via `QApplication.clipboard()`
- [ ] Connect `clipboard.dataChanged` signal to a handler method (e.g. `on_clipboard_changed`)
- [ ] Verify the event loop runs and the `dataChanged` signal fires by printing to console when you copy anything

---

## Phase 3: Tray Icon

- [ ] Create a `TrayIcon` class that inherits from `QSystemTrayIcon`
- [ ] Supply a 16x16 or 32x32 PNG icon file in the project folder and load it with `QIcon`
- [ ] Build a right-click `QMenu` with at minimum: "Pause / Resume", "Settings", "Quit"
- [ ] Wire "Quit" to `QApplication.quit()`
- [ ] Wire "Pause / Resume" to a boolean flag on `ClipboardWatcher` that skips processing when paused
- [ ] Call `tray.show()` to make it visible in the system tray
- [ ] Confirm the tray icon appears and the menu opens correctly

---

## Phase 4: Link Detection

- [ ] In `on_clipboard_changed`, call `clipboard.text()` to get the current clipboard string
- [ ] Write a helper function `is_link(text: str) -> bool` using a regex or `urllib.parse.urlparse` to detect URLs
- [ ] Guard the handler: only proceed if `is_link(text)` returns `True`
- [ ] Log detected links to the console for now to confirm detection works

---

## Phase 5: Correction Rules Engine

- [ ] In `rules.py`, define a `Rule` dataclass or namedtuple with fields: `name`, `enabled`, `apply(url: str) -> str`
- [ ] Implement the rules you want — common ones to start with:
  - [ ] Strip UTM tracking parameters (`utm_source`, `utm_medium`, `utm_campaign`, etc.)
  - [ ] Remove AMP suffixes (`/amp`, `?amp=1`)
  - [ ] Replace `x.com` with `vxtwitter.com` in any copied link — match the full domain only (i.e. `x.com/` or `www.x.com/`) so substrings like `box.com` are not affected; preserve the entire path, query string, and fragment exactly as-is so the link stays functional
  - [ ] Strip Facebook redirect wrappers (`l.facebook.com/l.php?u=...`)
  - [ ] Unwrap Google redirect URLs (`google.com/url?q=...`)
  - [ ] Force HTTPS on HTTP links
- [ ] Write a `clean_url(url: str, rules: list[Rule]) -> str` function that runs the URL through each enabled rule in sequence
- [ ] Write unit tests in `test_rules.py` using `unittest` or `pytest` covering each rule with a before/after URL pair

---

## Phase 6: Applying Corrections

- [ ] In `on_clipboard_changed`, after detecting a link, pass it through `clean_url()`
- [ ] Compare the result to the original — if they differ, call `clipboard.setText(cleaned_url)` to replace it
- [ ] Guard against infinite loops: the `setText` call will itself fire `dataChanged`. Set a flag (e.g. `self._setting = True`) before writing, check it at the top of the handler, and clear it immediately after
- [ ] Show a tray notification via `QSystemTrayIcon.showMessage()` when a correction is made, displaying the original vs cleaned URL

---

## Phase 7: Settings UI (Optional but Recommended)

- [ ] Create a `settings_dialog.py` with a `QDialog` subclass
- [ ] Add a `QListWidget` or table of checkboxes, one per rule, so the user can toggle rules on/off
- [ ] Persist settings to a JSON file in the user's config directory (use `QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)`)
- [ ] Load settings on startup in `config.py` and apply them when building the rules list
- [ ] Wire the "Settings" tray menu item to open this dialog

---

## Phase 8: Auto-Start on Login

- [ ] **macOS**: Create a `LaunchAgent` plist at `~/Library/LaunchAgents/com.yourname.clipboardfixer.plist` pointing to the Python executable and `main.py`
- [ ] **Windows**: Add a registry entry under `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` or create a shortcut in the Startup folder
- [ ] **Linux (systemd)**: Create a `~/.config/systemd/user/clipboard-fixer.service` unit file and enable it with `systemctl --user enable --now clipboard-fixer`
- [ ] Test that the app starts automatically after a reboot and appears in the tray

---

## Phase 9: Packaging (Optional)

- [ ] Add a `requirements.txt` by running `pip freeze > requirements.txt`
- [ ] Install `pyinstaller`: `pip install pyinstaller`
- [ ] Run `pyinstaller --onefile --windowed --icon=icon.png main.py` to produce a standalone binary
- [ ] Test the binary on a clean machine (or clean virtualenv) to confirm no missing dependencies
- [ ] Write a short install section in `README.md` covering both "run from source" and "use the binary" paths
