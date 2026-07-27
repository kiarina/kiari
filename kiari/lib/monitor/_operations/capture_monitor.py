from PIL import Image

from .._schemas.monitor_snapshot import MonitorSnapshot
from .._schemas.multiple_monitor_capture import MultipleMonitorCapture
from .._schemas.point import Point
from .._schemas.rect import Rect
from .._schemas.size import Size


def capture_monitor() -> MultipleMonitorCapture:
    import mss

    with mss.mss() as sct:
        monitors = [
            MonitorSnapshot(
                index=i,
                bounds=Rect(
                    origin=Point(
                        x=monitor["left"],
                        y=monitor["top"],
                    ),
                    size=Size(
                        width=monitor["width"],
                        height=monitor["height"],
                    ),
                ),
            )
            for i, monitor in enumerate(sct.monitors)
        ]

        screenshot = sct.grab(sct.monitors[0])
        image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

        return MultipleMonitorCapture(
            monitor_snapshots=monitors,
            full_desktop_screenshot=image,
        )
