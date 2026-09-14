from typing import Any, Literal

from pydantic import BaseModel


class RTDBWatchPayload(BaseModel):
    type: Literal["rtdb_event"] = "rtdb_event"
    path: str
    data: Any
