# Clipboard Link Corrector — Build Checklist

## Phase 1: Project Setup

- [x] Create a project folder, e.g. `clipboard-fixer/`
- [x] Create and activate a Python virtual environment inside it: `python -m venv .venv && source .venv/bin/activate`
- [x] Install dependencies: `pip install PyQt6`
- [x] Create the main entry point file: `main.py`
- [x] Create a `rules.py` file where link correction logic will live
- [x] Create a `config.py` file to hold user preferences (e.g. which rules are enabled)
- [x] Create a `README.md` describing what the app does and how to run it

---

## Phase 2: Core Application Shell

- [x] In `main.py`, import `QApplication`, `QSystemTrayIcon`, `QMenu`, and `QClipboard` from PyQt6
- [x] Instantiate `QApplication` with `sys.argv` and set `app.setQuitOnLastWindowClosed(False)` so the app stays alive with no visible windows
- [x] Create a `ClipboardWatcher` class that inherits from `QObject`
- [x] In `ClipboardWatcher.__init__`, grab the clipboard via `QApplication.clipboard()`
- [x] Connect `clipboard.dataChanged` signal to a handler method (e.g. `on_clipboard_changed`)
- [x] Verify the event loop runs and the `dataChanged` signal fires by printing to console when you copy anything

---

## Phase 3: Tray Icon

- [x] Create a `TrayIcon` class that inherits from `QSystemTrayIcon`
- [x] Supply a 16x16 or 32x32 PNG icon file in the project folder and load it with `QIcon`
- [x] Build a right-click `QMenu` with at minimum: "Pause / Resume", "Settings", "Quit"
- [x] Wire "Quit" to `QApplication.quit()`
- [x] Wire "Pause / Resume" to a boolean flag on `ClipboardWatcher` that skips processing when paused
- [x] Call `tray.show()` to make it visible in the system tray
- [x] Confirm the tray icon appears and the menu opens correctly

---

## Phase 4: Link Detection

- [x] In `on_clipboard_changed`, call `clipboard.text()` to get the current clipboard string
- [x] Write a helper function `is_link(text: str) -> bool` using a regex or `urllib.parse.urlparse` to detect URLs
- [x] Guard the handler: only proceed if `is_link(text)` returns `True`
- [x] Log detected links to the console for now to confirm detection works

---

## Phase 5: Correction Rules Engine

- [x] In `rules.py`, define a `Rule` dataclass or namedtuple with fields: `name`, `enabled`, `apply(url: str) -> str`
- [x] Implement the rules you want — common ones to start with:
  - [x] Strip UTM tracking parameters (`utm_source`, `utm_medium`, `utm_campaign`, etc.)
  - [x] Remove AMP suffixes (`/amp`, `?amp=1`)
  - [x] Replace `x.com` with `vxtwitter.com` in any copied link — match the full domain only (i.e. `x.com/` or `www.x.com/`) so substrings like `box.com` are not affected; preserve the entire path, query string, and fragment exactly as-is so the link stays functional
  - [x] Strip Facebook redirect wrappers (`l.facebook.com/l.php?u=...`)
  - [x] Unwrap Google redirect URLs (`google.com/url?q=...`)
  - [x] Force HTTPS on HTTP links
- [x] Write a `clean_url(url: str, rules: list[Rule]) -> str` function that runs the URL through each enabled rule in sequence
- [x] Write unit tests in `test_rules.py` using `unittest` or `pytest` covering each rule with a before/after URL pair

---

## Phase 6: Applying Corrections

- [x] In `on_clipboard_changed`, after detecting a link, pass it through `clean_url()`
- [x] Compare the result to the original — if they differ, call `clipboard.setText(cleaned_url)` to replace it
- [x] Guard against infinite loops: the `setText` call will itself fire `dataChanged`. Set a flag (e.g. `self._setting = True`) before writing, check it at the top of the handler, and clear it immediately after
- [x] Show a tray notification via `QSystemTrayIcon.showMessage()` when a correction is made, displaying the original vs cleaned URL

---

## Phase 7: Correction History Log

- [x] In `ClipboardWatcher`, add a `collections.deque(maxlen=10)` to store recent corrections; each entry is a `(original_url, cleaned_url)` tuple
- [x] After a correction is applied in `on_clipboard_changed`, append the pair to the deque
- [x] In `TrayIcon`, add a "Recent Corrections" submenu to the context menu
- [x] Connect the submenu's `aboutToShow` signal to a method that rebuilds its entries from the deque each time it opens
- [x] Each entry should display a truncated form of the cleaned URL; clicking it copies that cleaned URL back to the clipboard
- [x] When the deque is empty, show a single disabled "No corrections yet" placeholder item

---

## Phase 8: Settings UI (Optional but Recommended)

- [x] Create a `settings_dialog.py` with a `QDialog` subclass
- [x] Add a `QListWidget` or table of checkboxes, one per rule, so the user can toggle rules on/off
- [x] Persist settings to a JSON file in the user's config directory (use `QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)`)
- [x] Load settings on startup in `config.py` and apply them when building the rules list
- [x] Wire the "Settings" tray menu item to open this dialog

---

## Phase 9: Auto-Start on Login

- [ ] **macOS**: Create a `LaunchAgent` plist at `~/Library/LaunchAgents/com.yourname.clipboardfixer.plist` pointing to the Python executable and `main.py`
- [x] **Windows**: Add a registry entry under `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` or create a shortcut in the Startup folder
- [ ] **Linux (systemd)**: Create a `~/.config/systemd/user/clipboard-fixer.service` unit file and enable it with `systemctl --user enable --now clipboard-fixer`
- [ ] Test that the app starts automatically after a reboot and appears in the tray

---

## Phase 10: Packaging (Optional)

- [x] Add a `requirements.txt` by running `pip freeze > requirements.txt`
- [x] Install `pyinstaller`: `pip install pyinstaller`
- [x] Run `pyinstaller --onefile --windowed --icon=icon.png main.py` to produce a standalone binary
- [ ] Test the binary on a clean machine (or clean virtualenv) to confirm no missing dependencies
- [x] Write a short install section in `README.md` covering both "run from source" and "use the binary" paths
