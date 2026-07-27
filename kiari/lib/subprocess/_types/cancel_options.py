from typing import NotRequired, TypedDict


class CancelOptions(TypedDict, total=False):
    force: NotRequired[bool]
    """
    Specifies whether to force termination on cancel.

    True for SIGKILL equivalent, False for SIGTERM equivalent.
    Default is False.
    """

    timeout: NotRequired[float]
    """
    Maximum seconds to wait for graceful shutdown after sending the signal.

    Windows: CTRL_BREAK_EVENT
    Unix: SIGTERM

    Default is 3.0 seconds.
    """
