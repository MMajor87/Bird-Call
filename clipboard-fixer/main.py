import collections
import os
import sys
import urllib.parse
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction, QClipboard, QIcon
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from rules import clean_url, get_default_rules
from config import load_config
from settings_dialog import SettingsDialog


def _resource_path(filename: str) -> str:
    # PyInstaller extracts bundled files to sys._MEIPASS at runtime
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)


def _make_icon() -> QIcon:
    return QIcon(_resource_path("BlueJay.png"))


def is_link(text: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(text.strip())
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except ValueError:
        return False


class ClipboardWatcher(QObject):
    corrected = pyqtSignal(str, str)  # (original_url, cleaned_url)

    def __init__(self, rules):
        super().__init__()
        self.rules = rules
        self._setting = False
        self.paused = False
        self.history: collections.deque[tuple[str, str]] = collections.deque(maxlen=10)
        self._history_dirty = True  # ensures first menu open always renders
        clipboard = QApplication.clipboard()
        assert clipboard is not None
        self.clipboard: QClipboard = clipboard
        self.clipboard.dataChanged.connect(self.on_clipboard_changed)

    def on_clipboard_changed(self):
        if self._setting or self.paused:
            return
        text = self.clipboard.text().strip()
        if not text or not is_link(text):
            return
        cleaned = clean_url(text, self.rules)
        if cleaned == text:
            return
        # Defer the write to the next event loop tick.  On Windows, calling
        # setText() synchronously inside a dataChanged handler is discarded
        # because Qt hasn't finished processing the original clipboard event.
        QTimer.singleShot(0, lambda: self._apply_correction(text, cleaned))

    def _apply_correction(self, original: str, cleaned: str):
        self._setting = True
        self.clipboard.setText(cleaned)
        self._setting = False
        self.history.append((original, cleaned))
        self._history_dirty = True
        print(f"Corrected: {original[:80]} -> {cleaned[:80]}")
        self.corrected.emit(original, cleaned)


class TrayIcon(QSystemTrayIcon):
    def __init__(self, watcher: ClipboardWatcher, parent=None):
        super().__init__(_make_icon(), parent)
        self._watcher = watcher
        watcher.corrected.connect(self._on_corrected)

        menu = QMenu()

        pause_action = menu.addAction("Pause")
        assert pause_action is not None
        self._pause_action: QAction = pause_action
        self._pause_action.triggered.connect(self._toggle_pause)

        history_menu = menu.addMenu("Recent Corrections")
        assert history_menu is not None
        self._history_menu: QMenu = history_menu
        self._history_menu.aboutToShow.connect(self._rebuild_history_menu)

        settings_action = menu.addAction("Settings")
        assert settings_action is not None
        settings_action.triggered.connect(self._open_settings)

        menu.addSeparator()

        quit_action = menu.addAction("Quit")
        assert quit_action is not None
        quit_action.triggered.connect(QApplication.quit)

        self.setContextMenu(menu)
        self.setToolTip("Clipboard Link Corrector")

    def _toggle_pause(self):
        self._watcher.paused = not self._watcher.paused
        self._pause_action.setText("Resume" if self._watcher.paused else "Pause")

    def _open_settings(self):
        dialog = SettingsDialog(load_config(), parent=None)
        if dialog.exec():
            self._watcher.rules = get_default_rules(load_config())

    def _rebuild_history_menu(self):
        if not self._watcher._history_dirty:
            return
        self._watcher._history_dirty = False
        self._history_menu.clear()
        if not self._watcher.history:
            placeholder = self._history_menu.addAction("No corrections yet")
            assert placeholder is not None
            placeholder.setEnabled(False)
            return
        clipboard = QApplication.clipboard()
        assert clipboard is not None
        for _, cleaned in reversed(self._watcher.history):
            label = cleaned[:70] + ("…" if len(cleaned) > 70 else "")
            action = self._history_menu.addAction(label)
            assert action is not None
            action.triggered.connect(lambda checked, url=cleaned, cb=clipboard: cb.setText(url))

    def _on_corrected(self, original: str, cleaned: str):
        self.showMessage(
            "Link Corrected",
            f"Before: {original[:70]}\nAfter:   {cleaned[:70]}",
            QSystemTrayIcon.MessageIcon.Information,
            4000,
        )


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("clipboard-fixer")
    app.setQuitOnLastWindowClosed(False)

    config = load_config()
    rules = get_default_rules(config)
    watcher = ClipboardWatcher(rules)

    tray = TrayIcon(watcher)
    tray.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
