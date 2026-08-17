from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox, QLabel, QFrame, QPushButton
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
import threading

import autostart
from config import save_config
from rules import get_default_rules
from version import VERSION
from updates import get_latest_release, is_newer_release


class SettingsDialog(QDialog):
    update_check_finished = pyqtSignal(object)

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clipboard Link Corrector — Settings")
        self._config = config

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Enable / disable correction rules:"))
        self._checkboxes: dict[str, QCheckBox] = {}
        enabled = config.get("enabled_rules", {})
        for rule in get_default_rules({}):
            cb = QCheckBox(rule.label)
            cb.setChecked(enabled.get(rule.name, True))
            self._checkboxes[rule.name] = cb
            layout.addWidget(cb)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        layout.addWidget(QLabel("General:"))
        self._autostart_cb = QCheckBox("Start on login")
        self._autostart_cb.setChecked(autostart.is_enabled())
        layout.addWidget(self._autostart_cb)

        self._check_updates_button = QPushButton("Check for Updates")
        self._check_updates_button.clicked.connect(self._check_for_updates)
        layout.addWidget(self._check_updates_button)
        self._update_status = QLabel("")
        self._update_status.setWordWrap(True)
        layout.addWidget(self._update_status)
        self.update_check_finished.connect(self._on_update_check_finished)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        version_label = QLabel(f"Bird-Call v{VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        version_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(version_label)

        self.setLayout(layout)
        self.setMinimumWidth(360)

    def _check_for_updates(self):
        self._check_updates_button.setEnabled(False)
        self._update_status.setText("Checking GitHub for updates…")
        threading.Thread(target=self._fetch_latest_release, daemon=True).start()

    def _fetch_latest_release(self):
        self.update_check_finished.emit(get_latest_release())

    def _on_update_check_finished(self, release):
        self._check_updates_button.setEnabled(True)
        if release is None:
            self._update_status.setText("Could not check GitHub for updates. Please try again later.")
        elif is_newer_release(release, VERSION):
            self._update_status.setText(f"Version {release.version} is available. Opening the release page…")
            QDesktopServices.openUrl(QUrl(release.url))
        else:
            self._update_status.setText(f"You are up to date (v{VERSION}).")

    def _save_and_accept(self):
        enabled = self._config.setdefault("enabled_rules", {})
        for key, cb in self._checkboxes.items():
            enabled[key] = cb.isChecked()
        save_config(self._config)

        if self._autostart_cb.isChecked():
            autostart.enable()
        else:
            autostart.disable()

        self.accept()
