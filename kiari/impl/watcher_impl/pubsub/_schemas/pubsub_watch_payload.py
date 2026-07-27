from typing import Literal

from pydantic import BaseModel, Field


class PubsubWatchPayload(BaseModel):
    type: Literal["pubsub_message"] = "pubsub_message"
    message_id: str
    publish_time: str
    data: str
    attributes: dict[str, str] = Field(default_factory=dict)
