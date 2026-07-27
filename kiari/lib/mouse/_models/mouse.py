from kiari.lib.monitor import Monitor

from .._types.mouse_button import MouseButton


class Mouse:
    def __init__(self, monitor: Monitor) -> None:
        self._monitor: Monitor = monitor
        self._pressed_button: MouseButton | None = None

    def move(self, monitor_index: int, x: int, y: int, duration: float = 0.0) -> None:
        import pyautogui

        monitor_info = self._monitor.get_monitor_info(monitor_index)

        screen_x = x / monitor_info.scale_ratio / self._monitor.scale_factor
        screen_y = y / monitor_info.scale_ratio / self._monitor.scale_factor

        screen_x -= monitor_info.offset_vector.x
        screen_y -= monitor_info.offset_vector.y

        if self._pressed_button:
            # Drag operation
            pyautogui._mouseMoveDrag(  # type: ignore
                "drag", screen_x, screen_y, 0, 0, duration, button=self._pressed_button
            )

        else:
            # Normal move
            pyautogui.moveTo(screen_x, screen_y, duration=duration, _pause=False)

    def click(self, button: MouseButton = "left") -> None:
        import pyautogui

        pyautogui.click(button=button)

    def down(self, button: MouseButton = "left") -> None:
        import pyautogui

        pyautogui.mouseDown(button=button, _pause=False)
        self._pressed_button = button

    def up(self) -> None:
        import pyautogui

        if self._pressed_button is None:
            return

        pyautogui.mouseUp(button=self._pressed_button, _pause=False)
        self._pressed_button = None
