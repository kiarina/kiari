import sys

from .._types.keyboard_key import KeyboardKey
from .._utils.normalize_key import normalize_key
from .._utils.normalize_keys import normalize_keys


class Keyboard:
    def __init__(self) -> None:
        self._hotkey_initialized: bool = False
        """
        Whether hotkey initialization has been completed
        """

    def press(self, key: KeyboardKey) -> None:
        """
        Press and release a single key
        """
        import pyautogui

        pyautogui.press(normalize_key(key))

        self._hotkey_initialized = True

    def hotkey(self, *keys: KeyboardKey) -> None:
        """
        Press a hotkey combination

        Args:
            *keys: List of keys to press simultaneously (e.g., "command", "c")
        """
        import pyautogui

        if not self._hotkey_initialized:
            pyautogui.press("esc")

            self._hotkey_initialized = True

        pyautogui.hotkey(*normalize_keys(keys))

    def write(self, text: str) -> None:
        """
        Input text

        Uses clipboard for input, supporting multilingual text including Japanese.
        """
        import pyperclip  # type: ignore

        # Save current clipboard contents
        old_clipboard = pyperclip.paste()

        try:
            # Copy the text to input to clipboard
            pyperclip.copy(text)

            # Use different paste hotkeys depending on OS
            if sys.platform == "darwin":  # macOS
                self.hotkey("command", "v")
            else:  # Windows/Linux
                self.hotkey("ctrl", "v")

        finally:
            # Restore clipboard contents
            pyperclip.copy(old_clipboard)
