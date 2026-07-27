from pathlib import Path

import pytest
from pydantic import ValidationError

from kiari.streamlit import StreamlitIdentity
from kiari.streamlit.agent_store import AgentStore, AgentUnavailableError


def identity(user_id: str) -> StreamlitIdentity:
    return StreamlitIdentity(
        user_id=user_id,
        display_name=user_id,
        authenticator_name="test",
    )


def test_agent_store_enforces_global_id_and_owner(tmp_path: Path) -> None:
    store = AgentStore(tmp_path)
    alice = identity("alice")
    bob = identity("bob")
    record = store.create("agent-1", "org", alice)

    assert store.list("org", alice) == [record]
    assert store.list("org", bob) == []
    assert store.get_owned("agent-1", "org", alice) == record
    with pytest.raises(AgentUnavailableError):
        store.get_owned("agent-1", "org", bob)
    with pytest.raises(AgentUnavailableError):
        store.create("agent-1", "org", bob)

    store.delete(record)
    assert store.list("org", alice) == []


def test_agent_store_validates_agent_id(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        AgentStore(tmp_path).create("bad/id", "org", identity("alice"))
