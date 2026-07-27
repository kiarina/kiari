from typing import Any, Literal

from pydantic import BaseModel


class RTDBWatchPayload(BaseModel):
    type: Literal["rtdb_event"] = "rtdb_event"
    event_type: str
    path: str
    data: Any
