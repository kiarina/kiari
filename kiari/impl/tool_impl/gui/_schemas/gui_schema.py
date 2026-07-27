from pydantic import BaseModel, Field

from .._types.action import Action


class GuiSchema(BaseModel):
    """
    Tool for understanding and operating the GUI.

    Uses pyautogui and mss to get monitor information and perform keyboard and mouse operations.

    Supports the following actions:
    - keyboard_press: Press and release a single key
      Required arguments: key
    - keyboard_hotkey: Press multiple keys simultaneously (hotkey)
      Required arguments: keys
    - keyboard_write: Input text
      Required arguments: text
    - mouse_click: Execute a mouse click
      Optional arguments: button, monitor_index, x, y, duration
    - mouse_down: Press down a mouse button
      Optional arguments: button, monitor_index, x, y, duration
    - mouse_move: Move the mouse
      Required arguments: monitor_index, x, y
      Optional arguments: duration
    - mouse_up: Release a mouse button
      Optional arguments: button, monitor_index, x, y, duration
    - screenshot: Take a screenshot
      Required arguments: none
    """

    action: Action = Field(
        description=(
            "GUI action to execute\n\n"
            '- "keyboard_press": Press and release a single key '
            "(Required arguments: key)\n"
            '- "keyboard_hotkey": Press multiple keys simultaneously '
            "(Required arguments: keys)\n"
            '- "keyboard_write": Input text (Required arguments: text)\n'
            '- "mouse_click": Execute a mouse click '
            "(Optional arguments: button, monitor_index, x, y, duration)\n"
            '- "mouse_down": Press down a mouse button '
            "(Optional arguments: button, monitor_index, x, y, duration)\n"
            '- "mouse_move": Move the mouse '
            "(Required arguments: monitor_index, x, y, Optional: duration)\n"
            '- "mouse_up": Release a mouse button '
            "(Optional arguments: button, monitor_index, x, y, duration)\n"
            '- "screenshot": Take a screenshot (Required arguments: none)'
        ),
    )

    # --------------------------------------------------
    # Keyboard related
    # --------------------------------------------------

    key: str = Field(
        default="",
        description=("Key to press with pyautogui.press.\n(For keyboard_press action)"),
    )

    keys: list[str] = Field(
        default_factory=list,
        description=("List of keys to press with pyautogui.hotkey.\n(For keyboard_hotkey action)"),
    )

    text: str = Field(
        default="",
        description="Text to input with keyboard.\n(For keyboard_write action)",
    )

    # --------------------------------------------------
    # Mouse related
    # --------------------------------------------------

    button: str = Field(
        default="left",
        description=("Mouse button ('left' or 'right')\n(For mouse_click, mouse_down actions)"),
    )

    monitor_index: int = Field(
        default=1,
        description=(
            "Monitor index (starting from 1)\n"
            "Used to specify mouse position in multi-monitor environments.\n"
            "Required for mouse_move action.\n"
            "Optional for mouse_click, mouse_down, mouse_up actions."
        ),
    )

    x: int = Field(
        default=-1,
        description=(
            "X coordinate to move the mouse to.\n"
            "Required for mouse_move action.\n"
            "Optional for mouse_click, mouse_down, mouse_up actions."
        ),
    )

    y: int = Field(
        default=-1,
        description=(
            "Y coordinate to move the mouse to.\n"
            "Required for mouse_move action.\n"
            "Optional for mouse_click, mouse_down, mouse_up actions."
        ),
    )

    duration: float = Field(
        default=0.0,
        description=(
            "Time to take for mouse movement (seconds)\n"
            "For mouse_click, mouse_down, mouse_move, mouse_up actions."
        ),
    )
