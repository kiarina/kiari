from datetime import UTC, datetime
from typing import Literal

from kiarina.agi.run_context import IDStr
from pydantic import BaseModel, Field


class AgentRecord(BaseModel):
    schema_version: Literal[1] = 1
    agent_id: IDStr
    organization_id: IDStr
    owner_user_id: IDStr
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
