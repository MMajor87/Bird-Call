import os
import sys

_APP_NAME = "ClipboardLinkCorrector"

if sys.platform == "win32":
    import winreg

    _RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

    def _command() -> str:
        if getattr(sys, "frozen", False):
            # Running as a PyInstaller bundle — the exe is self-contained
            return f'"{sys.executable}"'
        # Running from source — use pythonw.exe so no console window appears
        pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
        main_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
        return f'"{pythonw}" "{main_py}"'

    def is_enabled() -> bool:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, _APP_NAME)
            winreg.CloseKey(key)
            return True
        except OSError:
            return False

    def enable() -> None:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, _APP_NAME, 0, winreg.REG_SZ, _command())
        winreg.CloseKey(key)

    def disable() -> None:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, _APP_NAME)
            winreg.CloseKey(key)
        except OSError:
            pass

else:
    def is_enabled() -> bool:
        return False

    def enable() -> None:
        pass

    def disable() -> None:
        pass
