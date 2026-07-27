from kiari.lib.keyboard import Keyboard
from kiari.lib.monitor import Monitor
from kiari.lib.mouse import Mouse


class GUI:
    def __init__(self) -> None:
        self._monitor: Monitor | None = None
        self._mouse: Mouse | None = None
        self._keyboard: Keyboard | None = None

    @property
    def monitor(self) -> Monitor:
        if self._monitor is None:
            self._monitor = Monitor()

        return self._monitor

    @property
    def mouse(self) -> Mouse:
        if self._mouse is None:
            self._mouse = Mouse(self.monitor)

        return self._mouse

    @property
    def keyboard(self) -> Keyboard:
        if self._keyboard is None:
            self._keyboard = Keyboard()

        return self._keyboard


gui = GUI()
