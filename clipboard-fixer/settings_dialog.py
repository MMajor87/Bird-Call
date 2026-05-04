from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox, QLabel, QFrame
)

import autostart
from config import save_config

_RULE_LABELS: dict[str, str] = {
    "strip_utm":           "Strip UTM tracking parameters",
    "remove_amp":          "Remove AMP suffixes",
    "x_to_vxtwitter":      "Replace x.com with vxtwitter.com",
    "tiktok_to_tnktok":    "Replace tiktok.com with tnktok.com",
    "facebook_to_facebed": "Replace facebook.com with facebed.com",
    "unwrap_facebook":     "Unwrap Facebook redirect links",
    "unwrap_google":       "Unwrap Google redirect links",
    "force_https":         "Force HTTPS on HTTP links",
}


class SettingsDialog(QDialog):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Clipboard Link Corrector — Settings")
        self._config = config

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Enable / disable correction rules:"))
        self._checkboxes: dict[str, QCheckBox] = {}
        enabled = config.get("enabled_rules", {})
        for key, label in _RULE_LABELS.items():
            cb = QCheckBox(label)
            cb.setChecked(enabled.get(key, True))
            self._checkboxes[key] = cb
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
