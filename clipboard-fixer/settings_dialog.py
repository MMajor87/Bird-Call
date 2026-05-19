from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox, QLabel, QFrame
)
from PyQt6.QtCore import Qt

import autostart
from config import save_config
from rules import get_default_rules
from version import VERSION


class SettingsDialog(QDialog):
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
