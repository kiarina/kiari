from .._views.background_event import BackgroundEvent
from .._views.finish_event import FinishEvent
from .._views.stream_event import StreamEvent

type SubprocessEvent = StreamEvent | FinishEvent | BackgroundEvent
