from typing import Literal

from pydantic import BaseModel


class SlackWatchPayload(BaseModel):
    type: Literal["slack_message"] = "slack_message"
    team_id: str
    channel_id: str
    user_id: str
    ts: str
    thread_ts: str = ""
    text: str
