import os
from pathlib import Path

from kiarina.agi.run_context import IDStr
from kiarina.utils.app import user_directory
from pydantic import TypeAdapter

from kiari.streamlit import StreamlitIdentity

from .._models.agent_record import AgentRecord

_id_adapter = TypeAdapter(IDStr)


class AgentUnavailableError(ValueError):
    pass


class AgentStore:
    def __init__(self, directory: Path | None = None) -> None:
        self.directory = directory or user_directory.get_user_data_dir() / "streamlit" / "agents"

    def list(self, organization_id: str, identity: StreamlitIdentity) -> list[AgentRecord]:
        if not self.directory.exists():
            return []

        records: list[AgentRecord] = []
        for path in self.directory.glob("*.json"):
            try:
                record = AgentRecord.model_validate_json(path.read_text())
            except Exception:
                continue
            if (
                record.organization_id == organization_id
                and record.owner_user_id == identity.user_id
            ):
                records.append(record)
        return sorted(records, key=lambda record: (record.created_at, record.agent_id))

    def get_owned(
        self,
        agent_id: str,
        organization_id: str,
        identity: StreamlitIdentity,
    ) -> AgentRecord:
        agent_id = _id_adapter.validate_python(agent_id)
        path = self._path(agent_id)
        try:
            record = AgentRecord.model_validate_json(path.read_text())
        except Exception as e:
            raise AgentUnavailableError("Agent is unavailable") from e

        if record.organization_id != organization_id or record.owner_user_id != identity.user_id:
            raise AgentUnavailableError("Agent is unavailable")
        return record

    def create(
        self,
        agent_id: str,
        organization_id: str,
        identity: StreamlitIdentity,
    ) -> AgentRecord:
        record = AgentRecord(
            agent_id=_id_adapter.validate_python(agent_id),
            organization_id=_id_adapter.validate_python(organization_id),
            owner_user_id=_id_adapter.validate_python(identity.user_id),
        )
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self._path(record.agent_id)
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as e:
            raise AgentUnavailableError("Agent ID is unavailable") from e

        with os.fdopen(descriptor, "w") as file:
            file.write(record.model_dump_json())
        return record

    def delete(self, record: AgentRecord) -> None:
        path = self._path(record.agent_id)
        current = AgentRecord.model_validate_json(path.read_text())
        if current != record:
            raise AgentUnavailableError("Agent is unavailable")
        path.unlink()

    def _path(self, agent_id: str) -> Path:
        return self.directory / f"{agent_id}.json"
