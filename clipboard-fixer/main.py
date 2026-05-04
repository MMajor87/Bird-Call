import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject

from rules import clean_url, get_default_rules
from config import load_config


class ClipboardWatcher(QObject):
    def __init__(self, rules):
        super().__init__()
        self.rules = rules
        self._setting = False
        self.paused = False
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_changed)

    def on_clipboard_changed(self):
        if self._setting or self.paused:
            return
        text = self.clipboard.text()
        if not text:
            return
        print(f"Clipboard changed: {text[:80]}")


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = load_config()
    rules = get_default_rules(config)
    watcher = ClipboardWatcher(rules)  # noqa: F841 — must stay alive

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
