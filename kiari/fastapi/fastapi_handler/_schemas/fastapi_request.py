from pydantic import BaseModel, Field

from ..._schemas.request_body import RequestBody


class FastAPIRequest(BaseModel):
    body: RequestBody
    headers: dict[str, str] = Field(default_factory=dict)
