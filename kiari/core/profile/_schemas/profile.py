from datetime import UTC, datetime

from pydantic import BaseModel, Field

from .._types.profile_name import ProfileName


class Profile(BaseModel):
    name: ProfileName
    description: str = ""
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
